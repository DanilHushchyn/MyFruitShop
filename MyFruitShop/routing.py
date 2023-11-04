from django.urls import re_path, path

from admin_panel import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/balance/$', consumers.BalanceConsumer.as_asgi()),
    re_path(r'ws/audit/$', consumers.AuditConsumer.as_asgi()),
    re_path(r'ws/store/$', consumers.StoreConsumer.as_asgi()),
]
