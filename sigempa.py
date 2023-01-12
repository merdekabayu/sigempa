from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
from flask_mysqldb import MySQL
from calendar import monthrange
from datetime import datetime, timedelta
import time
import fungsi.inputmanual as input
import fungsi.mapping as mapping
import fungsi.infogempa as infogempa
import fungsi.filter as f
import fungsi.infografis as ig
import fungsi.export as export
from fungsi.statistik import hitung_wilayah, hitung_chart
from fungsi.filter import filter_area
from fungsi.arrival import  esdx2pha, arrival2spk, arrivalsc4tnt, arrivalsc3pst
from fungsi.stat_sensor import status,slinktool, tabel_slinktool
from fungsi.waveform import waveformplot, allwaveform, down_waveformbyevent
import subprocess,os
import bcrypt

with open('workdir.txt','w') as f:
    py2output = subprocess.check_output(['whoami'])
    f.write(py2output)
    f.close()


app = Flask(__name__)
app.secret_key = "membuatLOginFlask1"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sigempa2023'
app.config['MYSQL_DB'] = 'sistem_diseminasi_test'
app.config["UPLOAD_FOLDER"] = "static/shakemap/"

mysql = MySQL(app)

@app.route('/htmltes')
def tes():
    
    return render_template('htmltes.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login(): 

    if request.method == 'POST':
        usr = request.form['username']
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor()
        curl.execute("SELECT * FROM users WHERE user=%s",(usr,))
        user = curl.fetchone()
        #print(user['password'])
        curl.close()

        if user is not None and len(user) > 0 :
            #print(password)
            if bcrypt.hashpw(password, user[2].encode('utf-8')) == user[2].encode('utf-8'):
                session['id'] = user[0]
                session['user'] = user[1]
                return redirect(url_for('index'))
            else :
                #session.clear()
                flash("Wrong Password !!")
                return render_template("loginpage.html")
                #return redirect(url_for('login'))
        else :
            flash("User Not Found !!")
            return render_template("loginpage.html")
    else:
        #session.clear()
        return render_template("loginpage.html")
    
    #return render_template("loginpage.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login')) 


@app.route('/')

def index():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM db_gempa ORDER BY 2 DESC, 3 DESC LIMIT 0, 50")
        parameter = cur.fetchall()
        cur.close()

        with open('fungsi/infogempa.txt') as f:
            info = f.readlines()  
            f.close()  
        input.teksinfogb()
        fileinput = 'fungsi/gmt/episenter.dat'
        file = open(fileinput, 'r')
        baris = file.readlines()
        lat = baris[0].split()[0]
        long = baris[0].split()[1]
        #submit_ok = True
        filemap = subprocess.check_output('ls static/peta_diseminasi*.png',shell=True)
        mapf = filemap.decode().split('\n')[0]
        return render_template('mainpage1.html', mapfile = mapf, data=parameter, infogb=info, koord =[lat,long])
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))
    

@app.route('/index/tabelgempa')
def tabelgempa():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM db_gempa ORDER BY 2 DESC, 3 DESC LIMIT 0, 50")
        parameter = cur.fetchall()
        cur.close()
        noshakemap = '../static/noshakemap.jpg'
        return render_template('tabeleq.html', data=parameter, shakemap=noshakemap)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))


@app.route('/infografis/mingguan')
def ig_mingguan():
    hari = 7
    tdy = datetime.today()
    end = (tdy - timedelta(days=1))
    start = (tdy - timedelta(days=hari))
    
    chart = ig.infografis(start,end)
    par = chart[0]
    stat = chart[1]
    jml_gempa = stat[0][0]
    jml_drskn = stat[0][1]
    hist_harian = stat[0][2]
    mag = stat[0][3]
    depth = stat[0][4]
    hist_mag = stat[0][5]
    hist_tab = stat[0][6]
    wilayah = stat[1][:7]
    rangedate = chart[2]

    start,end = "a","a"
    #mapping.map_seismisitas_mingguan(start,end)
    #print('ini histogram = #######',hist_tab)

    #submit_ok = True
    filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
    mapf = filemap.decode().split('\n')[0]
    return render_template('infog_mingguan.html',mapfile=mapf, data=par,
                                                jml_gempa=jml_gempa,
                                                jml_drskn=jml_drskn,
                                                hist_harian=hist_harian,
                                                mag=mag,
                                                depth=depth,
                                                hist_mag=hist_mag,
                                                hist_tab=hist_tab,
                                                wilayah=wilayah,
                                                rangedate=rangedate)


@app.route('/infografis/bulanan')
def ig_bulanan():
    today = datetime.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)
    thn = last_month.year
    bulan = last_month.month
    lhari = last_month.day
    end = datetime(thn,bulan,lhari)
    start = datetime(thn,bulan,1)
    
    chart = ig.infografis(start,end)
    par = chart[0]
    stat = chart[1]
    jml_gempa = stat[0][0]
    jml_drskn = stat[0][1]
    hist_harian = stat[0][2]
    mag = stat[0][3]
    depth = stat[0][4]
    hist_mag = stat[0][5]
    hist_tab = stat[0][6]
    wilayah = stat[1][:7]
    rangedate = chart[2]

    filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
    mapf = filemap.decode().split('\n')[0]

    return render_template('infog_bulanan.html', mapfile=mapf,data=par,
                                                jml_gempa=jml_gempa,
                                                jml_drskn=jml_drskn,
                                                hist_harian=hist_harian,
                                                mag=mag,
                                                depth=depth,
                                                hist_mag=hist_mag,
                                                hist_tab=hist_tab,
                                                wilayah=wilayah,
                                                rangedate=rangedate)


@app.route('/infografis/custom', methods=["POST","GET"])
def customig():
    if 'user' in session:
        if request.method == 'POST':
            date = request.form['datefilter']
            
            datestart = date.split()[0]
            dateend = date.split()[2]
            
            start = datetime.strptime(datestart, '%d-%b-%y')
            end = datetime.strptime(dateend, '%d-%b-%y')

            chart = ig.infografis(start,end)
            par = chart[0]
            stat = chart[1]
            jml_gempa = stat[0][0]
            jml_drskn = stat[0][1]
            hist_harian = stat[0][2]
            mag = stat[0][3]
            depth = stat[0][4]
            hist_mag = stat[0][5]
            hist_tab = stat[0][6]
            wilayah = stat[1][:7]
            rangedate = chart[2]
            filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
            mapf = filemap.decode().split('\n')[0]

            return render_template('infog_custom.html',mapfile=mapf, data=par,
                                                        jml_gempa=jml_gempa,
                                                    jml_drskn=jml_drskn,
                                                    hist_harian=hist_harian,
                                                    mag=mag,
                                                    depth=depth,
                                                    hist_mag=hist_mag,
                                                    hist_tab=hist_tab,
                                                    wilayah=wilayah,
                                                    rangedate=rangedate)
        else:
            return redirect(url_for('ig_mingguan'))
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))

@app.route('/infografis/filter')
def filterig():
    if 'user' in session:
        tdy = datetime.today()
        end = tdy
        start = tdy - timedelta(days=30)
        
        chart = ig.infografis(start,end)
        par = chart[0]
        stat = chart[1]
        jml_gempa = stat[0][0]
        jml_drskn = stat[0][1]
        hist_harian = stat[0][2]
        mag = stat[0][3]
        depth = stat[0][4]
        hist_mag = stat[0][5]
        hist_tab = stat[0][6]
        wilayah = stat[1][:7]
        rangedate = chart[2]

        start,end = "a","a"
        #mapping.map_seismisitas_mingguan(start,end)
        #print('ini histogram = #######',hist_tab)

        today = datetime.today()
        day30ago = today - timedelta(days=30)
        today = today.strftime('%d-%m-%Y %H:%M')
        day30ago = day30ago.strftime('%d-%m-%Y %H:%M')
        depth1 = 0
        depth2 = 1000
        mag1 = 1.0
        mag2 = 9.0
        lat1 = 3.50
        lat2 = -2.75
        long1 = 124.00
        long2 = 130.00
        felt = 0
        #submit_ok = True
        filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
        mapf = filemap.decode().split('\n')[0]
        return render_template('infog_filter.html', mapfile=mapf,data=par,
                                                    jml_gempa=jml_gempa,
                                                    jml_drskn=jml_drskn,
                                                    hist_harian=hist_harian,
                                                    mag=mag,
                                                    depth=depth,
                                                    hist_mag=hist_mag,
                                                    hist_tab=hist_tab,
                                                    wilayah=wilayah,
                                                    rangedate=rangedate, date = [day30ago,today,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt])
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))

@app.route('/infografis/filteredig', methods=["POST","GET"])
def filtered_ig():
    try:
        if request.method == 'POST':
            date1 = request.form['date1']
            date2 = request.form['date2']
            depth1 = request.form['depth1']
            depth2 = request.form['depth2']
            mag1 = request.form['mag1']
            mag2 = request.form['mag2']
            lat1 = request.form['lat1']
            lat2 = request.form['lat2']
            long1 = request.form['long1']
            long2 = request.form['long2']
            felt = request.form.getlist('felt')
            felt = len(felt)
            print('halo0000 disini felt ############',felt)
            start = datetime.strptime(date1, '%d-%m-%Y %H:%M').date()
            end = datetime.strptime(date2, '%d-%m-%Y %H:%M').date()
            hari = (end - start).days+1
            date_list = [end - timedelta(days=x) for x in range(hari)]
            date_list.sort()
            chart = ig.infografis_parfilter(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            par = chart[0]
            stat = chart[1]
            jml_gempa = stat[0][0]
            jml_drskn = stat[0][1]
            hist_harian = stat[0][2]
            mag = stat[0][3]
            depth = stat[0][4]
            hist_mag = stat[0][5]
            hist_tab = stat[0][6]
            wilayah = stat[1][:7]
            rangedate = chart[2]
            filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
            mapf = filemap.decode().split('\n')[0]
            return render_template('infog_filter.html',mapfile=mapf, data=par,
                                                    jml_gempa=jml_gempa,
                                                    jml_drskn=jml_drskn,
                                                    hist_harian=hist_harian,
                                                    mag=mag,
                                                    depth=depth,
                                                    hist_mag=hist_mag,
                                                    hist_tab=hist_tab,
                                                    wilayah=wilayah,
                                                    rangedate=rangedate, date = [date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt])
        else:
            today = datetime.today()
            filter = f.filter_parameter()
            today = today.strftime('%d-%m-%Y %H:%M')

            filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
            mapf = filemap.decode().split('\n')[0]
            
            return render_template('infog_filter.html',mapfile=mapf,data=filter, date = [today,today])

    except:
        return redirect(url_for('filterig'))

@app.route('/database')
def database():
    if 'user' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM db_gempa ORDER BY 2 DESC, 3 DESC LIMIT 0, 50")
        parameter = cur.fetchall()
        cur.close()
        today = datetime.today()
        day30ago = today - timedelta(days=30)
        today = today.strftime('%d-%m-%Y %H:%M')
        day30ago = day30ago.strftime('%d-%m-%Y %H:%M')
        depth1 = 0
        depth2 = 1000
        mag1 = 1.0
        mag2 = 9.0
        lat1 = 3.50
        lat2 = -2.75
        long1 = 124.00
        long2 = 130.00
        return render_template('database.html',data=parameter, date = [day30ago,today,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2])
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))

@app.route('/database/sorted', methods=["POST","GET"])
def filter_tabel():
    try:
        if request.method == 'POST':
            date1 = request.form['date1']
            date2 = request.form['date2']
            depth1 = request.form['depth1']
            depth2 = request.form['depth2']
            mag1 = request.form['mag1']
            mag2 = request.form['mag2']
            lat1 = request.form['lat1']
            lat2 = request.form['lat2']
            long1 = request.form['long1']
            long2 = request.form['long2']
            filter = f.filter_parameter(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2)
            return render_template('database.html',data=filter, date = [date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2])
        else:
            today = datetime.today()
            filter = f.filter_parameter()
            today = today.strftime('%d-%m-%Y %H:%M')
            
            return render_template('database.html',data=filter, date = [today,today])
    except:
        return redirect(url_for('database'))

    

@app.route('/export/<string:tipe>', methods=["GET"])
def exp(tipe):
    if 'user' in session:
        tdy = datetime.today()
        type = tipe.split('!')[0]
        if type == 'mingguan':
            hari = 7
            end = (tdy - timedelta(days=1))
            start = (tdy - timedelta(days=hari))
            date_list = [end - timedelta(days=x) for x in range(hari)]
            date_list.sort()
            fpath = 'fungsi/export/Statistik Gempa Mingguan '
            chart = ig.infografis(start,end)
        elif type == 'bulanan':
            first = tdy.replace(day=1)
            last_month = first - timedelta(days=1)
            thn = last_month.year
            bulan = last_month.month
            lhari = last_month.day
            end = datetime(thn,bulan,lhari)
            start = datetime(thn,bulan,1)
            date_list = [end - timedelta(days=x) for x in range(lhari)]
            date_list.sort()
            fpath = 'fungsi/export/Statistik Gempa Bulanan '
            chart = ig.infografis(start,end)
        elif type == 'customig':
            tgl = tipe.split('!')[1]
            start = tgl.split('@')[0]
            end = tgl.split('@')[1]
            start = datetime.strptime(start, '%d-%B-%Y').date()
            end = datetime.strptime(end, '%d-%B-%Y').date()
            hari = (end - start).days+1
            date_list = [end - timedelta(days=x) for x in range(hari)]
            date_list.sort()
            fpath = 'fungsi/export/Statistik Gempa Periode '
            chart = ig.infografis(start,end)
        elif type == 'dbfilter':
            string = tipe.split('!')[1]
            par = string.split('@')
            date1 = par[0]
            date2 = par[1]
            depth1 = par[2]
            depth2 = par[3]
            mag1 = par[4]
            mag2 = par[5]
            lat1 = par[6]
            lat2 = par[7]
            long1 = par[8]
            long2 = par[9]
            felt = float(par[10])
            start = datetime.strptime(date1, '%d-%m-%Y %H:%M').date()
            end = datetime.strptime(date2, '%d-%m-%Y %H:%M').date()
            hari = (end - start).days+1
            date_list = [end - timedelta(days=x) for x in range(hari)]
            date_list.sort()
            chart = ig.infografis_parfilter(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            fpath = 'fungsi/export/Statistik Filter by '

            
        
        par = chart[0]
        chart = hitung_chart(par,date_list)
        wilayah = hitung_wilayah(par)
        start = chart[2][0][0]
        end = chart[2][0][len(chart[2][0])-1]

        if type == 'dbfilter':
            path = fpath+date1+'%'+date2+'%'+depth1+'%'+depth2+'%'+mag1+'%'+mag2+'%'+lat1+'%'+lat2+'%'+long1+'%'+long2+'.csv'
        else:
            path = fpath+start+' sd '+end+'.csv'
        export.export(par,chart,wilayah,path)
        print('halo disini export')
        
        return send_file(path, as_attachment=True)
        
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))


@app.route('/database/arrival')
def arrival():
    if 'user' in session:
        today = datetime.today()
        day30ago = today - timedelta(days=30)
        today = today.strftime('%d-%m-%Y %H:%M')
        day30ago = day30ago.strftime('%d-%m-%Y %H:%M')
        depth1 = 0
        depth2 = 1000
        mag1 = 1.0
        mag2 = 9.0
        lat1 = 3.50
        lat2 = -2.75
        long1 = 124.00
        long2 = 130.00
        return render_template('database_arrival.html', date = [day30ago,today,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2])
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))

@app.route('/database/downloadarrival', methods=["POST"])
def arrival_download():
    if 'user' in session:
        date1 = request.form['date1']
        date2 = request.form['date2']
        depth1 = request.form['depth1']
        depth2 = request.form['depth2']
        mag1 = request.form['mag1']
        mag2 = request.form['mag2']
        lat1 = request.form['lat1']
        lat2 = request.form['lat2']
        long1 = request.form['long1']
        long2 = request.form['long2']
        felt = 0
        format = request.form['format_arrival']
        source = request.form['data_source']
        
        if source == 'SPK':
            path = arrival2spk(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.txt'
        elif source == 'Seiscomp4 Ternate':
            path = arrivalsc4tnt(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.txt'
        elif source == 'Repogempa PGN':
            path = arrivalsc3pst(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.txt'
        
        if format == 'HypoDD (*.pha)':
            finp = path
            path = esdx2pha(finp)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.pha'
        

        #path ='fungsi/export/Data Arrival Format 2.txt'
        return send_file(path, as_attachment=True, attachment_filename=namefile)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))



@app.route('/sensor/status', methods=["POST","GET"])
def sensor_stat():
    
    print('ini sensor/status')
    data = slinktool()
    print('ini slibktool ok')
    last_data = data[0]
    print(last_data)
    today = data[1]
    stat = status(last_data,today)
    tabel = tabel_slinktool(last_data,today)
    #waveform = 

    utcnow = datetime.utcnow()
    utctime = utcnow.time()
    timerange = datetime(2023,1,1,15,0,1).time()
    timerange1 = datetime(2023,1,1,23,55,0).time()
    dt = datetime.today()
    yes = (dt - timedelta(days=1))
    yest = yes.strftime('%d%m%y')
    
    fileav='static/availability_'+yest+'.png'
    print('sampee siniiii ####',fileav)
    if not os.path.exists(fileav):
        if utctime >= timerange and utctime <= timerange1:
            
            command = 'sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:availability_new.png '+fileav
            os.system(command)
            print('sampee siniiii 1 ####')
        else:
            os.system('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 sh run_availability.sh')
            command = 'sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:availability_new.png '+fileav
            os.system(command)
    if request.method == 'GET':
        sta = 'TNTI'
    else:
        sta = request.form['station']
    try:
        waveformplot(sta)
        nodata = ''
        fwav = subprocess.check_output('ls static/waveform/waveform24h'+sta+'*.jpg',shell=True)
        wavf = fwav.decode().split('\n')[0]
        
    except:
        nodata = 'nodata'
        wavf = ''
    
    filemap = subprocess.check_output('ls static/sensor_status*.jpg',shell=True)
    mapf = filemap.decode().split('\n')[0]
    
    #os.system('ls static/waveform/waveform24h'+sta+'*.jpg')
    
    

    return render_template('sensor_stat.html', gambar=[mapf,wavf], data=tabel,fileav=fileav,sta=sta,nodata = nodata)


@app.route('/sensor/allwaveform', methods=["POST","GET"])
def downloadwaveform():
    if 'user' in session:
        if request.method == 'GET':
            today = datetime.today()
            today = today.strftime('%d-%m-%Y %H:%M:%S')

            return render_template('download_waveform.html', date = [today,today])
        else:
            try:
                allwaveform()
                return send_file('fungsi/waveform/waveform.mseed', as_attachment=True, attachment_filename='waveform.mseed')
            except:
                today = datetime.today()
                today = today.strftime('%d-%m-%Y %H:%M:%S')
                return render_template('download_waveform.html', date = [today,today])

    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))


@app.route('/sensor/waveformbyevent', methods=["POST","GET"])
def waveformbyevent():
    if 'user' in session:
        if request.method == 'GET':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM db_gempa ORDER BY 2 DESC, 3 DESC LIMIT 0, 50")
            parameter = cur.fetchall()
            cur.close()
            
        else:
            parameter = f.filter()
            
        parameter_new = []
        for par in parameter:
            try:
                id = par[0]
                s = id.split('-')[0]
                if s == 'TNT':
                    source = 'tnt_'
                elif s == 'MNI':
                    source = 'mni_'
                elif s == 'GTO':
                    source = 'gto_'
                elif s == 'PGN':
                    source = 'pst_'
                elif s == 'AAI':
                    source = 'aai_'
                idpar = id.split('-')[1]
                dataarrival = (source+idpar+'.txt')
                if os.path.exists('fungsi/arrival/esdx_arrival/'+dataarrival):
                    arrivalexist = 1
                else:
                    arrivalexist = 0
                param = (par[0],par[1],par[2],par[3],par[4],par[5],par[6],par[7],par[8],dataarrival,arrivalexist)
            except:
                dataarrival = (par[0]+'.txt')
                arrivalexist = 0
                param = (par[0],par[1],par[2],par[3],par[4],par[5],par[6],par[7],par[8],dataarrival,arrivalexist)
            parameter_new += [param]
        return render_template('waveformbyevent.html', data=parameter_new)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))


@app.route('/sensor/waveformbyevent/download', methods=["POST","GET"])
def downloadwaveformbyevent():
    if 'user' in session:
        if request.method == 'GET':
            return redirect(url_for('waveformbyevent'))
        else:
            id = down_waveformbyevent()
            print(id)
            #return Response(generate(), mimetype='text/csv')
            return send_file('fungsi/waveform/'+id+'.mseed', as_attachment=True, conditional=True, attachment_filename=id+'.mseed',cache_timeout=600)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))



@app.route('/inputmanual', methods=["POST","GET"])
def inputmanual():
    if request.method == 'POST':
        date = request.form['ot_date']
        time = request.form['ot_time']
        lat = request.form['lat']
        long = request.form['long']
        depth = request.form['depth']
        mag = request.form['mag']
        info = request.form['info']

        if lat == '' or long == '' or depth == '' or mag == '':
            out = input.inputbyid()
            fileinput = out[0]
            opsi_par = out[1]
            info = out[2]
            try:
                input.esdx2par(fileinput,opsi_par,info)
            except:
                flash("Empty arrival data. Please enter parameters manually !!",'fail')
                return redirect(url_for('index'))

        else:
            input.inputmanual()

        
        mapping.map_diseminasi()
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))



@app.route('/inputotomatis', methods=["POST","GET"])
def inputotomatis():
    if request.method == 'POST':
        out = input.inputotomatis()
        fileinput = out[0]
        opsi_par = out[1]
        info = '-'
        input.esdx2par(fileinput,opsi_par,info)
        mapping.map_diseminasi()
        flash("Input Sucess !!",'success')
        return redirect(request.referrer)
        #return render_template('index4.html', submit=submit_ok, infogb=info)
    else:
        return redirect(url_for('index'))


@app.route('/editparameter', methods=["POST","GET"])
def editparameter():
    if request.method == 'POST':
        input.editparameter()
        return redirect(request.referrer)
    else:
        return redirect(url_for('index'))

@app.route('/index/tabelgempa/filteredtable', methods=["POST","GET"])
def filter():
    noshakemap = '../../static/noshakemap.jpg'
    if 'user' in session:
        if request.method == 'POST':
            tabel = f.filter()
            return render_template('tabeleq.html', data=tabel, shakemap=noshakemap)
        else:
            tabel = f.filter_edit()
            return render_template('tabeleq.html', data=tabel, shakemap=noshakemap)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))


@app.route('/mapdetail/<string:var>', methods=["GET"])
def mapdetail(var):
    mapping.map_detail(var)
    return var+'.png'

@app.route('/detailshake/<string:var>', methods=["GET"])
def detailshake(var):
    return var+'.jpg'

@app.route('/teksparameter/<string:var>', methods=["GET"])
def teksparameter(var):
    teks = infogempa.infogempa(var)
    return teks

@app.route('/teksnarasi/<string:var>', methods=["GET"])
def teksnarasi(var):
    with open('fungsi/narasigb/'+var+'.txt','r') as fin:
        teks = fin.read()
    #teks = infogempa.infogempa(var)
    return teks

@app.route('/hapus/<string:id_data>', methods=["GET"])
def hapus(id_data):
    if 'user' in session:
        cur = mysql.connection.cursor()
        sql = f"DELETE FROM db_gempa WHERE `Event ID`='{id_data}'"
        a = cur.execute(sql)
        mysql.connection.commit()
        return redirect(request.referrer)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))
    
    
if __name__ == "__main__":
	app.run(debug=True)
