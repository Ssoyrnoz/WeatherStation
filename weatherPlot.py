

from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from weather_interface import WeatherInterface
import datetime
import time
import os

class WeatherPlot():
    def __init__(self):
        self.maxtime = 50
        self.datafile = str(os.getcwd())+'/weather.txt'
        self.wi = WeatherInterface()

    def plot(self, sensorname, color, timestamp, sensordata):

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
        data = open(self.datafile,'r')
        datalist = data.readlines()

        checktime = datetime.datetime.now()
        timestamps = []
        data = []
        for i in range(self.maxtime):
            linedic = self.wi.sortOutput(str(datalist[i]))
            temptime = linedic['timestamp']
            temptime = temptime.strip('\n')
            #print temptime
            #print '-------------'
            #timest = float(str(temptime[6:8])+str(temptime[9:11]))+float((1.0/60.0)*int(temptime[12:14]))+float((1.0/3600.0)*int(temptime[15:17]))
            timeobj = datetime.datetime.strptime(temptime, "%Y%m%d-%H:%M:%S")
            #print timeobj

            #if datetime_object < checktime:
            data.append(float(linedic[sensorname]))
            timestamps.append(timeobj)
        #timestamps[:] = [x - min(timestamps) for x in timestamps]
        return data, timestamps

if __name__ == "__main__":
    wp = WeatherPlot()
    data, timestamps = wp.dataToLists('humidity')
    #print "data = "+str(data)
    #print "timestamps = "+str(timestamps)
    wp.plot('Humidity', 'b', timestamps, data)
