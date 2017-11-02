# WeatherStation
This software package is used to record and display weather sensor data
from the SparkFun Weather Shield:
https://www.sparkfun.com/products/13956
and the SparkFun Weather Meters:
https://www.sparkfun.com/products/8942

The software dependencies and all required files can be installed automatically
by running 
```
install/make
```
This will install every python dependency 
needed by the code, as well as move files around and set up symbolic links
needed for systemd to run the weather station software at boot.

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

The code is run at boot and monitored for crashing using the systemd service
handler. There are two services that are added when install/make is run,
these services make each of the python scripts run at boot and restart if
the process crashes for any reason.

The weather station processes can be controlled with the following command:

```
sudo systemctl [command] [service]
```

commands:
* start     &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    Immediately starts the process
* stop      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    Immediately stops the process
* restart   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    Stops then starts the process
* enable    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    Enables the process at boot
* disable   &nbsp;&nbsp;&nbsp;&nbsp;    Diables the process at boot

services:
* weather_plot.service
* weather_interface.service
