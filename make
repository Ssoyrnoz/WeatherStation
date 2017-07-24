sudo -H apt-get -y install apache2
sudo -H apt-get -y install python-pip
sudo -H pip install --upgrade pip
sudo -H apt-get -y install python-matplotlib
sudo mkdir /var/www/cgi-bin
sudo cp live.py /var/www/cgi-bin/live.py
sudo usermod -a -G dialout matt
