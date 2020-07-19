import requests
from pprint import pprint

main_link = "https://api.github.com/users/ze6pamax/repos"
response = requests.get(main_link,
		headers={'Accept': 'application/vnd.github.nebula-preview+json'})

json_res = response.json()

print("Список активных репозиториев:")
for i in json_res:
	print(i["name"])

