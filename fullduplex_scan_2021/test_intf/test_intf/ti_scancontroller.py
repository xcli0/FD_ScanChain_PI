#!/usr/bin/python

import time
import os
import re
import logging
import test_intf.testScanModule as testScanModule
from test_intf.ti_device import Device

# Description:
# Scan controller class that takes a scanSequence and a scanSettings as input and develops
# a test interface for scan setup.

# Scan controller class
class ScanController(object):

    def __init__(self, device, scan_sequence_file="scanSequence.txt", 
                 scan_settings_file="scanSettings.txt"): 
        self.device = device
        self.scanDict = {}
        self.scanList = []
        self.scanDictKeysSorted = []
        self.outScanDict = {}

        # reading scanSequence.txt and scanSettings.txt
        testScanModule.readScanSequenceFile(self.scanList, self.scanDict, 
                                            self.scanDictKeysSorted, 
                                            scan_sequence_file)
        testScanModule.readScanSettingsFile(self.scanDict, scan_settings_file)
      
        # input and output vectors for scanning and comparison
        self.inScanVector = testScanModule.genTestScanVector(self.scanList, 
                                                             self.scanDict) 
        #Generate scanVector needed for scan in
        self.outScanVector = []
   
    def UpdateScanSettings(self, updateScanSettingsFile):
        testScanModule.ReadupdateScanSettings(self.scanDict,
                                              updateScanSettingsFile)
        self.inScanVector = testScanModule.genTestScanVector(self.scanList, 
                                                             self.scanDict)
   # Scan ins the data from the text file
   # Allow user to be able to pass in own bits to send file
    def scan_in(self):   

        print("[INFO] Scan in function launched!")
        # Scan data in
        for val in (self.inScanVector):
            self.device.scan_in.set(val);

            # Toggle Phi
            self.device.phi.on()
            self.device.phi.off()

            # Toggle Phi Bar
            self.device.phi_bar.on()
            self.device.phi_bar.off()

        # Toggle Update
        #time.sleep(1)
        #wait=1        
        #while wait > 0:
            #print(wait)
            #time.sleep(1)
            #wait = wait - 1
        self.device.update.on()
        #time.sleep(0.1)
        self.device.update.off()

    # Scans the data out 
    def scan_out(self):
        print("[INFO] Scan out function launched!")
        # Toggle Capture
        self.device.capture.on()

        # Toggle Phi Bar
        self.device.phi_bar.on()
        self.device.phi_bar.off()
        
        self.device.capture.off()

        for val in self.inScanVector:
            scan_out_data = self.device.scan_out.read()
            #print(scan_out_data)
            self.outScanVector.append(scan_out_data)
            # Toggle Phi
            self.device.phi.on()
            self.device.phi.off()

            # Toggle Phi Bar
            self.device.phi_bar.on()
            self.device.phi_bar.off()

        #generate new dictionary from output scan
        self.outScanDict = testScanModule.genOutputScanDict(self.scanList,
                                                            self.scanDict,
                                                            self.outScanVector)
    def scan_compare(self):
        #check what is going on
        testScanModule.scanCheck(self.scanDict, self.outScanDict,
                                 self.scanDictKeysSorted, "scanCompare.txt")

    def print_result(self):
        print("[INFO] Scan out Results:")
        for var_name, var_result in self.outScanDict.items():
            print(var_name, ":", var_result['value'])
