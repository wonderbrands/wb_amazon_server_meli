#!/usr/bin/python
import sys
import json
import pprint 
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

url_sr ='https://somosreyes.odoo.com'
#url_sr ='https://somosreyes-test-834600.dev.odoo.com'
client_id_sr ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret_sr ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

class RestAPI:
	def __init__(self):
		self.url = url_sr
		self.client_id = client_id_sr
		self.client_secret = client_secret_sr
		self.client = BackendApplicationClient(client_id=self.client_id)
		self.oauth = OAuth2Session(client=self.client)

	def route(self, url):
		if url.startswith('/'):
			url = "%s%s" % (self.url, url)
		return url

	def authenticate(self):
		try:
			self.oauth.fetch_token(
			token_url=self.route('/api/authentication/oauth2/token'),
			client_id=self.client_id, client_secret=self.client_secret
			)
			#print(self.oauth.fetch_token(token_url=self.route('/api/authentication/oauth2/token'),client_id=self.client_id, client_secret=self.client_secret) )
		except Exception as e:
			raise e
		

	def execute(self, enpoint, type="GET", data={}):
		try:
			if type == "POST":
				response = self.oauth.post(self.route(enpoint), data=data)
			elif type == "PUT":
				response = self.oauth.put(self.route(enpoint), data=data)
			else:
				response = self.oauth.get(self.route(enpoint), data=data)
				print ('RESPONSE', response)
			if response.status_code != 200:
				#api.authenticate()
				raise Exception(pprint(response.json()))
			else:
				#print response.json()
				return response.json()

		except Exception as e:
			print ('Error al realizar el request en: Execute()'+str(e) )
			return False
	
	def get_order_in_odoo(self, marketplace_order_id):
		try:
			data = {
				'model': "sale.order",
				'domain': json.dumps([['id', '=', str(marketplace_order_id) ]]),
				'fields': json.dumps(['id','name', 'marketplace_order_id','client_order_ref','tracking_number','warehouse_id','seller_marketplace','commitment_date']),
				'limit': 1
			}
			response = api.execute('/api/search_read', data=data)
			
			existe=len(response)
			if existe==0: #No existe
				return False 
			else:
				return response[0]
		except Exception as e:
			print('Error en verify_exist_order_in_odoo() : '+str(e))
			return False

	def update_tokens_in_odoo(self, client_id, access_token, refresh_token, token_type, expires, last_date_retrieve):
		try:
			data = {
			"model":"tokens_markets.tokens_markets",
			"domain":json.dumps([["client_id","=", client_id]]),
			"fields":json.dumps(["client_id", "seller", "name_markeplace"]),
			}
			response =api.execute("/api/search_read", data=data)
			print ('ODOO RESPONSE READ|'+str(response) )
			ids=response[0]["id"]
			print (ids)
			
			# update product
			values = {
				'access_token': access_token,
				'refresh_token': refresh_token,
				'token_type':token_type, 
				'expires':expires,
				'last_date_retrieve':last_date_retrieve,
			}

			data = {
				"model": "tokens_markets.tokens_markets",
				'ids':[ids],
				"values": json.dumps(values),
			}
			print ('DATA ODOO|'+ str(data) )
			response = api.execute('/api/write', type="PUT", data=data)
			print('ACTUALIZANDO ODOO|'+ str(response) )
			return True
		except Exception as e:
			print ('Error en update_tokens_in_odoo(): '+ str(e) )
			return False

api = RestAPI()
api.authenticate()

if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	'''
	marketplace_order_id=6345
	api.get_order_in_odoo(marketplace_order_id)
	null='null'
	false=False
	'''

	client_id = '5630132812404309'
	access_token = 'APP_USR-5630132812404309-070416-e2c54f8f217b80f3fe607d4bdd9102cb-160190870'
	refresh_token = 'TG-5d1e305555091300068ca07e-160190870'
	token_type ='bearer'
	expires ='21600'
	last_date_retrieve ='2019-07-07 13:00:00'
	api.update_tokens_in_odoo(client_id, access_token, refresh_token, token_type, expires, last_date_retrieve)
	