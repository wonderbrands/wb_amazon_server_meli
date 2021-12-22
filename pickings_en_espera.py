import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

#url ='https://somosreyes-test-1289955.dev.odoo.com/'
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

def movimientos_pick(state):
	try:
		lista_picking_id_en_espera=[]

		data = {
		'limit': 5000,
		'model': "stock.move",
		#'domain': json.dumps([['state', '=', 'done'], ]),
		'domain': json.dumps([['state', '=', state], ['location_id','=',12], ]),
		'fields': json.dumps([ 'state','origin','picking_id','product_id','product_uom_qty','reserved_availability', 'quantity_done', 'location_dest_id', '__last_update']),
		#'fields': json.dumps([]),
		
		}
		response = api.execute('/api/search_read', data=data) #"state": "confirmed"
		#print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		i=0
		for dato in response:
			i=i+1
			print (i, dato['state'],dato['origin'],dato['picking_id'][1],dato['__last_update'],dato['product_id'][1], dato['reserved_availability'])
			lista_picking_id_en_espera.append(dato['picking_id'][1])


	except Exception as e:
		return False

if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()

	#state='confirmed'
	state='assigned'
	resultado = movimientos_pick(state)