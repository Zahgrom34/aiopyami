import asyncio
import time
import unittest
from src.ami import AsteriskManager

from src.client import Client
from src.formats import Action
from src.exceptions import AuthenticationError

# Connection credentials
ASTERISK_HOST = '172.16.35.254'
ASTERISK_PORT = 5038
ASTERISK_USERNAME = 'autocall'
ASTERISK_PASSWORD = '86ae14978e03c7b7417ca9a17a0b52b5'

class TestClient(unittest.IsolatedAsyncioTestCase):
    # async def test_connection(self):
    #     am = Client(ASTERISK_HOST, ASTERISK_PORT)
        
    #     print("Connecting to the server...")
    #     manager = await am.connect(ASTERISK_USERNAME, ASTERISK_PASSWORD)
    #     self.assertIsInstance(manager, AsteriskManager)

    #     await am.disconnect()
    
    
    async def test_ping(self):
        try:
            am = Client(ASTERISK_HOST, ASTERISK_PORT)
            manager = await am.connect(ASTERISK_USERNAME, ASTERISK_PASSWORD)
            await am.subscribe_to_events(["on"])
            # Create an asyncio.Event to signal when data is received
            data_received_event = asyncio.Event()

            # Define a callback function to handle the received data
            def handle_data(response):
                # Process the received data as needed
                print("Received data:", response)
                # Set the event to indicate data is received
                data_received_event.set()

            print("Ping pong sent to server")
            # Send the action with the callback
            action = Action("Ping", {})
            await manager.send_action_callback(action, handle_data)

            # Wait until the data is received
            await data_received_event.wait()

        except KeyboardInterrupt:
            await am.disconnect()



    # async def test_send_action(self):
    #     try:
    #         am = Client(ASTERISK_HOST, ASTERISK_PORT)
    #         not_responded = True
            
    #         print("Connecting to the server...")
    #         manager = await am.connect(ASTERISK_USERNAME, ASTERISK_PASSWORD)
    #         self.assertIsInstance(manager, AsteriskManager)
    #         print("Connected to the server successfully")

    #         await am.subscribe_to_events(["on"])
    #         # Action callback which will be called and executed
    #         async def action_cb(response_dict: dict):
    #             not_responded = False
    #             self.assertEqual(response_dict.get("Response", None), "Success")

    #         # Prepare the action
            # action = Action("Originate", {
            #     "Channel": "SIP/101test",
            #     "Context": "default",
            #     "Exten": "998993031234",
            #     "Priority": "1",
            #     "CallerID": "3125551212",
            #     "Timeout": "30000"
            # })
    #         await manager.send_action_callback(action, action_cb, action_id="ABC45678901234567890")
            
    #         while not_responded:
    #             time.sleep(2)
            
    #         await am.disconnect()

    #     except KeyboardInterrupt:
    #         await am.disconnect()

if __name__ == "__main__":

    unittest.main()