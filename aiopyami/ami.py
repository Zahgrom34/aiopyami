import asyncio
import uuid
from typing import Callable, Optional

from aiopyami.exceptions import NoConnectionMade
from aiopyami.formats import Action, AsteriskResponse
from aiopyami.utils import dump_data


class AsteriskManager:
    def __init__(self, _client: object) -> None:
        self.__client = _client
        self._action_callbacks = {}
        self._action_queue = []
        self._actions_queue_event = asyncio.Event()
        self._action_callbacks_event = asyncio.Event()

    async def send_action_and_wait(self, action: Action, /,
                                   timeout: float = 30000,
                                   action_id: Optional[str] = None,
                                   raise_on_timeout: bool = True) -> AsteriskResponse:
        """
        Same as send_action_callback, but with differences. 
        Instead of calling transaction response callback function, it will stop the event loop until it won't receive any response data
        If it will receive data, it will return it immediately

        Args:
            action (Action): Action model to send and parameters should be in dict format
            timeout (float): Estimated timeout in milliseconds to wait AMI to respond
            action_id (Optional[str]): ActionID for this transaction. Defaults to None.
            raise_on_timeout (bool): Whether to raise an exception if the action response time takes longer than estimated timeout.
        
        NOTE: This method is coroutine. Please use it with await prefix and inside asynchronous method
        """
        response_id = await self.send_action(action, action_id)

        # Add the transaction ActioID to the queue
        self._action_queue.append(response_id)

        # Wait for the the response, if response will took longer than estimated timeout. Raise an exception
        try:
            response = await asyncio.wait_for(self.__client.queue.get(), timeout)

        except asyncio.TimeoutError:
            if raise_on_timeout:
                raise asyncio.TimeoutError("Timed out waiting for response")

        return response

    async def send_action_callback(self, action: Action, callback: Callable[[AsteriskResponse], None], /, callback_timeout: float = 30000, action_id: Optional[str] = None) -> None:
        """
        Same as send_action but it was made for huge requests that require time to respond

        Args:
            action (Action): Action model to send and parameters should be in dict format
            callback (Callable[[str], None]): Function which will be called when response will be received.
            action_id (Optional[str]): ActionID for this transaction. Defaults to None.
        
        NOTE: This method is coroutine. Please use it with await prefix and inside asynchronous method
        """
        response_id = await self.send_action(action, action_id)

        self._action_callbacks[response_id] = callback
        self._action_callbacks[response_id + "_timeout_task"] = asyncio.create_task(
            self._remove_callback_after_timeout(response_id, callback_timeout))

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
        
        NOTE: This method is coroutine. Please use it with await prefix and inside asynchronous method
        """
        if self.__client.transport is None or self.__client.transport.is_closing():
            raise NoConnectionMade(
                "Can't send an action to a client without connection")

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

    def _dispatch_action(self, response: str):
        """Dispatches all data related to actions that has been received from the server"""
        event_data = dump_data(response)
        action_id = event_data.get("ActionID")

        # Checks for send_action_callback actions
        callback = self._action_callbacks.get(action_id)
        if callback:
            print("Callback executed: ", callback)
            # Remove the callback once executed
            del self._action_callbacks[action_id]
            if action_id + '_timeout_task' in self._action_callbacks:
                self._action_callbacks[action_id + '_timeout_task'].cancel()
                del self._action_callbacks[action_id + '_timeout_task']

            if not len(self._action_callbacks.items()):
                self._action_callbacks_event.set()

            event_data = AsteriskResponse.from_response(response)
            asyncio.run_coroutine_threadsafe(callback(event_data), self.__client.loop)

        # Checks for send_action_and_wait actions
        if action_id in self._action_queue:
            event_data = AsteriskResponse.from_response(response)
            self._action_queue.remove(action_id)
            self.__client.queue.put_nowait(event_data)

            if not len(self._action_queue):
                self._actions_queue_event.set()
    

    async def wait_for_actions_complete(self) -> None:
        """
        Waits for all actions to be completed
        If  this function will be called inside coroutine, it will freeze that coroutine, until all actions won't be completed
        """
        await self._actions_queue_event.wait()
        await self._action_callbacks_event.wait()