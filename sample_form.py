from Tkinter import * 
from systray import systray


def systray_dblclk_callback(s):
    s.show_warning("Hey!!! I don't like being double clicked. It tickles ;)")
    
def hide_callback(s):
    s.hide()
        



def build_systray_control():
    menu_item = systray.MenuItem(name="hide", title="Hide")
    menu_item.onclick = hide_callback

    control = systray.Control("Application Icon", "default.ico")
    control.on_double_click = systray_dblclk_callback
    control.add_menuitem(menu_item)

    return control
    

class Application(Frame): 
    def balloon_message(self):
        #self.systray.show_info("We're alive and well!")
        self.systray.show_message("A message")
        #self.systray.show_warning("A warning")
        #self.systray.show_error("An error... whoops!!!")
        
    def toggle_visibility(self): 
        if self.systray.visible:
            self.systray.hide()
        else:
            self.systray.show()

    def toggle_enable(self): 
            if self.systray.enabled:
                self.systray.disable()
            else:
                self.systray.enable()


    def createWidgets(self): 
        self.QUIT = Button(self) 
        self.QUIT["text"] = "QUIT" 
        self.QUIT["fg"] = "red" 
        self.QUIT["command"] = self.quit 
        self.QUIT.pack({"side": "left"}) 
        
        self.show_btn = Button(self) 
        self.show_btn["text"] = "Toggle Visibility"
        self.show_btn["command"] = self.toggle_visibility
        self.show_btn.pack({"side": "left"}) 
        
        self.enable_btn = Button(self) 
        self.enable_btn["text"] = "Enable / Disable"
        self.enable_btn["command"] = self.toggle_enable
        self.enable_btn.pack({"side": "left"}) 
        
        self.balloon = Button(self)
        self.balloon["text"] = "Balloon Tooltip"
        self.balloon["command"] = self.balloon_message
        self.balloon.pack({"side": "left"})
        
        

    def __init__(self, master=None): 
        Frame.__init__(self, master) 
        self.pack() 
        self.createWidgets() 
        
        self.systray = build_systray_control()
        self.systray.enable()
        
        
        
app = Application() 
app.mainloop() 
app.systray.disable() #call this anytime, to destroy the systray
