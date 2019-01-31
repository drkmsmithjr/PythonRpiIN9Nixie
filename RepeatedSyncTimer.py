#!/usr/bin/python

import math
import time
from threading import Timer  

# this timer will sychronize to system time time.time().   Great for clocks but for RAMPING the scope
class RepeatedSyncTimer(object):
  def __init__(self, interval ,function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.error = 0.0
    # set this so that the interval is at 50% 0f a second, for clock to update
    # only needed if we have seconds
    self.next_call = math.ceil(time.time()) + 0.5
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args,**self.kwargs)

  def start(self):
    if not self.is_running:
      #syncronize the interval to 50% to allow to account for errors in the timer.
      #the timer interval is adjusted to sychronize with real time.  
      # this is important for clocks.  Above this was set at 50% of the interval
      self.next_call += self.interval
      # test to see if next call if negative.  if so,then set for 0.1 second
      if (self.next_call - time.time()) < 0:
         self.next_call = time.time() + 0.1
      self._timer = Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    #check to see that the timer is running.   
    if self.is_running:
       self._timer.cancel()
       self.is_running = False
       return True
    else:
       return False
