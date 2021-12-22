#!/usr/bin/python
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

log_file='/home/ubuntu/meli/logs/orders_meli_'+str(fecha)+'.log'
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


def get_offset(date_created_from, date_created_to, seller_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token
		r=requests.get(url, headers=headers)
		paging=r.json()['paging']
		print ('paging: ', paging)
		total=paging['total']
		offset=paging['offset']
		limit=paging['limit']
		print (total, offset, limit)
		numero_paginas=int(total/limit)
		print (numero_paginas)
		offset = total-50
		if offset > 0:
			pass	
		else:
			offset=0

		print ('offset:' , offset)
		return offset
	except Exception as e:
		print ('Error en get_offset(): '+str(e))

def get_orders_meli(date_created_from, date_created_to, seller_id, access_token, offset):
	try:
		#import datetime
		#ahora = datetime.datetime.utcnow()
		#hace_una_hora = ahora - datetime.timedelta(hours=1)
		#date_created_from = str(hace_una_hora)[:13].replace(' ', 'T')
		#date_created_to = str(ahora)[:-13].replace(' ', 'T')
		print (date_created_from, date_created_to)
		
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
	
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&offset='+str(offset)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token
		#url='https://api.mercadolibre.com/orders/search/recent?seller='+str(seller_id)+'&access_token='+access_token
		print (url)
		r=requests.get(url, headers=headers)

		numero_de_ordenes=len(r.json()['results'])
		#print numero_de_ordenes
		#print (json.dumps(r.json()['results'], indent=4, sort_keys=True))
		
		i=0
		for i in range(0, numero_de_ordenes):
			order_id=r.json()['results'][i]['id']
			pack_id = get_pack_id_meli(order_id, access_token)
			status = r.json()['results'][i]['status']
			date_closed = (r.json()['results'][i]['date_closed'])[:-10].replace(' ', 'T')
			date_created = (r.json()['results'][i]['date_created'])[:-10].replace(' ', 'T')
			date_last_updated = (r.json()['results'][i]['date_last_updated'])[:-5].replace(' ', 'T')
			total_amount =  r.json()['results'][i]['total_amount']
			shipping_mode =  r.json()['results'][i]['shipping'].get('shipping_mode')
			print (order_id,status,date_closed, date_created,date_last_updated, total_amount, shipping_mode)

			substatus =  r.json()['results'][i]['shipping'].get('substatus')
			direccion =  r.json()['results'][i]['shipping'].get('receiver_address')

			
			#print (direccion)
			if direccion:
				address_line = direccion['address_line']
				city = direccion['city']['name']
				country = direccion['country']['name']
				#municipality = direccion['municipality']['name']
				#neighborhood = direccion['neighborhood']['name']
				#receiver_name = direccion['receiver_name']
				#receiver_phone = direccion['receiver_phone']
				state = direccion['state']['name']
				street_name = direccion['street_name']
				street_number = direccion['street_number']
				zip_code = direccion['zip_code']

				#direccion_entrega = street_name +' '+ str(street_number) +' ' + str(municipality)+  ' '+ str(neighborhood)+' '+ str(city)+' '+  str(state)+' '+str(country) +' C.P.' +str(zip_code)

				direccion_entrega = street_name +' '+ str(street_number) +', ' +str(city)+', '+  str(state)+', '+str(country) +', C.P.' +str(zip_code)
				comentario = direccion['comment']
				print (direccion_entrega)
				print ('Etiqueta Meli: ', substatus)
			else:
				print ('Sin Dirección')
			i=i+1
			#insertar_notificaciones_orders_meli(pack_id, order_id, seller_id, date_created, date_last_updated)
		
	except Exception as e:
		raise e



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
		#print 'INSERT SQL|'+str(sql)
		try:
			cursor.execute(sql)
			connection_object.commit()
			logging.info('user_id '+str(user_id)+'|order_id '+ str(order_id)+ '|saved '+saved+ '|sent '+sent+'|received '+received )
			print ('MYSQL|'+'user_id '+str(user_id)+'|order_id '+ str(order_id)+ '|saved '+saved+ '|sent '+sent+'|received '+received)
			return True
		except Exception as e:
			logging.info(str(order_id)+'|ERROR SQL|'+str(e))
			return False

if __name__ == '__main__':
	date_created_from = '2020-08-26'
	date_created_to = '2020-08-26'
	seller_id=160190870
	access_token = recupera_meli_token(seller_id)
	offset = get_offset(date_created_from, date_created_to, seller_id, access_token)
	get_orders_meli(date_created_from, date_created_to, seller_id, access_token, offset)

	seller_id=25523702	
	access_token = recupera_meli_token(seller_id)
	offset = get_offset(date_created_from, date_created_to, seller_id, access_token)
	get_orders_meli(date_created_from, date_created_to, seller_id, access_token, offset)

	
