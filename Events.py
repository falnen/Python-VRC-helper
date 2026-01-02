
import ttkbootstrap as ttk
import re
from ttkbootstrap.tooltip import ToolTip
from Layout import Eventi_layout
from Constants import LAYOUT_TEMPLATES, REQUIRED_FIELDS, WIDGET_DATA
from Osc import OSC_Listner
class aug(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent,width=10)
        self.parent = parent
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
        #address = self.parent.Trigger.get()
        self.parent.controller.unregister_stick_addresses(self.parent,self.parent.addresses)
        self.parent.controller.stick_count -= 1
        self.parent.controller.reflow_sticks()
        self.parent.destroy()

number_re = re.compile(r"^-?(0|[1-9]\d*)(\.\d*)?$")
class Eventi(Eventi_layout):
    def  __init__(self,parent,Id,controller,Title,triggers):
        super().__init__(parent,Id[1],template=LAYOUT_TEMPLATES)
        self.controller = controller
        self.Id = Id
        self.Title = Title
        self.addresses = [Title if Id[1] == 'OSC' else None]
        self.triggers = triggers
        self.stick_data: dict[str,dict[str,str]] = {}
        '''
        key: Treeview item id\n
        value:\n {
            'user': str,
            'avatar': str,
            'world': str,
            'timestamp': str,
            'message': str,
            'condition': str,
            'conditionOP': str,
            'address': str,
            'value': str,
            'delay': str
        }
        '''
        self.name_var = ttk.BooleanVar()
        self.avatar_var = ttk.BooleanVar()
        self.world_var = ttk.BooleanVar()
        self.value_var = ttk.BooleanVar()
        self.ovalue_var = ttk.BooleanVar()
        self.toggle_var = ttk.BooleanVar(value=True)
        self.label = aug(self)
        def Insert_data():
            stick_type = self.Id[1]
            Trigger = self.Trigger.get()
            entry_type = REQUIRED_FIELDS.get(stick_type,{})
            required = entry_type.get(Trigger,entry_type.get('*',[]))
            #print(self.addresses)
            data = {
                'user':self.widgets['name_entry'].get() if self.widgets.get('name_entry') else None,
                'avatar':self.widgets['avatar'].get() if self.widgets.get('avatar') and Trigger == 'Avatar changed' else None,
                'world':self.widgets['world'].get() if self.widgets.get('world') and Trigger == 'Invite' else None,
                'timestamp':None,# TODO: maybe implement
                'message':None, # TODO: implement
                'condition':self.widgets['condition_entry'].get() if self.widgets.get('condition_entry') else None,
                'conditionOP': self.widgets['condition_operator'].get() if self.widgets.get('condition_operator') else None,
                'expression':self.widgets['compound_expression'].get() if self.widgets.get('compound_expression') else None,
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
            elif stick_type == 'OSC':
                if self.value_var.get(): data['condition'] = 'ANY'
                if self.ovalue_var.get(): data['value'] = 'INPUT'
            if missing := [key for key in required if not data.get(key)]:
                #print(missing)
                return

            item = self.Response_list.selection()
            Stored_condition = f'{self.widgets['compound_expression'].get() if self.widgets.get('compound_expression') else ''} {self.widgets['condition_operator'].get() if self.widgets.get('condition_operator') else ''} {self.widgets['condition_entry'].get() if self.widgets.get('condition_entry') else ''}'.strip()
            if stick_type == 'OSC':
                if item:
                    self.stick_data[item[0]] = data
                    self.Response_list.item(item,text=Stored_condition,values=(data['address'],data['value'],data['delay']))
                else:
                    self.stick_data[self.Response_list.insert('','end',text=Stored_condition,values=(data['address'],data['value'],data['delay']))] = data
            elif stick_type == 'VRC':
                match Trigger:
                    case 'Invite':condition = f"{data['user']} : {data['world']}"
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
                #print(values)
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
                    elif isinstance(widget, ttk.Checkbutton):
                        widget.config    
                    

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
                self.Response_value_avatars.grid(row=2,column=1,sticky='s',padx=[5,0],pady=[5,0])
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
        def Remove_response():
            selected = self.Response_list.selection()
            iid = selected[0]
            prev = self.Response_list.prev(iid) or self.Response_list.next(iid)
            self.Response_list.delete(iid)
            self.stick_data.pop(iid, None)
            if prev:
                self.Response_list.selection_set(prev)
            else:
                self.Response_save.configure(text='Save')
                self.List_remove.configure(state='disabled')
                self.List_orderup.configure(state='disabled')
                self.List_orderdown.configure(state='disabled')
                self.List_ordertop.configure(state='disabled')
                self.List_orderbottom.configure(state='disabled')
        def compound_list_select(_):
            tree = self.widgets['compound_list']
            selected = tree.selection()
            if selected:
                self.widgets['compound_add'].configure(text='Remove',command=compound_remove)
            else:
                self.widgets['compound_add'].configure(text='Add',command=compound_add)
        def compound_add():
            address = self.widgets['compound_address'].get()
            if address not in [self.widgets['compound_list'].item(iid)['text'] for iid in self.widgets['compound_list'].get_children()]:
                self.widgets['compound_list'].insert('','end',text=address)
                self.addresses.append(address)
                self.controller.register_stick_addresses(self,[address])
        def compound_remove():
            tree = self.widgets['compound_list']
            selected = tree.selection()
            iid = selected[0]
            self.addresses.remove(tree.item(iid)['text'])
            self.controller.unregister_stick_addresses(self,[tree.item(iid)['text']])
            tree.delete(iid)
        def change_address(_=None):
            address = self.Trigger.get()
            old_address = self.Title
            self.Title = address
            if old_address in self.addresses:
                self.addresses.remove(old_address)
            if address not in self.addresses:
                self.addresses.append(address)
            self.controller.unregister_stick_addresses(self,[old_address])
            self.controller.register_stick_addresses(self,[address])
        def Reset_headings(_=None):
            self.Response_list.column('#0',width=68)
            self.Response_list.column('Address',width=50)
            self.Response_list.column('Value',width=50)
            self.Response_list.column('Delay',width=50)
        def Clear_select(event):
            tree = event.widget
            selected = tree.selection()
            if selected:
                tree.selection_remove(selected)
        def is_user_check():
            if self.name_var.get(): self.widgets['name_entry'].configure(state='disabled')
            else: self.widgets['name_entry'].configure(state='normal')
        def is_ava_check():
            if self.avatar_var.get(): self.widgets['avatar'].configure(state='disabled')
            else: self.widgets['avatar'].configure(state='normal')
        def is_world_check():
            if self.world_var.get(): self.widgets['world'].configure(state='disabled')
            else: self.widgets['world'].configure(state='normal')
        def is_value_check():
            if self.value_var.get(): self.widgets['condition_entry'].configure(state='disabled')
            else: self.widgets['condition_entry'].configure(state='normal')
        def is_ovalue_check():
            if self.ovalue_var.get(): self.Response_value.configure(state='disabled')
            else: self.Response_value.configure(state='normal')
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
        self.List_remove.configure(command=Remove_response)
        self.List_orderup.configure(command=lambda:Move('u'))
        self.List_orderdown.configure(command=lambda:Move('d'))
        self.List_ordertop.configure(command=lambda:Move('t'))
        self.List_orderbottom.configure(command=lambda:Move('b'))
        self.Trigger.configure(values=triggers,postcommand=lambda:self.Trigger.configure(values=triggers))
        self.Trigger.set(self.Title)
        self.Trigger.bind('<<ComboboxSelected>>',change_address)
        self.Trigger.bind('<Enter>',unbind_scroll)
        self.Response_list.bind("<<TreeviewSelect>>", Response_list_select)
        self.Response_list.bind('<ButtonPress-1>',Reset_headings)
        self.Response_list.bind('<ButtonPress-3>',Clear_select)
        self.Response_address.bind('<Enter>',unbind_scroll)
        self.Response_address.bind('<<ComboboxSelected>>',ava_list_swap)

        if self.Id[1] == 'OSC':
            self.widgets['any_value'].configure(variable=self.value_var,command=is_value_check)
            self.Value_overwrite.configure(variable=self.ovalue_var,command=is_ovalue_check)
            self.Response_list.column('#0',anchor='w',minwidth=68,width=68,stretch=True)
            self.Response_list.heading('#0',text='Condition',anchor='w')
            self.widgets['compound_list'].bind("<<TreeviewSelect>>", compound_list_select)
            self.widgets['compound_list'].bind('<ButtonPress-3>',Clear_select)
            self.widgets['compound_address'].configure(values=triggers,postcommand=lambda:self.widgets['compound_address'].configure(values=triggers))
            self.widgets['compound_address'].bind('<Enter>',unbind_scroll)
            self.widgets['compound_address'].set(controller.response_parameters[0])
            self.widgets['compound_add'].configure(command=compound_add)
            self.widgets['compound_list'].column('#0',anchor='w',minwidth=0,stretch=False)
            self.widgets['compound_toggle'].configure(command=self.compound_toggle)
            self.widgets['condition_entry'].configure(validatecommand=(self.vcmd,'%P'))
            self.widgets['condition_operator'].bind('<Enter>',unbind_scroll)
            self.widgets['condition_operator'].set('=')
            self.compound_toggle()

        elif self.Id[1] == 'VRC':
            self.Response_list.column('#0',anchor='w',minwidth=68,width=100,stretch=True)
            self.widgets['any_name'].configure(variable=self.name_var,command=is_user_check)
            self.widgets['any_avatar'].configure(variable=self.avatar_var,command=is_ava_check)
            self.widgets['any_world'].configure(variable=self.world_var,command=is_world_check)
            match self.Title:
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
    
    def compound_toggle(self):
        self.stick_data.clear()
        self.Response_list.delete(*self.Response_list.get_children())
        self.controller.unregister_stick_addresses(self,self.addresses)
        self.controller.register_stick_addresses(self,self.addresses)
        match self.widgets['compound_toggle'].cget('text'):
            case 'Single input':
                self.addresses.clear()
                self.addresses.append(self.Title)
                self.Trigger.configure(state='readonly')
                self.Trigger.set(self.Title)
                self.widgets['compound_list'].delete(*self.widgets['compound_list'].get_children())
                self.widgets['compound_toggle'].configure(text='Compound input')
                self.widgets['compound_label'].grid_remove()
                self.widgets['compound_address'].grid_remove()
                self.widgets['compound_add'].grid_remove()
                self.widgets['compound_list'].grid_remove()
                self.widgets['compound_expression'].grid_remove()
                self.widgets['value_label'].grid_configure(row=1)
                self.widgets['condition_entry'].grid_configure(row=1)
                self.widgets['condition_operator'].grid_configure(row=1)
                self.widgets['any_value'].grid_configure(row=1)
            case 'Compound input':
                self.Trigger.configure(state='disabled')
                for address in self.addresses:
                    self.widgets['compound_list'].insert('','end',text=address)
                self.widgets['compound_toggle'].configure(text='Single input')
                self.widgets['compound_label'].grid()
                self.widgets['compound_expression'].grid()
                self.widgets['compound_address'].grid()
                self.widgets['compound_add'].grid()
                self.widgets['compound_list'].grid()
                self.widgets['value_label'].grid_configure(row=2)
                self.widgets['condition_entry'].grid_configure(row=2)
                self.widgets['condition_operator'].grid_configure(row=2)
                self.widgets['any_value'].grid_configure(row=2)

    def Load(self,Trigger,Sticktype,Addresses,data):
        self.addresses = Addresses
        if len(Addresses) > 1:
            self.widgets['compound_toggle'].configure(text='Compound input')
            self.compound_toggle()
        for iid, responsedata in data.items():
            if iid == 'Title' or iid == 'Type' or iid == 'Addresses': continue
            if Sticktype == 'OSC':
                Stored_condition = f'{responsedata['expression'] if responsedata['expression'] else ''} {responsedata['conditionOP']} {responsedata['condition']}'.strip()
                self.stick_data[self.Response_list.insert('','end',iid=iid,text=Stored_condition,values=(responsedata['address'],responsedata['value'],responsedata['delay']))] = responsedata
            elif Sticktype == 'VRC':
                match Trigger:
                    case 'Invite':condition = f'{responsedata['user']} : {responsedata['world']}'
                    case 'Avatar changed':condition = f'{responsedata['user']} : {responsedata['avatar']}'
                    case 'User joined' | 'User left' | 'Invite request' | 'Friend requests':condition = responsedata['user']
                self.stick_data[self.Response_list.insert('','end',iid=iid,text=condition,values=(responsedata['address'],responsedata['value'],responsedata['delay']))] = responsedata
            else:
                 print('Error loading:\nUnimplemented Type')