#!/usr/bin/python
from flask import Flask, request, abort
app = Flask(__name__)

@app.route('/saludo', methods=['GET'])
def webhook():
	try:
		if request.method == 'GET':

			return '<H1>HOLA SHERY!! HERMOSA!</H1>', 200
		else:
			abort(400)
	except Exception as e:
		return 'Error: '+str(e) 


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8080)