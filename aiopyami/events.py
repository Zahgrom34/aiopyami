from __future__ import annotations
import asyncio

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Text

from aiopyami.formats import AsteriskResponse
from aiopyami.utils import dump_data

# Type annotations
if TYPE_CHECKING:
    from aiopyami.ami import AsteriskManager
    from aiopyami.client import Client


class EventManager:
    def __init__(self, client: Client, manager: AsteriskManager) -> None:
        """EventManager constructor"""
        self.client = client
        self.manager = manager
        self._events_handlers: Dict[str, EventHandler] = {}
    
    def register_event_handler(self, name: str, event_handler: EventHandler) -> None:
        self._events_handlers[name] = event_handler(self.client)

    def unregister_event_handler(self, name: str) -> None:
        del self._events_handlers[name]

    def _dispatch_events(self, event: str) -> None:
        # Dispatch events
        event_data = dump_data(event)
        
        for ekey in self._events_handlers.keys():
            self.call_event_trigger(ekey, event_data.get("Event"), 
                                    AsteriskResponse.from_response(event_data))

    def call_event_trigger(self, handler_name: str, event_name: str, _data: AsteriskResponse) -> bool:
        # Find handler with the given name
        _handler = self._events_handlers.get(handler_name)
        _event = _handler._events.get(event_name, None)

        # Get event with name `event_name`
        if not _event:
            return False
        
        asyncio.run_coroutine_threadsafe(_event(self.manager, _data), self.client.loop)
        return True

class EventHandler:
    def __init__(self, client: Client) -> None:
        """
        Base class for custom event handler implementations
        """
        self.client = client
        self._events: Dict[str, Callable[[AsteriskManager, AsteriskResponse], None]] = {}

    
def event_trigger(self, event: str):
        """
        Registers wrapped function as event
        If AMIClient receives an event with the same name, then this function will be called.

        Args:
            event (str): Name of event which will be listened for
        """
        def decorator(func: function):
            def wrapped_func(*args, **kwargs):
                return func(*args, **kwargs)
            
            wrapped_func.event_name = event
            self._events[event] = wrapped_func
            return wrapped_func
        
        return decorator

class EventTrigger:

    def __init__(self, events: Text | List[Text]) -> None:
        self.events = events

    def __call__(self, func) -> Any:
        async def wrapper(instance: EventHandler, *args, **kwargs):
            if type(self.events) is str:
                instance._events[self.event] = func
            
            else:
                for event in self.events:
                    instance._events[event] = func
            return await func(*args, **kwargs)
        
        
        return wrapper