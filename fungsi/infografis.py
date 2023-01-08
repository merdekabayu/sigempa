from subprocess import run
from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from dateutil import tz
from shapely.geometry import Point, Polygon
from .statistik import hitung_wilayah, hitung_chart
from .filter import filter_area
from .mapping import map_seismisitas_mingguan

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
mysql = MySQL(app)


def infografis(start,end):
    
    yest = end
    hari=((end-start).days)+1
    seminggu = start.strftime('%Y-%m-%d')
    cur = mysql.connection.cursor()
    sql_filter = "SELECT * FROM db_gempa WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date` ASC, `Origin Time` ASC"
    condition = (seminggu, yest)
    cur.execute(sql_filter, condition)
    par = cur.fetchall()
    date_list = [yest - timedelta(days=x) for x in range(hari)]
    date_list.sort()

    par = filter_area(par)
    chart = hitung_chart(par,date_list)
    wilayah = hitung_wilayah(par)
    print('Ini Jml gempa = ',chart[0])
    print('Ini Gb dirasakan = ',chart[1])
    print('Ini hist harian = ',chart[2])
    print('Ini stat Mag = ',chart[3])
    print('Ini stat Depth = ',chart[4])
    print('Ini dist mag = ',chart[5])
    print('Ini hist wilayah = ',wilayah)
    grafik = [chart,wilayah]
    
    smg = (start).strftime('%d-%B-%Y')
    yday = yest.strftime('%d-%B-%Y')

    start = (start).strftime('%d-%b-%y')
    end = yest.strftime('%d-%b-%y')

    map_seismisitas_mingguan(par,start,end)
    
    rangedate = [smg,yday]


    return par,grafik,rangedate

def infografis_parfilter(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt):
    

    tgl1 = datetime.strptime(date1, '%d-%m-%Y %H:%M')
    tgl2 = datetime.strptime(date2, '%d-%m-%Y %H:%M')
    cur = mysql.connection.cursor()
    sql_filter = "SELECT * FROM db_gempa WHERE CONCAT(`Origin Date`,' ',`Origin Time`) BETWEEN %s AND %s AND `Latitude` BETWEEN %s AND %s AND `Longitude` BETWEEN %s AND %s AND `Depth` BETWEEN %s AND %s AND `Magnitude` BETWEEN %s AND %s ORDER BY `Origin Date` AND `Origin Time` ASC "
    condition = (tgl1,tgl2,lat2,lat1,long1,long2,depth1,depth2,mag1,mag2)
    cur.execute(sql_filter, condition)
    param = cur.fetchall()
    par=[]
    if felt == 1:
        for row in param:
            if len(str(row[8])) > 5:
                par += [row]
    else:
        par = param
        
    print('iniiiiii parrrrrr ##########',par)
    
    yest = tgl2
    hari=((tgl2-tgl1).days)+1
    date_list = [yest - timedelta(days=x) for x in range(hari)]
    date_list.sort()

    par = filter_area(par)
    chart = hitung_chart(par,date_list)
    wilayah = hitung_wilayah(par)
    print('Ini Jml gempa = ',chart[0])
    print('Ini Gb dirasakan = ',chart[1])
    print('Ini hist harian = ',chart[2])
    print('Ini stat Mag = ',chart[3])
    print('Ini stat Depth = ',chart[4])
    print('Ini dist mag = ',chart[5])
    print('Ini hist wilayah = ',wilayah)
    grafik = [chart,wilayah]
    
    smg = (tgl1).strftime('%d-%B-%Y')
    yday = yest.strftime('%d-%B-%Y')

    start = (tgl1).strftime('%d-%b-%y')
    end = yest.strftime('%d-%b-%y')

    map_seismisitas_mingguan(par,start,end)
    
    rangedate = [smg,yday]


    return par,grafik,rangedate

