from systray import systray
from systray import menu


menu_item1 = systray.MenuItem(title="Menu Item 1", name="menuitem1")
#menu_item1.icon = "default.ico"

menu_item2 = systray.MenuItem(title="Menu Item 2", name="menuitem2")
#menu_item2.icon = "default.ico"

def handler1(s):
    pass
    
#menu_item1.on_click = handler1


menu1 = systray.Menu(title="Menu 1", name="menu1")
menu1.add_menuitem(menu_item1)
menu1.add_menuitem(menu_item2)

menu2 = systray.Menu(title="Menu 2", name="menu2")
menu2.add_menu(menu1)
menu2.add_menuitem(menu_item1)

print "menuitem1 = ", menu_item1.get_tuple()
print "menu1 = ", menu1.get_tuple()
#menu2.items['menu1'].items['menuitem1'].icon = "published.ico"
print "menu2 = ", menu2.get_tuple()

menuroot = menu.MenuRoot()
menuroot.add_menu(menu2)
menuroot.add_menu(menu1)
print "menuroot = ", menuroot.get_tuple()
