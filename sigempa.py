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
from fungsi.waveform import *
import subprocess,os
import bcrypt
import glob
import re
from pathlib import Path

#os.system('whoami')


app = Flask(__name__)
app.secret_key = "membuatLOginFlask1"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sigempa2023'
app.config['MYSQL_DB'] = 'sistem_diseminasi'
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
        print('iiniiii infoooo',info)

        fileinput = 'fungsi/gmt/episenter.dat'
        file = open(fileinput, 'r')
        baris = file.readlines()

        if info == [] or baris == []:
            print('sampee siniiii')
            param = input.db2infogb()[0]
            info = [param]
            koord = input.db2infogb()[1]
            input.teksinfogb(param)
        else:
            param = info[0]
            input.teksinfogb(param)
            lat = baris[0].split()[0]
            long = baris[0].split()[1]
            koord = [lat,long]

        
        
        images = os.listdir('static/')
        name = set(os.path.splitext(k)[0] for k in images if k[:15]=='peta_diseminasi')
        ext = set(os.path.splitext(k)[1] for k in images if k[:15]=='peta_diseminasi')
        mapf = 'static/'+''.join(name)+''.join(ext)

        print('ini infooooooo',info)

        
        return render_template('mainpage1.html', mapfile = mapf, data=parameter, infogb=info, koord = koord)
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
    

@app.route('/tabelgempa/ekinerja', methods=['GET', 'POST'])
def tabel_ekin():
    if 'user' in session:
        
        if request.method == 'POST':
            tabel = f.filter_ekin()
            return render_template('tabel_ekin.html', data=tabel)
            
        else:
            os.system('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 sh vps_server/ekin_arrival/copy_arrival.sh')
            input.input_ekin('fungsi/arrival/ekin_arrival/ekin_arrival.txt')
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM db_ekin ORDER BY 2 DESC, 3 DESC LIMIT 0, 100")
            parameter = cur.fetchall()
            cur.close()

            return render_template('tabel_ekin.html', data=parameter)
        
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))
    

@app.route('/datapga',methods=["POST","GET"])
def datapga():
    if 'user' in session:
        if request.method == 'GET':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM db_gempa ORDER BY 2 DESC, 3 DESC LIMIT 0, 50")
            parameter = cur.fetchall()
            cur.close()
        else:
            cur = mysql.connection.cursor()
            date = request.form['datefilter']
            with open("fungsi/filter.txt", "w") as file:
                    file.write(date)
                    file.close
            datestart = date.split()[0]
            dateend = date.split()[2]
            sql_filter = "SELECT * FROM db_gempa WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
            condition = (datestart,dateend)
            cur.execute(sql_filter, condition)
            parameter = cur.fetchall()
            cur.close()
        # qc_list = os.listdir('fungsi/arrival/qc_arrival/')
        qc_list = sorted(Path('fungsi/arrival/qc_arrival/').iterdir(), key=os.path.getmtime)
        qc_data = []
        for qc in qc_list:
            file = str(qc).split('/')[3]
            name = file.split('_')
            id = name[0]
            ot = name[1].split('.')[0]
            t = datetime.strptime(ot, '%Y%m%dT%H%M%S')
            tstart = (t - timedelta(seconds=4))
            tend = (t + timedelta(seconds=4))
            # print(id,t,tstart,tend)
            qc_data += [[id,t,tstart,tend,qc]]

        # print(qc_data)

        parameter_qc = []
        for par in parameter:
            date = par[1]
            time = par[2]
            ot=datetime.combine(date, datetime.strptime(str(time), '%H:%M:%S').time())
            data_qc=0
            id_qc = "-"
            for qc in qc_data:
                if qc[2]<ot<qc[3]:
                    data_qc = 1
                    id_qc = qc[0]

            cur = mysql.connection.cursor()
            sql = f"SELECT * FROM db_pga WHERE `QC ID`='{id_qc}'"
            cur.execute(sql)
            ada = cur.fetchone()
            cur.close()
            par = list(par)
            par.append(data_qc)
            par.append(id_qc)
            if ada is not None:
                pga_picked = 1
                par.append(pga_picked)
                d = list(ada)
                t_qc = str(d[3])[:12]
                d[3] = t_qc
                ada = tuple(d)
                par.append(ada)
                
            else:
                pga_picked = 0
                par.append(pga_picked)
                par.append(('-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-',\
                             '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-') )
            # print(par,data_qc)
            parameter_qc += [par]
        print(parameter_qc)
        return render_template('tabelqc.html', data=parameter_qc)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))



@app.route('/pickpga/', methods=["GET","POST"])
def pickpga():
    if 'user' in session:
        id_data = request.args.get('id')
        id_qc = request.args.get('id_qc')
        cur = mysql.connection.cursor()
        sql = f"SELECT * FROM db_gempa WHERE `Event ID` = '{id_data}'"
        cur.execute(sql)
        parameter = cur.fetchone()
        cur.close()

        print(parameter)
        id_qc = request.args.get('id_qc')
        print('ini id qc',id_qc)
        datapga = plotpga(parameter)

        return render_template('pickpga.html', datapga=datapga,id_qc=id_qc,parameter=parameter)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))
    
@app.route('/submitpga', methods=["POST"])
def submitpga():
    if 'user' in session:
        
        id_qc = request.form['id_qc']
        id_event = request.form['id_event']
        info = request.form['info']
        # print('ini submitpga = ',mtai,tnti,ihmi,a_hmhn,a_mumui,id_qc)

        ls = glob.glob('fungsi/arrival/qc_arrival/'+str(id_qc)+'*')
        ls.sort(key=os.path.getmtime)
        print(ls[len(ls)-1])
        f_qc = ls[len(ls)-1]

        data = id_event,info

        input.inputpga(fileinput=f_qc,data=data)

        return redirect(url_for('datapga'))
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
    

    #mapping.map_seismisitas_mingguan(start,end)
    
    filemap = subprocess.check_output('ls static/seismisitas*.jpg',shell=True)
    mapf = filemap.decode().split('\n')[1]
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
    mapf = filemap.decode().split('\n')[1]

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
            mapf = filemap.decode().split('\n')[1]

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
        mapf = filemap.decode().split('\n')[1]
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
            mapf = filemap.decode().split('\n')[1]
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

        resptnt = os.system('ping -c 1 36.91.152.130')
        resppst=os.system("sshpass -p 'bmkg212$' ssh -t -p2222 sysop@36.91.152.130 ping -c 1 172.19.3.51")
        print('disini respon',resppst,resptnt)
        if source == 'SPK':
            path = arrival2spk(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.txt'
        
        
        elif source == 'Seiscomp4 Ternate' and resptnt == 0:
            path = arrivalsc4tnt(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.txt'
        elif source == 'Repogempa PGN'and resptnt == 0 and resppst == 0:
            path = arrivalsc3pst(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.txt'
        elif resptnt != 0 or resppst != 0:
            flash("Request Fail",'fail')
            return redirect(request.referrer)


    
        
        if format == 'HypoDD (*.pha)':
            finp = path
            path = esdx2pha(finp)
            nfile = path.split('.')[0]
            nfile = nfile.split('/')[2]
            namefile = nfile+'_'+date1+'_'+date2+'_'+depth1+'_'+depth2+'_'+mag1+'_'+mag2+'_'+lat1+'_'+lat2+'_'+long1+'_'+long2+'.pha'
        
        print(namefile)
        #path ='fungsi/export/Data Arrival Format 2.txt'
        return send_file(path, as_attachment=True, download_name=namefile)
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))



@app.route('/sensor/quality', methods=["POST","GET"])
def sensor_qual():
    resptnt = os.system('ping -c 1 36.91.152.130')
    print(resptnt)
    if resptnt == 0:
        if request.method == 'GET':
            sta = 'TNTI'
        else:
            sta = request.form['station']
        try:
            psdplot(sta)
            nodata = ''
            fwav = subprocess.check_output('ls static/waveform/wform_'+sta+'_Z.jpg',shell=True)
            fpsd = subprocess.check_output('ls static/waveform/psd_'+sta+'_Z.jpg',shell=True)
            wavfz = fwav.decode().split('\n')[0]
            psdz = fpsd.decode().split('\n')[0]
            
            fwav = subprocess.check_output('ls static/waveform/wform_'+sta+'_N.jpg',shell=True)
            fpsd = subprocess.check_output('ls static/waveform/psd_'+sta+'_N.jpg',shell=True)
            wavfn = fwav.decode().split('\n')[0]
            psdn = fpsd.decode().split('\n')[0]

            fwav = subprocess.check_output('ls static/waveform/wform_'+sta+'_E.jpg',shell=True)
            fpsd = subprocess.check_output('ls static/waveform/psd_'+sta+'_E.jpg',shell=True)
            wavfe = fwav.decode().split('\n')[0]
            psde = fpsd.decode().split('\n')[0]
            
            wavf = [wavfz,wavfn,wavfe]
            psd = [psdz,psdn,psde]
        except:
            nodata = 'nodata'
            wavf = ''
            psd = ''
        return render_template('sensor_psd.html',gambar=[wavf,psd],sta=sta,nodata = nodata,ping=resptnt)
    else:
        return render_template('sensor_psd.html', ping=resptnt)


@app.route('/sensor/status', methods=["POST","GET"])
def sensor_stat():
    
    resptnt = os.system('ping -c 1 36.91.152.130')
    if resptnt == 0:
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
        dt = datetime.utcnow()
        yes = (dt - timedelta(days=1))
        yest = yes.strftime('%d%m%y')
        
        fileav='static/availability_'+yest+'.png'
        print('sampee siniiii ####',fileav)
        if not os.path.exists(fileav):
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
        return render_template('sensor_stat.html', ping=resptnt,gambar=[mapf,wavf], data=tabel,fileav=fileav,sta=sta,nodata = nodata)
    else:
        return render_template('sensor_stat.html', ping=resptnt)
    
    #os.system('ls static/waveform/waveform24h'+sta+'*.jpg')


@app.route('/sensor/slinktable', methods=["POST","GET"])
def tabel_slink():
    
    resptnt = os.system('ping -c 1 36.91.152.130')
    if resptnt == 0:
        data = slinktool()
        last_data = data[0]
        today = data[1]
        # stat = status(last_data,today)
        tabel = tabel_slinktool(last_data,today)
        return render_template('slink_table2.html', ping=resptnt, data=tabel)

    else:
        return render_template('slink_table2.html', ping=resptnt)
    
     

@app.route('/sensor/allwaveform', methods=["POST","GET"])
def downloadwaveform():
    if 'user' in session:
        resptnt = os.system('ping -c 1 36.91.152.130')
        if resptnt == 0:
            if request.method == 'GET':
                today = datetime.today()
                today = today.strftime('%d-%m-%Y %H:%M:%S')

                return render_template('download_waveform.html', ping=resptnt, date = [today,today])
            else:

                # try:
                fout = waveform_fdsn()
                return send_file(fout, as_attachment=True, conditional=True, download_name=fout.split('/')[2])
                # except:
                    # today = datetime.today()
                    # today = today.strftime('%d-%m-%Y %H:%M:%S')
                    # return render_template('download_waveform.html',ping=resptnt, date = [today,today])

                # try:
                #     allwaveform()
                #     return send_file('fungsi/waveform/waveform.mseed', as_attachment=True, attachment_filename='waveform.mseed')
                # except:
                #     today = datetime.today()
                #     today = today.strftime('%d-%m-%Y %H:%M:%S')
                #     return render_template('download_waveform.html',ping=resptnt, date = [today,today])
        else:
            return render_template('download_waveform.html',ping=resptnt)

    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))


@app.route('/sensor/waveformbyevent', methods=["POST","GET"])
def waveformbyevent():
    if 'user' in session:
        resptnt = os.system('ping -c 1 36.91.152.130')
        if resptnt == 0:
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
            return render_template('waveformbyevent.html',ping=resptnt, data=parameter_new)
        else:
            return render_template('waveformbyevent.html',ping=resptnt)
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
            return send_file('fungsi/waveform/'+id+'.mseed', as_attachment=True, conditional=True, download_name=id+'.mseed')
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))
    

@app.route('/downloadpga/', methods=["POST"])
def datapga_download():
    if 'user' in session:
        date = request.form['datefilter_pga']
        cur = mysql.connection.cursor()
        datestart = date.split()[0]
        dateend = date.split()[2]
        sql_filter = "SELECT * FROM db_pga WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
        condition = (datestart,dateend)
        # print(condition)
        cur.execute(sql_filter, condition)
        header = [i[0] for i in cur.description]
        print(header)
        tabel = cur.fetchall()
        path = 'fungsi/export/datapga.csv'
        with open(path, 'w') as f:
            f.write(','.join(header) +'\n')
            for row in tabel:
                f.write(','.join(str(r) for r in row) + '\n')
            f.close()

        print(tabel)
        #return Response(generate(), mimetype='text/csv')
        return send_file(path, as_attachment=True, conditional=True, download_name='PGA - '+datestart+'-'+dateend+'.csv')
    else:
        flash("Please, Login First !!")
        return redirect(url_for('login'))
    

@app.route('/downloadqc/', methods=["POST"])
def dataqc_download():
    if 'user' in session:
        date = request.form['datefilter_pga']
        cur = mysql.connection.cursor()
        datestart = date.split()[0]
        dateend = date.split()[2]
        sql_filter = "SELECT `QC ID` FROM db_pga WHERE `Origin Date` BETWEEN %s AND %s ORDER BY `Origin Date`, `Origin Time` ASC"
        condition = (datestart,dateend)
        cur.execute(sql_filter, condition)

        path = 'fungsi/export/arrival_qc.txt'
        list_id = cur.fetchall()
        with open(path,'w', encoding='utf-8') as out:
            for id in list_id:
                ls = glob.glob('fungsi/arrival/qc_arrival/'+str(id[0])+'*')
                ls.sort(key=os.path.getmtime)
                f_qc = ls[len(ls)-1]
                with open(f_qc, 'r', encoding='utf-8') as input_file:
                    out.write(input_file.read())

        return send_file(path, as_attachment=True, conditional=True, download_name='Arrival QC - '+datestart+'-'+dateend+'.txt')
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
                pesan = input.esdx2par(fileinput,opsi_par,info)
                flash("",pesan)
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
        pesan = input.esdx2par(fileinput,opsi_par,info)
        mapping.map_diseminasi()
        flash("",pesan)
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
