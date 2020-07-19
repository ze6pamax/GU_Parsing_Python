import requests

main_link = "https://api.github.com/users/ze6pamax/repos"
response = requests.get(main_link,
		headers={'Accept': 'application/vnd.github.nebula-preview+json'})

json_res = response.json()

i = 1
print("Список активных репозиториев:\n")
for repo in json_res:
	print(f'{i}. {repo["name"]}')
	i +=1
