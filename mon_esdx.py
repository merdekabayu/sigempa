# Importing libraries
import time
from bs4 import BeautifulSoup
import requests
import filecmp


print("running")
while True:
    try:

        def monitor(url,par):
            f = "/root/sigempa_v2/sigempa/fungsi/arrival/"+par+".txt"
            f_new = "/root/sigempa_v2/sigempa/fungsi/arrival/"+par+"_new.txt"
            soup = BeautifulSoup(requests.get(url).text, "lxml")
            with open(f_new, "w") as file:
                file.write(str(soup))
                file.close()

            if filecmp.cmp(f,f_new):
                #print(f,'no change')
                pass
                
            else:
                #print(f,'change')
                soup = BeautifulSoup(requests.get(url).text, "lxml")
                
                with open(f, "w") as file:
                    file.write(str(soup))
                    file.close()
                
                file = open(f,'r')
                baris = file.readlines()
                for i in range(len(baris)):
                    baris[i]=baris[i].split()
                file.close()
                i=0
                id = []
                while i < len(baris):
                    if len(baris[i]) > 0 and baris[i][0] == 'Public':
                        id += [baris[i][2]]
                    i +=1
                id = id[0]
                fout = '/root/sigempa_v2/sigempa/fungsi/arrival/esdx_arrival/'+par+'_'+id+'.txt'
                with open(fout, "w") as file:
                    file.write(str(soup))
                    file.close()
                
        
        par = 'pst'
        url = 'http://202.90.198.127/esdx/log/pusat.php'
        #url = 'https://stageofternate.com/pst.html'
        monitor(url,par)
        par = 'mni'
        url = 'http://202.90.198.127/esdx/log/manado.php'
        #url = 'https://stageofternate.com/mni.html'
        monitor(url,par)
        par = 'gto'
        url = 'http://202.90.198.127/esdxsta/log/gorontalo.txt'
        #url = 'https://stageofternate.com/gto.html'
        monitor(url,par)
        par = 'tnt'
        url = 'http://202.90.198.127/esdxsta/log/ternate.txt'
        #url = 'https://stageofternate.com/tnt.html'
        monitor(url,par)
        par = 'aai'
        url = 'http://202.90.198.127/esdx/log/ambon.php'
        #url = 'https://stageofternate.com/tnt.html'
        monitor(url,par)
        time.sleep(300)
        

    except Exception as e:
        print(e)

