import asyncio
import sys

from mangum import Mangum
from app.main import app

# Ensured Python >= 3.14 has an event loop before

if sys.version_info >= (3, 14):
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

# Call Magnum(app), When  Mangum tries to initialize the FastAPI lifespan cycle

handler = Mangum(app)