# Filename: compensation.py
# Charley Peng <cpeng92@gmail.com>
# October 2013
# Based off Joris Keizer's 2D sweep.

# First function is to retain on a peak.
# Function Compensation.

from numpy import pi, random, arange, size
from time import time, sleep
import sys

import qt

print 'This is incomplete'
import sys
# probably needs some more try catches
sys.exit(1)


# filename and data tags
# we still want to measure data of course.
filename = 'D236_measuring'
SOURCE_1_data_tag = 'V_gate [V]'
SOURCE_2_data_tag = 'V_sd [V]'
MULTIMETER_data_tag = 'I [pA]'
# LOCKIN

# Current Amplifier converter constant
I_sens = -1e-9  # A/V

# Current protection
# if we are above this, we break
I_max = 1e-9    # A
enable_protection = True

# SOURCE_1 sweep
V1_start = 0.00
V1_end = 1.0
V1_step = 0.005

# SOURCE_2 sweep
V2_start = 0.001
V2_end = 0.001
V2_step = 0.05

# Alternatively Set Sweep Time in Minutes
T_sweep = True  # flag to pick time sweep
Duration = 60 * 60  # in seconds
T_wait = 1 * 60 # in seconds

# Instruments parameters
SOURCE_1_driver = 'x_Yokogawa_7651'
SOURCE_1_address = 3
SOURCE_2_driver = 'x_Yokogawa_7651'
SOURCE_2_address = 4
SOURCE_2_enabled = True
MULTIMETER_driver = 'x_HP_34401A'
MULTIMETER_address = 1
LOCKIN_driver = 'x_SR830'
LOCKIN_address = 5  # change.

SOURCE_1_range = 1
SOURCE_2_range = 1
MULTIMETER_range = 1
MULTIMETER_resolution = 3e-6


#
# DON'T EDIT BELOW
#

def compensation(OldV=V, LockInThresh=0.005, Meter=None, MeterThresh=1e-8, LockIn=LOCKIN, jump=0.004, iterations=1):
    """
    @type LockIn: x_SR830
    :param LockInThresh:
    :param Meter:
    :param MeterThresh:
    :param LockIn:
    :param jump:
    :param iterations:
    :return:
    """
    # does one shot of compensation by default
    # threshold

    # TODO: Fix

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
                OldV += jump # in volts
            else:
                OldV -= jump
        # else we do nothing.

    # By default we do not measure I_sd but if it is provided we
    # also provide meter threshold. also this can be used just as a check we're on the peak

    return OldV # which has now been modified

# Function to check whether an instrument is initialized
def check_instruments(str):
    instruments = qt.instruments.get_instrument_names()
    flag = False
    for i in range(size(instruments)):
        if instruments[i] == str:
            flag = True
    return flag

# Initialize SOURCE_1
print "--------------------------------------------------------"
if not check_instruments('SOURCE_1'):
    print "SOURCE_1 not initialized."
    print "Trying to initialize SOURCE_1..."
    SOURCE_1 = qt.instruments.create(
        'SOURCE_1', SOURCE_1_driver, address='GPIB::' + str(SOURCE_1_address), reset=False)
    if not check_instruments('SOURCE_1'):
        print "Could not initialize SOURCE_1, exiting..."
        sys.exit()
    else:
        print "SOURCE_1 initialized."
        SOURCE_1.set_range(SOURCE_1_range)
        print "Range: " + str(SOURCE_1.get_range()) + "V"
else:
    print "SOURCE_1 initialized."
    SOURCE_1.set_range(SOURCE_1_range)
    print "Range: " + str(SOURCE_1.get_range()) + "V"

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

# Function to generate the sweep arrays
def generate_sweep(V1, V2, step):
    sweep = None
    if V1 == V2:
        sweep = [V1]
    elif (V2 >= 0 and V1 >= 0) or (V2 <= 0 and V1 <= 0):
        if V1 < V2:
            sweep = arange(V1, V2 + step, abs(step))
        else:
            sweep = arange(V1, V2 - step, -abs(step))
    return sweep

# Setup the sweep arrays
print "--------------------------------------------------------"
if T_sweep:
    print "Sweeping for {0} minutes, waiting for {1} seconds".format(Duration / 60.0, T_wait)
else:
    if SOURCE_1.get_range() < abs(V1_start) or SOURCE_1.get_range() < abs(V1_end):
        print "WARING: Sweep outside SOURCE_1 range settings"
    sweep_1 = generate_sweep(V1_start, V1_end, V1_step)
    print "Sweep SOURCE_1 from " + str(V1_start) + "V to " + str(V1_end) + "V in " + str(V1_step) + "V steps"

# Ask whether to continue
print "--------------------------------------------------------"
print "FILENAME: " + filename
print "--------------------------------------------------------"
key = raw_input('Continue [Y]/n?')
if (key == 'n') or (key == 'N'):
    sys.exit('Exiting')

# Setup the data file and plots
data = qt.Data(name=filename)
if T_sweep:
    # todo: figure out timezone of time.time()
    data.add_coordinate('Time [Unix]')
data.add_coordinate(SOURCE_1_data_tag)
data.add_value(MULTIMETER_data_tag)
data.create_file()

plot_sweep = qt.Plot2D(data, name='Sweep', coorddim=1, valdim=2, maxtraces=4)

# Start the measurement

t = time()
qt.mstart()
if T_sweep:
    while Duration > 0:
        # Decrement duration by time since last measurement
        Duration -= (time() - t) # this will be a floating point.
        t = time()

        # I was thinking we read before and then read straight after => Just to see it's doing the correct thing.
        # But then plotting it straight out may not make sense.

        I_meas = MULTIMETER.get_readval()
        # If MULTIMETER goes into overload set the value to zero
        if abs(I_meas) > 1e20:
            I_meas = 0
            break
        data.add_data_point(time(), V, I_meas * I_sens / 1e-12)
        plot_sweep.update()

        V = compensation()
        I_meas = MULTIMETER.get_readval()
        data.add_data_point(time(), V, I_meas * I_sens / 1e-12)

        if (I_meas * I_sens) > abs(I_max):
            print "BREAKING: Max I reached"
            if enable_protection:
                print 'Exceed Current Limit Exiting...'
                break

        qt.msleep(0.001)
        sleep(T_wait)  # probably blocking so not good, probably should use msleep

else:
    for V1 in sweep_1:
        SOURCE_1.set_voltage(V1)
        I_meas = MULTIMETER.get_readval()
        # If MULTIMETER goes into overload set the value to zero
        # This works for the HP multimeter, other multimeters may need another values
        # surely you should do something else if it goes into overload,
        # break/reset the instrument
        if abs(I_meas) > 1e20:
            I_meas = 0
        data.add_data_point(V2, V1, I_meas * I_sens / 1e-12)
        plot_sweep.update()
        qt.msleep(0.001)
        if (I_meas * I_sens) > abs(I_max):
            print "BREAKING: Max I reached"
            if enable_protection:
                print 'Exceed Current Limit Exiting...'
                break
data.new_block()
# plot_map.update()

qt.mend()

# Tidying up
# Don't worry this ramps down.
SOURCE_1.set_voltage(0)

# Save sweep and map as png-file
plot_sweep.save_png()
# if (V2_start<>V2_end) and (SOURCE_2_enabled==True):
# plot_map.save_png()

data.close_file()
