#!/usr/bin/python
import mysql.connector #as mariadb
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector import pooling
import sys
import json
from flask import Flask, request, abort
import requests
import datetime
from datetime import datetime, date, time, timedelta
from connector_mariadb import *
import logging

app = Flask(__name__)

url_sr ='https://somosreyes-test-348102.dev.odoo.com'
client_id_sr ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret_sr ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

connect=connect_to_orders()
cursor=connect['cursor']
connection_object=connect['connection_object']

def insertar_notificaciones_orders_meli(notification):
	
	resource=notification['resource'].split("/")[1]

	if resource=='orders':
		order_id=notification['resource'].split("/")[2]
		user_id=notification['user_id']
		topic=notification['topic']
		application_id=notification['application_id']
		attempts=notification['attempts']
		sent=notification['sent']
		received=notification['received']
		saved = datetime.now()

		sql=""
		sql+="INSERT INTO notify_meli("
		sql+="order_id,"
		sql+="application_id,"
		sql+="user_id,"
		sql+="topic,"
		sql+="attempts,"
		sql+="sent,"
		sql+="received,"
		sql+="saved"
		sql+=") VALUES ("
		sql+="'"+str(order_id)+"',"
		sql+="'"+str(application_id)+"',"
		sql+="'"+str(user_id)+"', "
		sql+="'"+str(topic)+"', "
		sql+=str(attempts)+", "
		sql+="'"+str(sent)+"', "
		sql+="'"+str(received)+"', "
		sql+="'"+str(saved)[:-1]+"'"
		sql+=")"
		print 'INSERT SQL|'+str(sql)
		#logging.info('INSERT SQL|'+str(sql))
		try:
			cursor.execute(sql)
			connection_object.commit()
			print 'MYSQL|'+str(order_id)
			#logging.info('MYSQL|'+str(order_id))
			#cursor.close()
			return True
		except Exception as e:
			print 'ERROR SQL|'+str(e)
			#logging.info('ERROR SQL|'+str(e))
			#send_email_order_error(order_id, str(e) )
			#connection_object.rollback()
			#cursor.close()
			return False

@app.route('/post_orders_meli', methods=['POST'])
def webhook():
	try:
		if request.method == 'POST':
			content = request.json
			notification=json.loads(json.dumps(content))
			insertar_notificaciones_orders_meli(notification)
			return '', 200
		else:
			abort(400)
	except Exception as e:
		cursor.close()
		connection_object.close()
		return 'Error: '+str(e) 


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8080)