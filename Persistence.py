from pathlib import Path
import json
import appdirs 
from shutil import move
import Layout
directory_dir = Path(appdirs.user_data_dir('osc app', 'falnen'))
directory_dir.mkdir(parents=True, exist_ok=True)
directory_file = directory_dir.joinpath("Directory.json")
saved_controllers = set()

# get current working directory
def Directory():
    if not directory_file.exists():
        with open(directory_file,'w') as file:
            json.dump({'Settings directory': str(directory_dir)}, file, indent=4)

    with open(directory_file,'r') as file:
        config = json.load(file)
    return config.get('Settings directory')

# update working directory and move State file if it exists
def Update_dir(new_path):
    new_path = Path(new_path)
    new_path.mkdir(exist_ok=True)
    old_dir = Path(Directory())  
    old_state_file = old_dir.joinpath("App State.json")
    new_state_file = new_path.joinpath("App State.json")
    
    if old_state_file.exists():
        move(old_state_file,new_state_file)
    
    with open(directory_file,'w') as file:
            json.dump({"Settings directory":str(new_path)},file,indent=4)

# save all controllers to App State file
def save_state(frames_dict):
    dir = Path(Directory())
    app_state_file = dir.joinpath("App State.json")
    if app_state_file.exists():
        with open(app_state_file,'r') as file:
            State = json.load(file)
    else:
        State = {"App version":0.1}

    State['Server'] = {
        'Ip':Layout.Ip_entry.get(),
        'Port':Layout.Port_entry.get(),
        'Path':Layout.location_var.get()
        }
    
    State['Avatar data'] = list(frames_dict.values())[0].saved_avatars
    
    for id in Layout.Object_list.get_children():
        controller = frames_dict[id]
        name = controller.name
        State[name] = {'Avatar':controller.Avatar.get()}
        saved_controllers.add(controller.name)
        for StickId, Stick in controller.Stick_list.items():
            State[name][StickId] = {'Type':Stick.Id[1],'Trigger':Stick.Trigger.get()}
            responseIds = Stick.Response_list.get_children()
            for response in responseIds:
                data = Stick.stick_data[response]
                State[name][StickId][response] = data

    for key in list(State.keys()):
        if key not in saved_controllers and key not in {'App version', 'Server', 'Avatar data'}:
            del State[key]

    with open(app_state_file,'w') as file:
        json.dump(State,file,indent=4)

def Load_data():
    dir = Path(Directory())
    app_state_file = dir.joinpath("App State.json")
    if app_state_file.exists():
        with open(app_state_file,'r') as file:
            data = json.load(file)
        return data
    else: return None
    