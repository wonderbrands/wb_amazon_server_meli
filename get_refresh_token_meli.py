import requests
import json

def recupera_meli_refresh_token(user_id):
    try:
        print('User Id: ', user_id)
        token_dir=''
        if user_id ==25523702:# Usuario de SOMOS REYES VENTAS
            token_dir='/home/ubuntu/meli/tokens_meli.txt'
        elif user_id ==160190870:# Usuario de SOMOS REYES OFICIALES
            token_dir='/home/ubuntu/meli/tokens_meli_oficiales.txt'

        archivo_tokens=open(token_dir, 'r')
        tokens=archivo_tokens.read().replace("'", '"')
        tokens_meli = json.loads(tokens)
        print (tokens_meli)
        archivo_tokens.close()
        refresh_token=tokens_meli['refresh_token']
        return refresh_token
    except Exception as e:
        print ('Error recupera_meli_refresh_token : '+str(e))
        return False

def obtener_token_meli_whith_refresh_token(refresh_token):
    try:
        headers = {
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        }   

        client_id='5703097592380294'
        client_secret='Fn5yHq1e1DBgy2EiRk7rLhsyRexcZYAQ'
        url=' https://api.mercadolibre.com/oauth/token?grant_type=refresh_token&client_id='+str(client_id)+'&client_secret='+str(client_secret)+'&refresh_token='+refresh_token
        r=requests.post(url, headers=headers)
        #archivo_tokens.write( str(r.json()) )
        #archivo_tokens.close()
        print (r.json())
        
        return True
    except Exception as e:
        print (str(e))
        return False

if __name__ == '__main__':
    user_id = 25523702
    #refresh_token = recupera_meli_refresh_token(user_id)
    #print (refresh_token)
    #tokens =obtener_token_meli_whith_refresh_token(refresh_token)
    #print (tokens)
