import Layout
from Controller import Tabi
from Osc import OSC_Listner,OSC_client
from VRC import Log_parser
import Persistence
import queue
import VRC

'''
- T H E   P L A N -
      maybe.

Add 'test' button to controllers to send a test OSC message.
go over ai implemented theme feature.
allow popout message display log window.
consider converting expression widget to a text box for multi-line expressions.
consider also allowing expression widget to popout.
consider the difference between using ttk var vs reading directly from the widget.
reconsider UI design of 'compound' osc events.
Update 'saved avatars' parameters with details from 'Avatar_info_from_file'

Add option to hide unwanted parameters.
done :o ! -Event address change handling needs a custom function within Eventi.

well... it does...- Eventi trigger changing needs to remap address
redesign avatar menu
done, hopefully. - think of a way to make duplicate events unique for saving to json
rethink oscmappall toggle

done...PARAMETER AUTOFILL BUTTON!!!
not needed? manual player name entry
done...add avatar matching by ID from OSC, in addition to Name from Log.
STARTED, partially reverted, rethink.- app configuration
DONE ----??? App colors?
DONE ----??? Manually enter avatar names&ID's vs get automatically from the parser?
IDK,----??? configure osc message collection?---???what is this mean....
Done ----??? toggle automatic avatar parameter colection?
DONE enough...-Next i think - controller configuration
DONE - select which avatar to use when creating a controller...
Done - fix sidebar
-Easy- configure log reader to only read logs from the current day, and skip to the current hour/some amount of time.
- finish parameter filter
done - enable parameter removal(delete unwanted parameters from the saved_avatars dict)
- avatar / parameter blacklist
kinda? - log filtering
----??? configure whats picked up by the log parser?
- debug into log, and maybe file.
- Condition matching with messages from notifications.
- system events....
'''
frames: dict[str,tuple[str,object]] = {} 
'''
Key = An Avatar Name\n
Value = [ttk.Treeview item id, ttk.Frame object id]\n
Generated in 'Create_controller' and 'Load_controller' in Main.
''' 
State = Persistence.Load_data()
Avatar_info_from_file = VRC.Build_avatar_list()

def match_avatar_id_with_name(avatar_id):
    '''
    Attempts to match an avatar id received from OSC with a known name. Then assigns that name to Tabi.current_avatar\n
    Tries matching from OSC .json files first,\n
    Then tries matching from VRC log, if enabled.\n
    Finally tries matching from the saved_avatars dict.\n
    Matching from the saved_avatars dict is a fallback, and not likely to produce a result unless the user input the avatar name and id manually.
    '''
    avatar_info = Avatar_info_from_file.get(avatar_id)
    print(avatar_info)
    if avatar_info:
        if avatar_info[0] not in Tabi.saved_avatars.keys():
            Tabi.saved_avatars[avatar_info[0]] = [avatar_id,avatar_info[1]]
            if Tabi.avatar_name_hold: Tabi.avatar_name_hold = None
            assign_avatar_button(avatar_info[0])
        Tabi.current_avatar = avatar_info[0]
    elif Layout.VRC_Toggle.get() and Tabi.avatar_name_hold is not None:
        Tabi.saved_avatars[Tabi.avatar_name_hold] = [avatar_id,[]]
        Tabi.current_avatar = Tabi.avatar_name_hold
        assign_avatar_button(Tabi.avatar_name_hold)
        Tabi.avatar_name_hold = None
    elif not Layout.VRC_Toggle.get():
        if avatar_id not in [why[0] for why in Tabi.saved_avatars.values()]: return
        for avatar_name,avatar_id in Tabi.saved_avatars.items():
            if avatar_id[0] != avatar_id: continue
            Tabi.current_avatar = avatar_name
            break
    else: return

def OSC_handler():
    '''
    Empties OSC message queue.\n
    Calls handler function on the controller with a matching avatar, and the 'universal' controller.
    '''
    count = 0
    try:
        while count < 50:
            address, message = OSC_Listner.active_server.message_queue.get_nowait()
            if address == '/avatar/change': match_avatar_id_with_name(message)
            if Layout.logvar_1.get(): Layout.Message_display(address,message,text='Received:')
            eController = frames.get(Tabi.current_avatar)
            if eController:
                eController[1].handler(address=address,OSCmessage=message)
                frames.get('Universal')[1].handler(address=address,OSCmessage=message)
            else:
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
        Tabi.avatar_name_hold = None
        Tabi.current_avatar = Avatar
        if Avatar not in Tabi.saved_avatars.keys():
            Tabi.avatar_name_hold = Avatar
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
        'Local avatar': f'{Avatar} added to known avatars',
    }
    message = templates.get(Event_type,'err')
    Layout.Message_display(address=Event_type,message=message,text='Log event:')
    for fController in frames.values():
        if fController[1].Avatar.get() not in [Tabi.current_avatar,'Universal']:continue
        fController[1].handler(address=Event_type,VRCevent=Event)

def VRC_watcher():
    '''periodically(currently every 500ms) attempts to read the latest vrchat log for new events'''
    # TODO: 'old log' skipping logic
    if not VRC_events.Local_user: VRC_events.Find_user()
    #print(VRC_events.user_id)
    if Nolog := VRC_events.Read_log():
        Layout.Message_display('No logs found.','retrying in 30 seconds...','Error:\n')
        delay = 30000
    else: delay = 500
    if Layout.VRC_Toggle.get(): Layout.Root.after(delay,VRC_watcher)

def Create_controller(avatar):
    '''
    It creates controllers.\n
    '''
    tab_name = f'{avatar} Controller'
    item_id = Layout.Object_list.insert('', 'end', text=tab_name)
    new_frame = Tabi(Layout.TabSpace,controller_id=item_id,controlled_avatar=avatar,name=tab_name,destroy=Destroy_controller)
    frames[avatar] = (item_id,new_frame)
    new_frame.grid(row=0, column=0, sticky='nsew',padx=(0,4),pady=(4,4))
    Layout.Pages.grid_remove()
    Layout.menu_buttons[avatar].destroy()
    Layout.menu_buttons.pop(avatar)
    for frame in frames.values():
        frame[1].lower()
        frame[1].grid_remove()
    try:
        Layout.Object_list.selection_set(item_id)
        new_frame.grid()
        new_frame.lift()
    except: pass

def Load_controllers(data):
    '''
    It loads controllers.
    '''
    for tab_name,Sticks in data.items():
        item_id = Layout.Object_list.insert('', 'end', text=tab_name)
        new_frame = Tabi(Layout.TabSpace,controller_id=item_id,controlled_avatar=data[tab_name]['Avatar'],name=tab_name,destroy=Destroy_controller)
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
    prev_controller_id = Layout.Object_list.prev(ControllerId)
    prev_controller_avatar = None
    if len(Layout.Object_list.get_children()) == 1: return
    Layout.Object_list.delete(ControllerId)
    if frames[avatar][1].winfo_exists():
        frames[avatar][1].destroy()
        frames.pop(avatar)
        if remove_avatar and avatar != 'Universal': Tabi.saved_avatars.pop(avatar)
        else: assign_avatar_button(avatar)
    for avatar_name,frame_id in frames.items():
        if prev_controller_id != frame_id[0]: continue
        prev_controller_avatar = avatar_name
        break
    if prev_controller_avatar:
        Layout.Object_list.selection_set(prev_controller_id)
        frames[prev_controller_avatar][1].grid()
        frames[prev_controller_avatar][1].lift()
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
    if avatar not in used_avatars:
        if  avatar_button := Layout.insert_avatar_button(avatar): avatar_button.configure(command=lambda avatar=avatar:Create_controller(avatar))

def manual_controller_helper():
    avatar = Layout.manual_name_entry.get()
    avatar_id = Layout.manual_id_entry.get()
    Tabi.saved_avatars[avatar] = [avatar_id,[]]
    assign_avatar_button(avatar)

def load_settings(settings):
    Layout.r_ipvar.set(settings['r_Ip'])
    Layout.r_portvar.set(settings['r_Port'])
    Layout.s_ipvar.set(settings['s_Ip'])
    Layout.s_portvar.set(settings['s_Port'])
    Layout.logvar_1.set(settings['Log_received'])
    Layout.logvar_2.set(settings['Log_sent'])
 
    Layout.style.colors.set('primary', settings.get('Primary-color'))
    Layout.style.colors.set('secondary', settings.get('Secondary-color'))
    # reapply widget configs and force builder update after setting colors
    # try theme-manager apply which registers a temporary theme
    try:
        Layout.theme_manager.apply_colors()
        Layout.theme_manager.refresh_widgets()
        Layout.style_widgets()
    except Exception as e: Layout.Message_display(text='Theme error :', address ='', message= e)


def defocus(event):
    '''
    Work around.\n
    Enables clicking outside of focusable widgets to remove focus from focusable widgets.
    '''
    widget = event.widget
    try:
        class_name = widget.winfo_class()
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
        for econtroller in frames.values(): econtroller[1].resetclient()
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
Layout.Mapall_toggle.configure(command=OSC_mapall)
Layout.vrc_enable.configure(command=VRC_watcher)

OSC_Listner.active_server = OSC_Listner()
VRC_events = Log_parser(VRC_handler)

if State:# Loads previous app state from file, if it exists.
    if State.get('Avatar data'): Tabi.saved_avatars = State['Avatar data']
    load_settings(State['Settings'])
    if State.get('Controllers'): Layout.Root.after(0,Load_controllers(State['Controllers']))
    for avatar in Tabi.saved_avatars.keys():

        assign_avatar_button(avatar)
else:
    assign_avatar_button('Universal')
    Layout.Root.after(0,Create_controller('Universal'))

OSC_Listner.active_server.Start_server(Layout.r_ipvar.get(),Layout.r_portvar.get())
OSC_Listner.active_server.Map_address('/avatar/change') #Required for avatar matching via ID when VRC log parsing is dissabled.

OSC_mapall()
OSC_handler()
VRC_watcher()

Layout.Root.protocol("WM_DELETE_WINDOW", lambda: (Persistence.save_state(frames), Layout.Root.destroy()))

if __name__ == "__main__":
    
    Layout.Root.mainloop()
