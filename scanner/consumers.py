# scanner/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ScanProgressConsumer(WebsocketConsumer):
    def connect(self):
        self.scan_id = self.scope["url_route"]["kwargs"]["scan_id"]
        self.room_group_name = f"scan_{self.scan_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    '''
    def scan_update(self, event):
        self.send(text_data=json.dumps(event))
    '''
        
    def scan_update(self, event):
        self.send(text_data=json.dumps({
            "progress": event.get("progress"),
            "step": event.get("step"),
            "grade": event.get("grade"),
            "risk_score": event.get("risk_score"),
            "status": event.get("status")
        }))

    
        
        
    def scan_complete_trigger(self, event):
        self.send(text_data=json.dumps({
            "type": "complete",
            "force_reload": True,
            "progress": 100,
            "grade": event.get("grade"),
            "risk_score": event.get("risk_score")
        }))