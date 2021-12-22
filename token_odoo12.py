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
username='moises.santiago@somos-reyes.com'
password='S0l0!vida9cita'

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(token_url=url+'/api/authentication/oauth2/token', client_id=client_id,
        client_secret=client_secret)

print (token)
