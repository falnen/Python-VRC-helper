import ttkbootstrap as ttk
from ttkbootstrap import scrolled as stk
import Events
from Constants import READ_ONLY_PARAMETERS, CONTROLS_LIST,GAME_EVENTS
from Osc import OSC_client

class Tabi(ttk.Frame):
    saved_avatars = {'Universal':[None,[]]}
    avatar_name_hold = None
    avatar_id_hold = None
    System_events = ['a']
    Network_events = ['b']
    def __init__(self,parent,message_display,controlled_avatar,data = None, name="New Controller",controller_id=None, destroy=None):
        super().__init__(parent)
        self.name = name
        self.controlled_avatar = controlled_avatar
        self.parent = parent
        self.message_display = message_display
        self.id = controller_id
        self.kill = destroy
        self.stick_type = ttk.StringVar()

        self.Client = OSC_client('127.0.0.1',9000)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)

        self.Learned_parameters = []
        self.filtered_parameters = []

        self.stick_count = 0
        self.Stick_list = {}
        def Add_stick():
            StickType = self.stick_type.get()
            title = Title.get()
            match StickType:
                case 'OSC':triggers = self.Control_parameters
                case 'VRC':triggers = GAME_EVENTS
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
                Title.configure(values=self.Control_parameters,state='normal')
                Title.set(self.Control_parameters[0])
            elif self.stick_type.get() == 'VRC':
                Title.configure(values=GAME_EVENTS,state='readonly')
                Title.set(GAME_EVENTS[0])
            elif self.stick_type.get() == 'SYS':
                Title.configure(values=self.Control_parameters)

        def populate_parameter_filter(_):
            for item in self.learned_parameters_filter.get_children():
                self.learned_parameters_filter.delete(item)
            if self.Avatar.get() == 'Universal':
                for avatarid, parameters in self.saved_avatars.values():
                    for parameter in parameters:
                        try:
                            self.learned_parameters_filter.insert('','end',iid=parameter,text=parameter)
                        except:pass
                return
            for parameter in self.saved_avatars[self.Avatar.get()][1]:
                self.learned_parameters_filter.insert('','end',iid=parameter,text=parameter)

        def filter_enable():
            def_sel = self.default_parameters_filter.selection()
            cu_sel = self.learned_parameters_filter.selection()


        self.Stick_space = stk.ScrolledFrame(self,style='Tab.TFrame',padding=[5,35,15,0])
        Spacer_frame = ttk.Frame(self,height=14)
        Headder_button = ttk.Button(Spacer_frame,style='c.TButton',text='Collapse',width=8,command=hide)
        Header_seperator = ttk.Separator(self,orient='horizontal',bootstyle='PRIMARY')
        Header_frame = ttk.Frame(self,padding=0)
        self.Avatar = ttk.Combobox(Header_frame,width=25,values=self.saved_avatars,state='readonly')
        self.Avatar.bind('<<ComboboxSelected>>',populate_parameter_filter)
        self.Avatar.set(self.controlled_avatar)
        self.filterlabel = ttk.Label(Header_frame,text='Filter')
        self.filter = ttk.Entry(Header_frame)
        self.filter_enable = ttk.Button(Header_frame,text='Enable',width=8)
        self.filter_disable = ttk.Button(Header_frame,text='Disable',width=8)
        self.default_parameters_filter = ttk.Treeview(Header_frame,height=8,style='L.Treeview')
        self.default_parameters_filter.column('#0',width=240)
        self.default_parameters_filter.heading('#0',text='Default avatar parameters',anchor='n')
        self.learned_parameters_filter = ttk.Treeview(Header_frame,height=8,style='L.Treeview')
        self.learned_parameters_filter.column('#0',width=240)
        self.learned_parameters_filter.heading('#0',text='Custom avatar parameters',anchor='n')
        populate_parameter_filter(0)

        self.Add_event_button = ttk.Button(self,text='Add Event',command=Add_stick)
        Title = ttk.Combobox(self,width=30,style='event.TCombobox')
        selection1 = ttk.Radiobutton(self,padding=[2,0,2,0],text='OSC',value='OSC',bootstyle='outline-toolbutton',variable=self.stick_type,command=List_set)
        selection2 = ttk.Radiobutton(self,padding=[2,0,2,0],text='VRC',value='VRC',bootstyle='outline-toolbutton',variable=self.stick_type,command=List_set)
        selection3 = ttk.Radiobutton(self,padding=[2,0,2,0],text='SYS',value='SYS',bootstyle='outline-toolbutton',variable=self.stick_type,command=List_set,state='disabled')
        selection4 = ttk.Radiobutton(self,padding=[2,0,2,0],text='NET',value='NET',bootstyle='outline-toolbutton',variable=self.stick_type,command=List_set,state='disabled')
        self.stick_type.set('OSC')
        List_set()

        self.Stick_space.container.configure(style='Tab.TFrame')
        self.Stick_space.grid(row=1,column=0,sticky='nsew')
        self.Stick_space.columnconfigure(0,weight=1)
        self.Stick_space.vscroll.pack_configure(side='right',fill='y',pady=[19,0])
        self.Stick_space.vscroll.configure(bootstyle='light-round')
        self.Avatar.configure(postcommand=lambda:self.Avatar.configure(values=list(self.saved_avatars)))

        Spacer_frame.grid(row=1,column=0,sticky='new')
        Headder_button.pack(side='right',padx=[0,2])
        Header_seperator.grid(row=1,column=0,sticky='new',pady=14)
        self.Add_event_button.grid(row=1,column=0,sticky='n')
        Header_frame.grid(row=0,column=0,sticky='nsew')
        Header_frame.rowconfigure([0,1,2,3],weight=1)
        Header_frame.columnconfigure([0,1,3,4],weight=1,uniform='a')
        Header_frame.columnconfigure(2,weight=0)
        selection1.grid(row=1,column=0,sticky='n',padx=[245,0],pady=[5,0])
        selection2.grid(row=1,column=0,sticky='n',padx=[325,0],pady=[5,0])
        selection3.grid(row=1,column=0,sticky='n',padx=[400,0],pady=[5,0])
        selection4.grid(row=1,column=0,sticky='n',padx=[475,0],pady=[5,0])
        Title.grid(row=1,column=0,sticky='n',padx=[0,420],pady=[5,0])
        self.Avatar.grid(row=0,column=3,sticky='ne')
        self.filterlabel.grid(row=1,column=2,pady=[0,10])
        self.filter.grid(row=1,column=2,sticky='s')
        self.filter_enable.grid(row=2,column=2,sticky='s',pady=[0,30])
        self.filter_disable.grid(row=2,column=2,sticky='s')
        self.default_parameters_filter.grid(row=1,column=0,sticky='nse',columnspan=2,rowspan=3,pady=[0,10])
        self.learned_parameters_filter.grid(row=1,column=3,sticky='nsw',columnspan=2,rowspan=3,pady=[0,10])
        Controller_settings_button = ttk.Button(Header_frame,style='setting.TButton',text='❌',width=3,command=lambda:self.kill(self.id))
        Controller_settings_button.grid(row=0,column=4,sticky='ne')
        for parameter in READ_ONLY_PARAMETERS + CONTROLS_LIST:
            self.default_parameters_filter.insert('','end',text=parameter)
        hide()
    @property
    def Control_parameters(self):
        return self.Learned_parameters + list(READ_ONLY_PARAMETERS)
    @property
    def Response_parameters(self):
        return self.Learned_parameters + list(CONTROLS_LIST)

    def Lookup(self,Stick,OSCmessage=None,VRCevent=None):
        Ids = Stick.Response_list.get_children()

        Received_value = self.normalize(OSCmessage) if OSCmessage else None
        if not VRCevent: VRCevent = [None,None,None,None,None]
        for Id in Ids:
            data = Stick.stick_data[Id]
            passed = (
                (data['conditionOP'] == '=' and Received_value == int(data['condition'])) or
                (data['conditionOP'] == '<' and Received_value < int(data['condition'])) or
                (data['conditionOP'] == '>' and Received_value > int(data['condition']))
                ) if Received_value is not None else (
                (data['user'] == VRCevent.get('User') and data['avatar'] == None) or
                (data['user'] == VRCevent.get('User') and data['avatar'] == VRCevent.get('Avatar'))or
                (data['user'] == VRCevent.get('User') and data['avatar'] == 'ANY') or
                (data['user'] == 'ANY' and data['avatar'] == None) or
                (data['user'] == 'ANY' and data['avatar'] == VRCevent.get('Avatar')) or
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
            print(f'error {value}')
            return value

    def handler(self,address,OSCmessage=None,VRCevent=None):
        if address ==  'Local player': self.user = VRCevent[0]
        for Stick in self.Stick_list.values():
            user_address = Stick.Trigger.get()
            if address == user_address:
                self.Lookup(Stick,OSCmessage=OSCmessage,VRCevent=VRCevent)

    def Load(self,Sticks):
        for StickId,data in Sticks.items():
            if StickId == 'Avatar':continue
            StickType = data['Type']
            if StickType == 'NET': self.Network_events
            elif StickType == 'VRC': triggers = GAME_EVENTS
            elif StickType == 'SYS': triggers = self.System_events
            elif StickType == 'OSC': triggers = self.Control_parameters

            Stick = Events.Eventi(self.Stick_space,Id=(StickId,StickType),controller=self,Title=data['Trigger'],triggers=triggers)
            self.Stick_list[StickId] = Stick
            self.stick_count += 1
            Stick.grid(row=StickId,column=0,sticky='nsew',padx=2,pady=4)
            Stick.Load(data)