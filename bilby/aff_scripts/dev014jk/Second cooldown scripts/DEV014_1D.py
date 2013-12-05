# Measurement script for experiments on tunnel gap charge sensor device DEV014JK
# November 2013
# Matthew House

from numpy import pi, random, arange, size
from time import time, sleep
from generate_sweep import generate_sweep
import sys
import qt

# initialize instruments
x = Dev014JK()

# Data filename 
filename='DEV014_testing'

# Voltage sweep
sweeping_yoko = YOKO_A
SWEEP_data_tag='V_A [V]'
V_start = 0
V_end   = 2        
V_step  = 0.01       
	
# time to wait after setting voltage before reading data (seconds)
pauseTime = 0.0
# time to wait after setting initial voltage (seconds)
initialPauseTime = 2

# names of data points
METER_A_data_tag  = 'I_A [nA]'
METER_B_data_tag  = 'I_B [nA]'
LOCKIN_data_tag_x = 'Lock-in response (real) [V]'
LOCKIN_data_tag_y = 'Lock-in response (imag) [V]'

# Gain of the current amplifiers
I_A_gain =  1  # nA/V  
I_B_gain = -1  # nA/V
# Maximum allowed current
current_limit = 10 # nA

# Set up the sweep arrays
sweep = generate_sweep(V_start, V_end, V_step)
print "Sweep " + SWEEP_data_tag + "from " + str(V_start) + "V to " + str(V_end) + "V in " + str(V_step) + "V steps";        
         
# Ask whether to continue
print "--------------------------------------------------------"
print "FILENAME: " + filename
print "--------------------------------------------------------"
key = raw_input('Continue [Y]/[n]? ')
if (key=='n') or (key=='N'):
    sys.exit('I am exiting because you told me to.') 
 
# Setup the data file and plots
data = qt.Data(name=filename)    
data.add_coordinate(SWEEP_data_tag)
data.add_value(METER_A_data_tag)
data.add_value(METER_B_data_tag)
data.add_value(LOCKIN_data_tag_x)
data.add_value(LOCKIN_data_tag_y)
data.create_file()

# Create the plots
plot_ADC = qt.Plot2D(data, name='Transport DC current', coorddim=0, valdim=1)
plot_BDC = qt.Plot2D(data, name='Gap DC current',       coorddim=0, valdim=2)
plot_lockin_x = qt.Plot2D(data, name='Gap AC (real)',   coorddim=0, valdim=3)
plot_lockin_y = qt.Plot2D(data, name='Gap AC (imag)',   coorddim=0, valdim=4)

# Start the measurement
print "Starting measurement..."
start_time = time()
qt.mstart()
sweeping_yoko.set_voltage(sweep[0])
qt.msleep(initialPauseTime)
for volts in sweep: 
	# set voltage
	sweeping_yoko.set_voltage(volts)
	qt.msleep(pauseTime)
	
	# read data from instruments
	I_A = I_A_gain * METER_A.get_readval()
	I_B = I_B_gain * METER_B.get_readval()
	L_x = LOCKIN_B.get_X()
	L_y = LOCKIN_B.get_Y()
	
	# add data to data set and update plots
	data.add_data_point(volts, I_A, I_B, L_x, L_y)
	plot_ADC.update()
	plot_BDC.update()
	plot_lockin_x.update()
	plot_lockin_y.update()
	
	if abs(I_A) > current_limit or abs(I_B) > current_limit:
		print "Current limit reached! Exiting..."
		break
	
qt.mend()
print "Measurement complete."
print "Time elapsed: " + str((time() - start_time)) + " seconds."

# Save plots as PNG image files
plot_ADC.save_png()
plot_BDC.save_png()
plot_lockin_x.save_png()
plot_lockin_y.save_png()

data.close_file()