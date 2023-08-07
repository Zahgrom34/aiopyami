import asyncio
import socket

from asyncio import Transport
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
            # Connect to ami client
            self.ami_socket = await loop.create_connection(lambda: self, self.host, self.port)
            
            # Create connection action
            login_cmd = Action("Login", {
                "Username": login,
                "Secret": password
            })
            await self.__manager.send_action_callback(login_cmd, InternalHandler.asterisk_authenticated)
            
            return self.__manager

        except socket.gaierror as ge:
            raise ConnectionError(f"Failed to resolve hostname: {ge}")
        except socket.timeout as te:
            raise ConnectionError(f"Connection to Asterisk AMI timed out: {te}")
        except socket.error as se:
            raise ConnectionError(f"Failed to connect to Asterisk AMI: {se}")

    
    def connection_made(self, transport: Transport) -> None:
        self.transport = transport

    
    def data_received(self, data: bytes) -> None:
        response = data.decode()
        self.queue.put_nowait(response)

        if "ActionID" in response:
            asyncio.create_task(self.__manager._dispatch_action(response))


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