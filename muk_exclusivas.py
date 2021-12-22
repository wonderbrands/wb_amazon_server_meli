import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

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
		try:
			self.oauth.fetch_token(
			token_url=self.route('/api/authentication/oauth2/token'),
			client_id=self.client_id, client_secret=self.client_secret
			)
		except Exception as e:
			print ('Error|authenticate(): '+str(e))
			return False
		

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
			return response.json()

	def update_stock_exclusivas(self, default_code, stock_exclusivas):
		try:
			data = {
			"model":"product.product",
			"domain":json.dumps([["default_code","=", default_code]]),
			"fields":json.dumps(["name", "default_code", "stock_exclusivas"]),
			}
			response =api.execute("/api/search_read", data=data)
			#print (response)
			ids=response[0]["id"]
			#print (ids)
			
			# update product
			values = {
				'stock_exclusivas': stock_exclusivas,
			}

			data = {
				"model": "product.product",
				'ids':[ids],
				"values": json.dumps(values),
			}
			#print (data)
			response = api.execute('/api/write', type="PUT", data=data)
			#print(response)
		except Exception as e:
			api.authenticate()
			print ('Error en update_stock_exclusivas(): '+str(e) )

		
	def productos_exclusivas_en_odoo12(self, marca):
		try:
			lista_exclusivas=[]
			data = {
			"model":"product.category",
			"domain":json.dumps([["name","=", marca]]),
			"fields":json.dumps(["name"]),
			}
			response =api.execute("/api/search_read", data=data)
			id_exclusivas = response[0]['id']
			#print (response)
			
			data = {
			"model":"product.product",
			"limit":limite, 
			"domain":json.dumps([["categ_id","=", id_exclusivas]]),
			"fields":json.dumps(["default_code"]),
			}
			response =api.execute("/api/search_read", data=data)
			for producto in response:
				sku=producto['default_code']
				lista_exclusivas.append(sku)
			#print (len(lista_exclusivas ) )
			return lista_exclusivas
		except Exception as e:
			print('Error en productos_exclusivas_en_odoo12 : '+str(e))
			return False

	def productos_es_exclusivas(self):
		try:
			lista_exclusivas=[]
			data = {
			"model":"product.product",
			"limit":limite, 
			"domain":json.dumps([["producto_exclusivas","=", True]]),
			"fields":json.dumps(["default_code"]),
			}
			response =api.execute("/api/search_read", data=data)
			id_exclusivas = response[0]['id']
			#print (json.dumps(response, indent=4, sort_keys=True))
			#print (response)
			
			for producto in response:
				sku=producto['default_code']
				lista_exclusivas.append(sku)
				print (sku)
			#print (len(lista_exclusivas ) )
			return lista_exclusivas
		except Exception as e:
			print('Error en productos_exclusivas_en_odoo12 : '+str(e))
			return False

# init API
api = RestAPI()
api.authenticate()
if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	#marca='Exclusivas'
	#api.update_stock_exclusivas(default_code,stock_exclusivas)
	#lista_exclusivas = api.productos_exclusivas_en_odoo12(marca)
	#print ('urrea: ',lista_urrea)
	#for default_code in lista_urrea:
	#	api.update_stock_urrea(self, default_code, stock_urrea)
	lista_exclusivas=api.productos_es_exclusivas()
	
	
