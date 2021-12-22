#!/usr/bin/python
import pprint 

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

url_sr ='https://somosreyes-test-348102.dev.odoo.com'
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
			#elif type == "DELETE":
			#    response = self.oauth.delete(self.route(enpoint), data=data)
			else:
				response = self.oauth.get(self.route(enpoint), data=data)
			if response.status_code != 200:
				raise Exception(pprint(response.json()))
				api.authenticate()
			else:
				return response.json()
				print (response.json())

		except Exception as e:
			print ('Error al realizar el request en: Execute()'+str(e) )
		
api = RestAPI()
null='null'
false=False