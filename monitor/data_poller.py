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
def_containers = ["container1", "container2"]

################################################################################
# CODE - DON'T TOUCH UNLESS YOU KNOW WHAT YOU'RE DOING                         #
################################################################################
import sqlite3
import argparse
from time import time

def collecData(con, group, timestamp):
        cpu_uage = 0
        mem_rss = 0
        mem_cache = 0
        mem_swap = 0

        with open('/cgroup/%s/memory.stat' % (group,), 'r') as f:
                lines = f.read().splitlines()

        for line in lines:
                data = line.split()
                if data[0] == "total_rss":
                        mem_rss = int(data[1])
                elif data[0] == "total_cache":
                        mem_cache = int(data[1])
                elif data[0] == "total_swap":
                        mem_swap = int(data[1])

        with open('/cgroup/%s/cpuacct.usage' % (group,), 'r') as f:
                cpu_usage = int(f.readline())

        con.execute("""\
                INSERT INTO data (name, time, cpu_usage, mem_rss, mem_cache, mem_swap)
                VALUES (?,?,?,?,?,?)""", (group, timestamp, cpu_usage, mem_rss, mem_cache, mem_swap) )

def initDatabase(con):
        con.execute("""\
                CREATE TABLE data (
                  name TEXT NOT NULL,
                  time INTEGER NOT NULL,
                  cpu_usage INTEGER,
                  mem_rss INTEGER,
                  mem_cache INTEGER,
                  mem_swap INTEGER,
                  PRIMARY KEY (name,time)
                )
        """)

def main():
        parser = argparse.ArgumentParser()
        parser.add_argument('-db','--database', default=def_sqlitedb,
                                 help="SQLite database file")
        parser.add_argument('-c', '--containers', nargs='+', default=def_containers,
                                 help="LXC Containers to create charts for")
        parser.add_argument('--init', action='store_true',
                                 help="Initialize the database")

        args = parser.parse_args()

        con = sqlite3.connect(args.database)

        if args.init:
                initDatabase(con)
        else:
                for group in args.containers:
                        collecData(con, group, int(time()))

        con.commit()
        con.close()

if __name__ == "__main__":
	main()