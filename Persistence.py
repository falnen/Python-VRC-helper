import os
import json
import appdirs 
from shutil import move
import Layout

directory_dir = appdirs.user_data_dir('osc app','falnen')
os.makedirs(directory_dir,exist_ok=True)
directory_file = os.path.join(directory_dir,"Directory.json")
saved_controllers = {}

# get current working directory
def Directory():
    os.makedirs(directory_dir, exist_ok=True)
    if not os.path.exists(directory_file):
        with open(directory_file,'w') as file:
            json.dump({'Settings directory':directory_dir},file, indent=4)

    with open(directory_file,'r') as file:
        config = json.load(file)
    return config.get('Settings directory')

# update working directory and move State file if it exists
def Update_dir(new_path):
    old_dir = Directory()  
    old_state_file = os.path.join(old_dir, "App State.json")
    new_state_file = os.path.join(new_path, "App State.json")

    os.makedirs(new_path, exist_ok=True)
    if os.path.exists(old_state_file):
        move(old_state_file,new_state_file)
    
    with open(directory_file,'w') as file:
            json.dump({"Settings directory":new_path},file,indent=4)

# save all controllers to App State file
def save_state(frames_dict):
    path = Directory()
    app_state_file = os.path.join(path,"App State.json")
    os.makedirs(path, exist_ok=True)
    if os.path.exists(app_state_file):
        with open(app_state_file,'r') as file:
            State = json.load(file)
    else:
        State = {"App version":0.1}

    State['Server'] = {
        'Ip':Layout.Ip_entry.get(),
        'Port':Layout.Port_entry.get(),
        'Path':Layout.location_var.get()
        }
    
    for id in Layout.Object_list.get_children():
        controller = frames_dict[id]
        name = controller.name
        State[name] = {}
        saved_controllers[controller.name] = 1
        for StickId, Stick in controller.Stick_list.items():
            print(Stick,StickId)
            State[name][StickId] = {'Type':Stick.Id[1],'Trigger':Stick.Trigger.get()}
            responseIds = Stick.Response_list.get_children()
            for response in responseIds:
                data = Stick.stick_data[response]
                State[name][StickId][response] = data
    
    check = State.copy()
    for i in check:
        if i not in saved_controllers:
            if i in {'App version','Server'}:
                continue
            State.pop(i)

    with open(app_state_file,'w') as file:
        json.dump(State,file,indent=4)

def Load_data():
    path = Directory()
    app_state_file = os.path.join(path,"App State.json")
    if os.path.exists(app_state_file):
        with open(app_state_file,'r') as file:
            data = json.load(file)
        return data
    else: return None
    