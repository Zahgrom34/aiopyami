class AuthenticationError(Exception):
    def __init__(self, login: str, secret: str) -> None:
        self.login = login
        self.secret = secret
    
    def __str__(self) -> str:
        return f"Failed to authenticate to AsteriskAMI with {self.login} as username and {self.secret} as password"
    

class NoConnectionMade(Exception):
    pass


class SerializationError(Exception):
    pass