from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
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
    command = 'sshpass -p "bmkg212$" scp -p 2222 -r fungsi/run_scmssort.sh sysop@36.91.152.130:vps_server/run_scmssort.sh'
    os.system(command)
    os.system('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 sh vps_server/run_scmssort.sh')
    command = 'sshpass -p "bmkg212$" scp -p 2222 -r sysop@36.91.152.130:vps_server/'+sta+'.mseed fungsi/waveform/'+sta+'.mseed'
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


def allwaveform():
    date1 = request.form['date1']
    date2 = request.form['date2']
    date1 = datetime.strptime(date1, '%d-%m-%Y %H:%M:%S')
    date2 = datetime.strptime(date2, '%d-%m-%Y %H:%M:%S')

    year1 = date1.strftime('%Y')
    year2 = date2.strftime('%Y')
    file1 = ('%03d')%(date1.timetuple().tm_yday)
    file2 = ('%03d')%(date2.timetuple().tm_yday)

    dir1 = subprocess.call('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year1,shell=True)
    dir2 = subprocess.call('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year2,shell=True)

    if dir1 != 1:
        catstring1 = "/home/sysop/seiscomp/var/lib/archive/"+year1+"/*/*/*/*."+file1
    else:
        catstring1 = "/media/sysop/BACKUP-TNT/WAVEFORM-SEISCOMP/"+year1+"/*/*/*/*."+file1
    
    if dir2 != 1:
        catstring2 = "/home/sysop/seiscomp/var/lib/archive/"+year2+"/*/*/*/*."+file2
    else:
        catstring2 = "/media/sysop/BACKUP-TNT/WAVEFORM-SEISCOMP/"+year2+"/*/*/*/*."+file2

    range1 = date1.strftime('%Y-%m-%d %H:%M:%S')
    range2 = date2.strftime('%Y-%m-%d %H:%M:%S')
    rentang = range1+'~'+range2

    command = "cat "+catstring1+" "+catstring2+"|scmssort -v -t '"+rentang+"' -u > '/home/sysop/vps_server/waveform.mseed'"

    with open('fungsi/download_waveform.sh','w') as f:
        f.write('#!/bin/bash'+'\n'+
                'export SEISCOMP_ROOT="/home/sysop/seiscomp"'+'\n'+
                'export PATH="/home/sysop/seiscomp/bin:/home/sysop/bin:$PATH"'+'\n'+
                'export LD_LIBRARY_PATH="/home/sysop/seiscomp/lib:$LD_LIBRARY_PATH"'+'\n'+
                'export PYTHONPATH="/home/sysop/seiscomp/lib/python:$PYTHONPATH"'+'\n'+
                'export MANPATH="/home/sysop/seiscomp/share/man:$MANPATH"'+'\n'+
                command)
        f.close()
    os.system('chmod +x fungsi/download_waveform.sh')
    command = 'sshpass -p "bmkg212$" scp -p 2222 -r fungsi/download_waveform.sh sysop@36.91.152.130:vps_server/download_waveform.sh'
    print(command)
    os.system(command)
    print('sampe siniii')
    os.system('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 sh vps_server/download_waveform.sh')

    os.system('sshpass -p "bmkg212$" scp -p 2222 -r sysop@36.91.152.130:vps_server/waveform.mseed fungsi/waveform/waveform.mseed')
    
    return send_file('fungsi/waveform/waveform.mseed', as_attachment=True, attachment_filename='waveform.mseed')


def down_waveformbyevent():
    otmin = request.form['otmin']
    otplus = request.form['otplus']
    id = request.form['id']
    date = request.form['date']
    time = request.form['time']
    fromstalist = request.form['fromstalist']
    arrivalcheck = request.form.getlist('arrivalcheck')
    archeck = len(arrivalcheck)
    dataarrival = request.form['dataarrival']

    dt = datetime.strptime(date+' '+time,'%Y-%m-%d %H:%M:%S')
    date1 = dt - timedelta(minutes=float(otmin))
    date2 = dt + timedelta(minutes=float(otplus))

    year1 = date1.strftime('%Y')
    year2 = date2.strftime('%Y')
    file1 = ('%03d')%(date1.timetuple().tm_yday)
    file2 = ('%03d')%(date2.timetuple().tm_yday)

    range1 = date1.strftime('%Y-%m-%d %H:%M:%S')
    range2 = date2.strftime('%Y-%m-%d %H:%M:%S')
    rentang = range1+'~'+range2

    dir1 = subprocess.call('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year1,shell=True)
    dir2 = subprocess.call('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year2,shell=True)
    if dir1 != 1:
        dirwave1 = "/home/sysop/seiscomp/var/lib/archive/"
    else:
        dirwave1 = "/media/sysop/BACKUP-TNT/WAVEFORM-SEISCOMP/"
    
    if dir2 != 1:
        dirwave2 = "/home/sysop/seiscomp/var/lib/archive/"
    else:
        dirwave2 = "/media/sysop/BACKUP-TNT/WAVEFORM-SEISCOMP/"


    pathdataarrival = 'fungsi/arrival/esdx_arrival/'+dataarrival
    if os.path.exists(pathdataarrival) and archeck == 1:
        file = open(pathdataarrival,'r')
        baris = file.readlines()
        for i in range(len(baris)):
            baris[i]=baris[i].split()
        file.close()

        i = 0
        stalist = []
        while i < len(baris):
            if len(baris[i])>0 and baris[i][0]=='sta':
                try:
                    j=0
                    
                    while j<1:
                        i=i+1
                        try:
                            phase = baris[i][4]
                            if phase == 'P':
                                idStaP = baris[i][0]
                                net = baris[i][1]
                                stalist += [(idStaP,net)]
                                
                            if phase == 'S':
                                idStaS = baris[i][0]
                                if idStaP != idStaS:
                                    net = baris[i][1]
                                    stalist += [(idStaS,net)]
                        except:
                            break	    
                except:
                    break
            i = i+1


        if file1 !=  file2:
            catstring_list = ""
            for sta in stalist:
                catstring_list += dirwave1+year1+"/"+sta[1]+"/"+sta[0]+"/*/*."+file1+" "
            for sta in stalist:
                catstring_list += dirwave2+year2+"/"+sta[1]+"/"+sta[0]+"/*/*."+file2+" "
        else:
            catstring_list = ""
            for sta in stalist:
                catstring_list += dirwave1+year1+"/"+sta[1]+"/"+sta[0]+"/*/*."+file1+" "
                
        command = "cat "+catstring_list+"| scmssort -v -t '"+rentang+"' -u > '/home/sysop/vps_server/"+id+".mseed'"
    

    if archeck == 0:
        if fromstalist == '*':
            if file1 !=  file2:
                catstring_list = ""
                catstring_list += dirwave1+year1+"/*/*/*/*."+file1+" "
                catstring_list += dirwave2+year2+"/*/*/*/*."+file2+" "
            else:
                catstring_list = ""
                catstring_list += dirwave1+year1+"/*/*/*/*."+file1+" "

            
            
        else:
            stalist = fromstalist.split(',')
            if file1 !=  file2:
                catstring_list = ""
                for sta in stalist:
                    catstring_list += dirwave1+year1+"/*/"+sta+"/*/*."+file1+" "
                for sta in stalist:
                    catstring_list += dirwave2+year2+"/*/"+sta+"/*/*."+file2+" "
            else:
                catstring_list = ""
                for sta in stalist:
                    catstring_list += dirwave1+year1+"/*/"+sta+"/*/*."+file1+" "
        
        command = "cat "+catstring_list+"| scmssort -v -t '"+rentang+"' -u > '/home/sysop/vps_server/"+id+".mseed'"
        


    with open('fungsi/download_waveformbyevent.sh','w') as f:
        f.write('#!/bin/bash'+'\n'+
                'export SEISCOMP_ROOT="/home/sysop/seiscomp"'+'\n'+
                'export PATH="/home/sysop/seiscomp/bin:/home/sysop/bin:$PATH"'+'\n'+
                'export LD_LIBRARY_PATH="/home/sysop/seiscomp/lib:$LD_LIBRARY_PATH"'+'\n'+
                'export PYTHONPATH="/home/sysop/seiscomp/lib/python:$PYTHONPATH"'+'\n'+
                'export MANPATH="/home/sysop/seiscomp/share/man:$MANPATH"'+'\n'+
                command)
        f.close()
    os.system('chmod +x fungsi/download_waveformbyevent.sh')
    command = 'sshpass -p "bmkg212$" scp -p 2222 -r fungsi/download_waveformbyevent.sh sysop@36.91.152.130:vps_server/download_waveformbyevent.sh'
    os.system(command)
    os.system('sshpass -p "bmkg212$" ssh -p 2222 sysop@36.91.152.130 sh vps_server/download_waveformbyevent.sh')
    os.system('sshpass -p "bmkg212$" scp -p 2222 -r sysop@36.91.152.130:vps_server/'+id+'.mseed fungsi/waveform/'+id+'.mseed')

    
    print(id)
    return id
    

