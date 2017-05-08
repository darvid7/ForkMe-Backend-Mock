import requests
import datetime
import time
import json

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

response = requests.get(query)

status = response.status_code
content_type = response.headers['content-type'] or None
encoding = response.encoding
text = response.text

json_server_endpoint = 'http://localhost:3000/repositories'

print('status: %s\ncontent type: %s\nencoding: %s\n' % (status, content_type, encoding))
results = json.loads(text)
print('url: ' + query)
print('count items returned: ' + str(results['total_count']))
repos = results['items']
print('count repos returned: ' + str(len(repos)))

for repo in repos:
	print('repo name: ' + str(repo['full_name']), end=", ")
	print('stars: ' + str(repo['stargazers_count']), end=", ")
	print('watchers: ' + str(repo['watchers_count']), end='\n')
	# Assume full name can be used to uniquely identify repositories (might need to change for implementation that looks back in time).
	data = repo['full_name']: repo
	requests.post(json_server_endpoint, data=data)

with open('query_response.txt', 'w') as fh:
	fh.write(text)

