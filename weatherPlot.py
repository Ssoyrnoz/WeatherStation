

from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from weather_interface import WeatherInterface
import datetime
import time
import os

class WeatherPlot():
    def __init__(self):
        self.maxtime = 50           #Number of entries to plot
        self.datafile = str(os.getcwd())+'/weather.txt'     #Location of data file
        self.wi = WeatherInterface()

    def plot(self, sensorname, color, timestamp, sensordata):
        #Generic plotting routine

        fig,ax=plt.subplots(1)
        fig.set_size_inches(8,8)
        ax.set_ylabel(str(sensorname))
        ax.set_xlabel('Time [hours]')
        ax.set_title(str(sensorname))

        ax.plot(timestamp, sensordata, color+'.')
        plt.gcf().autofmt_xdate()
        #ax.legend( loc='upper right', ncol=1, shadow=True, numpoints = 3 )
        plt.grid(True)
        fig.tight_layout()
        plt.show()
        return

    def dataToLists(self, sensorname):
        '''
        sort the data from each line in the data file
        and extract the data for a specific sensor
        '''
        data = open(self.datafile,'r')
        datalist = data.readlines()
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

if __name__ == "__main__":
    wp = WeatherPlot()
    #Extract the data for a named sensor
    '''
    sensorname, sensortitle
    tempf, Temp [F]
    humidity, Humidity [%]
    pressure, Pressure [pascal]
    light_lvl, Light Level
    rainin, Rain [in]
    dailyrainin, Daily Rain [in]
    windgustmph_10m, Wind Gust - 10min [mph]
    windspdmph_avg2m, Wind Gust - 2min avg [mph]
    windgustmph, Wind Gust [mph]
    windspeedmph, Wind Speed [mph]
    '''
    data, timestamps = wp.dataToLists('humidity')
    #Plot the data
    wp.plot('Humidity', 'b', timestamps, data)
