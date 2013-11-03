import pygtk
pygtk.require('2.0')
import gtk
import sweep


class sweep_gui:

    def __init__(self, sweep):
        
        self.sweep = sweep

        self._adj_loops = [[[] for col in range(3)] for row in range(self.sweep._number_of_loops)]
        self._adj_channels = [[[] for col in range(3)] for row in range(len(self.sweep.get_channels_out())+1)]

        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("destroy", lambda w: gtk.main_quit())
        window.set_title("Sweep GUI")
                                  
        main_hbox = gtk.VBox(False, 5)
        main_hbox.set_border_width(10)
        window.add(main_hbox)
        adj = [[],[]]
        self.get_all()
        for i in range(0, self.sweep.get_number_of_loops()):
            self.axis_spinners(main_hbox, i)
        self.constant_spinners(main_hbox)

        button = gtk.Button("Start Sweep!")
        button.connect("clicked", self.start, adj)
        main_hbox.pack_start(button, True, True, 5)

        window.show_all()

        
    def start(self, adj, set):
        self.sweep.run()

    def get_all(self):
        vec1 = self.sweep.get_channel_factors()
        vec2 = self.sweep.get_loops()
        for j in range(0,self.sweep.get_number_of_loops()):
            for i in range(0,3):
                self._adj_loops[j][i] = gtk.Adjustment(0,-1, 1, .1, 0.1, 0.0)
                self._adj_loops[j][i].set_value(vec2[j][i])
            
            for i in range(0, len(self.sweep.get_channels_out())):
                self._adj_channels[j][i] = gtk.Adjustment(0,-1, 1, .1, 0.1, 0.0)
                self._adj_channels[j][i].set_value(vec1[j][i])

        for j in range(0,self.sweep.get_number_of_loops()):
            for i in range(0,3):
                self._adj_loops[j][i].connect("value_changed", self.loop_change, j)
            for i in range(0, len(self.sweep.get_channels_out())):
                self._adj_channels[j][i].connect("value_changed", self.channel_factor_change, j)
                
        vec = self.sweep.get_channel_constants()
        for i in range(0, len(self.sweep.get_channels_out())):
                self._adj_channels[self.sweep.get_number_of_loops()][i] = gtk.Adjustment(0,-1, 1, .1, 0.1, 0.0)
                self._adj_channels[self.sweep.get_number_of_loops()][i].set_value(float(vec[i]))
                self._adj_channels[self.sweep.get_number_of_loops()][i].connect("value_changed",
                                                                                    self.channel_factor_change, self.sweep.get_number_of_loops())
            
        
        
    def constant_spinners(self, box):
        frame = gtk.Frame('starting constants')
        box.pack_start(frame, True, True, 0)
        hbox = gtk.HBox(False, 0)
        hbox.set_border_width(5)
        frame.add(hbox)
        self.create_channel_spinner(hbox, self.sweep.get_number_of_loops())
        
    def axis_spinners(self, box, loop):
        if loop == 0:
            frame = gtk.Frame('x axis')
        elif loop == 1:
            frame = gtk.Frame('y axis')
        elif loop == 2:
            frame = gtk.Frame('z axis')
        else:
            frame = gtk.Frame('loop ' + str(loop))
            
        box.pack_start(frame, True, True, 0)
        hbox = gtk.HBox(False, 0)
        hbox.set_border_width(5)
        frame.add(hbox)        
        self.create_loops_spinner(hbox, loop)
        self.create_channel_spinner(hbox, loop)       
            
    def create_loops_spinner(self, box, loop):
        self.create_spinner(box, "Start :", self._adj_loops[loop][0])            
        self.create_spinner(box, "End :", self._adj_loops[loop][1])
        self.create_spinner(box, "Step size :", self._adj_loops[loop][2])


    def create_channel_spinner(self, box, loop):      
        for i in range(0, len(self.sweep.get_channels_out())):
            self.create_spinner(box, self.sweep.get_channels_out()[i].get_name() +" :",self._adj_channels[loop][i])
                    
    def channel_factor_change(self, adj, loop):
        channel_factor = [[] for row in range(len(self.sweep.get_channels_out()))] 
        for i in range(0, len(self.sweep.get_channels_out())):
            channel_factor[i] = self._adj_channels[loop][i].get_value()
        if loop == self.sweep.get_number_of_loops():
            self.sweep.set_channel_constants(channel_factor)
        else:
            self.sweep.set_channel_factors(channel_factor,loop)

    def loop_change(self, adj, loop):
        loops = [[] for row in range(3)]
        for i in range(0, 3):
            loops[i] = self._adj_loops[loop][i].get_value()
        self.sweep.set_loops(loops, loop)

        
        

            
    

    def create_spinner(self, box, label, adj):
        
        vbox1 = gtk.VBox(False, 0)
        box.pack_start(vbox1, True, True, 5)
        labels = gtk.Label(label)
        labels.set_alignment(0, 0.5)
        vbox1.pack_start(labels, False, True, 0)
        spinner = gtk.SpinButton(adj, 0, 6)
        spinner.set_numeric(True)
        spinner.set_wrap(False)
        vbox1.pack_start(spinner, False, True, 0)
        

    
def main():
    gtk.main()
    return 0
if __name__ == "__main__":
    sweep_gui(sw1)

    main()
    
        

        
    
