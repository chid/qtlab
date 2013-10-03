import qt
import numpy



class channels(object):

    '''Class for  channels to be used in the sweeper.
    Usage: Initialise with
    <name> = channels.channels_out('<name>', inst, parameter, dividerfactor = '<float>')
    where inst, is an instrument form the qt.instruments class, and parameter is a parameter in that instance
    '''

    def __init__(self, name, inst, parameter):
        self.inst = inst
        self._parameter_name = parameter
        self._name = name

    def get_units(self):
        return self.inst.get_parameter_options(self._parameter_name)['units']
    
    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name
    
class channels_out(channels):
    '''subclass for  out channels'''
    def __init__(self,name, inst, parameter, dividerfactor = 1):
        super(channels_out, self).__init__(name, inst, parameter)
        self._divider_factor = float(dividerfactor)
        self._check_parameter_has_sweep_tag()
        
    def get_out(self):
        return float(self.inst.get(self._parameter_name))/ self._divider_factor

    def set_out(self,val):
        self.inst.set(self._parameter_name, val*self._divider_factor)

    def get_divider_factor(self):
        return self._divider_factor

    def set_divider_factor(val):
        self._divider_factor = float(val)

    def _check_parameter_has_sweep_tag(self):
        tag = self.inst.get_parameter_options(self._parameter_name)['tags'] 
        if 'sweep' not in tag:
            print 'Warning: this may not be a parameter you can sweep'
            
class channels_in(channels):
    '''subclass for in channels'''
    def __init__(self,name, inst, parameter, gain = 1e8):
        super(channels_in, self).__init__(name, inst, parameter)
        self._gain = float(gain) 
        self._check_parameter_has_measure_tag()


    def get_in(self):
        return self.inst.get(self._parameter_name)/self._gain

    def get_gain(self):
        return self._gain

    def set_gain(self, val):
        self._gain = float(val)

    
    def _check_parameter_has_measure_tag(self):
        tag = self.inst.get_parameter_options(self._parameter_name)['tags'] 
        if 'measure' not in tag:
            print 'Warning: this may not be a parameter you can measure'        
        
