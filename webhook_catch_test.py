#!/usr/bin/python3
import sys

from flask import Flask, request, abort

import datetime
from datetime import datetime, date, time, timedelta
import logging

import json
import requests

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauth_odoo12 import *

oauth=oauth_odoo12_test()
url=oauth['url']
client_id=oauth['client_id']
client_secret=oauth['client_secret']

def get_token_venti():
    try:
        token_file=open("/home/ubuntu/venti/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        return None

def update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		body={
		        "sku": str(default_code),
				"channelData": [
					{
						"channel": "mercadolibre",
						"quantity": stock_mercadolibre
					},
					{
						"channel": "linio",
						"quantity":stock_linio,
					},
					{
						"channel": "amazon",
						"quantity":stock_amazon,
					},
					{
						"channel": "prestashop",
						"quantity": stock_prestashop
					}, 
					{
						"channel": "walmart",
						"quantity": stock_walmart
					}, 
					{
						"channel": "claroshop",
						"quantity": stock_claroshop
					}, 
				]
			}

		url='https://ventiapi.azurewebsites.net/api/stock/updatepricestockbychannel'
		r=requests.post(url, headers=headers, data= json.dumps(body) )
		print (r.text)
		print ('Actualizando SKU: %s Meli %s |  Linio %s |Amazon %s |Prestashop %s |Walmart %s |ClaroShop %s en Venti.' % (default_code, str(stock_mercadolibre), str(stock_linio), str(stock_amazon), str(stock_prestashop), str(stock_walmart), str(stock_claroshop) ) )
		 
		if "Producto no encontrado" in r.text:
			print (r.text+' SKU: ', default_code ) 


	except Exception as e:
		print('Error en update_product_venti: %s', str (e))

def get_stock_quant_ids(product_id):
	try:
		data = {
			'model': "product.product",
			'domain': json.dumps([['id', '=', product_id]]),
			'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids',"stock_exclusivas", "stock_urrea", 'virtual_available' ]),
		}
		print (data)
		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))#
		stock_quant_ids = response[0]['stock_quant_ids']
		default_code = response[0]['default_code']
		list_price = response[0]['list_price']
		stock_exclusivas = response[0]['stock_exclusivas']
		stock_urrea = response[0]['stock_urrea']
		virtual_available =response[0]['virtual_available']

		return dict(stock_quant_ids=stock_quant_ids, default_code=default_code, list_price=list_price, stock_exclusivas=stock_exclusivas, stock_urrea=stock_urrea, virtual_available=virtual_available )
	except Exception as e:
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
			raise Exception(pprint(response.json()))
		else:
			return response.json()

api = RestAPI()
api.authenticate()


#================================================================================
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
	try:
		if request.method == 'POST':
			input_odoo=json.loads(json.dumps(request.form))
			#print (json.dumps(input_odoo, sort_keys=True, indent=4, separators=(',', ': ')) )
			records = json.loads(input_odoo['records'])
			print (records)
			#print (type(records))
			#print (records[0])
			product_id = records[0]['product_id'][0]
			reference =  records[0]['reference']
			print ('Referencia: ', reference)
			pronosticado = 0 
			if 'WH/PICK/' in reference or 'WH/IN/' in reference:
				print ('Movimiento: ',product_id, reference)
				data_stock_quant_ids = get_stock_quant_ids(product_id)
				stock_quant_ids = data_stock_quant_ids['stock_quant_ids']
				default_code = data_stock_quant_ids['default_code']

				if stock_quant_ids:
					print ('stock_quant_ids', stock_quant_ids)
					for id in stock_quant_ids:	
						stock_quant = get_stock_quant(id)
						print('stock_quant',stock_quant)
						location_id =stock_quant['location_id']
						quantity=stock_quant['quantity']	
						reserved_quantity =stock_quant['reserved_quantity']
						if location_id[1] == 'AG/Stock':
							print (default_code, location_id, quantity, reserved_quantity)
							pronosticado=int(stock_quant['quantity'] ) - int(stock_quant['reserved_quantity'])
							print ('Pronosticado: ', pronosticado)
				else:
					pronosticado = data_stock_quant_ids['virtual_available']


				print ('pronosticado', pronosticado) 

				stock_exclusivas = data_stock_quant_ids['stock_exclusivas']
				stock_urrea = data_stock_quant_ids['stock_urrea']

				stock_mercadolibre =  int(pronosticado + int(stock_exclusivas) + int(stock_urrea) )
				if stock_mercadolibre < 0:
					stock_mercadolibre=0

				stock_linio = int(pronosticado + int(stock_exclusivas) )
				if stock_linio < 0:
					stock_linio=0

				stock_amazon =  int(pronosticado + int(stock_exclusivas) + int(stock_urrea))
				if stock_amazon < 0:
					stock_amazon = 0

				stock_prestashop =  int(pronosticado + int(stock_exclusivas) + int(stock_urrea))
				if stock_prestashop < 0:
					stock_prestashop = 0

				stock_walmart =  int(pronosticado + int(stock_exclusivas) )
				if stock_walmart < 0:
					stock_walmart = 0

				stock_claroshop =  int(pronosticado + int(stock_exclusivas) + int(stock_urrea))
				if stock_claroshop < 0:
					stock_claroshop = 0

	
				print(default_code,',',stock_amazon,',',stock_linio,',',stock_prestashop,',',stock_claroshop,',',stock_mercadolibre)

				access_token_venti = get_token_venti()

				update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti)

			return 'OK', 200
		else:
			abort(400)
	except Exception as e:
		return 'Error: '+str(e) 


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8082)