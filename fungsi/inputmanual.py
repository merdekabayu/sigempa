from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import tz
import math as m
import requests
from subprocess import run
import os
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
app.config["UPLOAD_FOLDER"] = "static/shakemap/"
mysql = MySQL(app)

def inputmanual():
    cur = mysql.connection.cursor()

    opsi_par = request.form['parameter']
    id = request.form['id']
    date = request.form['ot_date']
    time = request.form['ot_time']
    lat = request.form['lat']
    long = request.form['long']
    depth = request.form['depth']
    mag = request.form['mag']
    info = request.form['info']
    timeutc = date + ' ' + time

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
    sql_kota = "SELECT * FROM db_kota"
    cur.execute(sql_kota)
    kota = cur.fetchall()
    k = 0
    jarak = []
    azm = []

    while k < len(kota):
        lintang = lat
        bujur = long
        b = m.radians(float(lintang))
        c = m.radians(kota[k][2])
        delt = m.radians(kota[k][3] - float(bujur))
        deg = m.acos(m.sin(b) * m.sin(c) + m.cos(b) * m.cos(c) * m.cos(delt))
        jarak += [str(deg * 6371)]
        k = k + 1
    minjarak = jarak.index(str(min([float(i) for i in jarak])))
    min_jarak = ('%.0f') % float(jarak[minjarak])
    minkota = kota[minjarak][1]
    eplat, stlat, deltalong = (m.radians(float(lintang)), m.radians(float(kota[minjarak][2])),
                                m.radians(float(bujur) - kota[minjarak][3]))
    baz = m.atan2((m.sin(deltalong) * m.cos(eplat)),
                    (m.cos(stlat) * m.sin(eplat) - m.sin(stlat) * m.cos(eplat) * m.cos(deltalong)))
    baz = (m.degrees(baz) + 360) % 360

    if float(baz) < 5:
        arah = 'Utara '
        arah1 = 'Utara '
    elif float(baz) < 85:
        arah = 'TimurLaut '
        arah1 = 'Timur Laut '
    elif float(baz) < 95:
        arah = 'Timur '
        arah1 = 'Timur '
    elif float(baz) < 175:
        arah = 'Tenggara '
        arah1 = 'Tenggara '
    elif float(baz) < 185:
        arah = 'Selatan '
        arah1 = 'Selatan '
    elif float(baz) < 265:
        arah = 'BaratDaya '
        arah1 = 'Barat Daya '
    elif float(baz) < 275:
        arah = 'Barat '
        arah1 = 'Barat '
    else:
        arah = 'BaratLaut '
        arah1 = 'Barat Laut '

    param = ('Info Gempa Mag:' + mag + ', ' + tgl + '-' + bulan + '-' + tahun + ' ' + waktu +
                ' WIT, Lok: ' + ltg + ' ' + NS + ', ' + bujur + ' BT (' + min_jarak + ' km ' +
                arah + minkota + '), Kedlmn:' + depth + ' Km ::BMKG-TNT')
    ket = min_jarak + ' km ' + arah + minkota
    
    if opsi_par == "TERNATE":
        par = 'TNT'
    elif opsi_par == "MANADO":
        par = 'MNI'
    elif opsi_par == "GORONTALO":
        par = 'GTO'
    elif opsi_par == "PUSAT":
        par = 'PGN'
    elif opsi_par == "AMBON":
        par = 'AAI'
    else:
        par = 'TNT'

    idev = par+'-'+id
    info = request.form['info']
    insert = (idev, date, time, lat, long, depth, mag, ket, info)
    sql_insert = ("INSERT IGNORE INTO `db_gempa`(`Event ID`,`Origin Date`,`Origin Time`,"
                "`Latitude`,`Longitude`,`Depth`,`Magnitude`,`Remark`,`Information`) VALUES " + str(insert))
    a = cur.execute(sql_insert)
    print(a)
    mysql.connection.commit()

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

    tgl = ('%d')%float(tgl)
    fileoutput1 = 'fungsi/gmt/episenter.dat'
    fileoutput2 = 'fungsi/gmt/param.txt'
    fileoutput3 = 'fungsi/gmt/jarak.txt'
    fileoutput4 = 'fungsi/infogempa.txt'
    file1 = open(fileoutput1, 'w')
    file2 = open(fileoutput2, 'w')
    file3 = open(fileoutput3, 'w')
    file4 = open(fileoutput4, 'w')
    file1.write(lintang + ' ' + bujur + ' ' + depth + ' ' + mag)
    file2.write(tgl + ' ' + bulan1 + ' 20' + tahun + ' ' + waktu + ' WIT ' + ltg + ' '+ NS + ' - '
                +bujur + ' BT ' + depth + ' Km ' + minkota)
    file3.write(min_jarak + ' Km ' + arah1)
    file4.write(param)
    file1.close()
    file2.close()
    file3.close()
    file4.close()
    if len(info) > 3:
        with open('fungsi/gmt/info.txt','w') as f:
            f.write(info)
            f.close()
    else:
        with open('fungsi/gmt/info.txt','w') as f:
            f.write('')
            f.close()
    
    #return redirect(request.referrer)
def inputotomatis():
    cur = mysql.connection.cursor()
    
    opsi_par = request.form['par_otomatis']

    if opsi_par == 'TERNATE':
        fileinput = 'fungsi/mailexportfile.txt'
    elif opsi_par == 'MANADO':
        soup = BeautifulSoup(requests.get('http://202.90.198.127/esdx/log/manado.php').text, "lxml")
        with open("parameter.txt", "w") as file:
            file.write(str(soup))
            file.close
        fileinput = 'parameter.txt'
    elif opsi_par == 'PUSAT':
        soup = BeautifulSoup(requests.get('http://202.90.198.127/esdx/log/pusat.php').text, "lxml")
        with open("parameter.txt", "w") as file:
            file.write(str(soup))
            file.close
        fileinput = 'parameter.txt'
    elif opsi_par == 'AMBON':
        soup = BeautifulSoup(requests.get('http://202.90.198.127/esdx/log/ambon.php').text, "lxml")
        with open("parameter.txt", "w") as file:
            file.write(str(soup))
            file.close
        fileinput = 'parameter.txt'
    elif opsi_par == 'GORONTALO':
        soup = BeautifulSoup(requests.get('http://202.90.198.127/esdxsta/log/gorontalo.txt').text, "lxml")
        with open("parameter.txt", "w") as file:
            file.write(str(soup))
            file.close
        fileinput = 'parameter.txt'
    else:
        soup = BeautifulSoup(requests.get('http://202.90.198.127/esdxsta/log/ternate.txt').text, "lxml")
        with open("parameter.txt", "w") as file:
            file.write(str(soup))
            file.close
        fileinput = 'parameter.txt'

    return fileinput,opsi_par

def inputbyid():

    opsi_par = request.form['parameter']
    id = request.form['id']
    info = request.form['info']
    print(info)

    if opsi_par == "TERNATE":
        par = 'TNT'
        par1 = 'tnt_'
    elif opsi_par == "MANADO":
        par = 'MNI'
        par1 = 'mni_'
    elif opsi_par == "GORONTALO":
        par = 'GTO'
        par1 = 'gto_'
    elif opsi_par == "PUSAT":
        par = 'PGN'
        par1 = 'pst_'
    elif opsi_par == "AMBON":
        par = 'AAI'
        par1 = 'aai_'
    else:
        par = 'TNT'
        par1 = 'tnt_'

    idev = par+'-'+id
    fileinput = 'fungsi/arrival/esdx_arrival/'+par1+id+'.txt'

    return fileinput,opsi_par,info


def esdx2par(fileinput,opsi_par,info):
    cur = mysql.connection.cursor()
    
    fileoutput, fileoutput1, fileoutput2, fileoutput3, legend = 'fungsi/infogempa.txt', 'fungsi/gmt/episenter.dat', 'fungsi/gmt/param.txt', 'fungsi/gmt/jarak.txt', 'fungsi/gmt/legenda.txt'
    legenda = open(legend, 'w')
    
    #a=subprocess.call("/home/operasional/flask_app/fungsi/coba.sh")
    #run("pwd",shell=True)
    # baca isi file input dan buka file output
    file = open(fileinput, 'r')
    baris = file.readlines()
    for i in range(len(baris)):
        baris[i] = baris[i].split()
    file.close()
    file, file1, file2, file3 = open(fileoutput, 'w'), open(fileoutput1, 'w'), open(fileoutput2, 'w'), open(fileoutput3, 'w')

    sql_kota = "SELECT * FROM db_kota"
    cur.execute(sql_kota)
    kota = cur.fetchall()

    i=0
    while i < len(baris):
        if len(baris[i]) > 0 and baris[i][0] == 'Public':
            id = baris[i][2]
        if len(baris[i]) > 0 and baris[i][0] == 'Origin:':
            if opsi_par == 'PUSAT':
                i = i+1
            else:
                i = i
            date = baris[i + 1][1]
            wkt = baris[i + 2][1]
            timeutc = date + ' ' + wkt
            print(timeutc)
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            utc = datetime.strptime(timeutc[0:19], '%Y-%m-%d %H:%M:%S')
            utc = utc.replace(tzinfo=from_zone)
            ot = utc.astimezone(to_zone)
            tgl = ot.strftime("%d")
            bulan = ot.strftime("%b")
            tahun = ot.strftime("%y")
            waktu = ot.strftime("%X")
            lintang = (('%.2f') % float(baris[i + 3][1]))
            if float(lintang) > 0:
                NS = "LU"
                lat = lintang
            else:
                NS = "LS"
                lat = ('%.2f') % abs(float(lintang))

            bujur = (('%.2f') % float(baris[i + 4][1]))
            depth = ('%.0f') % float(baris[i + 5][1])
            k = 0
            jarak = []
            azm = []
            import math as m
            while k < len(kota):
                b = m.radians(float(lintang))
                c = m.radians(kota[k][2])
                delt = m.radians(kota[k][3] - float(bujur))
                deg = m.acos(m.sin(b) * m.sin(c) + m.cos(b) * m.cos(c) * m.cos(delt))
                jarak += [str(deg * 6371)]
                k = k + 1
            minjarak = jarak.index(str(min([float(i) for i in jarak])))
            min_jarak = ('%.0f') % float(jarak[minjarak])
            minkota = kota[minjarak][1]
            eplat, stlat, deltalong = (m.radians(float(lintang)), m.radians(float(kota[minjarak][2])),
                                        m.radians(float(bujur) - kota[minjarak][3]))
            baz = m.atan2((m.sin(deltalong) * m.cos(eplat)),
                            (m.cos(stlat) * m.sin(eplat) - m.sin(stlat) * m.cos(eplat) * m.cos(deltalong)))
            baz = (m.degrees(baz) + 360) % 360
            if float(baz) < 5:
                arah = 'Utara '
                arah1 = 'Utara '
            elif float(baz) < 85:
                arah = 'TimurLaut '
                arah1 = 'Timur Laut '
            elif float(baz) < 95:
                arah = 'Timur '
                arah1 = 'Timur '
            elif float(baz) < 175:
                arah = 'Tenggara '
                arah1 = 'Tenggara '
            elif float(baz) < 185:
                arah = 'Selatan '
                arah1 = 'Selatan '
            elif float(baz) < 265:
                arah = 'BaratDaya '
                arah1 = 'Barat Daya '
            elif float(baz) < 275:
                arah = 'Barat '
                arah1 = 'Barat '
            else:
                arah = 'BaratLaut '
                arah1 = 'Barat Laut '
        if len(baris[i])>1 and baris[i][1]=='Network':
            numag = baris[i][0]
            m_ = 1
            print('sampee sininiiii ######??',numag)
            while m_ <= float(numag):
                linemag = baris[i+m_]
                if 'preferred' in linemag:
                    mag = baris[i+m_][1]
                m_ += 1
            mag = ('%.1f')%float(mag)
            param = ('Info Gempa Mag:' + mag + ', ' + tgl + '-' + bulan + '-' + tahun + ' ' + waktu +
                        ' WIT, Lok: ' + lat + ' ' + NS + ', ' + bujur + ' BT (' + min_jarak + ' km ' +
                        arah + minkota + '), Kedlmn:' + depth + ' Km ::BMKG-TNT')
            episenter = ()
            if bulan == "Jan":
                bulan1 = "Januari"
            elif bulan == "Feb":
                bulan1 = "Februari"
            elif bulan == "Mar":
                bulan1 = "Maret"
            elif bulan == "Apr":
                bulan1 = "April"
            elif bulan == "May":
                bulan1 = "Mei"
            elif bulan == "Jun":
                bulan1 = "Juni"
            elif bulan == "Jul":
                bulan1 = "Juli"
            elif bulan == "Aug":
                bulan1 = "Agustus"
            elif bulan == "Sep":
                bulan1 = "September"
            elif bulan == "Oct":
                bulan1 = "Oktober"
            elif bulan == "Nov":
                bulan1 = "November"
            else:
                bulan1 = "Desember"
            file.write(param)
            file1.write(lintang + ' ' + bujur + ' ' + depth + ' ' + mag)
            tgl = ('%d')%float(tgl)
            file2.write(tgl + ' ' + bulan1 + ' 20' + tahun + ' ' + waktu + ' WIT ' + lat + ' ' + NS + ' - '
                        + bujur + ' BT ' + depth + ' Km ' + minkota)
            file3.write(min_jarak + ' Km ' + arah1)
            legenda.write('N\nT ' + param)
            if len(info) > 3:
                with open('fungsi/gmt/info.txt','w') as f:
                    f.write(info)
                    f.close()
            else:
                with open('fungsi/gmt/info.txt','w') as f:
                    f.write('')
                    f.close()

        i = i + 1

    file.close()
    file1.close()
    file2.close()
    file3.close()
    legenda.close()

    time = utc.strftime("%X")
    #id = "BMKG-TNT" + QtCore.QDate.fromString(date, "yyyy-MM-dd").toString(
    #    "yyyyMMdd") + "T" + QtCore.QTime.fromString(time, "hh:mm:ss").toString("hhmmss")
    lat = lintang
    long = bujur
    ket = min_jarak + ' km ' + arah + minkota
    info = info
    print('sampe infoo siniii ######',info)
    if opsi_par == "TERNATE":
        par = 'TNT'
        par1 = 'tnt'
    elif opsi_par == "MANADO":
        par = 'MNI'
        par1 = 'mni'
    elif opsi_par == "GORONTALO":
        par = 'GTO'
        par1 = 'gto'
    elif opsi_par == "PUSAT":
        par = 'PGN'
        par1 = 'pst'
    elif opsi_par == "AMBON":
        par = 'AAI'
        par1 = 'aai'
    else:
        par = 'TNT'
        par1 = 'tnt'
    idev = par+'-'+id
    
    insert = (idev, date, time, lat, long, depth, mag, ket, info)
    #print(insert)
    sql_insert = ("INSERT IGNORE INTO `db_gempa`(`Event ID`,`Origin Date`,`Origin Time`,"
                    "`Latitude`,`Longitude`,`Depth`,`Magnitude`,`Remark`,`Information`) VALUES " + str(insert))
    cur.execute(sql_insert)
    
    
    #cur.execute("INSERT INTO db_gempa('Event ID','Origin Date','Origin Time',\
    #    'Latitude','Longitude','Depth','Magnitude','Remark','Information') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",\
    #         (id,date,time,lat,long,depth,mag,ket,info))
    mysql.connection.commit()
    cur.close()


    arr = 'fungsi/arrival/esdx_arrival/'+par1+'_'+id+'.txt'
    if os.path.exists(arr):
        print("arrival sudah ada")
    else:
        source = fileinput
        target = arr
        shutil.copy(source, target)


    return "ok"

def teksinfogb():
    cur = mysql.connection.cursor()
    with open('fungsi/infogempa.txt') as f:
        info = f.readlines()  
        f.close()
    info = info[0]
    param = info.split(", ")
    ot = param[1]
    ot = ot.split()
    otime = ot[0]+' '+ot[1]
    dateotime = datetime.strptime(otime, '%d-%b-%y %H:%M:%S')
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    dateotime_rep = dateotime.replace(tzinfo=from_zone)
    dateotimeutc = dateotime_rep.astimezone(to_zone)
    dateutc = dateotimeutc.date()
    timeutc = dateotimeutc.time()
    timeutc = timeutc.strftime("%H:%M:%S")
    insert = (dateutc, timeutc)
    
    sql = ("SELECT * FROM db_gempa WHERE `Origin Date`=%s AND `Origin Time`=%s")
    cur.execute(sql, insert)
    parameter = cur.fetchone()
    infodir = parameter[8]
    infokata = info.split()

    inf = info.split(" ::")
    if len(infodir) > 3 and 'di' not in infokata:
        with open('fungsi/infogempa.txt', 'w') as f:
            f.write(inf[0]+', '+infodir+' ::'+inf[1])
            f.close()
    print('ini p[a----------=',parameter[8])

    return infodir


def editparameter():
    cur = mysql.connection.cursor()

    id = request.form['id']
    date = request.form['ot_date']
    time = request.form['ot_time']
    lat = request.form['lat']
    long = request.form['long']
    depth = request.form['depth']
    mag = request.form['mag']
    info = request.form['info']
    narasi = request.form['narasi']

    if len(narasi) > 5:
        with open('fungsi/narasigb/'+id+'.txt','w') as fout:
            fout.write(narasi)
            fout.close()

    #Upload files
    shakemap = request.files['file']
    print('halloo disini shakemap : '+str(shakemap))
    if shakemap.getbuffer().nbytes > 0:
        fname = secure_filename(shakemap.filename)
        print(fname)
        shakemap.save(app.config['UPLOAD_FOLDER'] + fname)
        namefile = fname.split('.')
        print(namefile[0])
        filerename = id +'.jpg'
        os.system('pwd')
        os.rename('static/shakemap/'+fname, 'static/shakemap/'+filerename)
        



    timeutc = date + ' ' + time

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
    sql_kota = "SELECT * FROM db_kota"
    cur.execute(sql_kota)
    kota = cur.fetchall()
    k = 0
    jarak = []

    while k < len(kota):
        lintang = lat
        bujur = long
        b = m.radians(float(lintang))
        c = m.radians(kota[k][2])
        delt = m.radians(kota[k][3] - float(bujur))
        deg = m.acos(m.sin(b) * m.sin(c) + m.cos(b) * m.cos(c) * m.cos(delt))
        jarak += [str(deg * 6371)]
        k = k + 1
    minjarak = jarak.index(str(min([float(i) for i in jarak])))
    min_jarak = ('%.0f') % float(jarak[minjarak])
    minkota = kota[minjarak][1]
    eplat, stlat, deltalong = (m.radians(float(lintang)), m.radians(float(kota[minjarak][2])),
                                m.radians(float(bujur) - kota[minjarak][3]))
    baz = m.atan2((m.sin(deltalong) * m.cos(eplat)),
                    (m.cos(stlat) * m.sin(eplat) - m.sin(stlat) * m.cos(eplat) * m.cos(deltalong)))
    baz = (m.degrees(baz) + 360) % 360

    if float(baz) < 5:
        arah = 'Utara '
        arah1 = 'Utara '
    elif float(baz) < 85:
        arah = 'TimurLaut '
        arah1 = 'Timur Laut '
    elif float(baz) < 95:
        arah = 'Timur '
        arah1 = 'Timur '
    elif float(baz) < 175:
        arah = 'Tenggara '
        arah1 = 'Tenggara '
    elif float(baz) < 185:
        arah = 'Selatan '
        arah1 = 'Selatan '
    elif float(baz) < 265:
        arah = 'BaratDaya '
        arah1 = 'Barat Daya '
    elif float(baz) < 275:
        arah = 'Barat '
        arah1 = 'Barat '
    else:
        arah = 'BaratLaut '
        arah1 = 'Barat Laut '

    param = ('Info Gempa Mag:' + mag + ', ' + tgl + '-' + bulan + '-' + tahun + ' ' + waktu +
                ' WIT, Lok: ' + ltg + ' ' + NS + ', ' + bujur + ' BT (' + min_jarak + ' km ' +
                arah + minkota + '), Kedlmn:' + depth + ' Km ::BMKG-TNT')
    ket = min_jarak + ' km ' + arah + minkota
    idev = id
    info = request.form['info']
    insert = (date, time, lat, long, depth, mag, ket, info, idev)
    sql_update = ("UPDATE `db_gempa` SET `Origin Date`=%s,`Origin Time`=%s,`Latitude`=%s,`Longitude`=%s,`Depth`=%s,"
                    "`Magnitude`=%s,`Remark`=%s, `Information`=%s WHERE `Event ID`=%s ")
                
    cur.execute(sql_update, insert)
    mysql.connection.commit()

    
    #return redirect(request.referrer)