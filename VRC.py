from os import path
import re
#from datetime import datetime
from pathlib import Path
import json
from Constants import READ_ONLY_PARAMETERS

log_dir = Path.home() / "AppData" / "LocalLow" / "VRChat" / "VRChat"
Avtr_dir = Path.home() / "appData" / "LocalLow" / "VRChat" / "VRChat" / "OSC"
user_folders = Avtr_dir.glob('usr_*')
avatar_folders = [avatar.joinpath('Avatars') for avatar in user_folders]
logfile_pattern = "output_log_*"

def find_latest_log() -> Path:
    log_files = list(log_dir.glob(logfile_pattern))
    return max(log_files, key=lambda f: f.stat().st_birthtime) if log_files else None

def Build_avatar_list() -> dict:
    try:User_avtr_dir = Avtr_dir.joinpath(Log_parser.User_id)
    except:User_avtr_dir = max(avatar_folders,key=lambda f:f.stat().st_mtime)
    OSC_avatars = {}
    try:
        for json_file in User_avtr_dir.rglob("*.json"):
            with open(json_file, 'r', encoding = 'utf-8-sig') as file:
                data = json.load(file)
                name = data['name']
                new_parameters = []
                for parameter in data['parameters']:
                    address = parameter['output']['address']
                    if address in READ_ONLY_PARAMETERS:continue
                    new_parameters.append(address)
                OSC_avatars[name] = data['id']
                OSC_avatars[data['id']] = [name,new_parameters]
        return OSC_avatars
    except:
        print('error reading avatar Json files.')

class Log_parser:
    user_id = None
    def __init__(self,handler):
        self.last_line = 0
        self.log_file = find_latest_log()
        self.handler = handler
        self.skip = 'Normal'
        self.Local_user = None
        self.search_limit = 0
        self.worldname = re.compile(r'worldName=(.*)}')
        self.event_patterns = {
            'friendRequest':'Friend request',
            'group':'Group',
            'invite':'Invite',
            'requestInvite':'Invite request',
        }
        self.repatterns = {
            'User joined' : re.compile(r'\[Behaviour\] Initialized player(?P<User>.*)'),
            'User left' : re.compile(r'\[Behaviour\] OnPlayerLeft (?P<User>.*) \('),
            'Avatar changed' : re.compile(r'\[Behaviour\] Switching (?P<User>.*?) to avatar (?P<Avatar>.*)'),
            'Author' : re.compile(r'Unpacking Avatar \((?P<Avatar>.*?) by (?P<User>.*?)\)'),
            'Errorbreak' : re.compile(r'Received Notification:'),
            'Notification' : re.compile(r'Received Notification:.*?:(?P<User>[^,]*).*type:\s(?P<Type>[^,]*).*created at:\s(?P<Timestamp>[^,]*).*details:\s\{(?P<Details>{.*})\}.*message:\s"(?P<Message>[^"]*)'),
            'Loading' : re.compile(r'\[Behaviour\] launching in normal manner'),
            'Finishedloading' : re.compile(r'\[Behaviour\] Initialized PlayerAPI .*? is local'),
            'SocketError' : re.compile(r'Websocket exploded!'),
            #'Filedate': re.compile(f'{now.year}-{now.month if now.month >= 10 else f'0{now.month}'}-{now.day if now.day >= 10 else f'0{now.day}'}'),
            #'Logtime' : re.compile(f'{now.year}.{now.month if now.month >= 10 else f'0{now.month}'}.{now.day if now.day >= 10 else f'0{now.day}'}')
        }

    def Find_user(self):
        find = re.compile(r'User Authenticated: (?P<User>.*) \((?P<ID>.*)\)')
        with open(self.log_file,'r',encoding='utf-8') as file:
            while not self.Local_user:
                file.seek(self.last_line,0)
                line = file.readline()
                self.last_line = file.tell()
                if found := find.search(line):
                    self.Local_user = found.group('User')
                    self.User_id = found.group('ID')
                    print(self.User_id)
                    self.Read_log()

    def Read_log(self):
        #if not self.repatterns['Filedate'].search(str(self.log_file)):
        #    return 1
        with open(self.log_file, 'r',encoding='utf-8') as file:
            while True:
                file.seek(self.last_line,0)
                line = file.readline()
                self.last_line = file.tell()

                if not line: break
                if not line.strip(): continue

                for condition, pattern in self.repatterns.items():
                    result = pattern.search(line)
                    if not result:
                        continue
                    if condition == 'SocketError':
                        self.skip = 'sockerr'
                        break
                    elif self.skip == 'sockerr':
                        if condition == 'Errorbreak': break
                        else:
                            self.search_limit += 1
                            if self.search_limit > 3:
                                self.search_limit = 0
                                self.skip = 'Normal'
                    elif condition == 'Errorbreak': continue
                    elif condition == 'Loading':
                        self.skip = 'Loading'
                        break
                    elif condition =='Finishedloading':
                        self.skip = 'Normal'
                        break
                    elif self.skip == 'Loading':
                        if not condition == 'Avatar changed': continue
                        args = result.groupdict()
                        if not args.get('User') == self.Local_user: break
                        args['Type'] = 'Local avatar'
                        self.handler(args)
                        break

                    args = result.groupdict()
                    args.setdefault('Type',condition)
                    if args.get('Type') in self.event_patterns.keys(): args['Type'] = self.event_patterns[args['Type']]
                    if condition == 'Notification' and args.get('Type') == 'Invite': args['World'] = self.worldname.search(args['Details']).group(1)
                    elif condition == 'Avatar changed' and args.get('User') == self.Local_user:
                        args['Type'] = 'Local avatar'
                    self.handler(args)
