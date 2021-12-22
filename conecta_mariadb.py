#!/usr/bin/python
import mysql.connector as mariadb

mariadb_connection = mariadb.connect(user='moises', password='ttgo702', database='meli')
cursor = mariadb_connection.cursor()
print cursor