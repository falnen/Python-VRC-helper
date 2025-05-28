
import ttkbootstrap as ttk
import re
from ttkbootstrap.tooltip import ToolTip
from Layout import Eventi_layout

class aug(ttk.Frame):
    def __init__(self,parent,type):
        super().__init__(parent,width=10)
        self.parent = parent
        self.type = type
        self.configure(style='Tab.TFrame')
        self.rowconfigure(0,weight=1)
        self.columnconfigure([0,1],weight=1)

        self.Typelabel = ttk.Label(self,text='Event',foreground='#ff5f93',background='#171717',font=('','10'))
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
            self.Expandb.configure(text='➕')
        else:
            self.parent.body.grid()
            self.Expandb.configure(text='➖')

    def Destroy(self,event=None):
        self.parent.controller.stick_count -= 1
        self.parent.controller.Stick_list.pop(self.parent.Id[0])
        self.parent.destroy()

class Eventi(Eventi_layout):
    number_re = re.compile(r"^-?\d*\.?\d*$")
    REQUIRED_FIELDS = {
            'VRC': {
                'Notifications': ['user','timestamp', 'message', 'address', 'value', 'delay'],
                'User join': ['user', 'address', 'value', 'delay'],
                'User leave': ['user', 'address', 'value', 'delay'],
                'Friend requests': ['user', 'address', 'value', 'delay'],
                'Avatar changed': ['user', 'avatar', 'address', 'value', 'delay'],
            },
            'OSC': {'*': ['condition', 'address', 'value', 'delay']},
            'SYS': {'*': []},
                }
    LAYOUT_TEMPLATES = {
        'VRC': {
            'vrclabel': {'widget': ttk.Label, 'params': {"text":''}, 'grid':{'row':1,'column':0,'sticky':'n','padx':[0,60],'pady':[0,5]}},
            'name_entry': {'widget': ttk.Entry, 'params': {'width':20}, 'grid':{'row':1,'column':0,'sticky':'s','padx':[0,0],'pady':[0,0]}},
            'any_name': {'widget': ttk.Checkbutton, 'params': {'text':'Any'}, 'grid':{'row':1,'column':0,'sticky':'n','padx':[60,0],'pady':[3,0]}},
            'avatar': {'widget': ttk.Entry, 'params': {}, 'grid':{'row':2,'column':0,'sticky':'s','pady':[0,0]}},
            'avatar_label':{'widget':ttk.Label, 'params': {'text':'Avatar :'}, 'grid':{'row':2,'column':0,'sticky':'n','padx':[0,60],'pady':[0,5]}},
            'any_avatar': {'widget': ttk.Checkbutton, 'params': {'text':'Any'}, 'grid':{'row':2,'column':0,'sticky':'n','padx':[60,0],'pady':[3,0]}},
            },
        "OSC": {
                'value_label': {'widget': ttk.Label, 'params': {'text':'Value'}, 'grid':{'row':2,'column':0,'sticky':'n'}},
                'condition_entry': {'widget': ttk.Entry, 'params':{'width':8,'validate':'key'}, 'grid':{'row':2,'column':0,'sticky':'s'}},
                'condition_operator': {'widget': ttk.Combobox, 'params':{'values':['=','>','<'],'width':2,'state':'readonly'}, 'grid':{'row':1,'column':0,'sticky':'n'}}
             }
    }
    def  __init__(self,parent,Id,controller,Title,triggers):
        super().__init__(parent,triggers,Id[1],template=self.LAYOUT_TEMPLATES)
        self.controller = controller
        self.Id = Id
        self.triggers = triggers
        self.stick_data = {}
        self.name_var = ttk.BooleanVar()
        self.avatar_var = ttk.BooleanVar()
        self.label = aug(self,'Int')

        self.configure(labelwidget=self.label,labelanchor='ne',height=50,style='Tab.TLabelframe')
        self.vcmd = self.register(self.__Validate_osc_entry)
        
        self.Response_address.configure(values=controller.Response_parameters)
        self.Response_value.configure(validatecommand=(self.vcmd,'%P'))
        self.Response_save.configure(command=self.Set)
        self.List_remove.configure(command=self.Remove)
        self.List_orderup.configure(command=lambda:self.Move('u'))
        self.List_orderdown.configure(command=lambda:self.Move('d'))
        self.List_ordertop.configure(command=lambda:self.Move('t'))
        self.List_orderbottom.configure(command=lambda:self.Move('b'))
        self.Trigger.set(Title)
        self.Trigger.bind('<FocusOut>',self.No_empty_trigger)
        self.Trigger.bind('<Enter>',self.unbind_scroll)
        self.Response_list.bind("<<TreeviewSelect>>", self.Response_list_select)
        self.Response_list.bind('<ButtonPress-1>',self.Reset_headings)
        self.Response_address.bind('<Enter>',self.unbind_scroll)

        if self.Id[1] == 'OSC':
            self.Response_list.column('#0',anchor='w',minwidth=68,width=100,stretch=True)
            self.Trigger.configure(state='normal')
            self.Response_list.heading('#0',text='Condition',anchor='w')
            self.widgets['condition_entry'].configure(validatecommand=(self.vcmd,'%P'))
            self.widgets['condition_operator'].bind('<Enter>',self.unbind_scroll)
            self.widgets['condition_operator'].set('=')
            for widget in self.widgets.values():
                widget.grid()

        if self.Id[1] == 'VRC':
            self.Response_list.column('#0',anchor='w',minwidth=68,width=68,stretch=False)
            self.widgets['any_name'].configure(variable=self.name_var,command=self.is_user_check)
            self.widgets['any_avatar'].configure(variable=self.avatar_var,command=self.is_ava_check)
            for widget in self.widgets.values():
                widget.grid()
            match Title:
                case 'User joined' | 'User left':
                    self.Response_list.heading('#0',text='Name',anchor='w')
                    self.widgets['vrclabel'].configure(text='User :',foreground='', font=('','9'))
                    for name in ('avatar', 'any_avatar'):
                        self.widgets.pop(name, None).destroy()
                case 'Avatar changed':
                    self.Response_list.heading('#0',text='Name : Avatar',anchor='w')
                    self.widgets['vrclabel'].configure(text='User :',foreground='', font=('','9'))
    
            #world_invite = ttk.Radiobutton(self.body,text='World Invite')
            #group_invite = ttk.Radiobutton(self.body,text='Group Invite')
            #join_request = ttk.Radiobutton(self.body,text='Join Request')
            #group_posts = ttk.Radiobutton(self.body,text='Group Post')

    def Set(self):
        stick_type = self.Id[1]
        Trigger = self.Trigger.get()
        entry_type = Eventi.REQUIRED_FIELDS.get(stick_type,{})
        required = entry_type.get(Trigger,entry_type.get('*',[]))
        self.name_var
        data = {
            'trigger':self.Trigger.get(),
            'user':self.widgets['name_entry'].get() if self.widgets.get('name_entry') else None,
            'avatar':self.widgets['avatar'].get() if self.widgets.get('avatar') and self.Trigger.get() == 'Avatar changed' else None,
            'timestamp':None,
            'message':None,
            'condition':self.widgets['condition_entry'].get() if self.widgets.get('condition_entry') else None,
            'conditionOP': self.widgets['condition_operator'].get() if self.widgets.get('condition_operator') else None,
            'address':self.Response_address.get(),
            'value':self.Response_value.get(),
            'delay':self.Response_delay.get(),
        }
        
        if stick_type == 'VRC':
            if self.name_var.get(): data['user'] = 'ANY'
            if self.avatar_var.get(): data['avatar'] = 'ANY'
            if self.avatar_var.get() == '': data['avatar'] = None
        if missing := [key for key in required if not data.get(key)]: return
        
        item = self.Response_list.selection()
        if stick_type == 'OSC':
            if item:
                self.stick_data[item[0]] = data
                self.Response_list.item(item,text=f'{data["conditionOP"]} {data["condition"]}',values=(data['address'],data['value'],data['delay']))
            else: self.stick_data[self.Response_list.insert('','end',text=f'{data["conditionOP"]} {data["condition"]}',values=(data['address'],data['value'],data['delay']))] = data
        elif stick_type == 'VRC':
            if Trigger == 'Notifications':
                pass
            if item:
                self.stick_data[item[0]] = data
                self.Response_list.item(item,text=data['user'] if Trigger != 'Avatar changed' else f'{data['user']} : {data['avatar']}',values=(data['address'],data['value'],data['delay']))
            else: self.stick_data[self.Response_list.insert('','end',text=data['user'] if Trigger != 'Avatar changed' else f'{data['user']} : {data['avatar']}',values=(data['address'],data['value'],data['delay']))] = data
        else:
            print('Error saving:\nUnimplemented Type')
    def Move(self,v):
        Item = self.Response_list.selection()
        Index = self.Response_list.index(Item)
        Last = len(self.Response_list.get_children())
        match v:
            case 'u':self.Response_list.move(Item,'',Index-1)
            case 'd':self.Response_list.move(Item,'',Index+1)
            case 't':self.Response_list.move(Item,'',0)
            case 'b':self.Response_list.move(Item,'',Last)
    def Remove(self):
        if Selected_item := self.Response_list.selection():
            self.Response_list.delete(Selected_item)
    def Response_list_select(self,_):
        if self.Response_list.selection():
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
    def No_empty_trigger(self,_):
        if not self.Trigger.get():
            self.Trigger.set(self.triggers[0])
    def Reset_headings(self,_):
        Selected_item = self.Response_list.selection()
        if Selected_item:self.Response_list.selection_remove(Selected_item)
        self.Response_list.column('#0',width=100)
        self.Response_list.column('Address',width=100)
        self.Response_list.column('Value',width=50)
        self.Response_list.column('Delay',width=50)
    def is_user_check(self):
        if self.name_var.get(): self.widgets['name_entry'].configure(state='disabled')
        else: self.widgets['name_entry'].configure(state='normal')
    def is_ava_check(self):
        if self.avatar_var.get(): self.widgets['avatar'].configure(state='disabled')
        else: self.widgets['avatar'].configure(state='normal')
    def unbind_scroll(self,event):
        event.widget.bind("<MouseWheel>", lambda e: 'break')
    def __Validate_osc_entry(self,entry):
        return entry == "" or bool(Eventi.number_re.match(entry)) if self.Response_address.get() != '/avatar/change' else True
    def Load(self,data):
        Responsestuple =  data.popitem()
        Trigger =  data.popitem()
        try:datatype = data.popitem()
        except:return
        iid = Responsestuple[0]
        Responses = Responsestuple[1]
        self.stick_data[iid] = Responses
        if datatype[1] == 'OSC':
            self.Response_list.insert('','end',iid=iid,text=f'{Responses["conditionOP"]} {Responses["condition"]}',values=(Responses['address'],Responses['value'],Responses['delay']))
        elif datatype[1] == 'VRC':
            if Trigger == 'Notifications':
                pass
            self.Response_list.insert('','end',iid=iid,text=Responses['user'] if Trigger != 'Avatar changed' else f'{Responses['user']} : {Responses['avatar']}',values=(Responses['address'],Responses['value'],Responses['delay']))
        else:
             print('Error loading:\nUnimplemented Type')