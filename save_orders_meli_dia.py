#!/usr/bin/python

'''
Ejecutar este Modulo para recuperar las ordenes generadas en Mercado Libre.
	1. Recupera las ordenes de un dia especifico.
	2. Guarda los Id de las Ordenes de Mercado libre en la tabla notify_meli de la BD meli.
	3. Si existe algun error que no sea posible al reiniciar o intentar reiniciar MariaDB, reinicia la Maquina virtual en Amazon AWS
'''

import json
import requests
import urllib 
from pprint import pprint
import datetime
from datetime import datetime, date, time, timedelta
import calendar
from connector_mariadb import *
import logging


date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/ubuntu/meli/logs/save_orders_meli_'+str(fecha)+'.log'
logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)


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

def get_offset(seller_id, access_token, date_created_from, date_created_to):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&order.status=paid&access_token='+str(access_token)		
		#url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'q:2515774634&tags:mshops&access_token='+str(access_token)		
		#url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&q:2515774634&tags:mshops&access_token='+str(access_token)		
		
		r=requests.get(url, headers=headers)
		print url
		paging=r.json()['paging']
		print 'paging: ', paging
		total=paging['total']
		offset=paging['offset']
		limit=paging['limit']
		print 'Total de ordenes de Venta:', total
		print 'Offset:', offset
		print 'limite: ', limit
		numero_paginas=int(total/limit)
		print 'Numeros  de paginas: ', numero_paginas
		offset = total-50
		if offset > 0:
			pass	
		else:
			offset=0

		print 'Total:' , total
		print '===================================================================================================================='
		return total
	except Exception as e:
		print 'Error en get_offset(): '+str(e)

def get_orders_meli(seller_id, access_token, offset, date_created_from, date_created_to):
	global pedido_no 
	try:
		print date_created_from, date_created_to
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		#url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&offset='+str(offset)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&order.status=paid&access_token='+access_token
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&offset='+str(offset)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&tag:mshops&access_token='+str(access_token)		
		     
		print url
		r=requests.get(url, headers=headers)
		numero_de_ordenes=len(r.json()['results'])

		i=0
		for i in range(0, numero_de_ordenes):
			order_id=r.json()['results'][i]['id']
			pack_id = get_pack_id_meli(order_id, access_token)
			status = r.json()['results'][i]['status']
			date_created = (r.json()['results'][i]['date_created'])[:-10].replace(' ', 'T')
			date_last_updated = (r.json()['results'][i]['date_last_updated'])[:-5].replace(' ', 'T')
			total_amount =  r.json()['results'][i]['total_amount']
			i=i+1

			print pedido_no, i, order_id,status,date_last_updated, total_amount
			pedido_no = pedido_no+1
			insertar_notificaciones_orders_meli(pack_id, order_id, seller_id, date_created, date_last_updated)

	except Exception as e:
		print 'Error|get_orders_meli()'+str(e)


connect=connect_to_orders()
cursor=connect['cursor']
connection_object=connect['connection_object']

def insertar_notificaciones_orders_meli(pack_id, order_id, user_id, sent, received):
	resource='orders'
	if resource=='orders':
		car_id = pack_id
		order_id=order_id
		user_id=user_id
		topic='order'
		application_id=''
		attempts='1'
		sent=sent
		received=received
		saved = str(datetime.now())[:-6]
		sql=""
		sql+="INSERT INTO notify_meli("
		sql+="car_id,"
		sql+="order_id,"
		sql+="application_id,"
		sql+="user_id,"
		sql+="topic,"
		sql+="attempts,"
		sql+="sent,"
		sql+="received,"
		sql+="saved"
		sql+=") VALUES ("
		sql+="'"+str(car_id)+"',"
		sql+="'"+str(order_id)+"',"
		sql+="'"+str(application_id)+"',"
		sql+="'"+str(user_id)+"', "
		sql+="'"+str(topic)+"', "
		sql+=str(attempts)+", "
		sql+="'"+str(sent)+"', "
		sql+="'"+str(received)+"', "
		sql+="'"+str(saved)[:-1]+"'"
		sql+=")"
		print 'INSERT SQL|'+str(sql)
		try:
			cursor.execute(sql)
			connection_object.commit()
			print 'MYSQL|'+'user_id '+str(user_id)+'|order_id '+ str(order_id)+ '|saved '+saved+ '|sent '+sent+'|received '+received
			return True
		except Exception as e:
			print (str(order_id)+'|ERROR SQL|'+str(e))
			if 'Duplicate entry' in str(e):
				pass
			else:
				#envia_email(notificacion)
				#print('|ERROR SQL|'+str(e) )
				print ('Orden '+str(order_id) +' Ya fue salvada')
				#--- intenta reiniciar el Servidor de SQL 

			return False
pedido_no = 1
if __name__ == '__main__':
	date_created_from = '2020-09-03' 
	date_created_to = '2020-09-03'

	seller_id=160190870
	access_token = recupera_meli_token(seller_id)
	total = get_offset(seller_id, access_token, date_created_from, date_created_to)
	print 'Total:', total

	pedido_no = 1
	for pagina in range(0, total, 50):
		get_orders_meli(seller_id, access_token, pagina, date_created_from, date_created_to)
	
	
	seller_id=25523702	
	access_token = recupera_meli_token(seller_id)
	total = get_offset(seller_id, access_token, date_created_from, date_created_to)
	print 'Total:', total

	pedido_no = 1
	for pagina in range(0, total, 50):
		get_orders_meli(seller_id, access_token, pagina, date_created_from, date_created_to)

	