from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
from dateutil import tz
import requests
from subprocess import run

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
mysql = MySQL(app)


def filter_parameter(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2):
    
    tgl1 = datetime.strptime(date1, '%d-%m-%Y %H:%M')
    tgl2 = datetime.strptime(date2, '%d-%m-%Y %H:%M')

    cur = mysql.connection.cursor()
    sql_filter = "SELECT * FROM db_gempa WHERE CONCAT(`Origin Date`,' ',`Origin Time`) BETWEEN %s AND %s AND `Latitude` BETWEEN %s AND %s AND `Longitude` BETWEEN %s AND %s AND `Depth` BETWEEN %s AND %s AND `Magnitude` BETWEEN %s AND %s ORDER BY 2 ASC, 3 ASC "
    condition = (tgl1,tgl2,lat2,lat1,long1,long2,depth1,depth2,mag1,mag2)
    print(condition)
    cur.execute(sql_filter, condition)
    print(cur)
    parameter = cur.fetchall()
    for x in parameter:
        print(x)

    return parameter

def filter():
    cur = mysql.connection.cursor()
    date = request.form['datefilter']
    with open("fungsi/filter.txt", "w") as file:
            file.write(date)
            file.close
    #2022-11-16 - 2022-11-16
    datestart = date.split()[0]
    dateend = date.split()[2]
    sql_filter = "SELECT * FROM db_gempa WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
    condition = (datestart,dateend)
    cur.execute(sql_filter, condition)
    tabel = cur.fetchall()
    print(tabel)
    
    return tabel

def filter_ekin():
    cur = mysql.connection.cursor()
    date = request.form['datefilter']
    #2022-11-16 - 2022-11-16
    datestart = date.split()[0]
    dateend = date.split()[2]
    sql_filter = "SELECT * FROM db_ekin WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
    condition = (datestart,dateend)
    cur.execute(sql_filter, condition)
    tabel = cur.fetchall()
    # print(tabel)
    
    return tabel

def filter_tabelpga():
    cur = mysql.connection.cursor()
    date = request.form['datefilter']
    with open("fungsi/filter.txt", "w") as file:
            file.write(date)
            file.close
    #2022-11-16 - 2022-11-16
    datestart = date.split()[0]
    dateend = date.split()[2]
    sql_filter = "SELECT * FROM db_gempa WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
    condition = (datestart,dateend)
    cur.execute(sql_filter, condition)
    tabel = cur.fetchall()
    print(tabel)
    
    return tabel

def filter_edit():
    cur = mysql.connection.cursor()
    with open('fungsi/filter.txt') as f:
        date = f.readlines()
    print(date)
    datestart = date[0].split()[0]
    dateend = date[0].split()[2]
    print(datestart,dateend)
    sql_filter = "SELECT * FROM db_gempa WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
    condition = (datestart,dateend)
    cur.execute(sql_filter, condition)
    tabel = cur.fetchall()
    
    return tabel

def filter_area(par):
    f_par = []
    for row in par:
        lat=row[3]
        long=row[4]
        if lat <= 3.5 and lat >= -2.75 and long <= 130 and long >= 124 :
            f_par += [row]
    return f_par

        

    
    

