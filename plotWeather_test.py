from PIL import Image, ImageDraw
import PIL.ImageOps
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from weather_interface import WeatherInterface
import datetime
import time
import os, sys
import shutil
import numpy as np
import operator
import re
import traceback

class WeatherPlot():
    def __init__(self):
	self.wi = WeatherInterface()
	self.plotTime = 23		#Length of data plot, in hours - DO NOT EXCEED 24

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

	self.date = datetime.datetime.now()
        self.logfile = '/logs/'+datetime.datetime.strftime(self.date, "%Y%m%d")+"-weather.txt"
        self.datafile = str(os.getcwd())+self.logfile     #Location of data file

	self.pressure = 'atm'

    def dataToLists(self):
        '''
        sort the data from each line in the data file
        and extract the data for a specific sensor
        '''

        checktime = datetime.datetime.now()
	logDate = datetime.datetime.strftime(checktime, "%Y%m%d")
	#print logDate
	datecount = 0
	timeCheck = 0

        data = {}

	datalist = []
	tempFile = open(str(os.getcwd())+'/logs/'+logDate+"-weather.txt",'r')
        templist = tempFile.readlines()
        tempFile.close()
        templist.reverse()
	datalist = datalist + templist


	sensorList = []
	linedic = self.wi.sortOutput(str(datalist[0]))
	for key in linedic:
	    sensorList.append(key)
	    data[key] = []

	while timeCheck < self.plotTime:

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
			print "Deleting "+str(timeobj)+" for incorrect key: "+str(key)
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
		    dayCheck = (checktime - timeobj).days * 24.0
		timeCheck = ((checktime - timeobj).seconds/(60.0*60.0)) + dayCheck	# Hours
		#print timeCheck


		if timeCheck < self.plotTime and len(datalist) < 1:
		    print "Opening new log"
		    datecount += 1
		    logDateParse = datetime.datetime.strptime(logDate, "%Y%m%d")
		    print "logDateParse: "+logDateParse.strftime("%Y%m%d")
		    logDate = logDateParse - datetime.timedelta(days=1)
		    tempFile = open(str(os.getcwd())+'/logs/'+logDate.strftime("%Y%m%d")+"-weather.txt",'r')
		    print "new log file: logs/"+logDate.strftime("%Y%m%d")+"-weather.txt"
		    templist = tempFile.readlines()
		    tempFile.close()
		    templist.reverse()
		    datalist = datalist + templist

	    except Exception as e:
                #print 'Exception: '+str(e)
		#traceback.print_exc()
	        continue
	#index_min = min(xrange(len(data)), key=data.__getitem__)
	#index_max = max(xrange(len(data)), key=data.__getitem__)

        return data #, timestamps, index_min, index_max

    def minmax(self, list):
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

    def plotPressure(self, dataDict):
	pressure, timestamp = dataDict['pressure'], dataDict['timestamp']
	pressure = self.convertPressure(pressure)

        ind_min_prs, ind_max_prs = self.minmax(pressure)
        min_prs, max_prs = float(pressure[ind_min_prs]), float(pressure[ind_max_prs])
        min_prs_time, max_prs_time = timestamp[ind_min_prs], timestamp[ind_max_prs]

	self.outDict["pressure"] = "%.5f"%pressure[0]
	self.outDict["minPrs"] = "%.5f"%min_prs
	self.outDict["minPrsTime"] = min_prs_time.strftime("%m-%d %H:%M")
	self.outDict["maxPrs"] = "%.5f"%max_prs
	self.outDict["maxPrsTime"] = max_prs_time.strftime("%m-%d %H:%M")

	stp = 0.964739		#Calculated for elev = 990 ft

	stpList = []
	for i in range(len(timestamp)):
	    stpList.append(stp)

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Pressure [ATM]')
        ax.set_title('Barometric Pressure')

        ax.plot(timestamp, pressure, 'm-')
	ax.plot(timestamp, stpList, 'y-', label='Std. Pressure=%.4f'%stp)
        majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
	ax.legend( loc='upper left', ncol=1, shadow=True, numpoints = 2 )
        ax.autoscale_view()
        #ax.set_axis_bgcolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot

        minTimeStr = min_prs_time.strftime('%m-%d %H:%M')
        maxTimeStr = max_prs_time.strftime('%m-%d %H:%M')
        minmaxText = timestamp[0].strftime('%Y%m%d %H:%M:%S')+" || Current: %.5f \nLow: %.5f at %s || High: %.5f at %s" % (float(pressure[0]), min_prs, minTimeStr, max_prs, maxTimeStr)
	fig.text(0.05, -0.06, minmaxText)

        plt.grid(True)
        fig.tight_layout()
        #plt.show()
        plt.savefig(os.getcwd()+'/pressure.png', bbox_inches='tight')
        plt.close('all')
        return

    def plotHumidity(self, dataDict):
	humidity, timestamp = dataDict['humidity'], dataDict['timestamp']

        ind_min_hum, ind_max_hum = self.minmax(humidity)
        min_hum, max_hum = float(humidity[ind_min_hum]), float(humidity[ind_max_hum])
        min_hum_time, max_hum_time = timestamp[ind_min_hum], timestamp[ind_max_hum]

        minTimeStr = min_hum_time.strftime('%m-%d %H:%M')
        maxTimeStr = max_hum_time.strftime('%m-%d %H:%M')

	self.outDict["humidity"] = humidity[0]
	self.outDict["minHum"] = min_hum
	self.outDict["minHumTime"] = minTimeStr
	self.outDict["maxHum"] = max_hum
	self.outDict["maxHumTime"] = maxTimeStr

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Humidity [%]')
        ax.set_title('Humidity')

        ax.plot(timestamp, humidity, 'm-')

        majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.autoscale_view()
        #ax.set_axis_bgcolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot

        minmaxText = timestamp[0].strftime('%Y%m%d %H:%M:%S')+" || Current: %.1f \nLow: %.1f at %s || High: %.1f at %s" % (float(humidity[0]), min_hum, minTimeStr, max_hum, maxTimeStr)
        fig.text(0.05, -0.06, minmaxText)

        plt.grid(True)
        fig.tight_layout()
        #plt.show()
        plt.savefig(os.getcwd()+'/humidity.png', bbox_inches='tight')
        plt.close('all')
        return

    def windDirection(self, degree):
	windDirection = (float(degree) + self.windOffset) % 360.0
	for key, list in self.windDirDict.iteritems():
	    if windDirection >= list[0] and windDirection < list[1]:
	        return key

    def plotWind(self, dataDict):

        windavg2m, windgust10mL, timestamps = dataDict['windspdmph_avg2m'], dataDict['windgustmph_10m'], dataDict['timestamp']

	self.outDict["timestamp"] = timestamps[0].strftime("%Y-%m-%d %H:%M:%S")

	windgust10m = []
	windgust10m = [float(i) for i in windgust10mL]
        index_maxGust = self.minmax(windgust10m)[1]
	maxGust = max(windgust10m)
	self.outDict["maxGust"] = maxGust
        maxGustTime = timestamps[index_maxGust].strftime('%m-%d %H:%M')
        self.outDict["maxGustTime"] = maxGustTime
	maxGustDir = self.windDirection(float(dataDict['windgustdir'][index_maxGust]))

        index_maxWind = self.minmax(windavg2m)[1]
        maxWind = float(windavg2m[index_maxWind])
        self.outDict["maxWind"] = maxWind
	maxWindTime = timestamps[index_maxWind].strftime('%m-%d %H:%M')
        self.outDict["maxWindTime"] = maxWindTime
	maxWindDir = self.windDirection(float(dataDict['winddir'][index_maxWind]))
	self.outDict["maxWindDir"] = maxWindDir

        currentWind = float(windavg2m[0])
        self.outDict["wind"] = currentWind
	currentGust = float(windgust10m[0])
	self.outDict["windGust"] = currentGust
        currentDir = self.windDirection(float(dataDict['winddir'][0]))
        self.outDict["windDir"] = currentDir
	currentGustDir = self.windDirection(float(dataDict['windgustdir'][0]))
	self.outDict["windGustDir"] = currentGustDir


        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Wind Speed [mph]')
        ax.set_title('Wind Data')

        ax.plot(timestamps, windavg2m, 'y-', label='Avg Wind (2 min)')
        ax.plot(timestamps, windgust10m, 'c-', label='Wind Gust (10 min)')

	minmaxText = timestamps[0].strftime('%Y%m%d %H:%M:%S')+" || Current Wind: %.1f from %s || Current Gust: %.1f from %s \nMax Wind: %.1f at %s || Max Gust: %.1f at %s" % (currentWind, currentDir, currentGust, currentGustDir, maxWind, maxWindTime, maxGust, maxGustTime)
        fig.text(0.05, -0.06, minmaxText)

	majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.autoscale_view()
        ax.legend( loc='upper left', ncol=1, shadow=True, numpoints = 2 )
        #ax.patch.set_facecolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot
        plt.grid(True)
        fig.tight_layout()
        plt.savefig(os.getcwd()+'/wind.png', bbox_inches='tight')
	plt.close('all')
	plt.clf()
	return

    def plotTemp(self, dataDict):
        tempf, timestamps, dewpoint = dataDict['tempf'], dataDict['timestamp'], dataDict['dewpoint']

	index_temp_min, index_temp_max = self.minmax(tempf)
	minTemp, maxTemp = float(tempf[index_temp_min]), float(tempf[index_temp_max])
	minTime, maxTime = timestamps[index_temp_min], timestamps[index_temp_max]

        minTimeStr = minTime.strftime('%m-%d %H:%M')
        maxTimeStr = maxTime.strftime('%m-%d %H:%M')

        tempfs = []
        tempfs = [float(i) for i in tempf]

        dewpoints = []
        dewpoints = [float(i) for i in dewpoint]

	self.outDict["tempf"] = tempfs[0]
	self.outDict["dewpoint"] = dewpoints[0]
	self.outDict["temp_max"] = maxTemp
	self.outDict["temp_max_time"] = maxTimeStr
	self.outDict["temp_min"] = minTemp
	self.outDict["temp_min_time"] = minTimeStr

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Temperature [F]')
        #ax.set_xlabel('Time [hours]')
        ax.set_title('Temperature Data')

        ax.plot(timestamps, dewpoints, 'y-', label='Dewpoint [F]')
        ax.plot(timestamps, tempfs, 'c-', label='Temp [F]')

	'''
	for i in range(len(tempfs)):
	    deltaDew = tempfs[i] - dewpoints[i]
	    if deltaDew < 5.0:
		ax.plot(timestamps[i], dewpoints[i], 'b-')
	    elif deltaDew < 10.0 and deltaDew >= 5.0:
                ax.plot(timestamps[i], dewpoints[i], 'r-')
	'''

	currentTemp = tempfs[0]
	minmaxText = timestamps[0].strftime('%Y%m%d %H:%M:%S')+" || Current Temp: %.1f || Current Dewpoint: %.1f \nLow: %.1f at %s || High: %.1f at %s" % (currentTemp, dewpoints[0], minTemp, minTimeStr, maxTemp, maxTimeStr)
	fig.text(0.05, -0.06, minmaxText)
        majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.autoscale_view()
        ax.legend( loc='upper left', ncol=1, shadow=True, numpoints = 2 )
        #ax.patch.set_facecolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot
        plt.grid(True)
        fig.tight_layout()
        plt.savefig(os.getcwd()+'/tempf.png', bbox_inches='tight')
        plt.close('all')
	plt.clf()
        return

    def liveDataOut(self):
	outString = ""
	for key, value in self.outDict.iteritems():
	    outString = outString + str(key) + "=" + str(value) + ","
	outString = outString[:-1]
	#print outString
	directory = str(os.getcwd())+"/live.txt"
        f_out = open(directory,'w')
        f_out.write(outString)
        f_out.close()
	return

    def upload(self, sensorname):
        image = Image.open(os.getcwd()+'/'+sensorname+'.png')
        if image.mode == 'RGBA':
            r,g,b,a = image.split()
            rgb_image = Image.merge('RGB', (r,g,b))
            inverted_image = PIL.ImageOps.invert(rgb_image)
            r2,g2,b2 = inverted_image.split()
            final_transparent_image = Image.merge('RGBA', (r2,g2,b2,a))
            final_transparent_image.save(os.getcwd()+'/'+sensorname+'.png')
        else:
            inverted_image = PIL.ImageOps.invert(image)
            inverted_image.save(os.getcwd()+'/'+sensorname+'.png')

        shutil.copy(os.getcwd()+'/'+sensorname+'.png', '/var/www/html/'+sensorname+'.png')
        print 'copied '+sensorname+'.png'

    def checkDay(self, filename):
	now = datetime.datetime.now()
	filedate = str(filename).translate(None ,'/logs/-weather.txt')
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
	    self.logfile = '/logs/'+str(self.date.strftime("%Y%m%d"))+"-weather.txt"
	    print "Log file: "+self.logfile
	    print "Date change complete"
	    return


    def run(self):
        currentTime = datetime.datetime.now()
        dataDict = self.dataToLists()

	try:
            self.plotWind(dataDict)
            self.upload('wind')

            self.plotTemp(dataDict)
            self.upload('tempf')

	    self.plotPressure(dataDict)
	    self.upload('pressure')

	    self.plotHumidity(dataDict)
	    self.upload('humidity')
	except Exception as e:
	    print 'Exception:'+str(e)
	    traceback.print_exc()
	self.liveDataOut()
	shutil.copy(os.getcwd()+'/live.txt', '/var/www/html/live.txt')
	self.outDict = {}

	self.checkDay(self.logfile)
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
