##/*********************************************************************
##* Description:
##*     ScanConfig
##*********************************************************************/

import visa

from ti_abstract import TI_ABSTRACT_Oscilloscope

# Oscilloscope class to extract data from the oscilloscope
# Agilent InfiniiVision MSO7104B

class MSO7104B_oscope(TI_ABSTRACT_Oscilloscope):

    resource_id = "USB0::0x0957::0x175D::MY49520175::INSTR"    

    def __init__(self):
        self.freq = 0
        self.pk_to_pk = 0
        self.amp = 0
        self.stats = ""

    # Returns the frequency of the probe channel
    def get_frequency(self, channel):
        if (channel > 4):
            raise RuntimeError('Invalid channel number: {}'.format(channel))

        rm = visa.ResourceManager()

        my_instrument = rm.open_resource(MSO7104B_oscope.resource_id)
        channel_select = ":MEASURE:SOURCE CHANNEL" + str(channel)
        my_instrument.write(channel_select)
        self.freq = float(str(my_instrument.query(":MEASURE:FREQUENCY?")))
        return self.freq

    # Returns the peak to peak amplitude of the probe channel
    def get_pk_to_pk(self, channel):
        if (channel > 4):
            raise RuntimeError('Invalid channel number: {}'.format(channel))
            
        rm = visa.ResourceManager()

        my_instrument = rm.open_resource(MSO7104B_oscope.resource_id)
        channel_select = ":MEASURE:SOURCE CHANNEL" + str(channel)
        my_instrument.write(channel_select)
        self.pk_to_pk = float(str(my_instrument.query(":MEASURE:VPP?")))
        return self.pk_to_pk

    # Returns the mean amplitude of the probe channel
    def get_mean_amplitude(self, channel):
        if (channel > 4):
            raise RuntimeError('Invalid channel number: {}'.format(channel))
            
        rm = visa.ResourceManager()

        my_instrument = rm.open_resource(MSO7104B_oscope.resource_id)
        channel_select = ":MEASURE:SOURCE CHANNEL" + str(channel)
        my_instrument.write(channel_select)
        self.amp = float(str(my_instrument.query(":MEASURE:VAMPLITUDE?")))
        return self.amp

    # Returns the statistics of all the measurements shown on the oscope in a comma
    # seperated list. The format is shown below:
    # Measurement Label, Current, Min, Max, Mean, Std Dev, Count
    def get_stats(self, channel):
        if (channel > 4):
            raise RuntimeError('Invalid channel number: {}'.format(channel))
            
        rm = visa.ResourceManager()

        my_instrument = rm.open_resource(MSO7104B_oscope.resource_id)
        channel_select = ":MEASURE:SOURCE CHANNEL" + str(channel)
        my_instrument.write(channel_select)
        self.stats = str(my_instrument.query(":MEASURE:RESULTS?"))

        arr = self.stats.split(",")
        count = 0
        for i in range(0, len(arr), 7):
            print(arr[i])
            print("Current: " + str(float(arr[i+1])))
            print("Min: " + str(float(arr[i+2])))
            print("Max: " + str(float(arr[i+3])))
            print("Mean: " + str(float(arr[i+4])))
            print("Std Dev: " + str(float(arr[i+5])))
            print("Count: " + str(float(arr[i+6])) + "\n")

        return self.stats






