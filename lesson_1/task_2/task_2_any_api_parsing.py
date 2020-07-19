import requests
import json
from pprint import pprint

main_link = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

#?location=-33.8670522,151.1957362&radius=1500&type=restaurant&keyword=cruise&key=YOUR_API_KEY

with open('login.json','r') as f:
	cred = json.load(f)
	login=cred['login']
	pwd = cred['pass']
	app_key = cred['key']

#print(login,pwd,app_key)		

longitude = 55.592838
lattitude = 37.040266
location = str(longitude)+","+str(lattitude)
radius = 3000000
type = 'store'

search_params = {'location':location,
		'radius':radius,
		'type':type,
		'key':app_key}
		
response = requests.get(main_link,params=search_params)

json_res = response.json()

with open('res_maps_place_api.txt','w') as f:
	f.write("place_id;name;vicinity;type\n")
	for a in json_res:
		for result in json_res['results']:	
			place_id = result['place_id']
			name = result['name']
			vicinity = result['vicinity']
			type = result['types']
			for t in type:
				if t == 'store':
					f.write("{};{};{};{}\n".format(place_id,name,vicinity,t))
