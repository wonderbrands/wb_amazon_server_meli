# -*- coding: utf-8 -*-
import json
import requests
import urllib 
from pprint import pprint
import datetime
from datetime import datetime, date, time, timedelta
import calendar
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


#--- 1. recuperamos el token de CBT MELI
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

def get_substatus_shipment_label_meli (order_id, access_token): 
    try:
        headers = {'Accept': 'application/json','content-type': 'application/json'}
        url='https://api.mercadolibre.com/orders/'+str(order_id)+'/shipments?access_token='+access_token
        r=requests.get(url, headers=headers)
        print (json.dumps(r.json(), indent=4, sort_keys=True))
        substatus = r.json()['substatus']
        tracking_number = r.json()['tracking_number']

        print ('SUBSTATUS',substatus, tracking_number)
        #print (results['receiver_address'])
        #print (json.dumps(results['receiver_address'], indent=4, sort_keys=True))
        if substatus=='printed':
        	return True
        else:
        	return False

    except Exception as e:
        print (' Error order_shipment_meli(): '+ str(e))
        return False


def get_shipment_meli(shipping_id, access_token):
    try:
       
        headers = {'Accept': 'application/json','content-type': 'application/json','x-format-new': 'true','Authorization': 'Bearer '+ access_token}
        url='https://api.mercadolibre.com/shipments/'+str(shipping_id)+'/items'
        #print (url)

        r=requests.get(url, headers=headers)
        print (json.dumps(r.json(), indent=4, sort_keys=True))
        '''
        results = r.json()#['results'][0]
        #print (results['receiver_address'])
        #print (json.dumps(results['receiver_address'], indent=4, sort_keys=True))
        direccion = results['receiver_address']

        order_id=results['order_id']
        order_cost=results['order_cost']
        status = results['status']
        tracking_number = results['tracking_number']
        tracking_method = results['tracking_method']

        address_line = direccion['address_line']
        city = direccion['city']['name']
        country = direccion['country']['name']
        municipality = direccion['municipality']['name']
        neighborhood = direccion['neighborhood']['name']
        receiver_name = direccion['receiver_name']
        receiver_phone = direccion['receiver_phone']
        state = direccion['state']['name']
        street_name = direccion['street_name']
        street_number = direccion['street_number']
        zip_code = direccion['zip_code']

        direccion_entrega = street_name +' '+ str(street_number) +' ' + str(municipality)+  ' '+ str(neighborhood)+' '+ str(city)+' '+  str(state)+' '+str(country) +' C.P.' +str(zip_code)
        comentario = direccion['comment']
        
        print (direccion_entrega)
        print (comentario)
        print('tracking_method: ', tracking_method)
        print ('tracking_number: ', tracking_number)

        return dict(status=status, tracking_number=tracking_number, tracking_method=tracking_method)
        '''
    except Exception as e:
        print (' Error get_shipment_meli: '+ str(e))
        return False

def get_logistic_type_item_meli(MLM):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url='https://api.mercadolibre.com/items/'+MLM+'?access_token='+access_token
		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json(), indent=4, sort_keys=True))
		existe_item = len( r.json()['shipping'])
		
		if existe_item:
			item = r.json()['shipping']
			#print(json.dumps(item, indent=4, sort_keys=True))
			shipping_logistic_type = item['logistic_type']
			print('shipping_logistic_type', shipping_logistic_type)
			return shipping_logistic_type	
			
	except Exception as e:
		print ('Error en: '+str(e) )
		return False
def get_payment_method_id(payment_type):
	try:
		formas_pago_odoo = {'01':1, #Efectivo
							'02':2, #Cheque nominativo
							'03':3, #Transferencia electrónica de fondos
							'04':4, #Tarjeta de Crédito
							'05':5, #Monedero Electrónico
							'06':6, #Dinero Electrónico
							'08':7, #Vales de despensa
							'12':8,#Dación en pago
							'13':9, #Pago por subrogación 
							'14':10,#Pago por consignación
							'15':11,#Condonación
							'17':12,#Compensación
							'23':13,#Novación
							'24':14,#Confusión
							'25':15,#Remisión de deuda
							'26':16,#Prescripción o caducidad
							'27':17,#A satisfacción del acreedor
							'28':18,#Tarjeta de Débito
							'29':19,#Tarjeta de Servicio
							'30':20,#Aplicación de anticipos
							'99':21,#Por definir
							'31':22,#Intermediario pagos
							}
				
		formas_de_pago_meli_sat = { "credit_card":"04", 
									"debit_card":"28",
									"prepaid_card":"06",
									"atm":"03",
									"ticket":"01",
									"account_money":"06",
									"digital_currency":"06"}

		if payment_type == 'credit_card':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'debit_card':
			forma_pago_SAT =formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'prepaid_card':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'atm':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'ticket':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'account_money':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		elif payment_type == 'digital_currency':
			forma_pago_SAT = formas_de_pago_meli_sat[payment_type]
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]
		else :
			forma_pago_SAT = '99'
			formas_pago_odoo_id=formas_pago_odoo[forma_pago_SAT]

		print ('Forma de Pago SAT: ', forma_pago_SAT,formas_pago_odoo_id )
		return formas_pago_odoo_id

	except Exception as e:
		print('Error|get_payment_method_id(): '+str(e) )
		return False
	

def get_order_meli(seller_id, order_id, access_token):
	try:
		#headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true', 'Authorization': 'Bearer '+ access_token}
		url='https://api.mercadolibre.com/orders/search?seller='+str(seller_id)+'&q='+str(order_id)+'&access_token='+access_token

		#print url
		r=requests.get(url, headers=headers)
		existe_order = len( r.json()['results'])
		print (existe_order)
		print ('Orden: ', existe_order)
		order = None
		if existe_order>0:
			order = r.json()['results'][0]
			print(json.dumps(order, indent=4, sort_keys=True))
			shipping_id = order['shipping'].get('id')

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
		
			return order
		else:
			return False
			print ('Orden: ', order_id, 'No esxiste' )

		print (url)

	except Exception as e:
		print('Error get_order_meli: ' + str(e))

def get_order_meli_multi(seller_id, pedidos_de_carrito, access_token):
	try:

		lista_ids=''
		for order_id in pedidos_de_carrito:
			lista_ids+=str(order_id)+','

		ids = lista_ids[:-1]
		print ('IDS: ',ids )
		shipping_labels=''
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url = 'https://api.mercadolibre.com/multiget?resource=orders&ids='+str(ids)+'&access_token='+str(access_token)
		#print url
		r=requests.get(url, headers=headers)
		print (json.dumps(r.json(), indent=4, sort_keys=True))
	except Exception as e:
		print ('Error en get_order_meli_multi() '+ str(e) )
		return False


def get_paymet_Details(payment_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', }
		url='https://api.mercadopago.com/v1/payments/'+str(payment_id)+'?access_token='+access_token
		print ('pago:', url)

		r=requests.get(url, headers=headers)

		print(json.dumps(r.json(), indent=4, sort_keys=True))
	except Exception as e:
		raise e

def get_zpl_orders_meli(shipping_id, access_token):
	try:	
		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url='https://api.mercadolibre.com/shipment_labels?shipment_ids='+str(shipping_id)+'&response_type=zpl2&access_token='+str(access_token)
		print (url)
		r=requests.get(url, headers=headers)
		print (r.text)
	except Exception as e:
		raise e
	
if __name__ == '__main__':
	order_id ='4939958385' 
	#seller_id=25523702	
	seller_id=160190870

	user_id=seller_id
	access_token = recupera_meli_token(user_id)
	
	#print ("Seller: ", seller_id,", access_token", access_token)
	order_meli = get_order_meli(seller_id, order_id, access_token)
	#print (order_meli)
	
	#pack_id = order_meli.get('pack_id')
	#shipping_id =  order_meli.get('shipping').get('id')
	#print(pack_id, shipping_id)	
	#print ('==============================RECUPERANDO EL SHIPPING')
	#get_shipment_meli(shipping_id, access_token)
	'''
	get_substatus_shipment_label_meli (order_id, access_token)
	print (get_substatus_shipment_label_meli)
	'''
