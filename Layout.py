import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog
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
style.configure('TCombobox')
style.map('TCombobox',fieldbackground=[('disabled','#222222')])
style.configure('TLabelframe',bordercolor='#632646')
style.configure('TButton',foreground='#FF5F93',background='#222222',width=20)
style.map('TButton',background=[('active','#111111')])
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
    location_label.set(Selected_Folder)
    Update_dir(Selected_Folder)

def ctrlC_workaround(event):
    try:
        selected_text = event.widget.get("sel.first", "sel.last")
        event.widget.clipboard_clear()
        event.widget.clipboard_append(selected_text)
    except tk.TclError:
        pass 
    return "break"

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
