#!/usr/bin/python
import mysql.connector #as mariadb
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector import pooling
import imaplib, re
import email
import smtplib 
from email.mime.text import MIMEText

def envia_email(mensaje_error):
	try:
		# Establecemos conexion con el servidor smtp de gmail
		mailServer = smtplib.SMTP('mail.somos-reyes.com',26)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login("serverubuntu@somos-reyes.com","Ttgo702#")
		# Construimos el mensaje simple

		#mensaje= str(plantilla_1() ) +str (plantilla_2() )+ str( plantilla_3() )
		mensaje_enviar=mensaje_error
		mensaje = MIMEText(mensaje_enviar,"html", _charset="utf-8" )
		mensaje['From']="serverubuntu@somos-reyes.com"
		mensaje['To']= "moisantgar@gmail.com,sistemas@somos-reyes.com,lcheskin@gmail.com"
		mensaje['Subject']="ERROR | No se ha establecido la Conexion a la BD Meli AWS. Revise el aviso."
		# Envio del mensaje
		mailServer.sendmail(mensaje['From'], mensaje["To"].split(",") ,  mensaje.as_string())
		print ("Se ha enviado un correo de aviso a Leon y Moi. " )
		# Cierre de la conexion
		mailServer.close()
	except Exception as e:
		print ("No se pudo enviar el email de aviso! -> "+ str(e) )


def connect_to_orders():
	try:
		connection_pool = mysql.connector.pooling.MySQLConnectionPool(  pool_name="meli_pool",
																		pool_size=10,
																		pool_reset_session=True,
																		host='localhost',
																		database='meli',
																		user='moises',
																		password='ttgo702')
		connection_object = connection_pool.get_connection()

		if connection_object.is_connected():
			db_Info = connection_object.get_server_info()
			#print("Conectado a MariaDB - MySQL Usando un Pool de conexion... MariaDb - MySQL Server: ",db_Info)
			cursor = connection_object.cursor()
		return dict(cursor=cursor, connection_object=connection_object)

	except Exception as e:
		mensaje_error = ' <h2>No se ha podido establecer la conexion a la Base de Datos de meli.<h2><br>'
		mensaje_error += '<b>Motivo:</b> '+str(e)+'<br>'
		mensaje_error += 'Entre a la consola del servidor y digite: <br> sudo /etc/init.d/mysql restart <br>'
		envia_email(mensaje_error)
		print (mensaje_error + str(e) )
	

if __name__ == '__main__':
	connect_to_orders()