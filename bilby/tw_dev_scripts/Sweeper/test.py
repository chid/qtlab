import channels
import numpy
import sweep




sw1 = sweep.sweep('D244_2Dsweep',[VSD, VG1],[I1], loops = '1', updatepointbypoint = True)

sw1.set_loops([0,0.001,.00005],0)
sw1.set_channel_factors([1,1],0)

#sw1.add_final_coord([[0.2,0.4]],0)

#sw1.add_final_coord([[0.4,0.2],[0.2,0.4]],1)


#sw1.set_loops([0,0.2,0.005],1)
#sw1.set_channel_factors([0,1],1)

#sw1.set_loops([0,0.2,0.05],2)
#sw1.set_channel_factors([0,1,0],2)

#sw1.set_loops([0,0.2,0.05],3)
#sw1.set_channel_factors([0,1,0],3)


sw1.set_channel_constants([0,0])
