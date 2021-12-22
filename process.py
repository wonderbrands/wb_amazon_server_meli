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

connect=connect_to_orders()
cursor=connect['cursor']
connection_object=connect['connection_object']


def get_result_orders():
	try:
		print 'Recuperando ordenes notificadas....'
		query='SELECT user_id, car_id, order_id FROM notify_meli WHERE status_order IS NULL or status_order="";'
		cursor.execute(query)
		result = cursor.fetchall()
		cursor.close()
		connection_object.close()
		return result
	except mysql.connector.Error as mysql_error:
		print "Error executing query: %s" % (str(mysql_error))
		return False


if __name__ == '__main__':
	ordenes = get_result_orders()

	carro_anterior=None
	orden_anterior=None
	seller_anterior=None
	lista_pedidos=[]
	datos={}
	carro={}
	lista_carros=[]
	for orden in ordenes:
		seller={}
		carro={}
		seller_actual =orden[0] 
		carro_actual=orden[1]
		orden_actual=orden[2]

		if carro_actual==carro_anterior:
			lista_pedidos.append(orden_anterior)			
		else:
			lista_pedidos.append(orden_anterior)

			seller['seller_id']=seller_anterior
			lista_pedidos.append(seller)

			carro['car_id']=carro_anterior
			lista_pedidos.append(carro)
			print 'PEDIDOS: ',  lista_pedidos
			lista_carros.append(lista_pedidos)	
			print 'CARROS: ',  lista_carros
			lista_pedidos=[]

		carro_anterior=carro_actual
		orden_anterior=orden_actual
		seller_anterior=seller_actual

	print 'ANTEs',  lista_carros
	lista_pedidos.append(orden_actual)
	print 'PEDIDOS0: ', lista_pedidos

	seller['seller_id']=seller_actual
	lista_pedidos.append(seller)
	print 'PEDIDOS1: ', lista_pedidos

	carro['car_id']=carro_actual
	lista_pedidos.append(carro)
	print 'PEDIDOS2: ', lista_pedidos


	lista_carros.append(lista_pedidos)
	print 'PEDIDOS3: ', lista_pedidos
	print lista_carros

for carro in lista_carros:
	#print carro
	carrito = carro[-1]['car_id']
	seller_id =  carro[-2]['seller_id']
	pedidos= carro[:-2]
	print carrito, seller_id, pedidos

