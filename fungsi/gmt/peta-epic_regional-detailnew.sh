#! /bin/sh

SIZE="M17.38c"
AXIS="a2f1NwsE"
namafile = $9
psfile="fungsi/gmt/$9.ps"
evlat=$1
evlon=$2
magfile=$3
skala=$4
kiri=$5
kanan=$6
bawah=$7
atas=$8
REGION=$kiri/$kanan/$bawah/$atas
kota_besar_malut="fungsi/gmt/kota_besar_malut.dat"
kota_malut="fungsi/gmt/kota_malut.dat"
kota_sulut="fungsi/gmt/kota_sulutgto.dat"
parameter="fungsi/gmt/parameter.dat"
magnitudo="fungsi/gmt/mag_new/$magfile"

#echo %evlon% %evlat% > %parameter%
gmt grdimage fungsi/gmt/indo.nc -R$REGION -J$SIZE -Cfungsi/gmt/batimetri.cpt -K -V -I+a0+nt0.5 -Y8 -P > $psfile
gmt psxy -R -JM -W1.0 -Sf0.4i/0.05ilt -Gblack -O -K  fungsi/gmt/trench.gmt>> $psfile

echo $evlon $evlat | gmt psxy -R -JM -O -K -Sa0.2i -Wthin,red -Gred>> $psfile
echo $evlon $evlat | gmt psxy -R -JM -O -K -Sc0.3i -W2,red >> $psfile
echo $evlon $evlat | gmt psxy -R -JM -O -K -Sc0.6i -W2,red >> $psfile
echo $evlon $evlat | gmt psxy -R -JM -O -K -Sc0.9i -W2,red >> $psfile
gmt psxy $kota_malut -R -JM -O -K -Sc0.1i -G0 >> $psfile
gmt psxy $kota_sulut -R -JM -O -K -Sc0.1i -G0 >> $psfile
gmt psxy $kota_besar_malut -R -JM -O -K -Ss0.17i -W3,red >> $psfile
awk '{ print $1+0.08,$2,$3,$4,$5,$6,$7}' $kota_besar_malut | gmt pstext -R -JM -O -K >> $psfile
awk '{ print $1+0.06,$2,$3-4,$4,$5,$6,$7}' $kota_malut | gmt pstext -R -JM -O -K >> $psfile
awk '{ print $1+0.06,$2,$3-4,$4,$5,$6,$7}' $kota_sulut | gmt pstext -R -JM -O -K >> $psfile
#awk '{print $1+0.12, $2, BL, $14}' tahun_focal.txt |

gmt psbasemap -J -R$REGION -B$AXIS --MAP_LABEL_OFFSET=0.2 --FONT_ANNOT_PRIMARY=9p --FONT_LABEL=11p,Heveltica --MAP_FRAME_TYPE=inside --MAP_FRAME_WIDTH=0.1p -P -K -O -V -Lf$skala/1/100+lKM  >> $psfile

gmt pscoast -Dl -R111/141/-10/7 -JM3.5c -W0.3,gray40 -Swhite -Ggray40 --MAP_FRAME_TYPE=inside -O -K -V -Blrbt -Y0.1 -X1.1>> $psfile

gmt psxy -J -R -W1,red -O -K <<EOF>> $psfile
$kiri $atas
$kiri $bawah
$kanan $bawah
$kanan $atas
$kiri $atas
EOF

echo $evlon $evlat | gmt psxy -R -J -O -K -Sa0.2c -Gred >> $psfile
gmt psimage fungsi/gmt/template_map.png -Dx0/0+w7.51i+r300 -O -X-1.95 -Y-7.42 -K>> $psfile
gmt psimage $magnitudo -Dx0/0+w1.63i+r600 -O -X2.38 -Y2.62 -K>> $psfile
awk '{ print $1,$2,$3}' fungsi/gmt/param.txt | gmt pstext -R1/10/1/10 -JX4 -F+cTL+f9.5,Bookman-Demi,white -P -O -K -Y-0.92 -X5.97>> $psfile
awk '{ print $4,$5}' fungsi/gmt/param.txt | gmt pstext -R1/10/1/10 -JX4 -F+cTL+f9.5,Bookman-Demi,white  -P -O -K -Y-0.45 >> $psfile
awk '{ print $6,$7,$8,$9,$10}' fungsi/gmt/param.txt | gmt pstext -R1/20/1/10 -JX5 -F+cTL+f9.3,Bookman-Demi,white  -P -O -X-0.07 -Y-2.9  -K  >> $psfile
awk '{ print $11,$12}' fungsi/gmt/param.txt | gmt pstext -R1/20/1/10 -JX5 -F+cTL+f9.5,Bookman-Demi,white  -P -O -K -X5.27 >> $psfile
awk '{ print $1,$2,$3,$4}' fungsi/gmt/jarak.txt | gmt pstext -R1/20/1/10 -JX5 -F+cTL+f9.5,Bookman-Demi,white  -P -O -K -Y2.34 >> $psfile
awk '{ print $13}' fungsi/gmt/param.txt | gmt pstext -R1/20/1/10 -JX5 -F+cTL+f9.2,Bookman-Demi,white  -P -O -Y-0.47 -K>> $psfile
gmt pstext fungsi/gmt/info.txt -R1/20/1/10 -JX7 -F+cTL+f9.2,Bookman-Demi,white  -P -O -Y-5.02 -X-4.7>> $psfile
gmt psconvert $psfile -TG -A -P -E256

cp fungsi/gmt/$9.png static/map-detail/$9.png
#echo "Halo disini nilai R = $R"
#pwd

#lat=$1
#long=$2
#mag=$3
#psfile="/home/operasional/flask_app/fungsi/testing.ps"
#pscoast -JM15 -R120/130/-5/5 -Gdarkgreen -Swhite -Dh -Ba2f2 -K> $psfile
#echo $long $lat | psxy -R120/130/-5/5 -J -Sc0.5c -Gred -O >> $psfile
#echo "Ini Magnitude file $mag"
#psconvert -A -Tg $psfile
#rm -r static/peta_diseminasi.png
#cp -r fungsi/gmt/peta_diseminasi.png static/peta_diseminasi.png