#! /usr/bin/python3
# -*- coding: utf-8 -*-
import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauth_odoo12 import *

oauth=oauth_odoo12_production()
url=oauth['url']
client_id=oauth['client_id']
client_secret=oauth['client_secret']
limite =100

def get_stock_real_by_sku(sku):
    data = {"model":"product.product",
            "domain":json.dumps([["default_code","=",sku]]),
            "fields":json.dumps(["id", "default_code","stock_real", "stock_reservado", "name"]),
            }
    response =api.execute("/api/search_read", data=data)
    print (response)
    stock_real=response[0]['stock_real']
    stock_reservado= response[0]['stock_reservado']
    stock_neto= stock_real-stock_reservado
    print (stock_neto)



def get_stock_quant_ids(seller_sku):
    try:
        data = {
            'model': "product.product",
            'domain': json.dumps([['default_code', '=', seller_sku]]),
            'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids', 'virtual_available' ]),
        }

        response = api.execute('/api/search_read', data=data)
        #print (json.dumps(response, indent=4, sort_keys=True))#
        stock_quant_ids=response[0]['stock_quant_ids']
        return stock_quant_ids
    except Exception as e:
        print('Error en get_stock_quant_ids : '+str(e))
        api.authenticate()
        return False

def get_stock_quant(id):
    try:
        data = {
        'model': "stock.quant",
        'domain': json.dumps([['id', '=', id]]),
        'fields': json.dumps(['id' ,'quantity', 'location_id', 'reserved_quantity']),
        }
        response = api.execute('/api/search_read', data=data)
        #print (json.dumps(response, indent=4, sort_keys=True))
        location_id =response[0]['location_id']
        quantity=response[0]['quantity']    
        reserved_quantity =response[0] ['reserved_quantity']
        return dict(location_id=location_id, quantity=quantity, reserved_quantity=reserved_quantity)
    except Exception as e:
        print('Error en get_stock_quant : '+str(e))
        api.authenticate()
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
        else:
            response = self.oauth.get(self.route(enpoint), data=data)

    
        if response.status_code != 200:
            api.authenticate() # OJO COLOCAR PARA REACTIVAR TIMEOUT TOKEN
            raise Exception(pprint(response.json()))
        else:
            return response.json()

    
    def productos_en_odoo12(self, sku,i):
        try:
            data = {
            "model":"product.product",
            "domain":json.dumps([["default_code","=",sku]]),
            "fields":json.dumps(["id", "default_code","stock_exclusivas", "stock_urrea", "virtual_available"]),
            }
            response =api.execute("/api/search_read", data=data)
            #print(response)
            #print('SKU,StockAmazon,StockLinio,StockPrestashop,StockClaroShop,StockMeli')

            for producto in response:
                #---Calculamos politicas de stock para cada marketplace
                seller_sku=str(producto['default_code'])

                quantity=0
                stock_quant_ids = get_stock_quant_ids(seller_sku)
                if stock_quant_ids:
                    for id in stock_quant_ids:
                        stock_quant = get_stock_quant(id)
                        if stock_quant:
                            location_id = stock_quant['location_id']    
                            if location_id[1] == 'AG/Stock':
                                quantity=int(stock_quant['quantity'] ) - int(stock_quant['reserved_quantity'])
                else:
                    quantity = producto['virtual_available']
            
                stock_exclusivas = producto['stock_exclusivas']
                stock_urrea = producto['stock_urrea']

                stock_mercadolibre =  int(quantity + int(stock_exclusivas) + int(stock_urrea) )
                if stock_mercadolibre < 0:
                    stock_mercadolibre=0

                stock_linio = int(quantity + int(stock_exclusivas) )
                if stock_linio < 0:
                    stock_linio=0
                stock_amazon =  int(quantity + int(stock_exclusivas) + int(stock_urrea))

                stock_prestashop =  int(quantity + int(stock_exclusivas) + int(stock_urrea))
                if stock_prestashop < 0:
                    stock_prestashop = 0

                stock_walmart =  int(quantity + int(stock_exclusivas) )
                if stock_walmart < 0:
                    tock_walmart = 0

                stock_claroshop =  int(quantity + int(stock_exclusivas) + int(stock_urrea))
                if stock_claroshop < 0:
                    tock_walmart = 0

                existencias.write(seller_sku+','+str(stock_amazon)+','+str(stock_linio)+','+str(stock_prestashop)+','+str(stock_claroshop)+','+str(stock_mercadolibre)+'\n' )
                #print(str(i)+','+seller_sku+','+str(stock_amazon)+','+str(stock_linio)+','+str(stock_prestashop)+','+str(stock_claroshop)+','+str(stock_mercadolibre) )

            #return lista_productos_odoo_12
        except Exception as e:
            print('Error en productos_en_odoo12 : '+str(e))
            return False



api = RestAPI()
api.authenticate()
#existencias = open("PLANTILLA_FTP.CSV", "w")
if __name__ == '__main__':
    sku='MCC11-MEN'
    get_stock_real_by_sku(sku)

    '''
    try:
        
        i=1
        archivo=open('productos_odoo.csv', 'r')
        for producto in archivo:
            sku = producto[:-1]
            api.productos_en_odoo12(sku,i)
            i=i+1
        existencias.close()
    except Exception as e:
        print('Error: '+str(e))
    '''
    

