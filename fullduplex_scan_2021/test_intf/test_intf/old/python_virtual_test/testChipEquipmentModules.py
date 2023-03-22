#!/usr/bin/python
import re
import os
import sys
import warnings
import logging
# from PyDAQmx import *
import numpy
logging.basicConfig(filename="./test.log",level=logging.DEBUG)
import pdb
import numpy

#import the gpib interface module
#import the usb interface module
#import the daq interface module

#This package was started by Visvesh Sathe for
#the rest of the group to build upon. It contains a variety of test equipment
#which will be digitally interfaced with for the purpose of chip test.
#Some examples are power supplies, scopes, ammeters, function generators and
#power cards.

# Basic naming convention: <function>_<model> unless class is more generic (e.g. power_supply below)

class power_channel():
    def __init__(self,channel, vmin, vnom, vmax):
        self.channel
        self.vmin=vmin
        self.v=vnom
        self.vmax=vmax
        self.i="undef"


###Standard power supply class. Code written with intent for CMOS test. Some supplies have negative polarity.
###Caller provides channel_name, minVdd, maxVdd. Once the channel classes are defined, you have
###pretty much have what you need to set voltages, read voltages and read currents
###Gpib power supplies designate ports for each instrument, and each port has multiple channels
###(for each power output)
class gpib_power_supply():
    def __init__(self,port,channel,supplyName,minVdd, maxVdd, nomVdd):
        self.port=port
        self.channel=channel
        self.name=supplyName
        self.minVdd=minVdd
        self.maxVdd=maxVdd
        self.nomVdd=nomVdd
        i=0
        self.setVoltage(nomVdd)

    #Class methods to be filled in based on gpib python wrappers
    #Set voltage value on supply
    def setVoltage(self,voltageValue):
        if voltageValue < self.minVdd:
            logging.warning('Voltage setting request of {0} for {1} below limit. Setting to lower limit'.format(voltageValue, self.name))
            voltageValue = self.minVdd

        if voltageValue > self.maxVdd:
            logging.warning('Voltage setting request of {0} for {1} above limit. Setting to upper limit'.format(voltageValue, self.name))
            voltageValue = self.maxVdd
        ########################################################################
        ########################################################################
        ##### Call the voltage setting function on the port with desired value
        #### Using self.port, self.channel.
        print "INFO: Setting voltage of {0} to {1}".format(self.name, voltageValue)
        ########################################################################
        ########################################################################
        self.getVoltage()
        if self.getVoltage()==voltageValue:
            logging.info ("Set voltage of {0} to {1}".format(self.name,voltageValue))
        else:
            logging.error ("Voltage setion of {0} on {1} does not match get value of {2}".format(voltageValue,self.name,self.getVoltage()))

    def getCurrent(self):
        ###Call the current getting function here####
        ########################################################################
        ########################################################################
        ###iPort = iGet(self.port, self.channel)
        iPort=0.5 #Placeholder
        ########################################################################
        ########################################################################
        return iPort
    ### End of supply class


    def getVoltage(self):
        ###Call the voltage getting function here####
        ########################################################################
        ########################################################################
        ###vMeas = iGet(self.port, self.channel)

        vMeas=1 #Placeholder
        ########################################################################
        ########################################################################
        return vMeas
    ### End of supply class

    def getPower(self):
        pMeas = self.getVoltage * self.getCurrent
        return pMeas

    ### End of supply class



###Again, here we need to provide relevant configuration. Need to understand from Fahim these are. USB port names?
###May have to define scope ports here also with an oscilloscope_port class.
class oscilloscope():
    def __init__(self,name,port,channel):
        self.port=port
        self.channel=channel
        self.name=name

    ###Read data from the scope. This may be specific for each metric
    ###(amplitude, frequency etc..) or one combined result to be parsed
    def getFrequency(self):
        print "Reading frequency from scope {0}\n".format(self.name)
##End of oscilloscope class


#Define a daq port with number, direction, name and logic state.
#Direction is defined as either "in" or "out"
class daq_port():
    def __init__(self,index,port,channel,name,direction,state):
        self.port = port
        self.channel = channel
        self.name = name
        self.direction = direction
        self.state = 0

###DAQ usb_6501 with 24 programmable channels. Config file will map signal, direction and pin number
#Ensure support functions/structures like getting daq port no. from name, and name from no. etc.
class daq_usb_6501():
    def __init__(self, configFile):
        self.portList=[]
        self.nameNumDict={}
        self.configFile=configFile
        self.readConfigFile()
        self.initChannels()

    def initChannels(self):
       for name in self.nameNumDict:
          port = self.nameNumDict[name][1]
          channel = self.nameNumDict[name][2]
          task_handle = self.nameNumDict[name][3]
          # DAQmxCreateTask("",byref(task_handle))
         # # print "Dev2/port{0}/line{1}".format(port,channel)
          # if self.portList[self.nameNumDict[name][0]].direction == "out":
            # #print name
            # DAQmxCreateDOChan(task_handle, "Dev2/port{0}/line{1}".format(port, channel), "", DAQmx_Val_ChanPerLine)
          # else:
            # DAQmxCreateDIChan(task_handle, "Dev2/port{0}/line{1}".format(port, channel), "", DAQmx_Val_ChanPerLine)
# #            print task_handle


    def closeChannel(self, name):
        # DAQmxStopTask(self.nameNumDict[name][3])
        # DAQmxClearTask(self.nameNumDict[name][3])
        print "closing channel\n"

    def readConfigFile(self):
        with open(self.configFile, 'r') as rfh:
            lineList=rfh.readlines()
        for line in lineList:
            line.strip()
            line = line.split()
            #line=re.sub(r'\s+$','',line)
            if len(line) != 0:
                if line[0] == '#':
                    # pdb.set_trace()
                    continue  #Ignore comments
                #number, name, direction = re.split(r'\s+',line)
#                print line
                index, port, channel, name, direction = line
                # port=daq_port(number,name,direction,0)
                # self.portList.append(port)
                # self.portList.append(daq_port(number,name,direction,0))
                
                self.portList.append(daq_port(index, port,channel,name,direction,0))
                self.nameNumDict[name]=(int(index), port, channel, name)


    ##Done reading config file

    def readPortNo(self,index, port,channel,task_handle):
        ####Function to read from the port given the direction
        ########################################################################
        ########################################################################
        
        read = numpy.zeros((1,), dtype=numpy.dtype('uint8'))

        # DAQmxTaskControl(task_handle, DAQmx_Val_Task_Reserve)
        # DAQmxStartTask(task_handle)
        # DAQmxReadDigitalLines(task_handle, 1, -1, DAQmx_Val_GroupByChannel, read, 1, None, None, None)        
        # DAQmxStopTask(task_handle)

        #print "reading port no {0}, channel {1}".format(port, channel)
        ########################################################################
        ########################################################################
        #print "reading port {} as {}".format(port,logicState)

        logicState = read[0]
        #print logicState

        self.portList[index].state=logicState
        return logicState

    def readPortName(self,name):
        # for i in self.nameNumDict: print i, self.nameNumDict[i]
        index, port, channel, task_handle=self.nameNumDict[name]
        logicState=int(self.readPortNo(index, port, channel, task_handle))
        #print "reading port {0} with value {1}".format(name,logicState)
        return logicState


    def writePortNo(self,index, port,channel,task_handle,state):
        port=int(port)
        channel=int(channel)
        state = numpy.array([state], dtype=numpy.dtype('uint8'))
        if(self.portList[index].direction == "out"):
            ####Function to write port to state given the direction
            ########################################################################
            ########################################################################
            #print task_handle
            # DAQmxTaskControl(task_handle, DAQmx_Val_Task_Reserve)
            # DAQmxStartTask(task_handle)
            # DAQmxWriteDigitalLines(task_handle, 1, False, 10.0, DAQmx_Val_GroupByChannel, state, None, None)
            # DAQmxStopTask(task_handle)
            #print "writing {0} to port {1}, channel {2}".format(state[0], port, channel)
            ########################################################################
            ########################################################################
            actual_state = self.readPortNo(index,port,channel,task_handle)
            if actual_state != state:
                logging.warning("Writing {0} to port {1}, channel {2} failed which still has state {3}".format(state[0],port,channel,actual_state))
                print "Writing {0} to port {1}, channel {2} failed which still has state {3}".format(state[0],port,channel,actual_state)
            else:
                self.portList[index].state=state
                #print "port {0}, channel {1} successfully set".format(port, channel)
        else:
            logging.warning("Ignoring request to write {0} to port {1} since its port dir is {2}".format(state,number,self.portList[index].direction))

    def writePortName(self,name,state):
        index, port, channel, task_handle=self.nameNumDict[name]
        logicState=self.writePortNo(index, port,channel,task_handle,state)

