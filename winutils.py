#loose collection of utilities to make working with win32api for this project 
#easier. We don't pretend to be what we're not right now.

import win32gui
import win32con

class NotifyIcon(object):
    def __init__(self, hwnd=None, hicon=None, callback_message=None, tooltip="Default"):
        self.hwnd = hwnd
        self.hicon = hicon
        self.callback_message = callback_message
        self.id = 0
        self.tooltip = tooltip
        self.__alive = False
        
    def __is_good(self):
        if self.hwnd and self.hicon and self.callback_message:
            return True
        else:
            return False
            
    def _build_nid_default(self):
        if self.__is_good():
            return (
                self.hwnd, 
                self.id, 
                win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP, 
                self.callback_message, 
                self.hicon, 
                self.tooltip
                )
            
    def show(self):
        nid = self._build_nid_default()
        if self.__alive:
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
        else:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
            self.__alive = True
            
    def hide(self):
        nid = self._build_nid_default()
        if self.__alive:
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
            self.__alive = False
        else:
            #do nothing
            pass

    def _build_nid_ballon_tooltip(self, title, message, icon, timeout):
        if self.__is_good():
            return (
                self.hwnd, 
                self.id, 
                win32gui.NIF_MESSAGE | win32gui.NIF_ICON | win32gui.NIF_TIP | win32gui.NIF_INFO, 
                self.callback_message, 
                self.hicon, 
                self.tooltip,
                message, 
                timeout, 
                title, 
                icon)
                
    def show_balloon_tooltip(self, title, message, icon=win32gui.NIIF_INFO, timeout=10):
        nid = self._build_nid_ballon_tooltip(title, message, icon, timeout)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)        