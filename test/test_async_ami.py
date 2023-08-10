import unittest
from aiopyami.ami import AsteriskManager

from aiopyami.client import Client
from aiopyami.formats import Action

# Connection credentials
ASTERISK_HOST = 'localhost'
ASTERISK_PORT = 8080
ASTERISK_USERNAME = 'admin'
ASTERISK_PASSWORD = 'password'

class TestClient(unittest.IsolatedAsyncioTestCase):
    async def test_connection(self):
        am = Client(ASTERISK_HOST, ASTERISK_PORT)
        
        manager = await am.connect(ASTERISK_USERNAME, ASTERISK_PASSWORD)
        self.assertIsInstance(manager, AsteriskManager)

        await am.disconnect()
    
    
    async def test_ping(self):
        try:
            am = Client(ASTERISK_HOST, ASTERISK_PORT)
            manager = await am.connect(ASTERISK_USERNAME, ASTERISK_PASSWORD)
            await am.subscribe_to_events(["on"])

            print("Let's start playing ping pong with the server...")
            # Send the action with the callback
            action = Action("Ping", {})
            response = await manager.send_action_and_wait(action)

            self.assertEqual(response["Ping"], "Pong", str(response))

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