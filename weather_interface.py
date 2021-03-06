#! /usr/bin/python

"""
weather_interface.py
This program is designed to read in data from an arduino.
Specifically this is program interfaces to the arduino on the
MRO weather station.  Functionality includes reading the temperature,
humidity, pressure and light levels from the breakout board.
Wind speed and direction, along with rainfall,
are detected on external sensors.
TODO:
finish interface
Usage:
Options:
"""

__author__ = ["Matt Armstrong"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Matt Armstrong"
__email__ = "jmarmstr@uw.edu"
__status__ = "Developement"

import serial
import time
import datetime
import os
import csv
import math
import requests

class WeatherInterface():
    def __init__(self):
	self.serPort = '/dev/ttyACM0'
        self.dictlength = 16        #Number of lines from serial
        self.logfile = '/home/matt/WeatherStation/logs/'+datetime.datetime.now().strftime("%Y%m%d")+"-weather.txt"
        #self.logfile = '/weather.txt'
	self.WU_count = 0	    #Delay counter for WU upload
	self.runStart = datetime.datetime.now()

    def log(self):
    	"""
    	Check the serial port for data
    	and write any data with a timestamp
    	to the savefile
    	"""
    	data = ser.readline()
    	f = open(savefile, 'a')
    	f.write(str(time.strftime("%Y%m%d-%H:%M:%S"))+","+str(data))
    	f.close()

    def openPort(self):
        """ open the serial port for communication with the arduino, using 9600 baud"""
        self.ser=serial.Serial(self.serPort, 9600)
        self.readSer()
        return

    def closePort(self):
        """ close the serial port connection to the arduino"""
        self.ser.close()
        return

    def readSer(self):
        """ Read in the arduino output, parse, and return something useful
        Arguments:
            None
        Returns:
            s (string): parsed serial output
        """
        s = self.ser.readline().rstrip("\n").rstrip("\r")
	#print s
        return s

    def serOut(self, status, filename):
        directory = filename
        f_out = open(directory,'a')
        #print str(directory)
        f_out.write(str(status)+'\n')
        f_out.close()

    def sortOutput(self, serDat = None):
        weatherDat = {}
        rawDat = serDat
        #print rawDat
        weatherDat = dict(x.split('=') for x in rawDat.split(','))
        return weatherDat

    def dewPoint(self, humidity, tempf):
        humidity = float(humidity)
	#if humidity >= 100.0:
        #    humidity = 100.0
	#print humidity
 	tempC = (float(tempf)-32.0)/1.8
	TdpC = tempC - ((100.0 - humidity)/5.0)
	Tdp = TdpC*(1.8)+32.0
        return Tdp

    def checkDay(self, filename):
        now = datetime.datetime.now()
	print filename
        filedate = filename.translate(None, '/home/matt/WeatherStation/logs/-weather.txt')
        print now.strftime("%Y%m%d %H:%M:%S")
	checktime = datetime.datetime.strptime(filedate, "%Y%m%d")
        #checktime = datetime
	#print str(checktime.day())
        if (now - checktime).days == 0:
            return
        else:
            print "Date change processing"
            self.closePort()
	    now = datetime.datetime.now()
            self.logfile = '/home/matt/WeatherStation/logs/'+str(now.strftime("%Y%m%d"))+"-weather.txt"
            self.openPort()
            return

    def wundergroundOut(self, sortedDat):
	print 'Starting WUnderground upload'
	WUurl = 'https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?'
	WU_station_id = 'KWATOUTL14'
	WU_station_key = 'zk779BNA'
	WUcreds = "ID=" + WU_station_id + "&PASSWORD="+ WU_station_key
	WU_date_str = '&dateutc=now'
	WU_action_str = '&action=updateraw'
	WU_temp = '&tempf='+str(sortedDat['tempf'])
	WU_humidity = '&humidity='+str(sortedDat['humidity'])
	WU_baromin = '&baromin='+'%.2f' %(float(sortedDat['pressure'])/3386.39)
	WU_dewptf = '&dewptf='+str(sortedDat['dewpoint'])
	WU_windspeedmph = '&windspeedmph='+str(sortedDat['windspeedmph'])
	WU_winddir = '&winddir='+str(sortedDat['winddir'])
	WU_windgustmph = '&windgustmph='+str(sortedDat['windgustmph_10m'])
	WU_windgustdir = '&windgustdir='+str(sortedDat['windgustdir_10m'])
	WU_windgustmph_10m = '&windgustmph_10m='+str(sortedDat['windgustmph_10m'])
	WU_windgustdir_10m = '&windgustdir_10m='+str(sortedDat['windgustdir_10m'])
	WU_string = WUurl+WUcreds+WU_date_str+WU_temp+WU_humidity+WU_baromin+WU_dewptf+WU_windspeedmph+WU_winddir+WU_windgustmph+WU_windgustdir+WU_windgustmph_10m+WU_windgustdir_10m+WU_action_str
	print WU_string
	r = requests.get(WU_string)
	print("Received " + str(r.status_code) + " " + str(r.text))
	return

    def run(self):
        rawDat = self.readSer()
	#print rawDat
	currentTime = datetime.datetime.now()
        if rawDat.startswith('winddir=') == True:
            timestamp = currentTime.strftime("%Y%m%d-%H:%M:%S")
            weewxTime = currentTime.strftime("%Y%m%d %H:%M:%S")
	    timedDat = rawDat+',timestamp='+str(timestamp)
            try:
                sortedDat = self.sortOutput(timedDat)
		Tdp = self.dewPoint(sortedDat['humidity'], sortedDat['tempf'])
		outDat = timedDat+',dewpoint=%.1f'%Tdp
		sortedDat['dewpoint'] = "%.1f"%(Tdp)
                #print len(sortedDat)
		#print sortedDat
		if len(sortedDat) == self.dictlength:
                    try:
			self.serOut(outDat, self.logfile)
			liveOut = open('/home/matt/WeatherStation/logs/live_raw.txt', 'w')
			liveOut.write(outDat)
			liveOut.close()
			nap = 10
			if self.WU_count == 6:
			    tic = time.clock()
			    self.wundergroundOut(sortedDat)
			    self.WU_count = 0
			    #Calculate process runtime
			    runDelta = datetime.datetime.now() - self.runStart
			    #runDays, remainder = divmod(runDelta.total_seconds(),86400)
			    #runHours, remainder2 = divmod(remainder, 3600)
			    #print 'Process run time = ' + str(runDays) + ' days and ' + str(runHours) + ' hours.'
			    print 'Runtime = '+str(runDelta)
			    toc = time.clock()
			    process_time = toc - tic
			    if process_time < 10:
			        nap = 10 - process_time
			    else:
				nap = 0.1
			self.WU_count += 1
                        print "tmp[F]="+str(sortedDat['tempf'])+",hum[%]="+str(sortedDat['humidity'])+",dwp[F]="+str(sortedDat['dewpoint'])+",prs[pas]="+str(sortedDat['pressure'])+",wspd="+str(sortedDat['windspeedmph'])+",wspd2m="+str(sortedDat['windspdmph_avg2m'])+",wgst10m="+str(sortedDat['windgustmph_10m'])+',rainin='+str(sortedDat['rainin'])
                    except Exception as e:
			print e
			nap = 0.1
		else:
                    nap = 0.1
            except Exception as ex:
		print ex
                nap = 0.1
        else:
            nap = 0.1
        time.sleep(nap)
        self.checkDay(self.logfile)
        return

if __name__ == "__main__":
    w = WeatherInterface()
    run = True
    w.openPort()
    time.sleep(2)
    now = datetime.datetime.now()
    print str(now)
    #w.logfile = '/'+now.strftime("%Y%m%d")+"-weather.txt"
    print 'port open'
    while run == True:
        w.run()
        #junktime = w.checkDay(cTime)
    w.closePort()
