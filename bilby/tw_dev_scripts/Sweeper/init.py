import channels
import numpy
import sweep

time1 = qt.instruments.create('Meta', 'x_time')
HP1 = qt.instruments.create('HP1', 'x_HP_34401A_dummy', address = 'GPIB::14')
HP2 = qt.instruments.create('HP2', 'x_HP_34401A_dummy', address = 'GPIB::14')
Yoko1 = qt.instruments.create('Yoko1', 'x_Yokogawa_7651_dummy', address= 'GPIB::14')
Yoko2 = qt.instruments.create('Yoko2', 'x_Yokogawa_7651_dummy', address='GPIB::14')
Yoko3 = qt.instruments.create('Yoko3', 'x_Yokogawa_7651_dummy', address='GPIB::14')
Yoko1.set_parameter_options('voltage',maxval=2.00,minval=-2.00)
Yoko2.set_parameter_options('voltage',maxval=2.00,minval=-2.00)
Yoko3.set_parameter_options('voltage',maxval=2.00,minval=-2.00)
Lockin = qt.instruments.create('Lockin', 'x_SR830_dummy', address = 'GPIB::5')

VG1 = channels.channels_out('VG1', Yoko1, 'voltage', dividerfactor = '1')
VG2 = channels.channels_out('VG2', Yoko2, 'voltage', dividerfactor = '1')
VG3 = channels.channels_out('VG3', Yoko3, 'voltage', dividerfactor = '1')
VG4 = channels.channels_out('VG4', Lockin, 'out1', dividerfactor = '1')
Time = channels.channels_out('Time', time1, 'time', dividerfactor = '1')
I1 = channels.channels_in('I1', HP1, 'readval', gain = '2e8')
I1.set_units('A')
I2 = channels.channels_in('I2', HP2, 'readval', gain = '2e8')
I2.set_units('A')
