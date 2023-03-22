#!/usr/bin/python 
import sys
import os
import re
import logging

def clean_line(line):
    line=line.strip()
    if re.search('^\s*#', line): exit  #Ignore opening comments
    line=re.sub('^\s','',line)
    line=re.sub('\s$','',line)
    line=re.sub('#.*','',line) #Remove trailing comments
    line=re.sub('[:=\[\]]',' ',line)
    line = re.sub('^\s*$', '',line)
    line=re.sub('\s+',' ',line)
    line.strip()
    return line

###IMPORTANT!!: File designates design inputs. For the purpose of the scan chain then, these are outputs and vice versa!!
def scanParse(lineList): 
    module, value, signal, dirn, value, numBits = "x" , "x", "x", "x", "x", "x"#Default
    valid=1
    
    if (len(lineList)<2): valid=0
    if len(lineList)==2:  #Module declaration
        if(lineList[0] == 'module'):
            module=lineList[1]
        else: #output single_bit 
            (dirn, signal)=lineList
            if(dirn !='output'): sys.exit("Invalid direction in ScanConfig")
            numBits=1
            # includeScanSignal=1
    elif len(lineList)==3: #input/output single_bit value
        (dirn, signal, value)=lineList
        numBits=1
        # includeScanSignal=1
    elif len(lineList)==4:#output rangehigh rangeslow signal     
        if(not re.search('output', lineList[0])): sys.exit("Invalid line in ScanConfig. 4 element line that is not an output:\n{line}".format(line=lineList))
        (dirn, bitMax, bitMin, signal) = lineList
        numBits=abs(int(bitMax)-int(bitMin)+1)
        # Signal=1
    elif len(lineList)==5: #input rangehigh rangelow signal value    OR output rangehigh rangelow signal value
        (dirn, bitMax, bitMin, signal, value) = lineList
        numBits=abs(int(bitMax)-int(bitMin)+1)
        # includeScanSignal=1
        
    #IMPORTANT!: switch out the inputs and outputs to account for pin reversal for scan module definition
    dirn="input" if (dirn=="output") else "output"
    return(valid,module,dirn,numBits,signal,value)

def readScanFile(scanConfigFile):
    scanList=[]
    designModule='x'
    with open(scanConfigFile) as rfh:
        lines=rfh.readlines()
    module = "x"
    for line in lines:
        line=clean_line(line)
        lineList=re.split('\s+',line)
        (valid, module, dirn, numBits, signal, value) = scanParse(lineList)
        if module=='x' and valid==1: 
            scanList.append((signal,numBits,dirn,value))
        elif (module!='x'):
            designModule=module
    return designModule,scanList

#Append the scan values BACKWARDS (first to last) since the way the array is fed in the testbench is
# using indices of the array ... i.e [0] => rightmost first access
# signal,numBits,dirn,value
def genScanString(scanList):
    scanString=""
    assignments=""
    scanVal=''
    totalChainLength=0
    for i in range(len(scanList)-1,-1,-1):
        name = scanList[i][0]
        numBits = scanList[i][1]
        direction = scanList[i][2]
        value = scanList[i][3]
        if(re.search('[hbd]',value)): #Value represented as hex or bin or dec.
            signal_assignment= str(value)
                
        else:
            if(re.search('x',value)): #The value is slated as a dont care or x
                signal_assignment= str(numBits)+'\'b'+ numBits * 'x'
            else:
                # hexVal=re.sub('^0x','',hex(int(value)))
                signal_assignment= str(numBits)+'\'d'+ str(value)
        if (direction=='output'): #Thes are outputs, but you've switched to the reference of scan outputs.
            assignments+= str(name) + "=" + signal_assignment  + ';\n'
            scanString +=  str(name) + ','
        else:
            scanString+= signal_assignment + ',' 


    scanString=re.sub(',$','',scanString)
    scanString+=''
    return (assignments,scanString)

def getChainLength(scanList):
    length=0
    for i in range(len(scanList)):
        length+=scanList[i][1]
    return length

def genSetDefaultTestVariables(scanList,outFile):
    assignments,scanString=genScanString(scanList)
    functionString="""
    task set_default_test_variables();
       begin
          %s
       end
    endtask
""" %(assignments)
    wfh=open(outFile, 'w')
    wfh.write(functionString)
    wfh.close()


def genScanInTask(scanList,outFile):
    assignments,scanString=genScanString(scanList)
    n=getChainLength(scanList)
    functionString="""
   reg [%s:0] scanReg, scanOutReg;
    task scan_inputs();
      integer i=0;
      begin
	 scanReg={%s};
	 for(i=0;i<%d;i=i+1) begin
	    #10 scan_in=scanReg[i];
	    #10 phi=1;
	    #1 phi=0;
	    #10 phi_bar=1;
	    #1 phi_bar=0;
	 end
         update=1;
         #100 update=0;
      end
   endtask 
""" %(n-1,scanString,n)
    wfh=open(outFile, 'a')
    wfh.write(functionString)
    wfh.close()


def genScanOutTask(scanList,outFile):
    n=getChainLength(scanList)
    functionString="""   task scan_outputs();      
      integer i;	
     begin
	capture=1; //Capture the signals
	phi_bar=1; //Clock phi_bar to get the captured signals into the chain.
	#10 phi_bar=0;
	scanOutReg[0]=scan_out;	 
        #10
	capture=0; //Return to regular scan mode
	
	for(i=1;i<%d;i=i+1) begin
	   #10 phi=1;
	   #1 phi=0;
	    #10 phi_bar=1;
	    #1 phi_bar=0;
	    scanOutReg[i]=scan_out;
	 end
      end
   endtask
 """ %(n)
    wfh=open(outFile, 'a')
    wfh.write(functionString)
    wfh.close()
                  #Define scan_in
                  #Define scan_out
                  #Define report_results
                  #Define scan_module 0 with all the outputs
                  #


#The scanout chain is as long as the scan in chain. Extract data based on what you see from scanout from the locations
#Specified in the scan structure. Order of the chain is the order of the scanList.
def genReportResults(scanList,fileName,format,outFile):
    writeString=""
    rangeMin,rangeMax=-1,-1
    writeString = "$fwrite (file, \"Time is %d\\n\\n\\n\\n\\n\", $time);\n"
    print ("format is ", format)
    for i in range(len(scanList)):
        (signal,numBits,dirn,value)=scanList[i]
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
        mFormat =mFormat if re.search('x', format) else format
        rangeMin=int(rangeMax)+1
        rangeMax=int(rangeMax)+ int(numBits)
        writeString += "$fwrite (file,\"%s %s = %s\\n\", %s, scanOutReg[%d:%d]);\n" %(dirn, "%s", "%"+mFormat, "\""+signal+"\"", rangeMax,rangeMin)
        
        functionString="""  task report_results();
      integer file;      
      begin
	 file = $fopen("%s", "w");
	 %s
      end        
        $fclose(file);
   endtask // report_results
""" %(fileName,writeString)
    wfh=open(outFile, 'a')
    wfh.write(functionString)
    wfh.close()

#Get the scan signals and name the wires as inputs/outputs. This is used as part of the module declaration for the actual scan module.
def genScanPinDeclaration(scanList):
    string=""
    rangeMin,rangeMax=-1,-1
    for i in range(len(scanList)):
        # (signal,numBits,dirn,value)=scanList[i]
        # rangeMin=rangeMax+1
        # rangeMax=rangeMax + int(scanList[i][1])
        if(scanList[i][1]>1):
            string += scanList[i][2] + " [" + str(scanList[i][1]-1) + ":" + "0" + "] " + scanList[i][0] + ",\n"
        else:
            string += scanList[i][2]  + " " + scanList[i][0] + ",\n"
    string=re.sub(',$','',string);
    return string

def genScanDataInAssignments(scanList):
    string=""
    rangeMin,rangeMax=-1,-1
    # (signal,numBits,dirn,value)=scanList[i]
    string+='//Make assignments for chip_data_in\n'
    for i in range(len(scanList)):
        rangeMin=rangeMax+1
        rangeMax=rangeMax + int(scanList[i][1])
        if(scanList[i][2]=="output"): #Check if this is a scan_chain output
            string+= 'assign %s = chip_data_in[%d:%d];\n' %(scanList[i][0],rangeMax,rangeMin)
            string=re.sub(',$','',string)
    return string

def genScanDataOutAssignments(scanList):
    string=""
    rangeMin,rangeMax=-1,-1
    # (signal,numBits,dirn,value)=scanList[i]
    string+='//Make assignments for chip_data_out\n'
    for i in range(len(scanList)):
        rangeMin=rangeMax+1
        rangeMax=rangeMax + int(scanList[i][1])
        # if(scanList[i][2]=="input") : 
        string+= 'assign chip_data_out[%d:%d] = %s;\n' %(rangeMax,rangeMin,scanList[i][0])
    string=re.sub(',$','',string)
    return string



def genScanModule (module,scanList):
    moduleName = "scan_module_" + module
    n=int(getChainLength(scanList))
    scanDeclaration = genScanPinDeclaration(scanList)
    scan_data_in_assignments = genScanDataInAssignments(scanList)
    scan_data_out_assignments =  genScanDataOutAssignments(scanList)

    functionString="""
module %s 
  (
   input 	 scan_in,
   input 	 update,
   input 	 capture,
   input 	 phi,
   input 	 phi_bar,
   output 	 scan_out,
   %s
   );
   wire [%d:0] scan_cell_out;
   wire [%d:0] chip_data_out;
   wire [%d:0] chip_data_in;
   
   scan_cell sc[%d:0] (
		       .scan_in({scan_in,scan_cell_out[%d:1]}),
		       .scan_out(scan_cell_out[%d:0]),
		       .phi(phi),
		       .phi_bar(phi_bar),
		       .capture(capture),
		       .update(update),
		       .chip_data_out(chip_data_out),
		       .chip_data_in(chip_data_in)
		       );
   assign scan_out = scan_cell_out[0];
   //Autogen all these assignments.
   %s
   %s
endmodule // %s
""" %(moduleName, scanDeclaration, n-1, n-1, n-1, n-1, n-1, n-1, scan_data_in_assignments, scan_data_out_assignments,moduleName)
    fileName= moduleName + ".v"
    with open(fileName, 'w') as wfh:
        wfh.write(functionString)
    wfh.close()
    return moduleName
# End of genScanModule
########

###### Order matters. scanin opens in 'w' mode and wipes taskfile clean each new run...
def genScanTasks(scanList,taskFile,resultOut,writeFormat):
    genSetDefaultTestVariables(scanList,taskFile)
    genScanInTask(scanList,taskFile)
    genScanOutTask(scanList,taskFile)
    genReportResults(scanList,resultOut,writeFormat,taskFile)
#######

def genScanInstantiation(module, scanList):
    scanData=''
    for i in range(len(scanList)):
        # (signal,numBits,dirn,value)=scanList[i]
        scanData+='.' + scanList[i][0] + '(' + scanList[i][0] + '),\n'
    scanData=re.sub(',$','',scanData)
    string='''%s sm0 (
			  .scan_in(scan_in),
			  .scan_out(scan_out),
			  .update(update),
			  .capture(capture),
			  .phi(phi),
			  .phi_bar(phi_bar),
			  %s );\n''' %(module, scanData)
    return string


#Add the scan_module_declaration as a sibling of the module that will accept/provide scan data.
def genScanInterfaceFile(verilogFile,scanModuleName,scanList,module,verilogOut):
    fh=open(verilogFile,'r')
    wfh=open(verilogOut,'w')
    verilogTemplateList=fh.readlines()
#find endmodule index
    endmoduleIndex= [i for i,item in enumerate(verilogTemplateList) if re.search('^\s*endmodule',item)] #Remove the endmodule
    verilogTemplateList.pop(endmoduleIndex[0])
#Generate the module declaration in the template
    string="".join(verilogTemplateList)
    moduleString=genScanInstantiation(scanModuleName, scanList)
    # wfh.write('`include \"%s\"\n' %(taskFile))
    wfh.write("//Generated by the scanGen.py script by concatenating the {0} ".format(verilogFile))
    wfh.write("file with the scan instantiation\n")
    wfh.write(string)
    wfh.write(moduleString)
    wfh.write("endmodule\n")
    wfh.close()


def genTaskFile(scanList,taskFile,resultOut,writeFormat):
#write the taskfile to be included in to the testbench
    wfh=open(taskFile,'a')
    genScanTasks(scanList,taskFile,resultOut,writeFormat)
    wfh.close()

def genPWLFile(scanList,pwlFile):
    wfh=open(pwlFile,'w')
    scanBitTrace=genBitTrace(scanList)
    # print len(scanBitTrace), scanBitTrace
    defineParams(scanBitTrace,wfh)
    write_scanIn_pin(scanBitTrace,wfh)
    write_phi_pin(scanBitTrace,wfh)
    write_phi_bar_pin(scanBitTrace,wfh)
    write_update_pin(scanBitTrace,wfh)
    write_reset_pin(scanBitTrace,wfh)
    write_capture_pin(scanBitTrace,wfh)

#First get the vector of binary data you need. Back of the scanConfig file to front, msb->lsb
def genBitTrace(scanList):
    scanTrace=''
    for i in range(0,len(scanList),1):
        # print scanList[i][0:2]
        value = scanList[i][3]
        stringLength=scanList[i][1]
        value = "0" if re.search(r'x',value) else value
        if re.search(r'\'b[01]+',value) :
            match=re.search(r'\'b(?P<binString>[01]+)',value)
            scanTrace = scanTrace + match.group('binString')[::-1]
        elif re.search(r'\'h[0-9abcdef]+',value):
            match=re.search(r'\'h(?P<hexString>[0-9abcdef]+)',value)
            scanTrace = scanTrace+ bin(int(match.group('hexString'),16))[2:].zfill(stringLength)[::-1]
        elif re.search(r'\'d[0-9]+',value):
            match=re.search(r'\'d(?P<digString>[0-9]+)',value)
            scanTrace = scanTrace + bin(match.group('digString'))[2:].zfill(stringLength)[::-1]
        else:
            scanTrace = scanTrace + bin(int(value))[2:].zfill(stringLength)[::-1]
    return scanTrace

            
def defineParams(scanBitTrace,wfh):
    string='''
    .param scan_period=40n
    .param scan_transition=2n
    .param reset_delay = 10n
    .param experiment_start_time = '%d * scan_period'
    .param run_time = 2u
    .param scan_out_time = 'experiment_start_time + run_time + 5*scan_period'
    .param experiment_stop_time = 'scan_out_time + %d * scan_period '
''' %(len(scanBitTrace), len(scanBitTrace))
    wfh.write(string)
    

def write_scanIn_pin(scanBitTrace,wfh):
    wfh.write("\n\n************************\n")
    wfh.write("************************\n")
    wfh.write("************************\n")
    wfh.write("v_scan_in scan_in 0 PWL (\n")
    wfh.write("+0 0\n")
    for i in range(len(scanBitTrace)):
        wfh.write("+'{count}*scan_period+scan_transition' {bitVal}\n".format(count=i,bitVal=scanBitTrace[i]))
        wfh.write("+'{next_count}*scan_period' {bitVal}\n".format(next_count=i+1, bitVal=scanBitTrace[i]))
    wfh.write("+)")
        
 
def write_phi_pin(scanBitTrace,wfh):
    wfh.write("\n\n************************\n")
    wfh.write("************************\n")
    wfh.write("************************\n")
    wfh.write("v_phi phi 0 PWL (\n")
    # wfh.write("0 0\n")
    for i in range(len(scanBitTrace)):
        wfh.write("+'{count}*scan_period' 0\n".format(count=i))
        wfh.write("+'{count}*scan_period+scan_transition' vdd\n".format(count=i))
        wfh.write("+'{count}*scan_period' vdd\n".format(count=i+0.25))
        wfh.write("+'{count}*scan_period+scan_transition' 0\n".format(count=i+0.25))
    for i in range(len(scanBitTrace)):
        wfh.write("+'scan_out_time+{count}*scan_period' 0\n".format(count=i))
        wfh.write("+'scan_out_time+{count}*scan_period+scan_transition' vdd\n".format(count=i))
        wfh.write("+'scan_out_time+{count}*scan_period' vdd\n".format(count=i+0.25))
        wfh.write("+'scan_out_time+{count}*scan_period+scan_transition' 0\n".format(count=i+0.25))
    wfh.write("+)")

def write_phi_bar_pin(scanBitTrace,wfh):
    wfh.write("\n\n************************\n")
    wfh.write("************************\n")
    wfh.write("************************\n")
    wfh.write("v_phi_bar phi_bar 0 PWL (\n")
    # wfh.write("0 0\n")
    for i in range(len(scanBitTrace)):
        wfh.write("+'{count}*scan_period' 0\n".format(count=i+0.45))
        wfh.write("+'{count}*scan_period+scan_transition' vdd\n".format(count=i+0.45))
        wfh.write("+'{count}*scan_period' vdd\n".format(count=i+0.7))
        wfh.write("+'{count}*scan_period+scan_transition' 0\n".format(count=i+0.7))
    # Print out the solitary phi_bar you need to pulse the capture
    wfh.write("+'scan_out_time-1.55*scan_period' 0\n")
    wfh.write("+'scan_out_time-1.55*scan_period + scan_transition' vdd\n")
    wfh.write("+'scan_out_time-1.3*scan_period' vdd\n")
    wfh.write("+'scan_out_time-1.3*scan_period + scan_transition' 0\n")
    for i in range(len(scanBitTrace)):
        wfh.write("+'scan_out_time+{count}*scan_period' 0\n".format(count=i+0.45))
        wfh.write("+'scan_out_time+{count}*scan_period+scan_transition' vdd\n".format(count=i+0.45))
        wfh.write("+'scan_out_time+{count}*scan_period' vdd\n".format(count=i+0.7))
        wfh.write("+'scan_out_time+{count}*scan_period+scan_transition' 0\n".format(count=i+0.7))
    wfh.write("+)")

def write_update_pin(scanBitTrace,wfh):
    wfh.write("\n\n************************\n")
    wfh.write("************************\n")
    wfh.write("************************\n")
    wfh.write("v_update update 0 PWL (\n")
    wfh.write("+0 0\n")
    wfh.write("+'{count}*scan_period' 0\n".format(count=len(scanBitTrace)))
    wfh.write("+'{count}*scan_period+scan_transition' vdd\n".format(count=len(scanBitTrace)))
    wfh.write("+'{count}*scan_period' vdd\n".format(count=1+len(scanBitTrace)))
    wfh.write("+'{count}*scan_period+scan_transition' 0\n".format(count=1+len(scanBitTrace)))
    wfh.write("+)")

def write_reset_pin(scanBitTrace,wfh):
    wfh.write("\n\n************************\n")
    wfh.write("************************\n")
    wfh.write("************************\n")
    wfh.write("v_reset reset 0 PWL (\n")
    wfh.write("+0 vdd\n")
    wfh.write("+'{count}*scan_period' vdd\n".format(count=len(scanBitTrace)+5))
    wfh.write("+'{count}*scan_period+scan_transition' 0\n".format(count=len(scanBitTrace)+5))
    wfh.write("+)")


# Capture starts before the phi_bar pulse and outlasts it by a half-cycle
def write_capture_pin(scanBitTrace,wfh):
    wfh.write("\n\n************************\n")
    wfh.write("************************\n")
    wfh.write("************************\n")
    wfh.write("v_capture capture 0 PWL (\n")
    wfh.write("+0 0\n")
    wfh.write("+'scan_out_time-3*scan_period' 0\n")
    wfh.write("+'scan_out_time-3*scan_period + scan_transition' vdd\n")
    wfh.write("+'scan_out_time-1*scan_period' vdd\n")
    wfh.write("+'scan_out_time-1*scan_period + scan_transition' 0\n")
    wfh.write("+)")


def genTestScanVector(scanList):
    scanString=""
    scanVal=''
    totalChainLength=0
    for i in range(len(scanList)):
        name, numBits, direction, value  = scanList[i]
        # numBits = scanList[i][1]
        # direction = scanList[i][2]
        # value = scanList[i][3]
        if(re.match(r'.*[hbd]',value)):
            match=re.match(r'.*(?P<format>[hbd])(?P<val>\d+)',value)
            mFormat=match.group('format')
            mVal  = match.group('val')
        elif(re.match(r'x',value)): 
            mVal=0
            mFormat='d'
        else:
            match=re.match(r'(?P<val>\d+)',value)
            mFormat='d'
            mVal = match.group('val')
        
        if mFormat=='h':
            signal_assignment=bin(int(mVal,16))[2:].zfill(numBits)
        elif mFormat == 'b' :
            signal_assignment=mVal
        else:
            signal_assignment=bin(int(mVal))[2:].zfill(numBits)
                                
        #Reverse the signal assignment to set the lsb as the 0th index
        signal_assignment=signal_assignment[::-1]
        scanString+= signal_assignment 
    scanString=re.sub(',$','',scanString)
    scanVector = [int(i) for i in list(scanString)]
    return (scanVector)



#Generate a dict of dict given scanList and a scanvector (input or output)
#First index is signal name. Others are numBits, dirn, value and index
def genScanDicts(scanList,scanVector):
    rangeMin,rangeMax=-1,-1
    scanDict={}
    for i in range(len(scanList)):
        (signal,numBits,dirn,value)=scanList[i]
        #print scanList[i]
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
        if(inputScanDict[key]!=outputScanDict[key]):
            logging.warning("Warning! Signal {0} scanned in as {1} but scanned out as {2}\n".format(key, inputScanDict[key]["value"], outputScanDict[key]["value"]))


#Enable swapping out of a scan_chain signal from its scanConfig.txt file with a runtime changable value
#Handy for sweeping scan related signals
def modifyScanList(entry,scanList,newValue):
    for i in range(len(scanList)):
        (signal,numBits,dirn,value)=scanList[i]
        if signal != entry:
            next
        else:
            scanList[i] = (signal,numBits,dirn,newValue)
            #Decimal assumed in this context since calling function deals with int dacCode
            exit



def readEntryScanDict(entry,inputScanDict):
    for key in inputScanDict.keys():
        if key != entry:
            next
        else:
            return(inputScanDict[key]["value"])
            #Decimal assumed in this context since calling function deals with int dacCode
            exit


def readDecimal(entry):
    temp = [int(s) for s in re.findall(r'[-+]?\d+[\.]?\d*[eE]?[-+]?\d*', entry)]
    return(temp[1])

def writeDecimal(bits, entry):
    return('%d\'d%d' % (bits, entry))

