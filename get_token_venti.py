#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import json
from get_data_odoo import *
import pytz
import datetime

def venti():
	try:
		token_venti=open("token_venti.json", "w")
		
		body={
			"username":"tienda-obi@somos-reyes.com",
			"password":"LeonChes2017",
			"grant_type": "password",
			}

		headers = {
			"accept": "application/json",
			"content-type": "application/x-www-form-urlencoded",
			} 
		
		url='https://ventiapi.azurewebsites.net/login'
		data='username=tienda-obi@somos-reyes.com&password=LeonChes2017&grant_type=password'

		
		#r=requests.post(url, headers=headers, data=json.dumps(body))
		r=requests.post(url, headers=headers, data=body)
		print (r.json() )
		token_venti.write( str(r.json()["access_token"]) )
		token_venti.close()
		return r.json()

	except Exception as e:
		print (' Excepcion ', str(e) )
		return 0

if __name__ == '__main__':
	client_id ='VENTI-SOMOSREYES'
	venti = venti()
	access_token = venti["access_token"]
	refresh_token=''
	token_type =venti["token_type"]
	expires = venti["expires_in"]
	
	time_zone= pytz.timezone('America/Mexico_City')
	Mexico_City_time = datetime.datetime.now(tz=time_zone)
	fecha = Mexico_City_time.isoformat(' ')[:-13]
	last_date_retrieve = fecha
	resultado = api.update_tokens_in_odoo(client_id, access_token, refresh_token, token_type, expires, last_date_retrieve)
	if resultado:
		print ('Actualizado!')
	else:
		print('No actualizado!')