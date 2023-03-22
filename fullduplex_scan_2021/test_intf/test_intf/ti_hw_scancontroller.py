#!/usr/bin/python

import u3, time
import os
import re
import logging
#import digital_input_read
import sys
sys.path.append("..")
from test_intf.ti_abstract import TI_ABSTRACT_ScanController
import test_intf.testScanModule as testScanModule

# Description:
# Scan controller class that takes a scanSequence and a scanSettings as input and develops
# a test interface for scan setup. (last edited by visiting student Akash Pattnaik, 6/29/2018)

# Scan controller class
class Scan_controller(TI_ABSTRACT_ScanController):

    def __init__(self, labjack, pin_rst, pin_phi, pin_phi_bar, pin_update, pin_capture, pin_scan_in, 
            pin_scan_out, short_del=0.0001, long_del=0.0001, 
            scan_sequence_file="scanSequence.txt", scan_settings_file="scanSettings.txt"): 
        # 2kHz digital stream out
        # labjack configuration and necessary pins      
        self.lj = labjack
        self.lj.configIO(FIOAnalog = 0)
        self.pin_rst = pin_rst
        self.pin_phi = pin_phi
        self.pin_phi_bar = pin_phi_bar
        self.pin_update = pin_update
        self.pin_capture = pin_capture
        self.pin_scan_in = pin_scan_in
        self.pin_scan_out = pin_scan_out
        # short and long delays for phi and phi bar
        self.short_del = short_del
        self.long_del = long_del
        self.scanDict = {}
        self.scanList = []
        self.scanDictKeysSorted = []
        self.outScanDict = {}

        # reading scanSequence.txt and scanSettings.txt
        testScanModule.readScanSequenceFile(self.scanList, self.scanDict, self.scanDictKeysSorted, scan_sequence_file)
        testScanModule.readScanSettingsFile(self.scanDict, scan_settings_file)
      
        # input and output vectors for scanning and comparison
        self.inScanVector = testScanModule.genTestScanVector(self.scanList, self.scanDict) #Generate scanVector needed for scan in
        self.outScanVector = []

    # measures data from labjack stream
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

    def UpdateScanSettings(self, updateScanSettingsFile):
        testScanModule.ReadupdateScanSettings(self.scanDict, updateScanSettingsFile)
        self.inScanVector = testScanModule.genTestScanVector(self.scanList, self.scanDict)
   # Scan ins the data from the text file
   # Allow user to be able to pass in own bits to send file
    def scan_in(self):   
        # Assert Reset
        #self.lj.setFIOState(self.pin_rst, state = 0)
        # Deassert Reset
        #self.lj.setFIOState(self.pin_rst, state = 1)

        # Scan data in
        for val in (self.inScanVector):
            self.lj.setFIOState(self.pin_scan_in, state = val)

            # Toggle Phi
            self.lj.setFIOState(self.pin_phi, state = 1)
            time.sleep(self.short_del) # speed determined from max frequency of changing from one period
            self.lj.setFIOState(self.pin_phi, state = 0)

            # Toggle Phi Bar
            self.lj.setFIOState(self.pin_phi_bar, state = 1)
            time.sleep(self.short_del)
            self.lj.setFIOState(self.pin_phi_bar, state = 0)


        # Toggle Update
        self.lj.setFIOState(self.pin_update, state = 1)
        time.sleep(self.short_del) # speed determined from max frequency of changing from one period
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

        # speed determined from max frequency of changing from one period
        time.sleep(self.short_del)
        self.lj.setFIOState(self.pin_capture, state = 0)

        IO_value = self.pin_scan_out
        # ask for digital I/O
        self.lj.configIO(FIOAnalog = 0)
        # sets state low and sets as output (which is fixed by next function
        self.lj.setFIOState(IO_value, state = 0)
        # sets digital I/O direction to input and it also reads the state
        self.lj.getDIState(IO_value)

        self.lj.streamConfig( NumChannels = 1,
            PChannels = [193],
            NChannels = [31],
            Resolution = 3,
            SampleFrequency = 5000 )

        self.lj.packetsPerRequest = 1   # you can adjust this value to get more or less data

        scan_out = []

        # Scan data out
        for val in self.inScanVector:
            # Driving input values FOR TESTING ONLY
            self.lj.setFIOState(self.pin_scan_in, state = val)

            # Measure scan-out data
            scan_out_data = self.measure()
            scan_out.append(scan_out_data)

            # Toggle Phi
            self.lj.setFIOState(self.pin_phi, state = 1)
            # speed determined from max frequency of changing from one period
            time.sleep(self.short_del)
            self.lj.setFIOState(self.pin_phi, state = 0)

            # Toggle Phi Bar
            self.lj.setFIOState(self.pin_phi_bar, state = 1)
            time.sleep(self.short_del)
            self.lj.setFIOState(self.pin_phi_bar, state = 0)

        self.scan_out_results = []
        for i in range(0, len(scan_out)):
            port_num = 'AIN193'
            self.scan_out_results.append(scan_out[i][port_num][0][0])

        scan_out_mask = 0x1 << self.pin_scan_out
        for element in self.scan_out_results:
            if (element & scan_out_mask) > 0:
                self.outScanVector.append(1)
            elif (element & scan_out_mask) == 0:
                self.outScanVector.append(0)
            else:
                self.outScanVector.append('x')
    
    def scan_out_xun(self):
        # Toggle Capture
        self.lj.setFIOState(self.pin_capture, state = 1)

        # Toggle Phi Bar
        self.lj.setFIOState(self.pin_phi_bar, state = 1)
        time.sleep(self.short_del)
        self.lj.setFIOState(self.pin_phi_bar, state = 0)
        # speed determined from max frequency of changing from one period
        time.sleep(self.short_del)
        self.lj.setFIOState(self.pin_capture, state = 0)

        self.scan_out = []

        for val in self.inScanVector:
            scan_out_data = self.lj.getFIOState(self.pin_scan_out)
            self.scan_out.append(scan_out_data)
            # Toggle Phi
            self.lj.setFIOState(self.pin_phi, state = 1)
            # speed determined from max frequency of changing from one period
            time.sleep(self.short_del)
            self.lj.setFIOState(self.pin_phi, state = 0)

            # Toggle Phi Bar
            self.lj.setFIOState(self.pin_phi_bar, state = 1)
            time.sleep(self.short_del)
            self.lj.setFIOState(self.pin_phi_bar, state = 0)

        self.outScanVector = self.scan_out


    def scan_compare(self):
        #generate new dictionary from output scan
        self.outScanDict = testScanModule.genOutputScanDict(self.scanList, self.scanDict, self.outScanVector)

        #check what is going on
        testScanModule.scanCheck(self.scanDict, self.outScanDict, self.scanDictKeysSorted, "scanCompare.txt")

        # Assert Reset
        #self.lj.setFIOState(self.pin_rst, state = 0)
        # Deassert Reset
        #self.lj.setFIOState(self.pin_rst, state = 1)

