import sys
import json
import requests
import pprint
def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        return None

def webhook():
        token_venti=get_token_venti()
        headers={"content-type":"application/json","Authorization":"bearer "+ token_venti}
        body=[{"sku":"2000022136","quantity": "2"}]

        url='https://ventiapi.azurewebsites.net/api/stock/updatestock'

        r=requests.post(url, headers=headers, data= json.dumps(body) )     
        print r.json()



#token_venti=get_token_venti()
webhook()
