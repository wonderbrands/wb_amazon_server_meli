#!/usr/bin/python
import json
import requests

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

def get_shipping_cost(zip_code_from, zip_code_to, ancho, largo, alto, precio ):
	try:

		headers = {'Accept': 'application/json','content-type': 'application/json'}
		dimensiones=str(ancho)+'x'+str(largo)+'x'+str(alto)
		url = 'https://api.mercadolibre.com/sites/MLM/shipping_options?zip_code_from='+str(zip_code_from)+'&zip_code_to='+str(zip_code_to)+'&dimensions='+dimensiones+','+str(precio)

		r=requests.get(url, headers=headers)
		#print (json.dumps(r.json()['options'], indent=4, sort_keys=True))
		options=json.dumps(r.json()['options'])
		lista_costos =[]
		for option in json.loads(options):
			name = option['name'], 
			cost = option['cost']
			lista_costos.append(cost)

		costo_maximo = max(lista_costos)
		print 'Costo Envio:', costo_maximo
		
		return costo_maximo
	except Exception as e:
		print ('Error get_shipping_cost() : '+str(e))
		return False

def get_meli_attributes_by_category(category_id ):
	try:

		headers = {'Accept': 'application/json','content-type': 'application/json'}
		url = 'https://api.mercadolibre.com/categories/'+category_id+'/attributes'

		r=requests.get(url, headers=headers)
		print (json.dumps(r.json(), indent=4, sort_keys=True))
		attributes=json.dumps(r.json())

		for attribute in json.loads(attributes):
			print attribute['id'],  attribute['name']
			print attribute.get('values')

		return True
	except Exception as e:
		print ('Error get_shipping_cost() : '+str(e))
		return False



if __name__ == '__main__':
	'''
	zip_code_from = '53460'
	zip_code_to = '97060'
	ancho = 10
	largo = 10
	alto = 10
	precio = 2000
	get_shipping_cost(zip_code_from, zip_code_to, ancho, largo, alto, precio )
	'''


	category_id = 'MLM164780'
	get_meli_attributes_by_category(category_id )

	

	