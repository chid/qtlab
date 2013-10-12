import channels
import numpy
import sweep




sw1 = sweep.sweep('D244_2Dsweep',[Time, VG1],[I1], loops = '2', updatepointbypoint = True)

sw1.set_loops([0,5,.2],0)
sw1.set_channel_factors([1,0],0)

#sw1.add_final_coord([[0.2,0.4]],0)

#sw1.add_final_coord([[0.4,0.2],[0.2,0.4]],1)


sw1.set_loops([0,0.2,0.005],1)
sw1.set_channel_factors([0,1],1)

#sw1.set_loops([0,0.2,0.05],2)
#sw1.set_channel_factors([0,1,0],2)

#sw1.set_loops([0,0.2,0.05],3)
#sw1.set_channel_factors([0,1,0],3)


sw1.set_channel_constants([0,0])
