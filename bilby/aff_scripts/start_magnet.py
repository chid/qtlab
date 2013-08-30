# Initialize the energy bank of the magnet quickly 
# JK August 2013

print "Make sure that the magnet is connect."

Magnet1 = qt.instruments.create('Magnet1', 'x_AMI_420', address='GPIB::22', reset=False)

Magnet1.set_field_rate(0.1)
Magnet1.set_field_setpoint(1)

B=Magnet1.get_magnet_current()
while B<0.1:
    B=Magnet1.get_magnet_current()
    
Magnet1.set_field_rate(0.01)
Magnet1.set_field_setpoint(0)

print "Field rate : " + str(Magnet1.get_field_rate())
print "Field setpoint : " + str(Magnet1.get_field_setpoint())

