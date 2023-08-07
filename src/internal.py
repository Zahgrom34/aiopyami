from src.exceptions import AuthenticationError


class InternalHandler:
    login: str = ""
    password: str = ""

    @staticmethod
    async def asterisk_authenticated(response: dict):
        # TODO: Rewrite console output to logging output, remove printing
        if response.get('Response', "Error") == "Error":
            raise AuthenticationError(InternalHandler.login,
                                      InternalHandler.password)
        print("Connected to asterisk server")
        