# -*- coding: utf-8 -*-

import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauth_odoo12 import *

oauth=oauth_odoo12_production()
url=oauth['url']
client_id=oauth['client_id']
client_secret=oauth['client_secret']
print (url)
limite =100000

def get_token_venti():
    try:
        token_file=open("/home/ubuntu/venti/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        return None
#python /home/ubuntu/venti/get_token_venti.py
def update_product_venti(sku, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		body={
		        "sku": sku,
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
		print ('Actualizando SKU: %s Meli %s |  Linio %s |Amazon %s |Prestashop %s |Walmart %s |ClaroShop %s en Venti.' % (sku, str(stock_mercadolibre), str(stock_linio), str(stock_amazon), str(stock_prestashop), str(stock_walmart), str(stock_claroshop) ) )
		 
		if "Producto no encontrado" in r.text:
			print (r.text+' SKU: ', sku ) 


	except Exception as e:
		print('Error en update_product_venti: %s', str (e))


if __name__ == '__main__':
	#--Leyendo los datos del archivo PLANTILLA_FTP.csv
	i=1
	access_token_venti = get_token_venti()
	skus_productos_odoo_12=open('PLANTILLA_FTP.csv')	
	for registro_producto in skus_productos_odoo_12:
		producto = registro_producto[:-1].split(',')
		sku = producto [0].strip()
		stock_mercadolibre = int(producto[1])
		stock_linio  =  int(producto[2])
		stock_amazon  = int(producto[3]) 
		stock_prestashop  = int(producto[4])
		stock_walmart  = int(producto[5])
		stock_claroshop  = int(stock_walmart)
		update_product_venti(sku, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti)
		#print (sku, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop)
		i=i+1
		if i>100:
			break
		
	
		