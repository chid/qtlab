# File name: basic_measure_script.py

from numpy import pi, random, arange, size
from time import time,sleep

# Create instruments
# YOKO_1 = qt.instruments.create('YOKO_1','x_Yokogawa_7651',address='GPIB::4', reset=False)
# YOKO_2 = qt.instruments.create('YOKO_2','x_Yokogawa_7651',address='GPIB::3', reset=False)

YOKO_1.set_voltage(0)
YOKO_2.set_voltage(0)
