#!/usr/bin/python
import sys
import json
import requests
from time import sleep
import datetime
from datetime import datetime, date, time, timedelta
import pprint 
import logging
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from connector_mariadb import *
from collections import OrderedDict

import email
import imaplib, re
import smtplib 
from email.mime.text import MIMEText

date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/ubuntu/meli/logs/orders_meli_'+str(fecha)+'.log'
logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)

url_sr ='https://somosreyes.odoo.com'
#url_sr ='https://somosreyes-test-652809.dev.odoo.com'
client_id_sr ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret_sr ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

connect=connect_to_orders()
cursor=connect['cursor']
connection_object=connect['connection_object']

def envia_email(notificacion):
	try:
		# Establecemos conexion con el servidor smtp de gmail
		mailServer = smtplib.SMTP('mail.somos-reyes.com',26)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login("serverubuntu@somos-reyes.com","Ttgo702#")
		# Construimos el mensaje simple
		mensaje=notificacion
		mensaje_enviar=mensaje
		mensaje = MIMEText(mensaje_enviar,"html", _charset="utf-8" )
		mensaje['From']="serverubuntu@somos-reyes.com"
		mensaje['To']= "moisantgar@gmail.com, lcheskin@gmail.com, sistemas@somos-reyes.com, aliensantiago1969@gmail.com"
		mensaje['Subject']="Error al intentar actualizar las existencias de Odoo a Venti."
		# Envio del mensaje
		mailServer.sendmail(mensaje['From'], mensaje["To"].split(",") ,  mensaje.as_string())
		print ("Se ha enviado un correo de aviso a Leon y Moi.") 
		# Cierre de la conexion
		mailServer.close()
	except Exception as e:
		print ("No se pudo enviar el email de aviso! -> "+ str(e) )

def update_orders_saved(order_id,status_order,shipment_status,carrier,tracking_id, respuesta_odoo,market_place_fee, shipping_cost, total_paid_amount, transaction_amount, status_detail):
	try:
		connect=connect_to_orders()
		cursor=connect['cursor']
		connection_object=connect['connection_object']

		sql_update_query = "UPDATE notify_meli SET status_order=%s, shipment_status=%s, carrier=%s, tracking_id=%s, respuesta_odoo =%s,market_place_fee= '%s', shipping_cost='%s', total_paid_amount='%s', transaction_amount='%s', status_detail=%s WHERE order_id = %s;"
		#print sql_update_query
		input = (status_order, shipment_status, carrier, tracking_id, str(respuesta_odoo), market_place_fee, shipping_cost, total_paid_amount, transaction_amount, status_detail, order_id)
		dato = cursor.execute(sql_update_query, input)
		connection_object.commit()
		print("Record Updated successfully with prepared statement")
	except mysql.connector.Error as error :
		print("Failed to update record to database: {}".format(error))

def colocar_nota_a_orden_meli(so_name, order_id, access_token):
    headers = {
        'content-type': 'application/json', 'Authorization': 'Bearer '+ access_token
        } 

    data={"note":so_name}

    url='https://api.mercadolibre.com/orders/'+str(order_id)+'/notes?access_token='+access_token
    try:
        r=requests.post(url, data=json.dumps(data), headers=headers)
        mi_json= r.json()
        print (json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')) )
        return True
    except Exception as e:
        print ('Error en colocar_nota_a_orden_meli(): '+str(e) )
        return False

def get_id_odoo_product(seller_sku, title, id_order):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name','list_price']),
		}
		response = api.execute('/api/search_read', data=data)
		print ('RESPONSE PRODUCT:', response )
		cantidad_productos=len(response)

		if cantidad_productos>0:
			id_product=response[0]['id']
			return id_product
		else:
			logging.info('Orden Id: '+ str(id_order)+' No se encontro el Id del Producto en Odoo. SKU: '+ str(seller_sku)+' '+title )
			return False

	except Exception as e:
		print('Error en get_id_odoo_product() : '+str(e))
		return False


def get_odoo_sub_product(product_id):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['id', '=', product_id]]),
		'fields': json.dumps(['id','default_code','name','list_price']),
		}
		response = api.execute('/api/search_read', data=data)
		print ('RESPONSE PRODUCT:', response )
		cantidad_productos=len(response)

		if cantidad_productos>0:
			return response[0]
		else:
			logging.info('Orden Id: '+ str(id_order)+' No se encontro el Id del Producto en Odoo. SKU: '+ str(seller_sku)+' '+title )
			return False
	except Exception as e:
		print('Error en get_id_odoo_product() : '+str(e))
		return False


def get_id_odoo_product_kit(seller_sku, title, id_order):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['default_code', '=', seller_sku]]),
		'fields': json.dumps(['id','default_code','name','list_price','is_kit', 'sub_product_line_ids']),
		}
		response = api.execute('/api/search_read', data=data)
		print ('RESPONSE KIT PRODUCT:', response)
		sub_product_line_ids = response[0]['sub_product_line_ids']

		lineas_pedido=[]
		list_items = []
		for sub_product in sub_product_line_ids:

			data = {
			'model': "sub.product.lines",
			'domain': json.dumps([['id', '=', sub_product]]),
			'fields': json.dumps(['id','product_id', 'quantity']),
			}
			response = api.execute('/api/search_read', data=data)
			product_id = response[0]['product_id'][0]
			item_selled = get_odoo_sub_product(product_id)
			print ('item_selled : ',item_selled)
			product_id = item_selled['id']
			quantity =  response[0]['quantity']
			unit_price = item_selled['list_price']
			title = item_selled['name']
			list_items.append(product_id)
			lineas_pedido.append( (0,0,{'product_id': product_id,'product_uom':1, 'product_uom_qty':quantity, 'price_unit': unit_price, 'name': title}) )
		
		return dict(lineas_pedido=lineas_pedido, list_items=list_items)
			
	except Exception as e:
		print('Error en get_id_odoo_product() : '+str(e))
		return False

def consulta_team(name_team):
		try:
			lista_urrea=[]
			data = {
			"model":"crm.team",
			"domain":json.dumps([["name","=", name_team]]),
			"fields":json.dumps(["id", "name"]),
			}
			response =api.execute("/api/search_read", data=data)
			id_equipo = response[0]['id']
			#print response
			return id_equipo
		except Exception as e:
			print('Error en consulta_equipo() : '+str(e))
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
			'fields': json.dumps(['id','name', 'marketplace_order_id']),
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

def get_name_order_in_odoo(order_id):
	try:
		data = {
			'model': "sale.order",
			'domain': json.dumps([['id', '=', order_id ]]),
			'fields': json.dumps(['id','name', 'marketplace_order_id']),
			'limit': 1
		}
		response = api.execute('/api/search_read', data=data)
		existe=len(response)
		if existe==0: #No existe
			print('No se ha encontrado el Nombre de la orden ')
			return False 
		else:
			print('Se ha encontrado el Nombre de la orden ')
			name=response[0]['name']
			return name
	except Exception as e:
		print('Error en get_name_order_in_odoo() : '+str(e))
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
		return False
		print('Error en get_id_odoo_buyer_by_name() : '+str(e))

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
		return False
		print('Error en get_meli_ful_warehouse_id_by_name() : '+str(e))
	

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
				api.authenticate()# OJO COLOCAR PARA RECUPERAR EL ACCES TOKEN DE ODOO, SE PIERDE EN 1 HORA
				raise Exception(pprint(response.json()))
			else:
				#print response.json()
				return response.json()

		except Exception as e:
			print ('Error al realizar el request en: Execute()'+str(e) )
			return False
		
api = RestAPI()
api.authenticate()
null='null'
false=False

#--- 1. recuperamos el token de CBT MELI
def recupera_meli_token(user_id):
	try:
		#print 'USER ID:', user_id
		token_dir=''
		if user_id == 25523702:# Usuario de SOMOS REYES VENTAS
			token_dir='/home/ubuntu/meli/tokens_meli.txt' 
		elif user_id == 160190870:# Usuario de SOMOS REYES OFICIALES
			token_dir='/home/ubuntu/meli/tokens_meli_oficiales.txt'
		#print token_dir

		archivo_tokens=open(token_dir, 'r')
		#print 'archivo_tokens', archivo_tokens
		tokens=archivo_tokens.read()
		#print 'tokens',tokens
		tokens_meli = json.loads(tokens)
		#print (tokens_meli)
		archivo_tokens.close()
		access_token=tokens_meli['access_token']
		#print access_token
		return access_token	
	except Exception as e:
		print ('Error recupera_meli_token() : '+str(e) )
		return False


def get_shipment_meli(shipping_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'Authorization': 'Bearer '+ access_token}
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

def get_logistic_type_item_meli(mlm):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/items/'+mlm+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json(), indent=4, sort_keys=True))
		existe_item = len( r.json()['shipping'])
		
		if existe_item:
			item = r.json()['shipping']
			#print(json.dumps(item, indent=4, sort_keys=True))
			shipping_logistic_type = item['logistic_type']
			return shipping_logistic_type
		else:
			return False	
			
	except Exception as e:
		print ('Error en: '+str(e) )
		return False


def get_payment_method_id(payment_type):
	try:
		formas_pago_odoo = {'01':1, #Efectivo
							'02':2, #Cheque nominativo
							'03':3, #Transferencia electronica de fondos
							'04':4, #Tarjeta de Credito
							'05':5, #Monedero Electronico
							'06':6, #Dinero Electronico
							'08':7, #Vales de despensa
							'12':8,#Dacion en pago
							'13':9, #Pago por subrogacion 
							'14':10,#Pago por consignacion
							'15':11,#Condonacion
							'17':12,#Compensacion
							'23':13,#Novacion
							'24':14,#Confusion
							'25':15,#Remision de deuda
							'26':16,#Prescripcion o caducidad
							'27':17,#A satisfaccion del acreedor
							'28':18,#Tarjeta de Debito
							'29':19,#Tarjeta de Servicio
							'30':20,#Aplicacion de anticipos
							'99':21,#Por definir
							'31':22,#Intermediario pagos
							}
				
		formas_de_pago_meli_sat = { "credit_card":"04", 
									"debit_card":"28",
									"prepaid_card":"06",
									"atm":"03",
									"ticket":"01",
									"account_money":"06",
									"digital_currency":"06"}

		if payment_type == 'credit_card':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'debit_card':
			forma_pago_SAT =formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'prepaid_card':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'atm':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'ticket':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'account_money':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'digital_currency':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		else :
			forma_pago_SAT = '99'
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]

		print ('Forma de Pago SAT: ', forma_pago_SAT,formas_pago_odoo_id )
		return formas_pago_odoo_id

	except Exception as e:
		print('Error|get_payment_method_id(): '+str(e) )
		return False
	
def get_order_meli(seller_id, order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
		#print url
		r=requests.get(url, headers=headers)
		order_exist = len(r.json()['results'])
		#print (json.dumps(r.json()['results'], indent=4, sort_keys=True))#ok
		#print shipping_id, feedback,shipment,id_order,order_status,date_created
		shipping_labels=''

		if order_exist>0:
			order = r.json()['results'][0]
			id_order = order['id']
			order_status = order['status']
			date_created = order['date_created'][:-10]
			shipping_id = order['shipping']['id']
			#shipping_status = order['shipping']['status']
			shipping_status=''
			order_items = order['order_items']
			feedback = order['feedback']['sale']
			print ('SHIPPING_ID: ',shipping_id)
			print ('FEEDBACK: ',id_order, feedback)
			
			shipment= {}

			if shipping_id:
				shipment = get_shipment_meli(shipping_id, access_token)
				print ('SHIPMENT', shipment)
				shipping_labels='https://api.mercadolibre.com/shipment_labels?shipment_ids='+str(shipping_id)+'&response_type=zpl2&access_token='
			else:
				shipment={'status': shipping_status, u'tracking_method': '', u'tracking_number':''}
				print ('SHIPMENT', shipment)
				shipping_labels=''

			fulfilled = False
			if feedback==None:
				fulfilled = False	
			else: 
				fulfilled = feedback['fulfilled']
				#fulfilled_id = feedback['fulfilled']['id']

			print ('FULFILLED: ', fulfilled)
			
			buyer_name = order['buyer']['nickname'] #+'/'+order['buyer']['first_name']+ ' '+order['buyer']['last_name']
			buyer_email ='' # order['buyer']['email']
			seller_nickname = order['seller']['nickname']

			#--- Pago
			payments = order['payments']
			for payment in payments:
				#payment_market_place_fee = payment['marketplace_fee']
				payment_market_place_fee = 17.5
				payment_shipping_cost = payment['shipping_cost']
				payment_total_paid_amount = payment['total_paid_amount']
				payment_transaction_amount = payment['transaction_amount']
				payment_status_detail = payment['status_detail']
				
				payment_method_id = payment['payment_method_id']
				payment_type = payment['payment_type']
				payment_method_id = get_payment_method_id(payment_type)
				print ('payment_method_id', payment_method_id)
				

				print ('PAGO: ',payment_method_id, payment_type, payment_total_paid_amount, payment_transaction_amount, payment_market_place_fee, payment_total_paid_amount, payment_status_detail )

			list_items=[]
			list_item_selled=[]
			item_selled = {}
			lineas_pedido=[]
			es_combo=False
			combo_detail=''
			for item in order_items:
				print (item)
				mlm = item['item']['id']
				print ('MLM: ', mlm)
				logistic_type  = get_logistic_type_item_meli(mlm)
				print ('LOGISTICA MELI: ', logistic_type)

				seller_sku = item['item']['seller_sku']
				print ('SELLER SKU:', seller_sku)

				if seller_sku==None: #  No todos los productos tienen este campo ... buscar en seller_custom_field
					print ('NO TIENE SELLER SKU')
					seller_custom_field = item['item']['seller_custom_field']
					print ('seller_custom_field: ', seller_custom_field)
					seller_sku=seller_custom_field

				#sale_fee = item['sale_fee']
				unit_price = item['unit_price']/1.16
				quantity = item['quantity']	
				print ('seller_sku->', seller_sku, quantity)
				title =  item['item']['title']

				if 'COMBO' in seller_sku:
					combo = get_id_odoo_product_kit(seller_sku, title, id_order)
					lineas_pedido = combo['lineas_pedido']
					list_items = combo['list_items']
					es_combo=True
					combo_detail=str(seller_sku)+'|'+str(title)+'|'+str(quantity)+'|$'+str(item['unit_price'])
				else:	
					product_id = get_id_odoo_product(seller_sku, title, id_order)
					if product_id:
						item_selled['seller_sku']=seller_sku
						item_selled['product_id']=product_id
						item_selled['quantity']=quantity
						item_selled['unit_price']=unit_price

						list_items.append(product_id)
						list_item_selled.append(item_selled)

						lineas_pedido.append( (0,0,{'product_id': product_id,'product_uom':1, 'product_uom_qty':quantity, 'price_unit': unit_price, 'name': title}) )

					print ('SKU', seller_sku, 'Product id: ', product_id, item_selled)

			print ('Lineas de pedido: ', lineas_pedido)
	
			
			print ('RECUPERANDDO EL ID DEL CLIENTE DE MERCADO LIBRE')
			name='Mercado Libre API' # Cliente de Mercado Libre
			partner_id = get_id_odoo_buyer_by_name(name)
			print ('partner_id: ', partner_id)

			print ('RECUPERANDDO EL ID DEL COMERCIAL')
			usuario='Karen Monroy' # Comercial
			comercial_id = consulta_users(usuario)
			print ('comercial_id', comercial_id)

			return dict(id_order=id_order, fulfilled=fulfilled, order_status=order_status, date_created=date_created,seller_nickname=seller_nickname, buyer_name=buyer_name, buyer_email=buyer_email, partner_id=partner_id, shipping_id=shipping_id, shipment=shipment, list_items=list_items, lineas_pedido=lineas_pedido,quantity=quantity,comercial_id=comercial_id, total_paid_amount=payment_total_paid_amount, transaction_amount=payment_transaction_amount, market_place_fee=payment_market_place_fee, shipping_cost=payment_shipping_cost, status_detail=payment_status_detail, logistic_type=logistic_type, shipping_labels=shipping_labels, es_combo=es_combo, combo_detail=combo_detail,payment_method_id=payment_method_id
			)
		else:
			print ('La ordern : '+order_id+' No se encontro!')
			return False
	
	except Exception as e:
		print ('Error en get_order_meli() '+ str(e) )
		return False



#-------------------- Funciones de Webhooks---------------------------------------------------------------------------
def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        return None

def get_stock_real_from_odoo(product_id):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['id', '=', product_id]]),
		'fields': json.dumps(['default_code','stock_real','stock_exclusivas', 'stock_urrea', 'stock_markets']),
		}
		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))
		stock_real = response[0]['stock_real']
		stock_exclusivas = response[0]['stock_exclusivas']
		stock_urrea = response[0]['stock_urrea']
		stock_markets =response[0]['stock_markets']
		default_code = response[0]['default_code']
		return dict(default_code=default_code, stock_real=stock_real, stock_exclusivas=stock_exclusivas, stock_urrea=stock_urrea, stock_markets=stock_markets)
	except Exception as e:
		print('ERROR|get_stock_real_from_odoo()|'+str(e) )
		api.authenticate()
		return False

def update_stock_markets(product_id, stock_markets_nuevo):
	try:
		values = {'stock_markets' : stock_markets_nuevo,}
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


def get_mlm_from_meli(user_id, sku, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		'Authorization': 'Bearer '+ access_token
		}
		url='https://api.mercadolibre.com/users/'+str(user_id)+'/items/search?sku='+sku+'&status=active&access_token='+access_token
		r=requests.get(url, headers=headers)
		print (url)
		item_id_meli = r.json()['results'][0]
		return item_id_meli

	except Exception as e:
		raise e

def update_product_meli(item_id_meli, quantity, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		'Authorization': 'Bearer '+ access_token
		}
		data={'available_quantity': quantity}  

		url='https://api.mercadolibre.com/items/'+str(item_id_meli)+'?access_token='+access_token
		print (url)
		r=requests.put(url, headers=headers, data=json.dumps(data) )
		#print r.json()
		print ('Actualizado ', item_id_meli)

	except Exception as e:
		raise e


def webhook_venti(product_id, piezas_pedido):
	try:
		stock_markets_nuevo=0
		stock_from_odoo = get_stock_real_from_odoo(product_id)
		default_code = stock_from_odoo['default_code']
		stock_real = stock_from_odoo['stock_real'] 
		stock_markets_actual = stock_from_odoo['stock_markets']
		stock_exclusivas = stock_from_odoo ['stock_exclusivas']
		stock_urrea = stock_from_odoo ['stock_urrea']
		
		print ('ODOO| stock_real:', stock_real, ' piezas_pedido:', piezas_pedido)

		stock_markets_nuevo = (stock_real + stock_exclusivas + stock_urrea) - piezas_pedido
		if stock_markets_actual==0:
			stock_markets_nuevo = stock_real + stock_exclusivas + stock_urrea - piezas_pedido
		else:
			stock_markets_nuevo = stock_markets_actual - piezas_pedido
			print ('ODOO|stock_markets_actual:',stock_markets_actual, ' piezas_pedido:', piezas_pedido, ' stock_markets_nuevo',  stock_markets_nuevo)
		
		print ('ODOO|stock_real:',stock_real,', stock_exclusivas:', stock_exclusivas, ', stock_urrea:', stock_urrea, '-Pedidas:  ', piezas_pedido, '-> Nuevo stock_markets: ', stock_markets_nuevo)

		stock_mercadolibre =  stock_real + stock_exclusivas + stock_urrea - piezas_pedido
		if stock_mercadolibre < 0:
			stock_mercadolibre=0

		stock_linio = stock_real + stock_exclusivas - piezas_pedido
		if stock_linio < 0:
			stock_linio=0

		stock_amazon =  stock_real + stock_exclusivas + stock_urrea - piezas_pedido
		if stock_amazon < 0:
			stock_amazon = 0

		stock_prestashop =  stock_real + stock_exclusivas + stock_urrea - piezas_pedido
		if stock_prestashop < 0:
			stock_prestashop = 0

		stock_walmart =  stock_real + stock_exclusivas - piezas_pedido
		if stock_walmart < 0:
			stock_walmart = 0

		stock_claroshop =  stock_real + stock_exclusivas + stock_urrea - piezas_pedido
		if stock_claroshop < 0:
			stock_claroshop = 0

		print(default_code,',',stock_amazon,',',stock_linio,',',stock_prestashop,',',stock_claroshop,',',stock_mercadolibre)
		access_token_venti = get_token_venti()

		if stock_mercadolibre < stock_markets_nuevo:
			stock_markets_nuevo = stock_mercadolibre		
		
		#update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti)
		
		#--- El mismo SKU que tenemos en ODOO lo vendemos para las dos cuentas: SOMOS REYES VENTAS Y SOMOS REYE SOFICIALES
		#users_ids = [25523702, 160190870]
		#for user_id in users_ids:
		#	access_token = recupera_meli_token(user_id)
		#	item_id_meli = get_mlm_from_meli(user_id, default_code, access_token)
		#	respuesta_meli = update_product_meli(item_id_meli, stock_mercadolibre,access_token)

		#--- Actualiza el campo stock_markets en Odoo.

		#update_stock_markets(product_id, stock_markets_nuevo)
		#print ('Actualizando en Odoo SKU: ', default_code, ', stock_markets_nuevo: ', stock_markets_nuevo)
	
	except Exception as e:
		print ('Error|webhook_venti(): '+str(e) )
		return False

def update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		body={
		        "sku": str(default_code),
				"channelData": [
					{
						"channel": "mercadolibre",
						"quantity": int(stock_mercadolibre)
					},
					{
						"channel": "linio",
						"quantity":int(stock_linio)
					},
					{
						"channel": "amazon",
						"quantity": int(stock_amazon)
					},
					{
						"channel": "prestashop",
						"quantity": int(stock_prestashop)
					}, 
					{
						"channel": "walmart",
						"quantity": int(stock_walmart)
					}, 
					{
						"channel": "claroshop",
						"quantity": int(stock_claroshop)
					}, 
				]
			}

		url='https://ventiapi.azurewebsites.net/api/stock/updatepricestockbychannel'
		r=requests.post(url, headers=headers, data= json.dumps(body) )
		
		print ("VENTI|"+r.text)
		
		print ('INFO|Actualizando SKU: '+str(default_code)+'|Meli '+str(stock_mercadolibre)+'|Linio '+str(stock_linio)+' |Amazon  '+str(stock_amazon)+'|Prestashop  '+str(stock_prestashop)+'|Walmart  '+str(stock_walmart)+' |ClaroShop  '+str(stock_claroshop)+' en Venti.')

		if "Producto no encontrado" in r.text:
			print (r.text+' SKU: ', default_code )

		if "Authorization has been denied for this request" in r.text:
			#--- Envia email de error y recuperacion de Token
			notificacion='ERROR VENTI|update_product_venti(): Authorization has been denied for this request \n'
			notificacion+='ERROR VENTI|en programa que inserta las SO de Meli a Odoo, regenera token de Venti.'

			envia_email(notificacion)
			#get_token_venti()
			
	except Exception as e:
		print('ERROR|update_product_venti|', str (e))
		return False

	
#--------------------  Fin Funciones de Webhooks---------------------------------------------------------------------------

def make_map_meli_odoo(meli_data):
	try:
		name_team = 'Mercado Libre' #--Colocar en archivo de configuracion
		team_id = consulta_team(name_team)
		order_status = meli_data['order_status']
		list_items = meli_data['list_items']
		
		#---1)20190925--Activa el webhook de odoo hacia Venti cada vez que se crear un SO en Odoo proveniente de Meli------
		print ('list_items EN MAPEO DE CADA ITEM DE LA ORDEN:', list_items)
		i=0
		for product_id in list_items:
			piezas_pedido= int(meli_data['lineas_pedido'][i][2]['product_uom_qty'])
			print ('piezas_pedido:',piezas_pedido)

			###webhook_venti(product_id, piezas_pedido)
			
		#---Finaliza Activa el webhook de odoo hacia Venti cada vez que se crear un SO en Odoo proveniente de Meli------

		shipping_labels=''
		#if len(list_items)>0:
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
			ahora = datetime.now()
			fecha_hora_actual_utc = str(ahora.utcnow())[:-7] #
			tracking_method = meli_data['shipment']['tracking_method']

			if tracking_method==None:
				tracking_method =''
			tracking_number = meli_data['shipment']['tracking_number']
			if tracking_number==None:
				tracking_number=''
			
			state_so = 'draft'
			if meli_data['logistic_type']=='fulfillment':
				warehouse_name='Mercado Libre Full' #'Meli Fulfilment'
				warehouse_id = get_meli_ful_warehouse_id_by_name(warehouse_name)
				state_so = 'sale'
				print ('PEDIDDO DE VENTA DE FULLFILMENT')
			else:
				warehouse_id=1
				shipping_labels=meli_data['shipping_labels']
				state_so = 'draft'

			print ('WAREHOUSE: ',warehouse_id)

			comercial_id=meli_data['comercial_id']
			quantity =meli_data['quantity']
			lineas_pedido=meli_data['lineas_pedido']
			es_combo = meli_data['es_combo']
			
			if es_combo == True:
				state_so = 'draft' #---- para que revisen los precios no permitir la confirmación. #20201109

			combo_detail = meli_data['combo_detail']
			payment_method_id = meli_data['payment_method_id']
			shipping_id = meli_data['shipping_id']
			print ('SHIPING_ID al crear la Orden:',shipping_id)

			values = {
			'partner_id': meli_data['partner_id'],
			'state': state_so,
			'confirmation_date': fecha_orden_venta_string, #fecha_hora_actual_utc,
			'payment_term_id': 1,
			'user_id':comercial_id, 
			'order_line':lineas_pedido, #[(0,0,{'product_id': meli_data['list_items'][0],'product_uom':1, 'product_uom_qty':quantity })],#[(0, 0, { 'product_uom': '1', 'product_id': meli_data['list_items'][0],'product_uom_qty': str(quantity) })],
			'commitment_date': fecha_orden_venta_string,
			'tracking_number': tracking_method+'/'+tracking_number,
			'etiqueta_meli':shipping_labels, 
			'marketplace':'MERCADO LIBRE',
			'marketplace_order_id':marketplace_order_id,
			'seller_marketplace': meli_data['seller_nickname'],
			'date_created': fecha_orden_venta_string,
			'correo_marketplace':meli_data['buyer_email'],
			'client_order_ref' : meli_data['buyer_name'],
			'order_status':meli_data['order_status'],
			'warehouse_id':warehouse_id, 
			'picking_policy':'one',
			'combo':es_combo,
			'combo_detail':combo_detail,
			'team_id':team_id, 
			'l10n_mx_edi_payment_method_id':payment_method_id,
			'shipping_id':shipping_id,  
			}
			#print ('VALUES PAYLOAD: ', values)
			#logging.info('PAYLOLOAD|'+values)
			data = {
				'model': "sale.order",
				'values': json.dumps(values),
			}
			print (data)
			
			response = api.execute('/api/create', type="POST", data=data)
			print ('Respuesta al intentar crear la Orden en Odoo: ',response)
			print ('===============================================================================================')
			return response
		
		#else:
		#	print 'No se encontraron los articulos'
		#	return False
	
	except Exception as e:
		print ('Error make_map_meli_odoo(): '+str(e))
		return False

def get_result_orders():
	try:
		#print 'Recuperando ordenes notificadas....'
		query='SELECT user_id, car_id, order_id FROM notify_meli WHERE status_order IS NULL or status_order="";'
		cursor.execute(query)
		result = cursor.fetchall()
		cursor.close()
		connection_object.close()
		return result
	except mysql.connector.Error as mysql_error:
		print ("Error executing query: %s" % (str(mysql_error)) )
		return False

def procesa_pedido_normal(orden, access_token):
	try:
		result=''
		if orden:
			order_id =orden['id_order']  	
			order_status = orden['order_status']
			shipment_status = orden['shipment']['status']
			tracking_method = orden['shipment']['tracking_method']
			tracking_number = orden['shipment']['tracking_number']
			market_place_fee = orden['market_place_fee']
			shipping_cost = orden['shipping_cost']
			total_paid_amount = orden['total_paid_amount']
			transaction_amount = orden['transaction_amount']
			status_detail = orden['status_detail']
			
			result  = make_map_meli_odoo(orden)
			print ('Resultado al intentar crear la Orden: ', result, ' Order Id: ', order_id)
			if result:
				update_orders_saved(order_id, order_status,shipment_status,tracking_method,tracking_number, str(result), market_place_fee, shipping_cost, total_paid_amount, transaction_amount, status_detail)
				so_name = get_name_order_in_odoo(result[0])
				print ('La orden se ha generado en Odoo con nombre: ' + str(so_name) )
				colocar_nota_a_orden_meli(so_name, order_id, access_token)

		else:
			print (result)

	except Exception as e:
		print ('Error procesa_pedido_normal(): ' +str (e) )
		print ('========================================================================================')
		return False

def get_order_meli_multi(seller_id, pedidos_de_carrito, access_token):
	try:

		lista_ids=''
		for order_id in pedidos_de_carrito:
			lista_ids+=str(order_id)+','

		ids = lista_ids[:-1]
		print ('IDS: ',ids )
		shipping_labels=''
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
		url = 'https://api.mercadolibre.com/multiget?resource=orders&ids='+str(ids)+'&access_token='+str(access_token)
		print (url)
		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json(), indent=4, sort_keys=True))
		numero_pedidos= len(r.json()[0])
		lineas_pedido=[]
		list_items=[]
		list_item_selled=[]
		payment_shipping_cost = 0.0
		payment_total_paid_amount = 0.0
		payment_transaction_amount = 0.0
		ids_order=''

		pedidos_de_carrito= r.json()[0]
		for pedido in pedidos_de_carrito:
			order = pedido['body']
			pack_id_order = order['pack_id']

			id_order = order['id']
			order_status = order['status']
			date_created = order['date_created'][:-10]
			shipping_id = order['shipping']['id']
			
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
				shipping_labels = 'https://api.mercadolibre.com/shipment_labels?shipment_ids='+str(shipping_id)+'&response_type=zpl2&access_token='

			fulfilled = False
			if feedback==None:
				fulfilled = False	
			else: 
				fulfilled = feedback['fulfilled']
				#fulfilled_id = feedback['fulfilled']['id']

			print ('FULFILLED: ', fulfilled)
			
			buyer_name = order['buyer']['nickname'] #+'/'+order['buyer']['first_name']+ ' '+order['buyer']['last_name']
			buyer_email = ''#order['buyer']['email']
			seller_nickname = order['seller']['nickname']

			#--- Pago

			payments = order['payments']
			for payment in payments:
				#payment_market_place_fee = payment['marketplace_fee']

				payment_market_place_fee=0.0
				payment_shipping_cost += payment['shipping_cost']
				payment_total_paid_amount += payment['total_paid_amount']
				payment_transaction_amount += payment['transaction_amount']
				payment_status_detail = payment['status_detail']

				payment_method_id = payment['payment_method_id']
				payment_type = payment['payment_type']
				payment_method_id = get_payment_method_id(payment_type)

				print ('PAGO: ', payment_total_paid_amount, payment_transaction_amount, payment_market_place_fee, payment_total_paid_amount, payment_status_detail, payment_method_id, payment_type )

			
			item_selled = {}
			#lineas_pedido=[]
			es_combo=False
			combo_detail =''
			for item in order_items:
				print( item)
				mlm = item['item']['id']
				print ('MLM: ', mlm)
				logistic_type  = get_logistic_type_item_meli(mlm)
				print ('LOGISTICA MELI: ', logistic_type)

				seller_sku = item['item']['seller_sku']
				print ('SELLER SKU:', seller_sku)

				if seller_sku==None: #  No todos los productos tienen este campo ... buscar en seller_custom_field
					print ('NO TIENE SELLER SKU')
					seller_custom_field = item['item']['seller_custom_field']
					print ('seller_custom_field: ', seller_custom_field)
					seller_sku=seller_custom_field

					

				title =  item['item']['title']
				#sale_fee = item['sale_fee']
				unit_price = item['unit_price']/1.16
				quantity = item['quantity']	
				print ('seller_sku->', seller_sku, quantity)

				if 'COMBO' in seller_sku:
					combo = get_id_odoo_product_kit(seller_sku, title, id_order)
					lineas_pedido = combo['lineas_pedido']
					list_items = combo['list_items']
					es_combo=True
					combo_detail=str(seller_sku)+'|'+str(title)+'|'+str(quantity)+'|$'+str(item['unit_price'])
				else:
					product_id = get_id_odoo_product(seller_sku, title, id_order)
					if product_id:
						item_selled['seller_sku']=seller_sku
						item_selled['product_id']=product_id
						item_selled['quantity']=quantity
						item_selled['unit_price']=unit_price

						list_items.append(product_id)			
						list_item_selled.append(item_selled)

						lineas_pedido.append( (0,0,{'product_id': product_id,'product_uom':1, 'product_uom_qty':quantity, 'price_unit': unit_price, 'name': title}) )

					print ('SKU', seller_sku, 'Product id: ', product_id, item_selled)

			print ('Lineas de pedido: ', lineas_pedido)
	
			
			print ('RECUPERANDDO EL ID DEL CLIENTE DE MERCADO LIBRE')
			name='Mercado Libre API' # Cliente de Mercado Libre
			partner_id = get_id_odoo_buyer_by_name(name)
			print ('partner_id: ', partner_id)

			print ('RECUPERANDDO EL ID DEL COMERCIAL')
			usuario='Karen' # Comercial
			comercial_id = consulta_users(usuario)
			print ('comercial_id', comercial_id)
			ids_order=str(pack_id_order)+':'+str(ids)
			print ('IDS PASADOS: ', ids_order)
		return dict(id_order=ids_order, fulfilled=fulfilled, order_status=order_status, date_created=date_created,seller_nickname=seller_nickname,	buyer_name=buyer_name, buyer_email=buyer_email, partner_id=partner_id, shipping_id=shipping_id, shipment=shipment, list_items=list_items, lineas_pedido=lineas_pedido,quantity=quantity,comercial_id=comercial_id, total_paid_amount=payment_total_paid_amount, transaction_amount=payment_transaction_amount, market_place_fee=payment_market_place_fee, shipping_cost=payment_shipping_cost, status_detail=payment_status_detail, logistic_type=logistic_type, shipping_labels=shipping_labels, es_combo=es_combo, combo_detail=combo_detail, payment_method_id=payment_method_id)
		
	except Exception as e:
		print ('Error en get_order_meli_multi() '+ str(e) )
		return False

def procesa_pedido_carrito(orden, access_token):
	try:
		result=''
		if orden:
			order_status = orden['order_status']
			shipment_status = orden['shipment']['status']
			tracking_method = orden['shipment']['tracking_method']
			tracking_number = orden['shipment']['tracking_number']

			market_place_fee = orden['market_place_fee']
			shipping_cost = orden['shipping_cost']
			total_paid_amount = orden['total_paid_amount']
			transaction_amount = orden['transaction_amount']
			status_detail = orden['status_detail']
			order_ids=orden['id_order']
			pack_orders = order_ids.split(':')
			print (pack_orders)
			orders=pack_orders[1].split(',')
		
			result  = make_map_meli_odoo(orden)
			print ('Resultado al intentar crear la Orden: ', result, ' Order Id: ', order_ids)
			for order_id in orders:
				print (order_id)
				if result:
					update_orders_saved(order_id, order_status,shipment_status,tracking_method,tracking_number, str(result), market_place_fee, shipping_cost, total_paid_amount, transaction_amount, status_detail)
					so_name = get_name_order_in_odoo(result[0])
					print (order_id, ' La orden se ha generado en Odoo con nombre: ' + str(so_name) )
					colocar_nota_a_orden_meli(so_name, order_id, access_token)
			#sleep(1) # Time in seconds

		else:
			print (result)

	except Exception as e:
		print ('Error procesa_pedido_carrito(): ' +str (e) )



if __name__ == '__main__':
	ordenes = get_result_orders()
	print ('Ordenes: ',ordenes)

	carro_anterior=None
	orden_anterior=None
	seller_anterior=None
	lista_pedidos=[]
	datos={}
	carro={}
	lista_carros=[]
	for orden in ordenes:
		seller={}
		carro={}
		seller_actual =orden[0] 
		carro_actual=orden[1]
		orden_actual=orden[2]

		if carro_actual==carro_anterior and seller_actual == seller_anterior:
			lista_pedidos.append(orden_anterior)			
		else:
			lista_pedidos.append(orden_anterior)

			seller['seller_id']=seller_anterior
			lista_pedidos.append(seller)

			carro['car_id']=carro_anterior
			lista_pedidos.append(carro)

			print ('Lista Pedidos: ',lista_pedidos)
			lista_carros.append(lista_pedidos)	
			lista_pedidos=[]

		carro_anterior=carro_actual
		orden_anterior=orden_actual
		seller_anterior=seller_actual

	print ('Lista carros: ', lista_carros)
	print ('============================================================================================================')


for carro in lista_carros[1:]:
	#print carro
	carrito = carro[-1]['car_id']
	if carrito:
		carrito = carro[-1]['car_id']
		seller_id =  int(carro[-2]['seller_id'])
		pedidos= carro[:-2]
		#print carrito, seller_id, pedidos
		
		if len(carrito)>10: # Es Carrito de Compras
			#-----------------------------INICIO Nuevo 2019-12-02
			if len(pedidos)>10:
				pedidos1 = pedidos[:10] 
				print ('CARRO1:', carrito, pedidos1, seller_id, access_token )
				orden=get_order_meli_multi(seller_id, pedidos1, access_token)
				print  ('CARRRO ORDEN1: ', orden )
				procesa_pedido_carrito(orden, access_token)
				print ('============================================================================================================')

				otros =  len(pedidos) - 10
				pedidos2 =  pedidos[:otros] 
				#procesar el segundo grupo 
				print ('CARRO2:', carrito, pedidos2, seller_id, access_token )
				orden=get_order_meli_multi(seller_id, pedidos2, access_token)
				print  ('CARRRO ORDEN2: ', orden )
				procesa_pedido_carrito(orden, access_token)
				print ('============================================================================================================')
			else:# Si tenemos un carrito hasta con 10 pedidos.
				#------------------------------FIN Nuevo 2019-12-02
				access_token=recupera_meli_token(seller_id)
				print ('CARRO:', carrito, pedidos, seller_id, access_token )
				orden=get_order_meli_multi(seller_id, pedidos, access_token)

				print  ('CARRRO ORDEN: ', orden )
				procesa_pedido_carrito(orden, access_token)
				print ('============================================================================================================')

		else:
			access_token=recupera_meli_token(seller_id)
			print ('NORMAL', carrito, pedidos, seller_id, access_token )
			orden=get_order_meli(seller_id, pedidos[0], access_token)
			print ('NORMAL ORDEN: ', orden)
			procesa_pedido_normal(orden, access_token)
			print ('============================================================================================================' )