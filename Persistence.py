from pathlib import Path
import json
import appdirs 
from shutil import move
import Layout
from datetime import datetime

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

    State['Settings'] = {
        'r_Ip':Layout.r_ipvar.get(),
        'r_Port':Layout.r_portvar.get(),
        's_Ip':Layout.s_ipvar.get(),
        's_Port':Layout.s_portvar.get(),
        'Log_received':Layout.logvar_1.get(),
        'Log_sent':Layout.logvar_2.get(),
        'Path':Layout.location_var.get(),
        'Primary-color':Layout.style.colors.get('primary'),
        'Secondary-color':Layout.style.colors.get('secondary')
        }
        
    State['Avatar data'] = list(frames_dict.values())[0][1].saved_avatars
    State['Controllers'] = {}
    
    for avatar, controller in frames_dict.items():
        name = controller[1].name
        State['Controllers'][name] = {'Avatar':avatar}
        saved_controllers.add(name)
        for Title, sList in controller[1].Stick_list.items():
            for Stick in sList[1]:
                State['Controllers'][name][Stick.Id[0]] = {'Type':sList[0]}
                State['Controllers'][name][Stick.Id[0]]['Addresses'] = [a for a in Stick.addresses]
                State['Controllers'][name][Stick.Id[0]]['Title'] = Title
                responseIds = Stick.Response_list.get_children()
                for response in responseIds:
                    data = Stick.stick_data[response]
                    State['Controllers'][name][Stick.Id[0]][response] = data

    for key in State['Controllers'].keys():
        if key not in saved_controllers:
            del State['Controllers'][key]

    with open(app_state_file,'w') as file:
        json.dump(State,file,indent=4)

def Load_data() -> dict:
    dir = Path(Directory())
    app_state_file = dir.joinpath("App State.json")
    if app_state_file.exists():
        with open(app_state_file,'r') as file:
            data = json.load(file)
        return data
    else: return None
    