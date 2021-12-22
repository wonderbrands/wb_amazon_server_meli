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


def get_pack_id_meli(order_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'format-new':'true'}
		url='https://api.mercadolibre.com/orders/'+str(order_id)+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		print (url )
		print ( r.json()['pack_id'] )
		
	except Exception as e:
		print ('Error en get_pack_id_meli:  '+str(e))

def get_messages_meli(pack_id, user_id, access_token):
	try:	
		headers = {"Accept": "application/json","content-type": "application/json", "X-Pack-Format": "true" }
		url='https://api.mercadolibre.com/messages/packs/'+str(pack_id)+'/sellers/'+str(user_id)+'?access_token='+access_token#+'&limit=2&offset=1'
		#    https://api.mercadolibre.com/messages/packs/2000000089077943/sellers/415458330?access_token=$ACCESS_TOKEN&limit=2&offset=1

		print (url)
		r=requests.get(url, headers=headers)
		print (r.text)
	except Exception as e:
		print ('Error en get_messages_meli():  '+str(e))

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
        print (json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')) )
    except Exception as e:
        raise e
def colocar_nota_a_orden_meli(so_name, order_id, access_token):
    headers = {
        'content-type': 'application/json',
        } 

    data={"note":so_name}

    url='https://api.mercadolibre.com/orders/'+str(order_id)+'/notes?access_token='+access_token
    try:
        r=requests.post(url, data=json.dumps(data), headers=headers)
        mi_json= r.json()
        print (json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')) )
        return True
    except Exception as e:
        print ('Error en colocar_nota_a_orden_meli(): '+str(e) )
        return False

def ver_notas_orden_meli(so_name, order_id, access_token):
    headers = {
        'content-type': 'application/json',
        } 
    url='https://api.mercadolibre.com/orders/'+str(order_id)+'/notes?access_token='+access_token
    try:
        r=requests.get(url, headers=headers)
        mi_json= r.json()
        print (json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')) )
        return True
    except Exception as e:
        print ('Error en colocar_nota_a_orden_meli(): '+str(e) )
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
		mensaje+='IMPORTANTE Si el pedido fue realizado a través de la plataforma de MERCADO PAGO,'
		mensaje+='el método de pago siempre será 06 Dinero Electrónico.\n'
		mensaje+='EL COSTO ADMINISTRATIVO POR REFACTURACIÓN (SOLO DENTRO DEL MISMO MES CORRIENTE ) POR ERRORES AJENOS A NOSOTROS ES DE $50.00 MXN MAS IVA.\n' 
		mensaje+='Mayor información visitar nuestra pagina\n'
		mensaje+='www.somos-reyes.com \n'
		mensaje+='O En en los Teléfonos (55) 68309828 (55) 68309829.\n'
		return mensaje
	except Exception as e:
		print ('Erro en cuepo_mensaje() ' )
		return False
		

def adjuntar_archivo(ruta_archivo, access_token):    
    try:
        headers = {
        'Content-Type': 'multipart/form-data',
        }
        url= 'https://api.mercadolibre.com/messages/attachments?access_token='+access_token

        files = {'file': open(ruta_archivo, 'rb')}
        
        r = requests.post(url, files=files)
        id_pdf =r.json()['id']
        print (id_pdf)
        return id_pdf
    except Exception as e:
        print (str(e) )
        return False

def crear_mensaje(APPLICATION_ID, access_token, mensaje ):
    headers = {
        'content-type': 'application/json',
        } 
    data={"from": {"user_id":491096624},"to":[{"user_id":491101842,"resource":"orders","resource_id":2217328156,"site_id": "MLM"}],"subject": "CONFIRMACION DE PEDIDO "+so_name ,"text": {"plain":mensaje}, "attachments": ["491096624_b6b6543f-b233-468b-a3b8-b7545d700da1.pdf"],}

    url='https://api.mercadolibre.com/messages?access_token='+access_token+'&application_id='+str(APPLICATION_ID)
    print (url)
    try:
        r=requests.post(url, data=json.dumps(data), headers=headers)
        mi_json= r.json()
        print( json.dumps(mi_json, sort_keys=True, indent=4, separators=(',', ': ')) )
    except Exception as e:
        print (str(e) )




if __name__ == '__main__':

	client_order_ref ='SAMO1770877'
	tracking_number = '123456789000'
	so_name ='SO34496'
	APPLICATION_ID = '7159300450657160'
	ruta_archivo = '/home/ubuntu/meli/Pedido_SO34494.pdf'
	access_token='APP_USR-7159300450657160-112020-8b803f4e2ce4d87d7aca3f2158a5a4a8-491096624'
	
	adjuntar_archivo(ruta_archivo, access_token)

	#mensaje = cuerpo_mensaje (client_order_ref, tracking_number, so_name )
	#print mensaje

	
	#crear_mensaje(APPLICATION_ID, access_token, mensaje )
	
	