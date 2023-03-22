#!/usr/bin/python
import re
import os
import sys
import warnings
import testChipEquipmentModules
import scanModule
import trngTestModules
from time import sleep
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--iterations", default=10000, dest="iterations", help="Number of cycle iterations for the test [default: %default]")
parser.add_option("-b", "--begin", default=1.2, dest="vstart", help="Starting voltage in scaling sweep [default: %default]")
parser.add_option("-e", "--end", default=0.4, dest="vstop", help="Final voltage in scaling sweep [default: %default]")
parser.add_option("-s", "--step", default=-0.1, dest="vstep", help="step size of voltage scaling [default: %default]")
# parser.add_option("-g", "--genScanStruct", dest="genScanStruct", action="store_true", default=False, help="Create a scanInterface module by appending it to the verilogFile and dumping out on verilogOut [default: %default]")
(options,args) = parser.parse_args()

#Keep trng_dig at max voltage (1.2). Keep frequency liberally low through cycle walking
#Sweep Prng vdd and capture information on bias.

#############################################################
################   Array and Dict definitions ###############
#############################################################
#DAQ port map to be found in trng_daq_port.map
#GPIB interface setting for supply: port, channel, vddmin, vaddmax, vset 
supplyVoltageDict={
    "vdd_ro":(0,0,0, 1.2, 1.0), 
    "vdd_prng":(0,1,0, 1.2, 1.0),
    "vdd_trng_dig":(1,0,0, 1.2, 1.0),
    "vdd_test":(1,1,0, 1.2, 1.0),
    "vdd_tacvdd":(2,0,0, 1.2, 1.0),
    "dvdd":(2,1,0, 3.0, 2.5),
}
readSignalList = ["prng_bit", "trng_out", "trng_out_valid"]

#Initialize experiment by defining daq, scope, clock source(?) and power supplies
#Provide supply voltage definition. This code is set up for 
#gpib interface so you need port, channel and voltageValue.
#Return value is a dictionary mapping from name to supply object
daq=trngTestModules.initializeDaq("trng_daq_port.map")
supplyDict=trngTestModules.defineVoltageSupplies(supplyVoltageDict)
#############################################################
#############################################################



#############################################################
############ Scan In configuration, release reset ###########
#############################################################
#Scan your configuration, start-up clocks
module,scanList = scanModule.readScanFile("scan_scanConfig.txt")
scanVector=scanModule.genTestScanVector(scanList)
trngTestModules.scanDataIn(daq,scanVector)

stepCount=int((float(options.vstop)-float(options.vstart))/float(options.vstep))
for i in range(stepCount):
    vdd=vstart + i*vstep
    inputScanDict=trngTestModules.genScanDicts(scanList,scanVector)  #Generate a scanDict with scan inputs
    scanDataIn(scanVector)
    daq.writePortName("ro_clk_en",1) #Enable RO clock
    daq.writePortName("reset",0) #De-assert reset
    rawFileName="prng_trng_raw" + "{0:.2f}".format(vdd) + ".txt" 
    trngFileName="trng_" + "{0:.2f}".format(vdd) + ".txt" 
    walkCycles(daq, readSignalList, options.iterations, options.cycleSleep, rawFileName, trngFileName):
    scanOutVector=trngTestModules.scanDataOut(daq,len(scanVector))
    outputScanDict=trngTestModules.genScanDicts(scanList,scanOutVector)  #Generate a scanDict with scan outputs
    #Run scan check

