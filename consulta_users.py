import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

url ='https://somosreyes-test-2176255.dev.odoo.com/'
#url ='https://somosreyes.odoo.com'
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
			#response = api.execute('/api/write', type="PUT", data=data)
			#print(response)
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


	def get_order_line_id(self, order_line_id):
		try:
			data = {
			'model': "sale.order.line",
			'domain': json.dumps([['id', '=', order_line_id]]),
			#'fields': json.dumps(['id','product_id' ]),
			#'fields': json.dumps([]),
			}
			response = api.execute('/api/search_read', data=data)
			#print (response)
			#product_id=response[0]['product_id']
			print (json.dumps(response, indent=4, sort_keys=True))#ok
			#return product_id

		except Exception as e:
			return False

	def get_carrier_id(self, carrier_name):
		try:
			data = {
			"model":"product.product",
			"domain":json.dumps([["name","=", carrier_name]]),
			"fields":json.dumps(["name"]),
			}
			response =api.execute("/api/search_read", data=data)
			print(response)
			#partner_id = response[0]['id']
			#return partner_id
		except Exception as e:
			print('Error en carrier_name : '+str(e))
			return False

	def get_stock_quant(self, id):
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
			return False

	def consulta_equipo(self, name_team):
		try:
			lista_urrea=[]
			data = {
			"model":"crm.team",
			"domain":json.dumps([["name","=", name_team]]),
			"fields":json.dumps(["id", "name"]),
			}
			response =api.execute("/api/search_read", data=data)
			id_equipo = response[0]['id']
			print (response)
			return id_equipo
		except Exception as e:
			print('Error en consulta_equipo() : '+str(e))
			return False

	def consulta_users(self, usuario):
		try:
			lista_urrea=[]
			data = {
			"model":"res.users",
			"domain":json.dumps([["name","=", usuario]]),
			"fields":json.dumps(["name"]),
			}
			response =api.execute("/api/search_read", data=data)
			id_usuario = response[0]['id']
			return id_usuario

		except Exception as e:
			print('Error en productos_urrea_en_odoo12 : '+str(e))
			return 1

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



	def get_account_payment():
		try:
			data = {
			'model': "l10n_mx_edi.payment.method",
			'domain': json.dumps([['name', '!=', 'partner_type']]),
			#'fields': json.dumps(['id','name']),
			}
			response = api.execute('/api/search_read', data=data)
			
			for metodo in response:
				print ( metodo['id'],metodo['code'], metodo['display_name'])
				#print ( str(metodo['code'])+':'+str(metodo['id']))


			#print (json.dumps(response, indent=4, sort_keys=True))
			warehouse_id = response[0]['id']
			return warehouse_id
		except Exception as e:
			return False

	def get_account_payment_by_code(id_forma_de_pago):
		try:
			data = {
			'model': "l10n_mx_edi.payment.method",
			'domain': json.dumps([['id', '=', id_forma_de_pago]]),
			'fields': json.dumps(['id','name', 'code', 'display_name']),
			}

			response = api.execute('/api/search_read', data=data)
			print (response)
			#for metodo in response:
			#	print ( metodo['id'],metodo['code'], metodo['display_name'])
				#print ( str(metodo['code'])+':'+str(metodo['id']))

			#print (json.dumps(response, indent=4, sort_keys=True))
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



def get_stock_move_line_by_name(name):
	try:
		data = {
		'limit': 5000,
		'model': "stock.move",
		#'domain': json.dumps([['state', '=', 'done'], ]),
		'domain': json.dumps([['state', '=', 'assigned'], ['location_id','=',12], ]),
		'fields': json.dumps([ 'state','picking_id','product_id','product_uom_qty','reserved_availability', 'quantity_done', 'location_dest_id', '__last_update']),
		#'fields': json.dumps([]),
		
		}
		response = api.execute('/api/search_read', data=data) #"state": "confirmed"
		#print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		#location_dest_id = response[0]['location_dest_id']
		#product_uom_qty = response[0]['product_uom_qty']
		i=0
		for dato in response:
			i=i+1
			print (i, dato['state'],dato['picking_id'][1],dato['__last_update'],dato['product_id'][1], dato['reserved_availability'])

		#last_update = response[0]['__last_update']
		#reserved_availability=response[0]['reserved_availability']
		#print(last_update, reserved_availability)
		#return dict(reserved_availability=reserved_availability, last_update=last_update)
	except Exception as e:
		return False

def verify_exist_order_in_odoo(marketplace_order_id):
	
	data = {
		'model': "sale.order",
		'domain': json.dumps([['marketplace_order_id', '=', str(marketplace_order_id) ]]),
		'limit': 1
	}
	response = api.execute('/api/search', data=data)
	existe=len(response)
	if existe==0: #No existe
		print('No existe la orden ')
		return False 
	else:
		print('Si existe la orden ')
		return True


def get_token_odoo():
	headers = {'Accept': 'application/json',
	'content-type': 'application/json',
	'OAuth scope':'Bearer', 
	'client_id':'B38ULenQ5Wo9YHVpCNPwLYU06o0dif', 
	'client_secret':'PDzW1J08BJB0JB3UXh0TlQkiPOm3pU', 
	'redirect_uri':'https://127.0.0.1/callback', 
	'code':'dcee1806d2c50d0fb598', 
	'grant_type':'authorization_code',
	}
	headers= "{OAuth scope='Example' client_id='B38ULenQ5Wo9YHVpCNPwLYU06o0dif', client_secret='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU', redirect_uri='https%3A%2F%2F127.0.0.1%2Fcallback', code='dcee1806d2c50d0fb598' grant_type='authorization_code'}"
	url ='https://somosreyes-test-348102.dev.odoo.com'
	r=requests.post(url, headers=headers)
	print (r.json() )

def get_order_meli(seller_id, order_id, access_token):
	headers = {'Accept': 'application/json','content-type': 'application/json'}
	url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
	r=requests.get(url, headers=headers)
	order = r.json()['results'][0]
	print (json.dumps(order, indent=4, sort_keys=True))#ok


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


def get_id_odoo_product(seller_sku):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids', 'virtual_available','qty_available', 'stock_real' ]),
		#'fields': json.dumps([]),
		}
		response = api.execute('/api/search_read', data=data)
		print (response[0]['stock_real'])
		#stock_quant_ids=response[0]['stock_quant_ids']
		#print (json.dumps(response, indent=4, sort_keys=True))#ok

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

def get_id_odoo_sub_product_lines(sub_product_line_id):
	try:
		data = {
		'model': "sub.product.lines",
		'domain': json.dumps([['id', '=', sub_product_line_id]]),
		'fields': json.dumps(['id','product_id' ]),
		#'fields': json.dumps([]),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		product_id=response[0]['product_id']
		#print (json.dumps(response, indent=4, sort_keys=True))#ok
		return product_id

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

def update_price_product(default_code, list_price):
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
			
			# update product
			values = {
				'list_price': list_price,
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


def update_sale_order(ids, tracking_method,  tracking_number):
		try:		
			values = {'tracking_number': tracking_method+'/'+tracking_number,}

			data = {
				"model": "sale.order",
				'ids':ids,
				"values": json.dumps(values),
			}

			response = api.execute('/api/write', type="PUT", data=data)
			print('UPDATE SALE ORDER|',response)
		except Exception as e:
			print ('Error en update_sale_order: '+str(e) )


def update_stock_markets(product_id, stock_markets):
	try:
		values = {'stock_markets' : stock_markets,}
		data = {
				"model": "product.product",
				'ids':product_id,
				"values": json.dumps(values),
			}
		print (data)

		response = api.execute('/api/write', type="PUT", data=data)
		print('UPDATE stock_makets|',response)

	except Exception as e:
		print('Error|update_stock_markets|'+str(e))
		return False

def get_stock_move_line():
	try:
		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', '2020-04-17%'],['reference','like','WH/IN/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id']),
		#'fields': json.dumps([ 'reference','product_id', 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', 'date']),
		#'fields': json.dumps([]),
		#'order_by':json.dumps(['date'])
		'order':['date'],
		'limit': 100000

		}
		response = api.execute('/api/search_read', data=data)
		print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		
		for move in response:
			print (move['date'],move['reference'], move['product_id'][1].split(']')[0][1:])

		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', '2020-04-17%'],['reference','like','WH/OUT/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id']),
		#'fields': json.dumps([ 'reference','product_id', 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', 'date']),
		#'fields': json.dumps([]),
		#'order_by':json.dumps(['date'])
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)
		print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		
		for move in response:
			print (move['date'],move['reference'],move['product_id'][1].split(']')[0][1:])

		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', '2020-04-17%'],['reference','like','MELI/INT/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id']),
		#'fields': json.dumps([ 'reference','product_id', 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', 'date']),
		#'fields': json.dumps([]),
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)
		print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		
		for move in response:
			print( move['date'],move['reference'], move['product_id'][1].split(']')[0][1:])

		return True
	except Exception as e:
		return False

def get_full_stock_move_line():
	try:
		fecha_rastre = '2020-04-17%'
		'''
		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastre],['reference','like','MELI/IN/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id','location_id','location_dest_id']),
		#'fields': json.dumps([ 'reference','product_id', 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', 'date']),
		#'fields': json.dumps([]),
		#'order_by':json.dumps(['date'])
		'order':['date'],
		'limit': 100000

		}
		response = api.execute('/api/search_read', data=data)
		print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		
		for move in response:
			print move['date'],move['reference'], move['product_id'][1].split(']')[0][1:]

		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastre],['reference','like','MELI/OUT/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id','location_id','location_dest_id']),
		#'fields': json.dumps([ 'reference','product_id', 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', 'date']),
		#'fields': json.dumps([]),
		#'order_by':json.dumps(['date'])
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)
		print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		
		for move in response:
			print move['date'],move['reference'],move['product_id'][1].split(']')[0][1:]
		'''
		#--- Cuando enviamos a FULFILLMENT de MELI y dejamos el movimiento en PREPARADO------------------------------------
		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastre],['reference','like','MELI/INT/%'],['state','=', 'assigned'], ]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id','location_id','location_dest_id', 'state']),
		#'fields': json.dumps([ 'reference','product_id', 'remaining_qty', 'product_uom_qty', 'quantity_done', 'location_dest_id', 'date']),
		'fields': json.dumps([]),
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))
		#print (response)
		
		for move in response:
			fecha_proceso = move['date']
			referencia = move['reference']
			sku = move['product_id'][1].split(']')[0][1:]
			reserved_availability = move['reserved_availability']
			quantity_done = move['quantity_done']
			state = move['state']
			location_id  = move['location_id'][1]
			location_dest_id = move['location_dest_id'][1]

			print (fecha_proceso, referencia, sku, location_id,'->', location_dest_id, reserved_availability, quantity_done,state)

		return True
	except Exception as e:
		return False

def get_invoice_id():

	data = {
	'model': "account.invoice",
	'domain': json.dumps([['move_id', '=', 'SR2554'],]),
	#'fields': json.dumps([]),
	'fields': json.dumps([ 'move_id','name','access_token']),
	#'fields': json.dumps([]),
	#'order_by':json.dumps(['date'])
	'limit': 100000
	}
	response = api.execute('/api/search_read', data=data)
	#print (json.dumps(response, indent=4, sort_keys=True))
	print (response)


def get_id_odoo_buyer_by_name(name):
	try:
		data = {
		'model': "res.partner",
		'domain': json.dumps([['name', '=', name]]),
		'fields': json.dumps(['id','name']),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		id_partner=None
		for partner in response:
			#print (partner['id'])
			id_partner = partner['id']
		return id_partner
	except Exception as e:
		return False
		print('Error en get_id_odoo_buyer_by_name() : '+str(e))


if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()

	name='WH/PICK/197848'
	#name='WH/PICK/200715'
	name='WH/PICK/220415'
	name='WH/PICK/265236'
	resultado = get_stock_move_line_by_name(name)
	#print(resultado)

	#get_full_stock_move_line()
	
	#name='SO174622'
	#api.get_sale_order(name)
	#order_line_id = 178762
	#api.get_order_line_id(order_line_id)
	
	#carrier_name='FEDEX'
	#api.get_carrier_id(carrier_name)
	#get_invoice_id()

	#get_stock_real_combos()

	#api.get_meli_ful_warehouse_id_by_name()
	#api.get_locations_odoo()
	#name='WH/INT/00034'
	#get_stock_picking(name)
	'''
	formas_pago_odoo = {'01':1,
						'02':2,
						'03':3,
						'04':4,
						'05':5,
						'06':6,
						'08':7,
						'12':8,
						'13':9,
						'14':10,
						'15':11,
						'17':12,
						'23':13,
						'24':14,
						'25':15,
						'26':16,
						'27':17,
						'28':18,
						'29':19,
						'30':20,
						'99':21,
						'31':22}


	print ('Id Forma de pago', formas_pago['04'])
	id_forma_de_pago='01'
	datos = get_account_payment_by_code(id_forma_de_pago)
	print('Datos: ',datos)
	'''
	#name='SO34452'
	#api.get_sale_order(name)

	#get_account_payment()


	#print('======================================')
	'''
	seller_sku='COMBO-DEWALT-32'
	sub_product_line_ids = get_id_odoo_sub_product(seller_sku)

	for sub_product_line_id in sub_product_line_ids:
		subproducto = get_id_odoo_sub_product_lines(sub_product_line_id)
		print ('Subproducto: ',subproducto)
		product_id = subproducto[0]
		get_odoo_product_by_id(product_id)
	'''
	#get_id_odoo_product(seller_sku)

	'''
	product_id= 43734
	stock_markets = 1
	update_stock_markets(product_id, stock_markets)
	'''
	#lista = []
	

	#name_team = 'Ventas Linio' 
	#api.consulta_equipo(name_team)
	#print ('Print:',api.authenticate())
	#get_token_odoo()
	#ids=[3828]
	#tracking_method='UPS PRUEBA'
	#tracking_number='122334343545'
	#update_sale_order(ids, tracking_method, tracking_number)
	#get_locations_odoo()
	'''
	existencia = 0 

	total=0
	salidas = 0
	'''
	#seller_sku= '260585'#'57537-INTEX'
	
	#stock_quant_ids = get_id_odoo_product(seller_sku)
	#print(stock_quant_ids)

	'''
	
	for id in stock_quant_ids:
		stock_quant = api.get_stock_quant(id)
		location_id =stock_quant['location_id']
		quantity=stock_quant['quantity']	
		reserved_quantity =stock_quant['reserved_quantity']
		if location_id[1] == 'AG/Stock':
			print (seller_sku, location_id, quantity, reserved_quantity)
	
	get_id_odoo_product(seller_sku)
	stock_move_ids = get_stock_move_product(seller_sku)
	for id in stock_move_ids:	
		location_dest_id = get_stock_move_line(id)
		print(location_dest_id)

		
		if 'AG' in location_dest_id['location_dest_id'][1]:
			#print (location_dest_id)	
			if 'AG/Stock' in location_dest_id['location_dest_id'][1]:
				total =  int(location_dest_id['product_uom_qty'])	

			if 'AG/Output' in location_dest_id['location_dest_id'][1]:
				salidas =  salidas + int(location_dest_id['product_uom_qty'])

	
	
	existencia =  total -salidas
	print (existencia)
	'''


	'''
	#list_price =100.00
	#id_product=get_id_odoo_product(seller_sku) 
	#update_price_product(seller_sku, list_price)

	#get_tokens()

	
	order_id='2017709162'
	seller_id='160190870'
	access_token='APP_USR-5630132812404309-051608-7eae59f365c0a410e92d556f35ea8e2f-160190870'
	get_order_meli(seller_id, order_id, access_token)
	
	marketplace_order_id='2012751277'
	verify_exist_order_in_odoo(marketplace_order_id)
	usuario='APIsionate Meli'
	api.consulta_users(usuario)
	'''
	#warehouse_name='Mercado Libre Full'
	#print( api.get_meli_ful_warehouse_id_by_name(warehouse_name) )

	
	#name='Mercado Libre API' # Cliente de Mercado Libre
	#partner_id = get_id_odoo_buyer_by_name(name)
	#print ('partner_id: ', partner_id)
	'''
	comercial='Karen Monroy'
	comercial_id = api.consulta_users(comercial)
	print ('comercial_id', comercial_id)
	get_account_payment()
	seller_sku='FEDEX'
	get_id_odoo_product(seller_sku)
	'''
	#ordenes_meli_full = api.get_sale_order_meli_full()

