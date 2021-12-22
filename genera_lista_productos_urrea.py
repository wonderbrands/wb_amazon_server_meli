import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import sys 
from oauth_odoo12 import *

oauth=oauth_odoo12_test()
url=oauth['url']
client_id=oauth['client_id']
client_secret=oauth['client_secret']

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

    def execute(self, enpoint, type="GET", data={}):
        if type == "POST":
            response = self.oauth.post(self.route(enpoint), data=data)
        elif type == "PUT":
            response = self.oauth.put(self.route(enpoint), data=data)
        else:
            response = self.oauth.get(self.route(enpoint), data=data)
    
        if response.status_code != 200:
            raise Exception(pprint(response.json()))
        else:
            return response.json()
    
    def productos_urrea_en_odoo12(self, marca):
        try:
            lista_urrea=[]
            data = {
            "model":"product.category",
            "domain":json.dumps([["name","=", marca]]),
            "fields":json.dumps(["name"]),
            }
            response =api.execute("/api/search_read", data=data)
            id_urrea = response[0]['id']
            #print (id_urrea)

            data = {
            "model":"product.template",
            "limit":limite, 
            "domain":json.dumps([["categ_id","=", id_urrea]]),
            "fields":json.dumps(["id","default_code"]),
            }
            response =api.execute("/api/search_read", data=data)
            for producto in response:
                print (producto)
            return True
        except Exception as e:
            print('Error en productos_urrea_en_odoo12 : '+str(e))
            return False


api = RestAPI()
api.authenticate()

if __name__ == '__main__':
    marcas=['Urrea', 'Lock', 'Surtek']
    for marca in marcas:
        api.productos_urrea_en_odoo12(marca)

