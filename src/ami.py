import asyncio
import uuid

from typing import Callable, Optional
from src.exceptions import NoConnectionMade
from src.formats import Action
from src.utils import dump_data

class AsteriskManager:
    def __init__(self, _client: object) -> None:
        self.__client = _client
        self._action_callbacks = {}
    
    async def send_action_callback(self, action: Action, callback: Callable[[dict], None], /, callback_timeout: float = 30000, action_id: Optional[str] = None) -> None:
        """
        Same as send_action but it was made for huge requests that require time to respond

        Args:
            action (Action): Action model to send and parameters should be in dict format
            callback (Callable[[str], None]): Function which will be called when response will be received.
            action_id (Optional[str]): ActionID for this transaction. Defaults to None.
        """
        response_id = await self.send_action(action, action_id)

        self._action_callbacks[response_id] = callback
        self._action_callbacks[response_id + "_timeout_task"] = asyncio.create_task(self._remove_callback_after_timeout(response_id, callback_timeout))


    async def send_action(self, action: Action, action_id: Optional[str] = None) -> str:
        """
        Sends action to the asterisk and waits for the response.

        Args:
            action (Action): Action model to send and parameters should be in dict format
            action_id (Optional[str]): ActionID for this transaction. Defaults to None.

        Raises:
            NoConnectionMade: If client was not connected or connection lost.
            SerializationError: If response format is invalid and there is error in serializing response format into dictionary format.

        Returns:
            dict: Serialized response format. From string into dictionary.
        """
        if self.__client.transport is None or self.__client.transport.is_closing():
            raise NoConnectionMade("Can't send an action to a client without connection")
        
        action.params["ActionID"] = str(uuid.uuid4())

        if action_id is not None:
            action.params["ActionID"] = action_id
        
        self.__client.transport.write(action.ami_format().encode())
        
        return action.params["ActionID"]
    

    async def _remove_callback_after_timeout(self, action_id: str, timeout: float = 30000):
        await asyncio.sleep(timeout)
        # Check if the callback is still present in the _action_callbacks list
        if action_id in self._action_callbacks:
            del self._action_callbacks[action_id]

        if action_id + '_timeout_task' in self._action_callbacks:
            del self._action_callbacks[action_id + '_timeout_task']


    async def _dispatch_action(self, response: str):
        try:
            event_data = dump_data(response)
            action_id = event_data.get("ActionID")
            callback = self._action_callbacks.get(action_id)
            if callback:
                del self._action_callbacks[action_id]  # Remove the callback once executed
                if action_id + '_timeout_task' in self._action_callbacks:
                    self._action_callbacks[action_id + '_timeout_task'].cancel()
                    del self._action_callbacks[action_id + '_timeout_task']
                
                await callback(event_data)
        
        except Exception as e:
            print(e)
