
import re
from itertools import product
import argparse

parser = argparse.ArgumentParser(description='read index and find the combination')
parser.add_argument('-index', default= 0, type=int)
args = parser.parse_args()

fileinit="regular_scan_settings_test_init.txt"
filescan="regular_scan_settings_test_1108.txt"

#signals = ["STG51_Q_REV" , "STG51_I_REV" , "STG41_Q_REV" , "STG41_I_REV" , "STG31_Q_REV" , "STG31_I_REV" , "STG21_Q_REV" , "STG21_I_REV" , "STG11_Q_REV" , "STG11_I_REV"]
#signals = ["STG11_I_REV" , "STG11_Q_REV"  , "STG12_I_REV" , "STG12_Q_REV" ]
#signals = ["STG11_I_REV" , "STG11_Q_REV" , "STG21_I_REV" , "STG21_Q_REV" ,  "STG31_I_REV" , "STG31_Q_REV"]
#signals = ["STG11_I_REV" , "STG11_Q_REV"]

signals = ["STG12_Q_REV" , "STG12_I_REV"  ,  "STG21_Q_REV" , "STG21_I_REV" , "STG11_Q_REV" , "STG11_I_REV"]
#signals = ["STG22_Q_REV" , "STG22_I_REV"  ,  "STG32_Q_REV" , "STG32_I_REV" , "STG31_Q_REV" , "STG31_I_REV"]

#signals = ["STG12_Q_REV" , "STG12_I_REV" , "STG22_I_REV" , "STG22_Q_REV" , "STG32_I_REV" , "STG32_Q_REV"]

#signals = ["STG51_Q_REV" , "STG51_I_REV" , "STG41_Q_REV" , "STG41_I_REV" , "STG31_Q_REV" , "STG31_I_REV" , "STG21_Q_REV" , "STG21_I_REV" , "STG11_Q_REV" , "STG11_I_REV" , "STG52_Q_REV" , "STG52_I_REV" , "STG42_Q_REV" , "STG42_I_REV" , "STG32_Q_REV" , "STG32_I_REV" , "STG22_Q_REV" , "STG22_I_REV" , "STG12_Q_REV" , "STG12_I_REV" ]

sweep_values = [0, 2, 3, 255]
comb = product(sweep_values, repeat=len(signals))
comb = list(comb)

new_lines = []
lsb_value = 0
lines = []
new_lines = []
new_value_list = []
with open(fileinit, "r") as f1:
    lines = f1.readlines()
for line in lines:
    for j in range(len(signals)):
        if line.find(signals[j]) != -1:
            search = re.search(r"8\'d(\d+)$", line)
            init_value = search.group(1)           
            new_value=(comb[args.index][j] + int(init_value)) 
            new_value_string = "8\'d" + str(new_value)
            line = re.sub(r"8\'d\d+$", new_value_string, line)
            print (line)
    new_lines.append(line)

with open(filescan, "w") as f2:
    for line in new_lines:
        f2.write(line)


