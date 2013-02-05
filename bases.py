import sys
import win32gui
import win32con
import thread
import SysTrayIcon

import menu
import utils

__all__ = ['AppBase']




class _App(SysTrayIcon.SysTrayIcon):
    ''' Inherits SysTrayIcon and adds usefull properties and extentions '''
    
    #TODO: add support for on_load event and pop up notifier window
    def __init__(self, title, icon, menu, on_load=None, on_quit=None, on_double_click=None):            
        self.title = title
        self.menu = menu
        self.on_double_click = on_double_click
        SysTrayIcon.SysTrayIcon.__init__(self, icon, self.title, 
            self.menu.get_tuple(), on_load, on_quit, self.title, behave_traditional=False) #using self.title as windows_class_name
        self.visible = True
        self.alive = True

                
    def do_onload(self):
        win32gui.SendMessage(self.hwnd, self.WM_ONLOAD, self._get_quit_id(), win32con.WM_LBUTTONUP)
        
    def quit(self):
        win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, self._get_quit_id(), win32con.WM_LBUTTONUP)        
        self.visible = False

    def _get_quit_id(self):
        for k, v in self.menu_actions_by_id.items():
            if v == self.QUIT:
                return k
    
    def show_menu(self):
        #print "showing menu"
        self._prepare_menu(self.menu.get_tuple(), 0)
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        #win32gui.SetMenuDefaultItem(menu, 1000, 0)
        
        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu, 
                                win32con.TPM_LEFTALIGN, 
                                pos[0], 
                                pos[1], 
                                0, 
                                self.hwnd, 
                                None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
                
    def show_tooltip(self, title, text, timeout=1, icon=win32gui.NIIF_INFO):
        if self.visible:
            self.notify_icon.show_balloon_tooltip(title, text, icon, timeout)
            
    def show(self):
        if not self.visible:
#            nid = (self.hwnd, 0)
#            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
#            self.refresh_icon()
            self.notify_icon.show()
            self.visible = True
        
    def hide(self):
        if self.visible:
#            nid = (self.hwnd, 0)
#            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
            self.notify_icon.hide()
            self.visible = False

    #overloaded message handler for WM_DESTROY
    def destroy(self, hwnd, msg, wparam, lparam):
        if self.on_quit: self.on_quit(self)
        self.hide()
        win32gui.PostQuitMessage(0) # Terminate the app.
        self.alive = False

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONDBLCLK:
            #allow setting custom dbclick callback
            if callable(self.on_double_click):
                self.on_double_click(self)
                #self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
            pass
        elif lparam==win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam==win32con.WM_LBUTTONUP:
            pass
        return True

            
    def __set_text(self, s):
        self.hover_text = s
        self.refresh_icon()
        
    def __get_text(self):
        return self.hover_text
        
    text = property(__get_text, __set_text, None, "Text Shown On Mouse Hover")
    
    def __set_icon(self, s):
        self._icon = s
        self.refresh_icon()
    
    def __get_icon(self):
        return self._icon
        
    icon = property(__get_icon, __set_icon, None, "The Icon Shown on the tool bar")
    
    #TODO: make this guy pop up like Yahoo, but semitransparent and cool like outlook messages
    def set_status(self, message=None, icon=None):
        if message is not None:
            self.text = self.title + ' - ' + str(message)
            
        if icon is not None:
            try:
                self.icon = icon
            except:
                #do nothing just let it go for now
                #TODO: Raise and _App.Error('Invalid Icon File')
                pass
    
    def show_info(self, message):
        #win32gui.MessageBox(self.hwnd, str(message), self.title, win32con.MB_ICONINFORMATION)
        self.show_tooltip(self.title, str(message), icon=win32gui.NIIF_INFO)
        
    def show_warning(self, message):
        self.show_alert(message)
        
    #TODO: Deprecate This
    def show_alert(self, message):
        #win32gui.MessageBox(self.hwnd, str(message), self.title, win32con.MB_ICONERROR)
        self.show_tooltip(self.title, str(message), icon=win32gui.NIIF_WARNING)
        
    def show_error(self, message):
        self.show_tooltip(self.title, str(message), icon=win32gui.NIIF_ERROR)
        
    def show_message(self, message):
        self.show_tooltip(self.title, str(message), icon=win32gui.NIIF_NONE)
        
        
        
class AppBase(object):
    ''' Creates an instance of a System Tray Application. Call start() to run it '''
    
    def __init__(self, title, icon=None):
        self.icon = icon
        self.title = title
        self._on_quit = utils.DEFAULT_HANDLER
        self._on_load = utils.DEFAULT_HANDLER
        self._on_double_click = utils.DEFAULT_HANDLER
        self.menu = []
        self.nmenu = menu.MenuRoot()
        #self.systray = _App(title, icon, tuple([]))
        #self.default_menu_index = 0        
    
    def _start(self):
        #print "menu = ", self.menu
        #print "nemu = ", self.nmenu.get_tuple()
        #sys.exit(0)
        self.systray = _App(self.title, self.icon, self.nmenu , on_quit=self.on_quit, on_load=self.on_load, on_double_click=self.on_double_click)
        self.systray.do_onload()
        win32gui.PumpMessages()
        
    @utils.threaded
    def _start_control(self):
        self._start()
              
    def _stop(self):
        self.systray.quit()
               
    def add_menuitem(self, m):
        ''' Adds a menu item to the Application.
        
            Menu Items can't contain submenus
        '''
        self.menu.append(tuple(m))
        self.nmenu.add_menuitem(m)
        #print tuple(self.menu)
        return
        
    #TODO: implement type checking here and at add_menuitem, probably use decorators
    def add_menu(self, m):
        ''' Adds a Menu to the Application.
        
            Menus don't have onclick handlers, and can have attached submenus.
        '''
        self.menu.append(tuple(m))
        self.nmenu.add_menu(m)
        
    def __get_on_load(self):
        return self._on_load
        
    def __set_on_load(self, handler):
        self._on_load = handler
        
    def __del_on_load(self):
        self._on_load = None
        
    on_load = property(__get_on_load, __set_on_load, __del_on_load, "Sets/Gets the application ON_LOAD event handler, which is run when the app starts.")
    
    def __get_on_quit(self):
        return self._on_quit
        
    def __set_on_quit(self, handler):
        self._on_quit = handler
        
    def __del_on_quit(self):
        self._on_quit = None
        
    on_quit = property(__get_on_quit, __set_on_quit, __del_on_quit, "Sets/Gets the application ON_QUIT event handler")

    def __get_on_dblclk(self):
        return self._on_double_click
        
    def __set_on_dblclk(self, handler):
        self._on_double_click = handler
        
    def __del_on_dblclk(self):
        self._on_double_click = None
        
    on_double_click = property(__get_on_dblclk, __set_on_dblclk, __del_on_dblclk, "Sets/Gets the application ON_DOUBLE_CLICK event handler")

    def __get_visibility(self):
        return self.systray.visible
        
    def __set_visibility(self, v):
        self.systray.visible = v
                
    visible = property(__get_visibility, __set_visibility, None, "Sets/Gets the visibility")
        

