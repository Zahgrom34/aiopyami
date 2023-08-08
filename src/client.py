import asyncio
import socket

from asyncio import Transport
from typing import List
from src.formats import Action
from src.internal import InternalHandler

from src.ami import AsteriskManager

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
    

    async def connect(self, login: str, password: str):
        """
        Creates a new connection and AMI manager instance

        Args:
            login (str): AMI login credentials
            password (str): AMI password credentials
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


    async def subscribe_to_events(self, event_types: List[str]):
        """
        Subscribes to events which will 
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
        
    
    async def disconnect(self):
        """
        Disconnects from Asterisk AMI
        """
        logoff_cmd = Action("Logoff", {})
        await self.__manager.send_action(logoff_cmd)
        self.transport.close()