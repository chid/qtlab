# Filename: clear_all_instruments.py
# Joris Keizer <jgkeizer@gmail.com> 
# Sep 2013

instruments=qt.instruments.get_instrument_names()
for i in range(size(instruments)):
    qt.instruments.remove(instruments[i])
