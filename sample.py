#--------- systray sample ---------------
#from systray import systray
import systray
import time

mitem_txtchg = systray.MenuItem(title=' Change Text', name="chg_txt")

def txtchg_onclick(s):
    s.text = 'systray sample - ' + str(time.clock())  
    
mitem_txtchg.onclick = txtchg_onclick


menuitem_published = systray.MenuItem(name='pub_ico')
menuitem_published.icon = 'published.ico'

@systray.threaded
def menuitem_published_onclick(s):
    s.icon = 'published.ico'
    for i in xrange(0, 20000):
        time.sleep(1)
        print "looping ", i
    #print "quiting"
    #s.quit()
    
menuitem_published.onclick = menuitem_published_onclick

menuitem_default = systray.MenuItem(name='def_ico')
menuitem_default.icon = 'default.ico'

def menuitem_default_onclick(s):
    s.icon = 'default.ico'
    
menuitem_default.onclick = menuitem_default_onclick


menu_icon = systray.Menu(name='icon', title='Icon')
menu_icon.add_menuitem(menuitem_published)
menu_icon.add_menuitem(menuitem_default)

menuitem_hide = systray.MenuItem(name='hide', title="Hide")

def menuitem_hide_onclick(s):
    s.hide()
    print "I'm now Hidden"
    raw_input("Press Enter To Make Me Visible:")
    s.show()
    print "I'm now Visible"
    
menuitem_hide.onclick = menuitem_hide_onclick

menuitem_popup = systray.MenuItem(name='popup', title="PopUp")

def menuitem_popup_onclick(s):
    s.show_tooltip("Test Title", "Test")
    
menuitem_popup.onclick = menuitem_popup_onclick

menuitem_change_stuff = systray.MenuItem(name='chg_stuff', title=" Go Down")
menuitem_change_stuff.icon = 'default.ico'

def change_stuff(s):
    if s.menu.items['change'].items['chg_stuff'].icon == 'default.ico':
        s.menu.items['change'].items['chg_stuff'].icon = 'published.ico'
        s.menu.items['change'].items['chg_stuff'].title = ' Go Up'
    else:
        s.menu.items['change'].items['chg_stuff'].icon = 'default.ico'
        s.menu.items['change'].items['chg_stuff'].title = ' Go Down'
        
menuitem_change_stuff.onclick = change_stuff
        
menu_change = systray.Menu(name="change", title="Change Example")
menu_change.add_menuitem(menuitem_change_stuff)

def onload(s):
    s.icon = "published.ico"
    s.show_warning("We're soon going to stop working")


st_sample = systray.App('systray sample', 'default.ico')
st_sample.on_load = onload #we could implement a webserver here if we wanted :)
st_sample.add_menuitem(mitem_txtchg)
st_sample.add_menu(menu_icon)
st_sample.add_menuitem(menuitem_hide)
st_sample.add_menuitem(menuitem_popup)
st_sample.add_menu(menu_change)

st_sample.start()        