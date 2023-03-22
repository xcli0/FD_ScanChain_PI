#!/usr/bin/env python

import u3
import sys
import math
import numpy as np
from enum import Enum
from abc import ABCMeta, abstractmethod
from time import sleep
import numpy as np

from ti_abstract import TI_ABSTRACT_VoltageRegulator

# Programmable Voltage Regulator class

class I2CInterface(object):
    __metaclass__ = ABCMeta

    # Write a list of bytes
    @abstractmethod
    def write(self, addr, send_bytes): pass

    # Return a list of bytes
    @abstractmethod
    def read(self, addr, send_bytes, num_bytes_2_rec): pass

    # Write to an i2c channel
    def write_channel(self, addr, send_bytes, chan): pass

    # Read from an i2c channel
    def read_channel(self, addr, send_bytes, num_bytes_2_rec, chan): pass


# ProgVr class that interacts with the labjack
class ProgVr(TI_ABSTRACT_VoltageRegulator):
    PROG_DOMAIN_NAMES = [
        'VOUT0', 'VOUT1', 'VOUT2', 'VOUT3',
        'VOUT4', 'VOUT5', 'VOUT6', 'VOUT7'
    ]
    FIXED_DOMAIN_NAMES = [
        'VOUT_3V3'
    ]

    def __init__(self, labjack, scl_pin, sda_pin, vout_en_pin, rdy_pin, i2c_addr):
        # pin config
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.vout_en_pin = vout_en_pin
        self.rdy_pin = rdy_pin
        # init labjack
        self.lj = labjack
        # if len(devices) > 1:
            # raise RuntimeError("More than one labjack attached")
        # else:
            # device_id = devices.keys()[0]
            # self.lj = devices[device_id]
        # config pins
        self.lj.configDigital(scl_pin, sda_pin)
        # voltage reg device
        self.super_vreg = SUPER_VREG(i2c_addr)
        # i2c
        self.i2c = LabJackI2C(
            labjack=self.lj, scl_pin=scl_pin, sda_pin=sda_pin, speed_adj=100,
            i2c_mux=self.super_vreg.i2c_mux
        )
        # startup settings
        self.init()

    # Startup settings
    def init(self):
        self._run_tests()

    # Test function that encapsulates all the tests functions
    def _run_tests(self):
        r_sense_init = 5E3    # (ignore these comments, they aren't valid anymore) 4V on v_mon for 100mA
        r_shunt_init = 1000   # ..... ~7.7mA shunt load @ 0.3V
        r_set_init   = 10E3   # ..... 1V
        # Test that we can talk to the i2c mux
        # self._test_i2c_mux_channels()

        # Set the prog resistors and check their codes
        self._test_set_vout_domains(r_sense_init, r_shunt_init, r_set_init)

        # Set all resistors to startup values and read back their values
        # self.super_vreg.set_all_resistors('RSENSE', r_sense_init, self.i2c)
        # self.super_vreg.set_all_resistors('RSHUNT', r_shunt_init, self.i2c)
        # self.super_vreg.set_all_resistors('RSET',   r_set_init, self.i2c)

        # initial setting
        self.set_voltage('VOUT0', 0.5)
        print ('Voltage VOUT0: ' + str(self.get_voltage('VOUT0')))
        print ('Current VOUT0: ' + str(self.get_current('VOUT0')))

        # self.set_voltage('VOUT1', 0.6)
        # print ('Voltage VOUT1: ' + str(self.get_voltage('VOUT1')))
        # print ('Current VOUT1: ' + str(self.get_current('VOUT1')))

        # self.set_voltage('VOUT2', 0.5)
        # print ('Voltage VOUT2: ' + str(self.get_voltage('VOUT2')))
        # print ('Current VOUT2: ' + str(self.get_current('VOUT2')))

        # self.set_voltage('VOUT3', 0.5)
        # print ('Voltage VOUT3: ' + str(self.get_voltage('VOUT3')))
        # print ('Current VOUT3: ' + str(self.get_current('VOUT3')))

        # self.set_voltage('VOUT4', 0.5)
        # print ('Voltage VOUT4: ' + str(self.get_voltage('VOUT4')))
        # print ('Current VOUT4: ' + str(self.get_current('VOUT4')))

        # self.set_voltage('VOUT5', 0.5)
        # print ('Voltage VOUT5: ' + str(self.get_voltage('VOUT5')))
        # print ('Current VOUT5: ' + str(self.get_current('VOUT5')))

        # self.set_voltage('VOUT6', 0.5)
        # print ('Voltage VOUT6: ' + str(self.get_voltage('VOUT6')))
        # print ('Current VOUT6: ' + str(self.get_current('VOUT6')))

        # self.set_voltage('VOUT7', 0.5)
        # print ('Voltage VOUT7: ' + str(self.get_voltage('VOUT7')))
        # print ('Current VOUT7: ' + str(self.get_current('VOUT7')))

        # Set the steady state voltage
        print('')
        #for domain in ProgVr.PROG_DOMAIN_NAMES:
        #for domain in ['VOUT0']:
        #    for v in np.arange(0.3, 1.0, 0.1):
        #        sleep(1)
        #        self.set_voltage(domain, v)
        #        print ('Voltage VOUT0: ' + str(self.get_voltage('VOUT0')))
        #        print ('Current VOUT0: ' + str(self.get_current('VOUT0')))
        #self._test_resistor_settings()
        #print ('Voltage VOUT0: ' + str(self.get_voltage('VOUT0')))
        #print ('Current VOUT0: ' + str(self.get_current('VOUT0')))
        #print ('Startup current VOUT0: ' + str(self.get_current('VOUT0')))

        #self.super_vreg.vsense.adc4._write_config_register(0, 4, 0, 0, 4, 0, 0, 0, 3, self.i2c)
        #config_bytes = self.super_vreg.vsense.adc4._read_config_register(self.i2c)
        #print ('ADC4 config register: {}, {}'.format(hex(config_bytes[1]), hex(config_bytes[0])))
        #for i in range(0, 4):
            #print 'Voltage on chan {}: {}'.format(i, self.super_vreg.vsense.adc4.read_voltage(i, self.i2c))

        #print ('Startup voltage VOUT0: ' + str(self.super_vreg.vsense.adc4.read_voltage(0, self.i2c)))
        #config_bytes = self.super_vreg.vsense.adc4._read_config_register(self.i2c)
        #print ('ADC4 config register: {}, {}'.format(bin(config_bytes[1]), bin(config_bytes[0])))

        #print ('Startup voltage VOUT0: ' + str(self.super_vreg.vsense.adc4.read_voltage(2, self.i2c)))
        #config_bytes = self.super_vreg.vsense.adc4._read_config_register(self.i2c)
        #print ('ADC4 config register: {}, {}'.format(bin(config_bytes[1]), bin(config_bytes[0])))

        #print ('Startup voltage VOUT0: ' + str(self.super_vreg.vsense.adc4.read_voltage(3, self.i2c)))
        #config_bytes = self.super_vreg.vsense.adc4._read_config_register(self.i2c)
        #print ('ADC4 config register: {}, {}'.format(bin(config_bytes[1]), bin(config_bytes[0])))

        #print ('Startup VOUT0 RSENSE wiper code: ' +
        #    str(self.super_vreg.vreg1.r_sense._get_wiper_code(0, self.i2c))
        #)

        #print ('Startup VOUT0 RSET wiper code: ' +
        #    str(self.super_vreg.vreg1.r_set._get_wiper_code(0, self.i2c))
        #)
        #print ('Startup VOUT0 RSHUNT wiper code: ' +
        #    str(self.super_vreg.vreg1.r_shunt._get_wiper_code(0, self.i2c))
        #)

    # Test that we can talk to the i2c mux
    def _test_i2c_mux_channels(self):
        print 'Testing i2c mux communication...'
        all_good = True
        for channel in range(1, 9):
            self.super_vreg.i2c_mux.set_channel(self.i2c, channel)
            channel_code = self.super_vreg.i2c_mux._get_channel_setting(self.i2c)
            channel_dec = hot_to_dec(channel_code)
            print '\tChannel setting: {}, Actual: {}'.format(channel, channel_dec)
            if channel_dec != channel:
                all_good = False
        if all_good:
            print 'OK i2c mux is alive'

    def _test_set_vout_domains(self, r_sense_init, r_shunt_init, r_set_init):
        print 'Setting initial values for VOUT domains...'
        all_good = True
        for domain in ProgVr.PROG_DOMAIN_NAMES:
        # for domain in ['VOUT0']:
            vreg = self._get_vreg_for_domain(domain)
            resist_sub_addr = self._domain_to_vout_num(domain) % 2
            print '\tSetting r_sense...'
            self._test_resistor(vreg.r_sense, resist_sub_addr, r_sense_init)
            print '\tSetting r_shunt...'
            self._test_resistor(vreg.r_shunt, resist_sub_addr, r_shunt_init)
            print '\tSetting r_set...'
            self._test_resistor(vreg.r_set, resist_sub_addr, r_set_init)

    def _test_voltage_sweep(self):
        r_sense_init = 100E3
        r_shunt_init = 40
        r_set_init   = 20E3 # 1V
        domain = 'VOUT0'
        #for r_set in np.arange(1, 20E3, 10):
        self._test_set_vout_domains(r_sense_init, r_shunt_init, r_set_init)
        for v in np.arange(0.1, 1, 0.001):
            self.set_voltage(domain, v)
            sleep(0.050)


    def _test_resistor(self, resistor, sub_addr, value):
        resistor.set_resistance(sub_addr, value, self.i2c)
        sw_value = resistor.get_resistance(sub_addr)
        hw_value = resistor.get_hw_resistance(sub_addr, self.i2c)
        print '\tSW value: {}, HW value: {}'.format(sw_value, hw_value)

    def _test_resistor_settings(self):
        for domain in ['VOUT0']:
            vreg = self._get_vreg_for_domain(domain)
            resist_sub_addr = self._domain_to_vout_num(domain) % 2
            print '\tr_sense'
            self._test_get_resistor(vreg.r_sense, resist_sub_addr)
            print '\tr_shunt:'
            self._test_get_resistor(vreg.r_shunt, resist_sub_addr)
            print '\tr_set:'
            self._test_get_resistor(vreg.r_set, resist_sub_addr)


    def _test_get_resistor(self, resistor, sub_addr):
        sw_value = resistor.get_resistance(sub_addr)
        hw_value = resistor.get_hw_resistance(sub_addr, self.i2c)
        print '\tSW value: {}, HW value: {}'.format(sw_value, hw_value)

    def _domain_to_vout_num(self, domain):
        if domain == 'VOUT_3V3':
            vout_num = 8
        else:
            vout_num = int(domain[-1]) # grab the number from the name
        return vout_num

    def _get_vreg_for_domain(self, domain):
        if domain == 'VOUT0' or domain == 'VOUT1':
            return self.super_vreg.vreg1
        elif domain == 'VOUT2' or domain == 'VOUT3':
            return self.super_vreg.vreg2
        elif domain == 'VOUT4' or domain == 'VOUT5':
            return self.super_vreg.vreg3
        elif domain == 'VOUT6' or domain == 'VOUT7':
            return self.super_vreg.vreg4
        else:
            raise RuntimeError('Bad domain given: {}'.format(domain))

    def set_voltage(self, domain, voltage):
        vout_num = self._domain_to_vout_num(domain)
        if vout_num == 8:
            print "Can't set vout for fixed domain"
        else:
            self.super_vreg.set_vout(self.i2c, vout_num, voltage)

    def get_voltage(self, domain):
        voltage = self.super_vreg.get_vout(self.i2c, self._domain_to_vout_num(domain))
        return voltage, 'volts'

    def get_current(self, domain):
        current = self.super_vreg.get_current(self.i2c, self._domain_to_vout_num(domain))
        return current, 'amps'

    def get_power(self, domain):
        voltage, v_unit = self.get_voltage(domain)
        current, i_unit = self.get_current(domain)
        return (voltage * current, v_unit, i_unit)

# Labjack I2C class used to interact with I2C on the labjack
class LabJackI2C(I2CInterface):

    def __init__(self, labjack, scl_pin, sda_pin, speed_adj, i2c_mux):
        self.lj = labjack
        self.scl_pin = scl_pin
        self.sda_pin = sda_pin
        self.speed_adj = speed_adj
        self.i2c_mux = i2c_mux
        self.lj.configDigital(scl_pin, sda_pin) # this should already be done, but just in case

    # Send bytes sequentially to a slave
    # - Bytes are written MSB first!
    def write(self, addr, send_bytes):
        # TODO try NoStopWhenRestarting=True
        if self.speed_adj is not None:
            self.lj.i2c(
                Address=addr, I2CBytes=send_bytes, SpeedAdjust=self.speed_adj,
                SDAPinNum=self.sda_pin, SCLPinNum=self.scl_pin
            )
        else:
            self.lj.i2c(
                Address=addr, I2CBytes=send_bytes,
                SDAPinNum=self.sda_pin, SCLPinNum=self.scl_pin
            )

    # Write (e.g. an address pointer) and read a response
    # - Bytes are received MSB first!
    def read(self, addr, send_bytes, num_bytes_2_rec):
        if self.speed_adj is not None:
            data_bytes = self.lj.i2c(
                Address=addr, I2CBytes=send_bytes, SpeedAdjust=self.speed_adj,
                SDAPinNum=self.sda_pin, SCLPinNum=self.scl_pin,
                NumI2CBytesToReceive=num_bytes_2_rec
            )
        else:
            data_bytes = self.lj.i2c(
                Address=addr, I2CBytes=send_bytes,
                SDAPinNum=self.sda_pin, SCLPinNum=self.scl_pin,
                NumI2CBytesToReceive=num_bytes_2_rec
            )
        return data_bytes

    # Set the i2c channel and write
    def write_channel(self, addr, send_bytes, chan):
        self.i2c_mux.set_channel(self, chan)
        self.write(addr, send_bytes)

    # Set the i2c channel and read
    def read_channel(self, addr, send_bytes, num_bytes_2_rec, chan):
        self.i2c_mux.set_channel(self, chan)
        return self.read(addr, send_bytes, num_bytes_2_rec)

# Class used to control all the voltage regulator channels
class SUPER_VREG(object):
    # TODO change 17, 19 back to 19, 17
    VSENSE_VOUT_ADDRS = [19, 17, 15, 13, 11, 9, 7, 5, 3] # VOUT addresses
    VSENSE_VMON_ADDRS = [18, 16, 14, 12, 10, 8, 6, 4, 2] # VMON addresses
    LT3089_CURRENT_COEF = 5000
    #ADDR_MASK = 0x7

    def __init__(self, addr_sel=0x0):
        # setup i2c mux
        self.i2c_mux = TCA9548A(addr_sel)
        self.address = self.i2c_mux.address
        # setup VREG's
        self.vreg1 = VREG(channel=1)
        self.vreg2 = VREG(channel=2)
        self.vreg3 = VREG(channel=3)
        self.vreg4 = VREG(channel=4)
        # setup vsense
        self.vsense = VSENSE(
            chan_adc_0_1=5, chan_adc_2_3=6, chan_adc_4_5=7
        )

    def set_vout(self, i2c, vout_num, level):
        sub_addr = vout_num % 2
        vreg = self._get_vreg_for_vout_num(vout_num)
        vreg.set_vout(sub_addr, level, i2c)

    def get_vout(self, i2c, vout_num):
        if (vout_num <= 8 and vout_num >= 0):
            return self.vsense.get_vout(SUPER_VREG.VSENSE_VOUT_ADDRS[vout_num], i2c)
        else:
            raise RuntimeError('VSENSE subaddress is invalid')

    def get_current(self, i2c, vout_num):
        if (vout_num <= 8 and vout_num >= 0):
            voltage = self.vsense.get_vout(SUPER_VREG.VSENSE_VMON_ADDRS[vout_num], i2c)
            resist = self.get_resistor_setting(vout_num, 'RSENSE')
            print voltage
            return voltage / resist * SUPER_VREG.LT3089_CURRENT_COEF
        else:
            raise RuntimeError('VSENSE subaddress is invalid')

    def set_all_resistors(self, resistor, val, i2c):
        if resistor == 'RSENSE':
            for vreg in [self.vreg1, self.vreg2, self.vreg3, self.vreg4]:
                vreg.r_sense.set_resistance(0x0, val, i2c)
                vreg.r_sense.set_resistance(0x1, val, i2c)
        elif resistor == 'RSET':
            for vreg in [self.vreg1, self.vreg2, self.vreg3, self.vreg4]:
                vreg.r_set.set_resistance(0x0, val, i2c)
                vreg.r_set.set_resistance(0x1, val, i2c)
        elif resistor == 'RSHUNT':
            for vreg in [self.vreg1, self.vreg2, self.vreg3, self.vreg4]:
                vreg.r_shunt.set_resistance(0x0, val, i2c)
                vreg.r_shunt.set_resistance(0x1, val, i2c)
        else:
            raise RuntimeError('Invalid resistor given: {}'.format(resistor))

    def get_resistor_setting(self, vout_num, resistor):
        sub_addr = vout_num % 2
        vreg = self._get_vreg_for_vout_num(vout_num)
        if resistor == 'RSENSE':
            return vreg.r_sense.get_resistance(sub_addr)
        elif resistor == 'RSET':
            return vreg.r_set.get_resistance(sub_addr)
        elif resistor == 'RSHUNT':
            return vreg.r_shunt.get_resistance(sub_addr)
        elif resistor == 'RSENSE_FIXED':
            return vreg.RSENSE_FIXED_VAL
        else:
            raise RuntimeError('Invalid resistor given: {}'.format(resistor))

    # Get the hw regulator for the vout_num
    def _get_vreg_for_vout_num(self, vout_num):
        if (vout_num < 0 or vout_num > 7):
            raise RuntimeError('Invalid vout_num: {}'.format(vout_num))
        if (vout_num == 0 or vout_num == 1):
            return self.vreg1
        elif (vout_num == 2 or vout_num == 3):
            return self.vreg2
        elif (vout_num == 4 or vout_num == 5):
            return self.vreg3
        elif (vout_num == 6 or vout_num == 7):
            return self.vreg4

# Class for the channel mux
class TCA9548A(object):
    ADDR_MASK = 0x7

    def __init__(self, addr_sel):
        self.address = 0x70 | (TCA9548A.ADDR_MASK & addr_sel)

    def set_channel(self, i2c, chan):
        i2c_frames = []
        i2c_frames.append(dec_to_1hot(chan)) # only 1 channel is open at a time
        i2c.write(self.address, i2c_frames)

    def _get_channel_setting(self, i2c):
        i2c_frames = []
        resp = i2c.read(self.address, i2c_frames, 1)
        return resp['I2CBytes'][0]

class VSENSE(object):
    CHAN_PER_ADC = 4

    def __init__(self, chan_adc_0_1, chan_adc_2_3, chan_adc_4_5):
        # init adc's
        self.adc0 = ADS1115(0x0, chan_adc_0_1)
        self.adc1 = ADS1115(0x1, chan_adc_0_1)
        self.adc2 = ADS1115(0x0, chan_adc_2_3)
        self.adc3 = ADS1115(0x1, chan_adc_2_3)
        self.adc4 = ADS1115(0x0, chan_adc_4_5)

    def get_vout(self, vsense_sub_addr, i2c):
        adc_sub_addr = vsense_sub_addr % VSENSE.CHAN_PER_ADC
        if (vsense_sub_addr >= 0 and vsense_sub_addr <= 3):
            return self.adc0.read_voltage(adc_sub_addr, i2c)
        if (vsense_sub_addr >= 4 and vsense_sub_addr <= 7):
            return self.adc1.read_voltage(adc_sub_addr, i2c)
        if (vsense_sub_addr >= 8 and vsense_sub_addr <= 11):
            return self.adc2.read_voltage(adc_sub_addr, i2c)
        if (vsense_sub_addr >= 12 and vsense_sub_addr <= 15):
            return self.adc3.read_voltage(adc_sub_addr, i2c)
        if (vsense_sub_addr >= 16 and vsense_sub_addr <= 19):
            return self.adc4.read_voltage(adc_sub_addr, i2c)
        else:
            raise RuntimeError('Invalid vsense subaddress: {}'.format(vsense_sub_addr))

    def set_gain(self, vsense_sub_addr, i2c):
        pass

    def get_gain(self, vsense_sub_addr, i2c):
        pass

# Class for the ADC
class ADS1115(object):
    ADDR_MASK = 0x1
    # Register pointer addresses
    CONVERSION_REG_ADDR = 0x0
    CONFIG_REG_ADDR = 0x1
    CONFIG_LO_TH_ADDR = 0x2
    CONFIG_HI_TH_ADDR = 0x3
    # sleep time to make sure we capture at least 1 sample on a newly selected channel
    CONVERSION_SLEEP = 0.050
    # ADC max code (for single ended reads)
    ADC_CODE_MAX = 2**15 - 1
    # ADC FS voltage
    ADC_FS_VOLTAGE = 4.096 * (2**15 - 1)/(2**15) # see datasheet

    def __init__(self, addr_sel, channel):
        self.address = 0x48 | (ADS1115.ADDR_MASK & addr_sel)
        self.channel = channel

    def read_voltage(self, adc_sub_addr, i2c):
        # TODO implement non-modifying writes to config reg

        # Select the ADC channel
        self._write_config_register(
            os=0,               # useless
            mux=4+adc_sub_addr, # see datasheet (single ended read on channel)
            pga=1,              # fullswing = +-4.096V
            mode=0,             # continuous conversion (default)
            dr=4,               # 128SPS (default)
            comp_mode=0,        # traditional comparator
            comp_pol=0,         # ALERT/RDY active low (default)
            comp_lat=0,         # non-latching comparitor (default)
            comp_que=3,         # disable comparator (default)
            i2c=i2c
        )
        # wait for conversion
        sleep(ADS1115.CONVERSION_SLEEP)

        # get the result..
        adc_code = self._read_conversion_register(i2c)
        sign = 1
        bin_adc_code = format(adc_code, '016b')
        if int(bin_adc_code[0]) == 1:
            adc_code = (adc_code ^ 0xFFFF) + 1
            sign = -1

        voltage = sign * ADS1115.ADC_FS_VOLTAGE * (float(adc_code) / ADS1115.ADC_CODE_MAX)
        return voltage

    def _read_conversion_register(self, i2c):
        i2c_frames = []
        i2c_frames.append(0xFF & ADS1115.CONVERSION_REG_ADDR) # pointer register
        resp = i2c.read_channel(self.address, i2c_frames, 2, self.channel)
        conversion_bytes = resp['I2CBytes']
        return ((conversion_bytes[0] << 8) | conversion_bytes[1])

    def _write_config_register(
        self, os, mux, pga, mode, dr, comp_mode, comp_pol, comp_lat, comp_que, i2c
    ):
        i2c_frames = []
        i2c_frames.append(0xFF & ADS1115.CONFIG_REG_ADDR) # pointer register
        config_frames = self._compile_config_reg_frames(
            os, mux, pga, mode, dr, comp_mode, comp_pol, comp_lat, comp_que)
        i2c_frames = i2c_frames + config_frames
        i2c.write_channel(self.address, i2c_frames, self.channel)

    def _read_config_register(self, i2c):
        i2c_frames = []
        i2c_frames.append(0xFF & ADS1115.CONFIG_REG_ADDR) # pointer register
        resp = i2c.read_channel(self.address, i2c_frames, 2, self.channel)
        return resp['I2CBytes']

    def _read_thresh_lo_register(self, i2c):
        i2c_frames = []
        i2c_frames.append(0xFF & ADS1115.CONFIG_LO_TH_ADDR) # pointer register
        resp = i2c.read_channel(self.address, i2c_frames, 2, self.channel)
        return (resp['I2CBytes'][1] << 8 | resp['I2CBytes'][0])

    def _compile_config_reg_frames(
        self, os, mux, pga, mode, dr, comp_mode, comp_pol, comp_lat, comp_que
    ):
        # upper byte
        frame_upper = 0x00
        frame_upper = set_bit(frame_upper, 7, os)
        frame_upper = set_bits(frame_upper, 6, 4, mux) # mux
        frame_upper = set_bits(frame_upper, 3, 1, pga)
        frame_upper = set_bit(frame_upper, 0, mode)
        # lower byte
        frame_lower = 0x00
        frame_lower = set_bits(frame_lower, 7, 5, dr)
        frame_lower = set_bit(frame_lower, 4, comp_mode)
        frame_lower = set_bit(frame_lower, 3, comp_pol)
        frame_lower = set_bit(frame_lower, 2, comp_lat)
        frame_lower = set_bits(frame_lower, 1, 0, comp_que)
        return [frame_upper, frame_lower]

# Class for each voltage regulator
class VREG(object):
    RSENSE_ADDR = 0x0
    RSET_ADDR = 0x1
    RSHUNT_ADDR = 0x2
    RSENSE_FIXED_VAL = 30E3
    LT3089_RSET_CURRENT = 50E-6

    def __init__(self, channel):
        # init resistors
        self.r_set = AD52XX(VREG.RSET_ADDR, '5263', channel)
        self.r_sense = AD52XX(VREG.RSENSE_ADDR, '5242', channel)
        self.r_shunt = AD52XX(VREG.RSHUNT_ADDR, '5248', channel)

    def set_vout(self, vreg_sub_addr, voltage, i2c):
        r_setting = voltage / VREG.LT3089_RSET_CURRENT
        self.r_set.set_resistance(vreg_sub_addr, r_setting, i2c)
        # set the shunt resistor to a safe value
        # 10ohms @ 0.3V, 1000ohms @ 1.0V
        r_shunt_new = get_new_r_shunt(voltage)
        self.r_shunt.set_resistance(vreg_sub_addr, r_shunt_new, i2c)

def get_new_r_shunt(voltage):
    if (voltage <= 0.3):
        r_shunt_new = 10
    elif (voltage <= 0.4):
        r_shunt_new = 20
    elif (voltage <= 0.5):
        r_shunt_new = 20
    elif (voltage <= 0.6):
        r_shunt_new = 30
    elif (voltage <= 0.7):
        r_shunt_new = 40
    elif (voltage <= 0.8):
        r_shunt_new = 50
    elif (voltage <= 0.8):
        r_shunt_new = 60
    elif (voltage <= 1.0):
        r_shunt_new = 75
    elif (voltage <= 1.2):
        r_shunt_new = 100
    else:
        raise RuntimeError("Voltage greater than 1.2V not supported")
    return r_shunt_new


class AD52XX(object):
    ADDR_MASK = 0x3
    VALID_PID = ['5242', '5248', '5263']
    CODE_MAX = 255
    # RSENSE hw params
    RSENSE_RMAX = 1E6
    # RSET hw params
    RSET_RMAX = 20E3
    # RSET hw params
    RSHUNT_RMAX = 2.5E3

    def __init__(self, addr_sel, pid, channel):
        # set address & channel
        self.channel = channel
        self.address = 0x2C | (AD52XX.ADDR_MASK & addr_sel)
        # set device
        if pid not in AD52XX.VALID_PID:
            raise RuntimeError('Invalid PID given for AD52XX')
        self.pid = pid
        # set rmax
        if pid == '5242':
            self.r_max = AD52XX.RSENSE_RMAX
        elif pid == '5248':
            self.r_max = AD52XX.RSHUNT_RMAX
        else: # 5263
            self.r_max = AD52XX.RSET_RMAX
        # code is uninitialized
        self.r_value = None

    def set_resistance(self, resist_sub_addr, r_setting, i2c):
        code = int(r_setting / self.r_max * AD52XX.CODE_MAX)
        if (code < 0 or code > AD52XX.CODE_MAX):
            raise RuntimeError('Invalid digipot code: {}'.format(code))
        self._set_wiper_code(code, resist_sub_addr, i2c)
        self.r_value = float(code) / AD52XX.CODE_MAX * self.r_max

    def get_resistance(self, resist_sub_addr):
        if self.r_value is None:
            raise RuntimeError('Resistors not initialized yet')
        else:
            return self.r_value

    def get_hw_resistance(self, resist_sub_addr, i2c):
        wiper_code = self._get_wiper_code(resist_sub_addr, i2c)
        return int(float(wiper_code) / AD52XX.CODE_MAX * self.r_max)

    def _set_wiper_code(self, code, rdac_sub_addr, i2c):
        i2c_frames = []
        i2c_frames.append(self._compile_inst_frame(rdac_sub_addr, 0, 0, 0, 0))
        i2c_frames.append(0xFF & code)
        i2c.write_channel(self.address, i2c_frames, self.channel)

    def _get_wiper_code(self, rdac_sub_addr, i2c):
        i2c_frames = []
        i2c_frames.append(self._compile_inst_frame(rdac_sub_addr, 0, 0, 0, 0))
        response = i2c.read_channel(self.address, i2c_frames, 1, self.channel)
        wiper_code = response['I2CBytes'][0]
        return wiper_code

    def _compile_inst_frame(self, rdac_sub_addr, midscale_rst, shutdown, logic_1, logic_2):
        inst = 0x00
        if self.pid == '5242' or self.pid == '5248':
            inst = set_bit(inst, 7, rdac_sub_addr)
            inst = set_bit(inst, 6, midscale_rst)
            inst = set_bit(inst, 5, shutdown)
            inst = set_bit(inst, 4, logic_1)
            inst = set_bit(inst, 3, logic_2)
            # bits 2,1,0 are dont cares
            return inst
        else: # 5263
            inst = set_bits(inst, 6, 5, rdac_sub_addr)
            inst = set_bit(inst, 4, midscale_rst)
            inst = set_bit(inst, 3, shutdown)
            inst = set_bit(inst, 2, logic_1)
            inst = set_bit(inst, 1, logic_2)
            # bits 7,0 are dont cares
            return inst


def dec_to_1hot(num):
    return 1 << (num - 1) # note that 0x1_dec equals 0x1_1hot

def hot_to_dec(num):
    if (num == 1):
        return 1
    elif num % 2 != 0:
        raise RuntimeError('Number not 1hot encoded')
    else:
        return int(math.log(num, 2)) + 1

def set_bit(num, index, value):
    return num | (value << index)

# Assumes an 8-bit number!
def set_bits(num, index_hi, index_lo, value):
    mask = (0xFF >> (8 - index_hi - 1)) & (0xFF << index_lo)
    return num | (mask & value << index_lo)



