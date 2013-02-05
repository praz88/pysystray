#!/usr/bin/env python
# Module     : SysTrayIcon.py
# Synopsis   : Windows System tray icon.
# Programmer : Simon Brunning - simon@brunningonline.net
# Date       : 11 April 2005
# Notes      : Based on (i.e. ripped off from) Mark Hammond's
#              win32gui_taskbar.py and win32gui_menu.py demos from PyWin32
'''TODO

For now, the demo at the bottom shows how to use it...'''
         
import os
import sys
import win32api
import win32con
import win32gui_struct
try:
    import winxpgui as win32gui
except ImportError:
    import win32gui

import winutils

class SysTrayIcon(object):
    '''TODO'''
    #TODO: move into local method namespaces. No need to be global really
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]
    
    FIRST_ID = 1023
    
    def __init__(self, 
                 icon, 
                 hover_text, 
                 menu_options,
                 on_load=None,
                 on_quit=None,
                 default_menu_index=None, 
                 window_class_name=None,
                 behave_traditional=True):
        
        self._icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit
        self.on_load_method = on_load
                
        #print "menu_options = ", menu_options 
        #for menu in menu_options:
        #    print "menu = ", menu
        
        self._prepare_menu(menu_options, default_menu_index)
        
        message_map = self._build_message_map()                       
        #Register n Create the Window class.
        self.register_window_class(message_map, window_class_name)
        # Create the Window.
        self.window_style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU        
        #TODO: refactor into win worker utils library
        self.create_window(self.window_style)                

        self.notify_icon = winutils.NotifyIcon(hwnd=self.hwnd, callback_message=win32con.WM_USER+20)
        #self.notify_id = None
        self.refresh_icon()
        
        if behave_traditional:
            win32gui.PumpMessages()
            

    def _add_ids_to_menu_options(self, menu_options):
        result = []
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                result.append(menu_option + (self._next_action_id,))
            elif non_string_iterable(option_action):
                result.append((option_text, 
                               option_icon, 
                               self._add_ids_to_menu_options(option_action), 
                               self._next_action_id))
            else:
                #print 'Unknown item', option_text, option_icon, option_action
                pass
            self._next_action_id += 1
        return result

    def _prepare_menu(self, menu_options, default_menu_index=None):
        #prepare menu
        menu_options = menu_options + (('Quit', None, self.QUIT),)
        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options))
        #self.menu = self.menu_options
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id                
        self.default_menu_index = (default_menu_index or 0)

    def _build_message_map(self):
        #set message map
        #TODO: move these into systray.constants
        self.WM_ONLOAD = win32gui.RegisterWindowMessage("SystrayOnLoad")
        self.WM_CREATED = win32gui.RegisterWindowMessage("TaskbarCreated")
        
        message_map = {self.WM_CREATED : self.restart, 
                       self.WM_ONLOAD: self.on_load,
                       win32con.WM_DESTROY: self.destroy, 
                       win32con.WM_COMMAND: self.command,
                       win32con.WM_USER+20 : self.notify 
                       }
                       
        return message_map

    def register_window_class(self, message_map, window_class_name=None):
        #self.window_class_name = window_class_name or "SysTrayIconPy"                
        self.window_class = win32gui.WNDCLASS()
        self.window_class.hInstance = win32gui.GetModuleHandle(None)
        self.window_class.lpszClassName = window_class_name or "SysTrayIconPy"        #self.window_class_name
        self.window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW;
        self.window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        self.window_class.hbrBackground = win32con.COLOR_WINDOW
        self.window_class.lpfnWndProc = message_map # could also specify a wndproc.        
        self.classAtom = win32gui.RegisterClass(self.window_class)
        #return tuple of classAtom and window_class? hinst? that can be used in UnregisterWindowclass
        
    def create_window(self, style):
        #self.style = style
        self.hwnd = win32gui.CreateWindow(self.classAtom, 
                                          self.window_class.lpszClassName, #self.window_class_name, 
                                          style, 
                                          0, 
                                          0, 
                                          win32con.CW_USEDEFAULT, 
                                          win32con.CW_USEDEFAULT, 
                                          0, 
                                          0, 
                                          self.window_class.hInstance, #hinst, 
                                          None)
        win32gui.UpdateWindow(self.hwnd)
        
        
        
    def refresh_icon(self):
        # Try and find a custom icon
        #hinst = win32gui.GetModuleHandle(None)
        #TODO: also put this in NotifyIcon class
        if os.path.isfile(self._icon):
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            self.hicon = win32gui.LoadImage(self.window_class.hInstance, #hinst, 
                                       self._icon, 
                                       win32con.IMAGE_ICON, 
                                       0, 
                                       0, 
                                       icon_flags)
        else:
            self.hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        self.notify_icon.hicon = self.hicon
        self.notify_icon.tooltip = self.hover_text
        self.notify_icon.show()


    def on_load(self, hwnd, msg, wparam, lparam):
        if callable(self.on_load_method):
            self.on_load_method(self)
            
    def restart(self, hwnd, msg, wparam, lparam):
        self.refresh_icon()

    def destroy(self, hwnd, msg, wparam, lparam):
        if self.on_quit: 
            self.on_quit(self)
            
        self.notify_icon.hide()
        win32gui.PostQuitMessage(0) # Terminate the app.

    def notify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONDBLCLK:
            #allow setting custom dbclick callback
            self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
            pass
        elif lparam==win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam==win32con.WM_LBUTTONUP:
            pass
        return True
        
    def show_menu(self):
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
    
    def create_menu(self, menu, menu_options):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)
            
            if option_id in self.menu_actions_by_id:                
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text, 
                                                                hbmpItem=option_icon, 
                                                                wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = win32gui_struct.PackMENUITEMINFO(text=option_text, 
                                                                hbmpItem=option_icon, 
                                                                hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(self, icon):
        # First load the icon.
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hdcScreen = win32gui.GetDC(0)
        hbm = win32gui.CreateCompatibleBitmap(hdcScreen, ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # Fill the background.
        brush = win32gui.GetSysColorBrush(win32con.COLOR_MENU)
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), brush)
        # unclear if brush needs to be feed.  Best clue I can find is:
        # "GetSysColorBrush returns a cached brush instead of allocating a new
        # one." - implies no DeleteObject
        # draw the icon
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)
        
        return hbm

    def command(self, hwnd, msg, wparam, lparam):
        id = win32gui.LOWORD(wparam)
        self.execute_menu_option(id)
        
        
    def execute_menu_option(self, id):
        menu_action = self.menu_actions_by_id[id]      
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
            win32gui.UnregisterClass(self.classAtom, self.window_class.hInstance)
        else:
            menu_action(self)
            
   
    
            
def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, basestring)

# Minimal self test. You'll need a bunch of ICO files in the current working
# directory in order for this to work...
if __name__ == '__main__':
    import itertools, glob
    
    icons = itertools.cycle(glob.glob('*.ico'))
    hover_text = "SysTrayIcon.py Demo"
    def hello(sysTrayIcon): print "Hello World."
    def simon(sysTrayIcon): print "Hello Simon."
    def switch_icon(sysTrayIcon):
        sysTrayIcon._icon = icons.next()
        sysTrayIcon.refresh_icon()
        
    menu_options = (('Say Hello', icons.next(), hello),('Switch Icon', None, switch_icon), ('A sub-menu', icons.next(), (('Say Hello to Simon', icons.next(), simon), ('Switch Icon', icons.next(), switch_icon), )))
    #menu_options = (('hi', 'ok.ico', ), ('lo', None, hello))

    def bye(sysTrayIcon):
        print 'Bye, then.'
    
    SysTrayIcon(icons.next(), hover_text, menu_options, on_quit=bye, default_menu_index=1)

