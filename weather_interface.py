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
import os
import csv

class WeatherInterface():
    def __init__(self):
	self.serPort = '/dev/ttyACM0'
        self.dictlength = 15        #Number of lines from serial
        self.logfile = '/weather.txt'

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
        return s

    def serOut(self, status, filename):
        directory = str(os.getcwd())+filename
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

    def run(self):
        rawDat = self.readSer()
        if rawDat.startswith('winddir=') == True:
            timedDat = rawDat+',timestamp='+str(time.strftime("%Y%m%d-%H:%M:%S"))
            try:
                sortedDat = self.sortOutput(timedDat)
                if len(sortedDat) == self.dictlength:
                    self.serOut(timedDat, self.logfile)
                    nap = 10
                    print "tmp[F]="+str(sortedDat['tempf'])+",hum[%]="+str(sortedDat['humidity'])+",pressure[pas]="+str(sortedDat['pressure'])+",windspeedmph="+str(sortedDat['windspeedmph'])+",windgustmph_10m="+str(sortedDat['windgustmph_10m'])
                else:
                    nap = 0.1
            except:
                nap = 0.1
        else:
            nap = 0.1
        time.sleep(nap)

if __name__ == "__main__":
    w = WeatherInterface()
    run = True
    w.openPort()
    time.sleep(2)
    print 'port open'
    while run == True:
        w.run()
    w.closePort()
