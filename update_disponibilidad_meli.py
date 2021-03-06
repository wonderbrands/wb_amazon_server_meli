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
		#print (url)
		item_id_meli = r.json()['results'][0]
		return item_id_meli

	except Exception as e:
		print('Error al recuperar el MLM de: '+sku+' : ' +str(e))
		no_econtrados.write(sku+'\n')
		print ('Archivado')
		return False


def update_manufacturing_time(item_id_meli, availableDays, access_token):
	try:
		headers = {
		'accept': 'application/json',
		'content-type': 'application/x-www-form-urlencoded',
		}
		
		if availableDays==0:
			data={
				"sale_terms": 
				[{
					"id": "MANUFACTURING_TIME",
					"value_id": "null",
					"value_name": "null"
				}]
			}  

		if availableDays>0:
			data={
				"sale_terms": 
				[{
					"id": "MANUFACTURING_TIME",
					"value_name": str(availableDays)+" días"
				}]
			}  

		url='https://api.mercadolibre.com/items/'+str(item_id_meli)+'?access_token='+access_token
		#print (url)
		r=requests.put(url, headers=headers, data=json.dumps(data) )
		#print ('Actualizado ', item_id_meli)

	except Exception as e:
		print('Error en update_manufacturing_time(): '+str(e) )


if __name__ == '__main__':  
	user_id = 160190870
	'''
	sku='1615430015-BOS'
	availableDays = 10
	i=0
	access_token = recupera_meli_token(user_id)
	item_id_meli = get_mlm_from_meli(user_id, sku, access_token)
	print (i, user_id,sku,item_id_meli, availableDays)
	update_manufacturing_time(item_id_meli, availableDays, access_token)

	'''
	no_econtrados = open('no_actualizados_disponibles2.csv', 'w')

	
	archivo =  open('disponibilidad.csv')
	i=0
	for producto in archivo:
		disponible=producto[:-1].split(',')
		sku=disponible[0]
		availableDays = int(disponible[1])
	
		user_id = 160190870
		#user_id = 25523702
		access_token = recupera_meli_token(user_id)
		item_id_meli = get_mlm_from_meli(user_id, sku, access_token)
		#print (i, user_id,sku,item_id_meli, availableDays)
		update_manufacturing_time(item_id_meli, availableDays, access_token)
		i=i+1
	no_econtrados.close()

		
