LXC Monitoring
=======
LXC Monitoring collects cpu and memory statistics for several Linux Containers,
and creates pretty charts with it. Although it is intended for LXC containers,
it can be used to monitor any type of cgroup.

Optionally it can be configured to send a daily/weekly/... mail with those
charts.


REQUIREMENTS
=======
* SQLite v3
* Gnuplot (nox is ok)
* Python
* Python Gnuplot (http://gnuplot-py.sourceforge.net/)

  E.g.:
  apt-get install sqlite3 gnuplot-nox python python-gnuplot
  
  Note:
  The python-gnuplot package will install gnuplot-x11 on Ubuntu. If you don't
  want that, download gnuplot-py's source, change the default_term value in
  gp_unix.py to "png", compile and install.


INSTALLATION
=======
There are 2 files needed, a data poller and a chart generator.

Copy the files to the host server, open it in a text editor and change the
default configuration parameters (or use command line options). It's pretty
self-explanatory.

Initialize the database file:

	python /path/to/data_poller.py --init

Add the data poller script to the crontab:

	*/5 * * * * python /path/to/data_poller.py

This will collect data every 5 minutes and store it in the sqlite database you
configured.

If you want the charts to be generated automatically, add it to the crontab:

	0 3 * * 1 python /path/to/generate_charts.py

This will generate the charts every monday morning at 3 am. If you want to 
receive a nice mail with all the charts, add the -m option:

	0 3 * * 1 python /path/to/generate_charts.py -m

USAGE
=======
The default parameters can be overridden through command line options:

	usage: generate_charts.py [-h] [-d DAYS] [-n] [-db DATABASE] [-f FOLDER]
	                          [-b BASEURL] [-c CONTAINERS [CONTAINERS ...]] [-m]
	                          [-r RECIPIENTS [RECIPIENTS ...]]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -d DAYS, --days DAYS  Parse records from last DAYS days.
	  -n, --noclean         Don't clean up database
	  -db DATABASE, --database DATABASE
	                        SQLite database file
	  -f FOLDER, --folder FOLDER
	                        Save charts in FOLDER
	  -b BASEURL, --baseurl BASEURL
	                        Base URL
	  -c CONTAINERS [CONTAINERS ...], --containers CONTAINERS [CONTAINERS ...]
	                        LXC Containers to create charts for
	  -m, --mail            Send mail with the charts
	  -r RECIPIENTS [RECIPIENTS ...], --recipients RECIPIENTS [RECIPIENTS ...]
	                        Mail recipients
	

	usage: data_poller.py [-h] [-db DATABASE] [-c CONTAINERS [CONTAINERS ...]]
	                      [--init]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -db DATABASE, --database DATABASE
	                        SQLite database file
	  -c CONTAINERS [CONTAINERS ...], --containers CONTAINERS [CONTAINERS ...]
	                        LXC Containers to create charts for
	  --init                Initialize the database
	
	  
LICENSE
=======
"THE BEER-WARE LICENSE" (Revision 42):
[lennartATlacerta.be] wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return. Lennart Coopmans
