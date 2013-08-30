# Hall bar measurement (both sides of Hall bar)
# Sam Hile      <samhile@gmail.com>     2013
# Joris Keizer  <jgkeizer@gmail.com>    2013

# imports
from numpy import pi, random, arange, size

################################
# Create instruments 
################################

#LockIn1, SD, all other LockIns are syncs to this one, ground drain
LockIn1 = qt.instruments.create('LockIn1', 'x_SR830', address='GPIB::1', reset=False) #xx_a
#LockIn2 = qt.instruments.create('LockIn2', 'x_SR830', address='GPIB::2', reset=False) # broken at the moment
LockIn3 = qt.instruments.create('LockIn3', 'x_SR830', address='GPIB::3', reset=False) #xx_b
LockIn4 = qt.instruments.create('LockIn4', 'x_SR830', address='GPIB::4', reset=False) #xy_a
LockIn5 = qt.instruments.create('LockIn5', 'x_SR830', address='GPIB::5', reset=False) #xy_b

Meta = qt.instruments.create('Meta', 'x_Metadata')

################################
# Define static parameters
################################

I_meas = 199.9e-9 #A (currently I is not recorded, LockIn2 broken)
#v_drive = 0.204 #V 
#f_drive = 17 #Hz

# Define B-sweep parameters (The script sweeps the magnet-field from 0T to B_max and backdown to 0T).
B_max=1.5
step_size=0.005

# Create the sweep array, don't edit
sweep_up = arange(0,B_max,step_size)
sweep_down = arange(B_max,-step_size,-step_size)
B_field = concatenate((sweep_up,sweep_down))
#B_field = arange(1.3,-step_size,-step_size)

################################
# Setup instruments
################################

#LockIn1.set_amplitude(v_drive)
#LockIn1.set_amplitdue(f_drive)
Magnet1.set_field_setpoint(B_field[0])
Magnet1.ramp()

qt.mstart()
while(Magnet1.get_state()!=2): #2=holding at setpoint
    qt.msleep(1)
qt.mend()

################################
# Create data object and file
################################

# Make data object
# The file will be placed in the folder:
# <datadir>/<datestamp>/<timestamp>_testmeasurement/
# and will be called:
# <timestamp>_testmeasurement.dat
# to find out what 'datadir' is set to, type: qt.config.get('datadir')
data = qt.Data(name='DL014JK_real_199_2nA_HB1')

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('B [T]')
data.add_value('V_xx_a [V]')
data.add_value('V_xy_a [V]')
data.add_value('V_xx_a Q [V]')
data.add_value('V_xy_a Q [V]')
data.add_value('V_xx_b [V]')
data.add_value('V_xy_b [V]')
data.add_value('V_xx_b Q [V]')
data.add_value('V_xy_b Q [V]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.

plot_xx_a = qt.Plot2D(data, name='V_xx_a', coorddim=0, valdim=1, maxtraces=1)
plot_xx_b = qt.Plot2D(data, name='V_xx_b', coorddim=0, valdim=5, maxtraces=1)
plot_xy_a = qt.Plot2D(data, name='V_xy_a', coorddim=0, valdim=2, maxtraces=1)
plot_xy_b = qt.Plot2D(data, name='V_xy_b', coorddim=0, valdim=6, maxtraces=1)

################################
# Start the measurement
################################

print 'measurement started'
qt.mstart()

# get V_xx_(0)
Magnet1.set_field_setpoint(0)
V_xx_0_a= LockIn1.get_X()
V_xx_0_b= LockIn3.get_X()

# Sweep the field. It is actually a simple loop.
for B in B_field:
    Magnet1.set_field_setpoint(B)
    # Pause to let the current meter settle
    while(Magnet1.get_state()!=2):
       qt.msleep(1)
        
    # do the readout
    xx_a  = LockIn1.get_X()
    xxq_a = LockIn1.get_Y()
    xy_a  = LockIn4.get_X()
    xyq_a = LockIn4.get_Y()

    xx_b  = LockIn3.get_X()
    xxq_b = LockIn3.get_Y()
    xy_b  = LockIn5.get_X()
    xyq_b = LockIn5.get_Y()
           
    # save the data point to the file, this will automatically trigger
    # the plot windows to update
    
    # two sides of Hall bar 
    data.add_data_point(B, xx_a, xy_a, xxq_a, xyq_a, xx_b, xy_b, xxq_b, xyq_b)
  
    # one side of Hall bar
    #data.add_data_point(B, xx_a, xy_a, xxq_a, xyq_a)
    
    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    plot_xx_a.update()
    plot_xy_a.update()
    plot_xx_b.update()
    plot_xy_b.update()
    
qt.mend()

################################
# Tidying up 
################################

# after the measurement ends, you need to close the data file.
data.close_file()

# save the graphs as png-files
plot_xx_a.save_png()
plot_xy_a.save_png()
plot_xx_b.save_png()
plot_xy_b.save_png()

################################
# Some in situ analysis 
################################

# calculate Rxx(0), H_coef, ns
Rxx_0_a=abs(V_xx_0_a/I_meas) 
Rxx_0_b=abs(V_xx_0_b/I_meas)
Rxx_0=(Rxx_0_a+Rxx_0_b)/2
x=data.get_data()[:,0] # B
y=data.get_data()[:,2] # V
import numpy
fit_results=numpy.polyfit(x,y,1)
H_coef=abs(fit_results[0]) 
ns=abs(1/((H_coef/I_meas)*1.602e-19)/1e18)

print "-------------------------------------------"
print "R_xx(0) = " + str(Rxx_0) + " Ohms" 
print "H_coef  = " + str(H_coef) + " V T^-1"
print "ns      = " + str(ns) + " 10^14 cm^-2"
print "-------------------------------------------"
