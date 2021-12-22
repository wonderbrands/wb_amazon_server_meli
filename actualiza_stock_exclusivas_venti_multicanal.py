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
from collections import OrderedDict

date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/ubuntu/meli/logs/actualizando_exclusivas_venti_'+str(fecha)+'.log'
logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)

url_sr ='https://somosreyes.odoo.com'
#url_sr ='https://somosreyes-test-652809.dev.odoo.com'
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



def get_id_odoo_product(seller_sku):
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

def webhook_venti(product_id):
	try:
		stock_markets_nuevo=0
		stock_from_odoo = get_stock_real_from_odoo(product_id)
		default_code = stock_from_odoo['default_code']
		stock_real = stock_from_odoo['stock_real'] 
		stock_markets_actual = stock_from_odoo['stock_markets']
		stock_exclusivas = stock_from_odoo ['stock_exclusivas']
		stock_urrea = stock_from_odoo ['stock_urrea']
		
		print ('ODOO| stock_real:', stock_real)

		stock_markets_nuevo = (stock_real + stock_exclusivas + stock_urrea) 
		if stock_markets_actual==0:
			stock_markets_nuevo = stock_real + stock_exclusivas + stock_urrea 
		else:
			stock_markets_nuevo = stock_markets_actual
			print ('ODOO|stock_markets_actual:',stock_markets_actual, ' stock_markets_nuevo',  stock_markets_nuevo)
		
		print ('ODOO|stock_real:',stock_real,', stock_exclusivas:', stock_exclusivas, ', stock_urrea:', stock_urrea, '-> Nuevo stock_markets: ', stock_markets_nuevo)

		stock_mercadolibre =  stock_real + stock_exclusivas + stock_urrea 
		if stock_mercadolibre < 0:
			stock_mercadolibre=0

		stock_linio = stock_real + stock_exclusivas 
		if stock_linio < 0:
			stock_linio=0

		stock_amazon =  stock_real + stock_exclusivas + stock_urrea 
		if stock_amazon < 0:
			stock_amazon = 0

		stock_prestashop =  stock_real + stock_exclusivas + stock_urrea 
		if stock_prestashop < 0:
			stock_prestashop = 0

		stock_walmart =  stock_real + stock_exclusivas 
		if stock_walmart < 0:
			stock_walmart = 0

		stock_claroshop =  stock_real + stock_exclusivas + stock_urrea 
		if stock_claroshop < 0:
			stock_claroshop = 0

		print(default_code,',',stock_amazon,',',stock_linio,',',stock_prestashop,',',stock_claroshop,',',stock_mercadolibre)
		access_token_venti = get_token_venti()

		if stock_mercadolibre < stock_markets_nuevo:
			stock_markets_nuevo = stock_mercadolibre		

		print ('Actualizando en Odoo SKU: ', default_code, ', stock_markets_nuevo: ', stock_markets_nuevo)
		update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti)
		
		#--- Actualiza el campo stock_markets en Odoo.
		#update_stock_markets(product_id, stock_markets_nuevo)
	
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
			get_token_venti()
			
	except Exception as e:
		print('ERROR|update_product_venti|', str (e))
		return False

	
#--------------------  Fin Funciones de Webhooks---------------------------------------------------------------------------





if __name__ == '__main__':
	api = RestAPI()
	api.authenticate()
	#productos_exclusivas=open('productos_exclusivas.csv')
	
	#for producto in productos_exclusivas:
	#	default_code = producto[:-1]
	#	product_id = get_id_odoo_product(seller_sku)
	#	webhook_venti(product_id)
	access_token_venti = get_token_venti()
	print(access_token_venti)
	default_code = '445861-25B-SBDI'
	stock_mercadolibre =0 
	stock_linio =0
	stock_amazon =0
	stock_prestashop=0
	stock_walmart=0 
	stock_claroshop= 0 
	access_token_venti = get_token_venti()
	update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti)
