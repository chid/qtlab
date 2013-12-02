
from numpy import arange

# Function to generate the sweep arrays    
def generate_sweep(V1,V2,step):
    if (V2 >= 0 and V1 >= 0) or (V2 <= 0 and V1 <= 0):
        if V1 < V2:
            sweep = arange(V1,V2+step,abs(step))  
        else:
            sweep = arange(V1,V2-step,-abs(step))
    if V2 > 0 and V1 < 0:
        sweep = arange(V1,V2+step,abs(step))
    if V2 < 0 and V1 > 0:
        sweep = arange(V1,V2-step,-abs(step))
    if V1 == V2:
        sweep=[V1]
    return sweep
       