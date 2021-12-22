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


logging.basicConfig(level=logging.INFO, format='%(asctime)s[%(levelname)s] (%(threadName)-s) %(message)s ')


def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        return None

def create_webhook_venti(access_token_venti):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		
		body={
		"webhook": {
			"topic": "orders/created",
			"address": "https://somosreyes-test-973378.dev.odoo.com/api/custom/create_so",
			}
		}
		url='https://ventiapi.azurewebsites.net/api/webhooks/create'
		r=requests.post(url, headers=headers, data= json.dumps(body) )
		logging.info("RESPUESTA CREATE: "+r.text)

	except Exception as e:
		raise e

def list_webhook_venti(access_token_venti):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		
		url = 'https://ventiapi.azurewebsites.net/api/webhooks/list'
		r=requests.get(url, headers=headers )
		logging.info("RESPUESTA LIST: "+r.text)


	except Exception as e:
		raise e

def delete_webhook_venti(access_token_venti):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		
		body={
		"webhook": {
			 "id": 45
			}
		}
		url='https://ventiapi.azurewebsites.net/api/webhooks/delete'
		r=requests.post(url, headers=headers, data= json.dumps(body) )

		url = 'https://ventiapi.azurewebsites.net/api/webhooks/list'
		r=requests.get(url, headers=headers )
		logging.info("RESPUESTA DELETE: "+r.text)

	except Exception as e:
		raise e

if __name__ == '__main__':
	access_token_venti = get_token_venti()
	#create_webhook_venti(access_token_venti)
	list_webhook_venti(access_token_venti)
	delete_webhook_venti(access_token_venti)
