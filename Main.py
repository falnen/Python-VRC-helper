import Layout
import Controller
import Persistence
from Osc import OSC_Listner
from VRC import Log_parser
import queue

frames = {} #Key = f"Controller {len(Layout.Object_list.get_children()) + 1}" Value = Ttk.frame object ID.

State = Persistence.Load_data()
used_avatars = []


def Server_handler():
    count = 0
    try:
        while count < 30:
            address, message = Server.message_queue.get_nowait()
            Message_display(address,message,text='Received:')
            for Controller in frames.values():
                Controller.handler(address=address,OSCmessage=message)
            count +=1
        Message_display('Message rate exceding capacity!\n','\nPausing for UI Updates...\n',text='\nWarning :')
        Layout.Root.after_idle(Server_handler)
    except queue.Empty:
        Layout.Root.after(50,Server_handler)
    
def VRC_handler(Event):
    Event_type = Event.get('Type')
    User = Event.get('User')
    Avatar = Event.get('Avatar')
    templates = {
        'friendRequest': f'{Event_type} from {User}',
        'group':  f'{Event_type}  message? from {User} at {Event.get('Timestamp')} : {Event.get('Message')}',
        'invite': f'Received to join {User} in world {Event.get('World')}',
        'requestInvite':f'Invite requested by {User}',
        'Avatar changed': f'to ( {Avatar} ) for user ( {User} )',
        'User left': f'{User}',
        'User joined': f'{User}',
        'Author': f'for avatar ( {Avatar} ) is ( {User} )',
        'User': f'Is {User}',
        'New avatar': f'{Avatar} Added To Known avatars',
    }
    message = templates.get(Event_type,'err')
    Message_display(address=Event_type,message=message,text='Log event:')
    for fController in frames.values():
        fController.handler(address=Event_type,VRCevent=Event)

def VRC_watcher():
    if Nolog := VRC_events.Read_log():
        Message_display('No logs found.','retrying in 30 seconds...','Error:\n')
        delay = 30000
    else: delay = 1000
    Layout.Root.after(delay,VRC_watcher)

def Message_display(address,message,text = None):
    Layout.Log_display.insert('end',f"{text} {address} {message}\n")
    num_lines = int(Layout.Log_display.index('end-1c').split('.')[0])
    if num_lines > 500:
        Layout.Log_display.delete('1.0', '5.0')
    Layout.Log_display.yview('end')
    
def Create_controller(data = None):
    if data:
        for tab_name,Sticks in data.items():
            if tab_name in {'App version', 'Server'}:
                continue
            item_id = Layout.Object_list.insert('', 'end', text=tab_name)
            new_frame = Controller.Tabi(Layout.TabSpace,controller_id=item_id,data=Sticks,message_display=Message_display,name=tab_name,destroy=Destroy_controller)
            frames[item_id] = new_frame
            new_frame.grid(row=0, column=0, sticky='nsew',padx=(0,4),pady=(4,4))
            new_frame.Load(Sticks)
    else:
        tab_name = f"Controller {len(Layout.Object_list.get_children()) + 1}"
        item_id = Layout.Object_list.insert('', 'end', text=tab_name)
        new_frame = Controller.Tabi(Layout.TabSpace,controller_id=item_id,message_display=Message_display,name=tab_name,destroy=Destroy_controller)
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
        #used_avatars.remove(ControllerId)
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
def unfocus(event):
    widget = event.widget

    try:
        class_name = widget.winfo_class()

        if class_name not in ('Text','Button','Treeview','TEntry','TCombobox','Radiobutton','Scrollbar','Spinbox','Listbox'):
            Layout.Root.focus_set()
    except:
        pass      

Layout.Root.bind_all("<Button-1>",unfocus)
Layout.Settings_button.configure(command=Settings_view)
Layout.Add_Tab.configure(command=Create_controller)
Layout.Object_list.bind("<<TreeviewSelect>>", on_treeview_select)

Server = OSC_Listner()
Server.Start_server(Layout.Ip_entry.get(),Layout.Port_entry.get())
VRC_events = Log_parser(VRC_handler)

Layout.Root.after(1000,Server_handler)
Layout.Root.after(1000,VRC_watcher)
VRC_events.Find_user()
if State:
    Layout.Root.after(0,Create_controller(State))

Layout.Root.protocol("WM_DELETE_WINDOW", lambda: (Persistence.save_state(frames), Layout.Root.destroy()))

if __name__ == "__main__":
    
    Layout.Root.mainloop()
    
    