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
	self.plotTime = 23		#Length of data plot, in hours - DO NOT EXCEED 23

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
		timeCheck = (checktime - timeobj).seconds/(60*60)	# Hours
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

	ind_min_prs, ind_max_prs = self.minmax(pressure)
        min_prs, max_prs = float(pressure[ind_min_prs]), float(pressure[ind_max_prs])
        min_prs_time, max_prs_time = timestamp[ind_min_prs], timestamp[ind_max_prs]

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

	ind_min_hum, ind_max_hum = self.minmax(humidity)
	min_hum, max_hum = float(humidity[ind_min_hum]), float(humidity[ind_max_hum])
	min_hum_time, max_hum_time = timestamp[ind_min_hum], timestamp[ind_max_hum]

	minTimeStr = min_hum_time.strftime('%m-%d %H:%M')
        maxTimeStr = max_hum_time.strftime('%m-%d %H:%M')
        minmaxText = timestamp[0].strftime('%Y%m%d %H:%M:%S')+" || Current: %.1f \nLow: %.1f at %s || High: %.1f at %s" % (float(humidity[0]), min_hum, minTimeStr, max_hum, maxTimeStr)
        fig.text(0.05, -0.06, minmaxText)

        plt.grid(True)
        fig.tight_layout()
        #plt.show()
        plt.savefig(os.getcwd()+'/humidity.png', bbox_inches='tight')
        plt.close('all')
        return



    def plotWind(self, dataDict):

        windavg2m, windgust10m, timestamps = dataDict['windspdmph_avg2m'], dataDict['windgustmph_10m'], dataDict['timestamp']

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Wind Speed [mph]')
        ax.set_title('Wind Data')

        ax.plot(timestamps, windavg2m, 'y-', label='Avg Wind (2 min)')
        ax.plot(timestamps, windgust10m, 'c-', label='Wind Gust (10 min)')

	'''
	ax.annotate('Max Gust = %.1f [MPH]\n%s' % (windgust10m[index_gust_max], gusttimestamps[index_gust_max].strftime('%H:%M')),
	xy=(gusttimestamps[index_gust_max], windgust10m[index_gust_max]),
	xytext=(gusttimestamps[index_gust_max], windgust10m[index_gust_max]*0.7), #, textcoords='offset pixels',
	bbox = dict(boxstyle='round', fc='black', fill=False),
        horizontalalignment='center',
        verticalalignment='bottom',
	arrowprops=dict(facecolor='white', shrink=0.1, fill=True))
        '''

	index_maxGust = self.minmax(windgust10m)[1]
	maxGust = float(windgust10m[index_maxGust])
	maxGustTime = timestamps[index_maxGust].strftime('%m-%d %H:%M')
	maxGustDir = float(dataDict['windgustdir'][index_maxGust])

	index_maxWind = self.minmax(windavg2m)[1]
        maxWind = float(windavg2m[index_maxWind])
        maxWindTime = timestamps[index_maxWind].strftime('%m-%d %H:%M')
        maxWindDir = float(dataDict['winddir'][index_maxWind])

        currentWind = float(windavg2m[0])
	currentGust = float(windgust10m[0])
	currentDir = float(dataDict['winddir'][0])
	currentGustDir = float(dataDict['windgustdir'][0])

	minmaxText = timestamps[0].strftime('%Y%m%d %H:%M:%S')+" || Current Wind: %.1f from %.0f || Current Gust: %.1f from %.0f \nMax Wind: %.1f at %s || Max Gust: %.1f at %s" % (currentWind, currentDir, currentGust, currentGustDir, maxWind, maxWindTime, maxGust, maxGustTime)
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
        tempfs, timestamps, dewpoints = dataDict['tempf'], dataDict['timestamp'], dataDict['dewpoint']

	index_temp_min, index_temp_max = self.minmax(tempfs)
	minTemp, maxTemp = float(tempfs[index_temp_min]), float(tempfs[index_temp_max])
	minTime, maxTime = timestamps[index_temp_min], timestamps[index_temp_max]

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Temperature [F]')
        #ax.set_xlabel('Time [hours]')
        ax.set_title('Temperature Data')

        ax.plot(timestamps, dewpoints, 'y-', label='Dewpoint [F]')
        ax.plot(timestamps, tempfs, 'c-', label='Temp [F]')

	'''
        ax.annotate('Max Temp = %.1f [F]\n%s' % (tempfs[index_temp_max], timestamps[index_temp_max].strftime('%H:%M')),
        xy=(timestamps[index_temp_max], tempfs[index_temp_max]),
        xytext=(timestamps[index_temp_max], tempfs[index_temp_max]*0.8), #textcoords='offset pixels',
	bbox = dict(boxstyle='round', fc='black', fill=False),
        horizontalalignment='center',
        verticalalignment='bottom',
        arrowprops=dict(facecolor='white', shrink=0.2, fill=True))

	ax.annotate('Min Temp = %.1f [F]\n%s' % (tempfs[index_temp_min], timestamps[index_temp_min].strftime('%H:%M')),
        xy=(timestamps[index_temp_min], tempfs[index_temp_min]),
        xytext=(timestamps[index_temp_min], tempfs[index_temp_min]*1.2), #textcoords='offset pixels',
	bbox = dict(boxstyle='round', fc='black', fill=False),
        horizontalalignment='right',
        verticalalignment='bottom',
        arrowprops=dict(facecolor='white', shrink=0.2, fill=True))
	'''

	minTimeStr = minTime.strftime('%m-%d %H:%M')
	maxTimeStr = maxTime.strftime('%m-%d %H:%M')
	currentTemp = float(tempfs[0])
	minmaxText = timestamps[0].strftime('%Y%m%d %H:%M:%S')+" || Current Temp: %.1f || Current Dewpoint: %.1f \nLow: %.1f at %s || High: %.1f at %s" % (currentTemp, float(dewpoints[0]), minTemp, minTimeStr, maxTemp, maxTimeStr)
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

	shutil.copy(os.getcwd()+'/live.txt', '/var/www/cgi-bin/live.txt')

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
