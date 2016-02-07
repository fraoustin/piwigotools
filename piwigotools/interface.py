# -*- coding: utf-8 -*-

import sys
import os
import threading
try:
    import Queue as queue
except:
    import queue
import time

import piwigotools.progressbar as progressbar

class Step(threading.Thread):

    def __init__(self, qin, qout, qerr):
        threading.Thread.__init__(self)
        self.qin = qin
        self.qout = qout
        self.qerr = qerr

    def run(self):
        while not self.qin.empty():
            try:
                call, arg, kw = self.qin.get_nowait()
                try:
                    call(*arg, **kw)
                except Exception as e:
                   self.qerr.put([call, arg, kw, e]) 
                self.qout.put([call, arg, kw])
            except queue.Empty:
                pass
 
class Run:

    def __init__(self, name, cnt=1):
        self._name = name
        self._qin = queue.Queue()
        self._qout = queue.Queue()
        self._qerr = queue.Queue()
        self._threads = [ Step(self._qin, self._qout, self._qerr) for i in range(cnt)] 

    @property
    def error(self):
        """
            return true if _qerr.qsize() > 0
        """
        if self._qerr.qsize() > 0:
            return True
        return False    

    @property
    def strerror(self):
        ret = ""
        while not self._qerr.empty():
            call, arg, kw, e = self._qerr.get_nowait()
            ret = "%s%s\n" % (ret, e) 
        return ret    


    def add(self, call, arg, kw):
        self._qin.put([call, arg, kw])

    def start(self):
        self._qout.maxsize = self._qin.qsize()
        pbar = progressbar.ProgressBar(widgets=['%s ' %  self._name, 
                                    progressbar.Counter() , 
                                    ' on %s ' % self._qin.qsize(), 
                                    progressbar.Bar(), 
                                    ' ', 
                                    progressbar.Timer()],
                            maxval=self._qin.qsize()).start()
        if self._qin.qsize():
            for thread in self._threads:
                thread.start()
            while not self._qout.full():
                time.sleep(0.1) # sleep 0.1s
                pbar.update(self._qout.qsize())
        pbar.finish()    
        return self._qerr

class StepAnalyse(threading.Thread):

    def __init__(self, pbar):
        threading.Thread.__init__(self)
        self._pbar = pbar
        self._stopevent = threading.Event()

    def run(self):
        self._pbar.start()
        i = 0
        while not self._stopevent.isSet():
            try:
                self._pbar.update(i)
                i = i + 1
            except:
                pass
            time.sleep(0.1)

    def stop(self):
        self._stopevent.set()
        self._pbar.finish()

class Analyse:

    def __init__(self, name):
        self._name = name
        pbar = progressbar.ProgressBar(widgets=['%s: ' % name, 
                                            progressbar.AnimatedMarker(), 
                                            ' | ',  
                                            progressbar.Timer()]
                                    )
        self._thread = StepAnalyse(pbar)
    
    def start(self):
        self._thread.start()

    def stop(self):
        self._thread.stop()

def purge_kw(kw, notkw):
    return {k : kw[k] for k in kw if k not in notkw}



