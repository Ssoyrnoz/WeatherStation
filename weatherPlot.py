from PIL import Image, ImageDraw
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from weather_interface import WeatherInterface
import datetime
import time
import os

class WeatherPlot():
    def __init__(self):
        self.maxtime = 520          #Number of entries to plot
        self.datafile = str(os.getcwd())+'/weather.txt'     #Location of data file
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
        plt.gcf().autofmt_xdate()       #Make dates look pretty in plot
        plt.grid(True)
        fig.tight_layout()
        #plt.show()
        plt.savefig(os.getcwd()+'/'+figname+'.png', bbox_inches='tight')
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
            linedic = self.wi.sortOutput(str(datalist[i]))
            temptime = linedic['timestamp']
            temptime = temptime.strip('\n')
            timeobj = datetime.datetime.strptime(temptime, "%Y%m%d-%H:%M:%S")
            data.append(float(linedic[sensorname]))
            timestamps.append(timeobj)
        return data, timestamps

    def convertPressure(self, pressureData):
        '''
        Convert the pressure data from pascal to inHg
        '''
        atmData = []
        for i in range(len(pressureData)):
            #atmData.append((pressureData[i])/3386.375258)  #inHg
            atmData.append((pressureData[i])/101325.0)     #atm
        return atmData

if __name__ == "__main__":
    wp = WeatherPlot()
    #Extract the data for a named sensor
    weatherDict = {
    #'sensorname': 'sensortitle',
    'tempf': 'Temp [F]',
    'humidity': 'Humidity [%]',
    'pressure': 'Pressure [pascal]',
    #'light_lvl': 'Light Level',
    #'rainin': 'Rain [in]',
    #'dailyrainin': 'Daily Rain [in]',
    #'windgustmph_10m': 'Wind Gust - 10min [mph]',
    #'windspdmph_avg2m': 'Wind Speed - 2min avg [mph]',
    #'windgustmph': 'Wind Gust [mph]',
    #'windspeedmph': 'Wind Speed [mph]'
    }
    '''
    for key, value in weatherDict.iteritems():
    	sensorname = key
    	sensortitle = value
    	data, timestamps = wp.dataToLists(sensorname)
    	#data = wp.convertPressure(data)
    	#Plot the data
    	wp.plot(sensortitle, 'b', data, timestamps, sensorname)
