from weather_interface import WeatherInterface
import datetime
import time
import os, sys
import shutil
import numpy as np
import operator
import re
import traceback
import requests

class WeatherPlot():
    def __init__(self):
        self.wi = WeatherInterface()

        self.stationID = "KWATOUTL10"
        self.stationKey = "7u79f0i8"

        self.avgTime = 60		#Length of data average, in seconds

	self.date = datetime.datetime.now()
        self.logfile = '/home/matt/WeatherStation/logs/'+datetime.datetime.strftime(self.date, "%Y%m%d")+"-weather.txt"
        self.datafile = self.logfile     #Location of data file

        self.pressure = 'inHg'

	self.uploadKeys = [
	    'winddir_avg2m',
            'windgustmph',
            'tempf',
            'dewptf',
            'windspeedmph',
            'windgustdir_10m',
            'humidity',
            'winddir',
            'baromin',
            'windspdmph_avg2m',
            'windgustmph_10m',
            'windgustdir'
            ]


        self.sensorKeys = [
            'winddir_avg2m',
            'windgustmph',
            'tempf',
            'light_lvl',
            'dewpoint',
            'windspeedmph',
            #'timestamp',
            'windgustdir_10m',
            'rainin',
            'humidity',
            'winddir',
            'pressure',
            'windspdmph_avg2m',
            'windgustmph_10m',
            'dailyrainin',
            'windgustdir'
            ]

        self.windOffset = 0.0
        self.windDirDict = {
	   'N': [0.0, 45.0],
           'NE': [45.0, 90.0],
           'E': [90.0, 135.0],
           'SE': [135.0, 180.0],
           'S': [180.0, 225.0],
           'SW': [225.0, 270.0],
           'W': [270.0, 315.0],
           'NW': [315.0, 360.0]
           }

        self.outDict = {}

    def dataToLists(self):
        '''
        sort the data from each line in the data file
        and extract the data for a specific sensor
        '''

        checktime = datetime.datetime.now()
        logDate = datetime.datetime.strftime(checktime, "%Y%m%d")
        datecount = 0
        timeCheck = 0

        data = {}

        datalist = []
        tempFile = open('/home/matt/WeatherStation/logs/'+logDate+"-weather.txt",'r')
        templist = tempFile.readlines()
        tempFile.close()
        templist.reverse()
        datalist = datalist + templist

        sensorList = []
        linedic = self.wi.sortOutput(str(datalist[0]))
        for key in linedic:
            sensorList.append(key)
            data[key] = []

        while timeCheck < self.avgTime:
            # Sort datafile into a dictionary of lists
            # data = {sensorName: [sensorData]}
            # Sorts through data from newest to oldest

            try:
	        linedic = self.wi.sortOutput(str(datalist[0]))
                temptime = linedic['timestamp']
                temptime = temptime.strip('\n')
                timeobj = datetime.datetime.strptime(temptime, "%Y%m%d-%H:%M:%S")
	        del linedic['timestamp']

	        # Look for improper length dictionary
                if len(linedic) != len(self.sensorKeys):
                    print "Deleting "+str(linedic)+" for improper length"
                    del datalist[0]
                    continue

                # Check for blank entries, remove newline char
                for key in linedic:
                    linedic[key] = linedic[key].strip('\n')
                    if len(linedic[key]) == 0 :
                        print "Deleting "+str(linedic)+" for blank entry"
			del datalist[0]
                        continue
                    if key not in self.sensorKeys:
			del datalist[0]
			linedic = {}
	                continue

                for key in self.sensorKeys:
                    data[key].append(linedic[key])
                    del linedic[key]
                    if len(linedic) == 0:
                        #print "Deleting "+datalist[0]+" because completed"
                        data['timestamp'].append(timeobj)
                        del datalist[0]

                # See if the time is past self.plotTime
                dayCheck = 0.0
                if (checktime - timeobj).days >= 1:
                    dayCheck = (checktime - timeobj).days * 24.0*60.0*60.0
                timeCheck = (checktime - timeobj).seconds + dayCheck	# seconds

                if timeCheck < self.avgTime and len(datalist) < 1:
                    print "Opening new log"
                    datecount += 1
                    logDateParse = datetime.datetime.strptime(logDate, "%Y%m%d")
                    print "logDateParse: "+logDateParse.strftime("%Y%m%d")
                    logDate = logDateParse - datetime.timedelta(days=1)
                    tempFile = open('/home/matt/WeatherStation/logs/'+logDate.strftime("%Y%m%d")+"-weather.txt",'r')
                    print "new log file: logs/"+logDate.strftime("%Y%m%d")+"-weather.txt"
                    templist = tempFile.readlines()
                    tempFile.close()
                    templist.reverse()
                    datalist = datalist + templist

            except Exception as e:
                #print 'Exception: '+str(e)
                #traceback.print_exc()
                continue

        return data #, timestamps, index_min, index_max

    def minmax(self, list):
        '''
        Find the list index for minimum and maximum values
        '''
        index_min = min(xrange(len(list)), key=list.__getitem__)
        index_max = max(xrange(len(list)), key=list.__getitem__)

        return index_min, index_max

    def convertPressure(self, pressureData):
        '''
        Convert the pressure data from pascal to inHg or atm
        '''
        atmData = []

        for i in range(len(pressureData)):
            if self.pressure == 'atm':
		atmData.append(float(pressureData[i])/101325.0)     #atm
	    else:
	    	atmData.append(float(pressureData[i])/3386.375258)  #inHg
        return atmData

    def windDirection(self, degree):
        '''
        Converts wind direction in degrees to compass direction
        '''
        windDirection = (float(degree) + self.windOffset) % 360.0
        for key, list in self.windDirDict.iteritems():
            if windDirection >= list[0] and windDirection < list[1]:
                return key

    def liveDataOut(self):
        outString = ""
        for key, value in self.outDict.iteritems():
            outString = outString + str(key) + "=" + str(value) + ","
        outString = outString[:-1]
        directory = "/home/matt/WeatherStation/logs/live.txt"
        f_out = open(directory,'w')
        f_out.write(outString)
        f_out.close()
        return


    def checkDay(self, filename):
        '''
        Checks log file name against current date, updates if needed.
        '''
        print os.path.split(filename)[1]
        now = datetime.datetime.now()
        filedate = os.path.split(filename)[1].translate(None ,'-weather.txt')
        checktime = datetime.datetime.strptime(filedate, "%Y%m%d")
        print 'Now: '+now.strftime("%Y%m%d %H:%M:%S")
        print 'Checktime: '+checktime.strftime("%Y%m%d")
        print (now - checktime).days
        if (now - checktime).days == 0:
            return
        else:
            print "Date change processing"
            self.date = now
            print "Date: "+self.date.strftime("%Y%m%d")
            self.logfile = '/home/matt/WeatherStation/logs/'+str(self.date.strftime("%Y%m%d"))+"-weather.txt"
            print "Log file: "+self.logfile
            print "Date change complete"
            return


    def outUnderground(self, dataDict):

	avgData = {}
        for key in dataDict:
           if key == 'timestamp':
              continue
           tempdata = dataDict[key]
           sensorData = []
           for i in range(len(tempdata)):
              sensorData.append(float(tempdata[i]))
           avgData[key] = '%.1f' %(float(sum(sensorData)/len(sensorData)))

	avgData['baromin']='%.3f' %(float(avgData['pressure'])/3386.375258)
	avgData['dewptf']=avgData['dewpoint']

	outData = {}
        outData['ID']=self.stationID
        outData['PASSWORD']=self.stationKey

	for key in avgData:
	   if key in self.uploadKeys:
	      outData[key]=avgData[key]

	outData['dateutc']='now'
	outData['action']='updateraw'
	print "========================================"
	print "   Weather Data  ~  %s" %(dataDict['timestamp'][0].strftime("%Y%m%d - %H:%M"))
	print " "
	print "TempF = %s          Humid = %s" %(outData['tempf'], outData['humidity'])
	print "Dew = %s            Press = %s" %(outData['dewptf'], outData['baromin'])
	print " "
	print "Wind avg2m = %s      Wind Dir = %s" %(outData['windspdmph_avg2m'], outData['winddir_avg2m'])
        print "Wind Gust 10m = %s   Gust Dir = %s" %(outData['windgustmph_10m'], outData['windgustdir'])
	print " "
	print "Rain = %s          Daily Rain = %s" %(dataDict['rainin'][0], dataDict['dailyrainin'][0])
	print "========================================"


	r = requests.post("https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php", data=outData)
        print "Upload status = "+r.text

    def run(self):
        currentTime = datetime.datetime.now()
        dataDict = self.dataToLists()
	self.outUnderground(dataDict)
        return currentTime


if __name__ == "__main__":
    wp = WeatherPlot()

    run = True
    sleepTime = 30.0

    while run == True:
        tic = time.clock()
        currentTime = wp.run()
        toc = time.clock()
        elapsedTime = toc - tic
        if elapsedTime > sleepTime:
	    elapsedTime = sleepTime
	if elapsedTime < 0.0:
	    elapsedTime = sleepTime
	print 'processing time [s] = '+str(elapsedTime)
        time.sleep(sleepTime-elapsedTime)
