#!/bin/bash

# scrape weather data from first line in table of url = https://forecast.weather.gov/data/obhistory/metric/KSBA.html

URL="https://forecast.weather.gov/data/obhistory/metric/KSBA.html"
RAW=$(curl $URL )
CUT=$(echo $RAW | grep -oP '(?<=</table></form>).*?(?=</th></tr></table>)' | grep -oP '(?<=</th><th).*?(?=Time<br>)')
echo $CUT
echo 
TIME=$(echo $CUT | grep -oP '(?<=align="right">).*?(?=</td><td>)' | cut -d' ' -f1)
NOW=$(echo $TIME | cut -d' ' -f1)
echo "time"
echo $NOW

WC=$(echo $CUT | grep -oP '(?<=align="left">).*?(?=<td>)' | cut -d'>' -f1)
echo $WC
WN=$(echo $WC | cut -d'<' -f1)
echo "weather conditions"
echo $WN

TABLE=$(echo $RAW| grep -oP '(?<=/th>).*?(?=</th>)' )
echo "table"
echo $TABLE 

LINE=$(echo $TABLE | sed -e 's/\ //g' | grep -oP '(?<=<td>).*?(?=/td>)') 
echo 
echo "line"
echo $LINE

DATE=$(echo $LINE | cut -d' ' -f1 | sed -e 's/<//g')
WIND=$(echo $LINE | cut -d' ' -f2 | sed -e 's/<//g')
VIS=$(echo $LINE | cut -d' ' -f3 | sed -e 's/<//g')
SKY_COND=$(echo $LINE | cut -d' ' -f4 | sed -e 's/<//g')
AIR_T=$(echo $LINE | cut -d' ' -f5 | sed -e 's/<//g')
DWPNT=$(echo $LINE | cut -d' ' -f6 | sed -e 's/<//g')
MAX6HR=$(echo $LINE | cut -d' ' -f7 | sed -e 's/<//g')
MIN6HR=$(echo $LINE | cut -d' ' -f8 | sed -e 's/<//g')
HUMID=$(echo $LINE | cut -d' ' -f9 | sed -e 's/<//g')
WIND_CHILL=$(echo $LINE | cut -d' ' -f10 | sed -e 's/<//g')
HEAT_IND=$(echo $LINE | cut -d' ' -f11 | sed -e 's/<//g')
ALT=$(echo $LINE | cut -d' ' -f12 | sed -e 's/<//g')
SEA_LEV=$(echo $LINE | cut -d' ' -f13 | sed -e 's/<//g')
PCPT_1HR=$(echo $LINE | cut -d' ' -f14 | sed -e 's/<//g')
PCPT_3HR=$(echo $LINE | cut -d' ' -f15 | sed -e 's/<//g')
PCPT_6HR=$(echo $LINE | cut -d' ' -f16 | sed -e 's/<//g')

OUT="$DATE, $NOW, $WIND, $VIS, $WN, $SKY_COND, $AIR_T, $DWPNT, $MAX6HR, $MIN6HR, $HUMID, $WIND_CHILL, $HEAT_IND, $ALT, $SEA_LEV, $PCPT_1HR, $PCPT_3HR, $PCPT_6HR"

sed -i "s/INSERT/$OUT/g" $1
