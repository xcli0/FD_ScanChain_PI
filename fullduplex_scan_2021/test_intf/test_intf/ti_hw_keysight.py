#!/usr/bin/env python
# -*- coding: utf-8 -*-

import usbtmc
import time

from ti_abstract import TI_ABSTRACT_VoltageRegulator

# Keysight power supply class
class Keysight_psu(TI_ABSTRACT_VoltageRegulator):
   resource_id = "USB::0x2A8D::0x0602::INSTR"

   def __init__(self):
      self.volt = 0
      self.curr = 0
      self.output_en = 0
      self.max_volt = None
      self.max_curr = None
      self.instr = self._init_instr(Keysight_psu.resource_id)

   # Set the voltage on the power supply
   def set_voltage(self, v):
      self.volt = v
      self._send_cmd("VOLTAGE {}".format(v))

   # Get the voltage on the power supply
   def get_voltage(self):
      return float(self.instr.ask("MEASURE:VOLTAGE:DC?"))
      
   # Get the current on the power supply
   def get_current(self): 
      return float(self.instr.ask("MEASURE:CURRENT:DC?"))   

   # Set the current on the power supply
   def set_current(self, c):
      self.curr = c
      self._send_cmd("CURRENT {}".format(c))

   # Set the output enable on the power supply
   def set_output_en(self, en=True):
      self.output_en = en
      if en:
        self._send_cmd("OUTPUT 1")
      else:
        self._send_cmd("OUTPUT 0")

   # Send the command to the power supply
   def _send_cmd(self, cmd):
      self.instr.write(cmd) # for some reason have to send twice
      self.instr.write(cmd)

   def _init_instr(self, rid):
      return usbtmc.Instrument(rid)

