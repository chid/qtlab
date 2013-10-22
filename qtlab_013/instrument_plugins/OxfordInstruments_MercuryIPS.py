# OxfordInstruments_MercuryIPS.py class, to perform the communication between the Wrapper and the device
# By Matthew House <matthew.house@unsw.edu.au>, 2013
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

class OxfordInstruments_MercuryIPS(Instrument):
    '''
    This is the python driver for the Oxford Instruments Mercury iPS Magnet Power Supply.

    Usage:
    Initialize with
    <name> = instruments.create('name', 'OxfordInstruments_MercuryIPS', address='<Instrument address>')
   
    '''
    
    def __init__(self, name, address, reset=False):
        '''
        Initializes the Oxford Instruments Mercury iPS Magnet Power Supply.

        Input:
            name (string)    : name of the instrument
            address (string) : instrument address

        Output:
            None
        '''
        logging.debug(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        # Set up VISA communications variables
        self._address = address
        self._values = {}
        self._visainstrument = visa.Instrument(self._address)
        #self._visainstrument.stop_bits = 1
        
        # Define read-only parameters for the configuration of the power supply.
        # Although these can be set remotely (in engineering mode), this driver 
        # assumes you would only want to set them locally and doesn't allow you 
        # to set them remotely.
        self.add_parameter('hardware_version',    type=types.StringType, flags=Instrument.FLAG_GET)
        self.add_parameter('firmware_version',    type=types.StringType, flags=Instrument.FLAG_GET)
        self.add_parameter('serial_number',       type=types.StringType, flags=Instrument.FLAG_GET)
        self.add_parameter('current_limit',       type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('current_field_ratio', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('magnet_inductance',   type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('switch_present',      type=types.BooleanType, flags=Instrument.FLAG_GET)
        self.add_parameter('switch_current',      type=types.FloatType, flags=Instrument.FLAG_GET)
        
        # Define read-only parameters for the status of the power supply
        self.add_parameter('voltage', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('current', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('current_ramp_rate', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('field', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('field_ramp_rate', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('persistent_current', type=types.FloatType, flags=Instrument.FLAG_GET)
        self.add_parameter('persistent_field', type=types.FloatType, flags=Instrument.FLAG_GET)
        
        # Define parameters for the settings of the power supply
        self.add_parameter('action_status', type=types.IntType, flags=Instrument.FLAG_GETSET,
            format_map = {
            0 : "Hold",
            1 : "Ramp to setpoint",
            2 : "Ramp to zero", 
            3 : "Clamp"})
        self.add_parameter('current_setpoint', type=types.FloatType, flags=Instrument.FLAG_GETSET)
        self.add_parameter('field_setpoint', type=types.FloatType, flags=Instrument.FLAG_GETSET)
        self.add_parameter('current_ramp_rate_setpoint', type=types.FloatType, flags=Instrument.FLAG_GETSET)
        self.add_parameter('field_ramp_rate_setpoint', type=types.FloatType, flags=Instrument.FLAG_GETSET)
        self.add_parameter('switch_status', type=types.BooleanType, flags=Instrument.FLAG_GETSET)
        
    # Functions
    def send_command(self, message):
        '''
        Sends a SCPI command to the power supply. See the manual for a list of valid commands.

        Input:
            message (str) : SCPI command to execute.

        Output:
            (str) : The response to the command from the power supply.
        '''
        logging.info(__name__ + ' : Send the following command to the device: %s' % message)
        
        #self._visainstrument.write(message)
        #self._visainstrument.write('@%s%s' % (2, message))
        #sleep(0.020)
        #result = self._visainstrument.read()
        result = self._visainstrument.ask(message)
        
        logging.info('Response: %s' % result)
        return result
    
    def do_get_hardware_version(self):
        '''
        Queries the power supply and returns the hardware version number.
        
        Input:
            None
            
        Output:
            Hardware version number of the power supply (string).
        '''
        
        response = self.send_command('READ:SYS:MAN:HVER')
        return response.split('STAT:SYS:MAN:HVER:')[1]
    
    def do_get_firmware_version(self):
        '''
        Queries the power supply and returns the firmware version number.
        
        Input:
            None
            
        Output:
            Firmware version number of the power supply (string).
        '''
        
        response = self.send_command('READ:SYS:MAN:FVER')
        return response.split('STAT:SYS:MAN:FVER:')[1]
        
    def do_get_serial_number(self):
        '''
        Queries the power supply and returns the serial number.
        
        Input:
            None
            
        Output:
            Hardware serial number of the power supply (string).
        '''
        
        response = self.send_command('READ:SYS:MAN:SERL')
        return response.split('STAT:SYS:MAN:SERL:')[1]
    
    def do_get_current_limit(self):
        '''
        Queries the power supply and returns the current limit setting.
        
        Input:
            None
            
        Output:
            Maximum allowed current setting, in Amps.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:CLIM')
        return float(response.split('STAT:DEV:GRPZ:PSU:CLIM:')[1].split('A')[0])
    
    def do_get_current_field_ratio(self):
        '''
        Queries the power supply and returns its setting for the ratio of 
        current to field (in Amps / Tesla).
        
        Input:
            None
            
        Output:
            Value of the current-to-field ratio setting, in Amps / Tesla.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:ATOB')
        return float(response.split('STAT:DEV:GRPZ:PSU:ATOB:')[1])
    
    def do_get_magnet_inductance(self):
        '''
        Queries the power supply and returns the inductance of the magnet.
        
        Input:
            None
            
        Output:
            Value of the magnet inductance in Henries.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:IND')
        return float(response.split('STAT:DEV:GRPZ:PSU:IND:')[1].split('H')[0])
    
    def do_get_switch_present(self):
        '''
        Queries the power supply and returns True if it is configured with a
        persistent mode switch.
        
        Input:
            None
            
        Output:
            True if the system is configured for a persistent mode switch, False
            if it is not.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SWPR')
        if response.split('STAT:DEV:GRPZ:PSU:SWPR:')[1] == 'None':
            returnval = False
        else:
            returnval = True
            
        return returnval
    
    def do_get_switch_current(self):
        '''
        Queries the power supply and returns the setting for the persistent switch
        current, in milliamps.
        
        Input:
            None
            
        Output:
            Returns the value of the persistent mode switch current, in milliamps.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SHTC')
        return float(response.split('STAT:DEV:GRPZ:PSU:SHTC:')[1])
            
    def do_get_voltage(self):
        '''
        Retrieves the voltage applied to the magnet leads.
        
        Input:
            None
            
        Output:
            Value of the magnet voltage in Volts
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:VOLT')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:VOLT:')[1].split('V')[0])
        
    def do_get_current(self):
        '''
        Retrieves the current applied to the magnet.
        
        Input:
            None
            
        Output:
            Value of the magnet current in Amps
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:CURR')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:CURR:')[1].split('A')[0])
    def do_get_current_ramp_rate(self):
        '''
        Retrieves the ramp rate setting in terms of the current.
        
        Input:
            None
            
        Output:
            Value of the current ramp rate in Amps per . Only works 
            when the field is actually ramping.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:RCUR')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:RCUR:')[1].split('A')[0])
    
    def do_get_field(self):
        '''
        Retrieves the field the magnet is at.
        
        Input:
            None
            
        Output:
            Value of the magnet field in Tesla.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:FLD')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:FLD:')[1].split('T')[0])
    
    def do_get_field_ramp_rate(self):
        '''
        Retrieves the field ramping rate currently set on the power supply.
        
        Input:
            None
            
        Output:
            Value of the magnet ramping rate in Tesla per . Only works when
            the field is actually ramping.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:RFLD')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:RFLD:')[1].split('A')[0])
            
    def do_get_persistent_current(self):
        '''
        Retrieves the persistent current setting of the power supply
        
        Input:
            None
        Output:
            Value of the persistent current setting, in Amps
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:PCUR')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:PCUR:')[1].split('A')[0])            
    
    def do_get_persistent_field(self):
        '''
        Retrieves the persistent field setting of the power supply
        
        Input:
            None
        Output:
            Value of the persistent field setting, in Tesla
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:PFLD')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:PFLD:')[1].split('T')[0])
    
    def do_get_action_status(self):
        '''
        Retrieves the action status of the power supply: Hold, Clamp, Ramp to setpoint, 
        or Ramp to zero.
        
        Input:
            None
        Output:
            Integer which represents the action status of the power supply: 0: Hold,
            1: Ramp to setpoint, 2: Ramp to zero, 3: Clamp.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:ACTN')
        statusString = response.split('STAT:DEV:GRPZ:PSU:ACTN:')[1]
        
        if statusString == 'HOLD':
            return 0
        elif statusString == 'RTOS':
            return 1
        elif statusString == 'RTOZ':
            return 2
        elif statusString == 'CLMP':
            return 3
            
        print "Unknown status string returned by the power supply: " + statusString
        return -1
     
    def do_get_current_setpoint(self):
        '''
        Queries the power supply and returns the current setpoint.
        
        Input:
            None
        Output:
            Value of the target magnet current, in Amps.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:CSET')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:CSET:')[1].split('A')[0])
           
     
    def do_get_field_setpoint(self):
        '''
        Queries the power supply and returns the field setpoint.
        
        Input:
            None
        Output:
            Value of the target magnetic field, in Tesla.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:FSET')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:FSET:')[1].split('T')[0])

    def do_get_current_ramp_rate_setpoint(self):
        '''
        Queries the power supply and returns the setting for the current ramp rate.
        
        Input:
            None
        Output:
            Value of the ramping rate in terms of current, in Amps per minute.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:RCST')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:RCST:')[1].split('A/m')[0])
                      
    def do_get_field_ramp_rate_setpoint(self):
        '''
        Queries the power supply and returns the setting for the field ramp rate.
        
        Input:
            None
        Output:
            Value of the ramping rate in terms of field, in Tesla per minute.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:RFST')
        return float(response.split('STAT:DEV:GRPZ:PSU:SIG:RFST:')[1].split('T/m')[0])
                      
    def do_get_switch_status(self):
        '''
        Queries the power supply and returns status of the persistent mode switch heater,
        on or off.
        
        Input:
            None
        Output:
            True if the persistent mode switch is on, False if it is off. If the 
            power supply is configured for a magnet that has no switch, this function
            returns True.
        '''
        
        response = self.send_command('READ:DEV:GRPZ:PSU:SIG:SWHT')
        status_string = response.split('STAT:DEV:GRPZ:PSU:SIG:SWHT:')[1]
        
        if status_string == 'ON':
            return True
        elif status_string == 'OFF':
            return False
        else:
            # should throw an exception or something
            return False
                      
    # def examine(self):
        # '''
        # Examine the status of the device

        # Input:
            # None

        # Output:
            # None
        # '''
        # logging.info(__name__ + ' : Examine status')

        # print 'System Status: '
        # print self.get_system_status()

        # print 'Activity: '
        # print self.get_activity()

        # print 'Local/Remote status: '
        # print self.get_remote_status()

        # print 'Switch heater: '
        # print self.get_switch_heater()

        # print 'Mode: '
        # print self.get_mode()

        # print 'Polarity: '
        # print self.get_polarity()
