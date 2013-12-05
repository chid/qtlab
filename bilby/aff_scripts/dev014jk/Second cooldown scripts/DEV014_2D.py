# Measurement script for experiments on tunnel gap charge sensor device DEV014JK
# November 2013
# Matthew House

from numpy import pi, random, arange, size
from time import time, sleep
from generate_sweep import generate_sweep
import sys
import qt

YOKO_SA  = qt.instruments.create('YokoSA',  'x_Yokogawa_7651', address='GPIB::5',  reset=False)
YOKO_SB  = qt.instruments.create('YokoSB',  'x_Yokogawa_7651', address='GPIB::8',  reset=False)
YOKO_A   = qt.instruments.create('YokoA',   'x_Yokogawa_7651', address='GPIB::2',  reset=False)
YOKO_B   = qt.instruments.create('YokoB',   'x_Yokogawa_7651', address='GPIB::6',  reset=False)
METER_A  = qt.instruments.create('MeterA',  'x_HP_34401A',     address='GPIB::14', reset=False)
METER_B  = qt.instruments.create('MeterB',  'x_HP_34401A',     address='GPIB::9',  reset=False)
LOCKIN_B = qt.instruments.create('LockInB', 'SR830',           address='GPIB::13', reset=False)

# Data filename 
filename='DEV014_data_080'

# Voltage sweep 1 - fast changing variable
sweeping_yoko_1 = YOKO_A
SWEEP_1_data_tag = 'V_A [V]'
V1_start = 1
V1_end   = 3    
V1_step  = .01  

# Voltage sweep 2 - slow changing variable
sweeping_yoko_2 = YOKO_B
SWEEP_2_data_tag = 'V_B [V]'
V2_start = 2 
V2_end   = 3  
V2_step  = 0.04      

# time to wait after setting fast voltage
pauseTime = 0
# wait after setting initial voltages
initialPauseTime = 10

# names of data channels
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
sweep1 = generate_sweep(V1_start, V1_end, V1_step)
sweep2 = generate_sweep(V2_start, V2_end, V2_step)

print "Sweep " + SWEEP_1_data_tag + "from " + str(V1_start) + "V to " + str(V1_end) + "V in " + str(V1_step) + "V steps";        
print "Sweep " + SWEEP_2_data_tag + "from " + str(V2_start) + "V to " + str(V2_end) + "V in " + str(V2_step) + "V steps";        

# Ask whether to continue
print "--------------------------------------------------------"
print "FILENAME: " + filename
print "--------------------------------------------------------"
key = raw_input('Continue [Y]/[n]? ')
if (key=='n') or (key=='N'):
    sys.exit('I am exiting because you told me to.') 
 
# Set up the data file 
data = qt.Data(name=filename)    
data.add_coordinate(SWEEP_1_data_tag)
data.add_coordinate(SWEEP_2_data_tag)
data.add_value(METER_A_data_tag)
data.add_value(METER_B_data_tag)
data.add_value(LOCKIN_data_tag_x)
data.add_value(LOCKIN_data_tag_y)
data.create_file()

# Create the plots
plot_ADC = qt.Plot2D(data, name='Transport DC current', coorddim=0, valdim=2)
plot_BDC = qt.Plot2D(data, name='Gap DC current', coorddim=0, valdim=3)
plot_lockin_x = qt.Plot2D(data, name='Gap AC (real)', coorddim=0, valdim=4)
plot_lockin_y = qt.Plot2D(data, name='Gap AC (imag)', coorddim=0, valdim=5)

plot_map_ADC = qt.Plot3D(data, name='Transport DC current map', coorddims=(0,1), valdim=2, style='image')
plot_map_BDC = qt.Plot3D(data, name='Gap DC current map', coorddims=(0,1), valdim=3, style='image')
plot_map_lockin_x = qt.Plot3D(data, name='Gap AC current map (real)', coorddims=(0,1), valdim=4, style='image')
plot_map_lockin_y = qt.Plot3D(data, name='Gap AC current map (imag)', coorddims=(0,1), valdim=5, style='image')

# Start the measurement
print "Starting measurement..."
qt.mstart()
sweeping_yoko_1.set_voltage(sweep1[0])
sweeping_yoko_2.set_voltage(sweep2[0])
qt.msleep(initialPauseTime)

for V2 in sweep2 :
	sweeping_yoko_2.set_voltage(V2)
	#sweeping_yoko_1.set_voltage(sweep1[0])
	qt.msleep(pauseTime)
	
	for V1 in sweep1: 
		# set voltage
		sweeping_yoko_1.set_voltage(V1)
		qt.msleep(pauseTime)
		
		# read data from instruments
		I_A = I_A_gain * METER_A.get_readval()
		I_B = I_B_gain * METER_B.get_readval()
		L_x = LOCKIN_B.get_X()
		L_y = LOCKIN_B.get_Y()
		
		# add data to data set and update plots
		data.add_data_point(V1, V2, I_A, I_B, L_x, L_y)
		plot_ADC.update()
		plot_BDC.update()
		plot_lockin_x.update()
		plot_lockin_y.update()
		
		if abs(I_A) > current_limit or abs(I_B) > current_limit:
			print "Current limit reached! Exiting..."
			break
			
	data.new_block()
	plot_map_ADC.update()
	plot_map_BDC.update()
	plot_map_lockin_x.update()
	plot_map_lockin_y.update()
	
qt.mend()
print "Measurement complete."

# Save plots as PNG files
plot_ADC.save_png()
plot_BDC.save_png()
plot_lockin_x.save_png()
plot_lockin_y.save_png()
plot_map_ADC.save_png()
plot_map_BDC.save_png()
plot_map_lockin_x.save_png()
plot_map_lockin_y.save_png()

data.close_file()