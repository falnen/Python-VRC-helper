import Layout
import Controller
from Osc import OSC_Listner
from VRC import Log_parser
import Persistence
import queue

'''
- T H E   P L A N -
      maybe.

done...PARAMETER AUTOFILL BUTTON!!!

STARTED, good enough- app configuration
DONE ----??? App colors?
----??? Manually enter avatar names&ID's vs get automatically from the parser?
IDK,----??? configure osc message collection?---???what is this mean....
Done ----??? toggle automatic avatar parameter colection?
DONE enough...-Next i think - controller configuration
DONE - select which avatar to use when creating a controller...
Done - fix sidebar
-Easy- configure log reader to only read logs from the current day, and skip to the current hour/some amount of time.
- Release 0.2?
- finish parameter filter
- enable parameter removal(delete unwanted parameters from the saved_avatars dict)
- log filtering
----??? Set playername manually vs get automatically from parser?
----??? configure whats picked up by the log parser?
- debug into log, and maybe file.
- release 0.3?
- Condition matching with messages from notifications.
- system events....
- release 0.4?
'''

frames = {} #Key = Layout.Object_list.insert('', 'end', text=tab_name) - Value = ttk.Frame object ID.

State = Persistence.Load_data()

def OSC_handler():
    '''
    Empties OSC message queue.\n
    Calls handler function on the controller with a matching avatar, and the 'universal' controller.\n
    Populates the saved_avatars dict with received avatar ID's and parameters.
    '''
    count = 0
    try:
        while count < 50:
            address, message = OSC_Listner.active_server.message_queue.get_nowait()
            if address == '/avatar/change' and message not in Controller.Tabi.saved_avatars.values() and Controller.Tabi.avatar_name_hold is not None:
                Controller.Tabi.saved_avatars[Controller.Tabi.avatar_name_hold] = [message,[]]
                assign_avatar_button(Controller.Tabi.avatar_name_hold)
                Controller.Tabi.avatar_name_hold = None
            Layout.Message_display(address,message,text='Received:')
            eController = frames.get(VRC_events.avatar) or frames.get('Universal')
            eController[1].handler(address=address,OSCmessage=message)
            if eController[1].controlled_avatar != 'Universal':
                frames.get('Universal')[1].handler(address=address,OSCmessage=message)
            if Layout.parameter_collect.get(): eController[1].custom_parameters(address)
            count +=1
        Layout.Root.after_idle(OSC_handler)
    except queue.Empty:
        Layout.Root.after(50,OSC_handler)
    
def VRC_handler(Event):
    '''
    handles.\n
    vrchat.\n
    log.\n
    events.\n
    inspect VRC.py for more details.
    '''
    Event_type = Event.get('Type')
    User = Event.get('User')
    Avatar = Event.get('Avatar')
    if Event_type == 'Local avatar':
        Controller.Tabi.avatar_name_hold = None
        if Avatar not in Controller.Tabi.saved_avatars.keys():
            Controller.Tabi.avatar_name_hold = Avatar
        else: return
    templates = {
        'Friend request': f'{Event_type} from {User}',
        'Group':  f'{Event_type}  message? from {User} at {Event.get('Timestamp')} : {Event.get('Message')}',
        'Invite': f'received to join {User} in world {Event.get('World')}',
        'Invite request':f'from {User}',
        'Avatar changed': f'to ( {Avatar} ) for user ( {User} )',
        'User left': f'{User}',
        'User joined': f'{User}',
        'Author': f'for avatar ( {Avatar} ) is ( {User} )',
        'User': f'Is {User}',
        'Local avatar': f'{Avatar} Added To Known avatars',
    }
    message = templates.get(Event_type,'err')
    Layout.Message_display(address=Event_type,message=message,text='Log event:')
    for fController in frames.values():
        if fController[1].Avatar.get() not in [VRC_events.avatar,'Universal']:continue
        fController[1].handler(address=Event_type,VRCevent=Event)

def VRC_watcher():
    '''periodically(currently every 500ms) attempts to read the latest vrchat log for new events'''
    # Unimplemented: 'old log' skipping logic
    #if not Layout.VRC_Toggle.get():
    #    Layout.Root.after_cancel(Layout.Root.after_info()[0])
    #    return
    if Nolog := VRC_events.Read_log():
        Layout.Message_display('No logs found.','retrying in 30 seconds...','Error:\n')
        delay = 30000
    else: delay = 500
    Layout.Root.after(delay,VRC_watcher)

def Create_controller(avatar):
    '''
    It creates controllers.\n
    '''
    Layout.menu_win.withdraw()
    tab_name = f'{avatar} Controller'
    item_id = Layout.Object_list.insert('', 'end', text=tab_name)
    new_frame = Controller.Tabi(Layout.TabSpace,controller_id=item_id,controlled_avatar=avatar,name=tab_name,destroy=Destroy_controller)
    frames[avatar] = (item_id,new_frame)
    new_frame.grid(row=0, column=0, sticky='nsew',padx=(0,4),pady=(4,4))
    Layout.Pages.grid_remove()
    Layout.menu_buttons[avatar].destroy()
    Layout.menu_buttons.pop(avatar)
    for frame in frames.values():
        frame[1].lower()
    try:
        Layout.Object_list.selection_set(item_id)
        new_frame.lift()
    except: pass

def Load_controllers(data):
    '''
    It loads controllers.
    '''
    for tab_name,Sticks in data.items():
        item_id = Layout.Object_list.insert('', 'end', text=tab_name)
        new_frame = Controller.Tabi(Layout.TabSpace,controller_id=item_id,controlled_avatar=data[tab_name]['Avatar'],name=tab_name,destroy=Destroy_controller)
        frames[data[tab_name]['Avatar']] = (item_id,new_frame)
        new_frame.grid(row=0, column=0, sticky='nsew',padx=(0,4),pady=(4,4))
        new_frame.Load(Sticks)
    for frame in frames.values():
        frame[1].lower()
        frame[1].grid_remove()
    try:
        Layout.Object_list.selection_set(item_id)
        new_frame.lift()
    except: pass

def Destroy_controller(avatar,remove_avatar=None):
    '''
    Does what it says on the tin.
    '''
    ControllerId = frames[avatar][0]
    prev_controller = Layout.Object_list.prev(ControllerId)
    Layout.Object_list.delete(ControllerId)
    if frames[avatar][1].winfo_exists():
        frames[avatar][1].destroy()
        frames.pop(avatar)
        if remove_avatar:
            Controller.Tabi.saved_avatars.pop(avatar)
            return
        assign_avatar_button(avatar)
    if prev_controller in frames:
        Layout.Object_list.selection_set(prev_controller)
        frames[prev_controller].grid()
        frames[prev_controller].lift()
    else: Settings_view()
    
def on_treeview_select(event):
    '''
    When selecting an item from the controller list, removes the current controller tab, and shows the selected controller tab.
    '''
    if selected_item := Layout.Object_list.selection():
        Layout.Pages.lower()
        Layout.Pages.grid_remove()
        item_id = selected_item[0]
        for frame in frames.values():
            frame[1].lower()
            frame[1].grid_remove()
            if frame[0] == item_id:
                frame[1].grid()
                frame[1].lift()

def Settings_view():
    '''
    Hides all controllers and shows the settings view.
    '''
    if not Layout.Pages.grid_info():
        Layout.Pages.grid()
        Layout.Pages.lift()
        for frame in frames.values():
            frame[1].lower()
            frame[1].grid_remove()

def assign_avatar_button(avatar):
    '''
    Assigns avatars to the dropdown that pops up when clicking "Add New Controller"
    '''
    used_avatars = [frame[1].Avatar.get() for frame in frames.values()]
    #unused_avatars = [avatar for avatar in Controller.Tabi.saved_avatars if avatar not in used_avatars]
    if avatar not in used_avatars:
        avatar_button = Layout.insert_avatar_button(avatar)
        avatar_button.configure(command=lambda avatar=avatar:Create_controller(avatar))

def manual_controller_helper():
    avatar = Layout.manual_name_entry.get()
    avatar_id = Layout.manual_id_entry.get()
    Controller.Tabi.saved_avatars[avatar] = [avatar_id,[]]
    assign_avatar_button(avatar)

def load_settings(settings):
    Layout.r_ipvar.set(settings['r_Ip'])
    Layout.r_portvar.set(settings['r_Port'])
    Layout.s_ipvar.set(settings['s_Ip'])
    Layout.s_portvar.set(settings['s_Port'])
    Layout.style.colors.set('primary', settings['Primary-color'])
    Layout.style.colors.set('secondary', settings['Secondary-color'])
    Layout.app_color_set('#000000',3)

def defocus(event):
    '''
    Work around.\n
    Enables clicking outside of an entry to remove focus from said entry.
    '''
    widget = event.widget
    #print(Layout.Root.winfo_viewable())
    try:
        class_name = widget.winfo_class()
        if Layout.menu_win.winfo_viewable() and str(Layout.menu_win) in str(widget):
            return
        Layout.menu_win.withdraw()
        if class_name not in ('Text','TButton','Treeview','TEntry','TCombobox','Radiobutton','Scrollbar','Spinbox','Listbox'):
            Layout.Root.focus_set()
    except:
        pass      

def reset_oscServer():
    '''
    Stops the OSC server.\n
    Starts the OSC server with new address & port values.
    '''
    if not Layout.r_ipvar.get():Layout.r_ipvar.set('127.0.0.1')
    if not Layout.s_ipvar.get():Layout.s_ipvar.set('127.0.0.1')
    OSC_Listner.active_server.stop_server()
    try:
        Layout.Root.after(1000,OSC_Listner.active_server.Start_server,Layout.r_ipvar.get(),Layout.r_portvar.get())
    except Exception as e:
        print(e)
        Layout.r_ipvar.set('127.0.0.7')
        Layout.r_portvar.set(9001)
        Layout.Message_display(address='',message=f'{e}\nInvalid IP or Port\nSetting values to default\n',text='Error: ')
        Layout.Root.after(1000,OSC_Listner.active_server.Start_server,Layout.r_ipvar.get(),Layout.r_portvar.get())

def OSC_mapall():
    match Layout.test_var.get():
        case True: OSC_Listner.active_server.Map_all()
        case False: OSC_Listner.active_server.unMap_all()
Layout.Root.bind_all("<Button-1>",defocus)
Layout.Settings_button.configure(command=Settings_view)
Layout.Object_list.bind("<<TreeviewSelect>>", on_treeview_select)
Layout.manual_button.configure(command=manual_controller_helper)
Layout.Server_set.configure(command=reset_oscServer)
#Layout.vrc_enable.configure(command=VRC_watcher)

OSC_Listner.active_server = OSC_Listner()

if State:# Loads previous app state from file, if it exists.
    if State.get('Avatar data'): Controller.Tabi.saved_avatars = State.get('Avatar data')
    load_settings(State.get('Settings'))
    Layout.Root.after(0,Load_controllers(State['Controllers']))
    for avatar in Controller.Tabi.saved_avatars.keys():
            assign_avatar_button(avatar)

OSC_Listner.active_server.Start_server(Layout.r_ipvar.get(),Layout.r_portvar.get())
VRC_events = Log_parser(VRC_handler)

Layout.Mapall_toggle.configure(command=OSC_mapall)
OSC_mapall()

Layout.Root.after(1000,OSC_handler)
Layout.Root.after(1000,VRC_watcher)
VRC_events.Find_user()

Layout.Root.protocol("WM_DELETE_WINDOW", lambda: (Persistence.save_state(frames), Layout.Root.destroy()))

if __name__ == "__main__":
    
    Layout.Root.mainloop()
