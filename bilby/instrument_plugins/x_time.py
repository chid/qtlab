# Metatdata.py class, to store sample related metadata
# Sam Gorman <samuel.gorman@student.unsw.edu.au> 2013
# Sam Hile <samhile@gmail.com> 2013
# Charley Peng <cpeng92@gmail.com> 2013
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
import types
import logging
import time


class x_time(Instrument):
    '''
    This is the python driver for the time-instrument
    set_time(0) resets the time counter
    set_time(val>0) waits till time counter > val
    This driver can be use to 'sweep' time in any of the
    sweep programs. 

    Usage:
    Initialize with
    <name> = instruments.create('name', 'x_time')
    '''

    def __init__(self, name, reset=False, upperlim=10000, lowerlim=0):
        '''
        Initializes the metadata thingy.

        Input:
            name (string)    : name of the instance

        Output:
            None
        '''
        logging.info(__name__ + ' : Initializing meta')
        Instrument.__init__(self, name, tags=['virtual'])

        self.add_parameter('time', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET ,
            units = 's', tags = ['sweep'], minval=lowerlim, maxval=upperlim)   
            
        self.add_function('do_get_time')
        self.add_function('do_set_time')
        # reset ?
        self._starting_time = time.time()

        if reset:
            self.reset()
        else:
            self.get_all()
        self._dip = ''
        self._exp = ''
        self._notes = ''
        self._user = ''

    def get_all(self):
        '''
        Reads all implemented parameters that have been set,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info('reading all settings from x_time instrument')        

    def do_set_time(self, val):
        import time

        if val == 0:
            self.reset_time()
        else:
            while self.do_get_time() < val:
                time.sleep(0.001)

    def do_get_time(self):
        '''
        Returns the current time in this format
        %a, %d %b %Y %H:%M:%S
        '''
        return time.time() - self._starting_time

    def reset_time(self):
        self._starting_time = time.time()
           

