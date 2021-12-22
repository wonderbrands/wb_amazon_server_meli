import sys
import json
from flask import Flask, request, abort

app = Flask(__name__)


@app.route('/odoo_notify', methods=['POST'])
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

        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            } 
        body=[{"sku": sku,"quantity": int(quantity)}]
        print (body)

        r=requests.post(url, headers=headers, data=body)
        print (r.json() )


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