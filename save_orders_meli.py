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

import email
import imaplib, re
import smtplib 
from email.mime.text import MIMEText


date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/ubuntu/meli/logs/save_orders_meli_'+str(fecha)+'.log'
logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)

def envia_email(notificacion):
	try:
		# Establecemos conexion con el servidor smtp de gmail
		mailServer = smtplib.SMTP('mail.somos-reyes.com',26)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login("serverubuntu@somos-reyes.com","Ttgo702#")
		# Construimos el mensaje simple
		mensaje=notificacion
		mensaje_enviar=mensaje
		mensaje = MIMEText(mensaje_enviar,"html", _charset="utf-8" )
		mensaje['From']="serverubuntu@somos-reyes.com"
		mensaje['To']= "moisantgar@gmail.com, lcheskin@gmail.com, sistemas@somos-reyes.com, aliensantiago1969@gmail.com"
		mensaje['Subject']="Error al intentar salvar registro en la base de datos de MELI."
		# Envio del mensaje
		mailServer.sendmail(mensaje['From'], mensaje["To"].split(",") ,  mensaje.as_string())
		print ("Se ha enviado un correo de aviso a Leon y Moi.") 
		# Cierre de la conexion
		mailServer.close()
	except Exception as e:
		print ("No se pudo enviar el email de aviso! -> "+ str(e) )

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
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
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

def get_offset(seller_id, access_token):
	try:
		import datetime
		ahora = datetime.datetime.utcnow()
		date_created_from =  str(ahora)[:-16].replace(' ', 'T')
		date_created_to = str(ahora)[:-16].replace(' ', 'T')
		#date_created_from = '2019-10-20' 
		#date_created_to = '2019-10-20'

		print (date_created_from, date_created_to)

		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token
		
		r=requests.get(url, headers=headers)
		print (url)
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
		print ('Error en get_offset(): '+str(e) )

def get_orders_meli(seller_id, access_token, offset):
	try:
		import datetime
		ahora = datetime.datetime.utcnow()
		hace_una_hora = ahora - datetime.timedelta(hours=1)
		date_created_from = str(hace_una_hora)[:13].replace(' ', 'T')
		date_created_to = str(ahora)[:-13].replace(' ', 'T')

		date_created_from =  str(ahora)[:-16].replace(' ', 'T')
		date_created_to = str(ahora)[:-16].replace(' ', 'T')
		print (date_created_from, date_created_to)
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&offset='+str(offset)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token

		print (url)
		r=requests.get(url, headers=headers)
		numero_de_ordenes=len(r.json()['results'])

		i=0
		for i in range(0, numero_de_ordenes):
			order_id=r.json()['results'][i]['id']
			pack_id = get_pack_id_meli(order_id, access_token)
			status = r.json()['results'][i]['status']
			date_created = (r.json()['results'][i]['date_created'])[:-10].replace(' ', 'T')
			date_last_updated = (r.json()['results'][i]['date_last_updated'])[:-5].replace(' ', 'T')
			total_amount=  r.json()['results'][i]['total_amount']
			print (order_id,status,date_last_updated, total_amount)
			i=i+1
			insertar_notificaciones_orders_meli(pack_id, order_id, seller_id, date_created, date_last_updated)

	except Exception as e:
		print ('Error|get_orders_meli()'+str(e) )


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
		#print ('INSERT SQL|'+str(sql) )
		try:
			cursor.execute(sql)
			connection_object.commit()
			logging.info('user_id '+str(user_id)+'|order_id '+ str(order_id)+ '|saved '+saved+ '|sent '+sent+'|received '+received )
			print ('MYSQL|'+'user_id '+str(user_id)+'|order_id '+ str(order_id)+ '|saved '+saved+ '|sent '+sent+'|received '+received )
			return True
		except Exception as e:
			# ---- Si existe un error diferente al intento de Registros Duplicados, envia un mensaje a Leon, Moi (alien es Moi Cel) y Jesus.
			notificacion = ' ERROR SQL: '+str(e)
			if 'Duplicate entry' in str(e):
				pass
			else:
				envia_email(notificacion)
				logging.info(str(order_id)+'|ERROR SQL|'+str(e))
				#--- intenta reiniciar el Servidor de SQL
				


			return False

if __name__ == '__main__':
	seller_id=160190870
	access_token = recupera_meli_token(seller_id)
	offset = get_offset(seller_id, access_token)
	get_orders_meli(seller_id, access_token, offset)
	
	seller_id=25523702	
	access_token = recupera_meli_token(seller_id)
	offset = get_offset(seller_id, access_token)
	get_orders_meli(seller_id, access_token, offset)

	
