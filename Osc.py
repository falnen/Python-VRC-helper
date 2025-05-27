import threading
from pythonosc import dispatcher, osc_server, udp_client
from Layout import Log_display
import queue

class OSC_client:
    def __init__(self,ip,outport):
        self.ip = ip
        self.outport = outport
        self.client = udp_client.SimpleUDPClient(ip,outport)
    
    def send_message(self,address,response):
        self.client.send_message(address,response)

class OSC_Listner:
    def __init__(self):
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        self.last_message = (None,None)
        self.message_queue = queue.Queue()

    def Msg_handler(self,address,*args):
        value = round(args[0],3) if isinstance(args[0],float) else args[0]
        if self.last_message == (address,value):
            return
        self.last_message = (address,value)
        self.message_queue.put((address,value))
    
    def Start_server(self,ip,port):
        if self.server:
            return
        self.server = osc_server.ThreadingOSCUDPServer(('127.0.0.1', 9001), self.dispatcher)
        self.server_thread = threading.Thread(group=None,target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        self.server.dispatcher.set_default_handler(self.Msg_handler)
        Log_display.insert('end',f'Listning on - {ip}:{port}\n')
    
    def stop_server(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print('closed')
            self.server = None
            self.server_thread = None