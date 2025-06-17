import re
#from datetime import datetime
from pathlib import Path

log_dir = Path.home() / "AppData" / "LocalLow" / "VRChat" / "VRChat"
logfile_pattern = "output_log_*"

def find_latest_log():
    log_files = list(log_dir.glob(logfile_pattern))
    return max(log_files, key=lambda f: f.stat().st_birthtime) if log_files else None

class Log_parser:
    def __init__(self,handler):
        self.last_line = 0
        self.log_file = find_latest_log()
        self.handler = handler
        self.skip = 'Normal'
        self.Local_user = None
        self.avatar = None
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
        find = re.compile(r'User Authenticated: (?P<User>.*) ')
        with open(self.log_file,'r',encoding='utf-8') as file:
            while not self.Local_user:
                file.seek(self.last_line,0)
                line = file.readline()
                self.last_line = file.tell()
                if found := find.search(line):
                    self.Local_user = found.group(1)
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
                if not line.strip():continue

                for condition, pattern in self.repatterns.items():
                    result = pattern.search(line)
                    if not result:
                        continue
                    if condition == 'SocketError':
                        self.skip = 'sockerr'
                        continue
                    elif self.skip == 'sockerr':
                        if condition == 'Errorbreak': continue
                        else:
                            self.search_limit += 1
                            if self.search_limit > 2:
                                self.search_limit = 0
                                self.skip = 'Normal'
                    elif condition == 'Errorbreak': continue
                    elif condition == 'Loading':
                        self.skip = 'Loading'
                        continue
                    elif condition =='Finishedloading':
                        self.skip = 'Normal'
                        continue
                    elif self.skip == 'Loading':
                        if not condition == 'Avatar changed':
                            continue
                        args = result.groupdict()
                        if not args.get('User') == self.Local_user:
                            continue
                        args['Type'] = 'Local avatar'
                        self.avatar = args.get('Avatar')
                        continue

                    args = result.groupdict()
                    args.setdefault('Type',condition)
                    if args.get('Type') in self.event_patterns.keys(): args['Type'] = self.event_patterns[args['Type']]
                    if condition == 'Notification' and args.get('Type') == 'Invite': args['World'] = self.worldname.search(args['Details']).group(1)
                    elif condition == 'Avatar changed' and args.get('User') == self.Local_user:
                        args['Type'] = 'Local avatar'
                        self.avatar = args.get('Avatar')
                    self.handler(args)
