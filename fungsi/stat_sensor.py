from datetime import datetime, timedelta
import fungsi.infografis as ig
from subprocess import PIPE,Popen
import subprocess, os
from subprocess import run
import paramiko
from obspy.core import read
from obspy.core.utcdatetime import UTCDateTime
from obspy.core.stream import Stream
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.switch_backend('agg')



def status(last_data,today):

    #print(last_data)
    MTAI = [2.19802,	128.27585]
    GLMI = [1.8381,	127.7879]
    IHMI = [1.508213,	127.555625]
    JHMI = [1.082067,	127.47828]
    WHMI = [1.0825,	128.132]
    TNTI = [0.7718,	127.3667]
    PMMI = [0.3738,	127.4158]
    WBMI = [0.3393,	127.8708]
    GHMI = [-0.35629,	127.8797]
    LBMI = [-0.6379,	127.5008]
    OBMI = [-1.3413,	127.6444]
    SANI = [-2.049695,	125.988104]

    station =  [['MTAI',128.27585,2.19802],\
        ['GLMI',127.7879,1.8381],\
        ['IHMI',127.555625,1.508213],\
        ['JHMI',127.47828,1.082067],\
        ['WHMI',128.132,1.0825],\
        ['TNTI',127.3667,0.7718],\
        ['PMMI',127.4158,0.3738],\
        ['WBMI',127.8708,0.3393],\
        ['GHMI',127.8797,-0.35629],\
        ['LBMI',127.5008,-0.6379],\
        ['OBMI',127.6444,-1.3413],\
        ['SANI',125.988104,-2.049695]]

    
    fout = open('fungsi/gmt/status.dat','w')
    station_stat=[]
    for sta in last_data:
        print(sta[2])
        if sta[2] <= 900:
            stat = 1
        elif sta[2] > 900 and sta[2] <= 10800:
            stat = 2
        elif sta[2] > 10800 and sta[2] <= 43200:
            stat = 3
        elif sta[2] > 43200 and sta[2] <= 86400:
            stat = 4
        elif sta[2] > 86400:
            stat = 5
        print('ini status',sta[0],stat)

        for st in station:
            if st[0] == sta[0]:
                station_stat += [sta[0],stat]
                fout.write(('%.4f')%(st[1])+'\t'+('%.4f')%(st[2])+'\t'+str(stat)+'\t'+sta[0]+'\n')
    
    fout.close()
    print(today)
    tdy = today.strftime('%d-%b-%Y %H:%M:%S')
    run("fungsi/gmt/sensor_status.sh "+tdy, shell=True)
    

    
    return "ok"
    

def slinktool():

    host = "36.91.152.130"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='sysop', password='bmkg212$', port=2222)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/home/sysop/seiscomp/bin/slinktool -Q localhost | grep IA', get_pty=True)
    output = ssh_stdout.read()
    #print(output)

    with open('fungsi/slinktool.txt','w') as fout:
        fout.write(output.decode("utf-8")+'\n')
        fout.close()

    with open('fungsi/slinktool.txt','r') as fin:
        baris = fin.readlines()
        for i in range(len(baris)):
            baris[i]=baris[i].split()
        fin.close()

    i = 0
    sensor,sensorn,sensore, = [],[],[]
    sensor_sta = []
    while i < len(baris):
        if len(baris[i]) > 0:
            
            sta = baris[i][1]
            locid = baris[i][2]
            if locid == '00' or locid == '01':
                comp = baris[i][3][2:]
            else:
                comp = baris[i][2][2:]

            if sta=='MTAI' or sta=='GLMI' or sta=='IHMI' or sta=='JHMI' or sta=='WHMI' or sta=='TNTI' or sta=='WBMI' or sta=='PMMI' \
            or sta=='GHMI' or sta=='LBMI' or sta=='OBMI' or sta=='SANI':
                sensor += [baris[i]]
                sensor_sta += sta

        i += 1

    if 'GLMI' not in sensor_sta:
        strglmiz = ['IA GLMI     SHZ D 2022/09/30 08:23:43.2250  -  2022/10/02 06:03:54.0000'.split()]
        strglmin = ['IA GLMI     SHZ D 2022/09/30 08:23:43.2250  -  2022/10/02 06:03:54.0000'.split()]
        strglmie = ['IA GLMI     SHZ D 2022/09/30 08:23:43.2250  -  2022/10/02 06:03:54.0000'.split()]
        sensor += strglmiz
        sensor += strglmin
        sensor += strglmie

    #print(sensor)

    last_data=[]
    today = datetime.utcnow()
    TNTI,MTAI,GLMI,IHMI,JHMI,WHMI,WBMI,PMMI,GHMI,LBMI,OBMI,SANI=[],[],[],[],[],[],[],[],[],[],[],[]
    update = []
    for sta in sensor:
        dt = sta[len(sta)-2:]
        name = sta[1]
        name1 = sta[1]
        dtime = dt[0]+' '+dt[1]
        last_dt = datetime.strptime(dtime, '%Y/%m/%d %H:%M:%S.%f')
        delay = (today-last_dt).total_seconds()

        last_data += [[name,last_dt,delay]]
        last_data1 = [[name,last_dt,delay]]

        str1 = name1
        var1 = locals()
        var1[str1] += [last_data1]

        str = name
        var = locals()
        var[str] += [delay]
        print(TNTI)
        
        if len(name) > 2:
            minv = min(name)
            indexmin = name.index(minv)
            update += name1[indexmin]

 
    return update,today



def tabel_slinktool(last_data,today):
    tabel = []
    for dat in last_data:
        delay = dat[2]
        last_dt = dat[1]
        if delay <= 60:
            delay = ('%2d')%((today-last_dt).total_seconds())+' sec'
        elif delay <= 3600:
            delay = ('%2d')%((today-last_dt).total_seconds()/60)+' min'
        elif delay <= 86400:
            delay = ('%2d')%((today-last_dt).total_seconds()/3600)+' hour'
        else:
            delay = ('%2d')%(today-last_dt).days+' days'
        
        last_data = last_dt.strftime('%d-%b-%Y %H:%M:%S')
        #print(dat[0],last_data,delay)
        tabel += [[dat[0],last_data,delay]]
    return tabel

def waveformplot(sta):
    now = datetime.utcnow()
    yes = (now - timedelta(days=1))
    yearn = now.strftime('%Y')
    yeary = yes.strftime('%Y')
    filenow = ('%03d')%(now.timetuple().tm_yday)
    fileyes = ('%03d')%(yes.timetuple().tm_yday)
    catstringnow = "/home/sysop/seiscomp/var/lib/archive/"+yearn+"/IA/"+sta+"/*Z*/*."+filenow
    catstringyes = "/home/sysop/seiscomp/var/lib/archive/"+yeary+"/IA/"+sta+"/*Z*/*."+fileyes
    rangenow = now.strftime('%Y-%m-%d %H:%M:%S')
    rangeyes = yes.strftime('%Y-%m-%d %H:%M:%S')
    stnow = now.strftime('%Y-%m-%dT%H:59:59')
    styes = yes.strftime('%Y-%m-%dT%H:00:00')
    rentang = rangeyes+'~'+rangenow
    
    #command = 'sshpass -p "bmkg212$" ssh sysop@172.21.95.248 cat '+catstringyes+' '+catstringnow+'|scmssort -v -t '+rentang+' -u >'+sta+'.mseed'
    command = "cat "+catstringyes+" "+catstringnow+"|scmssort -v -t '"+rentang+"' -u >'/home/sysop/vps_server/"+sta+".mseed'"
    
    

    with open('fungsi/run_scmssort.sh','w') as f:
        f.write('#!/bin/bash'+'\n'+
                'pwd'+'\n'+
                'export SEISCOMP_ROOT="/home/sysop/seiscomp"'+'\n'+
                'export PATH="/home/sysop/seiscomp/bin:/home/sysop/bin:$PATH"'+'\n'+
                'export LD_LIBRARY_PATH="/home/sysop/seiscomp/lib:$LD_LIBRARY_PATH"'+'\n'+
                'export PYTHONPATH="/home/sysop/seiscomp/lib/python:$PYTHONPATH"'+'\n'+
                'export MANPATH="/home/sysop/seiscomp/share/man:$MANPATH"'+'\n'+
                #'source "/home/sysop/seiscomp/share/shell-completion/seiscomp.bash"'+'\n'+
                command)
        f.close()
    os.system('chmod +x fungsi/run_scmssort.sh')
    command = 'sshpass -p "bmkg212$" scp -P 2222 -r fungsi/run_scmssort.sh sysop@36.91.152.130:vps_server/run_scmssort.sh'
    os.system(command)
    os.system('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 sh vps_server/run_scmssort.sh')
    command = 'sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:vps_server/'+sta+'.mseed fungsi/waveform/'+sta+'.mseed'
    os.system(command)

    
    st = read('fungsi/waveform/'+sta+'.mseed')
    #st = read(Stream)
    st.filter("bandpass", freqmin=0.7, freqmax=5, corners=2)
    st.plot(type="dayplot", interval=60, color=['b'], starttime= UTCDateTime(styes), endtime= UTCDateTime(stnow),
            one_tick_per_line=True, outfile='static/waveform/'+sta+'.jpg', tick_format='%H:%M',size=(1600,1200),dpi=240)
    st.clear()
    #a = st.plot(type="dayplot", interval=60, color=['b'], outfile='static/waveform/TNTI.jpg', show=False)

    #"cat var/lib/archive/2023/IA/TNTI/*Z*/*.005 TNTI/*Z*/*.006|scmssort -v -t '2023-01-05 23:30~2023-01-06 00:45' -u > tes.mseed"   

    return "ok"


def arrivalsc3pst(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt):

    start = datetime.strptime(date1, '%d-%m-%Y %H:%M')
    end = datetime.strptime(date2, '%d-%m-%Y %H:%M')
    

    dt1 = start.strftime('%Y-%m-%d %H:%M')
    dt2 = end.strftime('%Y-%m-%d %H:%M')
    print('ini startend #####',dt1,dt2,date1,date2)

    query = ("SELECT PEvent.publicID, Origin.time_value, Origin.evaluationMode, Origin.quality_usedPhaseCount, Magnitude.magnitude_value, "
            "Magnitude.type, Magnitude.stationCount, Origin.latitude_value, Origin.longitude_value, Origin.depth_value, EventDescription.text "
            "FROM Event, PublicObject AS PEvent, Origin, PublicObject AS POrigin, Magnitude, PublicObject AS PMagnitude, EventDescription "
            "WHERE (Event.type IS NULL OR Event.type='earthquake') AND Event._oid=PEvent._oid AND Origin._oid=POrigin._oid AND Magnitude._oid=PMagnitude._oid AND "
            "Event.preferredOriginID=POrigin.publicID AND Event.preferredMagnitudeID=PMagnitude.publicID AND Event._oid=EventDescription._parent_oid AND EventDescription.type='region name' AND "
            "Origin.evaluationMode = 'manual' AND "
            "Magnitude.magnitude_value >= "+mag1+" AND "
			"Magnitude.magnitude_value <= "+mag2+" AND "
			"Origin.depth_value >= "+depth1+" AND "
            "Origin.depth_value <= "+depth2+" AND "
            "Origin.latitude_value <= "+lat1+" AND "
            "Origin.latitude_value >= "+lat2+" AND "
            "Origin.longitude_value >= "+long1+" AND "
            "Origin.longitude_value <= "+long2+" AND "
            "Origin.time_value >= '"+dt1+"' AND "
            "Origin.time_value <= '"+dt2+"' "
            "ORDER BY Origin.time_value DESC")

        
    host = "36.91.152.130"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='sysop', password='bmkg212$', port=2222)
    
    with open('fungsi/filter_sc3.sql') as input_file:
        list_event ='fungsi/list_event.txt'
        with open(list_event,'w') as fout:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mysql -usysop -psysop -h172.19.3.51 -P3306 -Dseiscomp3 -e"'+query+'"', get_pty=True)
            output = ssh_stdout.read()
            fout.write(output.decode("utf-8")+'\n')

    nama = 'fungsi/Data Arrival-RepoJkt.txt'
    with open(nama,'w') as list_detail:
        with open(list_event,'r') as fin:
            baris = fin.readlines()
            for i in range(len(baris)):
                baris[i]=baris[i].split('|')
            
            i = 3
            while i < len(baris):
                if len(baris[i])>1:
                    #print(baris[i])
                    evid = baris[i][1].split()[0]
                    print(evid)
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/home/sysop/seiscomp/bin/seiscomp exec scbulletin -d mysql://sysop:sysop@172.19.3.51/seiscomp3 -3 -x -E '+evid, get_pty=True)
                    output = ssh_stdout.read()
                    #print(output)
                    list_detail.write(output.decode("utf-8")+'\n\n')
                i += 1
            #print('ini paramikoo',output)
    
    #parameter = cur.fetchall()
    #cur.close()
    return nama


def esdx2pha(finp):
    
    # baca isi file input dan buka file output
    file = open(finp,'r')
    baris = file.readlines()
    for i in range(len(baris)):
        baris[i]=baris[i].split()
    file.close()


    i=0
    while i < len(baris):
        if len(baris[i]) > 0 and baris[i][0] == 'Public':
            id = baris[i][2]
        i +=1
    fileoutput = finp.split('.')[0]+'.pha'
    file = open(fileoutput,'w')

    # catat tiap baris file input ke file output
    i = 0
    event = 0
    while i < len(baris):
        if len(baris[i])>0 and baris[i][0]=='Origin:':
            event = event+1
            evnt = ('%1d')%(event)
            if baris[i+1][0] == 'Public':
                rms = ('%.3f')%float(baris[i+12][2])
                i = i+1
            else:
                i = i
                rms = ('%.3f')%float(baris[i+9][2])
            tahun = (('%2d')%float(baris[i+1][1].split('-')[0]))
            thn = float(tahun)-2000
            thn1 = ('%2d')%(thn)
            bulan = baris[i+1][1].split('-')[1].zfill(1)
            bln = (('%2d')%round(float(bulan),1))
            tanggal = baris[i+1][1].split('-')[2].zfill(1)
            tgl = (('%2d')%round(float(tanggal),1))
            jam = baris[i+2][1].split(':')[0].zfill(2)
            menit = baris[i+2][1].split(':')[1].zfill(2)
            detik = (('%.2f')%float(baris[i+2][1].split(':')[2])).zfill(4)
            lintang = (('%1.4f')%float(baris[i+3][1])).zfill(6)
            if float(lintang)>0:
                    NS = "N"
            else:
                    NS = "S"

            bujur = (('%.4f')%float(baris[i+4][1])).zfill(8)
            depth = ('%.2f')%float(baris[i+5][1])
            unknown = '0.00'
            time0 = float(detik)+float(menit)*60+float(jam)*60*60
        if len(baris[i])>1 and baris[i][1]=='Network':
            numag = baris[i][0]
            m = 1
            #print('sampee sininiiii ######',i)
            while m <= float(numag):
                linemag = baris[i+m]
                if 'preferred' in linemag:
                    mag = baris[i+m][1]
                m += 1
            mag = ('%.2f')%float(mag)
            file.write('#' + tahun.rjust(5)+bulan.rjust(3)+tanggal.rjust(3)+jam.rjust(3)+
                menit.rjust(3)+detik.rjust(6)+lintang.rjust(9)+bujur.rjust(10)+depth.rjust(7)+
                            mag.rjust(6)+ unknown.rjust(5)+ unknown.rjust(5)+rms.rjust(6)+
                            evnt.rjust(6)+'\n')

        if len(baris[i])>0 and baris[i][0]=='sta':
            try:
                j=0
                while j<1:
                    i=i+1
                    try:
                        idSta = baris[i][0]
                        phase = baris[i][4]
                        idP = idSta+phase
                        jam = baris[i][5].split(':')[0]
                        menit = baris[i][5].split(':')[1]
                        detik = baris[i][5].split(':')[2]
                        time1 = float(detik)+float(menit)*60+float(jam)*60*60
                        if (time1-time0) > 0:
                            deltatime = ('%.2f')%(time1-time0)
                        else:
                            deltatime = ('%.2f')%(time1-time0+86400)
                        wgt = baris[i][8]
                        file.write(idSta.rjust(5)+deltatime.rjust(12)+wgt.rjust(8)+phase.rjust(4)+'\n')
                    except:
                        break	
                                
            except:
                break
                    
        i = i+1
    file.close()

    return fileoutput


