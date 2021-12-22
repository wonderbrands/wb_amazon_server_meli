#!/usr/bin/python
import sys
import json
from flask import Flask, request, abort
import requests
import datetime
from datetime import datetime, date, time, timedelta
import pprint 
import logging
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

app = Flask(__name__)

date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]
#log_file='/home/ubuntu/meli/logs/orders_meli_'+str(fecha)+'.log'
#logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.DEBUG)

url_sr ='https://somosreyes-test-652809.dev.odoo.com'
client_id_sr ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret_sr ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

def get_id_odoo_product(seller_sku):
	try:
		data = {
		'model': "product.template",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name','list_price']),
		}
		response = api.execute('/api/search_read', data=data)
		print (response)
		id_product=response[0]['id']
		return id_product
	except Exception as e:
		print('Error en get_id_odoo_product() : '+str(e))
		return False

def consulta_users(usuario):
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
			api.authenticate()
			print('Error en consulta_users() : '+str(e))
			return 1

def verify_exist_order_in_odoo(marketplace_order_id):
	try:
		data = {
			'model': "sale.order",
			'domain': json.dumps([['marketplace_order_id', '=', str(marketplace_order_id) ]]),
			'fields': json.dumps(['id','name','name', 'marketplace_order_id']),
			'limit': 1
		}
		response = api.execute('/api/search_read', data=data)
		print ('VERIFY ORDER: ',response)
		existe=len(response)
		if existe==0: #No existe
			print('No existe la orden ')
			return False 
		else:
			print('Si existe la orden ')
			ids=response[0]['id']
			return ids
	except Exception as e:
		print('Error en verify_exist_order_in_odoo() : '+str(e))
		return False
	
def update_sale_order(ids, marketplace_order_id, tracking_method,  tracking_number):
		try:		
			values = {'tracking_number': tracking_method+'/'+tracking_number,}

			data = {
				"model": "sale.order",
				'ids':ids,
				"values": json.dumps(values),
			}
			response = api.execute('/api/write', type="PUT", data=data)
			print('UPDATE SALE ORDER|',marketplace_order_id, response)
		except Exception as e:
			print ('Error en update_sale_order: '+str(e) )

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
		#print (response)
		warehouse_id = response[0]['id']
		return warehouse_id
	except Exception as e:
		print('Error en get_meli_ful_warehouse_id_by_name() : '+str(e))
		return False
	

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
				#print 'RESPONSE', response
			if response.status_code != 200:
				api.authenticate()
				raise Exception(pprint(response.json()))
			else:
				#print response.json()
				return response.json()

		except Exception as e:
			print ('Error al realizar el request en: Execute()'+str(e) )
		
api = RestAPI()
api.authenticate()
null='null'
false=False

#--- 1. recuperamos el token de CBT MELI
def recupera_meli_token(seller_id):
	try:
		token_dir=''
		if seller_id ==25523702:# Usuario de SOMOS REYES VENTAS
			token_dir='/home/ubuntu/meli/tokens_meli.txt'
		elif seller_id ==160190870:# Usuario de SOMOS REYES OFICIALES
			token_dir='/home/ubuntu/meli/tokens_meli_oficiales.txt'

		archivo_tokens=open(token_dir, 'r')
		tokens=archivo_tokens.read()
		tokens_meli = json.loads(tokens)
		archivo_tokens.close()
		access_token=tokens_meli['access_token']
		return access_token	
	except Exception as e:
		print ('Error recupera_meli_token() : '+str(e) )
		return False


def get_shipment_meli(shipping_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url='https://api.mercadolibre.com/shipments/'+str(shipping_id)+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		results = r.json()
		order_id=results['order_id']
		order_cost=results['order_cost']
		status = results['status']
		tracking_number = results['tracking_number']
		tracking_method = results['tracking_method']
		return dict(status=status, tracking_number=tracking_number, tracking_method=tracking_method)
	except Exception as e:
		print (' Error get_shipment_meli: '+ str(e))
		return False

def get_order_meli(seller_id, order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
		#print url
		r=requests.get(url, headers=headers)
		order_exist = len(r.json()['results'])
		#print json.dumps(order, indent=4, sort_keys=True)#ok
		#print shipping_id, feedback,shipment,id_order,order_status,date_created

		if order_exist>0:
			order = r.json()['results'][0]
			id_order = order['id']
			order_status = order['status']
			date_created = order['date_created'][:-10]
			shipping_id = order['shipping']['id']
			order_items = order['order_items']
			feedback = order['feedback']['sale']
			print ('SHIPPING_ID: ',shipping_id)
			print ('FEEDBACK: ',id_order, feedback)

			if shipping_id:
				shipment = get_shipment_meli(shipping_id, access_token)
				print ('SHIPMENT', shipment)

			fulfilled = False
			if feedback==None:
				fulfilled = False	
			else: 
				#{u'fulfilled': True, u'date_created': u'2019-06-10T13:43:39.000-04:00', u'status': u'hidden', u'id': 9040975678709, u'rating': u'positive'}
				fulfilled = feedback['fulfilled']
				#fulfilled_id = feedback['fulfilled']['id']

			print ('FULFILLED: ', fulfilled)

			seller_nickname = order['seller']['nickname']
			buyer_name = order['buyer']['first_name']+ ' '+order['buyer']['last_name']
			buyer_email = order['buyer']['email']

			list_items=[]
			for item in order_items:
				#print item
				seller_sku = item['item']['seller_sku']
				if seller_sku==None: #  No todos los productos tienen este campo ... buscar en seller_custom_field
					seller_custom_field = item['item']['eller_custom_field']
					seller_sku=seller_custom_field
				
				product_id = get_id_odoo_product(seller_sku)
				print ('SKU', seller_sku, 'Product id: ', product_id)
				if product_id:
					list_items.append(product_id)

			print (list_items)

			print ('RECUPERANDDO EL ID DEL CLIENTE DE MERCADO LIBRE')
			name='Mercado Libre API' # Cliente de Mercado Libre
			partner_id = get_id_odoo_buyer_by_name(name)
			print ('partner_id: ', partner_id)

			print ('RECUPERANDDO EL ID DEL COMERCIAL')
			usuario='APIsionate Meli' # Comercial
			comercial_id = consulta_users(usuario)
			print ('comercial_id', comercial_id)

			return dict(id_order=id_order, fulfilled=fulfilled, order_status=order_status, date_created=date_created,seller_nickname=seller_nickname,
			buyer_name=buyer_name, buyer_email=buyer_email, partner_id=partner_id, shipping_id=shipping_id, shipment=shipment, list_items=list_items, comercial_id=comercial_id)
		else:
			print ('La ordern : '+order_id+' No se encontro!')
			return False

	except Exception as e:
		return False

def make_map_meli_odoo(meli_data):
	try:
		order_status = meli_data['order_status']
		list_items = meli_data['list_items']

		if len(list_items)>0:
			marketplace_order_id = meli_data['id_order']
			print ('marketplace_order_id: ',marketplace_order_id )
			existe_orden = verify_exist_order_in_odoo(marketplace_order_id)# True ya nola crea, False La crea
			print ("Existe la Orden?", existe_orden)
			status = meli_data['order_status']

			if existe_orden:
				if status=='cancelled':
					print ('La Orden esta Cancelada Meli')
				else:
					print ('La Orden ya Existe en Odoo, actualizar')
					tracking_number = meli_data['shipment']['tracking_number']
					tracking_method = meli_data['shipment']['tracking_method']
					if tracking_method==None or tracking_number==None:
						pass
					else:
						tracking_number = meli_data['shipment']['tracking_number']
						tracking_method = meli_data['shipment']['tracking_method']
						print (tracking_method+'/'+tracking_number)
						update_sale_order(existe_orden, marketplace_order_id, tracking_method,  tracking_number)

			else:
				print ('La orden no existe y se creara')
				fecha_orden_venta_string = meli_data['date_created']
				fecha_orden_venta_datetime = datetime.strptime(fecha_orden_venta_string, '%Y-%m-%dT%H:%M:%S')
				#print (fecha_orden_venta_datetime)
				ahora = datetime.now()
				fecha_hora_actual_utc = str(ahora.utcnow())[:-7] #
				#print ('Fecha:',fecha_hora_actual_utc)
				#print (meli_data['fulfilled'])
				tracking_method = meli_data['shipment']['tracking_method']
				if tracking_method==None:
					tracking_method =''
				tracking_number = meli_data['shipment']['tracking_number']
				if tracking_number==None:
					tracking_number=''

				if meli_data['fulfilled']:
					warehouse_name='Meli Fulfilment'
					warehouse_id = get_meli_ful_warehouse_id_by_name(warehouse_name)
				else:
					warehouse_id=1
				print ('WAREHOUSE: ',warehouse_id)

				comercial_id=meli_data['comercial_id']

				values = {
				'partner_id': meli_data['partner_id'], # {u'id': 24137, u'name': u'Mercado Pago Publico en General'} 
				'state': 'draft',
				'confirmation_date': fecha_hora_actual_utc,
				'payment_term_id': 1,
				'user_id':comercial_id, # debe estar dado de alta como: APIsionate Meli
				'order_line': [(0, 0, {'product_id': meli_data['list_items'][0] })],
				'commitment_date': fecha_hora_actual_utc,
				'tracking_number': tracking_method+'/'+tracking_number,
				'marketplace':'MERCADO LIBRE',
				'marketplace_order_id':marketplace_order_id,
				'seller_marketplace': meli_data['seller_nickname'],
				'date_created': fecha_hora_actual_utc,
				'correo_marketplace':meli_data['buyer_email'],
				'client_order_ref' : meli_data['buyer_name'],
				'order_status':meli_data['order_status'],
				'warehouse_id':warehouse_id, 
				'picking_policy':'one',
				}
				print ('VALUES: ', values)
				#logging.info('PAYLOLOAD|'+values)
				data = {
					'model': "sale.order",
					'values': json.dumps(values),
				}
				response = api.execute('/api/create', type="POST", data=data)
				print ('ORDEN CREADA: ', marketplace_order_id )
				print (response)
				print ('===============================================================================================')
				return response
		else:
			print ('No se encontraron los articulos')
			return False
	
	except Exception as e:
		print ('Error make_map_meli_odoo(): '+str(e))
		return False


@app.route('/', methods=['GET'])
def index():
	return "Hola desde APIsionate"

@app.route('/post_orders_meli', methods=['POST'])
def webhook():
	try:
		if request.method == 'POST':
			content = request.json
			notification=json.loads(json.dumps(content))
			resource=notification['resource'].split("/")[1]
			order_id=notification['resource'].split("/")[2]
			seller_id=notification['user_id']
			topic=notification['topic']
			application_id=notification['application_id']
			attempts=notification['attempts']
			sent=notification['sent']
			received=notification['received']
			print (notification)
		'''
			if resource=='orders':
				print '================================================================================================'
				print 'INICIO:', seller_id, topic,resource,order_id, attempts
				access_token=recupera_meli_token(seller_id)
				orden = get_order_meli(seller_id, order_id, access_token)
				print 'ORDEN:',orden
				#logging.info('RESPUESTA ORDEN|'+orden)
				if orden:
					result  = make_map_meli_odoo(orden)
					print 'Resultado al intentar crear la Orden: ', result, ' Order Id: ', order_id
			#logging.info('NOTIFICATION|'+user_id+'|'+topic+'|'+resource+'|'+order_id+'|'+attempts)
			return '', 200
		else:
			abort(400)
		'''
	except Exception as e:
		return 'Error: '+str(e) 
		

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8080)