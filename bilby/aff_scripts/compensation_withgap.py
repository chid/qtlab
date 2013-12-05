# Filename: compensation.py
# Charley Peng <cpeng92@gmail.com>
# October 2013
# Based off Joris Keizer's 2D sweep.

# First function is to retain on a peak.

from numpy import size
from time import time, sleep
import sys
import qt

# filename and data tags
# we still want to measure data of course.
filename = 'D244_compensation measurement'
COMP_data_tag = 'V_gate [V]'  # this is the gate one
SOURCE_2_data_tag = 'V_sd [V]'  # source 2 is SD
MULTIMETER_data_tag = 'I [pA] SET'
GMULTIMETER_data_tag = 'I [pA] GAP'
# LOCKIN

# Current Amplifier converter constant
I_sens = -1e-9  # A/V

# Current protection
# if we are above this, we break
I_max = 1e-9    # A
enable_protection = True

# first do a sweep and then determine where to start.
V_start = 0.04
V = V_start

# Alternatively Set Sweep Time in Minutes
T_sweep = True  # flag to pick time sweep
Duration = 60 * 60.0  # in seconds
T_wait = 1 * 60.0  # in seconds
measWait = 3  # time between compensating and measuring.

# Instruments parameters
COMP_driver = 'x_Yokogawa_7651'  # Compensation Gate.
COMP_address = 3
SOURCE_2_driver = 'x_Yokogawa_7651'
SOURCE_2_address = 4
SOURCE_2_enabled = True
MULTIMETER_driver = 'x_HP_34401A'
MULTIMETER_address = 1
GMULTIMETER_driver = 'x_HP_34401A'
GMULTIMETER_address = 1
LOCKIN_driver = 'x_SR830'
LOCKIN_address = 5  # change.

COMP_range = 1
SOURCE_2_range = 1  # should I change this lower?
MULTIMETER_range = 1
MULTIMETER_resolution = 3e-6
GMULTIMETER_range = 1
GMULTIMETER_resolution = 3e-6

#
# DO NOT EDIT BELOW
#


# Function to check whether an instrument is initialized
def check_instruments(value):
    instruments = qt.instruments.get_instrument_names()
    flag = False
    for i in range(size(instruments)):
        if instruments[i] == value:
            flag = True
    return flag

# Initialize COMP
print "--------------------------------------------------------"
if not check_instruments('COMP'):
    print "COMP not initialized."
    print "Trying to initialize COMP..."
    COMP = qt.instruments.create(
        'COMP', COMP_driver, address='GPIB::' + str(COMP_address), reset=False,
        maxval=0.5, minval=0)  # todo: make these parameters above.
    if not check_instruments('COMP'):
        print "Could not initialize COMP, exiting..."
        sys.exit()
    else:
        print "COMP initialized."
        COMP.set_range(COMP_range)
        print "Range: " + str(COMP.get_range()) + "V"
else:
    print "COMP initialized."
    COMP.set_range(COMP_range)
    print "Range: " + str(COMP.get_range()) + "V"

print "--------------------------------------------------------"

if not check_instruments('SOURCE_2'):
    if SOURCE_2_enabled:
        print "SOURCE_2 not initialized."
        print "Trying to initialize SOURCE_2..."
        SOURCE_2 = qt.instruments.create('SOURCE_2', SOURCE_2_driver, address='GPIB::' + str(SOURCE_2_address),
                                         maxval=0.005, minval=0,
                                         reset=False)  # todo: make these parameters above.
        if not check_instruments('SOURCE_2'):
            print "Could not initialize SOURCE_2, exiting..."
            sys.exit()
        print "SOURCE_2 initialized."
        SOURCE_2.set_range(SOURCE_2_range)
        print "Range: " + str(SOURCE_2.get_range()) + "V"
    else:
        print "SOURCE_2 not enabled."
else:
    if check_instruments('SOURCE_2'):
        print "SOURCE_2 initialized."
        SOURCE_2.set_range(SOURCE_2_range)
        print "Range: " + str(SOURCE_2.get_range()) + "V"
    else:
        print "SOURCE_2 initialized but not enabled."


# Initialize MULTIMETER
print "--------------------------------------------------------"
if not check_instruments('MULTIMETER'):
    print "MULTIMETER not initialized."
    print "Trying to initialize MULTIMETER..."
    MULTIMETER = qt.instruments.create(
        'MULTIMETER', MULTIMETER_driver, address='GPIB::' + str(MULTIMETER_address),
        reset=False)
    if not check_instruments('MULTIMETER'):
        print "Could not initialize MULTIMETER, exiting..."
        sys.exit()
    else:
        print "MULTIMETER initialized"
        print "Range: " + str(MULTIMETER.get_range())
        print "Resolution: " + str(MULTIMETER.get_resolution())
else:
    print "MULTIMETER initialized"
    MULTIMETER.set_range(MULTIMETER_range)
    MULTIMETER.set_resolution(MULTIMETER_resolution)
    print "Range: " + str(MULTIMETER.get_range())
    print "Resolution: " + str(MULTIMETER.get_resolution())

# Initialize GMULTIMETER
print "--------------------------------------------------------"
if not check_instruments('GMULTIMETER'):
    print "GMULTIMETER not initialized."
    print "Trying to initialize GMULTIMETER..."
    GMULTIMETER = qt.instruments.create(
        'GMULTIMETER', GMULTIMETER_driver, address='GPIB::' + str(GMULTIMETER_address),
        reset=False)
    if not check_instruments('GMULTIMETER'):
        print "Could not initialize GMULTIMETER, exiting..."
        sys.exit()
    else:
        print "GMULTIMETER initialized"
        print "Range: " + str(GMULTIMETER.get_range())
        print "Resolution: " + str(GMULTIMETER.get_resolution())
else:
    print "GMULTIMETER initialized"
    GMULTIMETER.set_range(GMULTIMETER_range)
    GMULTIMETER.set_resolution(GMULTIMETER_resolution)
    print "Range: " + str(GMULTIMETER.get_range())
    print "Resolution: " + str(GMULTIMETER.get_resolution())


if not check_instruments('LOCKIN'):
    print "Lock In was not Initialized...\nInitializing..."
    LOCKIN = qt.instruments.create('LOCKIN', LOCKIN_driver, address='GPIB::' + str(LOCKIN_address), reset=False)
    # @type LOCKIN: x_SR830
    #import x_SR830
    #LOCKIN = x_SR830('LOCKIN', address='GPIB::'+str(LOCKIN_address), reset=False)
    # LOCKIN.
    if not check_instruments('LOCKIN'):
        print "Could not initialize LOCKIN, exiting..."
        sys.exit()
# else we shouldn't need to do anything, though we could set frequency /
# amplitude.  since that's not part of this script.


def compensation(OldV=V, LockInThresh=0.005, Meter=None, MeterThresh=1e-8, LockIn=LOCKIN, jump=0.0004, iterations=1):
    # does one shot of compensation by default
    # threshold
    print "Original voltage", OldV
    # TODO: Fix (Simple just add as parameters)
    # right now this will just be a hardcoded value
    if OldV > .5 or OldV < 0:
        print 'Outside of voltage range'
        sys.exit(1)

    # Assumptions
    # All instruments initialized
    # Could have a check if jump is too large, perhaps user inputted mV instead of in volts.

    # Measure the Lock In
    LockInX = LockIn.get_X()
    # We can also get_Y as an error check.

    # iterations will be the number of iterations remaining
    while iterations > 0:
        iterations -= 1  # decrement the counter
        if Meter is not None:
            I = Meter.readval()  # or is it read nextval that we should use
            if I > MeterThresh:
                continue  # this means we don't bother correcting.

        if abs(LockInX) > LockInThresh:
            if LockInX > 0:
                OldV += jump  # in volts
            else:
                OldV -= jump
                # else we do nothing.

    # By default we do not measure I_sd but if it is provided we
    # also provide meter threshold. also this can be used just as a check we're on the peak
    print "New voltage", OldV
    return OldV, LockInX  # which has now been modified

# Setup the sweep arrays
print "--------------------------------------------------------"
if T_sweep:
    print "Sweeping for {0} minutes, waiting for {1} seconds".format(Duration / 60.0, T_wait)
    print "This script will assume that the gain setting on both the multimeters are identical"
    print "Starting at the voltage {0}".format(V_start)
else:
    print 'This script only does time sweeps, so you better set that up'
    sys.exit(0)

# Ask whether to continue
print "--------------------------------------------------------"
print "FILENAME: " + filename
print "--------------------------------------------------------"
key = raw_input('Continue [Y]/n?')
if (key == 'n') or (key == 'N'):
    sys.exit('Exiting')

# Setup the data file and plots
data = qt.Data(name=filename)
# todo: figure out timezone of time.time()
# seems to be local time.
data.add_coordinate('Time [Unix]')
data.add_coordinate(COMP_data_tag)
data.add_value(MULTIMETER_data_tag)
data.add_value(GMULTIMETER_data_tag)
data.add_value("LockInX")
data.add_value("LockIn")
# the last value is a flag which tells you whether the lock in measurement can be recorded.
# I know, this isn't really necessary.
data.create_file()

plot_sweep = qt.Plot2D(data, name='Sweep', coorddim=1, valdim=2, maxtraces=4)

# Start the measurement

t = time()
qt.mstart()
if T_sweep:
    # set SD bias. .5 mV
    # TODO: move this up
    SOURCE_2.set_voltage(0.0005)
    COMP.set_voltage(V_start)
    while Duration > 0:
        # Decrement duration by time since last measurement
        Duration -= (time() - t)  # this will be a floating point.
        t = time()

        # I was thinking we read before and then read straight after
        # => Just to see it's doing the correct thing.
        # But then plotting it straight out may not make sense.

        # TODO: do I need to wait before reading? similarly below
        I_meas = MULTIMETER.get_readval()
        I_gap = GMULTIMETER.get_readval() * I_sens / 1e-12  # in pA
        # If MULTIMETER goes into overload set the value to zero
        if abs(I_meas) > 1e20:
            I_meas = 0
            break
        data.add_data_point(time(), V, I_meas * I_sens / 1e-12, I_gap, 0, 0)  # terrible terrible
        plot_sweep.update()

        V, LockInXVal = compensation(V, LockInThresh=.5e-12, jump=1e-4)  # jump .1 mV on the gate
        if V > 0.5 or V < 0:
            print 'exited bounds'
            break

        if measWait > 0: # wait for some time.
            qt.msleep(measWait)

        COMP.set_voltage(V)
        I_meas = MULTIMETER.get_readval()
        I_gap = GMULTIMETER.get_readval() * I_sens / 1e-12  # in pA
        data.add_data_point(time(), V, I_meas * I_sens / 1e-12, I_gap, LockInXVal, 1)

        if (I_meas * I_sens) > abs(I_max):
            print "BREAKING: Max I reached"
            if enable_protection:
                print 'Exceed Current Limit Exiting...'
                break

        qt.msleep(0.001)
        sleep(T_wait)  # probably blocking so not good, probably should use msleep

# data.new_block()
# plot_map.update()

qt.mend()

# Tidying up
# Don't worry this ramps down.
COMP.set_voltage(0) # perhaps this shouldn't be done, just leave it where it is. [on a peak]
# I will just leave SD be the same.

# Save sweep and map as png-file
plot_sweep.save_png()
# if (V2_start<>V2_end) and (SOURCE_2_enabled==True):
# plot_map.save_png()

data.close_file()
