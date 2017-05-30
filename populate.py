import requests
import datetime
import time
import json

headers = {
	"Content-Length": "0",
	"Authorization": "token MY_OAUTH_TOKEN"
}

today = datetime.datetime.now()
seven_days = datetime.timedelta(days=7)
a_week_ago = today - seven_days
last_week_formatted = a_week_ago.strftime('%Y-%m-%d')

# Trending defined as hottest repos created in the last week.
root_endpoint = 'https://api.github.com/'
search = 'search/repositories'
seach_key_words = 'created:>%s' % last_week_formatted
sort = 'stars'
order = 'desc'

query = '%s%s?q=%s&sort=%s&order=%s' % (root_endpoint, search, seach_key_words, sort, order)

response = requests.get(query, headers=headers)

status = response.status_code
content_type = response.headers['content-type'] or None
encoding = response.encoding
text = response.text

json_server_endpoint = 'http://localhost:3000/repositories'

print('status: %s\ncontent type: %s\nencoding: %s\n' % (status, content_type, encoding))
results = json.loads(text)
try:
	print('url: ' + query)
	print('count items returned: ' + str(results['total_count']))
	repos = results['items']
	print('count repos returned: ' + str(len(repos)))
except KeyError:
	print("KeyError: " + str(results))
	raise KeyError


# Note: subscribers_count is not in repo responses from the Github API search query.
repo_tuples = [repo['full_name'].split('/') for repo in repos]  # List of lists of form [[owner, repo], ..]
repo_tuples.insert(0, ["golang", "go"])

query = "https://api.github.com/repos/%s/%s" 
repos_full_data = []
for repo in repo_tuples:
	response = requests.get(query % (repo[0], repo[1]), headers=headers)
	repo_data = json.loads(response.text)
	repos_full_data.append(repo_data)
	try:
		print("Added repo data: %s/%s, subscriber_count: %s" % (repo[0], repo[1], repo_data["subscribers_count"]))
	except KeyError:
		print("KeyError: " + str(repo_data))

json_data = []

headers = {"Content-Type": "application/json"}

# Only keep theses fields form Github API response.
relvant_fields = [
	"size", "full_name", "stargazers_count", "homepage", "description", "forks_count", "owner",
	"id", "organizations_url", "avatar_url", "html_url", "url", "followers_url", "login", "type",
	"repos_url", "gravatar_id", "created_at", "language", "open_issues_count", "score", "updated_at",
	"has_wiki", "subscribers_count"
]

print ("Adding to json server");

for repo in repos_full_data:
	repo_dict = {}
	print('repo name: ' + str(repo['full_name']), end=", ")
	print('stars: ' + str(repo['stargazers_count']))
	# print('watchers: ' + str(repo['watchers_count']), end='\n') this is same as star count.
	# Assume full name can be used to uniquely identify repositories (might need to change for implementation that looks back in time).
	for key, value in repo.items():
		if key not in relvant_fields:  # Skip over unwanted fields.
			continue
		if key == "owner":
			#  Parse owner field.
			owner_dict = {}
			for owner_key, owner_value in repo["owner"].items():
				if owner_key not in relvant_fields:
					continue
				owner_dict[owner_key] = owner_value
			repo_dict["owner"] = owner_dict
		else:
			# Add key.
			repo_dict[key] = value

	data = repo_dict
	jsonify = json.dumps(data)
	requests.post(json_server_endpoint, data=jsonify, headers=headers)
	time.sleep(1)
	json_data.append(jsonify)

with open('dict_to_json.txt', 'w') as fh:
	for l in json_data:
		fh.write(l)

with open('query_response.txt', 'w') as fh:
	fh.write(text)
