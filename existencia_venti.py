
import json
import requests
import logging

def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        logging.info ("Error en get_token_venti(): ", str(e) )
        logging.info("Error en get_token_venti(): "+ str(e))
        return None


def get_stock_from_venti(sku, access_token_venti):
	headers={"content-type":"application/json","Authorization":"bearer " + access_token_venti}
	
	#try:
	url='https://ventiapi.azurewebsites.net/api/stock/getpricestockbychannel/?id='+sku
	logging.info(url)
	r = requests.get(url, headers=headers )
	print ('Respuesta Venti:'+str(r.text) )
	'''
	stock_venti={}
	channelData = r.json()['channelData']
	for channel in channelData:
		canal= channel['channel'] 
		cantidad = channel['quantity']
		#logging.info(canal+','+ str(cantidad) )
		stock_venti[canal]=cantidad
	
	logging.info ('Venti:'+str(stock_venti) )
	'''
	#return stock_venti
	#print (json.dumps( r.json(), sort_keys=True, indent=4, separators=(',', ': ')) )
	#return stock_venti
	#except Exception as e:
	#	logging.info('Error en  get_stock_from_venti():'+str(e))

	
if __name__ == '__main__':	
	access_token_venti = get_token_venti()

	sku= '25.2531.20-URTEC'
	#sku='201508'
	print ('Buscando datos para:'+ sku)
	get_stock_from_venti(sku, access_token_venti)