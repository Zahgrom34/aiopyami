from dataclasses import dataclass

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