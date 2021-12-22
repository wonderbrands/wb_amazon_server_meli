import json
import requests
import urllib 
from pprint import pprint
import datetime
from datetime import datetime
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

url_sr ='https://somosreyes-test-348102.dev.odoo.com'
client_id_sr ='7CMhrUe2erWjtleBeLldnR3slrOOfN'
client_secret_sr ='uEbiVGsphfHB1c64U7mwNYJEfmNS9d'


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
			print(self.oauth.fetch_token(token_url=self.route('/api/authentication/oauth2/token'),client_id=self.client_id, client_secret=self.client_secret) )
		except Exception as e:
			print ('CADUCO EL TOKEN GENERAR UNO NUEVO============')
			raise e
		

	def execute(self, enpoint, type="GET", data={}):
		try:
			if type == "POST":
				response = self.oauth.post(self.route(enpoint), data=data)
			elif type == "PUT":
				response = self.oauth.put(self.route(enpoint), data=data)
			elif type == "DELETE":
				response = self.oauth.delete(self.route(enpoint), data=data)
			else:
				response = self.oauth.get(self.route(enpoint), data=data)
			if response.status_code != 200:
				#raise Exception(pprint(response.json()))
				print 'Codigo no es  200'
				pprint(response.json())
				return False
			else:
				print (response.json())
				return response.json()

		except Exception as e:
			print ('Error: Execute()'+str(e) )
			return False
		

null='null'
false=False

#--- 1. recuperamos el token de CBT MELI
def recupera_odoo_token(user_id):
	try:
		token_odoo_dir='/home/ubuntu/meli/tokens_odoo.txt'
		archivo_tokens=open(token_dir, 'r')
		tokens=archivo_tokens.read().replace("'", '"')
		tokens_meli = json.loads(tokens)
		archivo_tokens.close()
		access_token=tokens_meli['access_token']
		return access_token
	except Exception as e:
		print ('Error recupera_meli_token : '+str(e))
		return False


#--- 1. recuperamos el token de CBT MELI
def recupera_meli_token(user_id):
	try:
		#print('User Id: ', user_id)
		token_dir=''
		if user_id ==25523702:# Usuario de SOMOS REYES VENTAS
			token_dir='/home/ubuntu/meli/tokens_meli.txt'
		elif user_id ==160190870:# Usuario de SOMOS REYES OFICIALES
			token_dir='/home/ubuntu/meli/tokens_meli_oficiales.txt'

		archivo_tokens=open(token_dir, 'r')
		tokens=archivo_tokens.read().replace("'", '"')
		tokens_meli = json.loads(tokens)
		archivo_tokens.close()
		access_token=tokens_meli['access_token']
		return access_token
	except Exception as e:
		print ('Error recupera_meli_token : '+str(e))
		return False

	

def get_order_meli(seller_id, order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json(), indent=4, sort_keys=True))

		order = r.json()['results'][0]
		#print (json.dumps(order, indent=4, sort_keys=True))#ok
		shipping_id = order['shipping']['id']
		feedback = order['feedback']['sale']
		print ('feedback: ',feedback)
		shipment={}
		fulfilled=False
		if feedback:
			fulfilled = order['feedback']['sale']['fulfilled']
			if fulfilled:
				shipment = get_shipment_meli(shipping_id, access_token)

		id_order = order['id']
		order_status = order['status']
		date_created= order['date_created'][:-10]
		#print ('date_created: ', date_created)
		i=0
		items={}
		list_items=[]
		for item in order['order_items']:
			seller_sku = order['order_items'][i]['item']['seller_sku']
			product_id = get_id_odoo_product(seller_sku)
			list_items.append(product_id)
			items[seller_sku]=product_id
			quantity=order['order_items'][i]['quantity']

		
		seller_nickname = order['seller']['nickname']
		buyer_name = order['buyer']['first_name']+ ' '+order['buyer']['last_name']
		buyer_email = order['buyer']['email']
		
		name='Mercado Libre API' # Cliente de Mercado Libre
		partner_id = get_id_odoo_buyer_by_name(name)

		usuario='APIsionate Meli' # Comercial
		comercial_id = consulta_users(usuario)


		return dict( id_order=id_order, fulfilled=fulfilled, order_status=order_status, date_created=date_created,seller_nickname=seller_nickname,
			buyer_name=buyer_name, buyer_email=buyer_email, partner_id=partner_id, items=items, shipping_id=shipping_id, shipment=shipment, list_items=list_items, comercial_id=comercial_id)

	except Exception as e:
		print ('Error al intentear obtner la orden de Meli. get_order_meli(): '+ str(e))
		return False
	
def get_shipment_meli(shipping_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url='https://api.mercadolibre.com/shipments/'+str(shipping_id)+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json(), indent=4, sort_keys=True))
		results = r.json()#['results'][0]
		#print (results)
		order_id=results['order_id']
		order_cost=results['order_cost']
		status = results['status']
		tracking_number = results['tracking_number']
		tracking_method = results['tracking_method']
		return dict(status=status, tracking_number=tracking_number, tracking_method=tracking_method)
	except Exception as e:
		print (' Error get_shipment_meli: '+ str(e))
		return False

def consulta_users():
		try:
			lista_urrea=[]
			data = {
			"model":"res.users",
			#"domain":json.dumps([["name","=", usuario]]),
			"fields":json.dumps(["name"]),
			}
			response =api.execute("/api/search_read", data=data)
			pprint (response)
			#id_usuario = response[0]['id']
			return id_usuario

		except Exception as e:
			print('Error en consulta_users() : '+str(e))
			return 1

def get_id_odoo_product(seller_sku):
	try:
		data = {
		'model': "product.template",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		#'fields': json.dumps(['id','name']),
		}
		response = api.execute('/api/search_read', data=data)
		print (response)
		id_product=response[0]['id']
		return id_product
	except Exception as e:
		print('Error en get_id_odoo_product() : '+str(e))
		return False

def get_sku_odoo_product(id_product):
	try:
		data = {
		'model': "product.template",
		'domain': json.dumps([['id', '=', id_product]]),
		'fields': json.dumps(['id','name','default_code']),
		}
		print data
		response = api.execute('/api/search_read', data=data)
		print (response)
		#return response
	except Exception as e:
		print('Error en get_id_odoo_product() : '+str(e))
		return False

def verify_exist_order_in_odoo(marketplace_order_id):
	try:
		data = {
			'model': "sale.order",
			'domain': json.dumps([['marketplace_order_id', '=', str(marketplace_order_id) ]]),
			'limit': 1
		}
		response = api.execute('/api/search_read', data=data)
		existe=len(response)
		#print response
		id_orden=response[0]['id']
	
		if existe==0: #No existe
			print('No existe la orden ')
			return False 
		else:
			print('Si existe la orden ')
			return id_orden 
	except Exception as e:
		print('Error en verify_exist_order_in_odoo() : '+str(e))
		return False
	

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
		print('Error en get_id_odoo_buyer_by_name() : '+str(e))
		return False

def get_meli_ful_warehouse_id_by_name(warehouse_name):
	try:
		data = {
		'model': "stock.warehouse",
		'domain': json.dumps([['name', '=', warehouse_name]]),
		'fields': json.dumps(['id','name']),
		}
		response = api.execute('/api/search_read', data=data)
		print (response)
		warehouse_id = response[0]['id']
		return warehouse_id
	except Exception as e:
		print('Error en get_meli_ful_warehouse_id_by_name() : '+str(e))
		return False
def update_order_odoo(default_code, orden_id):
		try:
			data = {
			"model":"product.template",
			"domain":json.dumps([["default_code","=", default_code]]),
			"fields":json.dumps(["name", "default_code", "stock_exclusivas"]),
			}
			response =api.execute("/api/search_read", data=data)
			#print (response)
			ids=response[0]["id"]
			print (ids)
			
			# update sale order
			values = {
				'order_line': [(0, 0, {'product_id':3286})],
			}

			data = {
				"model": "sale.order",
				'ids':orden_id,
				"values": json.dumps(values),
			}
			print (data)
			response = api.execute('/api/write', type="PUT", data=data)
			print(response)
		except Exception as e:
			print ('Error en update_stock_exclusivas: '+str(e) )


def make_map_meli_odoo():
	try:
		values={'commitment_date': '2019-06-21 15:01:33', 
		'marketplace': 'MERCADO LIBRE', 
		'user_id': 33, 
		'confirmation_date': '2019-06-21 15:01:33', 
		'marketplace_order_id': 2058257613, 
		'correo_marketplace': u'sperez.rsgwxj+2-ogiydkobsgu3tmnjw@mail.mercadolibre.com.mx', 
		'order_line': [(0, 0, {'product_id': 85383})], 
		'payment_term_id': 1, 
		'tracking_number': u'MEL Middle Mile/27993158380', 
		'seller_marketplace': u'SOMOS-REYES', 
		'picking_policy': 'one', 
		'state': 'draft', 
		'client_order_ref': u'Sofia P\xe9rez', 
		'order_status': u'paid', 
		'date_created':	'2019-06-21 15:01:33', 
		'warehouse_id': 3, 
		'partner_id': 33608
		}

		data = {
			'model': "sale.order",
			'values': json.dumps(values),
		}
		pprint (data)
		response = api.execute('/api/create', type="POST", data=data)
		print response
		print ('Orden Creada: ', marketplace_order_id )
		return response
	
	except Exception as e:
		print ('Error make_map_meli_odoo(): '+str(e))
		return False



#api = RestAPI()
#api.authenticate()

if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	result  = make_map_meli_odoo()
	print ('Resultado: ', result)
	'''
	marketplace_order_id ='2059155907'
	orden_id=verify_exist_order_in_odoo(marketplace_order_id)

	if orden_id:
		print 'ORDEN ID: ', orden_id
		default_code='276119'
		update_order_odoo(default_code, orden_id)
		#get_id_odoo_product(seller_sku, orden_id)

	#update_stock_exclusivas(default_code)
	'''
	#id_product=3286
	#get_sku_odoo_product(id_product)
	
	#default_code='276119'
	#get_id_odoo_product(default_code)

	#update_order_odoo(default_code, orden_id)

	#consulta_users()