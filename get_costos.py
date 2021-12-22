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
from odoo_utils import *
from meli_utils import *

date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/ubuntu/meli/logs/get_costos_'+str(fecha)+'.log'
logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)


null='null'
false=False

def get_costos(seller_id, order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
		print(url)
		r=requests.get(url, headers=headers)
		order_exist = len(r.json()['results'])
		print (json.dumps(r.json()['results'], indent=4, sort_keys=True))
		
		shipping_labels=''

		if order_exist > 0:
			order = r.json()['results'][0]
			id_order = order['id']
			order_status = order['status']
			date_created = order['date_created'][:-10]
			shipping_id = order['shipping']['id']
			
			fulfilled = False
			if feedback==None:
				fulfilled = False	
			else: 
				fulfilled = feedback['fulfilled']
				sale = feedback['sale']
				
				print ('FULFILLED: ', fulfilled)
				print (sale, indent=4,)
	except Exception as e:
		print ('Error en get_order_meli(): '+ str(e) )
		return False
