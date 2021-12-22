#!/usr/bin/env python
import cherrypy
import requests
import os
import json
import datetime
import base64
from collections import OrderedDict
import datetime
from datetime import datetime, date, time, timedelta
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
#import urllib.parse
from get_access_token_meli import obtener_token_meli
from get_access_token_meli_oficiales import obtener_token_meli_oficiales


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
		obtener_token_meli_oficiales()
		obtener_token_meli()
		print ('Se han regenarados los Tokens...')
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

def get_id_odoo_product(seller_sku):
	try:
		data = {
		'model': "product.template",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','name']),
		}
		response = api.execute('/api/search_read', data=data)
		#print (response)
		id_product=response[0]['id']
		return id_product
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
		response = api.execute('/api/search', data=data)
		existe=len(response)
		if existe==0: #No existe
			print('No existe la orden ')
			return False 
		else:
			print('Si existe la orden ')
			return True
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
	

def make_map_meli_odoo(meli_data):
	try:
		marketplace_order_id = meli_data['id_order']
		print ('marketplace_order_id: ',marketplace_order_id) 
		existe_orden = verify_exist_order_in_odoo(marketplace_order_id)# True ya nola crea, False La crea
		print ("Existe la Orden?", existe_orden)
		status = meli_data['order_status']


		if existe_orden==True or status=='cancelled':
			print ('La Orden ya existe en Odoo o esta cancelada en Meli')       
		else:
			print ('La orden no existe y se creara')
			fecha_orden_venta_string = meli_data['date_created']
			fecha_orden_venta_datetime = datetime.strptime(fecha_orden_venta_string, '%Y-%m-%dT%H:%M:%S')
			#print (fecha_orden_venta_datetime)
			ahora = datetime.now()
			fecha_hora_actual_utc = str(ahora.utcnow())[:-7] #
			#print ('Fecha:',fecha_hora_actual_utc)
			#print (meli_data['fulfilled'])
			
			if len(meli_data['shipment'])>0:
				tracking_number = meli_data['shipment']['tracking_number']
			else:
				tracking_number=''

			if meli_data['fulfilled']:
				warehouse_name='Meli Fulfilment'
				warehouse_id = get_meli_ful_warehouse_id_by_name(warehouse_name)
			else:
				warehouse_id=1
			print ('warehouse',warehouse_id)

			comercial_id=meli_data['comercial_id']


			values = {
			'partner_id': meli_data['partner_id'], # {u'id': 24137, u'name': u'Mercado Pago Publico en General'} 
			'state': 'draft',
			'confirmation_date': fecha_hora_actual_utc,
			'payment_term_id': 1,
			'user_id':comercial_id, # debe estar dado de alta como: APIsionate Meli
			'order_line': [(0, 0, {'product_id': meli_data['list_items'][0] })],
			'commitment_date': fecha_hora_actual_utc,
			'tracking_number': tracking_number,
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
			#print (values)
			data = {
				'model': "sale.order",
				'values': json.dumps(values),
			}
			response = api.execute('/api/create', type="POST", data=data)
			print ('Orden Creada: ', marketplace_order_id )
			return response
	
	except Exception as e:
		print ('Error make_map_meli_odoo(): '+str(e))
		return False



#---http://52.70.87.2:8080/post_orders_meli
class Root(object):
	@cherrypy.expose
	def index(self):        
		return 'No service found'

	@cherrypy.expose
	def post_orders_meli(self):
		postdata = cherrypy.request.body.read()
		#print (postdata)
		notification = json.loads(postdata)
		resource=notification["resource"].split("/")[1]
		#print (resource)
		user_id=notification["user_id"]
		topic=notification["topic"]
		application_id=notification["application_id"]
		attempts=notification["attempts"]
		sent=notification["sent"]
		received=notification["received"]
		access_token=None
		if resource=="orders":
			order_id=notification["resource"].split("/")[2]
			#print (order_id)
			access_token = recupera_meli_token(user_id)
			seller_id=user_id
			print ("Order Id:",order_id ,", Seller: ", seller_id,", access_token", access_token)

			order = get_order_meli(seller_id, order_id, access_token)
			print ('Detalle de la Orden : ', order)
			
			result  = make_map_meli_odoo(order)
			print ('Resultado al intentar crear la Orden: ', result)

			response = cherrypy.response
			response.status = '200 OK'
			print(response.status)
			#Stop execution
			#cherrypy.response.body = None
			cherrypy.response.status = 200
			#cherrypy.response.finalize()
			#ahora = datetime.now()
			#fecha_hora_actual_utc = str(ahora.utcnow())[:-7]
			#print (ahora)
			#print(fecha_hora_actual_utc.split(' '))
			#fecha_hora_utc=fecha_hora_actual_utc.split(' ')
			#hora_utc=fecha_hora_utc[1]
			#if hora_utc==''
			#cherrypy.engine.exit()
			print ('======================================================================')    
				
if __name__ == '__main__':
	cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port':8080,'server.thread_pool': 10,'server.socket_queue_size': 10,'log.screen': False,})
	cherrypy.tree.mount(Root(), '/')
	cherrypy.engine.start()
	cherrypy.engine.block()
	
	

