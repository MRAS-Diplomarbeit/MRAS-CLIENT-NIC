import yaml


class Client:
    def __init__(self, filepath):
        try:
            file = open(r'' + filepath)
            yaml_file = yaml.load(file, Loader=yaml.FullLoader)
            self.log_name = yaml_file['client']['logfile']
            self.log_path = yaml_file['logs']['path']
            # Load log size in MB and convert to KB and Byte
            self.max_size = (yaml_file['logs']['maxSize']) * 1024 * 1024
            self.old_logs = yaml_file['logs']['oldLogs']
            self.error = None
        except (IOError, TypeError, KeyError) as e:
            self.error = e


class ClientBackend:
    def __init__(self, filepath):
        try:
            file = open(r'' + filepath)
            yaml_file = yaml.load(file, Loader=yaml.FullLoader)
            self.port = yaml_file['client']['client-backend']['port']
            self.protocol = yaml_file['client']['client-backend']['protocol']
            self.path = yaml_file['client']['client-backend']['path']
            self.error = None
        except (IOError, TypeError, KeyError) as e:
            self.error = e


class ClientClient:
    def __init__(self, filepath):
        try:
            file = open(r'' + filepath)
            yaml_file = yaml.load(file, Loader=yaml.FullLoader)
            self.port = yaml_file['client']['client-client']['port']
            self.protocol = yaml_file['client']['client-client']['protocol']
            self.path = yaml_file['client']['client-client']['path']
            self.error = None
        except (IOError, TypeError, KeyError) as e:
            self.error = e
