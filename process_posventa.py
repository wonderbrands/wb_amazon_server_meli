#!/usr/bin/python
# -*- coding: utf-8 -*-

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
#from connector_mariadb import *
#from get_data_odoo import *

#connect=connect_to_orders()
#cursor=connect['cursor']
#connection_object=connect['connection_object']


def get_order_meli(seller_id, order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token
		r=requests.get(url, headers=headers)
		existe_order = len( r.json()['results'])
		print (existe_order)
		print ('Orden: ', existe_order)
		if existe_order>0:
			order = r.json()['results'][0]
			#print(json.dumps(order, indent=4, sort_keys=True))
			shipping_id = order['shipping']['id']

			print ('SHIPPING ID: ', shipping_id)
			if shipping_id:
				pass
				#get_zpl_orders_meli(shipping_id, access_token)

			order_items = order['order_items']
			for item in order_items:
				seller_sku = item['item']['seller_sku']
				title =  item['item']['title']
				sale_fee = item['sale_fee']
				mlm = item['item']['id']
				print (seller_sku, mlm)
				print ('logistic_type_item_meli: ', get_logistic_type_item_meli(mlm) )

			payments= order['payments']
			for payment in payments:
				payment_id = payment['id']
				payment_method_id = payment['payment_method_id']
				payment_type = payment['payment_type']
				status_detail = payment['status_detail']
				print (payment_id, payment_method_id, payment_type, status_detail)
				payment_method_id = get_payment_method_id(payment_type)
				print ('payment_method_id', payment_method_id)
		else:
			print ('Orden: ', order_id, 'No esxiste' )

		print (url)
	except Exception as e:
		raise e


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
		print 'Error recupera_meli_token() : ' +str(e)
		return False

def get_result_orders():
	try:
		print 'Recuperando ordenes notificadas....'
		query='SELECT DISTINCT user_id, car_id,  order_id,respuesta_odoo, procesada FROM notify_meli WHERE respuesta_odoo IS NOT NULL and procesada IS NULL ;'
		cursor.execute(query)
		result = cursor.fetchall()
		cursor.close()
		connection_object.close()
		return result
	except mysql.connector.Error as mysql_error:
		print "Error executing query: %s" % (str(mysql_error))
		return False


def get_pack_id_meli(order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'format-new':'true'}
		url='https://api.mercadolibre.com/orders/'+str(order_id)+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		print url
		print r.json()['pack_id']
		
	except Exception as e:
		print 'Error en get_pack_id_meli:  '+str(e)

def get_messages_meli(pack_id, user_id, access_token):
	try:	
		headers = {"Accept": "application/json","content-type": "application/json", "X-Pack-Format": "true" }
		url='https://api.mercadolibre.com/messages/packs/'+str(pack_id)+'/sellers/'+str(user_id)+'?access_token='+access_token#+'&limit=2&offset=1'
		#    https://api.mercadolibre.com/messages/packs/2000000089077943/sellers/415458330?access_token=$ACCESS_TOKEN&limit=2&offset=1

		print url
		r=requests.get(url, headers=headers)
		print r.text
	except Exception as e:
		print 'Error en get_messages_meli():  '+str(e)

def mensajes_de_orden(order_id,  access_token):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        } 

    url='https://api.mercadolibre.com/messages/orders/'+str(order_id)+'?access_token='+access_token+'&limit=50&offset=0'
    #https://api.mercadolibre.com/messages/{message_id}?access_token=$ACCESS_TOKEN
   
    try:
        r=requests.get(url)
        mi_json= r.json()
        print json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': '))
    except Exception as e:
        raise e

def crear_usuario_test_25523702(access_token):
    headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        } 

    url='https://api.mercadolibre.com/users/test_user?access_token='+access_token
    print(url)
  
    try:
        r=requests.get(url)
        mi_json= r.json()
        print (mi_json)
        #print (json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')))
    except Exception as e:
        print('ERROR| '+str(e)) 

def cuerpo_mensaje (buyer_name, tracking_number, so_name ):
	try:
		mensaje=''
		mensaje+='ESTIMADO CLIENTE:'+ buyer_name +', GRACIAS POR SU COMPRA.\n'
		mensaje+='SU PEDIDO HA SIDO REGISTRADO Y SE ENCUENTRA EN PREPARACIÓN. SU PRODUCTO SE LE ESTARÁ ENVIANDO A LA BREVEDAD\n'
		mensaje+='CON SU NÚMERO DE RASTREO / GUIA :'+tracking_number+'\n'
		mensaje+='Su Numero de Pedido Interno es el '+ so_name+'\n'
		mensaje+='FACTURA EN LINEA: https://somosreyes.odoo.com/portal/facturacliente/.\n' 
		#mensaje+='SOLICITUD DE FACTURA: En caso de no contar con él, favor de solicitarlo a su ejecutivo de ventas.\n' 
		#mensaje+='Cuenta con 4 dias Hábiles después de recibir su Pedido para Solicitar la factura de lo contrario se factura a Público en General.\n'
		mensaje+='Cuenta hasta con el último día del mes en curso crear su factura de lo contrario se factura a Público en General.\n'
		#mensaje+='Una vez recibida la información no se podrá hacer cambios en la factura.\n '
		#mensaje+='Todos los números de Pedido comienzan con SO seguido de 5 dígitos. INGRESAR A:\n'
		#mensaje+='https://app.ventiapp.com/postventas/paso1/ye62LLN1d2go\n'
		mensaje+='IMPORTANTE Si el pedido fue realizado a través de la plataforma de MERCADO PAGO, \n'
		mensaje+='el método de pago siempre será 06 Dinero Electrónico.\n'
		mensaje+='EL COSTO ADMINISTRATIVO POR REFACTURACIÓN (SOLO DENTRO DEL MISMO MES CORRIENTE ) POR ERRORES AJENOS A NOSOTROS ES DE $50.00 MXN MAS IVA.\n' 
		mensaje+='Mayor información visitar nuestra pagina\n'
		mensaje+='www.somos-reyes.com \n'
		mensaje+='O En en los Teléfonos (55) 68309828 (55) 68309829.\n'
		return mensaje
	except Exception as e:
		print 'Erro en cuepo_mensaje() '
		return False
		

def crear_mensaje(APPLICATION_ID, access_token, mensaje ):
    headers = {
        'content-type': 'application/json',
        } 
    data={"from": {"user_id":491096624},"to":[{"user_id":491101842,"resource":"orders","resource_id":2217328156,"site_id": "MLM"}],"subject": "CONFIRMACION DE PEDIDO "+so_name ,"text": {"plain":mensaje}, "attachments": ["Pedido_SO34496.pdf"],}

    url='https://api.mercadolibre.com/messages?access_token='+access_token+'&application_id='+str(APPLICATION_ID)
    print (url)
    try:
        r=requests.post(url, data=json.dumps(data), headers=headers)
        mi_json= r.json()
        print json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': '))
    except Exception as e:
        print str(e)

def colocar_nota_a_orden_meli(so_name, order_id, access_token):
    headers = {
        'content-type': 'application/json',
        } 

    data={"note":so_name}

    url='https://api.mercadolibre.com/orders/'+str(order_id)+'/notes?access_token='+access_token
    try:
        r=requests.post(url, data=json.dumps(data), headers=headers)
        mi_json= r.json()
        print json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': '))
        return True
    except Exception as e:
        print 'Error en colocar_nota_a_orden_meli(): '+str(e)
        return False

def ver_notas_orden_meli(so_name, order_id, access_token):
    headers = {
        'content-type': 'application/json',
        } 
    url='https://api.mercadolibre.com/orders/'+str(order_id)+'/notes?access_token='+access_token
    try:
        r=requests.get(url, headers=headers)
        mi_json= r.json()
        print json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': '))
        return True
    except Exception as e:
        print 'Error en colocar_nota_a_orden_meli(): '+str(e)
        return False

def borrar_nota_orden_meli(note_id, order_id, access_token):
    headers = {
        'content-type': 'application/json',
        } 
    url='https://api.mercadolibre.com/orders/'+str(order_id)+'/notes/'+note_id+'?access_token='+access_token
    try:
        r=requests.delete(url, headers=headers)
        mi_json= r.json()
        print (json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')) )
        return True
    except Exception as e:
        print ('Error en colocar_nota_a_orden_meli(): '+str(e) )
        return False

if __name__ == '__main__':

	#api = RestAPI()
	#api.authenticate()
	'''
	ordenes = get_result_orders()
	pack_anterior=None
	pack_atual=None

	for orden in ordenes:
		user_id = int(orden[0])
		pack_id = orden[1]
		pack_actual=pack_id
		order_id = orden[2]
		respuesta_odoo = orden[3].replace('[','').replace(']','')
		procesada = orden[4]
		print user_id, pack_id, order_id,respuesta_odoo, procesada
		
		if pack_actual != pack_anterior:
			print 'ENVIA MENSAJE ===================>'
			print 'Actualiza orden_id en Maria: '+ order_id
			print 'Inserta Nota en Orden Meli : '+ respuesta_odoo
			pack_anterior=pack_actual
		else:
			print 'Actualiza orden_id en Maria: '+ order_id
			print 'Inserta Nota en Orden Meli : '+ respuesta_odoo
			


	
	
		so_odoo=api.get_order_in_odoo(respuesta_odoo)
		client_order_ref=so_odoo['client_order_ref']
		tracking_number=so_odoo['tracking_number']
		commitment_date = so_odoo['commitment_date']
		so_name=so_odoo['name'] + ' ' + str(commitment_date)
		warehouse=so_odoo['warehouse_id'][1]
		seller_marketplace=so_odoo['seller_marketplace']
		
		print client_order_ref, tracking_number, so_name, warehouse, seller_marketplace, commitment_date
	

	seller_marketplace = 'SOMOS-REYES-OFICIALES'
	if seller_marketplace=='SOMOS-REYES-OFICIALES':
		APPLICATION_ID=5630132812404309 # OFICIALES
		user_id=160190870
	else:
		APPLICATION_ID=5703097592380294  # VENTAS
		user_id=2072523352

	access_token = recupera_meli_token(user_id)
	access_token = 'APP_USR-7159300450657160-111918-f6e286abd5b27c57ad846a27e98911ea-491096624'

	#get_messages_meli(pack_id, user_id, access_token)
	'''
	client_order_ref ='SAMO1770877'
	tracking_number = '123456789000'
	so_name ='SO34496'
	APPLICATION_ID = '7159300450657160'
	access_token='APP_USR-7159300450657160-112015-9904da0b9a54927daf6e0107a89fdc32-491096624'

	mensaje = cuerpo_mensaje (client_order_ref, tracking_number, so_name )
	print mensaje

	crear_mensaje(APPLICATION_ID, access_token, mensaje )
	
	#mensajes_de_orden(order_id,access_token)


	#so_name='SO242582 API'
	#order_id=2072523352
	#user_id=25523702
	#access_token = recupera_meli_token(user_id)
	#crear_usuario_test_25523702(access_token)

	#colocar_nota_a_orden_meli(so_name, order_id, access_token)
	#ver_notas_orden_meli(so_name, order_id, access_token)

	#note_id= '5d1b8f92656800081dd894b0'
	#borrar_nota_orden_meli(note_id, order_id, access_token)
	#pack_id = '2000000105646053'
	#user_id = 25523702
	#access_token = recupera_meli_token(user_id)
	#print access_token
	#get_messages_meli(pack_id, user_id, access_token)
