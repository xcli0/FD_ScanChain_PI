#!/usr/bin/env python3

##############################
# Importing needed libraries #
##############################

import time
import sys
from signal import pause

sys.path.append("..") # Adds higher directory to python modules path.
from test_intf.ti_device import Device
from test_intf.ti_device_ports import *
from test_intf.ti_scancontroller import ScanController
import test_intf.testScanModule as testScanModule

############################################
# Setting up the raspberry pi (ports, etc) #
############################################

device = RASPBERRY
regular_scan = ScanController(device, scan_sequence_file="regular_scan_sequence_test.txt",
                              scan_settings_file="regular_scan_settings_test.txt")   #The first line in scan_sequence is the last bit in scan chain on chip.

###################
# Parsign reg.txt #
###################

def reverseBits(num,bitSize): 
    
     # convert number into binary representation 
     # output will be like bin(10) = '0b10101' 
     binary = bin(num) 
    
     # skip first two characters of binary 
     # representation string and reverse 
     # remaining string and then append zeros 
     # after it. binary[-1:1:-1]  --> start 
     # from last character and reverse it until 
     # second last character from left 
     reverse = binary[-1:1:-1] 
     reverse = reverse + (bitSize - len(reverse))*'0'
    
     # converts reversed binary string into integer 
     return (int(reverse,2)) 

## Loading the new value into the scan vector
bitSize=8
step=2
for weight in range(0, 255, step):

    weight_bin=format(weight,"08b")
    weight_rev=reverseBits(weight,bitSize)
    weight_bin_rev=format(weight_rev,"08b")
    regular_scan.scanDict["STG12_Q_REV"]["value"] = "8'd" + str(weight_rev)

    #Update scanin.
    regular_scan.inScanVector = testScanModule.genTestScanVector(regular_scan.scanList, regular_scan.scanDict)

    ########################
    # Example test program #
    ########################

    # Get current time. This is useful to compute how long it takes to scan in new values
    start_time = time.perf_counter()

    # Scan in, and get current time, again
    regular_scan.scan_in()
    scan_in_time = time.perf_counter()

    # Scan out, and get current time
    regular_scan.outScanVector = []
    regular_scan.scan_out()
    scan_out_time = time.perf_counter()

    # Print the values we obtained from scanning out
    regular_scan.print_result()

    # Compare the values we scanned in to the values we scanned out
    regular_scan.scan_compare()

    # Print how long it takes to scan in and scan out values
    print("Scan in time", scan_in_time - start_time)
    print("Scan out time", scan_out_time - scan_in_time)

    print("test output",weight)
    print("test output_rev",weight_rev)
    # Wait for the user to manually end execution of the program
    #time.sleep(2)
    input()

