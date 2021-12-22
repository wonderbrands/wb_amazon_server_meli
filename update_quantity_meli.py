import sys
import json
import requests


#--- 1. recuperamos el token de CBT MELI
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
		print ('Error recupera_meli_token() : '+str(e) )
		return False

def get_mlm_from_meli(user_id, sku, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		}
		url='https://api.mercadolibre.com/users/'+str(user_id)+'/items/search?sku='+sku+'&status=active&access_token='+access_token
		r=requests.get(url, headers=headers)
		print (url)
		item_id_meli = r.json()['results'][0]
		return item_id_meli

	except Exception as e:
		raise e


def update_product_meli(item_id_meli, quantity, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		}
		data={'available_quantity': quantity}  

		url='https://api.mercadolibre.com/items/'+str(item_id_meli)+'?access_token='+access_token
		print (url)
		r=requests.put(url, headers=headers, data=json.dumps(data) )
		#print r.json()
		print ('Actualizado ', item_id_meli)

	except Exception as e:
		raise e


def actualiza_inventario_item(item_id_meli, quantity, access_token ):
    #Actualizacion
    headers = {
		'accept': 'application/json',
		'content-type': 'application/json',
		}
    url='https://api.mercadolibre.com/items/'+item_id_meli+'?access_token='+access_token
    payload = {"available_quantity":quantity}
    print ('payload ', payload)

    r=requests.put(url, headers=headers, data=json.dumps(payload))


    #print r.headers
    #print r.json()

def update_manufacturing_time(item_id_meli, dias, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		}
		data={
			"sale_terms": 
			[{
				"id": "MANUFACTURING_TIME",
				#"value_name": str(dias)+" días"
				"value_id": "null",
				"value_name": "null"
			}]
		}  


		url='https://api.mercadolibre.com/items/'+str(item_id_meli)+'?access_token='+access_token

		print (url)
		r=requests.put(url, headers=headers, data=json.dumps(data) )
		#print r.json()
		print ('Actualizado ', item_id_meli)

	except Exception as e:
		raise e


if __name__ == '__main__':  
	#SOMOS-REYES OFICIALES = 160190870
	#SOMOS-REYES = 
	
	user_id = 160190870
	access_token = recupera_meli_token(user_id)
	sku = 'CH105-URR' 
	#quantity=7

	item_id_meli = get_mlm_from_meli(user_id, sku, access_token)
	print (item_id_meli)
	dias=5
	update_manufacturing_time(item_id_meli, dias, access_token)

	#actualiza_inventario_item(item_id_meli, quantity, access_token )

	#update_product_meli(item_id_meli, quantity, access_token)
