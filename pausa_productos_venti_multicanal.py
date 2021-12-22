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

def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
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
						"channel": "venticommerce",
						"quantity": int(stock_prestashop)
					}, 
					{
						"channel": "walmartedi",
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

	access_token_venti = get_token_venti()
	#print(access_token_venti)
	default_code = '293421'
	stock_mercadolibre =0 
	stock_linio =0
	stock_amazon =0
	stock_prestashop=0
	stock_walmart=0 
	stock_claroshop= 0 
	access_token_venti = get_token_venti()
	update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti)
