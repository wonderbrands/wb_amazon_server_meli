#!/usr/bin/python
import sys
import json
from flask import Flask, request, abort
import requests
import datetime
from datetime import datetime, date, time, timedelta


app = Flask(__name__)


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