
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

freezing = "green"
humid = "green"

statusDict = {}
dataList = []
f_in = open('live.txt','r')
dataList = f_in.split(',')
f_in.close()
for i in range(len(dataList)):
   (key, val) = dataList[i].split('=')
   statusDict[str(key)] = str(val)

print "Content-type:text/html\r\n\r\n"
print '<html>'
print '<head>'
print '<meta http-equiv="cahce-control" content="no-cache">'
print '<meta http-equiv="refresh" content="30"'
print '<title>Hermitage Weather Station</title>'
print '</head>'
print ' '
print '<body>'
print '<body onload="updateImage()"  bgcolor="black">'
print '<h2>'
print '<center><font color="blue">Hermitage Weather Station - v0.2</font></center>'
print '</h2>'
print ' '

if float(statusDict['tempf']) < 32.0:
    freezing = "blue"
else:
    freezing = "green"
print 'Temperature [F] = '+'<font color=\"'+freezing+'\">'+statusDict['tempf']+'</font>'
print '<br>'

if float(statusDict['humidity']) >= 95.0:
    humid = "red"
elif float(statusDict['humidity']) > 80.0 and float(statusDict['humidity']) < 95.0:
    humid = "yellow"
else:
    humid = "green"
print 'Humidity [%] ='+'<font color=\"'+humid+'\">'+statusDict['humidity']+'</font>'
print '<td><a href="latest.png"></a></td>'
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

