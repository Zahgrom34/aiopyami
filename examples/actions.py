"""
Basic example of sending actions to the server

In this example, we send an action to the server and thats it.
In this example, we will not wait for the server to respond, we will get only given ActionID or generated one
"""
import asyncio
from aiopyami.client import Client, Action
from settings import LOGIN_CREDENTIALS

# Alias for LOGIN_CREDENTIALS
creds = LOGIN_CREDENTIALS

async def main():
    am = Client(creds["HOSTNAME"], creds["PORT"])

    ami = await am.connect(creds["USERNAME"], creds["PASSWORD"])
    
    # In this example, we create a new Action and send it to the server
    action = Action("Ping", {})
    # Also there is optional parameter with ActionID. If not provided it will generate it and return it
    action_id = await ami.send_action(action)

    # In our case, Im not provided ActionID so it will be generated
    # So let's output new generated ActionID with a message
    print("Sent an action to the server with ActionID: {0}".format(action_id))

    # Now we've done what we need to do, we can disconnect from the server now
    await am.disconnect()


# We're going to launch it. Yay!
if __name__ == "__main__":
    asyncio.create_task(main())