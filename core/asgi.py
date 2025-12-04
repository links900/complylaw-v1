# core/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from scanner.consumers import ScanProgressConsumer  # ← Import your consumer
from django.urls import re_path
#import scanner.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            re_path(r'ws/scan/(?P<scan_id>\d+)/$', ScanProgressConsumer.as_asgi()),
            
            # This works for both int PK and UUID strings
            re_path(r'ws/scan/(?P<scan_id>[\w-]+)/$', ScanProgressConsumer.as_asgi()),
        ])
    ),
})