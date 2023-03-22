#!/usr/bin/python

# Description
#
# Convert a scanConfig file (Verilog format) to an intermediate format supported by
# the test_intf scan controller (as of August 2017)
# - Future patch for labjack/scan controller code

# Notes
#
# - Discards all lines from scanConfig except those that start with "input" or "output"
# - Isn't sensitive to spacing, but is sensitive to case
# - Will die if the scanConfig.txt file isn't formatted properly

import sys
import re

SCAN_CONFIG_FILE = 'scanConfig.txt'
SCAN_BITS_FILE = 'scan_bits.txt'

REGEX_BUS_SPEC = '\[ *[0-9]+ *: *[0-9]+ *\]'
BUS_PAT = re.compile(REGEX_BUS_SPEC)

def convert_file(config_file, bits_file):
   old_signal_list = []
   new_signal_list = []

   # Process input file (scanConfig)
   with open(config_file) as f:
      for line in f:
         if (is_valid_config_line(line)):
            new_sig = convert_signal(line)
            new_signal_list.append(new_sig)

   # Generate output file (scan_bits)
   with open(bits_file, 'w') as f:
      for sig in new_signal_list:
         sig_name, sig_bits = sig
         f.write('{} {}\n'.format(sig_name, sig_bits))


# Takes a valid line from a scanConfig file, returns a converted signal
# - Returned signal is a tuple of ("signal_name", "signal_bits")
def convert_signal(sig_string):
   # Remove the bracketed bus portion of the string if it's a bus
   # - Resulting string has the form "input/output <name> = <number>"
   if (is_bus_signal(sig_string)):
      sig_string = re.sub(BUS_PAT, '', sig_string)
   # Process name and the number
   toks = sig_string.split()
   sig_name = toks[1]
   sig_num = toks[3]
   new_sig_num = convert_number(sig_num)
   return (sig_name, new_sig_num)


# Convert a verilog number to flat binary string
# - Expects a string of format <length>'<type><number>, e.g., 8'd4
def convert_number(num_string):
   valid_types = ['b', 'h', 'd']
   toks = num_string.split("'") # split on apostrophe
   num_type = toks[1][0]
   # Process binary number
   if num_type == valid_types[0]:
      new_num = toks[1][1:] # strip off the type specifier (b, n, h)
   # Process hex number
   elif num_type == valid_types[1]:
      new_num = bin(int(toks[1][1:], 16))[2:] # convert to int and then binary, chop off "0b"
   elif num_type == valid_types[2]:
   # Process decimal number
      new_num = bin(int(toks[1][1:]))[2:] # convert to binary, chop off "0b"
   else:
      raise RuntimeError('Error on num_string: {}'.format(num_string))

   # Pad the binary string with zeros if needed
   full_length = int(toks[0])
   if (len(new_num) != full_length):
      pad_zeros = '0'*(full_length - len(new_num))
      new_num = pad_zeros + new_num
   return new_num


# Return true if the line should be processed as a signal
def is_valid_config_line(line):
   toks = line.split()
   if len(toks) == 0:
      return False
   elif (toks[0] == 'input' or toks[0] == 'output'):
      return True
   else:
      return False


# Return true if the signal is a bus
def is_bus_signal(line):
   result = BUS_PAT.search(line)
   if result is None:
      return False
   else:
      return True


if __name__ == '__main__':
   print('Convert scanConfig.txt to scan_bits.txt')
   convert_file('scanConfig.txt', 'scan_bits.txt')
   print('Done')
