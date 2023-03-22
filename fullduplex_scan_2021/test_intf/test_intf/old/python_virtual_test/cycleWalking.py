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
parser.add_option("-t", "--cycleSleep", default=0.01, dest="cycleSleep", help="Duration of time that the routine sleeps between successive clock cycles [default: %default]")
parser.add_option("-r", "--rawFile", default="trng_raw.txt", dest="rawFileName", help="Filename where raw data: prng, trng and  trng_valid are provided [default: %default]")
parser.add_option("-o", "--trngFile", default="trng_out.txt", dest="trngFileName", help="Filename where only valid trng output bits are recorded [default: %default]")
# parser.add_option("-g", "--genScanStruct", dest="genScanStruct", action="store_true", default=False, help="Create a scanInterface module by appending it to the verilogFile and dumping out on verilogOut [default: %default]")
(options,args) = parser.parse_args()


#Walk the cycle using the dio.
#Generate as many prng/trng bit pairs as you want
#record and pring the 128 bit random key


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
############ Scan In configuration ##########################
#############################################################
#Scan your configuration, start-up clocks
module,scanList = scanModule.readScanFile("scan_scanConfig.txt")
scanVector=scanModule.genTestScanVector(scanList)
inputScanDict=trngTestModules.genScanDicts(scanList,scanVector)  #Generate a scanDict with scan inputs
trngTestModules.scanDataIn(daq,scanVector)
#############################################################
#############################################################

#Release reset to run experiment. 
#############################################################
############ Run for given number of cycles ####### #########
#############################################################
# For a user-determined number of cycles, run the clock. Slowly.
daq.writePortName("reset",0) #De-assert reset
prngBias, trngBias = trngTestModules.walkCycles(daq, readSignalList, options.iterations, options.cycleSleep,options.rawFileName, options.trngFileName)

# Experiment complete. Read data out
scanOutVector=trngTestModules.scanDataOut(daq,len(scanVector))
outputScanDict=trngTestModules.genScanDicts(scanList,scanOutVector)  #Generate a scanDict with scan inputs
trngTestModules.scanCheck(inputScanDict,outputScanDict,"scanCompare.txt")

