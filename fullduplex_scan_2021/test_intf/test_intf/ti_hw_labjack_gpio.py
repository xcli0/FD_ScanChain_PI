#!/usr/bin/env python

from ti_abstract import TI_ABSTRACT_GPIO
import u3

# GPIO class to control digital I/O on the labjack

# IO Number: 0-7=FIO, 8-15=EIO, or 16-19=CIO.
# Direction: 1=Output, 0=Input.
class Labjack_gpio(TI_ABSTRACT_GPIO):

    def __init__(self, labjack): 
    	self.lj = labjack
        self.num_dio = 8

    #Get the number of digital I/O
    def get_total_dio(self): 
    	return self.num_dio

    #Set the state of a digital I/O
    def set_dio(self, dio_n, state): 
        DIR = 1
    	self.lj.getFeedback(u3.BitDirWrite(dio_n, DIR)) 
    	self.lj.getFeedback(u3.BitStateWrite(dio_n, state))    	

    #Get the state of a digital I/O
    def get_dio(self, dio_n): 
    	return self.lj.getFeedback(u3.BitStateRead(dio_n))
