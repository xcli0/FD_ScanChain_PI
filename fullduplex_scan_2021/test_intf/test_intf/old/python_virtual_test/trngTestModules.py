#!/usr/bin/python


import re
import os
import sys
import warnings
import logging
import testChipEquipmentModules
import scanModule
from time import sleep
import pdb

logging.basicConfig(filename="test.log",level=logging.DEBUG)
#This module is for common TRNG test chip tasks

#Define and initialize supply voltages
def defineVoltageSupplies(supplyConfigDict):
    supplyDict={}
    for name, config in supplyConfigDict.iteritems():
        port,channel,vmin,vmax,vnom = config
        # pdb.set_trace()
        supply=testChipEquipmentModules.gpib_power_supply(port, channel, name, vmin, vmax, vnom)
        supplyDict[name]=supply
    return supplyDict

#Define and initialize scope connections. Each port,channel is a virtual scope connection
def defineOscilloscopeConnections(scopeConfigDict):
    scopeDict={}
    for name, config in scopeConfigDict.iteritems():
        port,channel = config
        scope=testChipEquipmentModules.oscilloscope(name, port, channel)
        # TODO: If there is a function to estabilish that contact to the channel has been made put it here
        scopeDict[name]=scope
    return scopeDict

#Define the daq based on the configuration file and initialize all ports
def initializeDaq(portMapFile):
    daq=testChipEquipmentModules.daq_usb_6501(portMapFile)
    daq.writePortName("pad_clk",0)
    daq.writePortName("reset",1)
    daq.writePortName("update",0)
    daq.writePortName("capture",0)
    daq.writePortName("phi",0)
    daq.writePortName("phi_bar",0)
    daq.writePortName("scan_in",0)
    daq.writePortName("ro_clk_en",0)
    return daq

#Scan a single bit in only
#Signals phi, phi_bar, update, capture, scan_in and scan_out are assumed. 
def writeScanBit(daq,bit):
    daq.writePortName("scan_in",bit)
    
    daq.writePortName("phi",0) #If it was not zero, it is now...
    daq.writePortName("phi",1) #Pulse this once
    daq.writePortName("phi",0)
        
    daq.writePortName("phi_bar",0) #If it was not zero, it is now...
    daq.writePortName("phi_bar",1) #Pulse this once
    daq.writePortName("phi_bar",0)

#Read scan bits by flushing the scan chain with 0s
#Signals phi, phi_bar, update, capture, scan_in and scan_out are assumed. 
def readScanBit(daq):
    daq.writePortName("scan_in",0)
    
    daq.writePortName("phi",0) #If it was not zero, it is now...
    daq.writePortName("phi",1) #Pulse this once
    daq.writePortName("phi",0)
    
    daq.writePortName("phi_bar",0) #If it was not zero, it is now...
    daq.writePortName("phi_bar",1) #Pulse this once
    daq.writePortName("phi_bar",0)

    scanBit = daq.readPortName("scan_out") #Read the scan out signal at the end of this
    return scanBit

#Given a vector and the assumption of an lssd scan, scan the data in.
#Lmiitation: 1 daq has only one scan chain
def scanDataIn(daq,vector):
    #Ensure update and capture are 0
    daq.writePortName("update",0)
    daq.writePortName("capture",0)    
    for bit in vector:
        writeScanBit(daq,bit)
    #Bits in place. Fire the update
    daq.writePortName("update",1)
    daq.writePortName("update",0)

#After scan-in, run the test, and when done, run scan out as needed.
def scanDataOut(daq,scanLength):
    scanOutVector=[]
    daq.writePortName("capture",1)    
    daq.writePortName("phi_bar",1)    
    daq.writePortName("phi_bar",0)    
    daq.writePortName("capture",0)    
    scanOutBit = daq.readPortName("scan_out")
    scanOutVector.append(scanOutBit)
    #The first bit has been read already..you need one less iteration...
    for bit in range(scanLength-1):
        scanOutBit = readScanBit(daq)
        scanOutVector.append(scanOutBit)
    return scanOutVector
#Read signals in signalList based on edge of strobe signal. Choose rising or falling strobe by 
#putting the signal in the correct list. Count to iterations. 
#Note that both prng trng_valid and trng  are expected to be latched at the falling edge.

#Strobe is expected to be the raw ro clock (slow), prng_bit, trng_out and trng_out_valid are expected signals
def readPrngTrng(daq, strobe, fallSignalList, riseSignalList, iterations, rawFileName, trngFileName):
    count=0
    trigger=0 #trigger=1 asks for data from trigedge to be read once.
    strobeState=daq.readPortName(strobe)
    prevStrobeState=strobeState
    rfh=open(rawFileName, 'w')
    tfh=open(trngFileName,'w')
    fallDone=0 #Force the rising strobe to come after the fall strobe.
    prngOnes=0
    trngOnes=0
    writeTrng=0
    for signal in fallSignalList:
        rfh.write("{0:<{1}} ".format(signal,len(signal)))
    rfh.write("\n")
    for signal in riseSignalList:
        rfh.write("{0:<{1}} ".format(signal,len(signal)))
    rfh.write("\n")
    if(fallSignalList.index("trng_out") or riseSignalList.index("trng_out")):
        writeTrng=1
        tfh.write("trng_out\n")
        rfh.write("\n")

    while count<=int(iterations):
        stateDict={}
        strobeState=daq.readPortName(strobe)
        if(strobeState==1 and prevStrobeState==0 and fallDone==1): 
            for signal in riseSignalList:
                state=daq.readPortName(signal)
                fallDone=0
                stateDict[signal]=state
                count+=1
                trigger=1
        elif(strobeState==0 and prevStrobeState==1): 
            for signal in fallSignalList:
                state=daq.readPortName(signal)
                fallDone=1
                stateDict[signal]=state
        else:
            trigger=0
        prevStrobeState=strobeState
        if trigger==1: #Cycle complete, Write signal
            #prngOnes counts the number of ones in the prng ...easy check for fairness. Same for trngOnes
            prngOnes=prngOnes+1 if stateDict["prng_bit"]==1 else prngOnes
            for signal in fallSignalList+riseSignalList:
                rfh.write("{0:<{1}} ".format(stateDict[signal], len(signal)))
            rfh.write("\n")
            if(stateDict["trng_out_valid"]==1 and writeTrng==1):
                tfh.write("{}\n".format(stateDict["trng_out"]))
                trngOnes=trngOnes+1 if stateDict["trng_out"]==1 else trngOnes
            tfh.write("\n")
    
    rfh.close()
    tfh.close()
    prngBias=prngOnes*1.0/iterations -0.5
    trngBias=trngOnes*1.0/iterations -0.5
    return prngBias,trngBias


def walkCycles(daq,signalList,iterations,cycleSleep,rawFileName,trngFileName):
#Toggle clock manually through a port and read the prng and trng signals bit by bit. 
#This is slow so read just before rising edge.
    count=0
    rfh=open(rawFileName, 'w')
    tfh=open(trngFileName,'w')
    prngOnes=0
    trngOnes=0
    writeTrng=0
    iterations=int(iterations)
    for signal in signalList:
        rfh.write("{0:<{1}} ".format(signal,len(signal)))
    if(signalList.index("trng_out")):
        writeTrng=1
        tfh.write("trng_out\n")
    
    while count<iterations: #First read signals. then pulse clock
        # pdb.set_trace()
        stateDict={}
        count+=1
        for signal in signalList:
            state=daq.readPortName(signal)
#            print signal, state
            stateDict[signal]=state
        prngOnes=prngOnes+1 if stateDict["prng_bit"]==1 else prngOnes
        for signal in signalList:
            rfh.write("{0:<{1}} ".format(stateDict[signal], len(signal)))
        rfh.write("\n")
        if(stateDict["trng_out_valid"]==1):
            tfh.write("{}\n".format(stateDict["trng_out"]))
            trngOnes=trngOnes+1 if stateDict["trng_out"]==1 else trngOnes
        tfh.write("\n")
        daq.writePortName("pad_clk",0) 
        daq.writePortName("pad_clk",1)
        daq.writePortName("pad_clk",0)
        sleep(cycleSleep)
    rfh.close()
    tfh.close()
    prngBias=prngOnes*1.0/iterations -0.5
    trngBias=trngOnes*1.0/iterations -0.5
    return prngBias,trngBias

#From the data that has been obtained from the scan
#Leverage the "legacy scanlist" to enable easier access.
#Generate a dict of dict given scanList and a scanvector (input or output) 
#First index is signal name. Others are numBits, dirn, value and index
def genScanDicts(scanList,scanVector):
    rangeMin,rangeMax=-1,-1
    scanDict={}
    for i in range(len(scanList)):
        (signal,numBits,dirn,value)=scanList[i]
        print scanList[i]
        #Revert the direction once again to be dut centric and not scan centric
        dirn="output" if dirn=="input" else "input"
#Pick out the right output print format.
        if(re.match(r'.*[hbd]',value)):
            match=re.match(r'.*(?P<format>[hbd])(?P<val>\d+)',value)
            mFormat=match.group('format')
        elif(re.match(r'x',value)): 
            mFormat='d'
        else:
            match=re.match(r'(?P<val>\d+)',value)
            mFormat='d'
        rangeMin=int(rangeMax)+1
        rangeMax=int(rangeMax)+ int(numBits) 
        # pdb.set_trace()
        if(rangeMin==rangeMax):
           outputValue = str(scanVector[rangeMin])
        else:
            # outputValue = str(numBits) + "'" + mFormat + str("".join([str(x) for x in scanVector[rangeMin-1:rangeMax]]))
            outputValue = str("".join([str(x) for x in scanVector[rangeMin:rangeMax+1]]))
            outputValue=outputValue[::-1]
        if(mFormat=='d'):
            outputValue = int(outputValue, 2)
        elif(mFormat=='h'):
            outputValue = hex(int(outputValue, 2))[2:]
        elif(mFormat=='b'):
            outputValue = bin(int(outputValue, 2))[2:]
        
        outputValue = str(numBits) + "'" + mFormat + str(outputValue)
        scanDict[signal]={"numBits":numBits,"dirn":dirn,"value":outputValue,"index":rangeMin}
    return scanDict

#Check scan in and out signals and compare
def scanCheck(inputScanDict,outputScanDict,scanCompareFile):
    wfh=open(scanCompareFile,'w')
    wfh.write("{0:<20} {1:<20} {2:<20}\n".format("Signal", "Scan-in Value", "Scan-out Value"))
    for key in inputScanDict.keys():
        wfh.write("{0:<20} {1:<20} {2:<20}\n".format(key, inputScanDict[key]["value"], outputScanDict[key]["value"]))
        if(inputScanDict[key]!=outputScanDict[key] and inputScanDict[key]['dirn'] == 'input'):
            print "Scan failed on signal ", key
            logging.warning("Warning! Signal {0} scanned in as {1} but scanned out as {2}\n".format(key, inputScanDict[key]["value"], outputScanDict[key]["value"]))

 
#Enable swapping out of a scan_chain signal from its scanConfig.txt file with a runtime changable value
#Handy for sweeping scan related signals
def modifyScanList(entry,scanList,value):
    for i in range(len(scanList)):
        (signal,numBits,dirn,value)=scanList[i]
        if signal != entry: 
            next
        else:
            scanList[i] = (signal,numBits,dirn,value) 
            #Decimal assumed in this context since calling function deals with int dacCode
            exit


def recallFrequency(frequency,fTableFile):
    fDict={}
    with open(fTableFile,'r') as rfh:
        for line in rfh:
            line=line.strip()
            line=re.sub('^\s+','',line)
            (freq, f_id, vdd) = re.split(r'\s+',line)
            fDict[freq]={"f_id":f_id, "vdd":vdd}
        # pdb.set_trace()
        dividerIndex=5
        fMin=float(min(fDict))
        fMax=float(max(fDict))
        while not (frequency > fMin and frequency < fMax):
            fMin*=2
            fMax*=2
            dividerIndex-=1
            if dividerIndex==0: 
                logging.warn("Divider is now down to 1. fMax={0}. Requested frequency of {1} is out of range\n".format(fMax,frequency))
                exit
        #Target frequency is now in range. Sweep the table and scale up by divider to 
        for fCandidate in fDict.keys():
            fCandidateScaled=float(fCandidate)*(2**(5-dividerIndex))
            if frequency<=fCandidateScaled:
                return_fid = '1'*dividerIndex + '{0:02b}'.format(int(float(fDict[fCandidate]["f_id"]))-124)
                return (return_fid, fDict[fCandidate]["vdd"])
    rfh.close()

#A function that needs to be called after emulation scan-in to program the FPGA PLL as required.
#It needs to be fed three address-data values in sequence (Numerator, Denominator and some other code known to Patrick Howe). Assume I only need 3, and support no more than 4 address bits.
def enable_fpga_pll(daq, pllStrobe, pllAddressDataSel_0, pllAddressDataSel_1):
#Strobe in sequence 0: Assume rising edge triggered
    daq.writePortName( pllAddressDataSel_1,0)    
    daq.writePortName( pllAddressDataSel_0,0)    
    daq.writePortName(pllStrobe,0)
    daq.writePortName(pllStrobe,1)

    daq.writePortName( pllAddressDataSel_1,0)    
    daq.writePortName( pllAddressDataSel_0,1)    
    daq.writePortName(pllStrobe,0)
    daq.writePortName(pllStrobe,1)

    daq.writePortName( pllAddressDataSel_1,1)    
    daq.writePortName( pllAddressDataSel_0,0)    
    daq.writePortName(pllStrobe,0)
    daq.writePortName(pllStrobe,1)


def closeChannels (daq):
    for name in daq.nameNumDict:
        daq.closeChannel(name)