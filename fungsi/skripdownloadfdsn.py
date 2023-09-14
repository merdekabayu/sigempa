from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.signal import PPSD
from obspy import read_inventory
from obspy.imaging.cm import pqlx
from datetime import datetime
from pytictoc import TicToc

# t = TicToc()
# t.tic()
# t.toc()

# client = Client('http://36.91.152.130:8081', user='pgn', password='pgn1234')
client = Client('https://geof.bmkg.go.id/', user='bmkg', password='inatews2303#!3')

dtutc = datetime.utcnow()
tnow = UTCDateTime(dtutc)

sta = "TNTI"
st = client.get_waveforms("*",sta, "00,", "HH*,SH*", tnow-86400, tnow)
print(st)
inv = read_inventory("https://geof.bmkg.go.id/fdsnws/station/1/query?station="+sta+"&level=response&nodata=404")

ppsd = PPSD(st[0].stats, metadata=inv,ppsd_length=600,periode_limits=(0.02,100))
ppsd1 = PPSD(st[1].stats, metadata=inv,ppsd_length=600,periode_limits=(0.02,100))
ppsd2 = PPSD(st[2].stats, metadata=inv,ppsd_length=600,periode_limits=(0.02,100))

ppsd.add(st)
ppsd1.add(st)
ppsd2.add(st)
st[0].plot()
st[1].plot()
st[2].plot()
plt = ppsd.plot(cmap=pqlx, show=True)
plt = ppsd1.plot(cmap=pqlx, show=True)
plt = ppsd2.plot(cmap=pqlx, show=True)
# plt.savefig('psd_'+sta+'_Z.jpg')

