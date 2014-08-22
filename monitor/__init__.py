#!/usr/bin/python
# -*- coding: utf-8 -*-

# Licence MIT
# Originally licenced under BEER-WARE r42 by Lennart Coopmans <lennartATlacerta.be>

import sys
import ConfigParser


# configuration
config = ConfigParser.SafeConfigParser()

try:
    config.readfp(open('/etc/lwp/lwp.conf'))
except IOError:
    print ' * missed /etc/lwp/lwp.conf file'
    try:
        # fallback on local config file
        config.readfp(open('../lwp.conf'))
    except IOError:
        print ' * cannot read config files. Exit!'
        sys.exit(1)

DEBUG = config.getboolean('global', 'debug')
DATABASE = config.get('database', 'file')

GRAPH_FOLDER = config.get('monitor', 'folder')
GRAPH_DAYS = config.getint('monitor', 'days')

import Gnuplot
import sqlite3
import argparse

from time import time


def generate_mem_chart(c, group, start_time=time() - GRAPH_DAYS * 24 * 60 * 60, end_time=time(), folder=GRAPH_FOLDER):
    c.execute('SELECT time, mem_rss FROM graph_data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',
              (group, start_time, end_time,))
    rss = [[row[0], row[1] / 1024 / 1024] for row in c]
    c.execute('SELECT time, mem_cache FROM graph_data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',
              (group, start_time, end_time,))
    cache = [[row[0], row[1] / 1024 / 1024] for row in c]
    c.execute('SELECT time, mem_swap FROM graph_data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',
              (group, start_time, end_time,))
    swap = [[row[0], row[1] / 1024 / 1024] for row in c]

    for index, value in enumerate(cache):
        cache[index][1] += rss[index][1]

    for index, value in enumerate(swap):
        swap[index][1] += cache[index][1]

    g = Gnuplot.Gnuplot()
    g('set terminal pngcairo enhanced font "arial,10" size 700, 200 ')
    g('set output "%s/%s_mem.png"' % (folder, group, ))
    g('set clip two ')
    g('set xdata time ')
    g('set xtics %d ' % ( (rss[-1][0] - rss[0][0]) / 8,  ))
    g('set timefmt "%s"')
    g('set format x "%d/%m %Hh"')
    g('set xrange [ "%d" : "%d" ]' % ( rss[0][0] - 1000, rss[-1][0] + 1000,  ))
    g('set style fill transparent solid 0.50 noborder ')
    g('set style data filledcurves y1=0')

    swapData = Gnuplot.Data(swap);
    swapData.set_option(using=(1, 2))
    cacheData = Gnuplot.Data(cache);
    cacheData.set_option(using=(1, 2))
    rssData = Gnuplot.Data(rss);
    rssData.set_option(using=(1, 2))
    g.plot(swapData, cacheData, rssData)


def generate_CPU_chart(c, group, start_time=time() - GRAPH_DAYS * 24 * 60 * 60, end_time=time(), folder=GRAPH_FOLDER):
    c.execute('SELECT time, cpu_usage FROM graph_data WHERE name = ? AND TIME BETWEEN ? AND ? ORDER by time',
              (group, start_time, end_time,))
    usage = [[row[0], row[1] / 1024 / 1024] for row in c]

    diff = []
    for i in range(0, len(usage) - 1):
        #t = total[i+1][1]-total[i][1]
        usgdiff = usage[i + 1][1] - usage[i][1]
        #		timediff = usage[i+1][0]-usage[i][0]
        value = []
        value.append(usage[i + 1][0])
        #		value.append(usgdiff * 300 / timediff )
        value.append(usgdiff)
        diff.append(value)

    g = Gnuplot.Gnuplot()
    g('set terminal pngcairo  enhanced font "arial,10" size 700, 200 ')
    g('set output "%s/%s_cpu.png"' % (folder, group, ))
    g('set clip two ')
    g('set xdata time ')
    g('set xtics %d ' % ( (diff[-1][0] - diff[0][0]) / 8,  ))
    g('set timefmt "%s"')
    g('set format x "%d/%m %Hh"')
    g('set xrange [ "%d" : "%d" ]' % ( diff[0][0] - 1000, diff[-1][0] + 1000,  ))
    g('set style fill  transparent solid 0.50 noborder ')
    g('set style data filledcurves y1=0 ')

    usageData = Gnuplot.Data(diff)
    usageData.set_option(using=(1, 2))
    g.plot(usageData)


def clean_database(con, time):
    con.execute('DELETE FROM graph_data WHERE time < ?', (time,))
    con.commit()
    con.execute('VACUUM')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--days', type=int, default=GRAPH_DAYS,
                        help='Parse records from last DAYS days.')
    parser.add_argument('-n', '--noclean', action='store_true',
                        help="Don't clean up database")
    parser.add_argument('-db', '--database', default=DATABASE,
                        help="SQLite database file")
    parser.add_argument('-f', '--folder', default=GRAPH_FOLDER,
                        help="Save charts in FOLDER")
    parser.add_argument('-c', '--containers', nargs='+',
                        help="LXC Containers to create charts for")

    args = parser.parse_args()

    end_time = int(time())
    start_time = end_time - (args.days * 24 * 60 * 60)

    con = sqlite3.connect(args.database)
    c = con.cursor()

    for group in args.containers:
        generate_mem_chart(c, group, start_time, end_time, args.folder)
        generate_CPU_chart(c, group, start_time, end_time, args.folder)

    if not args.noclean:
        clean_database(con, start_time)

    c.close()

if __name__ == "__main__":
    main()
