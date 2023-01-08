set SIZE=M17.2c
set AXIS=a1f0.5NwsE
set psfile=gmt\peta_diseminasi.ps
set evlat=%1
set evlon=%2
set magfile=%3
set kota_besar_malut=gmt\kota_besar_malut.dat
set kota_malut=gmt\kota_malut.dat
set kota_sulut=gmt\kota_sulutgto.dat
set magnitudo=gmt\mag\%magfile%
set parameter=gmt\parameter.dat


set lebar=1.5
set tinggi=0.9375
for /f "delims=*" %%a in ('gawk "BEGIN {print %evlat%+%tinggi%}" ') do set atas=%%a
for /f "delims=*" %%a in ('gawk "BEGIN {print %evlat%-%tinggi%}" ') do set bawah=%%a
for /f "delims=*" %%a in ('gawk "BEGIN {print %evlon%-%lebar%}" ') do set kiri=%%a
for /f "delims=*" %%a in ('gawk "BEGIN {print %evlon%+%lebar%}" ') do set kanan=%%a
set REGION=%kiri%/%kanan%/%bawah%/%atas%
for /f "delims=*" %%a in ('gawk "BEGIN {print %evlat%-0.8}" ') do set scalelat=%%a
for /f "delims=*" %%a in ('gawk "BEGIN {print %evlon%+1.0}" ') do set scalelon=%%a

echo %evlon% %evlat%>%parameter%
grdimage gmt\map_pgr.nc  -R%REGION% -J%SIZE% -Cgmt\batimetri.cpt -K -V -I+a0+nt0.5 -Y8 -P > %psfile%
psxy -R -JM -W1.0 -Sf0.4i/0.05ilt -Gblack -O -K  gmt\trench.gmt>> %psfile%

gawk "{ print $1,$2,$3}" %parameter% |psxy -R -JM -O -K -Sa0.2i -Wthin,red -Gred>> %psfile%
psxy %parameter% -R -JM -O -K -Sc0.3i -W2,red >> %psfile%
psxy %parameter% -R -JM -O -K -Sc0.6i -W2,red >> %psfile%
psxy %parameter% -R -JM -O -K -Sc0.9i -W2,red >> %psfile%
psxy %kota_malut% -R -JM -O -K -Sc0.1i -G0 >> %psfile%
psxy %kota_besar_malut% -R -JM -O -K -Ss0.17i -W3,red >> %psfile%
psxy %kota_sulut% -R -JM -O -K -Sc0.1i -G0 >> %psfile%
gawk "{ print $1+0.08,$2,$3,$4,$5,$6,$7}" %kota_besar_malut% | pstext -R -JM -O -K >> %psfile%
gawk "{ print $1+0.04,$2,$3-2,$4,$5,$6,$7}" %kota_malut% | pstext -R -JM -O -K >> %psfile%
gawk "{ print $1+0.04,$2,$3-2,$4,$5,$6,$7}" %kota_sulut% | pstext -R -JM -O -K >> %psfile%

psbasemap -J -R%REGION% -B%AXIS% --MAP_LABEL_OFFSET=0.2 --FONT_ANNOT_PRIMARY=9p --FONT_LABEL=11p,Heveltica --MAP_FRAME_TYPE=inside --MAP_FRAME_WIDTH=0.1p -P -K -O -V -Lf%scalelon%/%scalelat%/1/50+lKM  >> %psfile%

pscoast -Dl -R115/135/-5/6.3333333333 -JM3.5c -W0.3,gray40 -Swhite -Ggray40 --MAP_FRAME_TYPE=inside -O -K -V -Blrbt -Y0.1 -X1.1>> %psfile%

echo %kiri% %atas% > kotak
echo %kiri% %bawah% >> kotak
echo %kanan% %bawah% >> kotak
echo %kanan% %atas% >> kotak
echo %kiri% %atas% >> kotak
psxy kotak -J -R -W1,red -O -K >> %psfile%
psxy %parameter% -R -J -O -K -Sa0.2c -Gred >> %psfile%

psimage gmt\template_peta0.png -Dx0/0+w7.5i+r300 -O -X-2 -Y-6.7 -K>> %psfile%
psimage %magnitudo% -Dx0/0+w1.6i+r600 -O -X1.55 -Y2 -K>> %psfile%
gawk "{ print $1,$2,$3}" gmt\param.txt | pstext -R1/10/1/10 -JX3 -F+cTL+f11,Times-Bold,white -P -O -K -Y-0.35 -X6>> %psfile%
gawk "{ print $4,$5}" gmt\param.txt | pstext -R1/10/1/10 -JX3 -F+cTL+f11,Times-Bold,white  -P -O -K -Y-0.45 >> %psfile%
gawk "{ print $6,$7,$8,$9,$10}" gmt\param.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f11,Times-Bold,white  -P -O -Y-3.7 -K -X-0.05 >> %psfile%
gawk "{ print $11,$12}" gmt\param.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f11,Times-Bold,white  -P -O -K -Y-0.1 -X6 >> %psfile%
gawk "{ print $1,$2,$3,$4}" gmt\jarak.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f10,Times-Bold,white  -P -O -K -Y2.25 >> %psfile%
gawk "{ print $13}" gmt\param.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f10,Times-Bold,white  -P -O -Y-0.43>> %psfile%

psconvert %psfile% -TG -A -P -E256
echo DONE