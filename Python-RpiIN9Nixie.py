#!/usr/bin/python

#Python-RpiIN9Nixie:    
# a python class that will work with the Rpi-IN9-NIXIE-Bar Graph hat 
# this file can be run by it self for burn in and testing of Nixies
# or as a class with use in another program.    

# the PIGPIO library will connect to hardware PWM 
# this required that 'sudo pigpiod' damean be started.
import pigpio
import sys

import time
import datetime
import math
from time import sleep
from threading import Timer   

from RepeatedSyncTimer import RepeatedSyncTimer


# Parameters for the Raspberry PI Zero / or B+

# pigpio uses the broadcom numbered GPIO
# BCM GPIO pins to connect to the Sensor 
# hardware PWM #0
IO1 = 18
# hardware PWM #1
IO2 = 19
# GPIO output
IO3 = 15

# frequency set from 1-125000000.   1MHz
FREQ = 1000000
# set hardware PWM#2 to 50Hz
FREQ2 = 50

# the maximum duty is 100% for RPI is 1M   
MAXDUTY = 1000000
MINDUTY = 0

# Default loop rate
LoopRate = 0.01


#default parameters set for IN-9
# defined in milliamps
MaxCURRENT = 12
BurnINCURRENT = 15
# one percent equates to .33mA with 100 ohm sense resistor with 3.3v PWM output voltage. 
DUTYCURRENTGAIN = (1.0/1000/3/10000)


class RpiIN9Nixie(object):
  def __init__(self, MaxCurrent = MaxCURRENT, BurnInCurrent = BurnINCURRENT, DutyToCurrentGain = DUTYCURRENTGAIN, InitCurrent = 1.0):
    # Current is defined in Milliamps.  
    self.MaxCurrent= MaxCurrent/1000.0 
    self.BurnInCurrent = BurnInCurrent/1000.0
    self.DutyGain = DutyToCurrentGain
    # initiate a gpio instance
    self.pi = pigpio.pi()
    # initate to current to 1ma
    self.InitCurrent = InitCurrent/1000.0
    DutyInit = (self.InitCurrent/self.DutyGain)
    self.pi.hardware_PWM(IO1, FREQ, DutyInit) # Setting the Hardware PWM
    # initate PWM2 to 100% duty
    self.DimmerDuty = 100
    self.pi.hardware_PWM(IO2, FREQ2, int(self.DimmerDuty/100.00*1000000))
    # initiate the power supply
    self.pi.write(IO3,0)
    self.Supply = True
    self.BurnIn = False
    self.current = self.InitCurrent
    self.INDEXPOSITIVE = True

    # start timer
    self.rt = RepeatedSyncTimer(LoopRate,self.RampBarNixie,datetime.datetime.now(), LoopRate)
    self.RampStop()
    self.RAMPSTARTED = False

    # setup timer for ramp function
    
  def RampBarNixie(self,timestr, burntime):
    #global pi2
    if self.INDEXPOSITIVE:
       barnixie.IncrementCurrent(0.5)
    else:
       barnixie.IncrementCurrent(-0.5)

  def RampStart(self):
    self.rt.start()
    self.RAMPSTARTED = True

  def RampStop(self):
    self.rt.stop()
    self.RAMPSTARTED = False

  def isRampStarted(self):
    if self.RAMPSTARTED:
       return True
    else:
       return False
  
  def SetCurrent(self,current):
    # current is given in mAmp. That is the reason it is divided by 1000
    self.current = current/1000.0
    # clamp current to range if it is outside range. Return True if inside range, False if outside
    if self.current <= self.MaxCurrent and self.current >= 0:
       Duty = int(self.current/self.DutyGain)
       self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM
       return True
    else:
       self.IncrementCurrent(0,False)
       Duty = int(self.current/self.DutyGain)
       self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM
       return False

  def SetCurrentPercent(self,CurrentPercent):
     # percent will need to be between 0 and 100 otherwise it will clamp and return false
     if CurrentPercent <= 100 and CurrentPercent >= 0:
        self.current = self.MaxCurrent*CurrentPercent/100 
        Duty = int(self.current/self.DutyGain)
        self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM
        return True
     elif CurrentPercent > 100:
        self.current = self.MaxCurrent
        Duty = int(self.current/self.DutyGain)
        self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM
        return False
     else:
        self.current = 0
        Duty = int(self.current/self.DutyGain)
        self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM
        return False 

  def IncrementCurrent(self,percent,Loop = True):
    # increment the current based on max current.  percent can be both positive or negative
    # default to looping the current if it reaches zero or end
    IncCurrent = percent/100*self.MaxCurrent
    self.current = self.current + IncCurrent
    if Loop:
       if self.current > self.MaxCurrent:
          self.current = 0
       elif self.current < 0:
          self.current = self.MaxCurrent
       self.SetCurrent(self.current*1000)
    else:
       if self.current > self.MaxCurrent:
          self.current = self.MaxCurrent
       elif self.current < 0:
          self.current = 0
       self.SetCurrent(self.current*1000)       

  def SetDimmerDuty(self,DUTY2):
    # DUTY is given as percentage.  1M in Pi will be 100%
    self.DimmerDuty = DUTY2
    self.pi.hardware_PWM(IO2, FREQ2, int(self.DimmerDuty/100.00*1000000))

  def BurnInOn(self):
    BurnInDuty = int(self.BurnInCurrent/self.DutyGain)
    self.SetDimmerDuty(100)
    self.pi.hardware_PWM(IO1,FREQ, BurnInDuty)
    self.BurnIn = True

  def BurnInOff(self):
    #return currents and duty back to what they were before the burnin
    self.SetDimmerDuty(self.DimmerDuty)
    Duty = int(self.current/self.DutyGain)
    self.pi.hardware_PWM(IO1,FREQ, Duty)
    self.BurnIn = False

  def IsBurnIn(self):
    if self.BurnIn:
       return True
    else:
       return False

  def SupplyOff(self): 
    self.pi.write(IO3,1)
    self.Supply = False

  def SupplyOn(self):
    self.pi.write(IO3,0)
    self.Supply = True

  def IsSupplyOn(self):
    if self.Supply:
       return True
    else:
       return False




 
if __name__ == "__main__":
   print "hello world"

   EXITPROGRAM = False
   
   barnixie = RpiIN9Nixie( InitCurrent = 3, MaxCurrent = 13)
   sleep(1)
   if barnixie.SetCurrentPercent(95):
      print("OK")
   else:
      print("Needed to clamp current")
   sleep(.1)
   barnixie.SetCurrentPercent(10)
   sleep(.1)
   barnixie.SetDimmerDuty(30)
   sleep(.1)
   barnixie.SetDimmerDuty(100)
   sleep(.1)
   barnixie.BurnInOn()
   sleep(.2)
   barnixie.BurnInOff()
   sleep(.2)
   #barnixie.SupplyOff()
   while EXITPROGRAM == False:
      while True:         
         if barnixie.IsBurnIn():
            print("The Nixie Current is Burning In at %smA which is %s%%" % (float(barnixie.BurnInCurrent*1000), float(barnixie.BurnInCurrent/barnixie.MaxCurrent*100)))
         else:
            print("The Nixie Current is %sma which is %s%%" % (float(barnixie.current*1000), float(barnixie.current/barnixie.MaxCurrent*100))) 
         print("The Dimmer Percentage is : %s" % float(barnixie.DimmerDuty))
         if barnixie.INDEXPOSITIVE:
            print("The index is set to POSITIVE")
         else:
            print("The index is set to NEGATIVE")   
         if barnixie.IsSupplyOn():
            print("The supply is ON")
         else:
            print("The supply if OFF")
         print("Press: ")
         print("return: to increase duty +/- 1/2 percent")
         print("[t]: toggle the index polarity")
         print("[d]: Set the Dimmer")
         print("[r]: Ramp the solution up or down")
         print("[l]: loop rate in seconds")
         print("[s]: Toggle the power supply")
         print("[b]: Burn-in current is set to %smA" % int(barnixie.BurnInCurrent*1000))
         print("[x] exit")
         print("ENter the Percent Current to power (0-100%): ")
          
         raw_option = raw_input("")
         # increment 
         if len(raw_option) == 0:
            if barnixie.INDEXPOSITIVE:
               barnixie.IncrementCurrent(0.5)
            else:
               barnixie.IncrementCurrent(-0.5)
            break
         elif raw_option == "t":
            if barnixie.INDEXPOSITIVE:
               barnixie.INDEXPOSITIVE = False
            else:
               barnixie.INDEXPOSITIVE = True
         elif raw_option == "d":
            while True:
               raw_option2 = raw_input("Enter the Dimmer percent (0-100): ")
               if raw_option2.isdigit():
                  raw_option2 = int(raw_option2)
                  if (raw_option2 > 100) or (raw_option2 < 0):
                     print("Please try again: need to input a number between 0-100")   
                  else:
                     barnixie.SetDimmerDuty(raw_option2)
                     break
               else:
                     print("Please input a digit for Dimmer Percentage")  
            break
         elif raw_option == "s":
            if barnixie.IsSupplyOn():
               barnixie.SupplyOff()
            else:
               barnixie.SupplyOn()
         elif raw_option == "b":
            if barnixie.IsBurnIn():
               barnixie.BurnInOff()
            else:
               barnixie.BurnInOn()  
         elif raw_option.isdigit():
            raw_option = int(raw_option)
            if (raw_option > 100) or (raw_option < 0):
               print("Please try again: need to input a number between 0-100")   
            else:
               barnixie.SetCurrentPercent(raw_option)
               break   
         elif raw_option == "r":
            if barnixie.isRampStarted():
               barnixie.RampStop()
               print ("Ramp Stopped")
            else:
               barnixie.RampStart()
               print ("Ramp started")
         elif raw_option == "l":
            while True:
               raw_option2 = raw_input("Enter the Loop Rate in Seconds: ")
               try:
                  LoopRate = float(raw_option2)
                  barnixie.rt.interval = LoopRate
                  print(LoopRate)
                  break
               except ValueError:
                  print("Please input a floating point number")                       
         elif raw_option == "x":
            EXITPROGRAM = True
            if barnixie.isRampStarted():
               barnixie.RampStop()
            barnixie.SetCurrentPercent(10)
            barnixie.SupplyOff()
            break
         else:
            print("Please input a digit for Current Percentage")
      
   exit()        
