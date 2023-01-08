from datetime import datetime, timedelta
import fungsi.infografis as ig
from flask import Flask, render_template, request
from flask_mysqldb import MySQL
from subprocess import PIPE,Popen
import subprocess, os
import paramiko


#################################
# Modified by: Bayu Merdeka TFN #
#################################
def arrival2spk(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt):

    
    chart = ig.infografis_parfilter(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt)
    par = chart[0]

    list_id=[]
    for row in par:
        list_id += [row[0]]
    #print(list_id)
    #print(format,source)
    nama = 'fungsi/export/Data Arrival-SPK.txt'
    fout = open(nama,'w')
    for id in list_id:
        eid = id.split('-')[1]
        sta = id.split('-')[0]

        if eid[:3] == 'bmg' or eid[:4] == 'bmkg':
            try:
                if sta == 'MNI':
                    with open('arrival/esdx_arrival/mni_'+eid+'.txt','r') as f:
                        isi = f.read()
                    arr = isi.split('<pre>')[1].split('</pre>')[0]
                    fout.write(arr+'\n\n')
                elif sta == 'PGN':
                    with open('arrival/esdx_arrival/pst_'+eid+'.txt','r') as f:
                        isi = f.read()
                    arr = isi.split('<pre>')[1].split('</pre>')[0]
                    fout.write(arr+'\n\n')
                elif sta == 'AAI':
                    with open('arrival/esdx_arrival/aai_'+eid+'.txt','r') as f:
                        isi = f.read()
                    arr = isi.split('<pre>')[1].split('</pre>')[0]
                    fout.write(arr+'\n\n')
                elif sta == 'GTO':
                    with open('arrival/esdx_arrival/gto_'+eid+'.txt','r') as f:
                        isi = f.read()
                    arr = isi.split('<p>')[1].split('</p>')[0]
                    fout.write(arr+'\n\n')
                elif sta == 'TNT':
                    print('ini id ev #############', id)
                    with open('arrival/esdx_arrival/tnt_'+eid+'.txt','r') as f:
                        isi = f.read()
                    arr = isi.split('<p>')[1].split('</p>')[0]
                    fout.write(arr+'\n\n')
                f.close()
            except:
                print(eid,'data arrival kosong !!!')
        else:
            print(eid,'data arrival kosong !!!')
    fout.close()

    return nama


def arrivalsc4tnt(date1,date2,depth1,depth2,mag1,mag2,lat1,lat2,long1,long2,felt):

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



    with open('fungsi/filter_sc3.sql','w') as sql:
        sql.write(query)
        sql.close()
    
    with open('fungsi/filter_sc3.sql') as input_file:
        list_event ='fungsi/list_event.txt'
        with open(list_event,'w') as fout:
            result = subprocess.run(['mysql', '-h172.21.95.248', '-usysop', '-psysop', '-P33066', '-Dseiscomp'], stdin=input_file, stdout=fout, stderr=PIPE)
            print(result)
    nama = 'fungsi/Data Arrival-SC4.txt'
    with open(nama,'w') as list_detail:
        with open(list_event,'r') as fin:
            baris = fin.readlines()
            for i in range(len(baris)):
                baris[i]=baris[i].split()
            
            host = "172.21.95.248"
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username='sysop', password='bmkg212$', port=2222)

            i = 1
            evid = []
            while i < len(baris):
                evid = baris[i][0]
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('/home/sysop/seiscomp/bin/seiscomp exec scbulletin -3 -x -E '+evid, get_pty=True)
                output = ssh_stdout.read()
                i += 1
                list_detail.write(output.decode("utf-8")+'\n\n')
            #print('ini paramikoo',output)
    
    #parameter = cur.fetchall()
    #cur.close()
    return nama


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

        
    host = "172.21.95.248"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username='sysop', password='bmkg212$', port=22)
    
    with open('fungsi/filter_sc3.sql') as input_file:
        list_event ='fungsi/list_event.txt'
        with open(list_event,'w') as fout:
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('mysql -usysop -psysop -h172.19.3.51 -P33066 -Dseiscomp3 -e"'+query+'"', get_pty=True)
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


