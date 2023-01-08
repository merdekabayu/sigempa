import time
import hashlib
import pickle
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from datetime import datetime
import requests



def esdx_mon(soup,soup_update,pst):

    if f == htmlstring_pst:
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
        file = pickle.load( open( 'fungsi/arrival/htmlstring_pst.p', 'rb'))
        pickle.dump( htmlstring_pst, open( 'fungsi/arrival/htmlstring_pst.p', "wb" ) )
        time.sleep(1)

    return 'ok'