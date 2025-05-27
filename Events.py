
import ttkbootstrap as ttk
import re
from ttkbootstrap.tooltip import ToolTip

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
        
        
class Eventi(ttk.Labelframe):
        #--------------IMPORTANT------------------
        #  Response_list stores all saved conditional responses defined by the user.
        #  The Set function contains rules and conditions for how conditions and responses are saved to Response_list.
        #  Eveything else in this class are UI element's and logic related to those elements.
    Color = '#FF5F93'
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

    def  __init__(self,parent,Id,controller,Title,triggers):
        super().__init__(parent)
        
        self.controller = controller
        self.Id = Id
        self.triggers = triggers
        self.label = aug(self,'Int')
        self.is_user_var = ttk.BooleanVar()
        self.is_ava_var = ttk.BooleanVar()
        self.stick_data = {}
        self.configure(labelwidget=self.label,labelanchor='ne',height=50,style='Tab.TLabelframe')
        
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        Header_frame = ttk.Frame(self)
        self.body = ttk.Frame(self)

        Header_frame.grid(row=0,column=0,sticky='nsew')
        self.body.grid(row=1,column=0,sticky='nsew')

        Header_frame.rowconfigure(0,weight=1)
        Header_frame.columnconfigure(0,weight=1)
        self.body.rowconfigure([0,1,2,3],weight=1)
        self.body.columnconfigure([0,1],weight=0,minsize=200)
        self.body.columnconfigure(2,weight=1)

        def Set():
            stick_type = self.Id[1]
            Trigger = self.Trigger.get()
            entry_type = Eventi.REQUIRED_FIELDS.get(stick_type,{})
            required = entry_type.get(Trigger,entry_type.get('*',[]))
            
            data = {
                'trigger':self.Trigger.get(),
                'user':user_name.get() if stick_type == 'VRC' else None,
                'avatar':avatar.get() if stick_type == 'VRC' and self.Trigger.get() == 'Avatar changed' else None,
                'timestamp':None,
                'message':None,
                'condition':Trigger_condition.get() if stick_type == 'OSC' else None,
                'conditionOP': Condition_operator.get() if stick_type == 'OSC' else None,
                'address':Response_address.get(),
                'value':Response_value.get(),
                'delay':Response_delay.get(),
            }
            
            if stick_type == 'VRC':
                if self.is_user_var.get(): data['user'] = 'ANY'
                if self.is_ava_var.get(): data['avatar'] = 'ANY'
                if self.is_ava_var.get() == '': data['avatar'] = None
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

        def Move(v):
            Item = self.Response_list.selection()
            Index = self.Response_list.index(Item)
            Last = len(self.Response_list.get_children())
            if v == 'u':
                self.Response_list.move(Item,'',Index-1)
            elif v == 'd':
                self.Response_list.move(Item,'',Index+1)
            elif v =='t':
                self.Response_list.move(Item,'',0)
            elif v =='b':
                self.Response_list.move(Item,'',Last)
        
        def Remove():
            Selected_item = self.Response_list.selection()
            if Selected_item:
                self.Response_list.delete(Selected_item)

        def Response_list_select(_):
            if self.Response_list.selection():
                Response_save.configure(text='Overwrite')
                List_remove.configure(state='normal')
                List_orderup.configure(state='normal')
                List_orderdown.configure(state='normal')
                List_ordertop.configure(state='normal')
                List_orderbottom.configure(state='normal')
            else:
                Response_save.configure(text='Save')
                List_remove.configure(state='disabled')
                List_orderup.configure(state='disabled')
                List_orderdown.configure(state='disabled')
                List_ordertop.configure(state='disabled')
                List_orderbottom.configure(state='disabled')

        def No_empty_trigger(_):
            if not self.Trigger.get():
                self.Trigger.set(Title)
        
        def Trigger_set(_):
            Trigger = self.Trigger.get()
            if Trigger == 'Notifications':
                self.Response_list.heading('#0',text='Type & Name',anchor='w')
                vrclabel.configure(text='From user/group',foreground=self.Color,font=('','10'))
                vrclabel.grid(row=1,column=0,sticky='s')
                user_name.grid(row=2,column=0,sticky='s',padx=[0,0],pady=[0,0])
                is_user.grid(row=2,column=0,sticky='n',padx=[0,0],pady=[0,5])
                world_invite.grid(row=1,column=0,sticky='nw',padx=[5,5],pady=[0,0])
                group_invite.grid(row=1,column=0,sticky='ne',padx=[5,5],pady=[0,0])
                join_request.grid(row=1,column=0,sticky='nw',padx=[5,5],pady=[16,0])
                group_posts.grid(row=1,column=0,sticky='ne',padx=[5,11],pady=[16,0])

            elif Trigger == 'Friend requests':
                self.Response_list.heading('#0',text='Name',anchor='w')
                vrclabel.configure(text='From User :',foreground='', font=('','9'))
                vrclabel.grid(row=1,column=0,sticky='n',padx=[0,60],pady=[0,5])
                is_user.grid(row=1,column=0,sticky='n',padx=[60,0],pady=[3,0])
                user_name.grid(row=1,column=0,sticky='s',padx=[0,0],pady=[0,0])
 
            elif Trigger in ('User joined', 'User left'):
                self.Response_list.heading('#0',text='Name',anchor='w')
                vrclabel.configure(text='User :',foreground='', font=('','9'))
                vrclabel.grid(row=1,column=0,sticky='n',padx=[0,60],pady=[0,5])
                is_user.grid(row=1,column=0,sticky='n',padx=[60,0],pady=[3,0])
                user_name.grid(row=1,column=0,sticky='s',padx=[0,0],pady=[0,0])

            elif Trigger == 'Avatar changed':
                self.Response_list.heading('#0',text='Name : Avatar',anchor='w')
                vrclabel.configure(text='User :',foreground='', font=('','9'))
                vrclabel.grid(row=1,column=0,sticky='n',padx=[0,60],pady=[0,5])
                is_user.grid(row=1,column=0,sticky='n',padx=[60,0],pady=[3,0])
                user_name.grid(row=1,column=0,sticky='s',padx=[0,0],pady=[0,0])
                avatar_label.grid(row=2,column=0,sticky='n',padx=[0,60],pady=[0,5])
                is_avatar.grid(row=2,column=0,sticky='n',padx=[60,0],pady=[3,0])
                avatar.grid(row=2,column=0,sticky='s',pady=[0,0])
            else:
                print('Error:\nCouldnt determine event type')

        def Reset_headings(_):
            Selected_item = self.Response_list.selection()
            if Selected_item:self.Response_list.selection_remove(Selected_item)
            self.Response_list.column('#0',width=100)
            self.Response_list.column('Address',width=100)
            self.Response_list.column('Value',width=50)
            self.Response_list.column('Delay',width=50)

        def Validate_osc_entry(entry):
            return entry == "" or bool(Eventi.number_re.match(entry)) if Response_address.get() != '/avatar/change' else True
        vcmd = self.register(Validate_osc_entry)

        def is_user_check():
            if self.is_user_var.get(): user_name.configure(state='disabled')
            else: user_name.configure(state='normal')
        def is_ava_check():
            if self.is_ava_var.get(): avatar.configure(state='disabled')
            else: avatar.configure(state='normal')
        
        def unbind_scroll(event):
            event.widget.bind("<MouseWheel>", lambda e: 'break')

        sep1 = ttk.Separator(self.body,orient='horizontal')
        sep2 = ttk.Separator(self.body,orient='vertical')
#----------------------------------------------------------------------------------------------------------------------------------------

        self.Response_list = ttk.Treeview(self.body,columns=['Address','Value','Delay'],selectmode='browse',height=8,style='L.Treeview')

#----------------------------------------------------------------------------------------------------------------------------------------
        self.Trigger = ttk.Combobox(Header_frame,justify='center',values=self.triggers,style='Label.TCombobox',width=45,state='disabled')
        self.Trigger.set(Title)
        self.Trigger.bind('<FocusOut>',No_empty_trigger)
        self.Trigger.bind('<Enter>',unbind_scroll)
        
        if self.Id[1] == 'OSC':
            self.Trigger.configure(state='normal')
            self.Response_list.heading('#0',text='Condition',anchor='w')

            value_label = ttk.Label(self.body,text='Value')
            Trigger_condition = ttk.Entry(self.body,width=8,validate='key',validatecommand=(vcmd,'%P'))
            Condition_operator = ttk.Combobox(self.body,values=['=','>','<'],width=2,state='readonly')
            Condition_operator.bind('<Enter>',unbind_scroll
)
            Condition_operator.set('=')
            self.Response_list.heading('#0',text='Condition',anchor='w')

            value_label.grid(row=2,column=0,sticky='n')
            Trigger_condition.grid(row=2,column=0,sticky='s')
            Condition_operator.grid(row=1,column=0,sticky='n')

        if self.Id[1] == 'VRC':
            vrclabel = ttk.Label(self.body,text='')
            user_name = ttk.Entry(self.body,width=20)
            is_user = ttk.Checkbutton(self.body,text='Any',variable=self.is_user_var,command=is_user_check)
            avatar = ttk.Entry(self.body)
            avatar_label = ttk.Label(self.body,text='Avatar :')
            is_avatar = ttk.Checkbutton(self.body,text='Any',variable=self.is_ava_var,command=is_ava_check)
            world_invite = ttk.Radiobutton(self.body,text='World Invite')
            group_invite = ttk.Radiobutton(self.body,text='Group Invite')
            join_request = ttk.Radiobutton(self.body,text='Join Request')
            group_posts = ttk.Radiobutton(self.body,text='Group Post')
            Trigger_set('')
        
        Condition_label = ttk.Label(self.body,text='Condition',foreground=self.Color,font=('','10'))
        Response_label = ttk.Label(self.body,text='Response',foreground=self.Color,font=('','10'))
        Response_address = ttk.Combobox(self.body,values=controller.Response_parameters)
        Address_label = ttk.Label(self.body,text='Address')
        Response_value = ttk.Entry(self.body,width=8,validate='key',validatecommand=(vcmd,'%P'))
        Value_label = ttk.Label(self.body,text='Value')
        Response_delay = ttk.Entry(self.body,width=4)
        Delay_label = ttk.Label(self.body,text='Delay')
        Response_save = ttk.Button(self.body,text='Save',command=Set)
        List_remove = ttk.Button(self.body,text='Remove',width=7,command=Remove,state='disabled')
        List_orderup = ttk.Button(self.body,text='▲',width=2,command=lambda:Move('u'),state='disabled',padding=[2,1,3,1])
        List_orderdown = ttk.Button(self.body,text='▼',width=2,command=lambda:Move('d'),state='disabled',padding=[2,1,3,1])
        List_ordertop = ttk.Button(self.body,text='⩞',width=2,command=lambda:Move('t'),state='disabled',padding=[2,1,3,1])
        List_orderbottom = ttk.Button(self.body,text='⩣',width=2,command=lambda:Move('b'),state='disabled',padding=[2,1,3,1])

        self.Response_list.column('#0',anchor='w',minwidth=68,width=68,stretch=False) if '/avatar/parameters/' in self.triggers else self.Response_list.column('#0',anchor='w',minwidth=68,width=100,stretch=True)
        
        self.Response_list.column('Value',anchor='center',width=50,minwidth=50,stretch=False)
        self.Response_list.column('Delay',anchor='center',width=50,minwidth=50,stretch=False)
        self.Response_list.column('Address',anchor='w',width=100,minwidth=60)
        self.Response_list.heading('Address',text='Address',anchor='center')
        self.Response_list.heading('Value',text='Value')
        self.Response_list.heading('Delay',text='Delay')

        self.Response_list.bind("<<TreeviewSelect>>", Response_list_select)
        self.Response_list.bind('<ButtonPress-1>',Reset_headings)
        Response_address.bind('<Enter>',unbind_scroll)
    
        sep1.grid(row=0,column=0,sticky='new',columnspan=3)
        sep2.grid(row=0,column=0,sticky='nse',rowspan=4,pady=[0,5])

        self.Response_list.grid(row=0,column=2,sticky='nsew',rowspan=4)
        self.Trigger.grid(row=0,column=0,sticky='n')

        Condition_label.grid(row=0,column=0,sticky='n',pady=[5,0])
        Response_label.grid(row=0,column=1,sticky='n',pady=[5,0])
        Response_address.grid(row=1,column=1,sticky='s',pady=[5,0])
        Address_label.grid(row=1,column=1,sticky='n',pady=[0,5])
        Response_value.grid(row=2,column=1,sticky='s',padx=[0,60],pady=[5,0])
        Value_label.grid(row=2,column=1,sticky='n',padx=[0,60],pady=[0,5])
        Response_delay.grid(row=2,column=1,sticky='s',padx=[50,0],pady=[5,0])
        Delay_label.grid(row=2,column=1,sticky='n',padx=[50,0],pady=[0,5])
        Response_save.grid(row=3,column=0,columnspan=2,sticky='s',pady=[0,5])

        List_remove.grid(row=3,column=2,sticky='s',pady=[0,5],padx=[0,0])
        List_orderup.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[0,90])
        List_orderdown.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[90,0])
        List_ordertop.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[0,135])
        List_orderbottom.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[135,0])

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
             print('Error saving:\nUnimplemented Type')