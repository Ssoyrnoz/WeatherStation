# WeatherStation
This software package is used to record and display weather sensor data
from the SparkFun Weather Shield:
https://www.sparkfun.com/products/13956
and the SparkFun Weather Meters:
https://www.sparkfun.com/products/8942

The sensor data is collected from an attached Arduino board through a USB
serial connection. These data are collected using the weather_interface.py
program. The data are stored in logs/YYYYMMDD-weather.txt

The data are plotted by a seperate program called plotWeather.py
This program reads the log files and collects the last n hours of data.
The data are sorted and plotted using matplotlib and saved to the working
directory and /var/www/html for live display usage.

A user interface to display the data is available by pointing a web browser
on the same local network to the ip of the weather station computer.
These data are displayed using a JavaScript webpage to provide live
and continuously updating data with minimal computing overhead and broad
compatability with most internet browsers.
