def dump_data(data: str):
    lines = data.strip().split("\r\n")

    dictionary = {}
    for line in lines:
        # Check if the line contains a colon
        if ":" in line:
            key, value = line.split(":", 1)
            dictionary[key.strip()] = value.strip()
        else:
            # Handle lines without a colon (e.g., standalone messages)
            dictionary[line.strip()] = None

    return dictionary


def stringify_data(data: dict):
    stringified = "\r\n".join([f"{key}: {value}" for key, value in data.items()])
    return f"{stringified}\r\n\r\n"
