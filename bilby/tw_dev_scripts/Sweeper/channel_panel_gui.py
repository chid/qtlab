import pygtk
pygtk.require('2.0')
import gtk

class channel_panel:

    def change_increment(self, adj, set):
        set.set_step_increment(adj.get_value())
        set.set_page_increment(adj.get_value())

    def get_all_channels(self, adj, set):
        for i in range(0, len(self._channels)):
            set[i].set_value(self._channels[i].get_out())
            
    def set_channels(self, adj, i):
        if adj.get_value() < self._channels[i].get_maxval() and adj.get_value()> self._channels[i].get_minval():
            self._channels[i].set_out(adj.get_value())
        adj.set_value(self._channels[i].get_out())
        
    def __init__(self,channels):
        self._channels = channels
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("destroy", lambda w: gtk.main_quit())
        window.set_title("Channel Panel GUI")

        main_hbox = gtk.HBox(False, 5)
        main_hbox.set_border_width(10)
        window.add(main_hbox)
        adj = [[] for row in range(len(self._channels))] 
        adj2  = [[] for row in range(len(self._channels))]
        for i in range(0,len(self._channels)):
            frame = gtk.Frame(self._channels[i].get_name())
            main_hbox.pack_start(frame, True, True, 0)
      
            vbox = gtk.VBox(False, 0)
            vbox.set_border_width(5)
            frame.add(vbox)
            
            # channel spinners
     
            vbox2 = gtk.VBox(False, 0)
            vbox.pack_start(vbox2, True, True, 5)

            vbox3 = gtk.VBox(False, 0)
            vbox.pack_start(vbox3, True, True, 5)


            label = gtk.Label("SET :")
            label.set_alignment(0, 0.5)
            vbox2.pack_start(label, False, True, 0)

            adj[i] = gtk.Adjustment(0, self._channels[i].get_minval(), self._channels[i].get_maxval(),
                                    self._channels[i].get_maxval()/1000, 0.0, 0.0)
            spinner = gtk.SpinButton(adj[i], 0, 6)
            spinner.set_numeric(True)
            spinner.set_wrap(False)
            vbox2.pack_start(spinner, False, True, 0)
            adj[i].connect("value_changed", self.set_channels, i)

            label2 = gtk.Label("Increment :")
            label2.set_alignment(0, 0.5)
            vbox3.pack_start(label2, False, True, 0)

            adj2[i] = gtk.Adjustment(0, 0, 1, 0.001, 0.001, 0.0)
            spinner2 = gtk.SpinButton(adj2[i], 0, 6)
            spinner2.set_numeric(True)
            spinner2.set_wrap(False)
            vbox3.pack_start(spinner2, False, True, 0)
            adj2[i].connect("value_changed", self.change_increment, adj[i]) 

        button = gtk.Button("Get all")
        button.connect("clicked", self.get_all_channels, adj)
        self.get_all_channels(0, adj)
        main_hbox.pack_start(button, True, True, 5)
        
        window.show_all()
        

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    channel_panel([VSD, VG1, VG2, VG3])
    main()
        
        
        
