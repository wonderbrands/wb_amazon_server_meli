import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

#url ='https://somosreyes-test-590581.dev.odoo.com'
url ='https://somosreyes.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

limite =100000
class RestAPI:
	def __init__(self):
		self.url = url
		self.client_id = client_id
		self.client_secret = client_secret

		self.client = BackendApplicationClient(client_id=self.client_id)
		self.oauth = OAuth2Session(client=self.client)

	def route(self, url):
		if url.startswith('/'):
			url = "%s%s" % (self.url, url)
			#print (url)
		return url

	def authenticate(self):
		self.oauth.fetch_token(
			token_url=self.route('/api/authentication/oauth2/token'),
			client_id=self.client_id, client_secret=self.client_secret
		)
		#print( self.oauth.fetch_token(token_url=self.route('/api/authentication/oauth2/token'),client_id=self.client_id, client_secret=self.client_secret) )


	def execute(self, enpoint, type="GET", data={}):
		if type == "POST":
			response = self.oauth.post(self.route(enpoint), data=data)
		elif type == "PUT":
			response = self.oauth.put(self.route(enpoint), data=data)
		elif type == "DELETE":
			response = self.oauth.delete(self.route(enpoint), data=data)
		else:
			response = self.oauth.get(self.route(enpoint), data=data)
		if response.status_code != 200:
			raise Exception(pprint(response.json()))
		else:
			#print (response.json() )
			return response.json()



def update_producto_exclusivas(default_code):
		try:
			data = {
			"model":"product.template",
			"domain":json.dumps([["default_code","=", default_code]]),
			"fields":json.dumps(["name", "default_code", "list_price"]),
			}
			response =api.execute("/api/search_read", data=data)
			#print (response)
			ids=response[0]["id"]
			#print (ids)
			
			values = {
				'producto_exclusivas': True,
			}

			data = {
				"model": "product.template",
				'ids':[ids],
				"values": json.dumps(values),
			}
			#print (data)
			response = api.execute('/api/write', type="PUT", data=data)
			print(response)
		except Exception as e:
			print ('Error en update_price_product: '+str(e) )




def get_tokens():
	try:
		data = {
		'model': "muk_rest.bearer_token",
		'domain': json.dumps([['id', '>', 1]]),
		'fields': json.dumps(['id','access_token', 'refresh_token', 'expires_in']),
		}
		response = api.execute('/api/search_read', data=data)
		print (response)

	except Exception as e:
		return False
	
# init API

if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	productos_exclusivas=open('productos_exclusivas.csv')
	
	for producto in productos_exclusivas:
		default_code = producto[:-1].split(',')[0]
		print default_code
		#default_code='145144'
		update_producto_exclusivas(default_code)
