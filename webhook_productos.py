import json
import requests
import logging
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import datetime
import email
import smtplib 
from email.mime.text import MIMEText
url ='https://somosreyes-test-973378.dev.odoo.com'
#url ='https://somosreyes.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'


date_time = datetime.datetime.now()
date_time_iso= date_time.isoformat() 
fecha=date_time_iso.split('T')[0]

log_file='/home/ubuntu/meli/logs/web_hooks_'+str(fecha)+'.log'
logging.basicConfig(filename=log_file,format='%(asctime)s|%(name)s|%(levelname)s|%(message)s', datefmt='%Y-%d-%m %I:%M:%S %p',level=logging.INFO)

limite =100000
class RestAPI:
	def __init__(self):
		self.url = url
		self.client_id = client_id
		self.client_secret = client_secret

		self.client = BackendApplicationClient(client_id=self.client_id)
		self.oauth = OAuth2Session(client=self.client)

	def route(self, url):
		if url.startswith('/'):
			url = "%s%s" % (self.url, url)
			#print (url)
		return url

	def authenticate(self):
		self.oauth.fetch_token(
			token_url=self.route('/api/authentication/oauth2/token'),
			client_id=self.client_id, client_secret=self.client_secret
		)
		#print( self.oauth.fetch_token(token_url=self.route('/api/authentication/oauth2/token'),client_id=self.client_id, client_secret=self.client_secret) )


	def execute(self, enpoint, type="GET", data={}):
		if type == "POST":
			response = self.oauth.post(self.route(enpoint), data=data)
		elif type == "PUT":
			response = self.oauth.put(self.route(enpoint), data=data)
		#elif type == "DELETE":
		#	response = self.oauth.delete(self.route(enpoint), data=data)
		else:
			response = self.oauth.get(self.route(enpoint), data=data)
		if response.status_code != 200:
			raise Exception(pprint(response.json()))
		else:
			#print (response.json() )
			return response.json()

def get_stock_from_venti(sku, access_token_venti):
	headers={"content-type":"application/json","Authorization":"bearer " + access_token_venti}
	try:
		url='https://ventiapi.azurewebsites.net/api/stock/getpricestockbychannel/'+sku
		r = requests.get(url, headers=headers )
		#print ( r.json() )
		channelData = r.json()
		for channel in channelData:
			print (channel)

		print (json.dumps( r.json(), sort_keys=True, indent=4, separators=(',', ': ')) )
		#return stock_venti
	except Exception as e:
		raise e

	
#-------------------- Funciones de Webhooks---------------------------------------------------------------------------
def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        logging.info("Error en get_token_venti(): "+ str(e))
        return None

def get_stock_real_from_odoo(product_id):
	try:
		data = {
		'model': "product.product",
		'domain': json.dumps([['id', '=', product_id]]),
		'fields': json.dumps(['default_code','stock_real','stock_exclusivas', 'stock_urrea', 'stock_markets','disponibilidad']),
		}
		response = api.execute('/api/search_read', data=data)
		#print (json.dumps(response, indent=4, sort_keys=True))
		stock_real = response[0]['stock_real']
		stock_exclusivas = response[0]['stock_exclusivas']
		stock_urrea = response[0]['stock_urrea']
		stock_markets =response[0]['stock_markets']
		default_code = response[0]['default_code']
		disponibilidad = response[0]['disponibilidad']
		#print ('DISPONIBILIDAD: ', disponibilidad)
		return dict(default_code=default_code, stock_real=stock_real, stock_exclusivas=stock_exclusivas, stock_urrea=stock_urrea, stock_markets=stock_markets, disponibilidad=disponibilidad)
	except Exception as e:
		print('ERROR|get_stock_real_from_odoo()|'+str(e) )
		api.authenticate()
		return False

def update_stock_markets(product_id, stock_markets_nuevo):
	try:
		values = {'stock_markets' : stock_markets_nuevo,}
		data = {
				"model": "product.product",
				'ids':product_id,
				"values": json.dumps(values),
			}
		print (data)
		response = api.execute('/api/write', type="PUT", data=data)
		print('UPDATE stock_makets|',response)

	except Exception as e:
		print('Error|update_stock_markets|'+str(e))
		return False

def webhook_venti(product_id):
	try:
		stock_markets_nuevo=0
		stock_from_odoo = get_stock_real_from_odoo(product_id)
		default_code = stock_from_odoo['default_code']
		stock_real = stock_from_odoo['stock_real'] 
		stock_markets_actual = stock_from_odoo['stock_markets']
		stock_exclusivas = stock_from_odoo ['stock_exclusivas']
		stock_urrea = stock_from_odoo ['stock_urrea']
		disponibilidad =  stock_from_odoo ['disponibilidad']
		
		#print ('ODOO| stock_real:', stock_real)

		stock_markets_nuevo = (stock_real + stock_exclusivas + stock_urrea) 
		if stock_markets_actual==0:
			stock_markets_nuevo = stock_real + stock_exclusivas + stock_urrea 
			stock_markets_nuevo = stock_markets_actual 
			#print ('ODOO|stock_markets_actual:',stock_markets_actual, ' stock_markets_nuevo',  stock_markets_nuevo)
		
		print ('ODOO|stock_real:',stock_real,', stock_exclusivas:', stock_exclusivas, ', stock_urrea:', stock_urrea, ', disponibilidad', disponibilidad)
		logging.info('ODOO|stock_real:'+str(stock_real)+', stock_exclusivas:'+str(stock_exclusivas)+ ', stock_urrea:'+str(stock_urrea) + ', disponibilidad:'+str(disponibilidad))

		stock_mercadolibre =  stock_real + stock_exclusivas + stock_urrea 
		if stock_mercadolibre < 0:
			stock_mercadolibre=0

		stock_linio = stock_real + stock_exclusivas 
		if stock_linio < 0:
			stock_linio=0

		stock_amazon =  stock_real + stock_exclusivas + stock_urrea 
		if stock_amazon < 0:
			stock_amazon = 0

		stock_prestashop =  stock_real + stock_exclusivas + stock_urrea 
		if stock_prestashop < 0:
			stock_prestashop = 0

		stock_walmart =  stock_real + stock_exclusivas 
		if stock_walmart < 0:
			stock_walmart = 0

		stock_claroshop =  stock_real + stock_exclusivas + stock_urrea 
		if stock_claroshop < 0:
			stock_claroshop = 0

		#print(default_code,',',stock_amazon,',',stock_linio,',',stock_prestashop,',',stock_claroshop,',',stock_mercadolibre)
		access_token_venti = get_token_venti()

		if stock_mercadolibre < stock_markets_nuevo:
			stock_markets_nuevo = stock_mercadolibre		

		#print ('Actualizando en Odoo SKU: ', default_code, ', stock_markets_nuevo: ', stock_markets_nuevo)
		update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti, disponibilidad)
		
		#--- Actualiza el campo stock_markets en Odoo.
		#update_stock_markets(product_id, stock_markets_nuevo)
	
	except Exception as e:
		print ('Error|webhook_venti(): '+str(e) )
		return False

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
		mensaje['To']= "moisantgar@gmail.com, lcheskin@gmail.com, sistemas@somos-reyes.com"
		mensaje['Subject']="Aviso lista drop y disponiles de urrea."
		# Envio del mensaje
		mailServer.sendmail(mensaje['From'], mensaje["To"].split(",") ,  mensaje.as_string())
		print ("Se ha enviado un correo de aviso a Leon y Moi y Jesus") 
		# Cierre de la conexion
		mailServer.close()
	except Exception as e:
		print ("No se pudo enviar el email de aviso! -> "+ str(e) )
		logging.info ("No se pudo enviar el email de aviso! -> "+ str(e) )

def update_product_venti(default_code, stock_mercadolibre, stock_linio, stock_amazon, stock_prestashop, stock_walmart, stock_claroshop, access_token_venti, disponibilidad):
	try:
		headers={"content-type":"application/json","Authorization":"bearer "+ access_token_venti}
		body={
		        "sku": str(default_code),
				"channelData": [
					{
						"channel": "mercadolibre",
						"quantity": int(stock_mercadolibre)
					},
					{
						"channel": "linio",
						"quantity":int(stock_linio)
					},
					{
						"channel": "amazon",
						"quantity": int(stock_amazon)
					},
					{
						"channel": "prestashop",
						"quantity": int(stock_prestashop)
					}, 
					{
						"channel": "walmart",
						"quantity": int(stock_walmart)
					}, 
					{
						"channel": "claroshop",
						"quantity": int(stock_claroshop)
					}, 
				]
			}

		url='https://ventiapi.azurewebsites.net/api/stock/updatepricestockbychannel'
		r=requests.post(url, headers=headers, data= json.dumps(body) )
		logging.info("VENTI HEADERS|"+ str(r.request.headers) )
		logging.info("VENTI BODY|"+ str(r.request.body) )

		#print ("VENTI|"+r.text)
		logging.info("VENTI RESPONSE|"+r.text)
		print ('WEBHOOK|Actualizando SKU: '+str(default_code)+'|Meli '+str(stock_mercadolibre)+'|Linio '+str(stock_linio)+' |Amazon  '+str(stock_amazon)+'|Prestashop  '+str(stock_prestashop)+'|Walmart  '+str(stock_walmart)+' |ClaroShop  '+str(stock_claroshop)+' en Venti.')
		logging.info('WEBHOOK|Actualizando SKU: '+str(default_code)+'|Meli '+str(stock_mercadolibre)+'|Linio '+str(stock_linio)+' |Amazon  '+str(stock_amazon)+'|Prestashop  '+str(stock_prestashop)+'|Walmart  '+str(stock_walmart)+' |ClaroShop  '+str(stock_claroshop)+' en Venti.')
		if "Producto no encontrado" in r.text:
			print (r.text+' SKU: ', default_code )
			logging.info (r.text+' SKU: ', default_code )

		if "Authorization has been denied for this request" in r.text:
			logging.info(r.text)
			get_token_venti()
			
	except Exception as e:
		#print('ERROR|update_product_venti|', str (e))
		logging.info ('ERROR|update_product_venti|'+str(e))
		notificacion='ERROR|update_product_venti|'+str(e)
		envia_email(notificacion)
		return False

	
#--------------------  Fin Funciones de Webhooks---------------------------------------------------------------------------

def diferencia_minutos(fecha_movimiento):
	try:
		#hoy = datetime.datetime.now()# Local

		hoy_utc = datetime.datetime.utcnow() #UTC

		fecha_utc = str(hoy_utc).split(' ')[0].split('-')
		anio=int(fecha_utc[0])
		mes=int(fecha_utc[1])
		dia=int(fecha_utc[2])
		horario_utc = str(hoy_utc).split(' ')[1].split('.')[0].split(':')

		year_movimiento = int(fecha_movimiento.split(' ')[0].split('-')[0])
		month_movimiento = int(fecha_movimiento.split(' ')[0].split('-')[1])
		day_movimiento = int(fecha_movimiento.split(' ')[0].split('-')[2])

		h=int(fecha_movimiento.split(' ')[1].split(':')[0])
		m=int(fecha_movimiento.split(' ')[1].split(':')[1])

		hora_entrada = datetime.datetime(year=year_movimiento,month=month_movimiento, day=day_movimiento, hour=h, minute=m)

		horas_transcurridas_movimiento =  (hoy_utc - hora_entrada).total_seconds() // 3600
		mins_transcurridos_movimiento =  ((hoy_utc- hora_entrada).total_seconds() % 3600) // 60

		return dict(horas_transcurridas_movimiento=horas_transcurridas_movimiento,mins_transcurridos_movimiento=mins_transcurridos_movimiento )

	except Exception as e:
		print ('Error|diferencia_minutos(): '+str(e) )
		return False
		

def get_stock_move_line(fecha_rastreo):
	intervalo_horas = 0
	intervalo_minutos=59
	try:
		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastreo],['reference','like','WH/IN/%']]),
		'fields': json.dumps(['reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id', 'location_dest_id']),
		'order':['date'],
		'limit': 100000

		}
		response = api.execute('/api/search_read', data=data)
		
		for move in response:
			fecha_movimiento = move['date']
			reference = move['reference']
			product_id = move['product_id'][0]
			quantity_done = move['quantity_done']
			location_dest_id = move['location_dest_id'][1]
			default_code = move['product_id'][1].split(']')[0][1:]
			horas_minutos = diferencia_minutos(fecha_movimiento)		
			horas = horas_minutos['horas_transcurridas_movimiento']
			minutos = horas_minutos['mins_transcurridos_movimiento']
			
			if horas == intervalo_horas and minutos <= intervalo_minutos:
				print fecha_movimiento, horas, minutos,reference, default_code, product_id,quantity_done,location_dest_id 
				logging.info( str(fecha_movimiento)+', '+str(horas)+', '+str(minutos)+', '+str(reference)+', '+str(default_code)+', '+str(product_id) )
				#webhook_venti(product_id)		
		
		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastreo],['reference','like','WH/OUT/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id', 'location_dest_id']),
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)

		
		for move in response:
			fecha_movimiento = move['date']
			reference = move['reference']
			product_id = move['product_id'][0]
			quantity_done = move['quantity_done']
			location_dest_id = move['location_dest_id'][1]
			default_code = move['product_id'][1].split(']')[0][1:]
			horas_minutos = diferencia_minutos(fecha_movimiento)		
			horas = horas_minutos['horas_transcurridas_movimiento']
			minutos = horas_minutos['mins_transcurridos_movimiento']
			
			if horas == intervalo_horas and minutos <= intervalo_minutos and ('LINIO' in location_dest_id or 'MELI' in location_dest_id or 'AMAZO' in location_dest_id):
				print fecha_movimiento, horas, minutos,reference, default_code, product_id,quantity_done,location_dest_id 
				logging.info( str(fecha_movimiento)+', '+str(horas)+', '+str(minutos)+', '+str(reference)+', '+str(default_code)+', '+str(product_id) )
				#webhook_venti(product_id)

		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastreo],['reference','like','WH/INT/%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id', 'location_dest_id']),
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)
		
		for move in response:
			fecha_movimiento = move['date']
			reference = move['reference']
			product_id = move['product_id'][0]
			quantity_done = move['quantity_done']
			location_dest_id = move['location_dest_id'][1]
			default_code = move['product_id'][1].split(']')[0][1:]
			horas_minutos = diferencia_minutos(fecha_movimiento)		
			horas = horas_minutos['horas_transcurridas_movimiento']
			minutos = horas_minutos['mins_transcurridos_movimiento']
			
			if horas == intervalo_horas and minutos <= intervalo_minutos and ('LINIO' in location_dest_id or 'MELI' in location_dest_id or 'AMAZO' in location_dest_id):
				print fecha_movimiento, horas, minutos,reference, default_code, product_id,quantity_done,location_dest_id 
				logging.info( str(fecha_movimiento)+', '+str(horas)+', '+str(minutos)+', '+str(reference)+', '+str(default_code)+', '+str(product_id) )
				#webhook_venti(product_id)

		data = {
		'model': "stock.move",
		'domain': json.dumps([['date', 'like', fecha_rastreo],['reference','like','INV%']]),
		'fields': json.dumps([ 'reference','product_id','date', 'product_qty', 'product_uom_qty', 'quantity_done', 'remaining_qty', 'reserved_availability', 'warehouse_id', 'location_dest_id']),
		'order':['date'],
		'limit': 100000
		}
		response = api.execute('/api/search_read', data=data)
		
		for move in response:
			fecha_movimiento = move['date']
			reference = move['reference']
			product_id = move['product_id'][0]
			quantity_done = move['quantity_done']
			location_dest_id = move['location_dest_id'][1]
			default_code = move['product_id'][1].split(']')[0][1:]
			horas_minutos = diferencia_minutos(fecha_movimiento)		
			horas = horas_minutos['horas_transcurridas_movimiento']
			minutos = horas_minutos['mins_transcurridos_movimiento']
			
			if horas == intervalo_horas and minutos <= intervalo_minutos and ('LINIO' in location_dest_id or 'MELI' in location_dest_id or 'AMAZO' in location_dest_id):
				print fecha_movimiento, horas, minutos,reference, default_code, product_id,quantity_done,location_dest_id 
				logging.info( str(fecha_movimiento)+', '+str(horas)+', '+str(minutos)+', '+str(reference)+', '+str(default_code)+', '+str(product_id) )		
				#webhook_venti(product_id)
		
		return True
	except Exception as e:
		print str(e)


if __name__ == '__main__':
	
	api = RestAPI()
	api.authenticate()
	hoy_utc = datetime.datetime.utcnow() #UTC
	hoy = datetime.datetime.now() #UTC
	fecha_rastreo = str(hoy_utc).split(' ')[0]
	print 'Fecha y Hora Local: ', hoy
	print 'Fecha de rastreo (UTC): ', fecha_rastreo+'%'
	get_stock_move_line(fecha_rastreo+'%')
	'''
	access_token_venti = get_token_venti()
	print (access_token_venti)
	sku = '57537-INTEX'
	get_stock_from_venti(sku, access_token_venti)
	'''
