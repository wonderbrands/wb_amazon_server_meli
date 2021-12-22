#!/usr/bin/python3
import json
import requests
import urllib 
from pprint import pprint
from datetime import datetime, date, time, timedelta
import calendar
import logging
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import logging
import datetime

date_time = datetime.datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file="/home/ubuntu/meli/logs/Ordenes_canceladas_del_dia_"+fecha+".log"

logging.basicConfig(filename =log_file ,level=logging.INFO, format='%(asctime)s[%(levelname)s] (%(threadName)-s) %(message)s ')
#logging.basicConfig( level=logging.INFO, format='%(asctime)s[%(levelname)s] (%(threadName)-s) %(message)s ')

#url ='https://somosreyes-test-1289955.dev.odoo.com/'
url ='https://somosreyes.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

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
		elif type == "PUT":
				response = self.oauth.put(self.route(enpoint), data=data)
		else:
			response = self.oauth.get(self.route(enpoint), data=data)

	
		if response.status_code != 200:
			api.authenticate() # OJO COLOCAR PARA REACTIVAR TIMEOUT TOKEN
			raise Exception(pprint(response.json()))
		else:
			return response.json()


	def update_pickings_cancelled(self, picking_id):
		try:
			data = {
			"model":"stock.picking",
			"domain":json.dumps([["id","like", picking_id]]),
			"fields":json.dumps(["name", "state"]),
			}
			response =api.execute("/api/search_read", data=data)
			print (response)

			# state ='draft' es presupuesto, si state ='sale', ya se confirmo  es pedido tiene salidas 
			state=response[0]["state"]
			print ('state stock_picking:', state)
			#if state =='draft': 
			ids=response[0]["id"]
			#print (ids)
			
			values = {
				'state':'cancel', 
			}

			data = {
				"model": "stock.picking",
				'ids':[ids],
				"values": json.dumps(values),
			}

			response = api.execute('/api/write', type="PUT", data=data)
			print('update_pickings_cancelled:', response)
		except Exception as e:
			print ('Error en update_sale_order: '+str(e) )


	def get_sale_order_in_odoo(self, order_id):
		try:
			data = {
			"model":"sale.order",
			"domain":json.dumps([["marketplace_order_id","like", order_id]]),
			"fields":json.dumps(["name", "marketplace_order_id", "order_status", "state", "picking_ids"]),
			}
			response =api.execute("/api/search_read", data=data)
			#print ('response odoo:', response)
			# state ='draft' es presupuesto, si state ='sale', ya se confirmo  es pedido tiene salidas 
			name=response[0]["name"]
			return name
		except Exception as e:
			print ('Error get_sale_order_in_odoo(): '+str(e) )



	def update_sale_order_cancelled(self, order_id):
		try:
			data = {
			"model":"sale.order",
			"domain":json.dumps([["marketplace_order_id","like", order_id]]),
			"fields":json.dumps(["name", "marketplace_order_id", "order_status", "state", "picking_ids"]),
			}
			response =api.execute("/api/search_read", data=data)
			print ('Odoo Response: ' + str(response) )

			# state ='draft' es presupuesto, si state ='sale', ya se confirmo  es pedido tiene salidas 
			state=response[0]["state"]
			name=response[0]["name"]
			print ('sale_order state: ', state)

			if state!='cancel':
				if state =='sale': 
					picking = response[0]['picking_ids']
					for picking_id in picking:
						print('Pick :', picking_id)
						api.update_pickings_cancelled(picking_id)

				ids=response[0]["id"]
				print (ids)
		
				values = {'order_status': 'cancelled', 'state':'cancel'}

				data = {
					"model": "sale.order",
					'ids':[ids],
					"values": json.dumps(values),
				}

				print (data)
				response = api.execute('/api/write', type="PUT", data=data)

				print('Odoo: Se ha cancelado la orden: '+str(name)+' :'+ str(response))
				logging.info('Meli:'+str(order_id)+'|'+'Odoo:'+str(name)+'|'+ str(response) )
			else:
				print(str(name), ' ya esta cancelada')
				
		except Exception as e:
			print ('Error en update_sale_order: '+str(e) )


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

def get_pack_id_meli(order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url = 'https://api.mercadolibre.com/multiget?resource=orders&ids='+str(order_id)+'&access_token='+access_token

		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json(), indent=4, sort_keys=True))
		body_id = r.json()[0][0]['body']['id']
		pack_id = r.json()[0][0]['body']['pack_id']
		#print pack_id, body_id
		if pack_id:
			return pack_id
		else:
			return order_id
	except Exception as e:
		print ('Error get_pack_id_meli() : '+str(e))
		return False


def get_offset(date_created_from, date_created_to, seller_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&sort=date_asc&order.status=cancelled&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token
		r=requests.get(url, headers=headers)
		paging=r.json()['paging']
		#print ('paging: ', paging)
		total=paging['total']
		offset=paging['offset']
		limit=paging['limit']
		#print (total, offset, limit)
		numero_paginas=int(total/limit)
		#print (numero_paginas)
		offset = total-50
		if offset > 0:
			pass	
		else:
			offset=0

		#print ('offset:' , offset)
		return offset
	except Exception as e:
		print ('Error en get_offset(): '+str(e))


def get_orders_meli_cancelled(date_created_from, date_created_to, seller_id, access_token, offset):
	try:
		print (date_created_from, date_created_to)	
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&offset='+str(offset)+'&sort=date_asc&order.status=cancelled&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token
		r=requests.get(url, headers=headers)
		numero_de_ordenes=len(r.json()['results'])
		ordenes_canceladas=r.json()['results']
		#print (json.dumps(r.json()['results'], indent=4, sort_keys=True))
		#print('Numero de Ordenes:', numero_de_ordenes )
		lista_ordenes_canceladas = []
		
		for orden in ordenes_canceladas:
			orden_id= orden['id']
			orden_status= orden['status']
			#print (orden_id, orden_status, seller_id)
			lista_ordenes_canceladas.append(orden_id)
		return lista_ordenes_canceladas

	except Exception as e:
		raise e


api = RestAPI()
api.authenticate()
if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()

	ahora = datetime.datetime.utcnow()
	date_created_from = str(ahora)[:10]
	date_created_to = str(ahora)[:10]

	print(date_created_from, date_created_to)
	
	#date_created_from = '2021-07-06'
	#date_created_to = '2021-07-06'
	
	seller_id=160190870
	access_token = recupera_meli_token(seller_id)
	#print (access_token)
	offset = get_offset(date_created_from, date_created_to, seller_id, access_token)
	canceladas_160190870 = get_orders_meli_cancelled(date_created_from, date_created_to, seller_id, access_token, offset)
	print ('CANCELADAS 160190870:', canceladas_160190870)
	for cancelada in canceladas_160190870:
		print(cancelada)
		api.update_sale_order_cancelled(cancelada)
	

	seller_id=25523702	
	access_token = recupera_meli_token(seller_id)
	offset = get_offset(date_created_from, date_created_to, seller_id, access_token)
	canceladas_25523702 = get_orders_meli_cancelled(date_created_from, date_created_to, seller_id, access_token, offset)	
	print ('CANCELADAS 25523702:', canceladas_160190870)
	for cancelada in canceladas_25523702:
		print(cancelada)
		api.update_sale_order_cancelled(cancelada)

	
	

	
