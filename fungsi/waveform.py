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
from obspy.signal import PPSD
from obspy import read_inventory
from obspy.imaging.cm import pqlx
from obspy.clients.fdsn import Client
from obspy.taup import TauPyModel
from obspy.geodetics.base import gps2dist_azimuth

#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.switch_backend('agg')



def psdplot(sta):
    # now = datetime.utcnow()
    # yes = (now - timedelta(days=1))
    # yeary = yes.strftime('%Y')
    # fileyes = ('%03d')%(yes.timetuple().tm_yday)
    # fseedz = "seiscomp/var/lib/archive/"+yeary+"/IA/"+sta+"/*Z*/*."+fileyes
    # fseedn = "seiscomp/var/lib/archive/"+yeary+"/IA/"+sta+"/*N*/*."+fileyes
    # fseede = "seiscomp/var/lib/archive/"+yeary+"/IA/"+sta+"/*E*/*."+fileyes
    # command = 'sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:'+fseedz+' fungsi/waveform/psd/'+sta+'_Z.mseed'
    # os.system(command)
    # command = 'sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:'+fseedn+' fungsi/waveform/psd/'+sta+'_N.mseed'
    # os.system(command)
    # command = 'sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:'+fseede+' fungsi/waveform/psd/'+sta+'_E.mseed'
    # os.system(command)

    # st = read('fungsi/waveform/psd/'+sta+'_Z.mseed')
    # st.plot(outfile='static/waveform/wform_'+sta+'_Z.jpg',dpi=100)
    # st1 = read('fungsi/waveform/psd/'+sta+'_N.mseed')
    # st1.plot(outfile='static/waveform/wform_'+sta+'_N.jpg',dpi=100)
    # st2 = read('fungsi/waveform/psd/'+sta+'_E.mseed')
    # st2.plot(outfile='static/waveform/wform_'+sta+'_E.jpg',dpi=100)


    dtutc = datetime.utcnow()
    tnow = UTCDateTime(dtutc)
    client = Client('https://geof.bmkg.go.id/', user='bmkg', password='inatews2303#!3')
    st = client.get_waveforms("*",sta, "00,", "HH*,SH*", tnow-86400, tnow)
    inv = read_inventory("https://geof.bmkg.go.id/fdsnws/station/1/query?station="+sta+"&level=response&nodata=404")
    
    stZ=st.select(component="Z")
    stN=st.select(component="N")
    stE=st.select(component="E")
    stZ.plot(outfile='static/waveform/wform_'+sta+'_Z.jpg',dpi=100)
    stN.plot(outfile='static/waveform/wform_'+sta+'_N.jpg',dpi=100)
    stE.plot(outfile='static/waveform/wform_'+sta+'_E.jpg',dpi=100)

    ppsd = PPSD(stZ[0].stats, metadata=inv,ppsd_length=600,periode_limits=(0.02,100))
    ppsd1 = PPSD(stN[0].stats, metadata=inv,ppsd_length=600,periode_limits=(0.02,100))
    ppsd2 = PPSD(stE[0].stats, metadata=inv,ppsd_length=600,periode_limits=(0.02,100))

    ppsd.add(stZ)
    ppsd1.add(stN)
    ppsd2.add(stE)
    
    plt = ppsd.plot(cmap=pqlx, show=False)
    plt.savefig('static/waveform/psd_'+sta+'_Z.jpg',dpi=240)
    plt = ppsd1.plot(cmap=pqlx, show=False)
    plt.savefig('static/waveform/psd_'+sta+'_N.jpg',dpi=240)
    plt = ppsd2.plot(cmap=pqlx, show=False)
    plt.savefig('static/waveform/psd_'+sta+'_E.jpg',dpi=240)
    # st.clear()

def plotpga(parameter):
    
    os.system('rm -r static/waveform/wpga_*.jpg')
    date = parameter[1]
    time = parameter[2]
    ot=datetime.combine(date, datetime.strptime(str(time), '%H:%M:%S').time())
    t = UTCDateTime(ot)
    source_latitude = parameter[3]
    source_longitude = parameter[4]
    source_depth = parameter[5]

    # station =  ['MTAI',128.27585,2.19802,"HN*","simora"]
    stations =  [['MTAI',128.27585,2.19802,"HN*","simora"],\
        ['IHMI',127.555625,1.508213,"HN*","geof"],\
        ['JHMI',127.47828,1.082067,"HN*","geof"],\
        ['WHMI',128.132,1.0825,"HN*","geof"],\
        ['TNTI',127.3667,0.7718,"BL*","geof"],\
        ['PMMI',127.4158,0.3738,"HN*","geof"],\
        ['WBMI',127.8708,0.3393,"HN*","geof"],\
        ['GHMI',127.8797,-0.35629,"HN*","geof"],\
        ['OBMI',127.6444,-1.3413,"HN*","geof"],\
        ['SANI',125.988104,-2.049695,"SL*","geof"],\
        ['MSHHI',128.425,0.629,"HN*","geof"],\
        ['WSHHI',127.813,0.764,"HN*","geof"],\
        ['TBMUI',124.344,-1.900,"HN*","geof"],\
        ['BDMUI',126.362,1.322,"HN*","geof"],\
        ['MUMUI',125.481,-1.785,"HN*","geof"],\
        ['TMTN',127.3718,0.7699,"AC*","simora"],\
        ['TMUN',127.44569,0.66456,"HN*","simora"],\
        ['HMHN',128.284,0.677,"AC*","simora"],\
        ['LBMI',127.5008,-0.6379,"HN*","simora"],\
        ['GLMI',127.7879,1.8381,"HN*","geof"]]
    
    sta_simora="MTAI,LBMI,TMTN,TMUN,HMHN"
    sta_geof="IHMI,JHMI,WHMI,TNTI,PMMI,WBMI,GHMI,LBMI,OBMI,SANI,WSHHI,MSHHI,TBMUI,BDMUI,MUMUI,TMTN,TMUN,HMHN"
    all_sta = "MTAI,LBMI,TMTN,TMUN,HMHN,IHMI,JHMI,WHMI,TNTI,PMMI,WBMI,GHMI,LBMI,OBMI,SANI,WSHHI,MSHHI,TBMUI,BDMUI,MUMUI,TMTN,TMUN,HMHN"
    # client = Client("http://202.90.199.206:8080")
    client = Client("http://36.91.152.130:8082")
    st0 = client.get_waveforms("IA",all_sta,"*","*", starttime=t-30,endtime= t+210)
    # client = Client("http://36.91.152.130:8082")
    # client = Client('https://geof.bmkg.go.id/', user='bmkg', password='inatews2303#!3')
    # st1 = client.get_waveforms("IA",sta_geof,"*","HN*,BL*,SL*", starttime=t-30,endtime= t+210)
    # st0 += st1

    inv = read_inventory("fungsi/acc_inventory.xml")

    data_pick = []
    for station in stations:
        
        station_latitude = station[2]
        station_longitude = station[1]
        sta = station[0]
        channel = station[3]
        ## Membaca data seismik
        st = st0.select(station=sta,channel=channel)
        # amp_pick = []
        
        if len(st) > 0:
            
            ## TAUP ##
            # theoretical backazimuth and distance
            baz = gps2dist_azimuth(source_latitude, source_longitude, station_latitude, station_longitude)
            TauPy_model = TauPyModel('iasp91')
            arrivals_p = TauPy_model.get_travel_times(distance_in_degree=0.001 * baz[0] / 111.11,
                                                    source_depth_in_km=source_depth,
                                                phase_list=["P","p","Pn","Pg"])
            arrivals_s = TauPy_model.get_travel_times(distance_in_degree=0.001 * baz[0] / 111.11,
                                                    source_depth_in_km=source_depth,
                                                phase_list=["S","s","Sn","Sg"])
            tiemp,tiems = [],[]
            for i in range(0,len(arrivals_p)): tiemp.append(arrivals_p[i].time)
            for ii in range(0,len(arrivals_s)): tiems.append(arrivals_s[ii].time)
            # first arrivals
            arriv_p = min(tiemp)
            arriv_s = min(tiems)
            print(sta,"P-wave arrival: ", arriv_p, "sec")
            print(sta,"S-wave arrival: ", arriv_s, "sec")

            start = t+arriv_p-20
            end = (arriv_s-arriv_p)+arriv_s+20
            end = t+end
            st.trim(starttime=start,endtime=end)

            pre_filt = (0.005, 0.006, 40.0, 45.0)
            st.remove_response(inventory=inv, pre_filt=pre_filt, output="ACC", plot=False)
            
            comp = ["Z","N","E"]
            amp = []
            for c in comp:
                tr1 = st.select(component=c)
                if len(tr1) > 0:
                    tr = st.select(component=c)[0]
                    tr.detrend("spline", order=3, dspline=500)
                    # ampl = max(abs(tr.data))
                    amin = min(tr.data)
                    aplus = max(tr.data)
                    if abs(amin) > aplus:
                        ampl = amin
                    else:
                        ampl = aplus
                    amax = ('%.6f') % float(max(abs(tr.data)))
                    samp = tr.stats.sampling_rate
                    p=(20)*samp
                    s=(20+(arriv_s-arriv_p))*samp

                    fig = plt.figure(figsize=(12, 2),dpi=150)
                    ax = fig.add_subplot()
                    ax.plot(tr.data, 'k')
                    ax.set_title(tr)
                    ax.axvline(x=p, color='b',linewidth=2, linestyle='--', label='P Wave')
                    ax.axvline(x=s, color='c',linewidth=2, linestyle='--', label='S Wave')
                    ax.axhline(y=ampl, linewidth=2, c='r',ls='dashed',label='Amp-max')
                    # Menampilkan legenda
                    ax.legend()
                    # Menampilkan plot
                    # plt.show()
                    fig.savefig('static/waveform/wpga_'+sta+'_'+c+'.jpg',pad_inches=0.1, bbox_inches='tight')
                    amp += c,amax
                else:
                    amp += c,'-'
                    os.system('cp -r static/waveform/nodata.png static/waveform/wpga_'+sta+'_'+c+'.jpg')
            am = [amp[1],amp[3],amp[5]]
            max_value = max(am)
            max_index = am.index(max_value)
            amp.insert(len(amp),amp[max_index*2])
            amp.insert(0,sta)
        else:
            os.system('cp -r static/waveform/nodata.png static/waveform/wpga_'+sta+'_Z.jpg')
            os.system('cp -r static/waveform/nodata.png static/waveform/wpga_'+sta+'_N.jpg')
            os.system('cp -r static/waveform/nodata.png static/waveform/wpga_'+sta+'_E.jpg')
            amp = [sta,'Z','-','N','-','E','-','Z']

        data_pick += [amp]
    print(data_pick)
    return data_pick




    
    # sta="JHMI"
    # t = UTCDateTime(ot)
    # client = Client('https://geof.bmkg.go.id/', user='bmkg', password='inatews2303#!3')
    # client = Client("http://202.90.199.206:8080")
    # st = client.get_waveforms("*",sta, "00,", "HN*", tnow, tnow+240)
    # # inv = read_inventory("https://geof.bmkg.go.id/fdsnws/station/1/query?station="+sta+"&level=response&nodata=404")
    # inv = read_inventory("https://simora.bmkg.go.id/fdsnws/station/1/query?station="+sta+"&level=response&nodata=404")
    



    # stZ=st.select(component="Z")
    # stN=st.select(component="N")
    # stE=st.select(component="E")
    # stZ.plot(outfile='static/waveform/wpga_'+sta+'_Z.jpg',dpi=200,size=(2000,650))
    # stN.plot(outfile='static/waveform/wpga_'+sta+'_N.jpg',dpi=100)
    # stE.plot(outfile='static/waveform/wpga_'+sta+'_E.jpg',dpi=100)



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
    os.system("sshpass -p 'bmkg212$' rsync -arvz -e 'ssh -p2222' --progress --delete sysop@36.91.152.130:vps_server/"+sta+".mseed fungsi/waveform/"+sta+".mseed")

    dtnow = datetime.now()
    namafile = dtnow.strftime("%Y%m%d_%H%M%S")
    os.system('rm -r static/waveform/waveform24h'+sta+'*.jpg')

    st = read('fungsi/waveform/'+sta+'.mseed')
    st.filter("bandpass", freqmin=0.7, freqmax=5, corners=2)
    st.plot(type="dayplot", interval=60, color=['b'], starttime= UTCDateTime(styes), endtime= UTCDateTime(stnow),
            one_tick_per_line=True, outfile='static/waveform/waveform24h'+sta+namafile+'.jpg', tick_format='%H:%M',size=(1600,1200),dpi=240)
    st.clear()
    #a = st.plot(type="dayplot", interval=60, color=['b'], outfile='static/waveform/TNTI.jpg', show=False)

    #"cat var/lib/archive/2023/IA/TNTI/*Z*/*.005 TNTI/*Z*/*.006|scmssort -v -t '2023-01-05 23:30~2023-01-06 00:45' -u > tes.mseed"   

    return "ok"

def waveform_fdsn():
    date1 = request.form['date1']
    date2 = request.form['date2']
    date1 = datetime.strptime(date1, '%d-%m-%Y %H:%M:%S')
    date2 = datetime.strptime(date2, '%d-%m-%Y %H:%M:%S')
    time1 = UTCDateTime(date1)
    time2 = UTCDateTime(date2)
    net = request.form['network']
    loc = request.form['location']
    chn = request.form['channel']
    stations = request.form['fromstalist']
    fout = 'fungsi/waveform/'+date1.strftime('%Y%m%d%H%M%S')+'_'+date2.strftime('%Y%m%d%H%M%S')+'.mseed'
    if net =='':
        net = '*'
    if loc =='':
        loc = '*'
    if chn =='':
        chn = '*'
    if stations == '':
        stations = '*'
    print('########',net,loc,chn)
    download_waveform(time1,time2,stations,fout,net,loc,chn)
    return fout

def download_waveform(time1,time2,sta,fout,network,location,channel):
    client = Client('http://36.91.152.130:8081/', user='sctnt', password='ternate97432')
     
    st = client.get_waveforms(network,sta, location, channel, time1, time2)
    st.write(fout, format='MSEED', encoding='STEIM1')

def allwaveform():
    date1 = request.form['date1']
    date2 = request.form['date2']
    date1 = datetime.strptime(date1, '%d-%m-%Y %H:%M:%S')
    date2 = datetime.strptime(date2, '%d-%m-%Y %H:%M:%S')

    year1 = date1.strftime('%Y')
    year2 = date2.strftime('%Y')
    file1 = ('%03d')%(date1.timetuple().tm_yday)
    file2 = ('%03d')%(date2.timetuple().tm_yday)

    dir1 = subprocess.call('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year1,shell=True)
    dir2 = subprocess.call('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year2,shell=True)

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
    command = 'sshpass -p "bmkg212$" scp -P 2222 -r fungsi/download_waveform.sh sysop@36.91.152.130:vps_server/download_waveform.sh'
    print(command)
    os.system(command)
    print('sampe siniii')
    os.system('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 sh vps_server/download_waveform.sh')

    os.system('sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:vps_server/waveform.mseed fungsi/waveform/waveform.mseed')

    os.system("sshpass -p 'bmkg212$' rsync -arvz -e 'ssh -p2222' --progress --delete sysop@36.91.152.130:vps_server/waveform.mseed fungsi/waveform/waveform.mseed")
    
    return "ok"


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

    dir1 = subprocess.call('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year1,shell=True)
    dir2 = subprocess.call('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 cd /home/sysop/seiscomp/var/lib/archive/'+year2,shell=True)
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
    command = 'sshpass -p "bmkg212$" scp -P 2222 -r fungsi/download_waveformbyevent.sh sysop@36.91.152.130:vps_server/download_waveformbyevent.sh'
    os.system(command)
    os.system('sshpass -p "bmkg212$" ssh -p2222 sysop@36.91.152.130 sh vps_server/download_waveformbyevent.sh')
    #os.system('sshpass -p "bmkg212$" scp -P 2222 -r sysop@36.91.152.130:vps_server/'+id+'.mseed fungsi/waveform/'+id+'.mseed')
    os.system("sshpass -p 'bmkg212$' rsync -arvz -e 'ssh -p2222' --progress --delete sysop@36.91.152.130:vps_server/"+id+".mseed fungsi/waveform/"+id+".mseed")
    #rsync -arvz -e 'ssh -p <port-number>' --progress --delete user@remote-server:/path/to/remote/folder /path/to/local/folder

    
    print(id)
    return id
    

