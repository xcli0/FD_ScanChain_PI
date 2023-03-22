#!/usr/bin/python
import re
import os
import sys
import warnings
import testChipEquipmentModules
import scanModule
import trngTestModules
from time import sleep
import pdb


# Routines to be written
# def roCalibration()
# def sweepF()


#DAQ port map to be found in trng_daq_port.map

#Name : port,channel,vmin,vmax,vnom
supplyVoltageDict={
    "vdd_ro":(0,0,0, 1.2, 1.0),
    "vdd_prng":(0,1,0, 1.2, 1.0),
    "vdd_trng_dig":(1,0,0, 1.2, 1.0),
    "vdd_test":(1,1,0, 1.2, 1.0),
    "vdd_tacvdd":(2,0,0, 1.2, 1.0),
    "dvdd":(2,1,0, 3.0, 2.5),
}

#Initialize experiment by defining daq, scope, clock source(?) and power supplies
#Provide supply voltage definition. This code is set up for
#gpib interface so you need port, channel and voltageValue.
#Return value is a dictionary mapping from name to supply object
daq=trngTestModules.initializeDaq("trng_daq_port.map")
supplyDict=trngTestModules.defineVoltageSupplies(supplyVoltageDict)

#Scan your configuration, start-up clocks
module,scanList = scanModule.readScanFile("prng_0_manual_scanConfig.txt")
scanVector=scanModule.genTestScanVector(scanList)
inputScanDict=trngTestModules.genScanDicts(scanList,scanVector)  #Generate a scanDict with scan inputs
trngTestModules.scanDataIn(daq,scanVector)
daq.writePortName("ro_clk_en",1) #Enable RO clock


#Release reset to run experiment. Wait 10ms to run
daq.writePortName("reset",0) #De-assert reset
sleep(0.01) #Sleep for 10ms

###################################################
############## Test code goes here ################
###################################################




scanOutVector=trngTestModules.scanDataOut(daq,len(scanVector))
outputScanDict=trngTestModules.genScanDicts(scanList,scanOutVector)  #Generate a scanDict with scan inputs
trngTestModules.scanCheck(inputScanDict,outputScanDict,"scanCompare.txt")




print scanVector
