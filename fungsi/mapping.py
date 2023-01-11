from subprocess import run
from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime
from dateutil import tz
import numpy as np
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
mysql = MySQL(app)


def map_seismisitas_mingguan(par,start,end):
    f1 = open("fungsi/gmt/gempa_mingguan.txt", "w")
    f2 = open("fungsi/gmt/dirasakan_mingguan.txt", "w")
    for coord in par:
        if len(coord[8]) < 5:
            x = str(coord[4])
            y = str(coord[3])
            z = str(coord[5])
            mag = str(coord[6])
            f1.write(x+" "+y+" "+z+" "+mag+"\n")
        else:
            x = str(coord[4])
            y = str(coord[3])
            z = str(coord[5])
            mag = str(coord[6])
            f2.write(x+" "+y+" "+z+" "+mag+"\n")
    f1.close()
    f2.close()
    
    run("fungsi/gmt/seismisitas.sh "+start+" "+end, shell=True)
    

    


def map_diseminasi():
    fileinput = 'fungsi/gmt/episenter.dat'
    file = open(fileinput, 'r')
    baris = file.readlines()
    lat = baris[0].split()[0]
    long = baris[0].split()[1]
    mag = baris[0].split()[3]
    mags = np.arange(1,9.1,0.1)
    indexmag = np.where(np.round(mags,2) == float(mag))
    magf = indexmag[0][0]+1
    magfile = str(magf)+'.png'
    #magfile = 'mag'+('%.0f')%(float(mag)*10)+'.png'
    opsi_map = request.form['opsi_map']
    

    if opsi_map=="Regional":
        kiri=('%.2f')%(float(long)-3)
        kanan=('%.2f')%(float(long)+3)
        bawah=('%.2f')%(float(lat)-1.875)
        atas=('%.2f')%(float(lat)+1.875)
        skala =('%.2f')%(float(long)+1.8)+'/'+('%.2f')%(float(lat)-1.6)
        variabel = lat+" "+long+" "+magfile+" "+skala+" "+kiri+" "+kanan+" "+bawah+" "+atas
        run("fungsi/gmt/peta-epic_regional.sh "+variabel, shell=True)
        #os.system("C:\Windows\System32\cmd.exe /c gmt\peta-epic_regional_new.bat" + " " + lat + " " + long+ " " + magfile)
    elif opsi_map=="Lokal":
        #set lebar=1.5
        #set tinggi=0.9375
        kiri=('%.2f')%(float(long)-1.5)
        kanan=('%.2f')%(float(long)+1.5)
        bawah=('%.2f')%(float(lat)-0.9375)
        atas=('%.2f')%(float(lat)+0.9375)
        skala =('%.2f')%(float(long)+1.0)+'/'+('%.2f')%(float(lat)-0.8)
        variabel = lat+" "+long+" "+magfile+" "+skala+" "+kiri+" "+kanan+" "+bawah+" "+atas
        run("fungsi/gmt/peta-epic_lokal.sh "+variabel, shell=True)
        #os.system("C:\Windows\System32\cmd.exe /c gmt\peta-epic_lokal_new.bat" + " " + lat + " " + long+ " " + magfile)
    else:
        #set lebar=0.8
        #set tinggi=0.5
        kiri=('%.2f')%(float(long)-0.8)
        kanan=('%.2f')%(float(long)+0.8)
        bawah=('%.2f')%(float(lat)-0.5)
        atas=('%.2f')%(float(lat)+0.5)
        skala =('%.2f')%(float(long)+0.6)+'/'+('%.2f')%(float(lat)-0.4)
        variabel = lat+" "+long+" "+magfile+" "+skala+" "+kiri+" "+kanan+" "+bawah+" "+atas
        run("flask_app/fungsi/gmt/peta-epic_lokal1.sh "+variabel, shell=True)
        
        #os.system("C:\Windows\System32\cmd.exe /c gmt\peta-epic_lokal1_new.bat" + " " + lat + " " + long+ " " + magfile)
    
    #a=subprocess.call("pwd")
    #return redirect(request.referrer)

def map_detail(var):
    id = var
    cur = mysql.connection.cursor()
    sql = f"SELECT * FROM db_gempa WHERE `Event ID`='{id}'"
    param = cur.execute(sql)
    par = cur.fetchall()
    par = par[0]
    date,time,lat,long,depth,mag,ket,info = par[1],par[2],par[3],par[4],par[5],par[6],par[7],par[8]
    date = date.strftime('%Y-%m-%d')
    #time = time.strftime('%H:%M:%S')

    print('sampe siniii ######',id)
    
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

    long = ('%.2f') % float(long)
    if float(lat) > 0:
        NS = "LU"
        ltg = ('%.2f') % float(lat)
    else:
        NS = "LS"
        ltg = ('%.2f') % abs(float(lat))
    mag = ('%.1f') % float(mag)

    if bulan=="Jan":
        bulan1 = "Januari"
    elif bulan=="Feb":
        bulan1 = "Februari"
    elif bulan=="Mar":
        bulan1 = "Maret"
    elif bulan=="Apr":
        bulan1 = "April"
    elif bulan=="May":
        bulan1 = "Mei"
    elif bulan=="Jun":
        bulan1 = "Juni"
    elif bulan=="Jul":
        bulan1 = "Juli"
    elif bulan=="Aug":
        bulan1 = "Agustus"
    elif bulan=="Sep":
        bulan1 = "September"
    elif bulan=="Oct":
        bulan1 = "Oktober"
    elif bulan=="Nov":
        bulan1 = "November"
    else:
        bulan1 = "Desember"

    keterangan = ket.split()
    min_jarak = keterangan[0]
    arah = keterangan[2]
    minkota = keterangan[3]
    bujur = ('%.2f')%(float(long))
    depth = ('%.0f')%(float(depth))

    fileoutput2 = 'fungsi/gmt/param.txt'
    fileoutput3 = 'fungsi/gmt/jarak.txt'
    file2 = open(fileoutput2, 'w')
    file3 = open(fileoutput3, 'w')
    file2.write(tgl + ' ' + bulan1 + ' 20' + tahun + ' ' + waktu + ' WIT ' + ltg + ' '+ NS + ' - '
                +bujur + ' BT ' + depth + ' Km ' + minkota)
    file3.write(min_jarak + ' Km ' + arah)
    file2.close()
    file3.close()

    magfile = 'mag'+('%.0f')%(float(mag)*10)+'.png'

    kiri=('%.2f')%(float(long)-3)
    kanan=('%.2f')%(float(long)+3)
    bawah=('%.2f')%(float(lat)-1.875)
    atas=('%.2f')%(float(lat)+1.875)
    skala =('%.2f')%(float(long)+1.8)+'/'+('%.2f')%(float(lat)-1.6)
    variabel = ('%.2f')%(float(lat))+" "+('%.2f')%(float(long))+" "+magfile+" "+skala+" "+kiri+" "+kanan+" "+bawah+" "+atas+" "+id
    run("fungsi/gmt/peta-epic_regional-detail.sh "+variabel, shell=True)

    print(date,time,lat,long,depth,mag,ket,info)

    cur.close()
    return par