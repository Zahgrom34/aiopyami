import asyncio
import os
import sys
import unittest
from src.ami import AsteriskManager

from src.client import Client
from src.exceptions import AuthenticationError

# Connection credentials
ASTERISK_HOST = '213.230.120.177'
ASTERISK_PORT = 5038
ASTERISK_USERNAME = 'autocall'
ASTERISK_PASSWORD = '86ae14978e03c7b7417ca9a17a0b52b5'

class TestClient(unittest.IsolatedAsyncioTestCase):
    async def test_connection(self):
        am = Client(ASTERISK_HOST, ASTERISK_PORT)
        
        print("Connecting to server...")
        manager = await am.connect(ASTERISK_USERNAME, ASTERISK_PASSWORD)
        self.assertIsInstance(manager, AsteriskManager)
    
        

if __name__ == "__main__":

    unittest.main()