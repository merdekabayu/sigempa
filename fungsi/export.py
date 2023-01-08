from subprocess import run
from flask import Flask, render_template, request, redirect,send_file
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from dateutil import tz
from .statistik import hitung_wilayah, hitung_chart
from .filter import filter_area
from .mapping import map_seismisitas_mingguan
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
mysql = MySQL(app)


def export(par,chart,wilayah,path):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM db_gempa")
    
    with open(path, 'w') as f:
        f.write("HISTOGRAM GEMPABMI" + '\n')
        header = ("Tanggal", "Jumlah")
        f.write(','.join(header) + '\n')
        i = 0
        while i < len(chart[2][0]):
            day = chart[2][0][i]
            hist = chart[2][1][i]
            isi = (day,str(hist))
            f.write(','.join(isi) + '\n')
            i+=1
        f.write("TOTAL," + chart[0]+","+'\n')
        f.write("TOTAL DIRASAKAN," + str(chart[1]) + "," + '\n')
        f.write('\n')
        f.write("BERDASARKAN MAGNITUDO" + '\n')
        m3prs=float(chart[3][0])/float(chart[0])
        m35prs=float(chart[3][1])/float(chart[0])
        m5prs=float(chart[3][2])/float(chart[0])
        M3prs="{: .1%}".format(m3prs)
        M35prs="{: .1%}".format(m35prs)
        M5prs="{: .1%}".format(m5prs)
        f.write("M < 3," + str(chart[3][0]) + ","+ M3prs+"," + '\n')
        f.write("3 < M < 5," + str(chart[3][1]) + ","+ M35prs+"," + '\n')
        f.write("M > 5," + str(chart[3][2]) + ","+ M5prs+"," + '\n')
        f.write('\n')
        f.write("BERDASARKAN KEDALAMAN" + '\n')
        m3prs=float(chart[4][0])/float(chart[0])
        m35prs=float(chart[4][1])/float(chart[0])
        m5prs=float(chart[4][2])/float(chart[0])
        M3prs="{: .1%}".format(m3prs)
        M35prs="{: .1%}".format(m35prs)
        M5prs="{: .1%}".format(m5prs)
        f.write("< 60 Km," + str(chart[4][0]) + ","+ M3prs+"," + '\n')
        f.write("60 - 300 Km," + str(chart[4][1]) + ","+ M35prs+"," + '\n')
        f.write("> 300 Km," + str(chart[4][2]) + ","+ M5prs+"," + '\n')
        f.write('\n')
        f.write("BERDASARKAN WILAYAH" + '\n')
        f.write("LAUT MALUKU,"+str(wilayah[0])+'\n')
        f.write("HALMAHERA BAG. UTARA,"+str(wilayah[1])+'\n')
        f.write("HALMAHERA BAG. TIMUR,"+str(wilayah[2])+'\n')
        f.write("HALMAHERA BAG. BARAT,"+str(wilayah[3])+'\n')
        f.write("HALMAHERA BAG. SELATAN,"+str(wilayah[4])+'\n')
        f.write("KEP. SULA & TALIABU,"+str(wilayah[5])+'\n')
        f.write("SULAWESI,"+str(wilayah[6])+'\n')
        f.write('\n')

        header = [par[0] for par in cur.description]
        f.write(','.join(header) + '\n')
        for row in par:
            f.write(','.join(str(r) for r in row) + '\n')
        f.write('\n')
        
    f.close()
    
    
    
    
    return 'done'

