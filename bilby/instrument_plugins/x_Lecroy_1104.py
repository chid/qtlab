# Lecroy_1104.py class, to perform the communication between the Wrapper and the device
# By Sam Hile <samhile@gmail.com>, 2013
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
from time import time, sleep
import visa
import types
import logging
import re
import win32com.client


class x_Lecroy_1104(Instrument):
    '''
    This is the python driver for the Lecroy ArbStudio 1104 AWG.

    Usage:
    Initialize with
    <name> = instruments.create('name', 'x_Lecroy_1104')
   
    '''
    
    def __init__(self, name, reset=True):
        '''
        Initializes the Lecroy ArbStudio 1104 AWG.

        Input:
            name (string)    : name of the instrument

        Output:
            None
        '''
        logging.debug(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        
        # Define set-only parameters for the configuration of the power supply.
        # Although these can be set remotely (in engineering mode), this driver 
        # assumes you would only want to set them locally and doesn't allow you 
        # to set them remotely.
        self.add_parameter('active',    type=types.IntType, channels=(1,2,3,4), flags=Instrument.FLAG_SET | Instrument.FLAG_GET, format_map = {
            0 : "Off",
            1 : "On"})
        self.add_parameter('steps',       type=types.IntType, channels=(1,2,3,4), flags= Instrument.FLAG_GET)
        self.add_parameter('levels',       type=types.ListType, channels=(1,2,3,4), flags=Instrument.FLAG_GET)
        self.add_parameter('lengths',       type=types.ListType, channels=(1,2,3,4), flags=Instrument.FLAG_GET)
        self.add_parameter('trigger', type=types.IntType, flags=Instrument.FLAG_SET | Instrument.FLAG_GET, format_map = {
            0 : "Continuous",
            1 : "External trigger"})
        self.add_parameter('ramp', type=types.IntType, flags=Instrument.FLAG_SET | Instrument.FLAG_GET)
        
        self.add_function('reset')
        self.add_function('run')
        self.add_function('clear')
        #self.add_function('add_step')
        
        #internals
        self._mathandle = win32com.client.Dispatch('matlab.application')
        
        if reset:
            self.reset()
            self.clear()
    # Functions
    def clear(self):
        '''
        Clears the step lists and settings in the wrapper. Does not reset instrument outputs (use reset() for that)

        Input:
            none

        Output:
            none
        '''
        logging.info(__name__ + ' : Clearing all settings and step values')
        
        self._active = [0, 0, 0, 0]
        self._steps = [0, 0, 0, 0]
        self._levels = []
        self._lengths = []
        self._trigger = 0
        self._ramp = 0
        for i in range(4):
            self._levels.append([])
            self._lengths.append([])

    
    def reset(self):
        '''
        Initialises the AWG, setting all outputs to zero. Does not clear values from the wrapper (use clear() for that) 

        Input:
            none

        Output:
            none
        '''
        logging.info(__name__ + ' : Resetting ArbStudio device')

        #uses .m file which should be in the MATLAB path
        self._mathandle.Execute("addpath('d:/ArbStudioLib');")
        self._mathandle.Execute("dev = InitARB;")

    
    def run(self):
        '''
        Uploads the waveform defined in the instrument wrapper to the ArbStudio and runs the output.
        Ensure it has been reset (with a .reset() call) before calling this 
        
        Input:
            None
            
        Output:
            none.
        '''
        
        ##build a big string to send to matlab
        ch_str = '[ '
        wv_str = '[ '
        for i in range(1,5):
            if self.get('active%d' % i) == 1:
                ch_str += '%d ' % i
                
                lev_str = '[ '
                len_str = '[ '
                for l in range(0,self.get('steps%d' % i)):
                    lev_str += '%e ' % self.get('levels%i' % i)[l]
                    len_str += '%e ' % self.get('lengths%i' % i)[l]
                lev_str += ']'
                len_str += ']'
                
                wv_str += "struct('levels',"
                wv_str += lev_str
                wv_str += " ,'lengths',"
                wv_str += len_str
                wv_str += ") "
                
        ch_str += ']'
        wv_str += ']'
        
        rp_str = '%d' % self.get_ramp()
        
        tr_str = '%d' % self.get_trigger()
        
        #print "MATLAB -->\nDonorPulses(dev,"+ch_str+","+wv_str+","+rp_str+","+tr_str+")"#
        
        #uses .m file which should be in the MATLAB path
        warn = self._mathandle.Execute("DonorPulses(dev,"+ch_str+","+wv_str+","+rp_str+","+tr_str+")")
        
        if warn:
            logging.warning(__name__ + " " + warn)
    
    def add_step(self, channel, level, length):
        '''
        Add a pulse step to a channel.
        
        Input:
            channel (int) : the channel to use
            level (float) : the set voltage in V
            length (float): the duration of the step in ms
            
        Output:
            none.
        '''
        
        self._levels[channel-1].append(level)
        self._lengths[channel-1].append(length)
        self._steps[channel-1] += 1

        
    def do_get_levels(self, channel):
        '''
        Returns the levels list for a channel.
        
        Input:
            channel (int) : 1-4
            
        Output:
            List of levels (string): in Volts
        '''
        
        return self._levels[channel-1]
    

    def do_get_lengths(self, channel):
        '''
        Returns the lengths list for a channel.
        
        Input:
            channel (int) : 1-4
            
        Output:
            List of lengths (string): in ms
        '''
        
        return self._lengths[channel-1]
    

    def do_get_trigger(self):
        '''
        Returns the trigger setting (off/on).
        
        Input:
            none
            
        Output:
            trigger status (int): 0=off, 1=on
        '''
        
        return self._trigger
    

    def do_get_ramp(self):
        '''
        Returns the ramp length (in points). The real length depends on the effective bandwidth.
        
        Input:
            none
            
        Output:
            ramp length (int): number of AWG points to ramp through
        '''
        
        return self._ramp
    

    def do_get_active(self, channel):
        '''
        Returns the active status for a channel.
        
        Input:
            channel (int) : 1-4
            
        Output:
            Channel status (int): 0=off 1=on
        '''
        
        return self._active[channel-1]
    
    
    def do_set_trigger(self, trigger):
        '''
        Set the trigger setting (off/on).
        
        Input:
            trigger status (int): 0=off, 1=on
            
        Output:
            none
        '''
        
        self._trigger = trigger
    

    def do_set_ramp(self, ramp):
        '''
        Sets the ramp length (in points). The real length depends on the effective bandwidth.
        
        Input:
            ramp length (int): number of AWG points to ramp through
            
        Output:
            none
        '''
        
        self._ramp = ramp
    

    def do_set_active(self, status, channel):
        '''
        Returns the active status for a channel.
        
        Input:
            channel (int) : 1-4
            
        Output:
            Channel status (int): 0=off 1=on
        '''
        
        self._active[channel-1] = status
    
    def do_get_steps(self, channel):
        '''
        Returns the number of steps in a channel.
        
        Input:
            channel (int) : 1-4
            
        Output:
            number of steps (int): 
        '''
        
        return self._steps[channel-1]
    

