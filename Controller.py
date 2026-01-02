import ttkbootstrap as ttk
import Events
from Layout import Tabi_layout, Message_display, s_ipvar, s_portvar, logvar_2
from Constants import READ_ONLY_PARAMETERS, CONTROLS_LIST,GAME_EVENTS
from Osc import OSC_client,OSC_Listner
import re
import ast
import operator

class Tabi(Tabi_layout):
    saved_avatars = {'Universal':[None,[]]}
    '''
    key = An Avatar Name\n
    value = [An Avatar Id, [Avatar Parameters] ]\n
    Generated in OSC_handler in Main... for now.
    '''
    avatar_name_hold = None
    current_avatar = None
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
        self.Stick_list: dict[str, tuple[str,list[object]]] = {}
        '''
        key: A parameter address
        \nvalue: A tuple containing the event type and a list of objects which share the parameter address
        '''

        def Add_stick():
            stick_type = self.stick_type.get()
            title = self.Title.get()
            match stick_type:
                case 'OSC':triggers = self.control_parameters
                case 'VRC':triggers = GAME_EVENTS
                case 'SYS':triggers = self.System_events
                case 'NET':triggers = self.Network_events

            Stick = Events.Eventi(self.Stick_space,Id=(self.stick_count,stick_type),controller=self,Title=title,triggers=triggers)
            self.register_stick_addresses(Stick,[title])

            row = len([c for c in self.Stick_space.winfo_children() if isinstance(c, Events.Eventi)])
            Stick.grid(row=row,column=0,sticky='nsew',padx=2,pady=4)
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
                    self.Title.configure(values=self.control_parameters,state='readonly')
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
                if parameter in CONTROLS_LIST + READ_ONLY_PARAMETERS:continue
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

    def resetclient(self):
        del self.Client
        self.Client = OSC_client(s_ipvar.get(),s_portvar.get())

    def _safe_eval_ast(self, node):
        """Evaluate a restricted AST node (Numbers, BinOp, UnaryOp)."""
        operators = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.Mod: operator.mod
        }
        if isinstance(node, ast.Expression):
            return self._safe_eval_ast(node.body)
        if isinstance(node, ast.Constant):  # Python 3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            Tabi_layout.Message_display(text='Expression evaluation error :', address ='{node.value}', message= f'\nNon-numeric constant in expression.')
            raise ValueError("Non-numeric constant in expression")
        if isinstance(node, ast.BinOp):
            left = self._safe_eval_ast(node.left)
            right = self._safe_eval_ast(node.right)
            op = type(node.op)
            if op in operators:
                return operators[op](left, right)
            Tabi_layout.Message_display(text='Expression evaluation error :', address ='{op}', message= f'\nOperator not allowed in expression.')
            raise ValueError("Operator not allowed")
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.UAdd):
                return +self._safe_eval_ast(node.operand)
            if isinstance(node.op, ast.USub):
                return -self._safe_eval_ast(node.operand)
            Tabi_layout.Message_display(text='Expression evaluation error :', address ='{node.op}', message= f'\nUnary operator not allowed in expression.')
            raise ValueError("Unary operator not allowed")
        Tabi_layout.Message_display(text='Expression evaluation error :', address ='{node}', message= f'\nUnsupported expression node.')
        raise ValueError("Unsupported expression node")

    def evaluate_expression(self, Stick, expr: str, values_map: dict):
        """
        Substitute placeholders of form {address} with the latest numeric value from values_map,
        then safely evaluate the resulting arithmetic expression.

        Returns numeric result or raises ValueError/KeyError when substitution/eval fails.
        """
        # replace each {address} with a numeric literal taken from values_map
        def repl(match):
            addr = match.group(1)
            if addr not in Stick.addresses:
                Tabi_layout.Message_display(text='Expression evaluation error :', address ='{addr}', message= f'\nAddress not registered in stick.')
                raise KeyError(f"address not registered in stick: {addr}")
            if addr not in values_map:
                # dependent value missing
                raise KeyError(f"missing value for address: {addr}")
            val = values_map[addr]
            if isinstance(val, bool):
                val = int(val)
            # try to coerce to number
            try:
                if isinstance(val, (int, float)):
                    return str(val)
                return str(float(val))
            except Exception as e:
                Tabi_layout.Message_display(text='Expression evaluation error :', address ='{addr}', message= f'\nNon-numeric value: {val}')
                raise ValueError(f"non-numeric value for {addr}: {val}") from e

        expr_sub = re.sub(r'\{([^}]+)\}', repl, expr)

        # parse and evaluate restricted AST
        node = ast.parse(expr_sub, mode='eval')
        return self._safe_eval_ast(node)

    def Lookup(self,Stick,OSCmessage=None,VRCevent=None):
        Ids = Stick.Response_list.get_children()
        Received_value = self.normalize(OSCmessage) if OSCmessage is not None else None
        #print(f'Received msg : {OSCmessage},\nProcessed msg : {Received_value}')
        
        if not VRCevent: VRCevent = {}
        for Id in Ids:
            data = Stick.stick_data[Id]
            if 'expression' in data and data['expression']:
                try:
                    values_map = OSC_Listner.active_server.values if OSC_Listner.active_server else {}
                    Received_value = self.evaluate_expression(Stick, data['expression'], values_map)
                except KeyError as ke:
                    # missing dependent value
                    Message_display(text='Expression skipped, missing value:', address ='{ke}', message= f'\n{data["expression"]}')
                    continue
                except Exception as e:
                    Message_display(text='Expression evaluation error :', address ='{e}', message= f'\n{data["expression"]}')
                    continue
                
            passed = (
                (data['conditionOP'] == '=' and Received_value == self.normalize(data['condition'])) or
                (data['conditionOP'] == '<' and Received_value < self.normalize(data['condition'])) or
                (data['conditionOP'] == '>' and Received_value > self.normalize(data['condition'])) or
                (data['condition'] == 'ANY')
                ) if Received_value is not None else (
                (data['user'] == VRCevent.get('User') and data['avatar'] == None) or
                (data['user'] == VRCevent.get('User') and data['avatar'] == VRCevent.get('Avatar'))or
                (data['user'] == VRCevent.get('User') and data['avatar'] == 'ANY') or
                (data['user'] == 'ANY' and data['avatar'] == None) or
                (data['user'] == 'ANY' and data['avatar'] == VRCevent.get('Avatar')) or
                (data['user'] == 'ANY' and data['avatar'] == 'ANY')
                )
            if passed:
                if Received_value is not None and data['value'] == 'INPUT':
                    self.after(data['delay'],lambda a=data['address'],r=Received_value:self.Client.send_message(a,r))
                    if logvar_2.get(): Message_display(data['address'],Received_value,text='Sent:')
                else:
                    self.after(data['delay'],lambda a=data['address'],r=self.stab(data['value']):self.Client.send_message(a,r))
                    if logvar_2.get(): Message_display(data['address'],self.stab(data['value']),text='Sent:')

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
        if isinstance(value, str):
            try:
                value = float(value) if '.' in value else int(value)
            except ValueError:
                return value
        if isinstance(value, tuple):
            value = value[0]  
        if isinstance(value, bool) or isinstance(value, int):
            return int(value)
        try:
            return float(value)
        except ValueError:
            print(f'error {value}')
            return value

    def register_stick_addresses(self, stick, addresses: list[str]):
        """Register a Stick object under each address. Map addresses on OSC listener."""
        for addr in addresses:
            if addr in self.Stick_list:
                if stick not in self.Stick_list[addr][1]:
                    self.Stick_list[addr][1].append(stick)
                    print(f'Added {addresses} to {self.Stick_list[addr]}')
                #print(f'{addresses} already registered to {self.Stick_list[addr]}')
            else:
                self.Stick_list[addr] = (stick.Id[1], [stick])
                #print(f'Registered {addresses} to {self.Stick_list[addr]}')
                if stick.Id[1] == 'OSC':
                    if OSC_Listner.active_server:
                        OSC_Listner.active_server.Map_address(addr)
        #print(f'{self.Stick_list}\n')
        
    def unregister_stick_addresses(self, stick, addresses: list[str]=None):
        '''Unregister a Stick object from each address. Unmap addresses on OSC listener.'''
        for addr in addresses:
            #print(f'address : {addr}')
            entry = self.Stick_list.get(addr)
            #print(f'entry : {entry}')
            if not entry: continue
            if stick not in entry[1]: continue
            self.Stick_list[addr][1].remove(stick)
            #print(f'Entry after removal : {entry}')
            #Checks if there are no more sticks registered to the address
            if not self.Stick_list[addr][1]:
                #print(f'detected empty list')
                del self.Stick_list[addr]
                if stick.Id[1] == 'OSC':
                    if OSC_Listner.active_server:
                        OSC_Listner.active_server.unMap_address(addr)
            #print(f'Unregistered {addr} from {self.Stick_list.get(addr)}')

    def reflow_sticks(self):
        children = [c for c in self.Stick_space.winfo_children() if isinstance(c, Events.Eventi)]
        for i, child in enumerate(children):
            child.grid_configure(row=i)
            child.Id = (i,child.Id[1])
        self.stick_count = len(children)

    def handler(self,address,OSCmessage=None,VRCevent=None):
        #Checks if an event exists with an address that matches the one provided
        if Sticks := self.Stick_list.get(address):
            #itterate over objects with matching addresses
            for Stick in Sticks[1]:
                #ignore event if it's been toggled off
                if not Stick.toggle_var.get(): return
                #send message to the lookup func to determine how to respond
                self.Lookup(Stick,OSCmessage=OSCmessage,VRCevent=VRCevent)

    def Load(self,Sticks):
        for Identifier,data in Sticks.items():
            if Identifier == 'Avatar':continue
            StickType = data['Type']
            Addresses = data['Addresses']
            Title = data['Title']
            match StickType:
                case 'OSC':
                    triggers = self.control_parameters
                case 'VRC':triggers = GAME_EVENTS
                case 'SYS':triggers = self.System_events
                case 'NET':triggers = self.Network_events

            Stick = Events.Eventi(self.Stick_space,Id=(Identifier,StickType),controller=self,Title=Title,triggers=triggers)
            self.register_stick_addresses(Stick,Addresses)
            Stick.grid(row=self.stick_count,column=0,sticky='nsew',padx=2,pady=4)
            self.stick_count += 1
            Stick.Load(Title,StickType,Addresses,data)