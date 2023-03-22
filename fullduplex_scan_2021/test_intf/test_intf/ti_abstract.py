#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

# General API for Voltage Regulator
class TI_ABSTRACT_VoltageRegulator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def set_voltage(self, domain, voltage): pass

    @abstractmethod
    def get_voltage(self, domain): pass

    @abstractmethod
    def get_current(self, domain): pass

# General API for Oscilloscope
class TI_ABSTRACT_Oscilloscope(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self): pass

# General API for Scan Controller
class TI_ABSTRACT_ScanController(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def scan_in(self): pass

    @abstractmethod 
    def scan_out(self): pass

# General API for GPIO
class TI_ABSTRACT_GPIO(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self): pass

    @abstractmethod
    def get_total_dio(self): pass

    @abstractmethod
    def set_dio(self, dio_n, state): pass

    @abstractmethod
    def get_dio(self, dio_n): pass
