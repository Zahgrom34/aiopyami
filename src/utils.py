def dump_data(data: str):
    lines = data.strip().split("\r\n")

    dictionary = {}
    for line in lines:
        key, value = line.split(":", 1)
        dictionary[key.strip()] = value.strip()

    return dictionary