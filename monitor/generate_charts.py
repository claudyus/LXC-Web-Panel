#!/usr/bin/python

################################################################################
# "THE BEER-WARE LICENSE" (Revision 42):                                       #
# <lennartATlacerta.be> wrote this file. As long as you retain this notice you #
# can do whatever you want with this stuff. If we meet some day, and you think #
# this stuff is worth it, you can buy me a beer in return. Lennart Coopmans    #
################################################################################

################################################################################
# DEFAULT CONFIGURATION                                                        #
################################################################################

def_sqlitedb = "lxc_monitor.db";
def_folder = "/var/www/charts/"
def_containers = ["container1", "container2"]
def_baseURL = "http://lacerta.be/charts/"
def_recipients = ["you@yourdomain"]
def_fromAddress = "noreply"
def_days = 7

################################################################################
# CODE - DON'T TOUCH UNLESS YOU KNOW WHAT YOU'RE DOING                         #
################################################################################

import Gnuplot
import sqlite3
import smtplib
import argparse

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import COMMASPACE
from time import time


def generateMemChart(c, group, starttime, endtime, folder):
	c.execute('SELECT time, mem_rss FROM data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',(group,starttime,endtime,))
	rss=[[row[0], row[1]/1024/1024] for row in c]
	c.execute('SELECT time, mem_cache FROM data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',(group,starttime,endtime,))
	cache=[[row[0], row[1]/1024/1024] for row in c]
	c.execute('SELECT time, mem_swap FROM data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',(group,starttime,endtime,))
	swap=[[row[0], row[1]/1024/1024] for row in c]
	
	for index, value in enumerate(cache):
		cache[index][1] += rss[index][1]
	
	for index, value in enumerate(swap):
		swap[index][1] += cache[index][1]
	
	g = Gnuplot.Gnuplot()
	g('set terminal pngcairo enhanced font "arial,10" size 700, 200 ')
	g('set output "%s/%s_mem.png"' % (folder, group, ))
	g('set clip two ')
	g('set xdata time ')
	g('set xtics %d ' % ( (rss[-1][0]-rss[0][0])/8,  ))
	g('set timefmt "%s"')
	g('set format x "%d/%m %Hh"')
	g('set xrange [ "%d" : "%d" ]' % ( rss[0][0]-1000,rss[-1][0]+1000,  ))
	g('set style fill transparent solid 0.50 noborder ')
	g('set style data filledcurves y1=0')

	swapData = Gnuplot.Data(swap);
	swapData.set_option(using=(1,2))
	cacheData = Gnuplot.Data(cache);
	cacheData.set_option(using=(1,2))
	rssData = Gnuplot.Data(rss);
	rssData.set_option(using=(1,2))
	g.plot(swapData,cacheData,rssData)

def generateCPUChart(c, group, starttime, endtime, folder):
	c.execute('SELECT time, cpu_usage FROM data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',(group,starttime,endtime,))
	usage=[[row[0], row[1]/1024/1024] for row in c]

	diff = []
	for i in range(0,len(usage)-1):
		#t = total[i+1][1]-total[i][1]
		usgdiff = usage[i+1][1]-usage[i][1]
#		timediff = usage[i+1][0]-usage[i][0]
		value = []
		value.append(usage[i+1][0])
#		value.append(usgdiff * 300 / timediff ) 
		value.append(usgdiff) 
		diff.append(value)
	
	g = Gnuplot.Gnuplot()
	g('set terminal pngcairo  enhanced font "arial,10" size 700, 200 ')
	g('set output "%s/%s_cpu.png"' % (folder, group, ))
	g('set clip two ')
	g('set xdata time ')
	g('set xtics %d ' % ( (diff[-1][0]-diff[0][0])/8,  ))
	g('set timefmt "%s"')
	g('set format x "%d/%m %Hh"')
	g('set xrange [ "%d" : "%d" ]' % ( diff[0][0]-1000,diff[-1][0]+1000,  ))
	g('set style fill  transparent solid 0.50 noborder ')
	g('set style data filledcurves y1=0 ')

	usageData = Gnuplot.Data(diff);
	usageData.set_option(using=(1,2))
	g.plot(usageData)
		
def sendMail(groups, recipients, baseurl):
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "Lacerta LXC Monitor"
	msg['To'] = COMMASPACE.join(recipients)

	html = """\
	<body style="padding: 20px">
	<div style="background-color: #2f2f2f; width: 720px; padding: 10px; margin-left: 20px; font-family: 'Helvetica Neue', Helvetica, Arial, Geneva, sans-serif;">
	<div>
	<div style="float: left"><a href="http://lacerta.be">
	<img class="site-logo" src="http://lacerta.be/d7/custom/lacerta.png" alt="Lacerta"/>
	</a>
	</div>
	<h2 style="color: #FAFAFA; padding: 0; margin: 0; font-size: 1.8em">Lacerta</h2>
	<h3 style="color: #FAFAFA; padding: 0; margin: 0; font-size: .8em">LXC Monitoring</h3>
	</div>
	<div style="clear: both">
	"""
	for group in groups:
		html+='<div style="background-color: #FFF; padding: 10px; margin-top: 10px;">'
		html+='<h3 style="font-size: 1em; margin: .2em 0">%s</h3>' % (group,)
		html+='<h4 style="font-size: .7em; margin: .2em 0; float: left; clear: left;">Memory (MB):</h4>'
		html+= """
		<ul style="float: left; list-style-type: none; margin: 0">
			<li style="font-size: .7em;  display: inline; padding-left: 5px; border-left: 10px solid #3f5f9f">RSS</li>
			<li style="font-size: .7em;  display: inline; padding-left: 5px; border-left: 10px solid #7fbf3f">Cache</li>
			<li style="font-size: .7em;  display: inline; padding-left: 5px; border-left: 10px solid #ff7f7f">Swap</li>
		</ul>
		"""
		html+='<img src="%s/%s_mem.png"/>' % (baseurl,group)
		html+='<h4 style="font-size: .7em; margin: .2em 0; float: left; clear: left;">CPU Usage (per 5m):</h4>'
		html+='<img src="%s/%s_cpu.png"/>' % (baseurl,group)
		html+='</div>'
		html+="\n"
	
	html += "</div></div></body>"

	part = MIMEText(html, 'html')
	msg.attach(part)
	s = smtplib.SMTP('localhost')
	s.sendmail(def_fromAddress, recipients, msg.as_string())
	s.quit()
	
def cleanDatabase(con, time):
	con.execute('DELETE FROM data WHERE time < ?',(time,))
	con.commit()
	con.execute('VACUUM')
	
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--days', type=int, default=def_days,
						help='Parse records from last DAYS days.')
	parser.add_argument('-n', '--noclean', action='store_true',
						help="Don't clean up database")
	parser.add_argument('-db','--database', default=def_sqlitedb,
						help="SQLite database file")
	parser.add_argument('-f','--folder', default=def_folder,
						help="Save charts in FOLDER")
	parser.add_argument('-b', '--baseurl', default=def_baseURL,
						help="Base URL")
	parser.add_argument('-c', '--containers', nargs='+', default=def_containers,
						help="LXC Containers to create charts for")
	parser.add_argument('-m', '--mail', action='store_true',
						help='Send mail with the charts')
	parser.add_argument('-r', '--recipients', nargs='+', default=def_recipients,
						help="Mail recipients")
	
	args = parser.parse_args()
	
	endtime = int(time())
	starttime = endtime - (args.days*24*60*60)
	
	con = sqlite3.connect(args.database)
	c = con.cursor()

	for group in args.containers:
		generateMemChart(c, group, starttime, endtime, args.folder)
		generateCPUChart(c, group, starttime, endtime, args.folder)

	if not args.noclean:
		cleanDatabase(con, starttime)
		
	c.close()
	
	if args.mail:
		sendMail(args.groups, args.recipients, args.baseurl)
	
if __name__ == "__main__":
    main()
