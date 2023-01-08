import datetime
import os
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np

dt = datetime.today()
tt = dt.timetuple()

yes = (dt - timedelta(days=1))
yest = yes.timetuple()
yesterday = yest.tm_yday
namafile = '{0:03}'.format(yesterday)

os.system('rm -r ~/aloptama/var/lib/archive/2022/IA/*/*/*Z*')

os.system('cp ~/seiscomp/var/lib/archive/2022/IA/TNTI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/TNTI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/SANI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/SANI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/OBMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/OBMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/LBMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/LBMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/GHMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/GHMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/PMMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/PMMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/WHMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/WHMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/WBMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/WBMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/JHMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/JHMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/IHMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/IHMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/GLMI/SHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/GLMI/SHZ.D/')
os.system('cp ~/seiscomp/var/lib/archive/2022/IA/MTAI/HHZ.D/*'+namafile+' ~/aloptama/var/lib/archive/2022/IA/MTAI/HHZ.D/')

TNTI,SANI,OBMI,LBMI,GHMI,PMMI,WHMI,WBMI,JHMI,IHMI,GLMI,MTAI=0,0,0,0,0,0,0,0,0,0,0,0
os.system('scardac -d mysql://sysop:sysop@localhost/seiscomp -a aloptama/var/lib/archive --debug 2> availability.txt')

fileinput = 'availability.txt'
file = open(fileinput,'r')
baris = file.readlines()
for i in range(len(baris)):
	baris[i]=baris[i].split()
file.close()

i = 0
while i < len(baris):
	if len(baris[i])>0 and baris[i][0]=='availability':
		sta = (baris[i-9][3].split('.'))[1]
		avper = (baris[i][2])[:-1]
		locals()[sta] = float(avper)
		#print('GHMI', GHMI)
	i = i+1
print('GHMI', GHMI)
print('GLMI', GLMI)
print('IHMI', IHMI)
print('JHMI', JHMI)
print('LBMI', LBMI)
print('MTAI', MTAI)
print('OBMI', OBMI)
print('PMMI', PMMI)
print('SANI', SANI)
print('TNTI', TNTI)
print('WBMI', WBMI)
print('WHMI', WHMI)

date = datetime.strftime(yes, '%d-%m-%Y')
Sta = ['TNTI','SANI','OBMI','LBMI','GHMI','PMMI','WHMI','WBMI','JHMI','IHMI','GLMI','MTAI']
Avper = [TNTI,SANI,OBMI,LBMI,GHMI,PMMI,WHMI,WBMI,JHMI,IHMI,GLMI,MTAI]

width = 0.5
#plt.plot()
plt.figure(figsize=(10, 5)) 
y = np.array(Avper)
colors = plt.cm.jet_r(y/100)
bar = plt.bar(Sta, Avper, width, align='center', color= colors)
plt.title('Data Availability Stasiun InaTEWS di Maluku Utara \nTanggal '+date,weight='bold')
plt.xlabel('Station', weight='bold')
plt.ylabel('Availability (%)', weight='bold')


for p in bar:
   height = p.get_height()
   plt.text(x=p.get_x() + p.get_width() / 2, y=height+1,
      s="{}%".format(height),
      ha='center', size=7, weight='bold')
  

#for i in range(len(Sta)):
#    ax.annotate(str(Avper[i]), xy=(Sta[i],Avper[i]), ha='center', va='bottom')

#plt.show()
plt.savefig('availability.png')
#command = "sshpass -p %s scp -r /home/sysop/availability.png personal@172.21.95.250:/C:/Users/Personal/Desktop/" % ("Ternate97432")
#os.system(command)
		#file.write('#' + tahun.rjust(5)+bulan.rjust(3)+tanggal.rjust(3)+jam.rjust(3)+
		#	menit.rjust(3)+detik.rjust(6)+lintang.rjust(9)+bujur.rjust(10)+depth.rjust(7)+
                #        mag.rjust(6)+ unknown.rjust(5)+ unknown.rjust(5)+rms.rjust(6)+
                #        evnt.rjust(6)+'\n')               
