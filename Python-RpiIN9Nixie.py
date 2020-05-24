#!/usr/bin/python

#Python-RpiIN9Nixie:    
# a python class that will work with the Rpi-IN9-NIXIE-Bar Graph hat 
# this file can be run by it self for burn in and testing of Nixies
# or as a class with use in another program.  
# by default, the class can handle two NIXIE Tubes at one time.  One is called Left and the Other is a Right.  

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
# hardware PWM #0 for First Nixie bar Graph (Left)
IO1 = 18
# low frequency PWM for First Nixie Bar Graph (Left) (range is 0-255)
IO4 = 14
# hardware PWM #1 for Second Nixie Bar Graph (Right)
IO2 = 13
# Low frequency PWM for Second Nixie Bar Graph (Right) (range is 0-255)
IO5 = 6
# GPIO output
IO3 = 15

# frequency set from 1-125000000.   1MHz
FREQ = 1000000
# set hardware PWM#2 to 50Hz (low frequency PWM)
FREQ2 = 50

# the maximum duty is 100% for RPI is 1M   
MAXDUTY = 1000000
MINDUTY = 0

# Default loop rate
LoopRate = 0.02

# one percent equates to .33mA with 100 ohm sense resistor with 3.3v PWM output voltage.
# one percent equates to 
# hardware PWM with PIGIO specifies duty at 1-1e6.   1% is 10000
# load resistor Rs is 133 ohms.
# power supply is 3.3v.
# Gain is 3.3v/Rs /(Scalling fActor).   The Scalling factor for hardware PWM using PIGPIO is 1000000
DUTYCURRENTGAIN = (3.3/133/1000000)

class RpiIN9Nixie(object):
  def __init__(self, MaxCurrent = 3, BurnInCurrent = 3, DutyToCurrentGain = DUTYCURRENTGAIN, InitCurrent = 1.0, MaxSupplyCurrent = 18.5):
    # Current is defined in Milliamps.  
    self.MaxCurrent= MaxCurrent/1000.0 
    self.BurnInCurrent = BurnInCurrent/1000.0
    self.DutyGain = DutyToCurrentGain
    # define the maximum supply current that the power supply can support
    self.MaxSupplyCurrent = MaxSupplyCurrent/1000.0
    # initiate a gpio instance
    self.pi = pigpio.pi()
    # initate to current to 1ma
    self.InitCurrent = InitCurrent/1000.0
    DutyInit = (self.InitCurrent/self.DutyGain)
    # Setting the Hardware PWM (pwm #0 - Left)
    self.pi.hardware_PWM(IO1, FREQ, DutyInit) 
    # setting second Hardware pwm (pwm #1 - Right)
    self.pi.hardware_PWM(IO2, FREQ, DutyInit)
    # how much the right channel is compared to the left in percent
    #self.LefttoRightOffset = -8 
    # initate the low frequency PWMs of both channels (Left and Right) to 100% duty
    self.DimmerDutyLeft = 100
    self.DimmerDutyRight = 100
    self.pi.set_PWM_frequency(IO4,FREQ2)    # Left 
    self.pi.set_PWM_frequency(IO5,FREQ2)    # Right
    self.pi.set_PWM_dutycycle(IO4, int(self.DimmerDutyLeft/100.00*255)) #Left
    self.pi.set_PWM_dutycycle(IO5, int(self.DimmerDutyRight/100.00*255)) #right
    # initiate the power supply
    self.pi.write(IO3,0)
    self.Supply = True
    # burnin true if either channel is being burned in
    self.BurnIn = False
    self.currentLeft = self.InitCurrent
    self.currentRight = self.InitCurrent
    self.INDEXPOSITIVE = True

    # start timer
    self.rt = RepeatedSyncTimer(LoopRate,self.RampBarNixie)
    self.RampStop()
    self.RAMPSTARTED = False

    # setup timer for ramp function
    
  def RampBarNixie(self):
    #global pi2
    if self.INDEXPOSITIVE:
       barnixie.IncrementCurrent(2.0)
    else:
       barnixie.IncrementCurrent(-2.0)

  def RampStart(self):
    self.rt.start()
    self.RAMPSTARTED = True

  def RampStop(self):
    # We may need to test the thread several times to stop the time
    for x in range (0,200):
       if self.rt.stop():
          break
       else:
          print("Failed to stop")
    self.RAMPSTARTED = False

  def isRampStarted(self):
    if self.RAMPSTARTED:
       return True
    else:
       return False
  
  def SetCurrent(self, current, Channel = "both"):
    # current is given in mAmp. That is the reason it is divided by 1000
    current = current/1000.0
    # by default, adjust both channels.    (left, right, both)
    # clamp current to range if it is outside range. Return True if inside range, False if outside
    if current <= self.MaxCurrent and current >= 0:
       Duty = int(current/self.DutyGain)
       if Channel == "both":
          self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
          self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
          self.currentLeft = current
          self.currentRight= current
       elif Channel == "left":
          self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
          self.currentLeft = current
       elif Channel == "right":
          self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
          self.currentRight = current
       else:
          return False
       return True
    else:
       self.IncrementCurrent(0,False, Channel)
       if Channel == "both":
          Duty = int(self.currentLeft/self.DutyGain)
          self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEft
          self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM right
       elif Channel == "left":
          Duty = int(self.currentLeft/self.DutyGain)
          self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM left
       else:
          Duty = int(self.currentRight/self.DutyGain)
          self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM right
       return False

  def SetCurrentPercent(self,CurrentPercent, Channel = "both"):
     # percent will need to be between 0 and 100 otherwise it will clamp and return false
     if CurrentPercent <= 100 and CurrentPercent >= 0:
        if Channel == "both":
           self.currentLeft = self.MaxCurrent*CurrentPercent/100
           self.currentRight = self.currentLeft 
           Duty = int(self.currentLeft/self.DutyGain)
           self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
           self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
        elif Channel == "left":
           self.currentLeft = self.MaxCurrent*CurrentPercent/100 
           Duty = int(self.currentLeft/self.DutyGain)
           self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
        elif Channel == "right":
           self.currentRight = self.MaxCurrent*CurrentPercent/100 
           Duty = int(self.currentRight/self.DutyGain)
           self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
        else:
           return False
        return True
     elif CurrentPercent > 100:
        if Channel == "both":
           self.currentLeft = self.MaxCurrent
           self.currentRight = self.currentRight
           Duty = int(self.currentLeft/self.DutyGain)
           self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
           self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
        elif Channel == "left":
           self.currentLeft = self.MaxCurrent
           Duty = int(self.currentLeft/self.DutyGain)
           self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
        elif Channel == "right":
           self.currentRight = self.MaxCurrent
           Duty = int(self.currentRight/self.DutyGain)
           self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
        else:
           return False
        return False
     else:
        if Channel == "both":
           self.currentLeft = 0
           self.currentRight = 0
           Duty = int(self.currentLeft/self.DutyGain)
           self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
           self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
        elif Channel == "left":
           self.currentLeft = 0
           Duty = int(self.currentLeft/self.DutyGain)
           self.pi.hardware_PWM(IO1, FREQ, Duty) # Setting the Hardware PWM LEFT
        elif Channel == "right":
           self.currentRight = 0
           Duty = int(self.currentRight/self.DutyGain)
           self.pi.hardware_PWM(IO2, FREQ, Duty) # Setting the Hardware PWM Right
        else:
           return False
        return False 

  def IncrementCurrent(self,percent,Loop = True, Channel = "both"):
    # increment the current based on max current.  percent can be both positive or negative
    # default to looping the current if it reaches zero or end
    IncCurrent = percent/100*self.MaxCurrent
    if Channel == "both":
       self.currentLeft = self.currentLeft + IncCurrent
       self.currentRight = self.currentRight + IncCurrent
       if Loop:
          if self.currentLeft > self.MaxCurrent:
             self.currentLeft = 0
          elif self.currentLeft < 0:
             self.currentLeft = self.MaxCurrent
          self.SetCurrent(self.currentLeft*1000, "left")
          if self.currentRight > self.MaxCurrent:
             self.currentRight = 0
          elif self.currentRight < 0:
             self.currentRight = self.MaxCurrent
          self.SetCurrent(self.currentRight*1000, "right")
       else:
          if self.currentLeft > self.MaxCurrent:
             self.currentLeft = self.MaxCurrent
          elif self.currentLeft < 0:
             self.currentLeft = 0
          self.SetCurrent(self.currentLeft*1000, "left") 
          if self.currentRight > self.MaxCurrent:
             self.currentRight = self.MaxCurrent
          elif self.currentRight < 0:
             self.currentRight = 0
          self.SetCurrent(self.currentRight*1000, "left")       
    elif Channel == "left":
       self.currentLeft = self.currentLeft + IncCurrent
       if Loop:
          if self.currentLeft > self.MaxCurrent:
             self.currentLeft = 0
          elif self.currentLeft < 0:
             self.currentLeft = self.MaxCurrent
          self.SetCurrent(self.currentLeft*1000, "left")
       else:
          if self.currentLeft > self.MaxCurrent:
             self.currentLeft = self.MaxCurrent
          elif self.currentLeft < 0:
             self.currentLeft = 0
          self.SetCurrent(self.currentLeft*1000, "left") 
    else:
       self.currentRight = self.currentRight + IncCurrent
       if Loop:
          if self.currentRight > self.MaxCurrent:
             self.currentRight = 0
          elif self.currentRight < 0:
             self.currentRight = self.MaxCurrent
          self.SetCurrent(self.currentRight*1000, "right")
       else:
          if self.currentRight > self.MaxCurrent:
             self.currentRight = self.MaxCurrent
          elif self.currentRight < 0:
             self.currentRight = 0
          self.SetCurrent(self.currentRight*1000, "left")       
       

  def SetDimmerDuty(self,DUTY2, Channel = "both"):
    # DUTY is given as percentage.  1M in Pi will be 100%
    if Channel == "both":
       self.DimmerDutyLeft = DUTY2
       self.DimmerDutyRight = DUTY2
       self.pi.set_PWM_dutycycle(IO4, int(self.DimmerDutyLeft/100.00*255)) # Left
       self.pi.set_PWM_dutycycle(IO5, int(self.DimmerDutyRight/100.00*255)) # Right
    elif Channel == "left":
       self.DimmerDutyLeft = DUTY2
       self.pi.set_PWM_dutycycle(IO4, int(self.DimmerDutyLeft/100.00*255)) # Left
    else:
       self.DimmerDutyRight = DUTY2
       self.pi.set_PWM_dutycycle(IO5, int(self.DimmerDutyRight/100.00*255)) # Right


  def BurnInOn(self, Channel = "both"):
    BurnInDuty = int(self.BurnInCurrent/self.DutyGain)
    if Channel == "both":
       self.pi.hardware_PWM(IO1,FREQ, BurnInDuty)
       self.pi.hardware_PWM(IO2,FREQ, BurnInDuty)
       self.pi.set_PWM_dutycycle(IO4, 255) # Left
       self.pi.set_PWM_dutycycle(IO5, 255) # Right
    elif Channel == "left":
       self.pi.hardware_PWM(IO1,FREQ, BurnInDuty)
       self.pi.set_PWM_dutycycle(IO4, 255) # Left
       
    else:
       self.pi.hardware_PWM(IO2,FREQ, BurnInDuty)
       self.pi.set_PWM_dutycycle(IO5, 255) # Right
    self.BurnIn = True

  def BurnInOff(self, Channel = "both"):
    #return currents and duty back to what they were before the burnin
    if Channel == "both":
       self.SetDimmerDuty(self.DimmerDutyLeft, Channel)
       Duty = int(self.currentLeft/self.DutyGain)  
       self.pi.hardware_PWM(IO1,FREQ, Duty)
       Duty = int(self.currentRight/self.DutyGain)    
       self.pi.hardware_PWM(IO2,FREQ, Duty)
    elif Channel == "left":
       self.SetDimmerDuty(self.DimmerDutyLeft, Channel)  
       Duty = int(self.currentLeft/self.DutyGain)  
       self.pi.hardware_PWM(IO1,FREQ, Duty)
    else:
       self.SetDimmerDuty(self.DimmerDutyRight, Channel)
       Duty = int(self.currentRight/self.DutyGain)    
       self.pi.hardware_PWM(IO2,FREQ, Duty)
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


   #print "hello world"

   if len(sys.argv) < 2:
      print("No Nixie Tube Defined.  It is either IN-9 or IN-13")
      print("for example: python Python-RpiIN9Nixie.py IN-13")
      exit()
   elif len(sys.argv) == 2:
      NixieType = sys.argv[1]
      if NixieType != "IN-9" and NixieType != "IN-13" :
         print("Incorrect Nixie Tube Defined.  It is either IN-9 or IN-13")
         exit()
   elif len(sys.argv) >= 3:
      print("There was an incorrect number of arguments for program:  two maximum")
      exit()
   # set the maximum currents:  13ma for IN-9 and 5ma for IN-13
   if NixieType == "IN-9":
      MaxCURRENT = 12
      BurnINCURRENT = 14
   else:
      MaxCURRENT = 4.6
      BurnINCURRENT = 5.2

   Channel = "both"
   EXITPROGRAM = False
   
   barnixie = RpiIN9Nixie( InitCurrent = 1, MaxCurrent = MaxCURRENT, BurnInCurrent = BurnINCURRENT)
   
   while EXITPROGRAM == False:
      while True:         
         if barnixie.IsBurnIn():
            print("The Nixie Current is Burning In at %smA which is %s%%" % (float(barnixie.BurnInCurrent*1000), float(barnixie.BurnInCurrent/barnixie.MaxCurrent*100)))
         else:
            print("The Left Nixie Current is %sma which is %s%%" % (float(barnixie.currentLeft*1000), float(barnixie.currentLeft/barnixie.MaxCurrent*100))) 
            print("The Right Nixie Current is %sma which is %s%%" % (float(barnixie.currentRight*1000), float(barnixie.currentRight/barnixie.MaxCurrent*100))) 
         print("The Left Dimmer Percentage is : %s" % float(barnixie.DimmerDutyLeft))
         print("The Right Dimmer Percentage is : %s" % float(barnixie.DimmerDutyRight))
         if barnixie.INDEXPOSITIVE:
            print("The index is set to POSITIVE")
         else:
            print("The index is set to NEGATIVE")   
         if barnixie.IsSupplyOn():
            print("The supply is ON")
         else:
            print("The supply if OFF")
         if Channel == "both":
            print("Commands will set Both Channels")
         elif Channel == "left":
            print("Commands will set LEFT Channel")
         else:
            print("Commands will set RIGHT Channel")
         print("Press: ")
         print("return: to increase duty +/- 1/2 percent")
         print("[t]: toggle the index polarity")
         print("[d]: Set the Dimmer")
         print("[c]: change the Channel either Both, Left, or Right")
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
               barnixie.IncrementCurrent(0.5, Channel)
            else:
               barnixie.IncrementCurrent(-0.5, Channel)
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
                     barnixie.SetDimmerDuty(raw_option2, Channel)
                     break
               else:
                     print("Please input a digit for Dimmer Percentage")  
            break
         elif raw_option == "c":
            while True:
               raw_option2 = raw_input("Which Channel (b=both, l=Left, r=right): ")
               if raw_option2== "b":
                  Channel = "both"
                  break
               elif raw_option2 == "l":
                  Channel = "left"
                  break
               elif raw_option2 == "r":
                  Channel = "right"
                  break
               else:
                  print("Please select either [b] for both, [l] for Left, [r] for right")  
         elif raw_option == "s":
            if barnixie.IsSupplyOn():
               barnixie.SupplyOff()
            else:
               barnixie.SupplyOn()
         elif raw_option == "b":
            if barnixie.IsBurnIn():
               barnixie.BurnInOff(Channel)
            else:
               barnixie.BurnInOn(Channel)  
         elif raw_option.isdigit():
            raw_option = int(raw_option)
            if (raw_option > 100) or (raw_option < 0):
               print("Please try again: need to input a number between 0-100")   
            else:
               barnixie.SetCurrentPercent(raw_option, Channel)
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
            barnixie.SetCurrentPercent(10, Channel)
            barnixie.SupplyOff()
            break
         else:
            print("Please input a digit for Current Percentage")
      
   exit()        
