#!/usr/bin/env python

from test_intf.ti_hw_raspberry_gpio import RaspberryPi
from test_intf.ti_device import Device
''' List of supported hardware platforms
    RST, PHI, PHI_BAR, UPDATE, CAPTURE, SACN_IN, SCAN_OUT'''

RASPBERRY = Device(RaspberryPi, 14, 15, 18, 23, 24, 25, 8)
''' RASPBERRY PORT:
    GPIO14 -> BOARD_PIN: 8
    GPIO15 -> BOARD_PIN: 10
    GPIO18 -> BOARD_PIN: 12
    GPIO23 -> BOARD_PIN: 16
    GPIO24 -> BOARD_PIN: 18
    GPIO25 -> BOARD_PIN: 22
    GPIO8  -> BOARD_PIN: 24'''

