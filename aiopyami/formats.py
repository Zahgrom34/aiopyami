from dataclasses import dataclass
from typing import Any
from aiopyami.exceptions import SerializationError

from aiopyami.utils import dump_data, stringify_data

@dataclass
class Action:
    action: str
    params: dict[str, str]

    def ami_format(self) -> str:
        ami_params = "\r\n".join([f"{key}: {value}" for key, value in self.params.items()])
        return f"Action: {self.action}\r\n{ami_params}\r\n\r\n"
    
    # TODO: let it stay for now. Maybe this feature is useless.
    @classmethod
    def dump_data(cls, data: str) -> 'Action':
        lines = data.strip().split("\r\n")
        action_line = lines.pop(0)
        action = action_line.split(":")[1].strip()

        params = {}
        for line in lines:
            key, value = line.split(":", 1)
            params[key.strip()] = value.strip()

        return cls(action=action, params=params)
    

class AsteriskResponse:

    def __init__(self, *args, **kwargs) -> None:
        self._data = dict(*args, **kwargs)
        self._response = ""
    
    @staticmethod
    def from_response(response: str | dict) -> 'AsteriskResponse':
        if type(response) is str:
            try:
                instance = AsteriskResponse()
                instance._data = dump_data(response)
                instance._response = response

            except Exception as e:
                raise SerializationError(
                    "Failed to serialize response data: %s" % e)
        
        if type(response) is dict:
            instance = AsteriskResponse()
            instance._data = response
            instance._response = stringify_data(response)
        
        return instance
    
    def to_dict(self):
        return self._data

    def __str__(self) -> str:
        return self._response
    
    def __add__(self, other: 'AsteriskResponse'):
        return AsteriskResponse(**{**self._data, **other._data})
    
    def __getitem__(self, key: object):
        return self._data[key]
    
    def __setitem__(self, key: object, value: Any):
        self._data[key] = value
    
    def __delitem__(self, key: object):
        del self._data[key]
