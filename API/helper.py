from datetime import datetime


def data_available(data, should_include):
    if data is None:
        return should_include
    missing_param = []
    for param in should_include:
        if param not in data:
            missing_param.append(param)
    return missing_param


def add_time(message: str) -> str:
    return str(datetime.now()) + " " + message
