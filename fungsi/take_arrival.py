# Importing libraries
import time
import hashlib
import pickle
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from .esdx_mon import esdx_mon


# setting the URL you want to monitor
url_mni = Request('http://202.90.198.127/esdx/log/manado.php')
url_tnt = Request('https://stageofternate.com/htmltes.html')
url_gto = Request('https://stageofternate.com/htmltes.html')
url_pst = Request('http://202.90.198.127/esdx/log/pusat.php')
url = Request('https://stageofternate.com/htmltes.html')
# to perform a GET request and load the
# content of the website and store it in a var
#htmlstring_mni = urlopen(url_mni).read()
#htmlstring_tnt = urlopen(url_tnt).read()
htmlstring_gto = urlopen(url_gto).read()
#htmlstring_pst = urlopen(url_pst).read()

#pickle.dump( htmlstring_mni, open( 'fungsi/arrival/htmlstring_mni.p', "wb" ) )
#pickle.dump( htmlstring_mni, open( 'fungsi/arrival/htmlstring_tnt.p', "wb" ) )
pickle.dump( htmlstring_gto, open( 'fungsi/arrival/htmlstring_gto.p', "wb" ) )
#pickle.dump( htmlstring_pst, open( 'fungsi/arrival/htmlstring_pst.p', "wb" ) )

print("running")
time.sleep(1)
while True:
    try:
        
        #htmlstring = urlopen(url_mni).read()
        htmlstring_mni = urlopen(url_mni).read()
        htmlstring_tnt = urlopen(url_tnt).read()
        htmlstring_gto = urlopen(url_gto).read()
        htmlstring_pst = urlopen(url_pst).read()
        f_mni = pickle.load( open( 'fungsi/arrival/htmlstring_mni.p', 'rb'))
        f_tnt = pickle.load( open( 'fungsi/arrival/htmlstring_tnt.p', 'rb'))
        f_gto = pickle.load( open( 'fungsi/arrival/htmlstring_gto.p', 'rb'))
        f_pst = pickle.load( open( 'fungsi/arrival/htmlstring_pst.p', 'rb'))
        pst = 'pst'
        mni = 'mni'
        gto = 'gto'
        time.sleep(1)

        #esdx_mon(f_pst,htmlstring_pst,pst)
        
        if f_mni == htmlstring_mni:
            print("esdx manado tidak ada yang berubah !!!!!")
            
        else:
            print("manado changed")

            htmlstring_mni = urlopen(url_mni).read()
            file = pickle.load( open( 'fungsi/arrival/htmlstring_mni.p', 'rb'))
            pickle.dump( htmlstring_mni, open( 'fungsi/arrival/htmlstring_mni.p', "wb" ) )

            soup = BeautifulSoup(requests.get('http://202.90.198.127/esdx/log/manado.php').text, "lxml")
            f = "fungsi/mni_arrival.txt"
            with open(f, "w") as file:
                file.write(str(soup))
                file.close()

            file = open(f,'r')
            baris = file.readlines()
            for i in range(len(baris)):
                baris[i]=baris[i].split()
            file.close()
            i=0
            while i < len(baris):
                if len(baris[i]) > 0 and baris[i][0] == 'Public':
                    id = baris[i][2]
                i +=1
            fout = 'fungsi/arrival/esdx_arrival/mni_'+id+'.txt'
            with open(fout, "w") as file:
                file.write(str(soup))
                file.close()

            
            time.sleep(1)


        if f_pst == htmlstring_pst:
            print("esdx pusat tidak ada yang berubah !!!!!")
        else:
            print("pusat changed")
            soup = BeautifulSoup(requests.get('http://202.90.198.127/esdx/log/pusat.php').text, "lxml")
            f = "fungsi/pst_arrival.txt"
            with open(f, "w") as file:
                file.write(str(soup))
                file.close()

            file = open(f,'r')
            baris = file.readlines()
            for i in range(len(baris)):
                baris[i]=baris[i].split()
            file.close()

            i=0
            id=[]
            while i < len(baris):
                if len(baris[i]) > 0 and baris[i][0] == 'Public':
                    id += [baris[i][2]]
                i +=1
            id = id[0]

            fout = 'fungsi/arrival/esdx_arrival/pst_'+id+'.txt'
            with open(fout, "w") as file:
                file.write(str(soup))
                file.close()

            htmlstring_pst = urlopen(url_pst).read()
            pickle.dump( htmlstring_pst, open( 'fungsi/arrival/htmlstring_pst.p', "wb" ) )
            time.sleep(1)


        if f_gto == htmlstring_gto:
            print("esdx gorontalo tidak ada yang berubah !!!!!")
            continue
        else:
            print("gorontalo changed")
            
            htmlstring_gto = urlopen(url_gto).read()
            file = pickle.load( open( 'fungsi/arrival/htmlstring_gto.p', 'rb'))
            pickle.dump( htmlstring_gto, open( 'fungsi/arrival/htmlstring_gto.p', "wb" ) )

            soup = BeautifulSoup(requests.get('http://202.90.198.127/esdxsta/log/gorontalo.txt').text, "lxml")
            f = "fungsi/gto_arrival.txt"
            with open(f, "w") as file:
                file.write(str(soup))
                file.close()

            file = open(f,'r')
            baris = file.readlines()
            for i in range(len(baris)):
                baris[i]=baris[i].split()
            file.close()
            i=0
            while i < len(baris):
                if len(baris[i]) > 0 and baris[i][0] == 'Public':
                    id = baris[i][2]
                i +=1
            fout = 'fungsi/arrival/esdx_arrival/gto_'+id+'.txt'
            with open(fout, "w") as file:
                file.write(str(soup))
                file.close()

            time.sleep(1)
            continue


    except Exception as e:
        
        print(e)

