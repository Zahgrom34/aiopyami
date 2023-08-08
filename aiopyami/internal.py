from aiopyami.exceptions import AuthenticationError
from aiopyami.formats import AsteriskResponse


class InternalHandler:
    login: str = ""
    password: str = ""

    @staticmethod
    async def asterisk_authenticated(response: AsteriskResponse):
        response = response.to_dict()
        # TODO: Rewrite console output to logging output, remove printing
        if response.get('Response', "Error") == "Error":
            raise AuthenticationError(InternalHandler.login,
                                      InternalHandler.password)
        print("Connected to asterisk server")