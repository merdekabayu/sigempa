from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
from dateutil import tz
import requests
from subprocess import run
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
mysql = MySQL(app)

def infogempa(var):
    cur = mysql.connection.cursor()

    id = var
    cur = mysql.connection.cursor()
    sql = f"SELECT * FROM db_gempa WHERE `Event ID`='{id}'"
    param = cur.execute(sql)
    par = cur.fetchall()
    par = par[0]
    date,time,lat,long,depth,mag,ket,info = par[1],par[2],par[3],par[4],par[5],par[6],par[7],par[8]
    date = date.strftime('%Y-%m-%d')
    #time = time.strftime('%H:%M:%S')

    print(date)
    
    timeutc = date + ' ' + str(time)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(timeutc[0:19], '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    ot = utc.astimezone(to_zone)
    tgl = ot.strftime("%d")
    bulan = ot.strftime("%b")
    tahun = ot.strftime("%y")
    waktu = ot.strftime("%X")
    bujur = ('%.2f') % float(long)
    depth = ('%.0f') % float(depth)
    if float(lat) > 0:
        NS = "LU"
        ltg = ('%.2f') % float(lat)
    else:
        NS = "LS"
        ltg = ('%.2f') % abs(float(lat))
    mag = ('%.1f') % float(mag)
    keterangan = ket.split()
    min_jarak = keterangan[0]
    arah = keterangan[2]
    minkota = keterangan[3]

    if len(info) > 3:
        param = ('Info Gempa Mag:' + mag + ', ' + tgl + '-' + bulan + '-' + tahun + ' ' + waktu +
                ' WIT, Lok: ' + ltg + ' ' + NS + ', ' + bujur + ' BT (' + min_jarak + ' km ' +
                arah +' '+ minkota + '), Kedlmn:' + depth + ' Km, '+info+' ::BMKG-TNT')
    else:
        param = ('Info Gempa Mag:' + mag + ', ' + tgl + '-' + bulan + '-' + tahun + ' ' + waktu +
                ' WIT, Lok: ' + ltg + ' ' + NS + ', ' + bujur + ' BT (' + min_jarak + ' km ' +
                arah +' '+ minkota + '), Kedlmn:' + depth + ' Km ::BMKG-TNT')
    return param
    
    

