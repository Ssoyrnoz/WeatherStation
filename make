sudo -H apt-get -y install apache2
sudo -H apt-get -y install python-pip
sudo -H pip install --upgrade pip
sudo -H apt-get -y install python-matplotlib
sudo mkdir /var/www/cgi-bin
sudo cp live.py /var/www/cgi-bin/live.py
sudo usermod -a -G dialout matt

sudo ln -s services/weather_plot.service /lib/systemd/system/weather_plot.service
sudo ln -s services/weather_interface.service /lib/systemd/system/weather_interface.service
sudo systemctl daemon-reload
sudo systemctl enable weather_interface.service
sudo systemctl enable weather_plot.service
