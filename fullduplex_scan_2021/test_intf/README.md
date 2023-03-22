
Overview
--------------

This is a python package that implements software API's to hardware test equipment.
The main objective is to provide a unified and abstracted interface to test devices, including power supplies, oscilloscopes, and DAQs.

Dependencies
---------------
The following python packages are required:
   - visa (http://pyvisa.readthedocs.io/en/stable/getting.html)
   - usbtmc (https://github.com/python-ivi/python-usbtmc)
   - numpy

Supported interfaces and hardware devices
-------------------------------------------

Because underlying hardware may have very different capabilities, the requirements for the parent classes should be fairly loose (flexible).
Top-level abstract classes interfaces are prefixed with `TI_ABSTRACT_`, while hardware specific subclasses (implementations) are prefixed with `TI_HW_`.
Only `TI_HW_` interfaces are meant to be accessible directly by users.
Of course There may be other classes, e.g., "helper classes", users may or may not hack on them at their discretion.

### Classes ###

* `TI_ABSTRACT_VoltageRegulator`
* `TI_ABSTRACT_Oscilloscope`
* `TI_ABSTRACT_ScanController`
* `TI_ABSTRACT_GPIO`

### Subclasses ###

* ti_hw_keysight.py
	This subclass has the ability to control the keysight E36102A power supply.
	The keysight E36102A power supply is connected through USB.
* ti_hw_labjack_gpio.py
	This subclass controls the gpio on the labjack.
* ti_hw_MSO7104B_oscope.py
	This subclass controls the MSO7104B oscilloscope.
	The get_stats method returns a comma seperated list
	of all the measurements displayed on the oscilloscope.
	More commands for this oscilloscope can be found here.
	http://www.keysight.com/upload/cmc_upload/All/7000B_series_prog_guide.pdf
* ti_hw_prog_vr.py
	This subclass contains the programmable voltage regulator methods. The programmable voltage has 8 output voltage channels that could be controlled.
* ti_hw_scancontroller.py
	This subclass implements the scan controller.
	The user has the ability to pass in scanSequence.txt and scan Settings.txt files in the scan controller constructor.
	The scan controller accepts a both files.
	These text files contains the data for scan chain. ScanSequence contains the fixed order and scan Settings contains assignments in any order (ordere is preserved from Sequence)
	The first bit vector you want to scan in has to be at the top of the file. Each bit vector is ordered MSB to LSB from left to right.

### Hardware devices ###

* Labjack U3 (used in almost all the subclass implementations)
* Custom Programmable VR board (ProgVR)
* Keysight E36102A PSU
* MSO7104B Oscilloscope
* NI DAQ (TBD?)
* FPGA-based scan?

Utils
-------------------------------
The `utils` directory contains useful scripts or code snippets, which may or may not be integrated later.

Code guidelines and style
-------------------------------

We will follow Google's python style conventions: https://google.github.io/styleguide/pyguide.html

Exceptions:

* indenting and spacing - the number of spaces is not important, but *we absolutely must not mix spaces and tabs*. *Spaces only*.
* the class and subclass prefixes mentioned above

Documentation
-------------------

There will be no official documentation, except for this README.
This puts extra emphasis on writing clean, self-documenting code.
