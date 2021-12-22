# -*- coding: utf-8 -*-
import sys
import requests
import json

#--- 1. recuperamos el token de CBT MELI
def recupera_meli_token(user_id):
	try:
		#print 'USER ID:', user_id
		token_dir=''
		if user_id ==25523702:# Usuario de SOMOS REYES VENTAS
			token_dir='/home/ubuntu/meli/tokens_meli.txt' 
		elif user_id ==160190870:# Usuario de SOMOS REYES OFICIALES
			token_dir='/home/ubuntu/meli/tokens_meli_oficiales.txt'
		#print token_dir

		archivo_tokens=open(token_dir, 'r')
		tokens=archivo_tokens.read()
		tokens_meli = json.loads(tokens)
		archivo_tokens.close()
		access_token=tokens_meli['access_token']
		#print access_token
		return access_token 
	except Exception as e:
		print ('Error recupera_meli_token() : '+str(e) )
		return False


def get_mlm_from_meli(user_id, sku, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		}
		url='https://api.mercadolibre.com/users/'+str(user_id)+'/items/search?sku='+sku+'&access_token='+access_token
		r=requests.get(url, headers=headers)
		print (url)
		item_id_meli = r.json()['results'][0]
		return item_id_meli
		#return True

	except Exception as e:
		print('Eror|'+str(e))

def leer_item(mlm, access_token):
	headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		}
	url='https://api.mercadolibre.com/items/'+item_id_meli+'?access_token='+access_token
	r=requests.get(url, headers=headers)
	print (r.json() )


if __name__ == '__main__':  
		sku='7526LD-URR'
		user_id = 160190870
		#user_id = 25523702
		access_token = recupera_meli_token(user_id)
		item_id_meli = get_mlm_from_meli(user_id, sku, access_token)
		print (user_id,sku,item_id_meli)
		leer_item(item_id_meli, access_token)
		