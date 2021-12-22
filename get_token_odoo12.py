import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import LegacyApplicationClient


'''
url ='https://somosreyes.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

'''
url ='https://somosreyes-test-348102.dev.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

def get_token_odoo():
	try:
		token_dir='/home/ubuntu/meli/token_odoo12.txt'
		archivo_tokens=open(token_dir, 'w')

		client = BackendApplicationClient(client_id=client_id)
		oauth = OAuth2Session(client=client)
		token = oauth.fetch_token(token_url=url+'/api/authentication/oauth2/token', client_id=client_id,
		        client_secret=client_secret)

		archivo_tokens.write( str(token) )
		archivo_tokens.close()
		access_token=token['access_token']

		print (access_token)
	except Exception as e:
		print('Error Token Odoo: '+str(e))




def consulta_users(usuario,  access_token):
		try:
			headers = {
			'authorization': access_token, 
			}

			data = {
			"model":"res.users",
			"domain":json.dumps([["name","=", usuario]]),
			"fields":json.dumps(["name"]),
			}
			#response =api.execute("/api/search_read", data=data)
			url_odoo=url+'/api/search_read'
			r=requests.get(url_odoo, headers=headers, data=data)
			print (r.json() )

		except Exception as e:
			print('consulta_users : '+str(e))
			return 1

access_token = get_token_odoo()
usuario='APIsionate Meli'
consulta_users(usuario, access_token)

import requests
from requests.auth import AuthBase

class TokenAuth(AuthBase):
    """Implements a custom authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """Attach an API token to a custom auth header."""
        r.headers['X-TokenAuth'] = f'{self.token}'  # Python 3.6+
        return r


usuario='APIsionate Meli'
data = {
"model":"res.users",
"domain":json.dumps([["name","=", usuario]]),
"fields":json.dumps(["name"]),
}
respuesta = requests.get('https://somosreyes-test-348102.dev.odoo.com/api/search_read',data=data,  auth=TokenAuth(access_token))
print (respuesta)

