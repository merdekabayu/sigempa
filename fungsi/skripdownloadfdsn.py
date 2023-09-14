from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from datetime import datetime
from pytictoc import TicToc

t = TicToc()
t.tic()
# client = Client('http://36.91.152.130:8081', user='pgn', password='pgn1234')
client = Client('https://geof.bmkg.go.id/', user='bmkg', password='inatews2303#!3')

dtutc = datetime.utcnow()
tnow = UTCDateTime(dtutc)

st = client.get_waveforms("IA", "TNTI", "", "SH*", tnow-86400, tnow)
print(st)
t.toc()

