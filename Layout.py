import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap import scrolled as stk
from ttkbootstrap.dialogs import colorchooser
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.style import ThemeDefinition
from ttkbootstrap.constants import *
from Persistence import Directory, Update_dir
from uuid import uuid4

Root = tk.Tk()
Root.title("app")
Root.geometry("900x500")
Root.minsize(900, 500)
Root.columnconfigure(0, weight=0)
Root.columnconfigure(1, weight=1)
Root.rowconfigure(0, weight=1)
Root.rowconfigure([1,2], weight=0)
style = ttk.Style("darkly")
style.colors.set('primary', '#632646')
style.colors.set('secondary', '#FF5F93')
style.colors.set('info', '#333333')
style.layout("danger.TButton", [('Button.border', {'sticky': 'nswe', 'children': [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})]})])
style.layout("arrow.TButton", [('Button.border', {'sticky': 'nswe', 'children': [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})]})])
style.layout("setting.TButton", [('Button.label', {'sticky': 'nswe'})])
style.layout("c.TButton", [('Button.label', {'sticky': 'nswe'})])
style.layout("pop.TButton", [('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [('Button.focus', {'sticky': 'nswe', 'children': [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})]})]})])
style.layout('Label.TCombobox',[("Combobox.downarrow",{"side": tk.RIGHT, "sticky": tk.S},),("Combobox.padding",{"expand": "1","sticky": tk.NSEW,"children": [("Combobox.textarea",{"sticky": tk.NSEW},)],},),])
style.layout('TButton',[('Button.border', {'sticky': 'nswe', 'border': '1', 'children': [('Button.padding', {'sticky': 'nswe', 'children': [('Button.label', {'sticky': 'nswe'})]})]})])
#----------------------------Styling

def style_widgets():
    Primary = style.colors.get('primary')
    Secondary = style.colors.get('secondary')
    style.colors.set('light', style.colors.update_hsv(Secondary,sd=-0.3,vd=-0.3))
    style.configure('TButton',foreground=Secondary,background='#222222',bordercolor=Primary,darkcolor=Primary,lightcolor=Primary,width=20)
    style.map('TButton',background=[('active','#111111')])
    
    style.configure('danger.TButton',foreground=style.colors.get('danger'),background='#222222',width=20)
    style.map('danger.TButton',background=[('active','#111111')])
    
    style.configure('arrow.TButton',foreground=Secondary,background='#222222',font=('',10),width=20)
    style.map('arrow.TButton',background=[('active','#111111')])
    style.configure('TEntry')
    style.map('TEntry',fieldbackground=[('disabled','#222222')])
    #Settings button layout
    
    style.configure("setting.TButton",background='#222222',relief="flat",font=("", 16))
    style.map("setting.TButton",background=[("active", "#222222")],foreground=[('active',Primary)])
    #other button

    style.configure("c.TButton",background='#222222',relief="flat",font=("", 10,))
    style.map("c.TButton",background=[("active", "#222222")],foreground=[('active',Primary)])
    #otherother button
    
    style.configure("pop.TButton",background='#171717',relief="flat",font=("", 10,))
    style.map("pop.TButton",foreground=[('active',Secondary), ('!active',Secondary)],background=[('active','#070707'),('!active','#171717')])
    #label combobox
    
    style.configure('TCombobox',bordercolor=Primary,arrowcolor=Secondary,focusfill=Primary)
    style.map('TCombobox',fieldbackground=[('disabled','#222222'),('readonly','#222222')],bordercolor=[('focus',Primary)],arrowcolor=[('focus',Primary)],background=[('readonly','#222222')])
    style.configure('Label.TCombobox',background='#222222')
    style.configure('event.TCombobox',padding=[0,0,0,0])

    style.configure('TLabelframe',bordercolor=Primary,lightcolor=Primary,darkcolor=Primary)

    style.configure('alt.TLabel',foreground=Secondary,background='#171717',font=('','10'))
    style.configure('alt2.TLabel',foreground=Secondary,background='#222222',font=('','10'))

    style.configure("Treeview",rowheight=50,relief='solid')
    style.map('Treeview',foreground=[('selected',Secondary), ('!selected',Secondary)],background=[('selected','#171717'),('!selected','#222222')],borderwidth=[('selected',1),('!selected',1),('hover',1)],bordercolor=[('selected',Primary),('!selected',Primary)])
    style.configure('L.Treeview',rowheight=20)
    style.configure('VL.Treeview',rowheight=25)
    style.configure('Tab.TFrame',background='#171717')
    style.configure('pop.TFrame',background=Primary)
    style.configure('Tab.TLabelframe',background='#171717',bordercolor=Primary,lightcolor=Primary,darkcolor=Primary,labeloutside=True)
    style.configure('Tab.TLabelframe.Label',background='#171717')
    style.configure('Tab.TNotebook',tabposition='wn',tabmargins=[0,10,0,10])
    style.configure('TCheckbutton',indicatorcolor=Primary)
    # Ensure toggle and other checkbutton variants pick up colors
    # Note: creating variant-specific styles like 'round.TCheckbutton' can trigger
    # ttkbootstrap builder errors if the builder method is unavailable. Stick to
    # the base 'TCheckbutton' to avoid creating unsupported styles.
    style.map('TCheckbutton',background=[('selected',Primary),('!selected','#222222')],foreground=[('selected',style.colors.get('light')),('!selected',Secondary)])
    style.configure('TRadiobutton',background='#222222',foreground=Secondary)
    style.map('TRadiobutton',background=[('selected',Primary),('!selected','#222222')],foreground=[('selected',style.colors.get('light')),('!selected',Secondary)])

    #Cautious Scrollbar styling... attempting this sometimes breaks the theme.
    try:
        style.configure('TScrollbar',troughcolor='#171717',background=Primary,arrowcolor=Secondary)
    except tk.TclError as e:
        if 'Duplicate element' not in str(e):
            raise
    try:
        style.configure('Vertical.TScrollbar',troughcolor='#171717',background=Primary,arrowcolor=Secondary)
    except tk.TclError as e:
        if 'Duplicate element' not in str(e):
            raise
    try:
        style.configure('Horizontal.TScrollbar',troughcolor='#171717',background=Primary,arrowcolor=Secondary)
    except tk.TclError as e:
        if 'Duplicate element' not in str(e):
            raise

    style.layout('Label.TCombobox',[("Combobox.downarrow",{"side": tk.RIGHT, "sticky": tk.S},),("Combobox.padding",{"expand": "1","sticky": tk.NSEW,"children": [("Combobox.textarea",{"sticky": tk.NSEW},)],},),])
    style.configure('TCombobox',bordercolor=Primary,arrowcolor=Secondary,focusfill=Primary)
    style.map('TCombobox',fieldbackground=[('disabled','#222222'),('readonly','#222222')],bordercolor=[('focus',Primary),('disabled','#222222')],arrowcolor=[('focus',Primary),('!focus',Secondary),('disabled',Secondary)],background=[('readonly','#222222')])
    style.configure('Label.TCombobox',background='#222222',bordercolor='#222222',arrowcolor=Secondary)
    style.map('Label.TCombobox',fieldbackground=[('disabled','#222222')],bordercolor=[('disabled','#222222')],arrowcolor=[('disabled',Secondary)])

    style.configure('TEntry',fieldbackground='#222222',bordercolor=Primary,focusfill=Primary)
    style.map('TEntry',fieldbackground=[('disabled','#222222'),('focus','#222222')],bordercolor=[('focus',Primary)])
style_widgets()
#----------------------------Functions
location_var = ttk.StringVar(value=Directory())
parameter_collect = ttk.BooleanVar(value=False)
VRC_Toggle = ttk.BooleanVar(value=True)
test_var = ttk.BooleanVar(value=False)
logvar_1 = ttk.BooleanVar(value=False)
logvar_2 = ttk.BooleanVar(value=False)
menu_buttons = {}

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

def show_custom_menu():
    mborderframe.grid(row=1,column=0,sticky='nesw', pady=(0,4),padx=(4,0))
    mborderframe.lift()
    manual_name_entry.focus()
    mborderframe.bind_all('<FocusIn>',hide_custom_menu, add='+')

def insert_avatar_button(avatar):
    if avatar in menu_buttons.keys(): return
    avatar_button = ttk.Button(mborderframe,text=avatar,style='pop.TButton')
    avatar_button.pack(padx=2, pady=1,fill='both')
    menu_buttons[avatar] = avatar_button
    return avatar_button

def hide_custom_menu(event):
    new_focus = event.widget.focus_get()
    if new_focus not in m_frame.winfo_children() and new_focus not in mborderframe.winfo_children():
        mborderframe.grid_forget()
        mborderframe.unbind_all('<FocusIn>')

class ThemeManager:
    """ This class is mostly AI generated, as my own implementation would frequently fail and i could not for the life of me figure it out.\n
    Safe theme manager: opens a color chooser, updates style colors in-place,
    and reapplies custom widget configurations without registering new themes.
    This avoids duplicate-theme registration errors and is compatible with custom layouts.
    """
    def __init__(self, style_obj):
        self.style = style_obj

    def choose_color(self, var):
        # var: 1 => primary, 2 => secondary, 3 => force white
        if var == 3:
            newcolor = '#ffffff'
        else:
            initial = self.style.colors.get('primary') if var == 1 else self.style.colors.get('secondary')
            try:
                chooser = colorchooser.ColorChooserDialog(Root, title='Palette', initialcolor=initial)
                chooser.show(wait_for_result=True)
                ret = getattr(chooser, 'result', None)
            except tk.TclError as e:
                try:
                    Message_display('Style', 'Color chooser error:', text=str(e))
                except Exception:
                    pass
                return
            if not ret:
                return
            if isinstance(ret, str):
                newcolor = ret
            else:
                newcolor = getattr(ret, 'hex', None) or str(ret)

        if var == 1:
            self.style.colors.set('primary', newcolor)
        elif var == 2:
            self.style.colors.set('secondary', newcolor)

        # Try to re-register a temporary theme to force ttkbootstrap builders
        # to re-run and update widgets that are created by builder methods
        # (combobox arrows, toggle toolbuttons, etc.). Use a unique name to
        # avoid duplicate-theme name errors.
        try:
            colors = {label: self.style.colors.get(label) for label in self.style.colors.label_iter()}
            themename = "temp_" + str(uuid4()).replace("-", "")[:12]
            definition = ThemeDefinition(themename, colors, self.style.theme_use())
            try:
                self.style.register_theme(definition)
                self.style.theme_use(themename)
            except Exception:
                # If registering fails, fall back to just reapplying widget configs
                pass

            try:
                style_widgets()
            except Exception as e:
                try:
                    Message_display('Style', 'Failed applying style:', text=str(e))
                except Exception:
                    pass
            # refresh existing widgets so builder-created elements (combobox arrows,
            # toggle toolbuttons, entry focus, etc.) update in-place
            try:
                self.refresh_widgets()
            except Exception:
                pass
        except Exception:
            # conservative fallback if colors iteration or theme registration fails
            try:
                style_widgets()
            except Exception:
                pass
            try:
                self.refresh_widgets()
            except Exception:
                pass

    def apply_colors(self):
        """Apply current `style.colors` by registering a temporary theme
        and reapplying widget-specific configurations. Use this at startup
        to force ttkbootstrap builder-generated widgets to pick up colors.
        """
        try:
            colors = {label: self.style.colors.get(label) for label in self.style.colors.label_iter()}
            themename = "startup_" + str(uuid4()).replace("-", "")[:12]
            definition = ThemeDefinition(themename, colors, self.style.theme_use())
            try:
                self.style.register_theme(definition)
                self.style.theme_use(themename)
            except Exception:
                pass
            try:
                style_widgets()
            except Exception:
                pass
        except Exception:
            try:
                style_widgets()
            except Exception:
                pass

    def refresh_widgets(self, root_widget=None):
        """Recursively reapply style names to existing widgets to force a visual refresh.
        This avoids having to destroy/recreate widgets created before a theme update.
        """
        if root_widget is None:
            root_widget = Root

        try:
            children = root_widget.winfo_children()
        except Exception:
            return

        for child in children:
            # If widget exposes a 'style' option, re-set it to force redraw
            try:
                s = child.cget('style')
            except Exception:
                s = None
            if s:
                try:
                    child.configure(style=s)
                except Exception:
                    pass

            # Keep refresh light-weight: ensure scrollbars get an orientation-specific style
            try:
                if isinstance(child, ttk.Scrollbar):
                    orient = child.cget('orient')
                    if orient and not child.cget('style'):
                        if orient.lower().startswith('v'):
                            child.configure(style='Vertical.TScrollbar')
                        else:
                            child.configure(style='Horizontal.TScrollbar')
            except Exception:
                pass

            # Recurse
            try:
                self.refresh_widgets(child)
            except Exception:
                pass

theme_manager = ThemeManager(style)
def validate_ip(P):
    if P == '' or P.replace('.', '').isdigit():
        if '..' not in P and not P.startswith('.'): 
            return True
    return False
def validate_r_port(P):
    if not P:
        r_portvar.set(0)
        return True
    if P.isdigit() and 0 <= int(P) <= 65535:
        return True
    return False
def validate_s_port(P):
    if not P:
        s_portvar.set(0)
        return True
    if P.isdigit() and 0 <= int(P) <= 65535:
        return True
    return False
vip = Root.register(validate_ip)
vrpo = Root.register(validate_r_port)
vspo = Root.register(validate_s_port)

r_ipvar = ttk.StringVar(value='127.0.0.1')
r_portvar = ttk.IntVar(value=9001)
s_ipvar = ttk.StringVar(value='127.0.0.1')
s_portvar = ttk.IntVar(value=9000)
#----------------------------Tab area
TabSpace = ttk.Frame(Root)
TabSpace.columnconfigure(0, weight=1)
TabSpace.rowconfigure(0, weight=1)
TabSpace.grid(row=0,column=1,rowspan=3,sticky="nsew",)

#----------------------------Tab List
Object_list = ttk.Treeview(Root,show='tree',height=6,selectmode='browse',style='Treeview')
Object_list.grid(column=0, row=0, sticky='nsw', pady=(4,4),padx=(4,0))

#------New tab button
Add_controller = ttk.Button(Root,text='Add New Controler',padding=8,command=show_custom_menu)
#menu_win = tk.Toplevel(Root,bg='#222222')
#menu_win.overrideredirect(True)
#menu_win.withdraw()
#menu_win.bind('<FocusOut>',hide_custom_menu)
mborderframe = ttk.Frame(Root,padding=2,style='pop.TFrame')
m_frame = ttk.Frame(mborderframe)
m_frame.pack(fill='both')
manual_name_entry = ttk.Entry(m_frame)
manual_name_label = ttk.Label(m_frame,text='Name : ')
manual_id_entry = ttk.Entry(m_frame)
manual_id_label = ttk.Label(m_frame,text='ID : ')
manual_button = ttk.Button(m_frame,text='Add Avatar')
ToolTip(manual_button,text='Avatar name and ID must match EXACTLY as they do in VRC or the controller will not work.',delay=0,bootstyle='selectbg')
manual_name_entry.grid(row=0,column=1,sticky='n',pady=[4,0],padx=[0,4])
manual_name_label.grid(row=0,column=0,sticky='n',pady=[4,0])
manual_id_entry.grid(row=1,column=1,sticky='n',pady=[4,0],padx=[0,4])
manual_id_label.grid(row=1,column=0,sticky='n',pady=[4,0])
manual_button.grid(row=2,column=0,columnspan=2,sticky='n',pady=[6,6])

Add_controller.grid(row=2,column=0,sticky='sew',padx=[4,0],pady=[0,45])

#------Settings Button
Settings_button = ttk.Button(Root,text='Settings',padding=8)
Settings_button.grid(row=2,column=0,sticky='sew',padx=[4,0],pady=[0,4])

#----------------------------Settings

#------Pages
Pages = ttk.Notebook(TabSpace)
Pages.grid(row=0,column=0,sticky='nsew',padx=(2,4),pady=(4,4))

#------Settings pages
Basic_settings = ttk.Frame(Pages)
VRC_Settings = ttk.Frame(Pages)
OSC_Settings = ttk.Frame(Pages)
Pages.add(Basic_settings,text='General',sticky='nsew')
Pages.add(OSC_Settings,text='OSC',sticky='nsew')
Pages.add(VRC_Settings,text='VRC',sticky='nsew')
Basic_settings.rowconfigure([0,1],weight=0)
Basic_settings.rowconfigure(2,weight=1)
Basic_settings.columnconfigure([0,1,2],weight=1)
VRC_Settings.rowconfigure(0,weight=1)
VRC_Settings.columnconfigure([0,1,2],weight=1)
OSC_Settings.rowconfigure([0,1,2],weight=1)
OSC_Settings.columnconfigure([0,1,2],weight=1)

#--------------------OSC Configuration

advanced_frame = ttk.Labelframe(Basic_settings,text='Advanced',padding=5)
advanced_label = ttk.Label(advanced_frame, justify='center', text='Performance', style='alt2.TLabel')
Mapall_toggle = ttk.Checkbutton(advanced_frame,variable=test_var,text='Map all OSC addresses.',bootstyle='round-toggle')
#ToolTip(Mapall_toggle, text='Disabling this settings will stop the app from automatically catching unmapped OSC messages.\nWhich will prevent avatar name, id, and parameter collection.\nMeaning all avatar controllers, and parameters will have to be input manually.',delay=0,bootstyle='selectbg')
advanced_frame.grid(row=1,column=2,sticky='se')
advanced_frame.rowconfigure((0,1,2),weight=1)
advanced_frame.columnconfigure(1,weight=1)
advanced_label.grid(row=1,column=0,sticky='n')
Mapall_toggle.grid(row=2,column=0)

#------Address entry
Address_frame = ttk.Labelframe(OSC_Settings,text='OSC Address',labelanchor='n')
Address_frame.grid(row=0,column=1,sticky='n',pady=(0,0))
Address_frame.rowconfigure([0,1,2,3,3,4,5],weight=1)
Address_frame.columnconfigure([0,1,2],weight=1)

address_label = ttk.Label(Address_frame,text='                    IP                                          Port')
address_label.grid(row=2,column=0,columnspan=3,sticky='nsew',padx=(5,5),pady=[0,5])

receive_label = ttk.Label(Address_frame,text='Receive',style='alt2.TLabel')
receive_label.grid(row=0,column=0,columnspan=3)
send_label = ttk.Label(Address_frame,text='Send',style='alt2.TLabel')
send_label.grid(row=2,column=0,columnspan=3)

rIp_entry = ttk.Entry(Address_frame,textvariable=r_ipvar,validate='key',validatecommand=(vip,'%P'),justify='center',width=20)
rIp_entry.grid(row=1,column=0,sticky='nsew',padx=(5,2),pady=(0,5))
rPort_entry = ttk.Entry(Address_frame,textvariable=r_portvar,validate='key',validatecommand=(vrpo,'%P'),justify='center',width=20)
rPort_entry.grid(row=1,column=2,columnspan=2,sticky='nsew',padx=(2,5),pady=(0,5))

sIp_entry = ttk.Entry(Address_frame,textvariable=s_ipvar,validate='key',validatecommand=(vip,'%P'),justify='center',width=20)
sIp_entry.grid(row=3,column=0,sticky='nsew',padx=(5,2),pady=(0,5))
sPort_entry = ttk.Entry(Address_frame,textvariable=s_portvar,validate='key',validatecommand=(vspo,'%P'),justify='center',width=20)
sPort_entry.grid(row=3,column=2,columnspan=2,sticky='nsew',padx=(2,5),pady=(0,5))

Server_set = ttk.Button(Address_frame,text='Set')
Server_set.grid(row=5,column=0,columnspan=3,sticky='s',pady=[0,5])
#------VRC
VRC_config_frame = ttk.Labelframe(VRC_Settings,text='Options',labelanchor='n',padding=8)
VRC_config_frame.grid(row=0,column=1,sticky='n',pady=(0,0))
VRC_config_frame.rowconfigure([0,1],weight=1)
VRC_config_frame.columnconfigure([0,1],weight=1)

vrc_enable = ttk.Checkbutton(VRC_config_frame,variable=VRC_Toggle,text='VRC Log Parser.\nDisabling this option will cause:\n- VRC Events to not work.\n- Player name to not automatically populate.\n- Avatar list to not automaticallt populate.',bootstyle='round-toggle')
vrc_enable.grid(row=0,column=0)
#------OSC
OSC_config_frame = ttk.Labelframe(OSC_Settings,text='Options',labelanchor='n',padding=12)
OSC_config_frame.grid(row=1,column=1,sticky='n',pady=(0,0))
OSC_config_frame.rowconfigure([0,1,2],weight=1,pad=8)
OSC_config_frame.columnconfigure(0,weight=1,pad=8)

acap = ttk.Checkbutton(OSC_config_frame,variable=parameter_collect,text='Automatic Avatar Parameter Collection',bootstyle='round-toggle')
acap.grid(row=2,column=0,sticky='w')
log_receive = ttk.Checkbutton(OSC_config_frame,variable=logvar_1,text='Log all received OSC messages to activity log.',bootstyle='round-toggle')
log_receive.grid(row=0,column=0,sticky='w')
log_sent = ttk.Checkbutton(OSC_config_frame,variable=logvar_2,text='Log all sent OSC messages to activity log.',bootstyle='round-toggle')
log_sent.grid(row=1,column=0,sticky='w')
#------OSC Event config



#------File Location
Location_frame = ttk.Labelframe(Basic_settings,text='Config Location',labelanchor='n',padding=10)
Location_frame.grid(row=0,column=0,columnspan=3,sticky='n')

location_label = ttk.Label(Location_frame,textvariable=location_var)
location_label.grid(row=0,column=1,sticky='n')

Location_button = ttk.Button(Location_frame,text='Change config folder',command=Get_folder)
Location_button.grid(row=1,column=1,sticky='s',pady=[5,0])

#------Color selections
Color_frame = ttk.Labelframe(Basic_settings,text='Theme Colors',labelanchor='n',padding=10)
Color_frame.grid(row=1,column=0,columnspan=3,sticky='n')

Color_label = ttk.Label(Color_frame,text='Change Theme Colors')
Color_label.grid(row=0,column=0,sticky='n',columnspan=2)

Color_button = ttk.Button(Color_frame,text='Primary',width=10,command=lambda : theme_manager.choose_color(1))
Color_button.grid(row=1,column=0,sticky='s',padx=[5,5],pady=[5,0])
Color_button2 = ttk.Button(Color_frame,text='Secondary',width=10,command=lambda : theme_manager.choose_color(2))
Color_button2.grid(row=1,column=1,sticky='s',padx=[5,5],pady=[5,0])

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
        self.Header_button = ttk.Button(self,style='c.TButton',text='Config',width=8,padding=0)
        Header_seperator = ttk.Separator(self,orient='horizontal')
        self.Header_frame = ttk.Frame(self,padding=0)
        avatar_label = ttk.Label(self.Header_frame,text='Avatar :',font=("", 10))
        self.Avatar = ttk.Combobox(self.Header_frame,width=25,state='disable')
        self.Delete_button = ttk.Button(self.Header_frame,text='Delete Controller',width=20,bootstyle='danger')
        ToolTip(self.Delete_button, text='There must always be atleast 1 controller.\nYou will be unable to delete this controller if it is the only controller.\nHold shift to delete saved avatar along with controller.\nProbably a temporary solution.',delay=0,bootstyle='selectbg')
        #self.Settings_button = ttk.Button(self.Header_frame,text='')

        self.Add_parameter_entry = ttk.Entry(self.Header_frame)
        self.Add_parameter = ttk.Button(self.Header_frame,text='Add New',width=16,padding=5)
        self.Remove_parameter = ttk.Button(self.Header_frame,text='Forget',width=16,padding=5)
        filterlabel = ttk.Label(self.Header_frame,text='Filter',font=("", 10))
        self.filter_entry = ttk.Entry(self.Header_frame)
        self.filter_enable = ttk.Button(self.Header_frame,text='Enable',width=9,padding=4,state='disable')
        self.filter_disable = ttk.Button(self.Header_frame,text='Disable',width=9,padding=4,state='disable')
        self.default_parameters_filter = ttk.Treeview(self.Header_frame,height=8,style='L.Treeview',selectmode='none')
        self.default_parameters_filter.column('#0',width=240)
        self.default_parameters_filter.heading('#0',text='Default parameters',anchor='n')
        self.learned_parameters_filter = ttk.Treeview(self.Header_frame,height=8,style='L.Treeview')
        self.learned_parameters_filter.column('#0',width=240)
        self.learned_parameters_filter.heading('#0',text='Custom parameters',anchor='n')

        self.Add_event_button = ttk.Button(self,text='Add Event')
        self.Title = ttk.Combobox(self,width=30)
        self.selection1 = ttk.Radiobutton(self,padding=[2,0,2,0],text='OSC',value='OSC',bootstyle='outline-toolbutton')
        self.selection2 = ttk.Radiobutton(self,padding=[2,0,2,0],text='VRC',value='VRC',bootstyle='outline-toolbutton')
        self.selection3 = ttk.Radiobutton(self,padding=[2,0,2,0],text='-',value='SYS',bootstyle='outline-toolbutton',state='disabled')
        self.selection4 = ttk.Radiobutton(self,padding=[2,0,2,0],text='-',value='NET',bootstyle='outline-toolbutton',state='disabled')

        self.Stick_space.container.configure(style='Tab.TFrame')
        self.Stick_space.grid(row=1,column=0,sticky='nsew')
        self.Stick_space.columnconfigure(0,weight=1)
        self.Stick_space.vscroll.pack_configure(side='right',fill='y',pady=[19,0])
        self.Stick_space.vscroll.configure(bootstyle='light-round')

        Spacer_frame.grid(row=1,column=0,sticky='new')
        self.Header_button.grid(row=1,column=0,sticky='ne',padx=[0,0],pady=[0
                                                                            ,0])
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
        self.Delete_button.grid(row=0,column=0,sticky='nw',padx=[5,0],pady=[2,2])
        #self.Settings_button.grid(row=0,column=1,sticky='n',padx=[5,0],pady=[2,2])
        avatar_label.grid(row=0,column=3,sticky='nw',columnspan=2,padx=[10,0],pady=[6,2])
        self.Avatar.grid(row=0,column=3,sticky='n',columnspan=2,padx=[35,0],pady=[2,2])
        self.Add_parameter.grid(row=2,column=2,sticky='n',padx=[4,4],pady=[0,0])
        self.Remove_parameter.grid(row=2,column=2,sticky='s',padx=[4,4],pady=[0,0])
        filterlabel.grid(row=0,column=2,sticky='n',pady=[6,0])
        self.filter_entry.grid(row=1,column=2,sticky='n',padx=[4,4])
        self.filter_enable.grid(row=1,column=2,pady=[8,4],padx=[0,70])
        self.filter_disable.grid(row=1,column=2,pady=[8,4],padx=[70,0])
        self.default_parameters_filter.grid(row=1,column=0,sticky='nse',columnspan=2,rowspan=3,pady=[0,10])
        self.learned_parameters_filter.grid(row=1,column=3,sticky='nsw',columnspan=2,rowspan=3,pady=[0,10])

class Eventi_layout(ttk.Labelframe):
    def __init__(self,parent,sticktype,template=None):
        super().__init__(parent)
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)

        self.widgets = {}

        self.Header_frame = ttk.Frame(self)
        self.body = ttk.Frame(self)
        self.Toggle = ttk.Checkbutton(self.Header_frame,text='Enabled',bootstyle='round-toggle',)
        self.sep1 = ttk.Separator(self.body,orient='horizontal')
        self.sep2 = ttk.Separator(self.body,orient='vertical')
        self.Response_list = ttk.Treeview(self.body,columns=['Address','Value','Delay'],selectmode='browse',height=8,style='L.Treeview')

        self.Trigger = ttk.Combobox(self.Header_frame,justify='center',style='Label.TCombobox',width=45,state='disabled')
        self.Condition_label = ttk.Label(self.body,text='Condition',style='alt2.TLabel')
        self.Response_label = ttk.Label(self.body,text='Response',style='alt2.TLabel')
        self.Response_address = ttk.Combobox(self.body,width=28)
        self.Address_label = ttk.Label(self.body,text='Address')
        self.Response_value = ttk.Entry(self.body,width=20,validate='key')
        self.Response_value_avatars = ttk.Combobox(self.body,width=20)
        self.Value_label = ttk.Label(self.body,text='Value :')
        self.Value_overwrite = ttk.Checkbutton(self.body,text='Use Input')
        self.Response_delay = ttk.Entry(self.body,width=4)
        self.Delay_label = ttk.Label(self.body,text='Delay (ms) :')
        self.Response_save = ttk.Button(self.body,text='Save')
        self.List_remove = ttk.Button(self.body,text='Remove',width=7,state='disabled')
        self.List_orderup = ttk.Button(self.body,text='▲',width=2,state='disabled',style='arrow.TButton',padding=[1,0,2,0])
        self.List_orderdown = ttk.Button(self.body,text='▼',width=2,state='disabled',style='arrow.TButton',padding=[1,0,2,0])
        self.List_ordertop = ttk.Button(self.body,text='△',width=2,state='disabled',style='arrow.TButton',padding=[3,2,4,2])
        self.List_orderbottom = ttk.Button(self.body,text='▽',width=2,state='disabled',style='arrow.TButton',padding=[3,2,4,2])

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
        self.Toggle.grid(row=0,column=2)
        self.sep1.grid(row=0,column=0,sticky='new',columnspan=3)
        self.sep2.grid(row=0,column=0,sticky='nse',rowspan=4,pady=[0,5])
        self.Response_list.grid(row=0,column=2,sticky='nsew',rowspan=4,pady=[1,0])
        self.Trigger.grid(row=0,column=0,columnspan=2,sticky='n')
        #self.Condition_label.grid(row=0,column=0,sticky='n',pady=[5,0])
        self.Response_label.grid(row=0,column=1,sticky='n',pady=[5,0])
        self.Response_address.grid(row=1,column=1,sticky='s',pady=[5,0])
        self.Address_label.grid(row=1,column=1,sticky='n',pady=[0,5])
        self.Response_value.grid(row=2,column=1,sticky='s',padx=[5,0],pady=[5,0])
        self.Value_label.grid(row=2,column=1,sticky='n',padx=[0,50],pady=[0,5])
        self.Value_overwrite.grid(row=2,column=1,sticky='n',padx=[80,0],pady=[3,0])
        self.Response_delay.grid(row=3,column=1,sticky='e',padx=[0,10],pady=[0,0])
        self.Delay_label.grid(row=3,column=1,sticky='e',padx=[0,55],pady=[0,0])
        self.Response_save.grid(row=3,column=0,columnspan=2,sticky='s',pady=[0,5])
        self.List_remove.grid(row=3,column=2,sticky='s',pady=[0,5],padx=[0,0])
        self.List_orderup.grid(row=3,column=2,sticky='s',pady=[0,9],padx=[0,145])
        self.List_orderdown.grid(row=3,column=2,sticky='s',pady=[0,9],padx=[145,0])
        self.List_ordertop.grid(row=3,column=2,sticky='s',pady=[0,7],padx=[0,95])
        self.List_orderbottom.grid(row=3,column=2,sticky='s',pady=[0,7],padx=[95,0])
