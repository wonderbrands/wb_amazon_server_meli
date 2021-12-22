#!/usr/bin/python
import mysql.connector as mariadb
# sudo mysql -u root -p 
# DROP TABLE notify_meli;
def crea_tabla_notify_meli():
	mariadb_connection = mariadb.connect(user='moises', password='ttgo702', database='meli')
	cursor = mariadb_connection.cursor()
	sql = '''
	CREATE TABLE notify_meli (
		id BIGINT NOT NULL AUTO_INCREMENT,
		car_id VARCHAR(20) NOT NULL, 
		order_id VARCHAR(20) NOT NULL, 
		status_order VARCHAR(30),
		application_id VARCHAR(25),
		user_id VARCHAR(25),
		topic VARCHAR(20),
		attempts int,

		carrier VARCHAR(50),
		tracking_number VARCHAR(50),
		tracking_id VARCHAR(30),
		shipment_status VARCHAR(30),
		respuesta_odoo VARCHAR(255),
		
		market_place_fee DECIMAL(8,2), 
		shipping_cost DECIMAL(8,2),
		total_paid_amount DECIMAL(10,2),
		transaction_amount DECIMAL(10,2),
		status_detail VARCHAR(30),
		
		products_sku VARCHAR(150),
		products_mlm VARCHAR(150),
		products_ids VARCHAR(150),

		sent VARCHAR(30),
		received VARCHAR(30),
		saved DATETIME(6),
		resolved VARCHAR(30),
		procesada  BOOLEAN, 
		CONSTRAINT UC_order_meli UNIQUE (order_id),
		PRIMARY KEY (id)
		)
		'''
	cursor.execute(sql)
	print "Se ha creado la tabla de notificaciones."

if __name__ == '__main__':
	crea_tabla_notify_meli()