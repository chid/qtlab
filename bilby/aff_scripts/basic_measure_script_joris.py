# File name: basic_measure_script.py

from numpy import pi, random, arange, size
from time import time,sleep

# Creation and setup of instuments moved to seperate file ("set_instruments.py")

I_sens=-1e-9          # Ampere / Volt  
I_max=10e-9            #A

# Setup sweep (first sweep, sd)
V_start=0         #V, YOKO_1
V_end=3.0            #V, YOKO_1
step_size=0.01         #V, YOKO_1  

# Setup map (second sweep, gate. NOTE: if you don't want to sweep this one use V_gate_start=V_gate_end)
V_gate_start=0.0        #V, YOKO_2
V_gate_end=0.0       #V, YOKO_2
step_size_gate=0.005  #V, YOKO_2 

# AGILENT
# range 100, resolution 1e-4, 1 point = 0.585 sec

# Setup the sweep arrays 
if YOKO_1.get_range() < abs(V_start) or YOKO_1.get_range() < abs(V_end):
    print "WARING: Sweep outside YOKO range settings"

if (V_end >= 0 and V_start >= 0) or (V_end <= 0 and V_start <= 0):
    if V_start < V_end:
        sweep = arange(V_start,V_end+step_size,abs(step_size))  
    else:
        sweep = arange(V_start,V_end-step_size,-abs(step_size))
if V_end > 0 and V_start < 0:
        sweep = arange(V_start,V_end+step_size,abs(step_size))
if V_end < 0 and V_start > 0:
        sweep = arange(V_start,V_end-step_size,-abs(step_size))

#if YOKO_2.get_range() < abs(V_gate_start) or YOKO_2.get_range() < abs(V_gate_end):
#    print "WARING: Map outside YOKO range settings"

if (V_gate_end >= 0 and V_gate_start >= 0) or (V_gate_end <= 0 and V_gate_start <= 0):
    if V_gate_start < V_gate_end:
        map = arange(V_gate_start,V_gate_end+step_size_gate,abs(step_size_gate))  
    else:
        map = arange(V_gate_start,V_gate_end-step_size_gate,-abs(step_size_gate))
if V_end > 0 and V_start < 0:
        map = arange(V_gate_start,V_gate_end+step_size_gate,abs(step_size_gate))
if V_end < 0 and V_start > 0:
        map = arange(V_gate_start,V_gate_end-step_size_gate,-abs(step_size_gate))
        
#print sweep
#print map        
        
# Setup the data file and plots
data = qt.Data(name='TB_04_13-17')    
data.add_coordinate('V_gate [V]')
data.add_coordinate('V_sd [V]')
data.add_value('I [pA]')
data.create_file()
plot_sweep = qt.Plot2D(data, name='Sweep', coorddim=1, valdim=2, maxtraces=4)
plot_map = qt.Plot3D(data, name='Map', coorddims=(0,1), valdim=2, style='image')

# Start the measurement
qt.mstart()

for V_b in map:
        #YOKO_2.set_voltage(V_b) 
        YOKO_1.set_voltage(sweep[0])
        qt.msleep(2.5)
        for V_a in sweep: 
            YOKO_1.set_voltage(V_a)
            I_meas=AGILENT.get_readval()
            data.add_data_point(V_b, V_a, I_meas*I_sens/1e-12)
            plot_sweep.update()
            qt.msleep(0.001)
            if (I_meas*I_sens)>abs(I_max): 
                print "BREAKING: Max I reached"
                #break
        data.new_block()
        plot_map.update()
qt.mend()

YOKO_1.set_voltage(0)
#YOKO_2.set_voltage(0)

plot_sweep.save_png()
plot_map.save_png()

data.close_file()