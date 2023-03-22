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
parser.add_option("-i", "--iterations", default=10000, dest="iterations", help="Number of INITIAL cycle iterations for the test [default: %default]")
parser.add_option("-o", "--outFile", default=prngCalibReport.txt, dest="outFile", help="Filename where the moves and results are measured [default: %default]")
parser.add_option("-t", "--biasThreshold", default=0.02, dest="biasThreshold", help="Target bias. Calibration ends once this bias is detected [default: %default]")
# parser.add_option("-g", "--genScanStruct", dest="genScanStruct", action="store_true", default=False, help="Create a scanInterface module by appending it to the verilogFile and dumping out on verilogOut [default: %default]")
(options,args) = parser.parse_args()


#Load dac code with 0 offset into the prng
#cycle walk as many signals as you want
#record bias and update
#Make the signals collected longer as you zoom in.

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
wfh=open(options.outFile,'w')
#Initialize experiment by defining daq, scope, clock source(?) and power supplies
#Provide supply voltage definition. This code is set up for 
#gpib interface so you need port, channel and voltageValue.
#Return value is a dictionary mapping from name to supply object
daq=trngTestModules.initializeDaq("trng_daq_port.map")
supplyDict=trngTestModules.definePowerSupplies(supplyVoltageDict)
#############################################################
#############################################################


#Release reset to run experiment. 
#############################################################
############ Run multiple iterations till you meet bias #####
#############################################################
# For a user-determined number of cycles, run the clock. Slowly.
#Using all signals on the fall signal list simply because I'll be running slowly enough for this 
module,scanList = scanModule.readScanFile(daq,"prng_0_manual_scanConfig.txt")
bias = options.bias
fallSignalList = ["prng_bit", "trng_out", "trng_out_valid"] #capture on falling edge of strobe
riseSignalList = [] #capture on rising edge of strobe
dacSign=0
dacMag=0
wfh.write("{0:<5} {0:<13} {1:<10}\n".format("dacSign", "dacMagnitude", "bias"))
while abs(bias)>options.biasThreshold :
    daq.writePortName("ro_clk_en",0) #Disable RO clock
    dacCode = dacSign*512 + dacMag
    trngTestModules.modifyScanList("dac_code_external",scanList,dacCode) #You have the code. Modify the scan list now
    scanVector=scanModule.genTestScanVector(daq,scanList) #Generate scanVector needed for scan in
    inputScanDict=trngTestModules.genScanDicts(scanList,scanVector)  #Generate a scanDict with this test
    trngTestModules.scanDataIn(scanVector)
    daq.writePortName("ro_clk_en",1) #Enable RO clock
    daq.writePortName("reset",0) #De-assert reset, running the experiment.
    prngBias,trngBias=trngTestModules.readPrngTrng(daq, "ro_clk" , fallSignalList, riseSignalList, options.iterations, "temp.txt" , trngFileName)
    wfh.write("{0:<5} {0:<13} {1:<10}\n".format(dacSign, dacMag, prngBias))
    #Decision loop for dac update
    if prngBias>0:
        if dacSign==1:
            if dacMag!=0:
                dacMag-=1
            else:
                dacMag=1
                dacSign=0
        else:
            dacMag+=1
    else:
        if dacSign==0:
            if dacMag!=0:
                dacMag-=1
            else:
                dacMag=1
                dacSign=1
        else:
            dacMag+=1
    #####
    scanOutVector=trngTestModules.scanDataOut(daq)
    outputScanDict=trngTestModules.genScanDicts(scanList,scanOutVector)
    trngTestModules.scanCheck(inputScanDict,outputScanDict,"scanCompare.txt")
            #TODO. Need to add a scan check here...

wfh.write("Final dac code is {0} resulting in a bias of {1}\n".format(dacCode,prngBias))
print "Final dac code is {0} resulting in a bias of {1}\n".format(dacCode,prngBias)
wfh.close()

# walkCycles(daq, readSignalList, iterations, cycleSleep,rawFileName, trngFileName):




