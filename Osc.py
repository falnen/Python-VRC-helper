from Layout import Log_display
from pythonosc import dispatcher, osc_server, udp_client
import threading
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
        self.dispatcher.set_default_handler(self.Msg_handler)

    def Msg_handler(self,address,*args):
        value = round(args[0],3) if isinstance(args[0],float) else args[0]
        if isinstance(value,bool): value = int(value)
        if self.last_message == (address,value): return
        self.last_message = (address,value)
        self.message_queue.put((address,value))
    
    def Start_server(self,ip,port):
        if self.server: return
        self.server = osc_server.BlockingOSCUDPServer((ip, port), self.dispatcher)
        self.server_thread = threading.Thread(group=None,target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        Log_display.insert('end',f'Listning on - {ip}:{port}\n')
        Log_display.yview('end')
    
    def stop_server(self):
        if not self.server: return
        Log_display.insert('end','Stopping Server...\n')
        Log_display.yview('end')
        self.server.shutdown()
        self.server.server_close()
        if self.server_thread.is_alive(): self.server_thread.join()
        self.server = None
        self.server_thread = None