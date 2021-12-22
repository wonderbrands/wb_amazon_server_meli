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



	def get_sale_order_meli_full(self):
		try:	
			partner_id = 73111
			warehouse_id =3 #{'id': 3, 'name': 'Mercado Libre Full'}
			state_order ='draft'
			expected_date = '07/09/2020'
			expected_date = '2020-09-07%'

			data = {
			'model': "sale.order",
			'domain': json.dumps([['name', '=', 'SO350635'],['partner_id', '=', partner_id], ['warehouse_id', '=', warehouse_id], ['state', '=', state_order ],  ['expected_date', 'like', expected_date  ]]),
			'fields': json.dumps(['id', 'name', 'warehouse_id', 'state', 'expected_date']),
			#'fields': json.dumps(['id' ,'quantity', 'location_id', 'reserved_quantity', 'l10n_mx_edi_payment_method_id']),
			}
			response = api.execute('/api/search_read', data=data)
			print(response)
			#print (json.dumps(response, indent=4, sort_keys=True))
			for order in response:
				print (order)
			
			return True 
		except Exception as e:
			print ('ERROR|'+str(e))
			return False

	def update_sale_order_meli_full(self, order_id):
		try:			
			# update sale.order
			values = {
				'state': 'sale',
			}

			data = {
				"model": "sale.order",
				'ids':[order_id],
				"values": json.dumps(values),
			}
			print (data)
			response = api.execute('/api/write', type="PUT", data=data)
			print(response)
		except Exception as e:
			print ('Error en update_price_product: '+str(e) )



	def get_sale_order(self, name):
		try:
			data = {
			'model': "sale.order",
			'domain': json.dumps([['name', '=', name]]),
			#'fields': json.dumps(['id', 'name', 'access_token', 'access_url']),
			#'fields': json.dumps(['id' ,'quantity', 'location_id', 'reserved_quantity', 'l10n_mx_edi_payment_method_id']),
			}
			response = api.execute('/api/search_read', data=data)
			print (json.dumps(response, indent=4, sort_keys=True))
			#location_id =response[0]['location_id']
			#quantity=response[0]['quantity']	
			#reserved_quantity =response[0] ['reserved_quantity']

			access_token =quantity=response[0]['access_token']
			access_url=quantity=response[0]['access_url']
			name= quantity=response[0]['name']

			url_odoo='https://somosreyes-test-652809.dev.odoo.com'
			url = url_odoo + access_url+'?access_token='+access_token+'&report_type=pdf&download=true'
			print (url)
			myfile = requests.get(url, allow_redirects=True)
			print (myfile.text)
			file = '/home/ubuntu/meli/Pedido_'+str(name)+'.pdf'
			print (file)
			open(file, 'wb'). write(myfile.content)
			return True 
		except Exception as e:
			print ('ERROR|'+str(e))
			return False


	

if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	ordenes_meli_full = api.get_sale_order_meli_full()
	order_id =350634
	api.update_sale_order_meli_full(order_id)

