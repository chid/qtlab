import qt
from numpy import pi, random, arange, size, zeros, linspace, floor
import numpy
import os
import os.path
import channels
import time
import sys
from lib.config import get_config
config = get_config()

class sweep(object):
    '''
    class for doing sweeps 

    Usage:
    Initialise with
    <name> = sweep.sweep(out channels, in channels,
                        loops = 'number of loops')
                        
    where the out and in channels come from the channels class
    and are put in to a list i.e out channels - [VG1, VG2],
    in channels - [I1]

    In addition you need to add the following to begin measurement:
    
    set_loops(list, loop number) - this defines the start, end, and
    stepsize for each axis. list is of the form [start, end, stepsize].
    The loop number corresponds to the axis i.e loop number = 0 is the
    xaxis, 1 is the yaxis, 2 is the zaxis etc.
    
    set_channel_constants(list) - this determines the starting values
    of all the out channels. list is a list the same size as the number
    of out channels, i.e. [0,0].
    
    set_channel_factors(list, loop number) - these are the prefactors
    associated with each out channel for each sweep axis. The loop
    number corresponds to the axis.
    
    From these three things you can determine how to sweep each channel.
    example: loops = 2 (this is a 2D stability diagram, sweeping on the
    xaxis and steping on the y)
    out channels = [VG1, VG2, VG3]
    in channels = [I1]
    set_channel_factors([1,.5,0],0) - this means the the xaxis
    corresponds to VG1 + 0.5* VG2
    set_channel_factors([0,0,1],1) - this means the yaxis corresponds to
    VG3
    set_channel_constants([0,0.5,0])-this means that there is a 0.5 V
    offset on VG2
    set_loops([0, 1, 0.1],0) - this means we sweep the xaxis
    from 0 to 1 with 0.1 steps 
    set_loops([-1, 1, 0.1],1) - this means we sweep the yaxis
    from -1 to 1 with 0.1 steps

    An additional option is to form a trapezium type sweep
    add_final_coord(list, loop) -   this sets the set_loops
    sweep to be the starting sweep, and the list input defines
    the ending sweep. Example using the above,
    add_final_coord([0,2],1), with this at the beginning
    of the 2D sweep, it will sweep from -1,1. At the end of
    the 2D sweep, it will sweep from 0,2.
    
            
    TODO
    Implement proper use of loop functions
    Bug check
    Allow user to determines the plots
    Update comments, rename stuff to make more understandable
    '''
    
    def __init__(self,name, channelsout, channelsin, updatepointbypoint = False,  loops = '1'):
        '''
        Initialises the sweep

        Input:
            channelsout (list of out channel instances) : out channels
            channelsin (list of in channel instances) : in channels
            updatepointbypoint(do you want the plot to update at each point?)
            loops (int) : number of loops
        '''
        self._updatepoints = updatepointbypoint
        self._name = name
        self._time = time.localtime()
        self._initialised = False
        self._check_ready = False
        self._added_final_coord = []
        self._number_of_loops = []
        self._channels_out = []
        self._number_of_out_channels = []
        self._channels_in = []
        self._number_of_in_channels = []
        self.set_number_of_loops(loops)
        self.set_channels_out(channelsout)
        self.set_channels_in(channelsin)
        self._initialised = True
        self._reset()
        
    def _check_ready1(self):
        '''checks to see if the necessary variables have been set to be able to start the sweeps'''
        self._check_ready = True
        if self._number_of_loops == [] or self._channels_out == [] or  self._channels_in == []:
            self._check_ready = False
        for i in range(0, len(self._channel_constants)):
            if self._channel_constants[i] == []:
                self._check_ready = False
        if sum(sum(abs(self._channel_factors)))  == 0:
            self._check_ready = False
        for i in range(0, len(self._loops)):
            for j in range(0, len(self._loops[0])):
                if  self._loops[i][j] == []:
                    self._check_ready = False

    def _check_if_out_of_range(self):
        pass

    def _reset(self):
        '''resets the variables that need to be changed if something like the number of loops changes'''
        print 'resetting channel constants, channel factors etc'
        self._channel_constants = [0 for row in range(self._number_of_out_channels)]       #starting values in the channel
        self._channel_factors = numpy.zeros((self._number_of_loops, self._number_of_out_channels))
        self._function = [[] for row in range(self._number_of_loops)]       #what do you want to run after you have steped?
        self._loops = [[0 for col in range(3)] for row in range(self._number_of_loops)]
        self._coord_current = [[] for row in range(self._number_of_loops)]
        self._sweep = [[] for row in range(self._number_of_loops)]
        self._final_coord = [[] for row in range(self._number_of_loops -1)]

    def add_final_coord(self, vec, loop):
        if loop == self._number_of_loops - 1:
            print 'Can not add final coordinates to the last loop'
        if loop != len(vec) - 1:
            print 'input [finalstart, finalend] is not the right size for the loop number'  
        else:
            self._added_final_coord.append(loop)
            self._final_coord[loop] = vec   

    def set_number_of_loops(self, val):
        '''Sets the number of loops for the sweep'''
        if self._number_of_loops != val:
            try:
                self._number_of_loops = int(val)
            except ValueError:
                self._number_of_loops = 1
            if self._number_of_loops < 1:
                print 'invalid number of loops'
                self._number_of_loops = 1
            if self._initialised == True:
                self._reset()

    def get_number_of_loops(self):
        '''Gets the number of loops in the sweep'''
        return self._number_of_loops
    
    def get_channels_out(self):
        '''Gets the out channels that will be sweeped'''
        return self._channels_out

    def set_channels_out(self, inst):
        '''Set the out channels that will be sweeped'''
        if self._channels_out != inst: 
            if checkoutchannels(inst) == False:
                print 'Invalid out channels'
                self._channels_out = []          
            else:
                self._channels_out = inst
            if self._initialised == True:
                self._reset()
            self._number_of_out_channels = len(self._channels_out)

    def get_channels_in(self):
        '''Gets the in channels that will be measured at each point of the sweep'''
        return self._channels_in

    def set_channels_in(self, inst):
        '''Sets the in channels that will be measured at each point of the sweep'''
        if self._channels_in != inst:
            if checkinchannels(inst) == False:
                print 'Invalid in channels'
                self._channels_in = []
            else:
                self._channels_in = inst
            if self._initialised == True:
                self._reset()
            self._number_of_in_channels = len(self._channels_in)

    def get_channel_factors(self):
        '''Gets the out channel factors'''
        return self._channel_factors

    def set_channel_factors(self, vec, loop):
        '''Sets the out channel factors'''
        if loop > (self._number_of_loops -1) or loop <0:
            print 'invalid loop number'
        elif is_floatable(vec) == False:
            print 'Illegal: invalid inputs'
        elif len(vec) != self._number_of_out_channels:
            print 'Illegal: number of elements in list must be the same as the number of channels'
        else:
            self._channel_factors[loop, :] = vec

    def get_channel_constants(self):
        '''Gets the out channel constants'''
        return self._channel_constants

    def set_channel_constants(self, vec):
        '''Sets the out channel constants'''
        if is_floatable(vec) == False:
            print 'Illegal: invalid inputs'
        elif len(vec) != self._number_of_out_channels:
            print 'Illegal: number of elements in list must be the same as the number of channels'
        else:        
            self._channel_constants = vec    

    def get_loops(self):
        '''Gets the loops that detemine how each axis is swept'''
        return self._loops

    def set_loops(self, val, loop):
        '''Sets the loops that detemine how each axis is swept'''
        if loop > (self._number_of_loops -1) or loop <0:
            print 'invalid loop number'
        elif is_floatable(val) == False:
            print 'Illegal: invalid inputs'
        elif len(val) != 3:
            print 'Illegal: loop should be a list of 3 values [start, end, stepsize]'
        elif val[2] <= 0:
            print 'Illegal: stepsize must be positive and non zero' 
        else:
            self._loops[loop] = val
    
    def set_function(self, func, loop):
        '''This hasnt been implemented but the idea is you can run a function everytime the loop starts'''
        self._function[loop] = func

    def run_function(self, loop):
        val = self._function [loop]()
        return val

    def get_axislabel(self, loop):
        '''From the channels and the channel factors this determined the label for each of the axis/loop'''
        axislabel = ''
        for q in range(0, self._number_of_out_channels):
            if self._channel_factors[loop][q] != 0:
                axislabel = axislabel + str(self._channel_factors[loop][q]) + self._channels_out[q].get_name()+ '(' + self._channels_out[q].get_units() + ')' + '+'
        axislabel = axislabel[0:(len(axislabel)-1)]
        return axislabel

    def get_filenamelabel(self, loop):
        '''From the channels and the channel factors this determined the label for filename'''
        axislabel = ''
        for q in range(0, self._number_of_out_channels):
            if self._channel_factors[loop][q] != 0:
                axislabel = axislabel + str(self._channel_factors[loop][q]) + self._channels_out[q].get_name()+ '_'
        axislabel = axislabel[0:(len(axislabel)-1)]
        return axislabel

    def run(self):
        '''This is how you begin the sweep. Checks if everything is setup then runs the measuremulti function'''
        self._check_ready1()
        if self._check_ready == True:
            print 'Starting measurement'
            self._time = time.localtime()
            qt.mstart()
            self._measuremulti(self._number_of_loops -1)
            qt.mend()
            print 'End of measurement'
        else:
            print 'Something is not set up properly. Check channels, channel factors, channel constants and loops.'           
            
    def _measure1d(self):
        '''This runs the 1D sweep (the xaxis loop). To do this need to calculate the voltage/field
        to set with the channels. After they are set the in channels are measured'''
  
        V = [[] for row in range(self._number_of_out_channels)]
        Out = [[] for row in range(self._number_of_out_channels)]
        In = [[]  for row in range(self._number_of_in_channels)]
        for x in self._sweep[0]:
            self._coord_current[0] = x
            for  q in range(0, self._number_of_out_channels):
                V[q] = dotproduct(self._coord_current[:], self._channel_factors[:, q]) + self._channel_constants[q]
                self._channels_out[q].set_out(V[q])
                Out[q] = self._channels_out[q].get_out()
            qt.msleep(0.001)
            for  q in range(0, self._number_of_in_channels):
                In[q] = self._channels_in[q].get_in()
                if In[q] > self._channels_in[q].get_max() and self._channels_in[q].get_max()>0:
                    print 'Aborting current above max'
                    qt.mend()
                    sys.exit()
            datapoints = self._coord_current + In + Out
            self._data.add_data_point(*datapoints)           
            if self._updatepoints == True:
                self._update_plots()                
        
    def _add_coordinates(self):
        '''This adds the appropriate coordinates and values to the data class (i.e.
        these are the coloumnsthat will be save to file)'''
        for q in range(0, self._number_of_loops):
            self._data.add_coordinate(self.get_axislabel(q))
        for q in range(0, self._number_of_in_channels):    
            self._data.add_value(self._channels_in[q].get_name()+ '(' + self._channels_in[q].get_units() + ')' )
        for q in range(0, self._number_of_out_channels):
            self._data.add_coordinate(self._channels_out[q].get_name() + '(' + self._channels_out[q].get_units() + ')' )

    def _add_plots(self):
        '''This adds plots which is determined by the number of loops and the number of in channels'''
        self._plots = [[] for row in range(self._number_of_loops)]       
        if self._number_of_loops == 1:
            self._plots = [[]]
            self._plots[0] = qt.Plot2D(self._data, name=self._channels_in[0].get_name(), coorddim=0, valdim=(self._number_of_loops), maxtraces=10)
            self._plots[0].set_plottitle(self._get_path().replace('\\','/'))
        if self._number_of_loops > 1:
            self._plots = [[] for row in range(1 + self._number_of_in_channels)]
            self._plots[0] = qt.Plot2D(self._data, name=self._channels_in[0].get_name(), coorddim=0, valdim=(self._number_of_loops), maxtraces=10)
            self._plots[0].set_plottitle(self._get_path().replace('\\','/'))
            for q in range(0, self._number_of_in_channels):
                self._plots[q+1] = qt.Plot3D(self._data, name='Stability ' + self._channels_in[q].get_name(), coorddims=(0,1), valdim=self._number_of_loops +q, style='image')
                self._plots[q+1].set_plottitle(self._get_path().replace('\\','/'))
                
    def _update_plots(self):
        '''This updates the plots.'''
        for q  in range(0, len(self._plots)):
            self._plots[q].update()

    def _save_plots(self):
        '''This save the plots as a png in the current folder'''
        for q  in range(0, len(self._plots)):
            self._plots[q].save_png()

    def _get_sweep(self, loop):
        ''' This gets the sweep list for a given loop. If there are no final coordinates relevent to this loop then things are easy.
            However if there are, things get complicated and we have to work out the sweep list which depends on the current coordinates'''
        self._startadds = 0
        self._endadds = 0
        if self._added_final_coord == []:
           self._sweep[loop] = arangemod(self._loops[loop][0], self._loops[loop][1], self._loops[loop][2])
        else:
            if loop == self._number_of_loops -1:
                self._sweep[loop] = arangemod(self._loops[loop][0], self._loops[loop][1], self._loops[loop][2])
            else:
                for q in self._added_final_coord:
                    if q >= loop:
                        self._startadds = self._startadds + self._add(0,loop,q)
                        self._endadds = self._endadds + self._add(1,loop,q)
                    
                self._sweep[loop] = arangemod(self._loops[loop][0] + self._startadds, self._loops[loop][1]+ self._endadds, self._loops[loop][2])


    def _add(self,i, loop, loopmax):
        ''''''
        add = (self._final_coord[loopmax][loop][i] - self._loops[loop][i]) * (self._coord_current[loopmax + 1] -self._sweep[loopmax + 1][0])/(self._sweep[loopmax+1][-1]  - self._sweep[loopmax+1][0])
        return add
    
        
    def _get_path(self):
        '''gets the pathname for saving the data'''
        path = config['datadir']
        path = os.path.join(path, time.strftime('%Y%m%d', self._time))
        path = os.path.join(path, time.strftime('%H%M%S', self._time) +'_'+ self._name)
        if self._number_of_loops == 1:
            path = os.path.join(path, '1D sweep' + self.get_filenamelabel(0) +'.dat')
        else:
            te = range(2, self._number_of_loops)
            te.reverse()
            if te !=[]:
                for i in te:
                    path = os.path.join(path, self.get_filenamelabel(i) +'_'+str(self._coord_current[i]))
            path = os.path.join(path, '2Dsweep_' + self.get_filenamelabel(1) +'_vs_' +self.get_axislabel(0) +'.dat')
        return path       
                            
    def _measuremulti(self, loop):
        '''This is the magic of the program which allow an infinite number of loops......'''
        self._get_sweep(loop)
        if self._number_of_loops > 1 and int(loop) == 1:
            self._data = qt.Data(name = '2Dsweep_' + self.get_axislabel(1) +'_vs_' +self.get_axislabel(0) )
            self._add_coordinates()
            self._add_plots()
            self._data.create_file(filepath = self._get_path())
        if self._number_of_loops == 1:
            self._data = qt.Data(name = '1D sweep' + self.get_axislabel(0))
            self._add_coordinates()
            self._add_plots()
            self._data.create_file(filepath  = self._get_path())                    
        if loop > 0:
            for y in self._sweep[loop]:
                self._coord_current[loop] = y
                self._measuremulti(loop-1)
                if y == self._sweep[loop][-1] and loop == 1:
                    self._data.close_file()
                    self._save_plots()
        else:
            self._measure1d()
            self._update_plots()
            self._data.new_block()
            if self._number_of_loops == 1:
                self._save_plots()
                          
def checkoutchannels(chan):
    '''This makes sure the out channels you put in are the right instance.'''
    try:
        t = True
        for i in range(0, len(chan)):
            if isinstance(chan[i], channels.channels_out) == False:
                t = False
        return t
    except NameError:
        return False
    
def checkinchannels(chan):
    '''This makes sure the in channels you put in are the right instance.'''
    try:
        t = True
        for i in range(0, len(chan)):
            if isinstance(chan[i], channels.channels_in) == False:
                t = False
        return t
    except NameError:
        return False

def arangemod(start, end, step):
    '''Simple function to allow you sweep from a more positive value to a more negative value. Also arrage cuts of the end value so I add it back.'''
    seq = linspace(start, end, 1 + round(abs(start - end)/step))
    return seq

def dotproduct(a, b):
    '''Function to do the dot product of two lists.'''
    ans = 0
    for q in range(0, len(a)):
        ans =  ans + a[q]*b[q]
    return ans

def is_floatable(s):
    '''This checks if you input a list of numbers not strings.'''
    try:
        [float(i) for i in s]
        return True
    except ValueError:
        return False
            
        
        
        
         
    
