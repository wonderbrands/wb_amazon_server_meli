import sys
import json
import requests
from flask import Flask, request, abort

app = Flask(__name__)

def get_token_venti():
    try:
        token_file=open("/home/ubuntu/meli/token_venti.json")
        token_data=token_file.read()
        return token_data
    except Exception as e:
        print ("Error en get_token_venti(): ", str(e) )
        return None

@app.route('/', methods=['POST'])
def webhook():
    print("Estas viendo el webhook"); sys.stdout.flush()
    if request.method == 'POST':
        print(request.form)
        json_value = json.dumps(request.form, separators=(',',':'))
        print (json_value)
        datos = json.loads(json_value)
        print (datos)
        payload=json.loads(datos['records'])
        sku = payload[0]['default_code']
        quantity = payload[0]['qty_available']
        price = payload[0]['list_price']

        print (sku, quantity, price)
        json_data={"sku":None, "quantity":None, "price":None}
        json_data["sku"]=sku
        json_data["quantity"]=int(quantity)
        json_data["price"]=price
        print (json_data)
        token_venti=get_token_venti()
        #headers = {"accept": "application/json", "content-type":"application/json","authorization": "Bearer " + token_venti} 
        headers={'Authorization': 'Bearer '+ token_venti}

        body=[{"sku": sku,"quantity": int(quantity)}]

        print(headers)
        print (body)

        url='https://ventiapi.azurewebsites.net/api/Stock/UpdateStock'
        #url='https://postb.in/1559682678012-8114686773624'
        r=requests.post(url, headers=headers, data=body)
        print(r.request.body)
        print(r.request.headers)
        print (r.text )
        print (r.headers)


        #fields = [k for k in request.form]  
        #print (fields)
        #values = [request.form[k] for k in request.form]
        #print (values)
        #data = dict(zip(fields, values))
        #print(data)
        #print(request.form['records'])
        #for data in request.form.items():
        #    print (data)



        return '', 200
    else:
        abort(400)

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=8081)