import multiprocessing
import os
import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
import sys 
from oauth_odoo12 import *

oauth=oauth_odoo12_production()
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
    
    def productos_x_marca_en_odoo12(self, marca):
        try:
            lista_urrea=[]
            productos_urrea = {}
            data = {
            "model":"product.category",
            "domain":json.dumps([["name","=", marca]]),
            "fields":json.dumps(["name"]),
            }
            response =api.execute("/api/search_read", data=data)
            id_urrea = response[0]['id']
            print (id_urrea)

            data = {
            "model":"product.template",
            "limit":limite, 
            "domain":json.dumps([["categ_id","=", id_urrea]]),
            "fields":json.dumps(["default_code"]),
            }
            response =api.execute("/api/search_read", data=data)
            #print(response)
            for producto in response:
                sku=producto['default_code']
                id_product = producto['id']
                productos_urrea[sku]=id_product
            return productos_urrea
        except Exception as e:
            print('Error en productos_urrea_en_odoo12 : '+str(e))
            return False

    def update_stock_exclusivas(self, default_code, stock_exclusivas):
        try:
            data = {
            "model":"product.template",
            "domain":json.dumps([["default_code","=", default_code]]),
            "fields":json.dumps(["default_code"]),
            }
            response =api.execute("/api/search_read", data=data)
            ids=response[0]["id"]
            #print (ids)
            
            # update product
            values = {
                'stock_exclusivas': stock_exclusivas,
            }

            data = {
                "model": "product.template",
                'ids':[ids],
                "values": json.dumps(values),
            }
            #print (data)
            response = api.execute('/api/write', type="PUT", data=data)
            print(response)
            return True
        except Exception as e:
            if 'token_expired' in str(e):
                api.authenticate()
            print ('Error en update_stock_exclusivas(): '+str(e) )
            return False


def process_update():
    try:
        archivo_importacion = open ('existencias_exclusivas.csv')
        
        i=0
        for linea in archivo_importacion:
            if i>1463:
                print (i, linea[:-1].split(','))
                producto_exclusivas = linea[:-1].split(',')

                sku_producto = producto_exclusivas[0]
                stock_exclusivas = int(producto_exclusivas[1])
                resultado = api.update_stock_exclusivas(sku_producto, stock_exclusivas)
                
            i=i+1
        archivo_importacion.close()
        return True
    except Exception as e:
        print ('Error en process_update(): '+str(e) )
        return False

WORKER_NUMBER = 3
if __name__ == '__main__':
    api = RestAPI()
    api.authenticate()

    jobs = []
    for i in range(WORKER_NUMBER):
        p = multiprocessing.Process(target=process_update, args=())
        jobs.append(p)
        p.start()
        

