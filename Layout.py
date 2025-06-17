import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap import scrolled as stk
from ttkbootstrap.constants import *
from Persistence import Directory, Update_dir

Root = tk.Tk()
Root.title("app")
Root.geometry("900x500")
Root.minsize(900, 500)
Root.columnconfigure(0, weight=0)
Root.columnconfigure(1, weight=1)
Root.rowconfigure(0, weight=1)
style = ttk.Style("darkly")
style.colors.set('primary', '#632646')
style.colors.set('light', '#82516a')
Primary = style.colors.get('primary')
light = style.colors.get('light')
#----------------------------Styling
style.layout("TButton", [('Button.border', {'sticky': 'nswe', 'children': [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})]})])
style.configure('TButton',foreground='#FF5F93',background='#222222',width=20)
style.map('TButton',background=[('active','#111111')])
style.configure('TEntry')
style.map('TEntry',fieldbackground=[('disabled','#222222')])
#Settings button layout
style.layout("setting.TButton", [('Button.label', {'sticky': 'nswe'})])
style.configure("setting.TButton",background='#222222',relief="flat",font=("", 18))
style.map("setting.TButton",background=[("active", "#222222")],foreground=[('active',Primary)])
#other button
style.layout("c.TButton", [('Button.label', {'sticky': 'nswe'})])
style.configure("c.TButton",background='#222222',relief="flat",font=("", 10,))
style.map("c.TButton",background=[("active", "#222222")],foreground=[('active',Primary)])
#label combobox
style.layout('Label.TCombobox',[("Combobox.downarrow",{"side": tk.RIGHT, "sticky": tk.S},),("Combobox.padding",{"expand": "1","sticky": tk.NSEW,"children": [("Combobox.textarea",{"sticky": tk.NSEW},)],},),])
style.configure('Label.TCombobox',background='#222222')
style.configure('event.TCombobox',padding=[0,0,0,0])
style.configure('TCombobox')
style.map('TCombobox',fieldbackground=[('disabled','#222222')])
style.configure('TLabelframe',bordercolor='#632646')

style.configure("Treeview",rowheight=50,relief='solid')
style.map('Treeview',foreground=[('selected','#FF5F93'), ('!selected','#FF5F93')],background=[('selected','#171717'),('!selected','#222222')],borderwidth=[('selected',1),('!selected',1),('hover',1)],bordercolor=[('selected','#632646'),('!selected','#632646')])
style.configure('L.Treeview',rowheight=20)
style.configure('VL.Treeview',rowheight=25)
style.configure('Tab.TFrame',background='#171717')
style.configure('Tab.TLabelframe',background='#171717',labeloutside=True)
style.configure('Tab.TLabelframe.Label',background='#171717')
style.configure('Tab.TNotebook',tabposition='wn',tabmargins=[0,10,0,10])
style.configure('Tab.TNotebook.Tab')
#----------------------------Functions
location_var = ttk.StringVar(value=Directory())

def Get_folder():
    Selected_Folder = filedialog.askdirectory(mustexist=True,)
    if not Selected_Folder:
        return
    location_var.set(Selected_Folder)
    Update_dir(Selected_Folder)

def ctrlC_workaround(event):
    try:
        selected_text = event.widget.get("sel.first", "sel.last")
        event.widget.clipboard_clear()
        event.widget.clipboard_append(selected_text)
    except tk.TclError:
        pass 
    return "break"

def Message_display(address,message,text = None):
    Log_display.insert('end',f"{text} {address} {message}\n")
    num_lines = int(Log_display.index('end-1c').split('.')[0])
    if num_lines > 500:
        Log_display.delete('1.0', '5.0')
    Log_display.yview('end')

#----------------------------Tab area
TabSpace = ttk.Frame(Root)
TabSpace.columnconfigure(0, weight=1)
TabSpace.rowconfigure(0, weight=1)
TabSpace.grid(row=0,column=1,sticky="nsew",)

#----------------------------Tab List
Object_list = ttk.Treeview(Root,show='tree',height=6,selectmode='browse',style='Treeview')
Object_list.grid(column=0, row=0, sticky='nsw', pady=(4,4),padx=(4,0))

#------Button BG
button_bg = ttk.Frame(Root,padding=2)
button_bg.grid(row=0,column=0,sticky='sew',padx=[8,4],pady=[0,8])
button_bg.columnconfigure(0,weight=1)
button_bg.rowconfigure(0,weight=1,minsize=35)
button_bg.rowconfigure(1,weight=1,minsize=35)

#------New tab button
Add_Tab = ttk.Button(button_bg,text='Add New Controler')
Add_Tab.grid(row=0,column=0,sticky='nsew',pady=[0,2])

#------Settings Button
Settings_button = ttk.Button(button_bg,text='Settings')
Settings_button.grid(row=1,column=0,sticky='nsew',pady=[2,0])

#----------------------------Settings

#------Pages
Configuration = ttk.Notebook(TabSpace)
Configuration.grid(row=0,column=0,sticky='nsew',padx=(2,4),pady=(4,4))

#------Settings page
Basic_settings = ttk.Frame(Configuration)
Configuration.add(Basic_settings,text='Settings',sticky='nsew')
Basic_settings.rowconfigure([0,1],weight=0)
Basic_settings.rowconfigure(2,weight=1)
Basic_settings.columnconfigure([0,1,2],weight=1)

#------Address entry
Address_frame = ttk.Labelframe(Basic_settings,text='ip and ports',labelanchor='n')
Address_frame.grid(row=0,column=1,sticky='n',pady=(0,0))
Address_frame.rowconfigure([0,1],weight=1)
Address_frame.columnconfigure([0,1],weight=1)

address_label = ttk.Label(Address_frame,text='                    IP                                          Port')
address_label.grid(row=0,column=0,columnspan=2,sticky='nsew',padx=(5,5))

Ip_entry = ttk.Entry(Address_frame,justify='center',width=20)
Ip_entry.grid(row=1,column=0,sticky='nsew',padx=(5,2),pady=(0,5))

Port_entry = ttk.Entry(Address_frame,justify='center',width=20)
Port_entry.grid(row=1,column=1,sticky='nsew',padx=(2,5),pady=(0,5))

if not Ip_entry.get():
    Ip_entry.insert(0,'127.0.0.1')

if not Port_entry.get():
    Port_entry.insert(0,'9000')

#------File Location
Location_frame = ttk.Labelframe(Basic_settings,text='Config Location',labelanchor='n',padding=10)
Location_frame.grid(row=1,column=0,columnspan=3,sticky='n')

location_label = ttk.Label(Location_frame,textvariable=location_var)
location_label.grid(row=0,column=1,sticky='n')

Location_button = ttk.Button(Location_frame,text='Change config folder',command=Get_folder)
Location_button.grid(row=1,column=1,sticky='s')

#------Activity log

Log_frame = ttk.Frame(Basic_settings)
Log_frame.rowconfigure(0,weight=1)
Log_frame.columnconfigure(0,weight=1)
Log_frame.grid(row=2,column=0,columnspan=3,sticky='nsew')

Log_display = tk.Text(Log_frame,state='normal',relief='flat',wrap='word',maxundo=1,autoseparators=True,undo=False,spacing3=4,font=('',10))
Log_display_scroll = ttk.Scrollbar(Log_frame,command=Log_display.yview,bootstyle='ROUND')
Log_display.configure(yscrollcommand=Log_display_scroll.set)
Log_display.bind("<Key>", lambda e: 'break' ) 
Log_display.bind("<Button-3>", lambda e: "break")
Log_display.bind("<Control-c>", ctrlC_workaround)
Log_display_scroll.grid(row=0,column=0,sticky='nse',pady=6,padx=6)
Log_display.grid(row=0,column=0,sticky='nsew',padx=2,pady=2)

class Tabi_layout(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)

        self.Stick_space = stk.ScrolledFrame(self,style='Tab.TFrame',padding=[5,35,15,0])
        Spacer_frame = ttk.Frame(self,height=14)
        self.Header_button = ttk.Button(Spacer_frame,style='c.TButton',text='Collapse',width=8)
        Header_seperator = ttk.Separator(self,orient='horizontal',bootstyle='PRIMARY')
        self.Header_frame = ttk.Frame(self,padding=0)
        self.Avatar = ttk.Combobox(self.Header_frame,width=25,state='readonly')
        filterlabel = ttk.Label(self.Header_frame,text='Filter')
        self.filter = ttk.Entry(self.Header_frame)
        self.filter_enable = ttk.Button(self.Header_frame,text='Enable',width=8)
        self.filter_disable = ttk.Button(self.Header_frame,text='Disable',width=8)
        self.Controller_settings_button = ttk.Button(self.Header_frame,style='setting.TButton',text='❌',width=3,command=lambda:self.kill(self.id))
        self.default_parameters_filter = ttk.Treeview(self.Header_frame,height=8,style='L.Treeview')
        self.default_parameters_filter.column('#0',width=240)
        self.default_parameters_filter.heading('#0',text='Default avatar parameters',anchor='n')
        self.learned_parameters_filter = ttk.Treeview(self.Header_frame,height=8,style='L.Treeview')
        self.learned_parameters_filter.column('#0',width=240)
        self.learned_parameters_filter.heading('#0',text='Custom avatar parameters',anchor='n')

        self.Add_event_button = ttk.Button(self,text='Add Event')
        self.Title = ttk.Combobox(self,width=30,style='event.TCombobox')
        self.selection1 = ttk.Radiobutton(self,padding=[2,0,2,0],text='OSC',value='OSC',bootstyle='outline-toolbutton')
        self.selection2 = ttk.Radiobutton(self,padding=[2,0,2,0],text='VRC',value='VRC',bootstyle='outline-toolbutton')
        self.selection3 = ttk.Radiobutton(self,padding=[2,0,2,0],text='SYS',value='SYS',bootstyle='outline-toolbutton',state='disabled')
        self.selection4 = ttk.Radiobutton(self,padding=[2,0,2,0],text='NET',value='NET',bootstyle='outline-toolbutton',state='disabled')

        self.Stick_space.container.configure(style='Tab.TFrame')
        self.Stick_space.grid(row=1,column=0,sticky='nsew')
        self.Stick_space.columnconfigure(0,weight=1)
        self.Stick_space.vscroll.pack_configure(side='right',fill='y',pady=[19,0])
        self.Stick_space.vscroll.configure(bootstyle='light-round')

        Spacer_frame.grid(row=1,column=0,sticky='new')
        self.Header_button.pack(side='right',padx=[0,2])
        Header_seperator.grid(row=1,column=0,sticky='new',pady=14)
        self.Add_event_button.grid(row=1,column=0,sticky='n')
        self.Header_frame.grid(row=0,column=0,sticky='nsew')
        self.Header_frame.rowconfigure([0,1,2,3],weight=1)
        self.Header_frame.columnconfigure([0,1,3,4],weight=1,uniform='a')
        self.Header_frame.columnconfigure(2,weight=0)
        self.selection1.grid(row=1,column=0,sticky='n',padx=[245,0],pady=[5,0])
        self.selection2.grid(row=1,column=0,sticky='n',padx=[325,0],pady=[5,0])
        self.selection3.grid(row=1,column=0,sticky='n',padx=[400,0],pady=[5,0])
        self.selection4.grid(row=1,column=0,sticky='n',padx=[475,0],pady=[5,0])
        self.Title.grid(row=1,column=0,sticky='n',padx=[0,420],pady=[5,0])
        self.Avatar.grid(row=0,column=3,sticky='ne')
        filterlabel.grid(row=1,column=2,pady=[0,10])
        self.filter.grid(row=1,column=2,sticky='s')
        self.filter_enable.grid(row=2,column=2,sticky='s',pady=[0,30])
        self.filter_disable.grid(row=2,column=2,sticky='s')
        self.default_parameters_filter.grid(row=1,column=0,sticky='nse',columnspan=2,rowspan=3,pady=[0,10])
        self.learned_parameters_filter.grid(row=1,column=3,sticky='nsw',columnspan=2,rowspan=3,pady=[0,10])
        self.Controller_settings_button.grid(row=0,column=4,sticky='ne')

class Eventi_layout(ttk.Labelframe):
    Color = '#FF5F93'
    def __init__(self,parent,sticktype,template=None):
        super().__init__(parent)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.widgets = {}
       
        self.Header_frame = ttk.Frame(self)
        self.body = ttk.Frame(self)
        self.Response_list = ttk.Treeview(self.body,columns=['Address','Value','Delay'],selectmode='browse',height=8,style='L.Treeview')
        self.Trigger = ttk.Combobox(self.Header_frame,justify='center',style='Label.TCombobox',width=45,state='disabled')
        self.sep1 = ttk.Separator(self.body,orient='horizontal')
        self.sep2 = ttk.Separator(self.body,orient='vertical')
        self.Condition_label = ttk.Label(self.body,text='Condition',foreground=self.Color,font=('','10'))
        self.Response_label = ttk.Label(self.body,text='Response',foreground=self.Color,font=('','10'))
        self.Response_address = ttk.Combobox(self.body)
        self.Address_label = ttk.Label(self.body,text='Address')
        self.Response_value = ttk.Entry(self.body,width=8,validate='key')
        self.Response_value_avatars = ttk.Combobox(self.body,width=8)
        self.Value_label = ttk.Label(self.body,text='Value')
        self.Response_delay = ttk.Entry(self.body,width=4)
        self.Delay_label = ttk.Label(self.body,text='Delay')
        self.Response_save = ttk.Button(self.body,text='Save')
        self.List_remove = ttk.Button(self.body,text='Remove',width=7,state='disabled')
        self.List_orderup = ttk.Button(self.body,text='▲',width=2,state='disabled',padding=[2,1,3,1])
        self.List_orderdown = ttk.Button(self.body,text='▼',width=2,state='disabled',padding=[2,1,3,1])
        self.List_ordertop = ttk.Button(self.body,text='⩞',width=2,state='disabled',padding=[2,1,3,1])
        self.List_orderbottom = ttk.Button(self.body,text='⩣',width=2,state='disabled',padding=[2,1,3,1])

        for name, widgetdata in template[sticktype].items():
            widget = widgetdata['widget'](self.body,**widgetdata.get('params',{}))
            widget.grid(**widgetdata.get('grid',{}))
            self.widgets[name] = widget

        if sticktype == 'VRC':self.Response_list.column('#0',anchor='w',minwidth=68,width=68,stretch=False)
        else: self.Response_list.column('#0',anchor='w',minwidth=68,width=100,stretch=True)
        self.Response_list.column('Address',anchor='w',width=100,minwidth=60)
        self.Response_list.column('Value',anchor='center',width=100,minwidth=50,stretch=True)
        self.Response_list.column('Delay',anchor='center',width=50,minwidth=50,stretch=False)
        self.Response_list.heading('Address',text='Address',anchor='center')
        self.Response_list.heading('Value',text='Value')
        self.Response_list.heading('Delay',text='Delay')

        self.Header_frame.rowconfigure(0,weight=1)
        self.Header_frame.columnconfigure([0,1],weight=0,minsize=200)
        self.Header_frame.columnconfigure(2,weight=1)
        self.body.rowconfigure([0,1,2,3],weight=1)
        self.body.columnconfigure([0,1],weight=0,minsize=200)
        self.body.columnconfigure(2,weight=1)

        self.Header_frame.grid(row=0,column=0,sticky='nsew')
        self.body.grid(row=1,column=0,sticky='nsew')
        self.sep1.grid(row=0,column=0,sticky='new',columnspan=3)
        self.sep2.grid(row=0,column=0,sticky='nse',rowspan=4,pady=[0,5])
        self.Response_list.grid(row=0,column=2,sticky='nsew',rowspan=4)
        self.Trigger.grid(row=0,column=0,columnspan=2,sticky='n')
        self.Condition_label.grid(row=0,column=0,sticky='n',pady=[5,0])
        self.Response_label.grid(row=0,column=1,sticky='n',pady=[5,0])
        self.Response_address.grid(row=1,column=1,sticky='s',pady=[5,0])
        self.Address_label.grid(row=1,column=1,sticky='n',pady=[0,5])
        self.Response_value.grid(row=2,column=1,sticky='s',padx=[0,60],pady=[5,0])
        self.Value_label.grid(row=2,column=1,sticky='n',padx=[0,60],pady=[0,5])
        self.Response_delay.grid(row=2,column=1,sticky='s',padx=[50,0],pady=[5,0])
        self.Delay_label.grid(row=2,column=1,sticky='n',padx=[50,0],pady=[0,5])
        self.Response_save.grid(row=3,column=0,columnspan=2,sticky='s',pady=[0,5])
        self.List_remove.grid(row=3,column=2,sticky='s',pady=[0,5],padx=[0,0])
        self.List_orderup.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[0,90])
        self.List_orderdown.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[90,0])
        self.List_ordertop.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[0,135])
        self.List_orderbottom.grid(row=3,column=2,sticky='s',pady=[0,8],padx=[135,0])
