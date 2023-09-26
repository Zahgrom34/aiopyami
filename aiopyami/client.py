import asyncio
import socket
from asyncio import Transport
from typing import List, Text, Type, TypeVar

from aiopyami.ami import AsteriskManager
from aiopyami.events import EventHandler, EventManager
from aiopyami.formats import Action
from aiopyami.internal import InternalHandler

T = TypeVar("T", bound="EventHandler")


class Client(asyncio.Protocol):
    def __init__(self, host: str, port: int) -> None:
        """
        Initializes a new client instance, used to connect and create AMI connection.

        Args:
            host (str): AMI host address
            port (int): AMI port
        """
        self.host = host
        self.port = port
        self.ami_socket = None
        self.queue = asyncio.Queue()
        self.transport = None
        self.loop = None
        self.__manager = AsteriskManager(self)
        self.__events = EventManager(self, self.__manager)
    

    async def connect(self, login: Text, password: Text) -> AsteriskManager:
        """
        Creates a new connection and AMI manager instance

        Args:
            login (str): AMI login credentials
            password (str): AMI password credentials
        
        NOTE: This method is coroutine. Please use it with await prefix and inside asynchronous method
        """
        try:
            loop = asyncio.get_running_loop()
            
            # Assign current loop to class instance parameter
            self.loop = loop

            # Connect to ami client
            self.ami_socket = await loop.create_connection(lambda: self, self.host, self.port)
            
            # Create connection action
            login_cmd = Action("Login", {
                "Username": login,
                "Secret": password
            })

            InternalHandler.login = login
            InternalHandler.password = password
            response = await self.__manager.send_action_and_wait(login_cmd)

            await InternalHandler.asterisk_authenticated(response)

            return self.__manager

        except socket.gaierror as ge:
            raise ConnectionError(f"Failed to resolve hostname: {ge}")
        except socket.timeout as te:
            raise ConnectionError(f"Connection to Asterisk AMI timed out: {te}")
        except socket.error as se:
            raise ConnectionError(f"Failed to connect to Asterisk AMI: {se}")


    async def subscribe_to_events(self, event_types: List[Text]) -> None:
        """
        Subscribes to events which will

        NOTE: This method is coroutine. Please use it with await prefix and inside asynchronous method
        """
        action = Action("Events", {
            "EventMask": ",".join(event_types),
        })

        await self.__manager.send_action(action, "EVENTS01")

    
    def connection_made(self, transport: Transport) -> None:
        print("Connection made successfully")
        self.transport = transport

    
    def data_received(self, data: bytes) -> None:
        received_bulk = data.decode()
        entries = received_bulk.split("\r\n\r\n")
        
        for response in entries:
            if "ActionID" in response:
                self.__manager._dispatch_action(response)


    def connection_lost(self, exc: Exception | None) -> None:
        print("Disconnected from Asterisk AMI")

        if exc is not None:
            raise exc
    
    def register_event_handler(self, name: Text, handler: Type[T]) -> None:
        """
        Register an event handler for listening to events from Asterisk

        Args:
            name (Text): Name of the event handler
            handler (EventHandler): Handler to be registered
        """
        if not issubclass(handler, EventHandler):
            raise ValueError("`handler` must be a subclass of EventHandler")
        
        # Register an event handler for listening to events from Asterisk
        self.__events.register_event_handler(name, handler)
    

    def unregister_event_handler(self, name: Text) -> None:
        """
        Unregister an event handler listening to events from Asterisk

        Args:
            name (Text): Name of the event handler to remove from listening
        """
        self.__events.unregister_event_handler(name)

    def is_connected(self):
        """
        Check if connection to Asterisk is stable and connected.
        It will return True if connection is alive otherwise False will be returned
        """
        if self.transport and not self.transport.is_closing():
            return True
        
        return False
    
    async def disconnect(self) -> None:
        """
        Disconnects from Asterisk AMI
        
        NOTE: This method is coroutine. Please use it with await prefix and inside asynchronous method
        """
        # Check if queue is empty
        if not self.queue.empty():
            # Wait for queue to be empty
            await self.queue.join()
        
        # Here we should add wait_for_actions_complete
        await self.__manager.wait_for_actions_complete()

        logoff_cmd = Action("Logoff", {})
        await self.__manager.send_action(logoff_cmd)
        self.transport.close()