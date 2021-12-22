#!/usr/bin/python
import requests
import pytz
import datetime
import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

url ='https://somosreyes-test-1289955.dev.odoo.com'
#url ='https://somosreyes.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

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
        elif type == "DELETE":
            response = self.oauth.delete(self.route(enpoint), data=data)
        else:
            response = self.oauth.get(self.route(enpoint), data=data)
        if response.status_code != 200:
            raise Exception(pprint(response.json()))
        else:
            #print (response.json() )
            return response.json()

    def update_tokens_in_odoo(self, client_id, access_token, refresh_token, token_type, expires, last_date_retrieve):
        try:
            data = {
            "model":"tokens_markets.tokens_markets",
            "domain":json.dumps([["client_id","=", client_id]]),
            "fields":json.dumps(["client_id", "seller", "name_markeplace"]),
            }
            response =api.execute("/api/search_read", data=data)
            print ('ODOO RESPONSE READ|'+str(response) )
            ids=response[0]["id"]
            print (ids)
            
            # update product
            values = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type':token_type, 
                'expires':expires,
                'last_date_retrieve':last_date_retrieve,
            }

            data = {
                "model": "tokens_markets.tokens_markets",
                'ids':[ids],
                "values": json.dumps(values),
            }
            print ('DATA ODOO|'+ str(data) )
            response = api.execute('/api/write', type="PUT", data=data)
            print('ACTUALIZANDO ODOO|'+ str(response) )
            return True
        except Exception as e:
            print ('Error en update_tokens_in_odoo(): '+ str(e) )
            return False


def obtener_token_meli_oficiales(client_id, client_secret):
    try:
        token_dir='/home/ubuntu/meli/tokens_meli_oficiales.txt'
        archivo_tokens=open(token_dir, 'w')

        headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        }   
        
        url='https://api.mercadolibre.com/oauth/token?grant_type=client_credentials&client_id='+str(client_id)+'&client_secret='+str(client_secret)
        r=requests.post(url, headers=headers)
        #archivo_tokens.write(str(r.text) )
        archivo_tokens.close()
        #print (r.json() )   
        return r.json()
    except Exception as e:
        print (str(e))
        return False




if __name__ == '__main__':
    api = RestAPI()
    api.authenticate()

    #---- CUENTA SOMOS-REYES VENTAS
    client_id='5703097592380294'
    client_secret='Fn5yHq1e1DBgy2EiRk7rLhsyRexcZYAQ'

    access_tokens = obtener_token_meli_oficiales(client_id, client_secret)
    print ('access_tokens:',access_tokens)
    
    try:
        
        if access_tokens:
            access_token = access_tokens['access_token']
            refresh_token = access_tokens['refresh_token']
            token_type = access_tokens['token_type']
            expires = access_tokens['expires_in']
            print(access_token, refresh_token, token_type, expires)

            time_zone= pytz.timezone('America/Mexico_City')
            Mexico_City_time = datetime.datetime.now(tz=time_zone)
            fecha = Mexico_City_time.isoformat(' ')[:-13]

            last_date_retrieve = fecha
            api.update_tokens_in_odoo(client_id, access_token, refresh_token, token_type, expires, last_date_retrieve)      
    except Exception as e:
        print('Error: ' +str(e))