#!/usr/bin/python3
# -*- coding: utf-8 -*-
import gi
gi.require_versions({'Gtk': '3.0', 'Gdk': '3.0'})
from gi.repository import Gtk, Gdk
from subprocess import check_output, call

contents = check_output("amixer contents", shell = True).decode()
contents_list = contents.splitlines()
name_list = []

CSS = """
scale {
    padding-top: 12px;
    padding-bottom: 4px;
    border: 1px inset #ccc;
}
slider{
    margin: 1px;
    border: 3px outset #ddd;
    background: #bdcdf8;
}
#mylabel {
    color: #354f6d;
    font-weight: bold;
    font-size: 9pt;
}
window {
    background: #f7f7f7;
}
label {
    font-size: 8pt;
}
"""


for x in range(len(contents_list)):
    line = contents_list[x]
    if "Playback Volume" in line:
        name = line.split(",name='")[1].split("'")[0]
        if not "Mic Playback" in name:
            name_list.append(name)
        
#print('\n'.join(name_list))

class Scale(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title = "AlsaMixerGUI")
        
        # style
        provider = Gtk.CssProvider()
        provider.load_from_data(bytes(CSS.encode()))
        style = self.get_style_context()
        screen = Gdk.Screen.get_default()
        priority = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        style.add_provider_for_screen(screen, provider, priority)
        
        self.set_icon_name("audio-volume-high")
        self.vbox = Gtk.VBox(homogeneous = False)
        self.hbox_sliders = Gtk.HBox(vexpand = True, margin_top = 20)
        self.hbox_names = Gtk.HBox(homogeneous = True, vexpand = False,  margin_bottom = 20)
        self.vbox.pack_start(self.hbox_sliders, 0, 1, 4)
        self.vbox.pack_start(self.hbox_names, 0, 0, 0)
        self.create_sliders()
        self.scroll_area = Gtk.ScrolledWindow()
        self.scroll_area.add(self.vbox)
        self.add(self.scroll_area)
        self.set_default_size(700, 320)
        self.connect("destroy", Gtk.main_quit)
        self.move(0, 0)
        
    def create_sliders(self, *args):
        for i in range(len(name_list)):
            name = name_list[i]
            print(name, i)
            
            label = Gtk.Label(label = name.split(" ")[0], name = "mylabel")
            label.set_alignment(1, 0)
            label.set_vexpand(False)
            label.set_hexpand(True)
            self.hbox_names.pack_start(label, 0, 0, 22)
            
            scale = Gtk.Scale.new_with_range(Gtk.Orientation.VERTICAL, 0, 100, 0.5)
            scale.set_digits(0)
            scale.set_value_pos(Gtk.PositionType.BOTTOM)
            scale.set_vexpand(False)
            scale.set_hexpand(True)
            scale.set_inverted(True)
            for x in range(0, 101, 10):
                scale.add_mark(x, 0, str(x))
            for x in range(5, 100, 10):
                scale.add_mark(x, 1, str(x))
            scale.connect("value-changed", self.item_activated, i)
            self.hbox_sliders.pack_start(scale, 0, 0, 22)
            try:
                value = check_output(f"amixer get {name.split(' ')[0]}", shell=True).decode().partition("[")[2].partition("%")[0]
                print(value)
                scale.set_value(int(value))
            except:
                return
            
                
    def item_activated(self, wdg, i):
        value = wdg.get_value()
        print(value)
        call(f'amixer -c 0 cset iface=MIXER,name="{name_list[i]}" {value}%', shell=True)


if __name__ == "__main__":        
    window = Scale()
    window.show_all()

    Gtk.main()