from .listener import FirstListener
from ... import Client
from settings import LOGIN_CREDENTIALS

# Alias for LOGIN_CREDENTIALS
creds = LOGIN_CREDENTIALS
am = Client(creds["HOSTNAME"], creds["PORT"])

async def on_start():
    
    # Let's connect to the server
    await am.connect(creds["USERNAME"], creds["PASSWORD"])
    
    # Before we register event listeners, we need to subscribe to the events
    await am.subscribe_to_events(["on"])

    # Now we can register our event listeners
    am.register_event_handler("FirstListener", FirstListener)


async def on_stop():
    if not am.is_connected():
        return
    
    await am.disconnect()