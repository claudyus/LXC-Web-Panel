# -*- coding: utf-8 -*-
import time, subprocess, sys
from threading import Thread
from Queue import Queue
import lwp.lxclite as lxc

LXC_QUEUE = Queue()
LXC_THREAD = None
WORKER_LOGGER = []

def worker():
    while True:
        item = LXC_QUEUE.get()
        if isinstance(item, WorkerItem):
            item.process()
        LXC_QUEUE.task_done()
        print str(WORKER_LOGGER[0])



def create_thread():
    print " * Creating LXC worker thread"
    LXC_THREAD = Thread(target=worker)
    LXC_THREAD.daemon = True
    LXC_THREAD.start()


## Supported commands are create / destroy / clone / start / stop / freeze / unfreeze / backup
class WorkerItem:
    def __init__(self):
        self.command = None
        self.params = {}
        self.author = None

    def process(self):
        if self.command == "create":
            li = LoggerItem()
            li.author = self.author
            print self.params["storage"]
            try:
                if lxc.create(self.params["container"], template=self.params["template"], storage=self.params["storage"], xargs=self.params["xargs"]) == 0:
                    li.message = u"Container {} created successfully!".format(self.params["container"])
                    li.type = "success"
                else:
                    li.message = u"Failed to create container {}!".format(self.params["container"])
                    li.type = "error"
            except:
                li.message = u"Failed to create container {}: {}!".format(self.params["container"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

        elif self.command == "clone":
            li = LoggerItem()
            li.author = self.author

            try:
                if lxc.destroy(orig=self.params["orig"], new=self.params["new"], snapshow=self.params["snapshot"]) == 0:
                    li.message = u"Container {} cloned successfully into {}!".format(self.params["orig"], self.params["new"])
                    li.type = "success"
                else:
                    li.message = u"Failed to clone container {} into {}!".format(self.params["orig"], self.params["new"])
                    li.type = "error"
            except:
                li.message = u"Failed to clone container {} into {}: {}!".format(self.params["orig"], self.params["new"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

        elif self.command == "destroy":
            li = LoggerItem()
            li.author = self.author

            try:
                if lxc.destroy(self.params["container"]) == 0:
                    li.message = u"Container {} destroyed successfully!".format(self.params["container"])
                    li.type = "success"
                else:
                    li.message = u"Failed to destroy container {}!".format(self.params["container"])
                    li.type = "error"
            except:
                li.message = u"Failed to destroy container {}: {}!".format(self.params["container"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

        elif self.command == "start":
            li = LoggerItem()
            li.author = self.author

            try:
                if lxc.start(self.params["container"]) == 0:
                    li.message = u"Container {} started successfully!".format(self.params["container"])
                    li.type = "success"
                else:
                    li.message = u"Failed to start container {}!".format(self.params["container"])
                    li.type = "error"
            except:
                li.message = u"Failed to start container {}: {}!".format(self.params["container"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

        elif self.command == "stop":
            li = LoggerItem()
            li.author = self.author

            try:
                if lxc.stop(self.params["container"]) == 0:
                    li.message = u"Container {} stopped successfully!".format(self.params["container"])
                    li.type = "success"
                else:
                    li.message = u"Failed to stop container {}!".format(self.params["container"])
                    li.type = "error"
            except:
                li.message = u"Failed to stop container {}: {}!".format(self.params["container"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

        elif self.command == "freeze":
            li = LoggerItem()
            li.author = self.author

            try:
                if lxc.freeze(self.params["container"]) == 0:
                    li.message = u"Container {} frozen successfully!".format(self.params["container"])
                    li.type = "success"
                else:
                    li.message = u"Failed to freeze container {}!".format(self.params["container"])
                    li.type = "error"
            except:
                li.message = u"Failed to freeze container {}: {}!".format(self.params["container"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

        elif self.command == "unfreeze":
            li = LoggerItem()
            li.author = self.author

            try:
                if lxc.unfreeze(self.params["container"]) == 0:
                    li.message = u"Container {} unfrozen successfully!".format(self.params["container"])
                    li.type = "success"
                else:
                    li.message = u"Failed to unfreeze container {}!".format(self.params["container"])
                    li.type = "error"
            except:
                li.message = u"Failed to unfreeze container {}: {}!".format(self.params["container"], str(sys.exc_info()[1]))
                li.type = "error"
            WORKER_LOGGER.append(li)

	# Backup TBD

class LoggerItem:
    def __init__(self):
        self.type = None
        self.message = None
        self.author = None
        self.time = time.time()

    def __str__(self):
        return u"{} ({}) | {} | {}".format(self.message, self.author, self.type, self.time)
