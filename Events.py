
import ttkbootstrap as ttk
import re
from ttkbootstrap.tooltip import ToolTip
from Layout import Eventi_layout
from Constants import LAYOUT_TEMPLATES, REQUIRED_FIELDS, WIDGET_DATA
from Osc import OSC_Listner
class aug(ttk.Frame):
    def __init__(self,parent,type):
        super().__init__(parent,width=10)
        self.parent = parent
        self.type = type
        self.configure(style='Tab.TFrame')
        self.rowconfigure(0,weight=1)
        self.columnconfigure([0,1],weight=1)

        self.Typelabel = ttk.Label(self,text='Event',style='alt.TLabel')
        Delete = ttk.Button(self,text='❌',width=3,padding=[0,1,2,1])
        self.Expandb = ttk.Button(self,text='➖',width=3,padding=[0,1,2,1],command=self.Expand)
        
        self.Typelabel.grid(row=0,column=0,sticky='n',padx=[0,10])
        Delete.grid(row=0,column=2,sticky='n')
        self.Expandb.grid(row=0,column=1,sticky='n',padx=[0,5])

        ToolTip(Delete, text='Hold Ctrl to delete',delay=0,bootstyle='selectbg')
        Delete.bind('<Control-Button-1>',self.Destroy)
    
    def Expand(self):
        if self.parent.body.grid_info():
            self.parent.body.grid_remove()
            self.Expandb.configure(text='◼️')
        else:
            self.parent.body.grid()
            self.Expandb.configure(text='➖')

    def Destroy(self,event=None):
        OSC_Listner.active_server.unMap_address(address=self.parent.Trigger.get())
        self.parent.controller.stick_count -= 1
        self.parent.controller.Stick_list.pop(self.parent.Trigger.get())
        self.parent.destroy()

number_re = re.compile(r"^-?(0|[1-9]\d*)(\.\d*)?$")
class Eventi(Eventi_layout):
    def  __init__(self,parent,Id,controller,Title,triggers):
        super().__init__(parent,Id[1],template=LAYOUT_TEMPLATES)
        self.controller = controller
        self.Id = Id
        self.triggers = triggers
        self.stick_data = {}
        self.name_var = ttk.BooleanVar()
        self.avatar_var = ttk.BooleanVar()
        self.world_var = ttk.BooleanVar()
        self.toggle_var = ttk.BooleanVar(value=True)
        self.label = aug(self,'Int')

        def Insert_data():
            stick_type = self.Id[1]
            Trigger = self.Trigger.get()
            entry_type = REQUIRED_FIELDS.get(stick_type,{})
            required = entry_type.get(Trigger,entry_type.get('*',[]))
            data = {
                'user':self.widgets['name_entry'].get() if self.widgets.get('name_entry') else None,
                'avatar':self.widgets['avatar'].get() if self.widgets.get('avatar') and Trigger == 'Avatar changed' else None,
                'world':self.widgets['world'].get() if self.widgets.get('world') and Trigger == 'Invite' else None,
                'timestamp':None,# TODO: maybe implement
                'message':None, # TODO: implement
                'condition':self.widgets['condition_entry'].get() if self.widgets.get('condition_entry') else None,
                'conditionOP': self.widgets['condition_operator'].get() if self.widgets.get('condition_operator') else None,
                'address':self.Response_address.get(),
                'value':self.Response_value.get() or self.Response_value_avatars.get(),
                'delay':self.Response_delay.get(),
            }

            if stick_type == 'VRC':
                if self.name_var.get(): data['user'] = 'ANY'
                if self.avatar_var.get(): data['avatar'] = 'ANY'
                #if not self.avatar_var.get() : data['avatar'] = None
                if self.world_var.get(): data['world'] = 'ANY'
                #if not self.world_var.get() : data['world'] = None
            if missing := [key for key in required if not data.get(key)]:
                print(missing)
                return

            item = self.Response_list.selection()
            if stick_type == 'OSC':
                if item:
                    self.stick_data[item[0]] = data
                    self.Response_list.item(item,text=f'{data["conditionOP"]} {data["condition"]}',values=(data['address'],data['value'],data['delay']))
                else: self.stick_data[self.Response_list.insert('','end',text=f'{data["conditionOP"]} {data["condition"]}',values=(data['address'],data['value'],data['delay']))] = data
            elif stick_type == 'VRC':
                match Trigger:
                    case 'Invite':condition = f'{data['user']} : {data['world']}'
                    case 'Avatar changed':condition = f'{data['user']} : {data['avatar']}'
                    case 'User joined' | 'User left' | 'Invite request' | 'Friend requests':condition = data['user']
                if item:
                    self.stick_data[item[0]] = data
                    self.Response_list.item(item,text=condition,values=(data['address'],data['value'],data['delay']))
                else: self.stick_data[self.Response_list.insert('','end',text=condition,values=(data['address'],data['value'],data['delay']))] = data
            else:
                print('Error saving:\nUnimplemented Type')
        def Response_list_select(_):
            item = self.Response_list.selection()
            if item:
                values = self.stick_data[item[0]]
                for data_key,widget_key in WIDGET_DATA.items():
                    value = values.get(data_key)
                    if hasattr(self, widget_key): widget = getattr(self, widget_key)
                    else: widget = self.widgets.get(widget_key)
                    if widget is None: continue

                    if isinstance(widget, ttk.Entry):
                        widget.delete(0, ttk.END)
                        widget.insert(0, value if value is not None else '')
                    elif isinstance(widget, ttk.Combobox):
                        widget.set(value if value is not None else '')
                    elif isinstance(widget, ttk.Label):
                        widget.config(text=value if value is not None else '')

                self.Response_save.configure(text='Overwrite')
                self.List_remove.configure(state='normal')
                self.List_orderup.configure(state='normal')
                self.List_orderdown.configure(state='normal')
                self.List_ordertop.configure(state='normal')
                self.List_orderbottom.configure(state='normal')
            else:
                self.Response_save.configure(text='Save')
                self.List_remove.configure(state='disabled')
                self.List_orderup.configure(state='disabled')
                self.List_orderdown.configure(state='disabled')
                self.List_ordertop.configure(state='disabled')
                self.List_orderbottom.configure(state='disabled')
        def ava_list_swap(_):
            avatar_info = []
            if self.Response_address.get() == '/avatar/change':
                for avatar in self.controller.saved_avatars.keys():
                    avatar_id = self.controller.saved_avatars.get(avatar)[0]
                    avatar_info.append(f'{avatar} ({avatar_id})')
                self.Response_value.grid_remove()
                self.Response_value_avatars.configure(values=avatar_info)
                self.Response_value_avatars.grid(row=2,column=1,sticky='s',padx=[0,62],pady=[5,0])
            else:
                self.Response_value_avatars.grid_forget()
                self.Response_value.grid()
        def toggle_active():
            match self.toggle_var.get():
                case True: self.Toggle.configure(text='Enabled')
                case False: self.Toggle.configure(text='Disabled')
        def Move(v):
            Item = self.Response_list.selection()
            Index = self.Response_list.index(Item)
            Last = len(self.Response_list.get_children())
            match v:
                case 'u':self.Response_list.move(Item,'',Index-1)
                case 'd':self.Response_list.move(Item,'',Index+1)
                case 't':self.Response_list.move(Item,'',0)
                case 'b':self.Response_list.move(Item,'',Last)
        def Remove():
            if Selected_item := self.Response_list.selection():
                previous_item = self.Response_list.prev(Selected_item)
                self.Response_list.delete(Selected_item)
                self.Response_list.selection_set(previous_item)
        def No_empty_trigger(_=None):
            if not self.Trigger.get():
                self.Trigger.set(self.triggers[0])
        def Reset_headings(_=None):
            self.Response_list.column('#0',width=68)
            self.Response_list.column('Address',width=50)
            self.Response_list.column('Value',width=50)
            self.Response_list.column('Delay',width=50)
        def Clear_select(_):
            if Selected_item := self.Response_list.selection(): self.Response_list.selection_remove(Selected_item)
        def is_user_check():
            if self.name_var.get(): self.widgets['name_entry'].configure(state='disabled')
            else: self.widgets['name_entry'].configure(state='normal')
        def is_ava_check():
            if self.avatar_var.get(): self.widgets['avatar'].configure(state='disabled')
            else: self.widgets['avatar'].configure(state='normal')
        def is_world_check():
            if self.world_var.get(): self.widgets['world'].configure(state='disabled')
            else: self.widgets['world'].configure(state='normal')
        def unbind_scroll(event):
            event.widget.bind("<MouseWheel>", lambda e: 'break')
        def Validate_osc_entry(entry):
            return entry == "" or bool(number_re.match(entry)) if self.Response_address.get() != '/avatar/change' else True

        self.configure(labelwidget=self.label,labelanchor='ne',height=50,style='Tab.TLabelframe')
        self.vcmd = self.register(Validate_osc_entry)
        self.Toggle.configure(command=toggle_active,variable=self.toggle_var)
        self.Response_address.configure(values=controller.response_parameters,postcommand=lambda:self.Response_address.configure(values=controller.response_parameters))
        self.Response_value.configure(validatecommand=(self.vcmd,'%P'))
        self.Response_save.configure(command=Insert_data)
        self.List_remove.configure(command=Remove)
        self.List_orderup.configure(command=lambda:Move('u'))
        self.List_orderdown.configure(command=lambda:Move('d'))
        self.List_ordertop.configure(command=lambda:Move('t'))
        self.List_orderbottom.configure(command=lambda:Move('b'))
        self.Trigger.configure(values=triggers,postcommand=lambda:self.Trigger.configure(values=triggers))
        self.Trigger.set(Title)
        self.Trigger.bind('<FocusOut>',No_empty_trigger)
        self.Trigger.bind('<Enter>',unbind_scroll)
        self.Response_list.bind("<<TreeviewSelect>>", Response_list_select)
        self.Response_list.bind('<ButtonPress-1>',Reset_headings)
        self.Response_list.bind('<ButtonPress-3>',Clear_select)
        self.Response_address.bind('<Enter>',unbind_scroll)
        self.Response_address.bind('<<ComboboxSelected>>',ava_list_swap)

        if self.Id[1] == 'OSC':
            self.Response_list.column('#0',anchor='w',minwidth=68,width=68,stretch=False)
            self.Trigger.configure(state='normal')
            self.Response_list.heading('#0',text='Condition',anchor='w')
            self.widgets['condition_entry'].configure(validatecommand=(self.vcmd,'%P'))
            self.widgets['condition_operator'].bind('<Enter>',unbind_scroll)
            self.widgets['condition_operator'].set('=')

        elif self.Id[1] == 'VRC':
            self.Response_list.column('#0',anchor='w',minwidth=68,width=100,stretch=True)
            self.widgets['any_name'].configure(variable=self.name_var,command=is_user_check)
            self.widgets['any_avatar'].configure(variable=self.avatar_var,command=is_ava_check)
            self.widgets['any_world'].configure(variable=self.world_var,command=is_world_check)
            match Title:
                case 'User joined' | 'User left' | 'Invite request' | 'Friend requests':
                    self.Response_list.heading('#0',text='Name',anchor='w')
                    for name in ('avatar', 'any_avatar','avatar_label','world','any_world','world_label'):
                        self.widgets.pop(name, None).destroy()
                case 'Avatar changed':
                    self.Response_list.heading('#0',text='Name : Avatar',anchor='w')
                    for name in ('world','any_world','world_label'):
                        self.widgets.pop(name, None).destroy()
                case 'Invite':
                    self.Response_list.heading('#0',text='Name : world',anchor='w')
                    for name in ('avatar', 'any_avatar','avatar_label'):
                        self.widgets.pop(name, None).destroy()
    
            #group_invite = ttk.Radiobutton(self.body,text='Group Invite')
            #group_posts = ttk.Radiobutton(self.body,text='Group Post')
        Reset_headings()
    
    def Load(self,data):
        Trigger =  data.get('Trigger')
        stick_type = data.get('Type')
        for iid, responsedata in data.items():
            if iid in {'Type', 'Trigger'}:
                continue
            
            self.stick_data[iid] = responsedata
            if stick_type == 'OSC':

                self.Response_list.insert('','end',iid=iid,text=f'{responsedata["conditionOP"]} {responsedata["condition"]}',values=(responsedata['address'],responsedata['value'],responsedata['delay']))
            elif stick_type == 'VRC':
                match Trigger:
                    case 'Invite':condition = f'{responsedata['user']} : {responsedata['world']}'
                    case 'Avatar changed':condition = f'{responsedata['user']} : {responsedata['avatar']}'
                    case 'User joined' | 'User left' | 'Invite request' | 'Friend requests':condition = responsedata['user']
                self.Response_list.insert('','end',iid=iid,text=condition,values=(responsedata['address'],responsedata['value'],responsedata['delay']))
            else:
                 print('Error loading:\nUnimplemented Type')