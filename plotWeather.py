from PIL import Image, ImageDraw
import PIL.ImageOps
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from weather_interface import WeatherInterface
import datetime
import time
import os
import shutil
import numpy as np
import operator
import re

class WeatherPlot():
    def __init__(self):
        self.maxtime = 7000          #Number of entries to plot
	self.date = datetime.datetime.now()
        self.logfile = '/logs/'+datetime.datetime.strftime(self.date, "%Y%m%d")+"-weather.txt"
        self.datafile = str(os.getcwd())+self.logfile     #Location of data file
        self.wi = WeatherInterface()

    def plot(self, sensorname, color, sensordata, timestamp, figname):
	print len(sensordata)
        #Generic plotting routine

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel(str(sensorname))
        ax.set_xlabel('Time [hours]')
        ax.set_title(str(sensorname))

        ax.plot(timestamp, sensordata, color+'-')
        majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
        ax.autoscale_view()
        #ax.set_axis_bgcolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot
        plt.grid(True)
        fig.tight_layout()
        #plt.show()
        plt.savefig(os.getcwd()+'/'+figname+'.png', bbox_inches='tight')
	plt.close('all')
	return

    def dataToLists(self, sensorname):
        '''
        sort the data from each line in the data file
        and extract the data for a specific sensor
        '''
        data = open(self.datafile,'r')
        datalist = data.readlines()
        data.close()
        datalist.reverse()
        checktime = datetime.datetime.now()
        timestamps = []
        data = []

	if (len(datalist) < self.maxtime) == True:
	    try:
		templog = str(os.getcwd())+'/logs/'+datetime.datetime.strftime(self.date - datetime.timedelta(days=1), "%Y%m%d")+"-weather.txt"
		tempdata = open(templog, 'r')
		templist = tempdata.readlines()
		tempdata.close()
		templist.reverse()
		datalist = datalist + templist
	    except Exception as e:
		print e

	for i in range(self.maxtime):
	    try:
		linedic = self.wi.sortOutput(str(datalist[i]))
            	temptime = linedic['timestamp']
                temptime = temptime.strip('\n')
                timeobj = datetime.datetime.strptime(temptime, "%Y%m%d-%H:%M:%S")
                data.append(float(linedic[sensorname]))
                timestamps.append(timeobj)
	    except Exception as e:
		#print e
	        continue
	    #else:
		#continue
	index_min = min(xrange(len(data)), key=data.__getitem__)
	index_max = max(xrange(len(data)), key=data.__getitem__)

        return data, timestamps, index_min, index_max

    def convertPressure(self, pressureData):
        '''
        Convert the pressure data from pascal to inHg
        '''
        atmData = []
        for i in range(len(pressureData)):
            atmData.append((pressureData[i])/3386.375258)  #inHg
            #atmData.append((pressureData[i])/101325.0)     #atm
        return atmData

    def plotWind(self):
        #windmph, timestamps = self.dataToLists('windspeedmph')
        windavg2m, windtimestamps, index_wind_min, index_wind_max = self.dataToLists('windspdmph_avg2m')
        windgust10m, gusttimestamps, index_gust_min, index_gust_max = self.dataToLists('windgustmph_10m')

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Wind Speed [mph]')
        ax.set_xlabel('Time [hours]')
        ax.set_title('Wind Data')

        ax.plot(windtimestamps, windavg2m, 'c-', label='Avg Wind (2 min)')
        ax.plot(gusttimestamps, windgust10m, 'b--', label='Wind Gust (10 min)')
	
	ax.annotate('Max Gust = %.1f [MPH]\n%s' % (windgust10m[index_gust_max], gusttimestamps[index_gust_max].strftime('%H:%M')),
	xy=(gusttimestamps[index_gust_max], windgust10m[index_gust_max]),
	xytext=(gusttimestamps[index_gust_max], windgust10m[index_gust_max]*0.7), #, textcoords='offset pixels',
	bbox = dict(boxstyle='round', fc='black', fill=False),
        horizontalalignment='center',
        verticalalignment='bottom',
	arrowprops=dict(facecolor='white', shrink=0.1, fill=True))
        
	majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.autoscale_view()
        ax.legend( loc='upper left', ncol=1, shadow=True, numpoints = 2 )
        #ax.patch.set_facecolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot
        plt.grid(True)
        fig.tight_layout()
        plt.savefig(os.getcwd()+'/wind.png', bbox_inches='tight')
	return
	plt.close('all')

    def plotTemp(self):
        tempfs, timestamps, index_temp_min, index_temp_max = self.dataToLists('tempf')
        dewpoints, timestamps2, index_dew_min, index_dew_max = self.dataToLists('dewpoint')
	print len(tempfs)

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,4)
        ax.set_ylabel('Temperature [F]')
        ax.set_xlabel('Time [hours]')
        ax.set_title('Temperature Data')

        ax.plot(timestamps2, dewpoints, 'm--', label='Dewpoint [F]')
        ax.plot(timestamps, tempfs, 'c-', label='Temp [F]')
	
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

        majorFormatter = mpl.dates.DateFormatter('%m-%d %H:%M')
        ax.xaxis.set_major_formatter(majorFormatter)
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.autoscale_view()
        ax.legend( loc='upper left', ncol=1, shadow=True, numpoints = 2 )
        #ax.patch.set_facecolor('black')
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot
        plt.grid(True)
        fig.tight_layout()
        plt.savefig(os.getcwd()+'/tempf.png', bbox_inches='tight')
        plt.close('all')
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
	if (now - checktime).days == 0:
	    return
	else:
	    print "Date change processing"
	    self.logfile = '/logs/'+str(datetime.datetime.strftime("%Y%m%d"))+"-weather.txt"
	    print "Date change complete"
	    return


    def run(self):
        currentTime = datetime.datetime.now()
        weatherDict = {
        #'sensorname': 'sensortitle',
        #'tempf': 'Temp [F]',
        'humidity': 'Humidity [%]',
        'pressure': 'Pressure [inHg]',
        #'light_lvl': 'Light Level',
        'rainin': 'Rain [in]',
        'dailyrainin': 'Daily Rain [in]',
        #'windgustmph_10m': 'Wind Gust - 10min [mph]',
        #'windspdmph_avg2m': 'Wind Speed - 2min avg [mph]',
        #'windgustmph': 'Wind Gust [mph]',
        #'windspeedmph': 'Wind Speed [mph]'
        }
	try:
            self.plotWind()
            self.upload('wind')
	except Exception as e:
	    print e
	try:
            self.plotTemp()
            self.upload('tempf')
	except Exception as e:
	    print e

	try:
            for key, value in weatherDict.iteritems():
                sensorname = key
       	        sensortitle = value
                data, timestamps, index_min, index_max = wp.dataToLists(sensorname)
                if sensorname == 'pressure':
	            data = wp.convertPressure(data)
                #Plot the data
                wp.plot(sensortitle, 'c', data, timestamps, sensorname)
                wp.upload(sensorname)
	        plt.close('all')
	except Exception as e:
	    print "plot cycle failed, skipping"
	    print e
	shutil.copy(os.getcwd()+'/live.txt', '/var/www/cgi-bin/live.txt')

	self.checkDay(self.logfile)
	return currentTime


if __name__ == "__main__":
    wp = WeatherPlot()
    #Extract the data for a named sensor
    #wp.self.logfile = WeatherInterface.checkDay(currentTime)
    run = True
    while run == True:
        tic = time.clock()
        currentTime = wp.run()
        toc = time.clock()
        elapsedTime = toc - tic
        if elapsedTime > 30.0:
	    elapsedTime = 30.0
	if elapsedTime < 0.0:
	    elapsedTime = 30.0
	print 'processing time [s] = '+str(elapsedTime)
        time.sleep(30.0-elapsedTime)
        #wp.self.logfile = WeatherInterface.checkDay(currentTime)
