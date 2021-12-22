import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

#url ='https://somosreyes-test-2176255.dev.odoo.com/'
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

	def get_stock_picking(name):
		try:
			data = {
			'model': "stock.picking",
			'domain': json.dumps([['name', '=', name]]),
			#'fields': json.dumps(['remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id']),
			}
			response = api.execute('/api/search_read', data=data)
			print (json.dumps(response, indent=4, sort_keys=True))
			#print (response)
			return True
		except Exception as e:
			return False
	

	
	def get_meli_ful_warehouse_id_by_name(self, warehouse_name):
		#[{'id': 1, 'name': 'Almacén General'}, {'id': 3, 'name': 'Mercado Libre Full'}, {'id': 4, 'name': 'Linio Full'}, {'id': 5, 'name': 'Amazon Full'}, {'id': 6, 'name': 'Ventas de Piso'}, {'id': 7, 'name': 'Urrea Dropshipping'}, {'id': 8, 'name': 'Amazon Onsite'}]

		try:
			data = {
			'model': "stock.warehouse",
			'domain': json.dumps([['name', '!=', '']]),
			'fields': json.dumps(['id','name']),
			}
			response = api.execute('/api/search_read', data=data)
			print (response)
			warehouse_id = response[0]['id']
			return warehouse_id
		except Exception as e:
			return False



	def get_locations_odoo(self):
		try:
			data = {
			'model': "stock.location",
			'domain': json.dumps([['display_name', '=', 'AG/Stock']]),
			'fields': json.dumps(['id','display_name', 'quant_ids']),
			}
			response = api.execute('/api/search_read', data=data)

			for res in response:
				print (res['display_name'], len(res['quant_ids']))
				if res['display_name'] =='AG/Stock':
					print (res['display_name'], len(res['quant_ids']))
					for quant_id in res['quant_ids']:
						print (quant_id)
					#	get_stock_quant(int(quant_id) )
					
						#get_odoo_product_by_id(product_id)



			print (json.dumps(response[0], indent=4, sort_keys=True))
			#return warehouse_id
		except Exception as e:
			return False


def get_stock_move_line(id):
	try:
		data = {
		'model': "stock.move",
		'domain': json.dumps([['id', '=', id]]),
		#'fields': json.dumps([ 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', '__last_update']),
		'fields': json.dumps([]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		location_dest_id = response[0]['location_dest_id']
		product_uom_qty = response[0]['product_uom_qty']
		last_update = response[0]['last_update']
		return dict(location_dest_id=location_dest_id, product_uom_qty=product_uom_qty, last_update=last_update)
	except Exception as e:
		return False



def get_stock_real_combos():
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', 'like', 'COMBO%']]),
		'fields': json.dumps(['id','default_code','name', 'stock_real' ]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		print (json.dumps(response, indent=4, sort_keys=True))#ok

		stock_move_ids=response[0]['stock_move_ids']
		return stock_move_ids
	except Exception as e:
		return False


def get_id_odoo_product_by_sku(seller_sku):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		#'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids', 'virtual_available','qty_available', 'stock_real' ]),
		'fields': json.dumps([]),
		}
		response = api.execute('/api/search_read', data=data)
		print (response[0]['stock_real'])
		#stock_quant_ids=response[0]['stock_quant_ids']
		print (json.dumps(response, indent=4, sort_keys=True))#ok

		#return stock_quant_ids
	except Exception as e:
		return False

def get_id_odoo_sub_product(seller_sku):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids', 'virtual_available','qty_available', 'stock_real', 'sub_product_line_ids' ]),
		#'fields': json.dumps([]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		#stock_quant_ids=response[0]['stock_quant_ids']
		sub_product_line_ids = response[0]['sub_product_line_ids']
		print (json.dumps(response, indent=4, sort_keys=True))#ok
		#return stock_quant_ids
		return sub_product_line_ids
	except Exception as e:
		return False

def get_odoo_product_by_id(product_id):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['id', '=', product_id]]),
		'fields': json.dumps(['id','default_code','name', 'list_price','stock_quant_ids', 'virtual_available','qty_available', 'stock_real' ]),
		#'fields': json.dumps([]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		#stock_quant_ids=response[0]['stock_quant_ids']
		print (json.dumps(response, indent=4, sort_keys=True))#ok
		#return stock_quant_ids
	except Exception as e:
		return False

def get_stock_move_product(seller_sku):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids', 'virtual_available' ]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		print (json.dumps(response, indent=4, sort_keys=True))#ok

		stock_move_ids=response[0]['stock_move_ids']
		return stock_move_ids
	except Exception as e:
		return False


def get_stock_quant_product(seller_sku):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name', 'list_price','stock_quant_ids', 'virtual_available' ]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		print (json.dumps(response, indent=4, sort_keys=True))#ok

		stock_quant_ids = response[0]['stock_quant_ids']
		return stock_quant_ids
	except Exception as e:
		return False

def get_stock_quant(quant_id):
		try:
			data = {
			'model': "stock.quant",
			'domain': json.dumps([['id', '=', quant_id]]),
			'fields': json.dumps(['id' ,'quantity', 'location_id', 'reserved_quantity']),

			}
			#print(data)
			response = api.execute('/api/search_read', data=data)
			#print (json.dumps(response, indent=4, sort_keys=True))
			location_id =response[0]['location_id']
			quantity=response[0]['quantity']	
			reserved_quantity =response[0] ['reserved_quantity']
			return dict(location_id=location_id, quantity=quantity, reserved_quantity=reserved_quantity)
		except Exception as e:
			return False
			

if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	seller_sku='153822'
	stock_quant_ids = get_stock_quant_product(seller_sku)
	#print(stock_quant_ids)
	quantity_total =0 
	reserved_quantity_total=0
	for quant_id in stock_quant_ids:
		stock_quant = get_stock_quant(quant_id)
		location_id=stock_quant['location_id']
		quantity = stock_quant['quantity']
		reserved_quantity = stock_quant['reserved_quantity']
		localizacion = location_id[1]
		print(localizacion, quantity, reserved_quantity)

		if 'AG/Stock' in localizacion:
			quantity_total+=quantity
			reserved_quantity_total+=reserved_quantity

	print(quantity_total-reserved_quantity_total)






	