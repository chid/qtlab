
class Dev014JK : 
	def __init__(self):
		self.yoko_SA = qt.instruments.create('YokoSA',  'x_Yokogawa_7651', address='GPIB::5',  reset=False)
		self.yoko_SB = qt.instruments.create('YokoSB',  'x_Yokogawa_7651', address='GPIB::8',  reset=False)
		self.yoko_A  = qt.instruments.create('YokoA',   'x_Yokogawa_7651', address='GPIB::2',  reset=False)
		self.yoko_B  = qt.instruments.create('YokoB',   'x_Yokogawa_7651', address='GPIB::6',  reset=False)
		self.meter_A = qt.instruments.create('MeterA',  'x_HP_34401A',     address='GPIB::14', reset=False)
		self.meter_B = qt.instruments.create('MeterB',  'x_HP_34401A',     address='GPIB::9',  reset=False)
		self.lockin  = qt.instruments.create('LockInB', 'SR830',           address='GPIB::13', reset=False)
		self.meter_A.set_resolution(3e-5)
		self.meter_B.set_resolution(3e-5)
		
		# create variables
		self.vA  = YokoVoltage(self.yoko_A,  'vA',  title='V_A',  units='V', gain=0.2)
		self.vB  = YokoVoltage(self.yoko_B,  'vB',  title='V_B',  units='V', gain=0.2)
		self.vSA = YokoVoltage(self.yoko_SA, 'vSA', title='V_SA', units='V')
		self.vSB = YokoVoltage(self.yoko_SB, 'vSB', title='V_SB', units='V')
		
	def read_settings(self) : 
		print "yoko_SA: " + str(self.yoko_SA.get_voltage()) + " V."
		print "yoko_SB: " + str(self.yoko_SB.get_voltage()) + " V."
		print "yoko_A: " + str(self.yoko_A.get_voltage()) + " V."
		print "yoko_B: " + str(self.yoko_B.get_voltage()) + " V."
		print "Lock-in frequency: " + str(self.lockin.get_frequency()) + " Hz"
		print "Lock-in amplitude: " + str(self.lockin.get_amplitude()) + " V"
		
	def read_meters(self) : 
		print "meter_A: " + str(self.meter_A.get_readval()) + " V."
		print "meter_B: " + str(self.meter_A.get_readval()) + " V."
		print "Lockin X: " + str(self.lockin.get_X()) + " V."
		print "Lockin Y: " + str(self.lockin.get_Y()) + " V."
		
	def make_safe(self) :
		self.yoko_A.set_voltage(0)
		self.yoko_B.set_voltage(0)
		self.yoko_SA.set_voltage(0)
		self.yoko_SB.set_voltage(0)
	
