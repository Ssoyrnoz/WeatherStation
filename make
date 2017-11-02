sudo -H apt-get -y install apache2
sudo -H apt-get -y install python-pip
sudo -H pip install --upgrade pip
sudo -H apt-get -y install python-matplotlib
sudo usermod -a -G dialout matt

sudo cp install/webpage/index.html /var/www/html/index.html
sudo cp install/webpage/weather.js /var/www/html/weather.js

sudo ln -s install/services/weather_plot.service /lib/systemd/system/weather_plot.service
sudo ln -s install/services/weather_interface.service /lib/systemd/system/weather_interface.service
sudo systemctl daemon-reload
sudo systemctl enable weather_interface.service
sudo systemctl enable weather_plot.service
