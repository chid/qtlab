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

# filename and data tags
filename='DEV238_dip3_4K_Gset_sweep_6'
SOURCE_1_data_tag='V_gate [V]' 
SOURCE_2_data_tag='V_sd [V]' 
MULTIMETER_data_tag='I [pA]'

# IV convertor constant 
I_sens=-1e-9  # A/V  

# Current protection
I_max=1e-9    # A
enable_protection=True

# SOURCE_1 sweep
V1_start=0.00        
V1_end=1.0            
V1_step=0.005          

# SOURCE_2 sweep
V2_start=0.001       
V2_end=0.001       
V2_step=0.05 

# Instruments parameters
SOURCE_1_driver='x_Yokogawa_7651'
SOURCE_1_address=3 
SOURCE_2_driver='x_Yokogawa_7651'
SOURCE_2_address=4
SOURCE_2_enabled=True                     
MULTIMETER_driver='x_HP_34401A'
MULTIMETER_address=1

SOURCE_1_range=1
SOURCE_2_range=1
MULTIMETER_range=1
MULTIMETER_resolution=3e-6


#################################################################
# DON'T EDIT BELOW
#################################################################


# Function to check whether an instrument is initialized
def check_instruments(str):
    instruments=qt.instruments.get_instrument_names()
    flag=False
    for i in range(size(instruments)):
        if instruments[i]==str:
            flag=True
    return(flag)

# Initialize SOURCE_1    
print "--------------------------------------------------------"
if check_instruments('SOURCE_1')==False:
    print "SOURCE_1 not initialized."
    print "Trying to initialize SOURCE_1..."
    SOURCE_1=qt.instruments.create('SOURCE_1',SOURCE_1_driver,address='GPIB::'+str(SOURCE_1_address), reset=False)
    if check_instruments('SOURCE_1')==False:
        print "Could not initialize SOURCE_1, exiting..."
        sys.exit()
    else:
        print "SOURCE_1 initialized."
        SOURCE_1.set_range(SOURCE_1_range)
        print "Range: " + str(SOURCE_1.get_range()) + "V"
else:
    print "SOURCE_1 initialized."
    SOURCE_1.set_range(SOURCE_1_range)
    print "Range: " + str(SOURCE_1.get_range()) + "V"

# Initialize SOURCE_2    
print "--------------------------------------------------------"
if check_instruments('SOURCE_2')==False:
    if SOURCE_2_enabled==True:
        print "SOURCE_2 not initialized."
        print "Trying to initialize SOURCE_2..."
        SOURCE_2=qt.instruments.create('SOURCE_2',SOURCE_2_driver,address='GPIB::'+str(SOURCE_2_address), reset=False)
        if check_instruments('SOURCE_2')==False:
            print "Could not initialize SOURCE_2, exiting..."
            sys.exit()
        print "SOURCE_2 initialized."
        SOURCE_2.set_range(SOURCE_2_range)
        print "Range: " + str(SOURCE_2.get_range()) + "V"
    else:
        print "SOURCE_2 not enabled."
else:
    if check_instruments('SOURCE_2')==True:
        print "SOURCE_2 initialized."
        SOURCE_2.set_range(SOURCE_2_range)
        print "Range: " + str(SOURCE_2.get_range()) + "V"
    else:
        print "SOURCE_2 initialized but not enabled."

# Initialize MULTIMETER        
print "--------------------------------------------------------"
if check_instruments('MULTIMETER')==False:
    print "MULTIMETER not initialized."
    print "Trying to initialize MULTIMETER..."
    MULTIMETER=qt.instruments.create('MULTIMETER',MULTIMETER_driver,address='GPIB::'+str(MULTIMETER_address), reset=False)
    if check_instruments('MULTIMETER')==False:
        print "Could not initialize MULTIMETER, exiting..."
        sys.exit() 
    else:
        print "MULTIMETER initialized"
        print "Range: " + str(MULTIMETER.get_range())
        print "Resolution: " + str(MULTIMETER.get_resolution())
else:
    print "MULTIMETER initialized"
    MULTIMETER.set_range(MULTIMETER_range)
    MULTIMETER.set_resolution(MULTIMETER_resolution)
    print "Range: " + str(MULTIMETER.get_range())
    print "Resolution: " + str(MULTIMETER.get_resolution())

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
print "--------------------------------------------------------" 
if SOURCE_1.get_range() < abs(V1_start) or SOURCE_1.get_range() < abs(V1_end):
    print "WARING: Sweep outside SOURCE_1 range settings"
sweep_1=generate_sweep(V1_start,V1_end,V1_step)
print "Sweep SOURCE_1 from " + str(V1_start) + "V to " + str(V1_end) + "V in " + str(V1_step) + "V steps";        
     
if (SOURCE_2_enabled==True):
    if SOURCE_2.get_range() < abs(V2_start) or SOURCE_2.get_range() < abs(V2_end):
        print "WARING: Sweep outside SOURCE_2 range settings"
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
data.create_file()

plot_sweep = qt.Plot2D(data, name='Sweep', coorddim=1, valdim=2, maxtraces=4)
if (V2_start<>V2_end) and (SOURCE_2_enabled==True): 
    plot_map = qt.Plot3D(data, name='Map', coorddims=(0,1), valdim=2, style='image')
    
# Start the measurement
qt.mstart()
for V2 in sweep_2:
        if (SOURCE_2_enabled==True):
            SOURCE_2.set_voltage(V2)
        SOURCE_1.set_voltage(sweep_1[0])
        qt.msleep(2.5)
        for V1 in sweep_1: 
            SOURCE_1.set_voltage(V1)
            I_meas=MULTIMETER.get_readval()
            # If MULTIMETER goes into overload set the value to zero
            # This works for the HP multimeter, other multimeters may need another values
            if abs(I_meas)>1e20:
                I_meas=0;
            data.add_data_point(V2, V1, I_meas*I_sens/1e-12)
            plot_sweep.update()
            qt.msleep(0.001)
            if (I_meas*I_sens)>abs(I_max): 
                print "BREAKING: Max I reached"
                if enable_protection==True:
                    print "Exiting..."
                    break
        data.new_block()
        #plot_map.update()
qt.mend()

# Tidying up
SOURCE_1.set_voltage(0)
if SOURCE_2_enabled==True:
    SOURCE_2.set_voltage(0)

# Save sweep and map as png-file
plot_sweep.save_png()
#if (V2_start<>V2_end) and (SOURCE_2_enabled==True): 
    #plot_map.save_png()

data.close_file()