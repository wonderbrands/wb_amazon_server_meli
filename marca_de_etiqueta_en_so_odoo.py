#!/usr/bin/python
import json
import requests
import datetime
from datetime import datetime, date, time, timedelta
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

def picking_order_in_odoo(marketplace_order_id):
	try:
		data = {
			'model': "sale.order",
			'domain': json.dumps([['marketplace_order_id', '=', str(marketplace_order_id) ]]),
			'fields': json.dumps(['id','name', 'marketplace_order_id']),
			'limit': 1
		}
		response = api.execute('/api/search_read', data=data)
		print ('VERIFY ORDER: ',response)
		existe=len(response)
		if existe==0: #No existe
			print('No existe la orden ')
			return False 
		else:
			print('Si existe la orden ')
			ids=response[0]['id']
			return ids
	except Exception as e:
		print('Error en verify_exist_order_in_odoo() : '+str(e))
		return False

def verify_exist_order_in_odoo(marketplace_order_id):
	try:
		data = {
			'model': "sale.order",
			'domain': json.dumps([['marketplace_order_id', '=', str(marketplace_order_id) ]]),
			'fields': json.dumps(['id','name', 'marketplace_order_id']),
			'limit': 1
		}
		response = api.execute('/api/search_read', data=data)
		print ('VERIFY ORDER: ',response)
		existe=len(response)
		if existe==0: #No existe
			print('No existe la orden ')
			return False 
		else:
			print('Si existe la orden ')
			ids=response[0]['id']
			return ids
	except Exception as e:
		print('Error en verify_exist_order_in_odoo() : '+str(e))
		return False

def update_sale_order(ids, imprimio_etiqueta_meli):
		try:		
			values = {'imprimio_etiqueta_meli': imprimio_etiqueta_meli,}

			data = {
				"model": "sale.order",
				'ids':ids,
				"values": json.dumps(values),
			}
			response = api.execute('/api/write', type="PUT", data=data)
			print('UPDATE SALE ORDER|',marketplace_order_id, response)
		except Exception as e:
			print ('Error en update_sale_order: '+str(e) )

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


def get_total(date_created_from, date_created_to, seller_id, access_token):
	try:
		headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
		url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+str(date_created_to)+'T23:59:59.000-00:00'+'&access_token='+str(access_token)
		#print (url)
		r=requests.get(url, headers=headers)
		paging=r.json()['paging']
		#print ('paging: ', paging)
		total=paging['total']
		offset=paging['offset']
		limit=paging['limit']
		#print (total, offset, limit)
		numero_paginas=int(total/limit+1)
		#print (numero_paginas)
		offset = total-50
		if offset > 0:
			pass	
		else:
			offset=0

		#print ('numero_paginas:' , numero_paginas)
		return numero_paginas
	except Exception as e:
		print ('Error en get_total: '+str(e))

def get_substatus_shipment_label_meli (order_id, access_token): 
    try:
        headers = {'Accept': 'application/json','content-type': 'application/json'}
        url='https://api.mercadolibre.com/orders/'+str(order_id)+'/shipments?access_token='+access_token
        r=requests.get(url, headers=headers)
        #print (json.dumps(r.json(), indent=4, sort_keys=True))
        shipment = r.json()
        substatus = shipment.get('substatus')
        logistic_type = shipment.get('logistic_type')
        status = shipment.get('status')
        tracking_method = shipment.get('tracking_method')
        tracking_number = shipment.get('tracking_number')
        mode = shipment.get('mode')
        #print (substatus, logistic_type, status, tracking_method, tracking_number)
        #print (results['receiver_address'])
        #print (json.dumps(results['receiver_address'], indent=4, sort_keys=True))
        return dict(mode=mode,substatus=substatus, logistic_type=logistic_type, status=status, tracking_method=tracking_method, tracking_number=tracking_number)
    except Exception as e:
        print (' Error order_shipment_meli(): '+ str(e))
        return False
def get_orders_meli(date_created_from, date_created_to, seller_id, access_token, numero_paginas, consecutivo):
	try:
		offset=0
		pagina=0
		
		for o in range(0, numero_paginas):
			headers = {'Accept': 'application/json','content-type': 'application/json', 'x-format-new': 'true'}
			url='https://api.mercadolibre.com/orders/search/?seller='+str(seller_id)+'&offset='+str(offset)+'&sort=date_asc&order.date_created.from='+date_created_from+'T00:00:00.000-00:00'+'&order.date_created.to='+date_created_to+'T23:59:59.000-00:00'+'&access_token='+access_token
			#print(url)
			r=requests.get(url, headers=headers)
			numero_de_ordenes=len(r.json()['results'])
			#print (json.dumps(r.json()['results'], indent=4, sort_keys=True))
			i=0
			for i in range(0, numero_de_ordenes):
				order_id=r.json()['results'][i]['id']
				pack_id = get_pack_id_meli(order_id, access_token)
				status = r.json()['results'][i]['status']
				date_closed = (r.json()['results'][i]['date_closed'])[:-10].replace(' ', 'T')
				date_created = (r.json()['results'][i]['date_created'])[:-10].replace(' ', 'T')
				date_last_updated = (r.json()['results'][i]['date_last_updated'])[:-10].replace(' ', 'T')
				total_amount =  r.json()['results'][i]['total_amount']
				shipping_mode =  r.json()['results'][i]['shipping'].get('shipping_mode')

				date_first_printed = r.json()['results'][i]['shipping'].get('date_first_printed')
				if date_first_printed:
					fecha_impresion = date_first_printed[:-10]
				else:
					fecha_impresion = 'No_Impresa'

				direccion =  r.json()['results'][i]['shipping'].get('receiver_address')
				envio= get_substatus_shipment_label_meli (order_id, access_token)
				substatus = envio['substatus']
				logistic_type = envio['logistic_type']
				status_shipment = envio['status']
				tracking_method = envio['tracking_method']
				tracking_number = envio['tracking_number']
				mode = envio['mode']

				print (consecutivo,',', pack_id,',', order_id,',',status,',',date_last_updated,',',substatus,',',logistic_type,',', mode ,',',status_shipment,',',tracking_method,',',tracking_number )
				i=i+1
				consecutivo=consecutivo+1

			offset=offset+50
			pagina=pagina+1
			if pagina>numero_paginas:
				break

	except Exception as e:
		print ('Error en get_orders_meli: '+str(e))



if __name__ == '__main__':
	date_created_from = '2019-08-22'
	date_created_to = '2019-08-22'
	consecutivo=1

	seller_id=160190870
	access_token = recupera_meli_token(seller_id)
	numero_paginas = get_total(date_created_from, date_created_to, seller_id, access_token)
	get_orders_meli(date_created_from, date_created_to, seller_id, access_token, numero_paginas, consecutivo)

	consecutivo=1
	seller_id=25523702
	access_token = recupera_meli_token(seller_id)
	numero_paginas = get_total(date_created_from, date_created_to, seller_id, access_token)
	get_orders_meli(date_created_from, date_created_to, seller_id, access_token, numero_paginas, consecutivo)
