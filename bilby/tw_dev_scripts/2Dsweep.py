# Arbitrary 2D Sweep
# Thomas Watson  <tfwatson15@gmail.com> 2013

# imports
from numpy import pi, random, arange, size

#This function modifies arrange so the end value is included
def range1(Vstart, Vend, Vstep):
        return arange(Vstart, Vend+Vstep, Vstep)

title = 'Stability 2D'  #title of experiment
Vnames = ['VG1', 'VG2', 'VG3', 'VG4'] #names of the parameters you are sweeping
xaxis = [1,0,1,0]       #parameters to sweep on x axis. The numbers correspond to a proportionality constant with respect to the xaxissweep values, ie. 1 will mean that gate will be sweep with the same values as xaxissweep 
xaxissweep = range1(-.5,.5,0.02)        #range to sweep on the x axis (Vstart, Vend, Vstep)        
yaxis = [0,1,0,1]       #parameters to sweep on x axis
yaxissweep = range1(-.5,.5,0.05)       #range to step on the y axis (Vstart, Vend, Vstep) 
const = [0,0,0,0]       #these are the starting values of each of the parameters

#This is where you set the values of the sweep parameters. V is of the same format as Vnames. 
def set_parameters(V):
        print ''
	#LockIn1.set_out1(V[0]) #VG1
	#LockIn1.set_out2(V[1]) #VG2
	#LockIn1.set_out3(V[2]) #VG3
	#LockIn1.set_out4(V[3]) #VG4

#This is where you get the values for the current from the meter instrument you are using.  	
def get_current():
        y = HP1.get_readval()
        return y


#This function finds the values of the sweep parameters given a specific x and y value. 	
def find_V(x, y):
	for  q in range(0, len(xaxis)): 
		V[q] = x* xaxis[q] + y* yaxis[q] + const[q]
	return V

#This function gets the labels for the x and y axis.
def get_axislabel(axis):
	axislabel = ''
	for  q in range(0, len(axis)):
		if axis[q] !=0:
			axislabel = axislabel + str(axis[q]) + Vnames[q] + '+'
	axislabel = axislabel[0:(len(axislabel)-1)]
        return axislabel



# Make data object
# The file will be placed in the folder:
# <datadir>/<datestamp>/<timestamp>_testmeasurement/
# and will be called:
# <timestamp>_testmeasurement.dat
# to find out what 'datadir' is set to, type: qt.config.get('datadir')
data = qt.Data(name=title)
V = [0,0,0,0]
# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate(get_axislabel(xaxis))
data.add_coordinate(get_axislabel(yaxis))
data.add_value('I_drn [nA]')
for q in range(0, len(Vnames)):
        data.add_coordinate(Vnames[q])
# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.

plot_Isd = qt.Plot2D(data, name='Isd (nA)', coorddim=0, valdim=2, maxtraces=10)
plot2D_Isd = qt.Plot3D(data, name='Stability Isd (nA)', coorddims=(0,1), valdim=2, style='image')
plot2D_Isd.set_xrange(xaxissweep.min(), xaxissweep.max())
plot2D_Isd.set_yrange(yaxissweep.min(), yaxissweep.max())

# preparation is done, now start the measurement.
print 'measurement started'
qt.mstart()

# It is actually a simple loop.
for y in yaxissweep:
        for x in xaxissweep:
                V = find_V(x,y)
                set_parameters(V)
                #V_drn = Meter1.get_readnextval()    
		#I_drn = V_drn / gain * 1e9 #for nA	
		qt.msleep(0.001)
		I_drn = get_current()
		# save the data point to the file, this will automatically trigger
		# the plot windows to update
		data.add_data_point(x, y, I_drn, *V)
		# the next function is necessary to keep the gui responsive. It
		# checks for instance if the 'stop' button is pushed. It also checks
		# if the plots need updating.
        #plot_Isd.update()	
	data.new_block()

qt.mend()
# after the measurement ends, you need to close the data file.
data.close_file()
plot2D_Isd.save_png()


		


	


