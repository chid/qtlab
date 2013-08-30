# Create instruments

YOKO_1 = qt.instruments.create('YOKO_1','x_Yokogawa_7651',address='GPIB::4', reset=False)
#YOKO_2 = qt.instruments.create('YOKO_2','x_Yokogawa_7651',address='GPIB::3', reset=False)
AGILENT = qt.instruments.create('AGILENT','x_HP_34401A', address='GPIB::1', reset=False)

# Setup instruments
YOKO_1.set_range(10)           # 
#YOKO_2.set_range(1)            #   
AGILENT.set_range(0.1)         # V, (0.01..100V)     
AGILENT.set_resolution(1e-05)  # V, (1e-4..3e-6)      

print "YOKO_1 range: " + str(YOKO_1.get_range())
#print "YOKO_2 range: " + str(YOKO_2.get_range())
print "AGILENT range: " + str(AGILENT.get_range())
print "AGILENT resolution: " + str(AGILENT.get_resolution())
