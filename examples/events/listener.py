from aiopyami import EventHandler, AsteriskManager, AsteriskResponse, EventTrigger, Action

# Let's create our event listener class first
class FirstListener(EventHandler):

    @EventTrigger(event="OriginateResponse")
    async def listen_originate_response(self, acx: AsteriskManager, response: AsteriskResponse):
        print("Originate response received from server ")
        print(str(response))

        # Now let's build the action object and send it to the server
        action = Action("Originate", {
            "Channel": "SIP/Test",
            "Context": "default",
            "Exten": "873123421",
            "Priority": "1",
            "CallerID": "3125551212",
            "Timeout": "30000"
        })
        await acx.send_action(action)

        # You can also disconnect/logoff and end the connection session
        await self.client.disconnect()