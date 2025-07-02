import ttkbootstrap as ttk
import Events
from Layout import Tabi_layout, Message_display, s_ipvar, s_portvar
from Constants import READ_ONLY_PARAMETERS, CONTROLS_LIST,GAME_EVENTS
from Osc import OSC_client,OSC_Listner

class Tabi(Tabi_layout):
    saved_avatars = {'Universal':[None,[]]}
    avatar_name_hold = None
    System_events = ['a']
    Network_events = ['b']
    def __init__(self,parent,controlled_avatar,name="New Controller",controller_id=None, destroy=None):
        super().__init__(parent)
        self.name = name
        self.controlled_avatar = ttk.StringVar(value=controlled_avatar)
        self.parent = parent
        self.id = controller_id
        self.kill = destroy
        self.stick_type = ttk.StringVar(value='OSC')
        self.Client = OSC_client(s_ipvar.get(),s_portvar.get())

        self.control_parameters = self.saved_avatars[self.controlled_avatar.get()][1] + list(READ_ONLY_PARAMETERS)
        self.response_parameters = self.saved_avatars[self.controlled_avatar.get()][1] + list(CONTROLS_LIST)
        self.filtered_parameters = []

        self.stick_count = 0
        self.Stick_list = {}

        def Add_stick():
            stick_type = self.stick_type.get()
            title = self.Title.get()
            match stick_type:
                case 'OSC':triggers = self.control_parameters
                case 'VRC':triggers = GAME_EVENTS
                case 'SYS':triggers = self.System_events
                case 'NET':triggers = self.Network_events

            #Id = (self.stick_count,stick_type)
            Stick = Events.Eventi(self.Stick_space,Id=(self.stick_count,stick_type),controller=self,Title=title,triggers=triggers)
            if stick_type == 'OSC': OSC_Listner.active_server.Map_address(title)
            self.Stick_list[title] = Stick
            Stick.grid(row=self.stick_count,column=0,sticky='nsew',padx=2,pady=4)
            self.stick_count += 1

        def hide():
            if not self.Header_frame.grid_info():
                self.Header_frame.grid()
                self.Header_button.configure(text='Close')
            else:
                self.Header_frame.grid_remove()
                self.Header_button.configure(text='Config')

        def kill(a=None):
            self.kill(self.controlled_avatar.get(),a)

        def List_set():
            match self.stick_type.get():
                case 'OSC':
                    self.Title.configure(values=self.control_parameters,state='normal')
                    self.Title.set(self.control_parameters[0])
                case 'VRC':
                    self.Title.configure(values=GAME_EVENTS,state='readonly')
                    self.Title.set(GAME_EVENTS[0])
                case 'SYS':
                    self.Title.configure(values=self.control_parameters)

        def populate_parameter_filter(e=None):
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

        def clear_select(_):
            if selection1 := self.default_parameters_filter.selection(): self.default_parameters_filter.selection_remove(selection1)
            if selection2 := self.learned_parameters_filter.selection(): self.learned_parameters_filter.selection_remove(selection2)

        def add_new_parameter():
            parameter = self.filter_entry.get()
            if parameter not in Tabi.saved_avatars[self.controlled_avatar.get()][1]:
                Tabi.saved_avatars[self.controlled_avatar.get()][1].append(parameter)
                self.learned_parameters_filter.insert('','end',iid=parameter,text=parameter)

        def forget_parameter():
            items = self.learned_parameters_filter.selection()
            for item in items:
                self.learned_parameters_filter.delete(item)
                if item in Tabi.saved_avatars[self.controlled_avatar.get()][1]:
                    Tabi.saved_avatars[self.controlled_avatar.get()][1].remove(item)
                    self.learned_parameters_filter.delete

        def filter_enable():
            def_sel = self.default_parameters_filter.selection()
            cu_sel = self.learned_parameters_filter.selection()
        
        self.Header_button.configure(command=hide)
        self.Avatar.configure(textvariable=self.controlled_avatar,values=list(self.saved_avatars))
        self.Delete_button.configure(command=kill)
        self.Delete_button.bind('<Shift-Button-1>',lambda a=None:kill(True))
        self.Title.configure(postcommand=List_set)
        self.Add_event_button.configure(command=Add_stick)
        self.selection1.configure(variable=self.stick_type,command=List_set)
        self.selection2.configure(variable=self.stick_type,command=List_set)
        self.selection3.configure(variable=self.stick_type,command=List_set)
        self.selection4.configure(variable=self.stick_type,command=List_set)
        self.Avatar.configure(postcommand=lambda:self.Avatar.configure(values=list(self.saved_avatars)))
        self.default_parameters_filter.bind('<ButtonPress-3>',clear_select)
        self.learned_parameters_filter.bind('<ButtonPress-3>',clear_select)
        self.Add_parameter.configure(command=add_new_parameter)
        self.Remove_parameter.configure(command=forget_parameter)
        self.Avatar.bind('<<ComboboxSelected>>',populate_parameter_filter)
        
        for parameter in READ_ONLY_PARAMETERS + CONTROLS_LIST:
            self.default_parameters_filter.insert('','end',text=parameter)
        List_set()
        populate_parameter_filter()
        hide()

    def custom_parameters(self,parameter):
        if parameter not in self.control_parameters + self.response_parameters + list(self.learned_parameters_filter.get_children()):
            Tabi.saved_avatars[self.controlled_avatar.get()][1].append(parameter)
            self.control_parameters.insert(1,parameter)
            self.response_parameters.insert(1,parameter)
            self.learned_parameters_filter.insert('','end',iid=parameter,text=parameter)

    def Lookup(self,Stick,OSCmessage=None,VRCevent=None):
        Ids = Stick.Response_list.get_children()
        Received_value = self.normalize(OSCmessage) if OSCmessage is not None else None
        if not VRCevent: VRCevent = {}
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
                Message_display(data['address'],self.stab(data['value']),text='Sent:')

    def stab(self,value):
        if value.isdigit():
            return int(value)
        if 'avtr' in value:
            value = value.split('(')[1].strip(')')
            return value
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
        if Stick := self.Stick_list.get(address):
            if not Stick.toggle_var.get(): return
            self.Lookup(Stick,OSCmessage=OSCmessage,VRCevent=VRCevent)

    def Load(self,Sticks):
        for StickId,data in Sticks.items():
            if StickId == 'Avatar':continue
            StickType = data['Type']
            match StickType:
                case 'OSC':
                    triggers = self.control_parameters
                    OSC_Listner.active_server.Map_address(data['Trigger'])
                case 'VRC':triggers = GAME_EVENTS
                case 'SYS':triggers = self.System_events
                case 'NET':triggers = self.Network_events

            Stick = Events.Eventi(self.Stick_space,Id=(StickId,StickType),controller=self,Title=data['Trigger'],triggers=triggers)
            self.Stick_list[data['Trigger']] = Stick
            Stick.grid(row=self.stick_count,column=0,sticky='nsew',padx=2,pady=4)
            self.stick_count += 1
            Stick.Load(data)