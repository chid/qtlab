# VTI Hall bar measurement
# Sam Hile  <samhile@gmail.com> 2013

# imports
from numpy import pi, random, arange, size
import qt
import time

# Create instruments -assume is done
LockIn1 = qt.instruments.create('LockIn1', 'x_SR830', address='GPIB::10', reset=False)
LockIn2 = qt.instruments.create('LockIn2', 'x_SR830', address='GPIB::4', reset=False)
LockIn3 = qt.instruments.create('LockIn3', 'x_SR830', address='GPIB::14', reset=False)
LockIn4 = qt.instruments.create('LockIn4', 'x_SR830', address='GPIB::6', reset=False)
LockIn5 = qt.instruments.create('LockIn5', 'x_SR830', address='GPIB::8', reset=False)
#Source1 = qt.instruments.create('Source1', 'x_Yokogawa_7651', address='GPIB::4', reset=False)
#Meter1 = qt.instruments.create('Meter1', 'x_Keithley_2001', address='GPIB::16', reset=False)# LockIn2 = qt.instruments.create('LockIn2', 'x_SR830', address='GPIB::4', reset=False)
# Magnet1 = qt.instruments.create('Magnet1', 'x_AMI_420', address='GPIB::22', reset=False)
# TempCon1 = qt.instruments.create('TempCon1', 'x_Cryocon_32B', address='GPIB::12', reset=False)
#LockIn1 = qt.instruments.get('LockIn1')
#Source1 = qt.instruments.get('Source1')
#Meter1 = qt.instruments.get('Meter1')
meta = qt.instruments.create('metadata', 'x_Metadata', reset=False)

#safety
# LockIn1.set_parameter_options('out1',maxval=2.00,minval=-2.00) #Gset
# LockIn1.set_parameter_options('out2',maxval=2.00,minval=-2.00) #Gdot
# LockIn1.set_parameter_options('out3',maxval=1.00,minval=-1.00) #Res
# Source1.set_parameter_options('voltage',maxval=2.00,minval=-2.00) #Src
# I_lim = 0.9 #nA

# Define static parameters
# v_Gset = 0.0 #V
# v_Gdot = 0.0 #V
# v_R = 0.0 #V
# v_S = 0.0 #V
# gain = 10e9 #Ohm


#the sweep set function
def setvolt(V):
    # Source1.set_voltage(V)
    qt.msleep(0.02)


# Define paremeter vectors
# enter start, end, and increment values: arange(start,end,increment))
V_swp = arange(0,1000.01,1) #in arb
sweepvar = 'tic [arb]'
measvar1 = 'V_xx [V]'
measvar2 = 'V_xy [V]'
measvar3 = 'V2_xx [V]'
measvar4 = 'V2_xy [V]'
measvar5 = 'I_bias [A]'
measvar6 = 'time [s]'
runname='1D_BX_rampup5_N5T'

# Setup to begin
# LockIn1.set_out1(v_Gset)
# LockIn1.set_out2(v_Gdot)
# Source1.set_voltage(v_S)
# LockIn1.set_out3(v_R)

# Make data object
# The file will be placed in the folder:
# <datadir>/<datestamp>/<timestamp>_testmeasurement/
# and will be called:
# <timestamp>_testmeasurement.dat
# to find out what 'datadir' is set to, type: qt.config.get('datadir')
data = qt.Data(name=runname)

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate(sweepvar)
data.add_coordinate(measvar6)
data.add_value(measvar1)
data.add_value(measvar2)
data.add_value(measvar3)
data.add_value(measvar4)
data.add_value(measvar5)



# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.

plot_1 = qt.Plot2D(data, name=(measvar1 + ' v ' + measvar6), coorddim=1, valdim=2, maxtraces=1)
plot_2 = qt.Plot2D(data, name=(measvar2 + ' v ' + measvar6), coorddim=1, valdim=3, maxtraces=1)
plot_3 = qt.Plot2D(data, name=(measvar3 + ' v ' + measvar6), coorddim=1, valdim=4, maxtraces=1)
plot_4 = qt.Plot2D(data, name=(measvar4 + ' v ' + measvar6), coorddim=1, valdim=5, maxtraces=1)
plot_5 = qt.Plot2D(data, name=(measvar5 + ' v ' + measvar6), coorddim=1, valdim=6, maxtraces=1)



# preparation is done, now start the measurement.
print 'measurement started'
qt.mstart()

# It is actually a simple loop.
t0 = time.time()
t = time.time() - t0
V = 0
#for V in V_swp:
while t < 3200:
    setvolt(V)
    # Pause to let the current meter settle
    qt.msleep(0.02)
    # readout
    xx = LockIn1.get_X()
    xy = LockIn2.get_X()
    xx2 = LockIn4.get_X()
    xy2 = LockIn5.get_X()
    I_drn = LockIn3.get_X()
    t = time.time() - t0
#    if ((I_drn > I_lim) or (I_drn < (-I_lim))): #current limiting
    # if 0:
        # print 'current limit warning!!'
        # data.add_data_point(V,xx, xy, I_drn,t)
        #plot_Isd.update()
        # break
    # save the data point to the file, this will automatically trigger
    # the plot windows to update
    data.add_data_point(V, t, xx, xy, xx2, xy2, I_drn)
    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    if divmod(V,10)[1] == 0:
        plot_1.update()
        plot_2.update()
        plot_3.update()
        plot_4.update()
        plot_5.update()
    V += 1
    
    

qt.mend()
# after the measurement ends, you need to close the data file.
data.close_file()
plot_1.save_png()
plot_2.save_png()
plot_3.save_png()
plot_4.save_png()
plot_5.save_png()



print 'measurement finished'


######################################

