#!/bin/bash

echo $1
DAY=$(date +%D)
TIME=$(date +%T)
echo "$DAY $TIME" > $1
echo "Day of month, Time of data collection, Wind speed (kph), Visibility (km), Weather, Sky COnditions, Air Temp (C), Dewpoint (C), 6 Hour Max Temp, 6 Hour Min Temp, Relative Humidity (%), Wind Chill (C), Heat Index (C), Alitimeter Pressure (cm), Sea Level (mb), Precipitation 1h r (cm), Precipitation 3hr (cm), Precipitation 6h (cm)" >> $1
echo "INSERT" >> $1
echo "---" >> $1
echo "Incident number, relative time since start, timestamp" >> $1 
