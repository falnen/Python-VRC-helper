import ttkbootstrap as ttk
from ttkbootstrap import scrolled as stk
import Events
from Constants import READ_ONLY_PARAMETERS, CONTROLS_LIST
from Osc import OSC_client

class Tabi(ttk.Frame):
    saved_avatars = []
    Game_events = ['User joined','User left','Avatar changed','Invite', 'Invite request', 'Friend requests']#Group invites and notifs todo
    System_events = ['a']
    Network_events = ['b']
    def __init__(self,parent,message_display,data = None, name="New Controller",controller_id=None, destroy=None):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.message_display = message_display
        self.id = controller_id
        self.kill = destroy
        self.stick_type = ttk.StringVar()

        self.Client = OSC_client('127.0.0.1',9000)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)
        
        self.Known_parameters = []

        self.stick_count = 0
        self.Stick_list = {}
        def Add_stick():
            StickType = self.stick_type.get()
            title = Title.get()
            match StickType:
                case 'OSC':triggers = self.Control_parameters
                case 'VRC':triggers = self.Game_events
                case 'SYS':triggers = self.System_events
                case 'NET':triggers = self.Network_events

            Id = (self.stick_count,StickType)
            Stick = Events.Eventi(self.Stick_space,Id=Id,controller=self,Title=title,triggers=triggers)
            self.Stick_list[Id[0]] = Stick
            self.stick_count += 1
            Stick.grid(row=Id[0],column=0,sticky='nsew',padx=2,pady=4)
           
        def hide():
            if not Header_frame.grid_info():
                Header_frame.grid()
                Headder_button.configure(text='Collapse')
            else:
                Header_frame.grid_remove()
                Headder_button.configure(text='Expand')

        def List_set():
            if self.stick_type.get() == 'OSC':
                Title.configure(values=self.Control_parameters)
                Title.set(self.Control_parameters[0])
            elif self.stick_type.get() == 'VRC':
                Title.configure(values=self.Game_events,state='readonly')
                Title.set(self.Game_events[0])
            elif self.stick_type.get() == 'SYS':
                Title.configure(values=self.Control_parameters)

        self.Stick_space = stk.ScrolledFrame(self,style='Tab.TFrame',padding=[5,35,15,0])
        self.Stick_space.container.configure(style='Tab.TFrame')
        self.Stick_space.grid(row=1,column=0,sticky='nsew')
        self.Stick_space.columnconfigure(0,weight=1)
        self.Stick_space.yview_scroll(100,'units')
        self.Stick_space.vscroll.pack_configure(side='right',fill='y',pady=[19,0])
        self.Stick_space.vscroll.configure(bootstyle='light-round')
        
        Spacer_frame = ttk.Frame(self,height=14)
        Headder_button = ttk.Button(Spacer_frame,style='c.TButton',text='Collapse',width=8,command=hide)
        Header_seperator = ttk.Separator(self,orient='horizontal',bootstyle='PRIMARY')
        self.Add_event_button = ttk.Button(self,text='Add Event',command=Add_stick)
        Header_frame = ttk.Frame(self,padding=0)

        Title = ttk.Combobox(Header_frame,width=45)
        self.Avatar = ttk.Combobox(Header_frame,width=25,values=self.saved_avatars)
        self.Avatar.configure(postcommand=lambda:self.Avatar.configure(values=self.saved_avatars))
        selection1 = ttk.Radiobutton(Header_frame,text='OSC',value='OSC',variable=self.stick_type,command=List_set)
        selection2 = ttk.Radiobutton(Header_frame,text='VRC',value='VRC',variable=self.stick_type,command=List_set)
        #selection3 = ttk.Radiobutton(Header_frame,text='SYS',value='SYS',variable=self.stick_type,command=List_set)
        
        Spacer_frame.grid(row=1,column=0,sticky='new')
        Headder_button.pack(side='right',padx=[0,2])
        Header_seperator.grid(row=1,column=0,sticky='new',pady=14)
        self.Add_event_button.grid(row=1,column=0,sticky='n')
        Header_frame.grid(row=0,column=0,sticky='nsew')
        Header_frame.rowconfigure(0,weight=1)
        Header_frame.columnconfigure([0,1,2,3,4],weight=1,uniform='a')
        selection1.grid(row=1,column=2,sticky='w')
        selection2.grid(row=1,column=2,sticky='e')
        #selection3.grid(row=2,column=0,sticky='e')
        Title.grid(row=0,column=1,sticky='ns',columnspan=3)
        self.Avatar.grid(row=0,column=0,sticky='nw')
        Controller_settings_button = ttk.Button(Header_frame,style='setting.TButton',text='❌',width=3,command=lambda:self.kill(self.id))
        Controller_settings_button.grid(row=0,column=4,sticky='ne')
        
    @property
    def Control_parameters(self):
        return self.Known_parameters + list(READ_ONLY_PARAMETERS)
    @property
    def Response_parameters(self):
        return self.Known_parameters + list(CONTROLS_LIST)
    
    def Lookup(self,Stick,OSCmessage=None,VRCevent=None):
        Ids = Stick.Response_list.get_children()

        Received_value = self.normalize(OSCmessage) if OSCmessage else None
        if not VRCevent: VRCevent = [None,None,None,None,None]
        for Id in Ids:
            data = Stick.stick_data[Id]
            passed = (
                (data['conditionOP'] == '=' and Received_value == data['value']) or
                (data['conditionOP'] == '<' and Received_value < data['value']) or
                (data['conditionOP'] == '>' and Received_value > data['value'])
                ) if OSCmessage else (
                (data['user'] == VRCevent[0] and data['avatar'] == None) or
                (data['user'] == VRCevent[0] and data['avatar'] == VRCevent[4])or
                (data['user'] == VRCevent[0] and data['avatar'] == 'ANY') or
                (data['user'] == 'ANY' and data['avatar'] == None) or
                (data['user'] == 'ANY' and data['avatar'] == VRCevent[4]) or
                (data['user'] == 'ANY' and data['avatar'] == 'ANY')
                )
            if passed:
                self.after(data['delay'],lambda a=data['address'],r=self.stab(data['value']):self.Client.send_message(a,r))
                self.message_display(data['address'],data['value'],text='Sent:')
            else:
                pass

    def stab(self,value):
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value 

    def normalize(self, value):
        if isinstance(value, tuple):
            value = value[0]  

        if isinstance(value, bool) or isinstance(value, int):
            return int(value)

        try:
            return float(value)
        except ValueError:
            return value
        
    def handler(self,address,OSCmessage=None,VRCevent=None):
        if address ==  'Local player': self.user = VRCevent[0]
        for Stick in self.Stick_list.values():
            user_address = Stick.Trigger.get()
            if address == user_address:
                self.Lookup(Stick,OSCmessage=OSCmessage,VRCevent=VRCevent)

    def Load(self,Sticks):
        for StickId,data in Sticks.items():
            StickType = data['Type']
            if StickType == 'NET': self.Network_events
            elif StickType == 'VRC': triggers = self.Game_events
            elif StickType == 'SYS': triggers = self.System_events
            elif StickType == 'OSC': triggers = self.Control_parameters

            Stick = Events.Eventi(self.Stick_space,Id=(StickId,StickType),controller=self,Title=data['Trigger'],triggers=triggers)
            self.Stick_list[StickId] = Stick
            self.stick_count += 1
            Stick.grid(row=StickId,column=0,sticky='nsew',padx=2,pady=4)
            Stick.Load(data)