def dump_data(data: str):
    lines = data.strip().split("\r\n")

    dictionary = {}
    for line in lines:
        key, value = line.split(":", 1)
        dictionary[key.strip()] = value.strip()

    return dictionary


def stringify_data(data: dict):
    stringified = "\r\n".join([f"{key}: {value}" for key, value in data.items()])
    return f"{stringified}\r\n\r\n"