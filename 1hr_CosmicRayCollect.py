#!/usr/bin/env python3

import scipy.stats as stats
import numpy  as  np
import sys
import os
import subprocess
from threading import Thread
from multiprocessing import Process, Pipe
import _thread
import RPi.GPIO as GPIO
import time
import datetime
import sys

### Configure
st = time.perf_counter()
WaitToCollect = 60 # start at 59 minute
CollectTime = 60*60 # one hour
ParentDir = "02-21-21" #UPDATE_ParentDir
path = "/home/pi/Desktop/CosmicRayDetection/center/"
DataPath = path + ParentDir + "/"

### Functions
def CheckDir(f, ff):
	i = 2				# format for f should be : NAME_n.txt with n = 1, 2, 3.....
	while True:
		try:
			ls = subprocess.check_output(['ls ' + path + "/" + f + " >/dev/null 2>&1"], shell = True)
			f = eval(ff)
			i = i + 1
		except:
			break		
	out = str(path + "/" + f)
	exp = str(i - 1)
	return out, exp

def NameRun():
	d = datetime.datetime.now()
	M = d.strftime("%m")
	D = d.strftime("%d")
	H = str(int(float(d.hour) + 1)) 
	ID = M+D+"_Hour" + H 
	return ID

def TimeOut(st, duration, RawDat, child_conn):
	print(time.perf_counter() - st)
	time.sleep(duration - (time.perf_counter() - st))	# set timeout for operations defined in this class
	print("ending program", time.perf_counter() - st)
	done=True
	child_conn.close()
	RawDat.close() # close df

def CollectData(st, child_conn, RawDat):
	count = 0
	to = Thread(target = TimeOut, args=(st, CollectTime, RawDat, child_conn,)) # i want to collect data in precise time window
	to.setDaemon(True)
	to.start() # set timeout 
	while done==False:
		try:
			if GPIO.input(37)==1:
				count = count + 1
				currentTime = datetime.datetime.now()
				line = str(count) + ", " + str(time.perf_counter() - st) + ", " + str(currentTime) + "\n"
				RawDat.write(line)
				while GPIO.input(37)==1:
					time.sleep(0.00001)
		except: # timeout kicked in during collection 
			print("Last attempt to send data: t = " + str(time.perf_counter() - st))
			to.join()
			os._exit(0)

# Setup Raw Data file
ID = NameRun()
OutDir = DataPath + "/" + ID
subprocess.Popen(["mkdir " + OutDir], shell=True)
subprocess.check_output(["ls " + OutDir], shell=True)
RawDat = OutDir + "/Raw.csv"
print(RawDat)

subprocess.check_output([path + "/StartDAQ.sh " + RawDat], shell=True) # get most recent weather data
print("Got weather data")

# get ready for data acq
WriteRaw = open(RawDat, 'a+')

GPIO.setmode(GPIO.BOARD)
GPIO.setup(37,GPIO.IN)

global done # flag 
done=False

# Setup DAQ as child process so it can be interrupted as soon as DAQ time is up; avoid duplicate data points
parent_conn, child_conn = Pipe() # multiprocessing to avoid timing issues

# wait until exact time to start. This is so i can start the initialization ahead of time and be ready to get precise time bins.
while time.perf_counter() - st <= WaitToCollect: # wait from initialization to start DAQ 
    pass
# start data collection as child process
DAQ_st = time.perf_counter()
GetData = Process(target = CollectData, args = (DAQ_st, child_conn, WriteRaw,)) # Data collection as child process

print(DAQ_st)
GetData.start()
# join when done 
GetData.join()
print(time.perf_counter() - DAQ_st)
print("proceed")

### Add weather to df header 

subprocess.check_output([path + "/AddWeather.sh " + RawDat + " > /dev/null"], shell = True)

### Process data


def ReadFile(infile):
    read = open(infile, 'r')
    lines = read.readlines()
    read.close()
    return lines

raw = ReadFile(RawDat)
print(raw)
event_rt = []
for i in range(7, len(raw)):
    temp = raw[i].split(', ')
    print(temp)
    event_rt.append(float(temp[1])/60)


EPM = [] # events per minute
minutes = 0
count = 0
print(event_rt)
for i in range(len(event_rt)):
    if event_rt[i] - minutes < 1:
        count = count + 1
    else:
        minutes = minutes + 1
        EPM.append(count)
        count = 1
EPM.append(count) # last unfill bin 

# make header for new df for processed data 
ProcDat = OutDir + "/EventsPerMin.csv"
subprocess.Popen(["head -4 " + RawDat + " > " + ProcDat], shell=True)
subprocess.check_output(["ls > /dev/null"], shell = True)

#write out events per minute
WriteEPM = open(ProcDat, 'a+')
WriteEPM.write("Minute since start, Events per minute\n")

for i in range(len(EPM)):
    print(EPM[i])
    WriteEPM.write(str(i+1) + ", " + str(EPM[i]) + "\n")
WriteEPM.close()

# Add to total file

EnvCond = raw[2].strip()

avg = stats.tmean(EPM)
std = stats.tstd(EPM)
var = stats.tvar(EPM)
rng = max(EPM) - min(EPM)

TotalDat = path + "/TotalOverTime.csv"
WriteTotal = open(TotalDat, 'a+')
DataSummary = str(avg) + ", " + str(std) + ", " + str(var) + ", " + str(rng)
WriteTotal.write("--- " +  str(ID) + " --- DATA: " + DataSummary + " --- CONDITIONS: " + EnvCond + "\n")
WriteTotal.close()
