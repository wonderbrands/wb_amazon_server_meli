# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import Warning 
from datetime import datetime
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

def get_stock_quant_ids(product_id):
    try:
        data = {
            'model': "product.product",
            'domain': json.dumps([['id', '=', product_id]]),
            'fields': json.dumps(['id','default_code','name', 'list_price','stock_move_ids','stock_quant_ids',"stock_exclusivas", "stock_urrea", 'virtual_available' ]),
        }
        response = api.execute('/api/search_read', data=data)
        stock_quant_ids = response[0]['stock_quant_ids']
        default_code = response[0]['default_code']
        list_price = response[0]['list_price']
        stock_exclusivas = response[0]['stock_exclusivas']
        stock_urrea = response[0]['stock_urrea']
        virtual_available =response[0]['virtual_available']

        return dict(stock_quant_ids=stock_quant_ids, default_code=default_code, list_price=list_price, stock_exclusivas=stock_exclusivas, stock_urrea=stock_urrea, virtual_available=virtual_available )
    except Exception as e:
        app.logger.error('ODOO|'+'get_stock_quant_ids()|'+ str(e) )
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
        location_id =response[0]['location_id']
        quantity=response[0]['quantity']    
        reserved_quantity =response[0] ['reserved_quantity']
        return dict(location_id=location_id, quantity=quantity, reserved_quantity=reserved_quantity)
    except Exception as e:
        app.logger.error('ODOO|'+'get_stock_quant()|'+ str(e) )
        api.authenticate()
        return False

#url_sr ='https://somosreyes.odoo.com'
url_sr ='https://somosreyes-test-590581.dev.odoo.com'
client_id_sr ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret_sr ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'
class RestAPI:
    def __init__(self):
        self.url = url_sr
        self.client_id = client_id_sr
        self.client_secret = client_secret_sr
        self.client = BackendApplicationClient(client_id=self.client_id)
        self.oauth = OAuth2Session(client=self.client)

    def route(self, url):
        if url.startswith('/'):
            url = "%s%s" % (self.url, url)
        return url

    def authenticate(self):
        try:
            self.oauth.fetch_token(
            token_url=self.route('/api/authentication/oauth2/token'),
            client_id=self.client_id, client_secret=self.client_secret
            )
            #print(self.oauth.fetch_token(token_url=self.route('/api/authentication/oauth2/token'),client_id=self.client_id, client_secret=self.client_secret) )
        except Exception as e:
            raise e
        

    def execute(self, enpoint, type="GET", data={}):
        try:
            if type == "POST":
                response = self.oauth.post(self.route(enpoint), data=data)
            elif type == "PUT":
                response = self.oauth.put(self.route(enpoint), data=data)
            else:
                response = self.oauth.get(self.route(enpoint), data=data)
                #print 'RESPONSE', response
            if response.status_code != 200:
                api.authenticate()
                raise Exception(pprint(response.json()))
            else:
                #print response.json()
                return response.json()

        except Exception as e:
            print ('Error al realizar el request en: Execute()'+str(e) )
            return False
        
api = RestAPI()
api.authenticate()

class product_stock(models.Model):
    _inherit = 'product.template'
    stock_real = fields.Integer(string="Stock Real", compute='_total')
    stock_exclusivas = fields.Integer(string="Stock Exclusivas")
    stock_urrea = fields.Integer(string="Stock Urrea")
    stock_markets = fields.Integer(string="Stock Markets")

    stock_mercadolibre = fields.Integer(string="Stock mercado Libre", compute='_total')
    stock_linio = fields.Integer(string="Stock Linio", compute='_total')
    stock_amazon = fields.Integer(string="Stock Amazon", compute='_total')

    ubicacion_pasillo = fields.Char(string="Pasillo")
    ubicacion_nivel = fields.Char(string="Nivel")
    ubicacion_pared = fields.Char(string="Pared")

    ubicacion_caja = fields.Char(string="Caja")

    status_producto = fields.Boolean(string="Baja/Descontinuado")
    precio_con_iva = fields.Monetary(string="Precio con IVA", compute = '_precio_con_iva')
    costo_dolares = fields.Monetary(string="Costo en USD")
    costo_anterior = fields.Monetary(string="Costo anterior")

    txt_filename =  fields.Char()
    txt_binary =  fields.Binary("Etiqueta ZPL")

    @api.multi
    def imprimir_zpl(self):
        ahora = datetime.now()
        fecha = ahora.strftime("%Y-%m-%d %H:%M:%S")

        dato=self
        content=''
        
        for record in self:           
            content+='^XA' +'\n'
            content+='^CFA,40' +'\n'
            content+='^FO15,60^FD'+ str(record.default_code)+'^FS'+'\n'
            content+='^CFA,30' +'\n'          
            content+='^FO15,100^FD'+ str(record.name)+'^FS'+'\n'
            content+='^FO15,140^FD'+ "PASILLO:"+ str(record.ubicacion_pasillo) +"NIVEL:" + str(record.ubicacion_nivel) +"PARED:"+ str(record.ubicacion_pared) +"CAJA:"+ str(record.ubicacion_caja) +'^FS'+'\n'
            content+='^FO15,180^FD'+ str(fecha)+'^FS'+'\n'
            content+='^BY4,3,100'+'\n'
            content+='^FO45,240^BC^FD'+str(record.barcode)+'^FS'+'\n'
            content+='^Xz'
        
        #raise Warning("Etiqueta ZPL creada")
        return self.write({
            'txt_filename': str(record.default_code)+'.zpl',
            'txt_binary': base64.encodestring(content.encode('utf-8'))
        })
   

    @api.multi
    @api.depends('stock_exclusivas', 'stock_urrea')
    def _total(self):
        _logger = logging.getLogger(__name__)
        data_stock_quant_ids = get_stock_quant_ids(product_id)
        stock_quant_ids = data_stock_quant_ids ['stock_quant_ids']
        pronosticado=0

        if stock_quant_ids:
            for id in stock_quant_ids:  
                stock_quant = get_stock_quant(id)
                location_id =stock_quant['location_id']
                quantity=stock_quant['quantity']    
                reserved_quantity = stock_quant['reserved_quantity']
                if location_id[1] == 'AG/Stock':
                    print ('ODOO|',default_code, location_id, quantity, reserved_quantity)
                    _logger.info(' ODOO|sku: %s location_id: %s quantity: %s reserved_quantity: %s', str(default_code), str(location_id),str(quantity), str(reserved_quantity) )
                    pronosticado=int(stock_quant['quantity'] ) - int(stock_quant['reserved_quantity'])

         _logger.info('ODOO| Stock Real: %s', str(pronosticado)) 
        
            self.stock_real = pronosticado
        else:
            self.stock_real = pronosticado
        return True

    @api.one
    @api.depends('list_price')
    def _precio_con_iva(self):
        if self.list_price: 
            self.precio_con_iva = round(float(self.list_price)*1.16, 2)
        else:
            self.precio_con_iva=0.00


        _logger = logging.getLogger(__name__)
        stock_quant_ids = self.env['product.product'].search([['default_code', '=', self.default_code]]).stock_quant_ids
        _logger.info('stock_quant_ids: %s', str(stock_quant_ids) )
        stock_real = 0
        for id_product in stock_quant_ids:          
            location_id = self.env['stock.quant'].search([['id', '=', id_product]]).location_id
            _logger.info('location_id: %s', str(location_id) )
            quantity= self.env['stock.quant'].search([['id', '=', id_product]]).quantity
            reserved_quantity = self.env['stock.quant'].search([['id', '=', id_product]]).reserved_quantity
            if location_id[1] == 'AG/Stock':
               stock_real = int(stock_quant['quantity'] ) - int(stock_quant['reserved_quantity'])

=========================


        product_id = self.env['product.product'].search([['default_code', '=', self.default_code]]).id
        product = self.env['product.product'].browse(product_id)
        #available_qty = product.with_context({'warehouse' : WAREHOUSE_ID}).qty_available
        available_qty = product.with_context({'location' : 12 }).qty_available
        self.stock_real = available_qty
        