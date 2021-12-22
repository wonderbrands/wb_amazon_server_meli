import json
import requests

def post_webhook(): 
    try:
        headers = {'Accept': 'application/json','content-type': 'application/json'}
        data = {'data':'Mensaje'}
        url='http://52.70.87.2:8082/webhook'
        r=requests.post(url, headers=headers, data=json.dumps(data))
        print r.request.headers
        print r.text 

        
    except Exception as e:
        print (' Error order_shipment_meli(): '+ str(e))
        return False

post_webhook()