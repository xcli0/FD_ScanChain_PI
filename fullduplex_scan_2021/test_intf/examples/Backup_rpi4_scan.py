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
                              scan_settings_file="regular_scan_settings_test_1108.txt")   #The first line in scan_sequence is the last bit in scan chain on chip.

###################
# Parsign reg.txt #
###################

## Writing the bits as a single string, going from MSB to LSB
## (in this case, this is as easy as removing line breaks)
#dbe_reg_file = open("reg.txt", "r")
#dbe_reg_string = ""
#for line in dbe_reg_file:
#    stripped_line = line.rstrip()
#    dbe_reg_string += stripped_line
#dbe_reg_file.close()
#dbe_reg_int = int(dbe_reg_string, 2)

## Loading the new value for dbe_reg into the scan vector
##regular_scan.scanDict["symbol_CLK_oversampling_factor"]["value"] = "4'd3"
#regular_scan.scanDict["scan_dbe_reg"]["value"] = "2407'd" + str(dbe_reg_int)
##Update scanin.
#regular_scan.inScanVector = testScanModule.genTestScanVector(regular_scan.scanList, regular_scan.scanDict)

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

# Wait for the user to manually end execution of the program
pause()

