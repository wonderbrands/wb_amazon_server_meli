import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauth_odoo12 import *

oauth=oauth_odoo12_production()
url=oauth['url']
client_id=oauth['client_id']
client_secret=oauth['client_secret']

limite =1000

def get_stock_quant_ids(seller_sku):
	try:
		data = {
			'model': "product.product",
			'domain': json.dumps([['default_code', '=', seller_sku]]),
			'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids', 'virtual_available' ]),
		}

		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))#
		stock_quant_ids=response[0]['stock_quant_ids']
		return stock_quant_ids
	except Exception as e:
		print('Error en get_stock_quant_ids : '+str(e))
		return False

def get_stock_quant(id):
	try:
		data = {
		'model': "stock.quant",
		'domain': json.dumps([['id', '=', id]]),
		'fields': json.dumps(['id' ,'quantity', 'location_id', 'reserved_quantity']),
		}
		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))
		location_id =response[0]['location_id']
		quantity=response[0]['quantity']	
		reserved_quantity =response[0] ['reserved_quantity']
		return dict(location_id=location_id, quantity=quantity, reserved_quantity=reserved_quantity)
	except Exception as e:
		print('Error en get_stock_quant : '+str(e))
		return False

def get_ag_Stock(stock_quant_ids):
	try:
		existencia_ag=0
		for id in stock_quant_ids:
			stock_quant = get_stock_quant(id)
			location_id =stock_quant['location_id']
			quantity=stock_quant['quantity']	
			reserved_quantity =stock_quant['reserved_quantity']
			if location_id[1] == 'AG/Stock':
				#print (seller_sku, location_id, quantity, reserved_quantity)
				return quantity
	except Exception as e:
		print('Error en get_ag_Stock : '+str(e))
		return False

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

	def execute(self, enpoint, type="GET", data={}):
		if type == "POST":
			response = self.oauth.post(self.route(enpoint), data=data)
		else:
			response = self.oauth.get(self.route(enpoint), data=data)

	
		if response.status_code != 200:
			api.authenticate() # OJO COLOCAR PARA REACTIVAR TIMEOUT TOKEN
			raise Exception(pprint(response.json()))
		else:
			return response.json()


# init API
api = RestAPI()
api.authenticate()
if __name__ == '__main__':

	seller_sku='OR-427964'
	stock_quant_ids = get_stock_quant_ids(seller_sku) # Obtener los quants_ids
	#print ('stock_quant_ids:',stock_quant_ids)
	
	ag_stock = get_ag_Stock(stock_quant_ids)
	print(seller_sku, 'AG/Stock:', ag_stock)
	'''
	for id in stock_quant_ids:
		stock_quant = get_stock_quant(id)
		location_id =stock_quant['location_id']
		quantity=stock_quant['quantity']	
		reserved_quantity =stock_quant['reserved_quantity']
		if location_id[1] == 'AG/Stock':
			print (seller_sku, location_id, quantity, reserved_quantity)
	'''

	

