
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

class WeatherPlot():
    def __init__(self):
        self.maxtime = 520          #Number of entries to plot
        self.logfile = str(datetime.strftime("%Y%m%d"))+"-weather.txt"
        self.datafile = str(os.getcwd())+'/'+self.logfile+'.txt'     #Location of data file
        self.wi = WeatherInterface()

    def plot(self, sensorname, color, sensordata, timestamp, figname):
        #Generic plotting routine

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,8)
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
        for i in range(self.maxtime):
            try:
		linedic = self.wi.sortOutput(str(datalist[i]))
            	temptime = linedic['timestamp']
                temptime = temptime.strip('\n')
                timeobj = datetime.datetime.strptime(temptime, "%Y%m%d-%H:%M:%S")
                data.append(float(linedic[sensorname]))
                timestamps.append(timeobj)
	    except:
		continue
        return data, timestamps

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
        windmph, timestamps = self.dataToLists('windspeedmph')
        windavg2m, timestamps = self.dataToLists('windspdmph_avg2m')
        windgust10m, timestamps = self.dataToLists('windgustmph_10m')

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,8)
        ax.set_ylabel('Wind Speed [mph]')
        ax.set_xlabel('Time [hours]')
        ax.set_title('Wind Data')

        #ax.plot(timestamps, windmph, 'b-.', label='Wind Speed')
        ax.plot(timestamps, windavg2m, 'c-', label='Avg Wind (2 min)')
        ax.plot(timestamps, windgust10m, 'b--', label='Wind Gust (10 min)')
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
        tempfs, timestamps = self.dataToLists('tempf')
        dewpoints, timestamps2 = self.dataToLists('dewpoint')

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,8)
        ax.set_ylabel('Temperature [F]')
        ax.set_xlabel('Time [hours]')
        ax.set_title('Temperature Data')

        #ax.plot(timestamps, windmph, 'b-.', label='Wind Speed')
	    ax.plot(timestamps2, dewpoints, 'm--', label='Dewpoint [F]')
        ax.plot(timestamps, tempfs, 'c-', label='Temp [F]')
        #ax.plot(timestamps2, dewpoints, 'm-', label='Dewpoint [F]')
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

    def run(self):
        currentTime = currentTime = time.strftime("%Y%m%d-%H:%M:%S")
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
        self.plotWind()
        self.upload('wind')
        self.plotTemp()
        self.upload('tempf')

	    for key, value in weatherDict.iteritems():
        	sensorname = key
        	sensortitle = value
        	data, timestamps = wp.dataToLists(sensorname)
        	if sensorname == 'pressure':
	            data = wp.convertPressure(data)
        	#Plot the data
        	wp.plot(sensortitle, 'c', data, timestamps, sensorname)
                wp.upload(sensorname)
	        plt.close('all')
	    return currentTime


if __name__ == "__main__":
    wp = WeatherPlot()
    #Extract the data for a named sensor
    run = True
    while run == True:
        tic = time.clock()
        currentTime = wp.run()
        toc = time.clock()
        elapsedTime = toc - tic
        print 'processing time [s] = '+str(elapsedTime)
        time.sleep(30.0-elapsedTime)
        wp.self.logfile = WeatherInterface.checkDay(currentTime)
