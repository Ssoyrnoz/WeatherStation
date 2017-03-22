#!/usr/bin/python

import cgi
import cgitb 
cgitb.enable()
import sys
import datetime
import time
import os
import cgi
import shutil

shutil.copy('../CloudCamera/testlog.txt', 'testlog.txt')
statusDict = {}
f_in =open ('testlog.txt','r')
for line in f_in:
   (key, val) = line.split('=')
   statusDict[str(key)] = str(val)
f_in.close()
#print statusDict
#rainStatus = ci.rain10m
#heatStatus = ci.heatStatus
print "Content-type:text/html\r\n\r\n"
print '<html>'
print '<head>'
print '<meta http-equiv="cahce-control" content="no-cache">'
print '<meta http-equiv="refresh" content="30"'
print '<title>Cloudunio Sensor Status</title>'
print '</head>'
print ' '
print '<body>'
print '<body onload="updateImage()"  bgcolor="black">'
print '<h2>'
print '<center><font color="blue">Apache Point Observatory Optical  Cloud Camera</font></center>'
print '</h2>'
print ' '
print '<table border="0">'
print '<tr>'
print '<td><a href="latest.png"><img src="http://users.apo.nmsu.edu/~jwhueh/CloudCamera/latest.png" width="400"  name="latest"></a></td>'
print '<td><a href="latest.mp4" width="400"  name="latestgif"><video width="400" height="400" controls>'
print '    <source src="http://users.apo.nmsu.edu/~jwhueh/CloudCamera/latest.mp4" type="video/mp4"></a></td>'
print '<td><font color="white">rain = %s <br>' % str(statusDict['rain'])
if str(statusDict['rain10m']).rstrip('\r').rstrip('\n') == 'True':
    print '<font color = "red">rain [in last 10 min] = %s</font><br>' % str(statusDict['rain10m'])
else:
    print '<font color = "green">rain [in last 10 min] = %s</font><br>' % str(statusDict['rain10m'])	
print 'heat = %s</td><br></font>' % str(statusDict['heat'])
print '</tr>'
print '</table>'
print ' '
print '<br><Br>'
print '<center>'
print '<font color="white">'
print 'Image will auto-refresh<br><br>'
print '</center>'
print '</font>'
print '</body>'
print '</html>'
#time.sleep(5)

