# VTI Hall bar measurement
# Sam Hile  <samhile@gmail.com> 2013

# imports
from numpy import pi, random, arange, size

# Create instruments -assume is done
# LockIn1 = qt.instruments.create('LockIn1', 'x_SR830', address='GPIB::5', reset=False)
# LockIn2 = qt.instruments.create('LockIn2', 'x_SR830', address='GPIB::4', reset=False)
# Magnet1 = qt.instruments.create('Magnet1', 'x_AMI_420', address='GPIB::22', reset=False)
# TempCon1 = qt.instruments.create('TempCon1', 'x_Cryocon_32B', address='GPIB::12', reset=False)

# Define static parameters
v_Gset = 0.0 #V
v_Gdot = 0.0 #V
v_R = 0.0 #V
v_S = 0.0 #V
gain = 10e9 #Ohm


# Define paremeter vectors
# enter start, end, and increment values: arange(start,end,increment))
V_gdot = arange(0,2.000,0.005)

# Setup to begin
LockIn1.set_out1(v_Gset)
LockIn1.set_out2(v_Gdot)
Source1.set_voltage(v_S)
Source2.set_voltage(v_R)

# Make data object
# The file will be placed in the folder:
# <datadir>/<datestamp>/<timestamp>_testmeasurement/
# and will be called:
# <timestamp>_testmeasurement.dat
# to find out what 'datadir' is set to, type: qt.config.get('datadir')
data = qt.Data(name='1D_run')

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('V_gdot [V]')
data.add_value('V_amp [V]')
data.add_value('I_drn [nA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.

plot_Isd = qt.Plot2D(data, name='Isd (nA)', coorddim=0, valdim=2, maxtraces=1)


# preparation is done, now start the measurement.
print 'measurement started'
qt.mstart()

# It is actually a simple loop.

for V in V_gdot:
    Source2.set_voltage(V)
    # Pause to let the current meter settle
    qt.msleep(0.2)
    
    # readout
    V_drn = Meter1.get_readnextval()
    I_drn = V_drn / gain * 1e9 #for nA
    # save the data point to the file, this will automatically trigger
    # the plot windows to update
    data.add_data_point(V, V_drn, I_drn)
    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    plot_Isd.update()

qt.mend()
# after the measurement ends, you need to close the data file.
data.close_file()
plot_Isd.save_png()



print 'measurement finished'