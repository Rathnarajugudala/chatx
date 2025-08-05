import os
import django  # Add this if not already
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# ✅ Configure settings BEFORE importing anything Django-related
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatPrj.settings')
django.setup()  # ✅ Required to load models outside of manage.py context

from ChatApp import routing  # Import AFTER django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        routing.websocket_urlpatterns
    ),
})
