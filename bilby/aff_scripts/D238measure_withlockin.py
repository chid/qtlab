# Filename: measure.py
#333 Joris Keizer <jgkeizer@gmail.com>
# Sep 2013

# Function: 1D/2D sweeps
#       1D: Sweep SOURCE_1
#           If SOURCE_2 enabled: set voltage
#           If SOURCE_2 not enabled: ignore SOURCE_2 entries, just sweep SOURCE_1
#       2D: Sweep SOURCE_1
#           Step  SOURCE_2

from numpy import pi, random, arange, size
from time import time,sleep
import sys

# Create instruments -assume is done
LOCKIN_1 = qt.instruments.create('LockIn1', 'x_SR830', address='GPIB::14', reset=False)
YOKO_1 = qt.instruments.create('Source1', 'x_Yokogawa_7651', address='GPIB::3', reset=False)
YOKO_2 = qt.instruments.create('Source2', 'x_Yokogawa_7651', address='GPIB::4', reset=False)
MULTIMETER = qt.instruments.create('Meter1', 'x_HP_34401A', address='GPIB::1', reset=False)
# Magnet1 = qt.instruments.create('Magnet1', 'x_AMI_420', address='GPIB::22', reset=False)
# TempCon1 = qt.instruments.create('TempCon1', 'x_Cryocon_32B', address='GPIB::12', reset=False)
#LockIn1 = qt.instruments.get('LockIn1')
#Source1 = qt.instruments.get('Source1')
#Meter1 = qt.instruments.get('Meter1')


# filename and data tags
filename='DEV238_dip3_GR_sw24'
trace_hold_time = 0.5

MULTIMETER_data_tag='I_SD [pA]'
LOCKIN_data_tag='Lock-in response [V]'

# IV convertor constant 
I_sens=-1e-8  # A/V  

# Current protection
I_max=9e-9    # A
enable_protection=True

# SOURCE_1 sweep # res
SOURCE_1_data_tag='V_res [V]'
V1_start =  -.3        
V1_end   =  0.3            
V1_step  =  0.0005          
def adjust_sw1_voltage(v):
    YOKO_2.set_voltage(v)

# SOURCE_2 sweep # Gdon
SOURCE_2_data_tag='V_Gdon [V]'
V2_start = 0.0       
V2_end   = 4.0       # has 1/5 divider in front of it
V2_step  = 0.025
def adjust_sw2_voltage(v):
    LOCKIN_1.set_out2(v)

#Static voltages
YOKO_1.set_voltage(0.001) #src bias
#YOKO_2.set_voltage(0.0) # res
LOCKIN_1.set_out1(0.000) # Gset
#LOCKIN_1.set_out2(0.000) # Gdon

# Instruments parameters
# SOURCE_1_driver='x_SR830'
# SOURCE_1_address=3 
# SOURCE_2_driver='x_Yokogawa_7651'
# SOURCE_2_address=4
SOURCE_2_enabled=True                     
MULTIMETER_driver='x_HP_34401A'
MULTIMETER_address=1

# SOURCE_1_range=1
# SOURCE_2_range=1
MULTIMETER.set_range(1) # in Volt
MULTIMETER.set_resolution(3e-4) #1e-6, 3e-6, 1e-5, 3e-5, 1e-4, 3e-4

  
#def adjust_sw2_voltage(v):
#    LOCKIN_1.set_out2(v)

#################################################################
# DON'T EDIT BELOW
#################################################################

   

# Function to generate the sweep arrays    
def generate_sweep(V1,V2,step):
    if (V2 >= 0 and V1 >= 0) or (V2 <= 0 and V1 <= 0):
        if V1 < V2:
            sweep = arange(V1,V2+step,abs(step))  
        else:
            sweep = arange(V1,V2-step,-abs(step))
    if V2 > 0 and V1 < 0:
        sweep = arange(V1,V2+step,abs(step))
    if V2 < 0 and V1 > 0:
        sweep = arange(V1,V2-step,-abs(step))
    if V1 == V2:
        sweep=[V1]
    return sweep
       
# Setup the sweep arrays
# print "--------------------------------------------------------" 
# if SOURCE_1.get_range() < abs(V1_start) or SOURCE_1.get_range() < abs(V1_end):
    # print "WARING: Sweep outside SOURCE_1 range settings"
sweep_1=generate_sweep(V1_start,V1_end,V1_step)
print "Sweep SOURCE_1 from " + str(V1_start) + "V to " + str(V1_end) + "V in " + str(V1_step) + "V steps";        
     
if (SOURCE_2_enabled==True):
    # if SOURCE_2.get_range() < abs(V2_start) or SOURCE_2.get_range() < abs(V2_end):
        # print "WARING: Sweep outside SOURCE_2 range settings"
    sweep_2=generate_sweep(V2_start,V2_end,V2_step)
    print "Step SOURCE_2 from " + str(V2_start) + "V to " + str(V2_end) + "V in " + str(V2_step) + "V steps";        
else:
    sweep_2=[0]
    
# Ask whether to continue
print "--------------------------------------------------------"
print "FILENAME: " + filename
print "--------------------------------------------------------"
key = raw_input('Continue [Y]/[n]? ')
if (key=='n') or (key=='N'):
    sys.exit('Exiting') 
 
# Setup the data file and plots
data = qt.Data(name=filename)    
data.add_coordinate(SOURCE_2_data_tag)
data.add_coordinate(SOURCE_1_data_tag)
data.add_value(MULTIMETER_data_tag)
data.add_value(LOCKIN_data_tag)
data.create_file()

plot_sweep = qt.Plot2D(data, name='Sweep', coorddim=1, valdim=2, maxtraces=4)
if (V2_start<>V2_end) and (SOURCE_2_enabled==True): 
    plot_map = qt.Plot3D(data, name='Map', coorddims=(0,1), valdim=2, style='image')
    
plot_sweep_lockin = qt.Plot2D(data, name='SweepLockin', coorddim=1, valdim=3, maxtraces=4)
if (V2_start<>V2_end) and (SOURCE_2_enabled==True): 
    plot_map_lockin = qt.Plot3D(data, name='MapLockin', coorddims=(0,1), valdim=3, style='image')
    
# Start the measurement
qt.mstart()
for V2 in sweep_2:
        if (SOURCE_2_enabled==True):
            adjust_sw2_voltage(V2)
        adjust_sw1_voltage(sweep_1[0])
        qt.msleep(trace_hold_time)
        for V1 in sweep_1: 
            adjust_sw1_voltage(V1)
            I_meas=MULTIMETER.get_readval()
            L_meas=LOCKIN_1.get_X()
            # If MULTIMETER goes into overload set the value to zero
            # This works for the HP multimeter, other multimeters may need another values
            if abs(I_meas)>1e20:
                print "Exiting..."
                break
                #I_meas=0;
            data.add_data_point(V2, V1, I_meas*I_sens/1e-12, L_meas)
            plot_sweep.update()
            plot_sweep_lockin.update()
            qt.msleep(0.001)
            if (I_meas*I_sens)>abs(I_max): 
                print "BREAKING: Max I reached"
                if enable_protection==True:
                    print "Exiting..."
                    break
        data.new_block()
        if (V2_start<>V2_end) and (SOURCE_2_enabled==True): 
            plot_map.update()
            plot_map_lockin.update()
qt.mend()

# Tidying up
# SOURCE_1.set_voltage(0)
# if SOURCE_2_enabled==True:
    # SOURCE_2.set_voltage(0)

# Save sweep and map as png-file
plot_sweep.save_png()
if (V2_start<>V2_end) and (SOURCE_2_enabled==True): 
    plot_map.save_png()

data.close_file()