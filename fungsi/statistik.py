from shapely.geometry import Point, Polygon
from subprocess import run
from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
from dateutil import tz
from shapely.geometry import Point, Polygon


def hitung_chart(par, date_list):
    par = par
    date_list = date_list

    data=[]
    for row in par:
        date=row[1]
        tgl=str(date)
        data += [tgl]
    print('ini jumlah gmp=',str(len(data)))

    felt = []
    for row in par:
        if len(str(row[8])) > 5:
            dirasakan = row[8]
            drs = str(dirasakan)
            felt += [drs]
    
    jml_drskn = len(felt)
    print('ini jumlah dirasakan=',str(jml_drskn))
    
    hist,TGL,hist_tab = [],[],[]
    for dat in date_list:
        tanggal = dat.strftime('%Y-%m-%d')
        jml= data.count(tanggal)
        tgl = dat.strftime('%d-%b-%y')
        TGL += [str(tgl)] 
        hist+= [jml]
        hist_tab +=[[str(tgl),jml]]
    histogram = [TGL,hist]
    #print('#',hist[0][2])
    
    M3,M35,M5=[],[],[]
    D3,D35,D5=[],[],[]
    for row in par:
        if row[6] < 3:
            m3 = str(row[6])
            mag3 = str(m3)
            M3 += [mag3]
        if row[6] >= 3 and row[6] < 5:
            m35 = str(row[6])
            mag35 = str(m35)
            M35 += [mag35]
        if row[6] >= 5:
            m5 = str(row[6])
            mag5 = str(m5)
            M5 += [mag5]
        if row[5] < 60:
            d3 = str(row[5])
            depth3 = str(d3)
            D3 += [depth3]
        if row[5] >= 60 and row[5] < 300:
            d35 = str(row[5])
            depth35 = str(d35)
            D35 += [depth35]
        if row[5] >= 300:
            d5 = str(row[5])
            depth5 = str(d5)
            D5 += [depth5]
    
    print ("M < 3 =" + str(len(M3)) + "," + '\n'+"5 < M < 3 =" + str(len(M35)) + "," + '\n'+"M > 5 =" + str(len(M5)))
    print ("< 60 Km =" + str(len(D3)) + "," + '\n'+"60 - 300 Km =" + str(len(D35)) + "," + '\n'+"> 300 Km =" + str(len(D5)))
    
    i = 0
    mag = []
    dis_mag,TGL = [],[]
    while i < len(par):
        mg = str(par[i][6])
        tgl = (par[i][1]).strftime('%d-%b')
        TGL += [str(tgl)] 
        dis_mag += [mg]
        i += 1
    dis_mag = [TGL,dis_mag]

    drskn = jml_drskn
    jmlgmp = str(len(data))
    
    MAG = [len(M3),len(M35),len(M5)]
    DEPTH = [len(D3),len(D35),len(D5)]
    dis_mag = dis_mag

    return jmlgmp,drskn,histogram,MAG,DEPTH,dis_mag,hist_tab





def hitung_wilayah(par):
    # Create a square
    laut_maluku = [(128.0001,3.5001),
                    (128.0001,3.0001),
                    (127.3001, 2.0001),
                    (126.7499, 0.7501),
                    (126.7499, -1.3301),
                    (123.9999, -1.3301),
                    (123.9999, -0.6001),
                    (125.4001, 1.1501),
                    (126.0001, 3.5001)]

    halbar = [(128.0001,0.1601),
                (126.7499, 0.1601),
                (126.7499, 0.7501),
                (127.3001, 2.0001),
                (128.0001, 1.6001)]

    sulawesi = [(123.9999, -0.6001),
                (125.4001, 1.1501),
                (126.0001, 3.5001),
                (123.9999, 3.5001)]

    halut = [(130.0001, 1.6001),
            (130.0001, 3.5001),
            (128.0001, 3.5001),
            (128.0001, 3.0001),
            (127.3001, 2.0001),
            (128.0001, 1.6001)]

    halsel = [(126.7499, -2.7501),
            (130.0001, -2.7501),
            (130.0001, -1.2001),
            (129.0001, -1.2001),
            (128.3001, 0.1601),
            (126.7499, 0.1601)]

    haltim = [(128.0001, 0.1601),
            (128.3001, 0.1601),
            (129.0001, -1.2001),
            (130.0001, -1.2001),
            (130.0001, 1.6001),
            (128.0001, 1.6001)]

    sula = [(123.9999, -2.7501),
            (126.7499, -2.7501),
            (126.7499, -1.3301),
            (123.9999, -1.3301)]
                
    #p = Point(125.97,3.39)
    Laut_maluku,Sula,Halsel,Haltim,Halbar,Halut,Sulawesi,other = [],[],[],[],[],[],[],[]
    for row in par:
        lat=row[3]
        long=row[4]
        p = Point(long,lat)

        
        if p.within(Polygon(laut_maluku)):
            Laut_maluku += [('lautmaluku')]
        elif p.within(Polygon(sula)):
            Sula += [('sula')]
        elif p.within(Polygon(halsel)):
            Halsel += [('halsel')]
        elif p.within(Polygon(haltim)):
            print('ini haltim ',row[1],row[7])
            Haltim += [('haltim')]
        elif p.within(Polygon(halbar)):
            Halbar += [('halbar')]
        elif p.within(Polygon(halut)):
            Halut += [('halut')]
        elif p.within(Polygon(sulawesi)):
            Sulawesi += [('sulawesi')]

        elif p.touches(Polygon(sula)):
            Sula += [('sula')]
        elif p.touches(Polygon(haltim)):
            Haltim += [('haltim')]
        elif p.touches(Polygon(halsel)):
            Halsel += [('halsel')]
        elif p.touches(Polygon(halut)):
            Halut += [('halut')]
        elif p.touches(Polygon(halbar)):
            Halbar += [('halbar')]
        elif p.touches(Polygon(laut_maluku)):
            Laut_maluku += [('lautmaluku')]
        elif p.touches(Polygon(sulawesi)):
            Sulawesi += [('sulawesi')]
        
        else:
            print(p, ' ada di luar!!!')
            poin = 'ada di luar'
            other += [('other')]
    
    
    hist_wilayah = [len(Laut_maluku),len(Halut),len(Haltim),len(Halbar),len(Halsel),len(Sula),len(Sulawesi),len(other)]
    #garis = [(125,1),(127,3),(125,3)]

    #p = Point(126.01,2)

    #if p.touches(Polygon(garis)):
    #    print('true')
    #else:
    #    print('false')

    return hist_wilayah

