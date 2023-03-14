from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
class MyConsumer(WebsocketConsumer):
    
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'client_{self.room_name}'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,self.channel_name
        )
        self.accept()
        
    def receive(self, text_data=None, bytes_data=None):
        print(type(text_data))
        message=json.loads(text_data)
        if(message['text_data']):
            self.send(text_data='Message Recieved')

    def disconnect(self, close_code):
        pass
        # Called when the socket closes
    def send_notification(self,event,type='send_notification'):
        
        print(event['task'])
        self.send(text_data=json.dumps({'task':event['task'],'new_links':event['message']}))
        