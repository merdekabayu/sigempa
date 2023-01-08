#! /bin/sh
lat=$1
long=$2
mag=$3

lebar=$(echo "$lat - 1"|bc)
panjang=$(echo "$long -1"|bc)

echo "_____ $panjang dan $lebar _____" 
psfile="/home/operasional/flask_app/fungsi/testing.ps"
pscoast -JM15 -R120/130/-5/5 -Gdarkgreen -Swhite -Dh -Ba2f2 -K> $psfile
echo $long $lat | psxy -R120/130/-5/5 -J -Sc0.5c -Gred -O >> $psfile
echo "Ini Magnitude file $mag"
psconvert -A -Tg $psfile
cp /home/operasional/flask_app/fungsi/testing.png /home/operasional/flask_app/static/gempaterkini.png