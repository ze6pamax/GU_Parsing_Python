import requests
from pprint import pprint
import json

main_link = "https://api.github.com/users/ze6pamax/repos"
response = requests.get(main_link,
		headers={'Accept': 'application/vnd.github.nebula-preview+json'})

json_res = response.json()

with open('github_repo_list.json','w') as outfile:
	json.dump(json_res,outfile)
