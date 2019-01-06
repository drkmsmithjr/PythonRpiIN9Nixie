#!/usr/bin/python
# the PIGPIO library will connect to hardware PWM 
import pigpio
import sys

import time
import datetime
import math
from time import sleep
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
    self._timer.cancel()
    self.is_running = False


def RampBarNixie(timestr, burntime):
    global DUTY
    global INDEXPOSITIVE
    global DUTY2
    global MAXDUTY
    global MINDUTY
    global pi
    #global pi2

    if INDEXPOSITIVE:
       DUTY = DUTY + 5000
    else:
       DUTY = DUTY - 5000
    if DUTY > MAXDUTY:
       DUTY = 0
    elif DUTY < 0:
       DUTY = MAXDUTY

    if DUTY > MINDUTY:
       pi.hardware_PWM(IO2, FREQ2, 1000000)
    else:
       pi.hardware_PWM(IO2, FREQ2, DUTY2)
    pi.hardware_PWM(IO1, FREQ, DUTY) # Setting the Hardware PWM

# pigpio uses the broadcom numbered GPIO
# BCM GPIO pins to connect to the Sensor 

IO1 = 18
IO2 = 19
IO3 = 15

# frequency set from 1-125000000 (30M is no likely to
FREQ = 1000000
FREQ2 = 50
# duty set from 0 to 1000000 (1M)(fully on)
DUTY = 000000 
# set the brighness to this percent
DUTY2 = 1000000
# the maximum duty is deteremined by sense resistor and NIXIE tube type.   
MAXDUTY = 380000
MINDUTY = 100000
BURNINDUTY = 500000

LoopRate = 0.01

# start timer
rt = RepeatedSyncTimer(LoopRate,RampBarNixie,datetime.datetime.now(), LoopRate)
rt.stop()
RAMPSTARTED = False
 
if __name__ == "__main__":
   
   if len(sys.argv) >= 2:
      print ("A parameter was sent")
      if sys.argv[1] == 'SENT':

#         x = PositionSensor('LX3302A','SENT','IO3')
         Type = 'SENT'
      else:

#         x = PositionSensor('LX3302A','PWM','IO2')
         Type = 'PWM'
   else:

#      x = PositionSensor('LX3302A','PWM','IO2')
      Type = 'PWM'

   print "hello world"
   # Hardware PWM #1 : the signal that the main value will be sent
   pi = pigpio.pi()
   # Hardware PWM #2: the low frequency 50Hz signal 
   #pi2 = pigpio.pi()
   # General GPIO output for enabling 
   #pi2 = pigpio.pi()

   if not pi.connected:
            exit() 

   DUTY = 0
   INDEXPOSITIVE = True
   EXITPROGRAM = False
   SUPPLYON = False

   
   pi.set_mode(IO3,pigpio.OUTPUT)


   while True: 
      print(DUTY)
      print(DUTY2)
      pi.hardware_PWM(IO1, FREQ, DUTY) # Setting the Hardware PWM
      pi.hardware_PWM(IO2, FREQ2, DUTY2)
      #Turn on power supply by pulling low (NIXIE TUBE SUPPLY)
      pi.write(IO3,0)
      SUPPLYON = True
      
      while True:

         
         if DUTY == BURNINDUTY:
            print("The current DUTY is BURNING IN at %s%%" % float(int(DUTY/1000000.0*10000)/100.0))
         else:
            print("The current DUTY is %s%%" % float(int(DUTY/1000000.0*10000)/100.0))
         print("The current DUTY2 is %s%%" % float(int(DUTY2/1000000.0*10000)/100.0))
         if INDEXPOSITIVE:
            print("The index is set to POSITIVE")
         else:
            print("The index is set to NEGATIVE")
         if SUPPLYON:
            print("The supply is ON")
         else:
            print("The supply if OFF")
         print("Press: ")
         print("return: to increase duty +/- 1/2 percent")
         print("[t]: toggle the index polarity")
         print("[d2]: Set the DUTY2 value")
         print("[r]: Ramp the solution up or down")
         print("[l]: loop rate in seconds")
         print("[s]: Toggle the power supply")
         print("[b]: Burn-in DUTY ratio set to %s" % BURNINDUTY)
         print("[x] exit")
         print("ENter the duty ratio in percent (0-%s): " % int(MAXDUTY/10000))
          
         raw_option = raw_input("")
         if len(raw_option) == 0:
            if INDEXPOSITIVE:
               DUTY = DUTY + 5000
            else:
               DUTY = DUTY - 5000
            if DUTY > MAXDUTY:
               DUTY = 0
            elif DUTY < 0:
               DUTY = MAXDUTY
               
            break
         elif raw_option.isdigit():
            # we will start time by writting to first next even number, timer will update from 2,4,6,8
            raw_option = int(raw_option)
            #print(raw_option)
            if (raw_option > 100) or (raw_option < 0):
               print("Please try again: need to input a number between 0-100")   
            else:
               DUTY = int(raw_option/100.0 *1000000)
               #print(DUTY)
               #print(raw_option/100.0)
               break
         elif raw_option == "t":
            if INDEXPOSITIVE:
               INDEXPOSITIVE = False
            else:
               INDEXPOSITIVE = True
         elif raw_option == "x":
            EXITPROGRAM = True
            break
         elif raw_option == "d2":
            while True:
               raw_option2 = raw_input("Enter the duty2 from 0 to 100: ")
               if raw_option2.isdigit():
                  raw_option2 = int(raw_option2)
                  if (raw_option2 > 100) or (raw_option2 < 0):
                     print("Please try again: need to input a number between 0-100")   
                  else:
                     DUTY2 = int(raw_option2/100.0 *1000000)
                     break
               else:
                     print("Please input a digit for DUTY2")  
            break
         elif raw_option == "r":
            if RAMPSTARTED:
               rt.stop()
               RAMPSTARTED = False
               print ("Ramp Stopped")
            else:
               rt.start()
               RAMPSTARTED = True
               print ("Ramp started")
         elif raw_option == "l":
            while True:
               raw_option2 = raw_input("Enter the Loop Rate in Seconds: ")
               try:
                  LoopRate = float(raw_option2)
                  rt.interval = LoopRate
                  print(LoopRate)
                  break
               except ValueError:
                  print("Please input a floating point number")  
            break
         elif raw_option == "s":
            if SUPPLYON:
               SUPPLYON = False
               pi.write(IO3,1)
            else:
               SUPPLYON = True
               pi.write(IO3,0)  
         elif raw_option == "b":
            DUTY = BURNINDUTY
            DUTY2 = 1000000
            break             
         else:
            print("Please try again: need to input an integer")
      
      if EXITPROGRAM:
         pi.hardware_PWM(IO1, FREQ, 0) # Setting the Hardware PWM
         pi.hardware_PWM(IO2, FREQ2, 0)
         # turn off power supply by pulling high
         pi.write(IO3,1)
         rt.stop()
         break
   exit()        
