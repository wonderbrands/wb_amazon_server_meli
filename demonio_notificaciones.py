#!/usr/bin/python
import sys
import json
from flask import Flask, request, abort
import requests
import datetime
from datetime import datetime, date, time, timedelta
import pprint 
import logging


app = Flask(__name__)



@app.route('/post_orders_meli', methods=['POST'])
def webhook():
	try:
		if request.method == 'POST':
			content = request.json
			notification=json.loads(json.dumps(content))
			resource=notification['resource'].split("/")[1]
			order_id=notification['resource'].split("/")[2]
			seller_id=notification['user_id']
			topic=notification['topic']
			application_id=notification['application_id']
			attempts=notification['attempts']
			sent=notification['sent']
			received=notification['received']
			print (notification)
			'''
			if resource=='orders':
				print '================================================================================================'
				print 'INICIO:', seller_id, topic,resource,order_id, attempts
				access_token=recupera_meli_token(seller_id)
				orden = get_order_meli(seller_id, order_id, access_token)
				print 'ORDEN:',orden
				#logging.info('RESPUESTA ORDEN|'+orden)
				if orden:
					result  = make_map_meli_odoo(orden)
					print 'Resultado al intentar crear la Orden: ', result, ' Order Id: ', order_id

			'''
			return '', 200
		else:
			abort(400)
	
		return notification
	except Exception as e:
		print ('Error' +str(e))
 
		

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8080)