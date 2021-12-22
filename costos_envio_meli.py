#!/usr/bin/python
import json
import requests
import urllib 
from pprint import pprint
import datetime
from datetime import datetime, date, time, timedelta
import calendar
import logging

import email
import imaplib, re
import smtplib 
from email.mime.text import MIMEText


date_time = datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/allien/meli/logs/costos_envio_meli_'+str(fecha)+'.log'
#logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)
logging.basicConfig(format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)
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
			token_dir='/home/allien/meli/tokens_meli.txt'
		elif user_id ==160190870:# Usuario de SOMOS REYES OFICIALES
			token_dir='/home/allien/meli/tokens_meli_oficiales.txt'

		archivo_tokens=open(token_dir, 'r')
		tokens=archivo_tokens.read().replace("'", '"')
		tokens_meli = json.loads(tokens)
		archivo_tokens.close()
		access_token=tokens_meli['access_token']
		return access_token
	except Exception as e:
		print ('Error recupera_meli_token : '+str(e))
		return False

def domain_discover(access_token):
	headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
	query='Alberca Piscina Rectangular 300 x 200 x 75 Cm 28272NP Intex'
	url = 'https://api.mercadolibre.com/sites/MLM/domain_discovery/search?q='+query
	r=requests.get(url, headers=headers)
	print (r.text)
	category_id=r.json()[0]['category_id']
	print(query, "categoria:", category_id)
	return category_id



def costo_envio_meli(seller_id, access_token, category_id ):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}		 
		item_price = 6759
		dimensions = '20x23x10,1000'
		url='https://api.mercadolibre.com/users/'+str(seller_id)+'/shipping_options/free?currency_id=MXN&listing_type_id=gold_pro&condition=new&category_id='+category_id+'&item_price='+str(item_price)+'&verbose=true&dimensions='+dimensions
		
		r=requests.get(url, headers=headers)
		resultado=r.json()['coverage']['all_country']['list_cost']
		print('Costo Envío calculado por dimensiones y precio de venta: ', resultado)
		#print (json.dumps(resultado, sort_keys=True, indent=4, separators=(',', ': ')) )		
	except Exception as e:
		print ('Error|get_orders_meli()'+str(e) )

def costo_envio_codigo_postal(seller_id, access_token, category_id ):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}		 
		item_price = 6759
		dimensions = '20x23x10,1000'
		cp=62740
		url='https://api.mercadolibre.com/users/'+str(seller_id)+'/shipping_options?zip_code='+str(cp)+'&dimensions='+dimensions
		
		r=requests.get(url, headers=headers)
		resultado=r.json()
		destination=resultado['destination']['city']['name']
		destination=resultado['destination']['zip_code']
		list_cost=resultado['options'][0]['list_cost']
		print('Costo Envío calculado por dimensiones y CP:',list_cost)
		#print(destination)
		#print(resultado)
		#print (json.dumps(resultado, sort_keys=True, indent=4, separators=(',', ': ')) )		
	except Exception as e:
		print ('Error|get_orders_meli()'+str(e) )

def get_shipment_meli(shipping_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/shipments/'+str(shipping_id)+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		results = r.json()
		print (json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')) )
		results = r.json()['shipping_option']['list_cost']
		print (shipping_id, 'Costo Envío real: ',results)	
		#return dict(status=status, tracking_number=tracking_number, tracking_method=tracking_method)
	except Exception as e:
		print (' Error get_shipment_meli: '+ str(e))
		return False

def get_order_meli(seller_id, order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
		#print url
		r=requests.get(url, headers=headers)
		results = r.json()
		print (json.dumps(results, sort_keys=True, indent=4, separators=(',', ': ')) )
	except Exception as e:
		print (' Error get_order_meli: '+ str(e))
		return False

if __name__ == '__main__':
	seller_id=160190870
	#seller_id =25523702
	access_token = recupera_meli_token(seller_id)
	print(access_token)
	#category_id = domain_discover(access_token)
	#costo_envio_meli(seller_id, access_token, category_id )
	#costo_envio_codigo_postal(seller_id, access_token, category_id )
	#order_id = 2578880273
	#get_order_meli(seller_id, order_id, access_token)
	
	shipping_id='40011419102'
	get_shipment_meli(shipping_id, access_token)

	#get_orders_meli(seller_id, access_token, offset)
	'''
	seller_id=25523702	
	access_token = recupera_meli_token(seller_id)
	offset = get_offset(seller_id, access_token)
	get_orders_meli(seller_id, access_token, offset)
	'''

	
