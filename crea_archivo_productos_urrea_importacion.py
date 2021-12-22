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


def disponibilidad_urrea(i, sku_producto):
    try:
        headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
        }
        data= '{"usuario": "uhpruebas", "password": "urre@"}'

        url='http://148.244.195.54:90/disponibilidad?id='+ sku_producto +'&cantidad=5'
        r=requests.post(url, headers=headers, data=data)
        #print (r.text)
        if(r.status_code==200 ):
    
            codigoDeProducto=''
            disponibilidad=''
            estatusInventario=''
            Total=0
            
            if len(r.json()):
                codigoDeProducto = r.json()['disponibilidadProducto']['codigoDeProducto']
                disponibilidad = r.json()['disponibilidadProducto']['disponibilidad']
                estatusInventario = r.json()['disponibilidadProducto']['estatusInventario']
                if ( str(estatusInventario)=='Con reservas' or str(estatusInventario)=='Disponible'):
                    disponible_urrea=1000
                else:
                    disponible_urrea =0

            return dict(sku_producto=sku_producto, disponible_urrea=disponible_urrea)

        else:
            notificacion="<h3>No se pudo conectar a Urrea Se mantiene el archivo anterior  </h3>"
            #envia_email(notificacion)
            return False 

        return r.text
    except Exception as e:
        return False

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
            "model":"product.product",
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
            #default_code = response[0]['default_code']
            #print (default_code)
            #print(response)
            for producto in response:
                sku=producto['default_code']
                id_product = producto['id']
                productos_urrea[sku]=id_product
            return productos_urrea
        except Exception as e:
            print('Error en productos_urrea_en_odoo12 : '+str(e))
            return False

    def update_stock_urrea(self, default_code, stock_urrea):
        try:
            data = {
            "model":"product.template",
            "domain":json.dumps([["default_code","=", default_code]]),
            "fields":json.dumps(["name", "default_code", "stock_urrea"]),
            }
            response =api.execute("/api/search_read", data=data)
            #print (response)
            ids=response[0]["id"]
            #print (ids)
            
            # update product
            values = {
                'stock_urrea': stock_urrea,
            }

            data = {
                "model": "product.template",
                'ids':[ids],
                "values": json.dumps(values),
            }
            #print (data)
            response = api.execute('/api/write', type="PUT", data=data)
            print(response)

        except Exception as e:
            #api.authenticate()
            print ('Error en update_stock_urrea(): '+str(e) )

if __name__ == '__main__':

    archivo_importacion = open ('importacion_urrea.csv', 'w')

    api = RestAPI()
    api.authenticate()

    marca='Surtek'
    ids_default_code = api.productos_x_marca_en_odoo12(marca)
    #print(ids_default_code)

    i=0
    for sku_producto in ids_default_code:
        disponibilidad = disponibilidad_urrea(i, sku_producto[:-4])
        print(i, disponibilidad)
        stock_urrea = disponibilidad['disponible_urrea']
        api.update_stock_urrea(sku_producto, stock_urrea)
        i=i+1



    '''
    i=0
    for sku_producto in ids_default_code:
        disponibilidad = disponibilidad_urrea(i, sku_producto[:-4])
        #print(disponibilidad)
        id_del_sku = ids_default_code.get(sku_producto)
        print(i,id_del_sku, disponibilidad['disponible_urrea'])
        archivo_importacion.write(str(id_del_sku)+','+ str(disponibilidad['disponible_urrea'])+'\n' )
        i=i+1
        if i>10:
            break
    archivo_importacion.close()
    '''
    



