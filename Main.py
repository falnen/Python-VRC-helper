import Layout
import Controller
from Constants import READ_ONLY_PARAMETERS, CONTROLS_LIST
from Osc import OSC_Listner
from VRC import Log_parser
import Persistence
import queue

frames = {} #Key = f"Controller {len(Layout.Object_list.get_children()) + 1}" Value = ttk.Frame object ID.

State = Persistence.Load_data()

def OSC_handler():
    count = 0
    try:
        while count < 50:
            address, message = Server.message_queue.get_nowait()
            if address == '/avatar/change':
                if message not in Controller.Tabi.saved_avatars.values() and Controller.Tabi.avatar_name_hold is not None:
                    Controller.Tabi.saved_avatars[Controller.Tabi.avatar_name_hold] = [message,[]]
                    Controller.Tabi.avatar_name_hold = None
            # Temporary filter: Avoids log spam from movement
            if address not in ('/avatar/parameters/Upright','/avatar/parameters/AngularY','/avatar/parameters/Halo-b_Angle','/avatar/parameters/VelocityZ','/avatar/parameters/VelocityX','/avatar/parameters/VelocityY','/avatar/parameters/VelocityMagnitude','/avatar/parameters/averageTrackerBattery','/avatar/parameters/leftControllerBattery','/avatar/parameters/rightControllerBattery'):
                Layout.Message_display(address,message,text='Received:')
            for eController in frames.values():
                if eController.Avatar.get() not in [VRC_events.avatar,'Universal']:continue
                eController.custom_parameters(address)
                eController.handler(address=address,OSCmessage=message)
            count +=1
        Layout.Root.after_idle(OSC_handler)
    except queue.Empty:
        Layout.Root.after(50,OSC_handler)
    
def VRC_handler(Event):
    Event_type = Event.get('Type')
    User = Event.get('User')
    Avatar = Event.get('Avatar')
    if Event_type == 'Local avatar':
        Controller.Tabi.avatar_name_hold = None
        if Avatar not in Controller.Tabi.saved_avatars.keys():
            Controller.Tabi.avatar_name_hold = Avatar
            return
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
        if fController.Avatar.get() not in [VRC_events.avatar,'Universal']:continue
        fController.handler(address=Event_type,VRCevent=Event)

def VRC_watcher():
    # Unimplemented: 'old log' skipping logic
    if Nolog := VRC_events.Read_log():
        Layout.Message_display('No logs found.','retrying in 30 seconds...','Error:\n')
        delay = 30000
    else: delay = 500
    Layout.Root.after(delay,VRC_watcher)

def Create_controller(data = None):
    used_avatars = [frame.Avatar.get() for frame in frames.values()]
    unused_avatars = [avatar for avatar in Controller.Tabi.saved_avatars if avatar not in used_avatars]
    if data:
        for tab_name,Sticks in data.items():
            if tab_name in {'App version', 'Server', 'Avatar data'}:
                continue
            item_id = Layout.Object_list.insert('', 'end', text=tab_name)
            new_frame = Controller.Tabi(Layout.TabSpace,controller_id=item_id,controlled_avatar=data[tab_name]['Avatar'],name=tab_name,destroy=Destroy_controller)
            frames[item_id] = new_frame
            new_frame.grid(row=0, column=0, sticky='nsew',padx=(0,4),pady=(4,4))
            new_frame.Load(Sticks)
    else:
        if not len(unused_avatars) >=1:
            return
        tab_name = f'{unused_avatars[0]} Controller'
        item_id = Layout.Object_list.insert('', 'end', text=tab_name)
        new_frame = Controller.Tabi(Layout.TabSpace,controller_id=item_id,controlled_avatar=unused_avatars[0],name=tab_name,destroy=Destroy_controller)
        frames[item_id] = new_frame
        new_frame.grid(row=0, column=0, sticky='nsew',padx=(0,4),pady=(4,4))
        Layout.Configuration.grid_remove()

    for frame in frames.values():
        frame.lower()
    try:
        Layout.Object_list.selection_set(item_id)
        new_frame.lift()
    except:
        pass

def Destroy_controller(ControllerId):
    itemid = Layout.Object_list.prev(ControllerId)
    Layout.Object_list.delete(ControllerId)
    if frames[ControllerId].winfo_exists():
        frames[ControllerId].destroy()
        frames.pop(ControllerId)
    if itemid in frames:
            Layout.Object_list.selection_set(itemid)
            frames[itemid].grid()
            frames[itemid].lift()
    else: Settings_view()
            
def on_treeview_select(event):
    if selected_item := Layout.Object_list.selection():
        Layout.Configuration.lower()
        Layout.Configuration.grid_remove()
        item_id = selected_item[0]
        for frame in frames.values():
            frame.lower()
            frame.grid_remove()
        if item_id in frames:
            frames[item_id].grid()
            frames[item_id].lift()

def Settings_view():
    if not Layout.Configuration.grid_info():
        Layout.Configuration.grid()
        Layout.Configuration.lift()
        for frame in frames.values():
            frame.lower()
            frame.grid_remove()

def defocus(event):
    widget = event.widget
    try:
        class_name = widget.winfo_class()
        if class_name not in ('Text','Button','Treeview','TEntry','TCombobox','Radiobutton','Scrollbar','Spinbox','Listbox'):
            Layout.Root.focus_set()
    except:
        pass      

Layout.Root.bind_all("<Button-1>",defocus)
Layout.Settings_button.configure(command=Settings_view)
Layout.Add_Tab.configure(command=Create_controller)
Layout.Object_list.bind("<<TreeviewSelect>>", on_treeview_select)

Server = OSC_Listner()
Server.Start_server(Layout.Ip_entry.get(),Layout.Port_entry.get())
VRC_events = Log_parser(VRC_handler)

Layout.Root.after(1000,OSC_handler)
Layout.Root.after(1000,VRC_watcher)
VRC_events.Find_user()
if State:
    if State.get('Avatar data'): Controller.Tabi.saved_avatars = State.get('Avatar data')
    Layout.Root.after(0,Create_controller(State))

Layout.Root.protocol("WM_DELETE_WINDOW", lambda: (Persistence.save_state(frames), Layout.Root.destroy()))

if __name__ == "__main__":
    
    Layout.Root.mainloop()
