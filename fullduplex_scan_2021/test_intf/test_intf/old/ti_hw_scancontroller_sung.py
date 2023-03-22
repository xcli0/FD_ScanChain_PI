#!/usr/bin/python

import u3, time
# import os
#import digital_input_read
import sys
sys.path.append("..")
from test_intf.ti_abstract import TI_ABSTRACT_ScanController

# Scan controller class
class Scan_controller(TI_ABSTRACT_ScanController):

   def __init__(self, labjack, pin_rst, pin_phi, pin_phi_bar, pin_update, pin_capture, pin_scan_in, pin_scan_out, short_del=0.0001, long_del=0.0001, scan_bits_file="scan_bits.txt"): 
      # 2kHz digital stream out
      
      SCAN_BITS_FILE = scan_bits_file
      # Temporary bit stream file
      # BITS_TO_SEND_FILE = "bits_to_send.txt"

      # new impl
      # BITS_TO_SEND_FILE = self.convert_bits(SCAN_BITS_FILE)
      # self.stream = BITS_TO_SEND_FILE
      # self.total_stream = self.stream.read()
      # self.total_stream_list = map(int, list(self.total_stream))

      # old impl
      # scan_bits = self.convert_bits(SCAN_BITS_FILE)
      # self.stream = open(BITS_TO_SEND_FILE, 'r') #file should have same name in the same folder
      # self.total_stream = self.stream.read()
      # self.total_stream_list = map(int, list(self.total_stream))

      self.total_stream = self.convert_bits(SCAN_BITS_FILE)
      self.total_stream_list = list(map(int, list(self.total_stream)))


      self.lj = labjack
      self.lj.configIO()
      self.pin_rst = pin_rst
      self.pin_phi = pin_phi
      self.pin_phi_bar = pin_phi_bar
      self.pin_update = pin_update
      self.pin_capture = pin_capture
      self.pin_scan_in = pin_scan_in
      self.pin_scan_out = pin_scan_out
      self.short_del = short_del
      self.long_del = long_del
      
   def measure(self):
      try:
         self.lj.streamStart()
         for r in self.lj.streamData():
            if r is not None:
               if r['errors'] or r['numPackets'] != self.lj.packetsPerRequest or r['missed']:
                  print ("error")
               break
      finally: 
         self.lj.streamStop()
      return r

   # Return a stream of bits with an input of a scan bits file
   def convert_bits(self, scan_bits_file):
      BITS_TO_SEND_FILE = "bits_to_send.txt"
      f = open(BITS_TO_SEND_FILE, "w")

      scan_bits = []
      with open(scan_bits_file, "r") as sb:
        for line in sb:
           scan_bits.append(line.split()[1])
      scan_bits = ''.join(scan_bits)
      scan_bits = scan_bits[::-1]
      # f.write(scan_bits)
      return scan_bits

   # Scan ins the data from the text file
   # Allow user to be able to pass in own bits to send file
   def scan_in(self, scan_bits_file=None):
      if (scan_bits_file != None): 
         # old impl
         BITS_TO_SEND_FILE = "bits_to_send.txt"
         self.convert_bits(scan_bits_file)
         self.stream = open(BITS_TO_SEND_FILE, 'r') #file should have same name in the same folder
         self.total_stream = self.stream.read()
         self.total_stream_list = map(int, list(self.total_stream))
         os.remove(BITS_TO_SEND_FILE)
         
      # check if file != none
      # open file = scan bits
   
      # Assert Reset
      self.lj.setFIOState(self.pin_rst, state = 0)
      # Deassert Reset
      self.lj.setFIOState(self.pin_rst, state = 1)

      # Scan data in
      x = 0
      for val in (self.total_stream_list):
         # self.stream.seek(x)
         # i = self.stream.read(1) # returns the value at that location and goes to the next byte when called again
         # if(i == ''): # fixes issue with reading files
         #    break

         # val = int(str(i))
         # val = int(self.total_stream_list[x])
         self.lj.setFIOState(self.pin_scan_in, state = val)

         # Toggle Phi
         self.lj.setFIOState(self.pin_phi, state = 1)
         time.sleep(self.short_del)#speed determined from max frequency of changing from one period
         self.lj.setFIOState(self.pin_phi, state = 0)

         # Toggle Phi Bar
         self.lj.setFIOState(self.pin_phi_bar, state = 1)
         time.sleep(self.short_del)
         self.lj.setFIOState(self.pin_phi_bar, state = 0)

         x+=1

      # Toggle Update
      self.lj.setFIOState(self.pin_update, state = 1)
      time.sleep(self.short_del)#speed determined from max frequency of changing from one period
      self.lj.setFIOState(self.pin_update, state = 0)

      # Wait for update
      time.sleep(self.long_del)

   # Scans the data out 
   def scan_out(self): 
      # Toggle Capture
      self.lj.setFIOState(self.pin_capture, state = 1)

      # Toggle Phi Bar
      self.lj.setFIOState(self.pin_phi_bar, state = 1)
      time.sleep(self.short_del)
      self.lj.setFIOState(self.pin_phi_bar, state = 0)

      time.sleep(self.short_del)#speed determined from max frequency of changing from one period
      self.lj.setFIOState(self.pin_capture, state = 0)

      IO_value = self.pin_scan_out
      print ("IO_value " + str(IO_value))
      self.lj.configIO(FIOAnalog = 0)     # ask for digital inputs
      self.lj.setFIOState(IO_value, state = 0) #sets state low and sets as output (which is fixed by next function
      self.lj.getDIState(IO_value) #sets digital input

      self.lj.streamConfig( NumChannels = 1,
         PChannels = [193],
         NChannels = [31],
         Resolution = 3,
         SampleFrequency = 5000 )

      self.lj.packetsPerRequest = 1   # you can adjust this value to get more or less data

      scan_out = []

      # Scan data out
      x = 0
      # while(x < len(self.total_stream_list)):
      for val in self.total_stream_list:
         # self.stream.seek(x)
         # i = self.stream.read(1) # returns the value at that location and goes to the next byte when called again
         # if(i == ''): # fixes issue with reading files
         #      break

         # val = int(self.total_stream_list[x])
         self.lj.setFIOState(self.pin_scan_in, state = val)

         # Measure scan-out data
         scan_out_data = self.measure()
         if x == 2:
            print ("scan out data" + str(scan_out_data))
         scan_out.append(scan_out_data)


         # Toggle Phi
         self.lj.setFIOState(self.pin_phi, state = 1)
         time.sleep(self.short_del)#speed determined from max frequency of changing from one period
         self.lj.setFIOState(self.pin_phi, state = 0)

         # Toggle Phi Bar
         self.lj.setFIOState(self.pin_phi_bar, state = 1)
         time.sleep(self.short_del)
         self.lj.setFIOState(self.pin_phi_bar, state = 0)

         x+=1

      # print 'scan out' + str(scan_out)
      scan_out_results = []
      for i in range(0, len(scan_out)):
         port_num = 'AIN193'
         scan_out_results.append(scan_out[i][port_num][0][0])
      # print 'scan out ' + str(scan_out_results)

      scan_out_results_mod = []
      scan_out_mask = 0x1 << self.pin_scan_out
      print ('scan out pin ' + str(self.pin_scan_out))
      print (str(scan_out_mask))
      for element in scan_out_results:
         # print "element " + str(element)
         # print "element AND scan_out_mask " + str(element & scan_out_mask)
         if (element & scan_out_mask) > 0:
            scan_out_results_mod.append(1)
         elif (element & scan_out_mask) == 0:
            scan_out_results_mod.append(0)
         else:
            scan_out_results_mod.append('x')
      # Print the scan in and scan out streams
      print ('total stream list ' + str(list(self.total_stream_list)))
      print ('scan_out_results_mod ' + str(scan_out_results_mod))
      if self.total_stream_list == scan_out_results_mod:
         print ("Scan Successful")
      else:
         print ("Scan Failed...")

      # Assert Reset
      self.lj.setFIOState(self.pin_rst, state = 0)
      # Deassert Reset
      self.lj.setFIOState(self.pin_rst, state = 1)


