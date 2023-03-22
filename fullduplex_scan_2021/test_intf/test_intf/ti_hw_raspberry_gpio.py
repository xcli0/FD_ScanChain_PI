#!/usr/bin/env python3

import gpiozero as gpiopi
from test_intf.ti_abstract_port import Port

class RaspberryPi(Port):
    '''Class Definition for Raspberry Pi
        Hardware Abstraction Layer'''

    def __init__(self, port_number, port_type):
        '''Class Constructor'''
        self.port_number = port_number
        self.port_type = port_type
        if self.port_type.lower() == "o":
            self.port = gpiopi.OutputDevice(port_number, active_high=True,
                                            initial_value=None)
        elif self.port_type.lower() == "i":
            self.port = gpiopi.DigitalInputDevice(port_number, pull_up=None,
                                                  active_state=True)
        else:
            raise ValueError('Bad port type definition')
    def on(self):
        '''Set HIGH value in port '''
        if self.port_type.lower() == "o":
            self.port.on()
        else:
            print("WARNING:Port defined as input")
    def off(self):
        '''Set LOW value in port '''
        if self.port_type.lower() == "o":
            self.port.off()
        else:
            print("WARNING:Port defined as input")
    def toggle(self):
        '''Toggle value in port '''
        if self.port_type.lower() == "o":
            self.port.toggle()
        else:
            print("WARNING:Port defined as input")
    def set(self, value):
        '''Set value in port HIGH/LOW'''
        if self.port_type.lower() == "o":
            if value == 1:
                self.port.on()
            else:
                self.port.off()
        else:
            print("WARNING:Port defined as input")
    def read(self):
        '''Read current port value'''
        return self.port.value
