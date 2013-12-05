
from instrument import Instrument

class Variable:
	""" Variable class
		This class represents a scalar variable which is set by the experimenter during an experiment.
		It serves as a base class that will be communicated to various instruments, implemented as subclasses.
		
		This class can be used by itself, as it will remember the value passed to set_value() and will
		return it via get_value(), so you can use it to store variables which are not read in from instruments.
	"""
	def __init__(self, name, **kwargs):
		""" Constructor for the Variable class.
				name - string indicating the simple name of the variable, used eg in saving to .mat file
				
				Optional arguments:
				units - string indicating the units of the variable. Default: "a. u."
				title - string indicating the long name of the variable, used in plot titles, axes. Defaults to the name.
				value - initial value of the variable. Defaults to 0.
				gain - A scale factor to divide the variable by before setting the instrument. I.e. if you are using a voltage source with a 1/5 voltage divider at the output, set the gain to 0.2.
		"""
		self.name  = name	
		self.units = kwargs.get('units', 'a. u.')
		self.title = kwargs.get('title', name) 
		self.value = kwargs.get('value', 0)
		self.gain  = kwargs.get('gain', 1)
	
	def set_value(self, value):
		self.value = value / gain

	def get_value(self):
		return self.value * self.gain
		
	def set_name(self, name):
		self.name = name
	
	def get_name(self):
		return self.name
		
	def set_title(self, title):
		self.title = title
	
	def get_title(self):
		return self.title
	
	def get_axis_title(self):
		''' Returns the title to use on a plot axis, including the units in parentheses.
		'''
		return self.get_title() + ' (' + self.get_units() + ')'
	
	def set_units(self, units):
		self.units = units
		
	def get_units(self):
		return self.units
	
	def get_gain(self):
		return self.gain
	
	def set_gain(self, gain):
		self.gain = gain
		  
# class VoltageVariable(Variable):
	# """
		# A class to represent a voltage which is set by an instrument
		# This is just a base class for specific instruments, each of which might have its
		# own set of commands. Subclass this one to implement specific voltage source instruments.
		
		# This class has one additional member which Variable does not, an Instrument which represents
		# a voltage source.
		
		# It also has an optional gain value, which represents a scale factor that is applied to the 
		# voltage before it reaches the DUT (eg, a voltage divider or amplifier). Could also be used to
		# change units (eg, to use mV instead of V, use a gain of 1000).
	# """
	
	# def __init__(self, instrument, name, **kwargs):
		# ''' Constructor takes all of the same arguments as Variable's constructor, plus:
			# instrument - a Instrument object for an initialized voltage source instrument
		# '''
		# Variable.__init__(self, name, **kwargs)
		# self.instrument = instrument
		# self.units = kwargs.get('units', 'V')
			
	# def set_voltage(self, volts):
		# ''' Convenience function, just calls set_value(volts).
		# '''
		# self.set_value(volts)
	
	# def get_voltage(self):
		# ''' Convenience function, calls get_value(). 
		# '''
		# return self.get_value()
	
	# def get_gain(self):
		# ''' Returns the gain value of the output voltage. For example, if there is a 1/5
			# voltage divider placed at the output of the voltage source, the gain is 0.2.
		# '''
		# return self.gain
		
class YokoVoltage(Variable):
	''' A class to represent a VoltageVariable set by a Yokogawa 7651 VoltageVariable source.
	'''
	def __init__(self, instrument, name, **kwargs):
		''' Constructor takes an instrument, which must be x_Yokogawa_7651 type.
			Default units are 'V'.
		'''
		Variable.__init__(self, name, **kwargs)
		self.instrument = instrument
		self.units = kwargs.get('units', 'V')
	
	def set_value(self, value):
		''' Sets the Yoko voltage source to the value passed, divided by the gain.
		'''
		self.instrument.set_voltage(value / self.gain)
	
	def get_value(self):
		''' Queries the Yokogawa instrument, returns the present voltage setting times the gain. 
		'''
		return self.gain * self.instrument.get_voltage()

class SR830AuxVoltage(Variable):
	''' A class to represent a voltage set by one of the AUX OUT ports of an SR830
		lock-in amplifier.
	'''
	def __init__(self, instrument, channel, name, **kwargs):
		''' Constructor takes the SR830 instrument object and the channel number (1-4)
			of the AUX OUT channel to use. Plus all of the same options as for the Variable class.
			Default units are 'V'.
		'''
		Variable.__init__(self, instrument, name, **kwargs)
		self.channel = channel
		self.units = kwargs.get('units', 'V')
		
	def set_value(self, value):
		''' Sets the SR830 AUX OUT voltage to the passed value, divided by the gain.
		'''
		self.instrument.set_oaux(self.channel, value / self.gain)
	
	def get_value(self):
		''' Queries the SR830 and returns the present voltage setting, times the gain.
		'''
		return self.gain * self.instrument.get_oaux(self.channel)

class Channel:
	""" Channel class
		This class represents a scalar data point which is read in from instruments during the experiment.
	"""
	def __init__(self, name, **kwargs):
		""" Constructor for the Channel class.
				name - string indicating the simple name of the data point, used eg in saving to .mat file
				
				Optional arguments:
				units - string indicating the units of the variable. Default: "a. u."
				title - string indicating the long name of the variable, used in plot titles, axes.
				Defaults to the name.
				gain - A scale factor. The data point will be gain times the value read from the instrument.
				Defaults to 1.
		"""
		self.name  = name	
		self.units = kwargs.get('units', 'a. u.')
		self.title = kwargs.get('title', name) 
		self.gain  = kwargs.get('gain', 1)
	
	def read_value(self):
		''' Reads in the value of the current measurement from the instrument.
		'''
		return 0 # nothing to do until this class is overloaded
		
	def set_name(self, name):
		self.name = name
	
	def get_name(self):
		return self.name
		
	def set_title(self, title):
		self.title = title
	
	def get_title(self):
		return self.title
	
	def set_units(self, units):
		self.units = units
		
	def get_units(self):
		return self.units
	
	def get_gain(self):
		return self.gain
	
	def set_gain(self, gain):
		self.gain = gain

class Keithley2001Current(Channel):
	''' This class represents a current value, measured using a current preamp fed into a Keithley 2001
		digital multimeter as a voltage. The gain represents the transconductance gain of the amplifier 
		(in, e.g., amps per volt). 
	'''
	
	def __init__(self, instrument, name, **kwargs):
		''' Constructor: same as Channel, but accepts an instrument with which to read the data point. Units default to 'A'.
		'''
		Channel.__init__(self, name, **kwargs)
		self.instrument = instrument
		self.units = kwargs.get('units', 'A')
	
	def read_value(self):
		return self.gain * self.instrument.get_readnextval()
		
class SR830X(Channel):
	''' This class represents the measurement of the X channel of an SR830 lock-in amplifier.
		No assumption is made about what mode the lock-in is in (A, A-B, I6, or I8).
	'''
	
	def __init__(self, instrument, name, **kwargs):
		''' Constructor, same as for Channel but with an instrument passed.
		'''
		Channel.__init__(self, name, **kwargs)
		self.instrument = instrument
	
	def read_value(self):
		return self.gain * self.instrument.get_X()
		
class SR830Y(Channel):
	''' This class represents the measurement of the Y channel of an SR830 lock-in amplifier.
		No assumption is made about what mode the lock-in is in (A, A-B, I6, or I8).
	'''
	
	def __init__(self, instrument, name, **kwargs):
		''' Constructor, same as for Channel but with an instrument passed.
		'''
		Channel.__init__(self, name, **kwargs)
		self.instrument = instrument
	
	def read_value(self):
		return self.gain * self.instrument.get_Y()
		
class SR830Amplitude(Variable):
	''' This class represents the amplitude of a lock-in excitation signal, 
		set by an SR830 lock-in amplifier.
	'''
	
	def __init__(self, instrument, name, **kwargs):
		''' Constructor. instrument must be of 'SR830' type
		'''
		Variable.__init__(self, name, **kwargs)
		self.instrument = instrument
		self.units = kwargs.get('units', 'V')
		
	def get_value(self):
		return self.gain * self.instrument.get_amplitude()
	
	def set_value(self, new_value):
		self.instrument.set_amplitude(new_value / self.gain)
		
class SR830Frequency(Variable):
	''' This class represents the frequency of a lock-in excitation signal, 
		set by an SR830 lock-in amplifier.
	'''
	
	def __init__(self, instrument, name, **kwargs):
		''' Constructor. instrument must be of 'SR830' type
		'''
		Variable.__init__(self, name, **kwargs)
		self.instrument = instrument
		self.units = kwargs.get('units', 'Hz')
		
	def get_value(self):
		return self.gain * self.instrument.get_frequency()
	
	def set_value(self, new_value):
		self.instrument.set_frequency(new_value / self.gain)
		