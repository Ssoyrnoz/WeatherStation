sudo apt-get -y install apache2
sudo apt-get -y install python-pip
sudo pip install --upgrade pip
sudo apt-get -y install python-matplotlib
sudo mkdir /var/www/cgi-bin
sudo cp live.py /var/www/cgi-bin/live.py
sudo usermod -a -G dialout mroweather
