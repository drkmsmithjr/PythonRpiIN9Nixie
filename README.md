# Python Raspberry Pi IN-9 and IN-13 Linear Nixie Tube Hat Library

This Python Library is used to control the IN-9 and IN-13 Linear Nixie Tube HAT for the Raspberry Pi.

See [www.surfncircuits.com](https://wp.me/p85ddV-HQ) for more information.  This github repository contains the python Library for a PCB Hat that works with the Rasperry Pi Zero, and B+ along with the [Nixie Tube Power Supply](https://wp.me/p85ddV-Ck) designed in a previous [www.surfncircuits.com](https://wp.me/p85ddV-HQ) blog. 

This library can be installed on the raspberry pi by the usual git clone technique.      

The complete HAT hardware and software design can also be downloaded at the [RpiNixieBarGraphHat](https://github.com/drkmsmithjr/RpiNixieBarGraphHat) repository.   This repository is a sub-module to the [RpiNixieBarGraphHat](https://github.com/drkmsmithjr/RpiNixieBarGraphHat) repository.      

This Library uses the [pigrio](http://abyz.me.uk/rpi/pigpio/) library because of its ability to control the harware PWM outputs of the raspbarry pi zero.

* To install this [pigrio](http://abyz.me.uk/rpi/pigpio/) library perform the following 

* sudo apt-get update

* sudo apt-get install pigpio python-pigpio



