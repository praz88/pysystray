import utils

__all__ = ['Menu', 'MenuItem']


#TODO: find a mature OrderedDict implementation

class _odict(dict):
    def __init__(self):
        dict.__init__(self)
        self.ovalues = []

    def __setitem__(self, item, value):
        dict.__setitem__(self, item, value)
        self.ovalues.append(value)

    def values(self):
        return self.ovalues
        
        
class MenuBase(list):
    ''' Parent Class for both Menus and MenuItems 
    
        title and icon properties are implemented here.
    '''
    def __init__(self, name, title):
        list.__init__(self)
        self.append(title)
        self.append(None)
        self.append(utils.DEFAULT_HANDLER)
        self.name = name
        #if not name:
        #    self.name = title
        
    def __get_title(self):
        return self[0]
        
    def __set_title(self, t):
        self[0] = t
        return
        
    title = property(__get_title, __set_title, None, "Sets/Gets the Menu Title")
        
    def __get_icon(self):
        return self[1]
        
    def __set_icon(self, icon):
        self[1] = icon
        return
                
    icon = property(__get_icon, __set_icon, None, "Sets/Gets the menu icon")
    
    def get_tuple(self):
        return tuple(self)
        

        
class Menu(MenuBase): 
    ''' Creates a Menu instance.
    
        Menus can contain other menus or menuitems
    '''
    
    def __init__(self, name, title=''):
        MenuBase.__init__(self, name, title)
        self.menu = []
        self.items = _odict() #should be {}, using _odict() as ordered dict
        
    def add_item(self, i):
        self.menu.append(tuple(i))
        self.items[i.name] = i
        self[2] = self.menu
    
    def add_menuitem(self, m):
        ''' Add a MenuItem to a Menu'''
        self.add_item(m)
        
        
    def add_menu(self, m):
        ''' Add a Menu to a Menu (add a sub menu)'''
        self.add_item(m)
        
    def get_tuple(self):
        menu = []
        for m in self.items.values():
            menu.append(m.get_tuple())
            
        self[2] = menu
        return tuple(self)
        
        
class MenuRoot(Menu):        
    def __init__(self):
        Menu.__init__(self, '')
        
    def get_tuple(self):
        #print "getting menuroot"
        menu = Menu.get_tuple(self)
        menu[2]
        return tuple(menu[2])

class MenuItem(MenuBase):
    ''' Creates and instance of a MenuItem
    
        Can be added to Menus or the main App, and can have onclick handlers
    '''
    
    def __init__(self, name, title=''):
        MenuBase.__init__(self, name, title)
        
    def __get_onclick(self):
        return self[2]
        
    def __set_onclick(self, h):
        self[2] = h
        
    onclick = property(__get_onclick, __set_onclick, None, "Sets/Gets the onclick handler for the MenuItem")
        