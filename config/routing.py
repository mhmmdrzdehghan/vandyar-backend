from chat.routing import websocket_urlpatterns as chat_websoket
from notification.routing import websocket_urlpatterns as notification_websocket
websocket_urlpatterns = chat_websoket + notification_websocket 