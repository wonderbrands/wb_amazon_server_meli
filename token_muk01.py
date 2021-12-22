import json
import requests
from pprint import pprint
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

'''
url ='https://somosreyes.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'

'''

url ='https://somosreyes-test-348102.dev.odoo.com'
client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'
username='moises.santiago@somos-reyes.com'
password='12345'

client_id ='B38ULenQ5Wo9YHVpCNPwLYU06o0dif'
client_secret ='PDzW1J08BJB0JB3UXh0TlQkiPOm3pU'
token_url = 'https://somosreyes-test-348102.dev.odoo.com/api/authentication/oauth2/token'

username='moises.santiago@somos-reyes.com'
password='12345'
scope = ['all']

oauth = OAuth2Session(
    client=LegacyApplicationClient(client_id=client_id)
)

token = oauth.fetch_token(
    token_url=token_url, 
    username=username, password=password,
    client_id=client_id, client_secret=client_secret
)

print (token)

#print(oauth.get("https://somosreyes-test-348102.dev.odoo.com/api/user").json())