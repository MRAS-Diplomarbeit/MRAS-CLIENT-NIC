import os
import platform
import sys

import yaml


class Client:
    def __init__(self, filepath):
        try:
            file = open(r'' + filepath)
            yaml_file = yaml.load(file, Loader=yaml.FullLoader)
            self._log_name = yaml_file['client']['logfile']
            self._log_path = yaml_file['logs']['path']
            self._max_size = yaml_file['logs']['maxSize']
            self._old_logs = yaml_file['logs']['oldLogs']
            self.error = None
        except (IOError, TypeError, KeyError) as e:
            self.error = e

    @property
    def log_name(self):
        return self._log_name

    @log_name.setter
    def log_name(self, value):
        # TODO: write to yaml file
        pass

    @property
    def log_path(self):
        return self._log_path

    @log_path.setter
    def log_path(self, value):
        # TODO. write to yaml
        pass

    @property
    def max_size(self):
        # Load log size in MB and convert to KB and Byte
        return self._max_size * 1024 * 1024

    @max_size.setter
    def max_size(self, value):
        self._max_size = value

    @property
    def old_logs(self):
        return self._old_logs

    @old_logs.setter
    def old_logs(self, value):
        self._old_logs = value


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

def err_handling(error, api_path):
    if type(error) is TypeError or type(error) is KeyError:
        print("Please provide all required fields for: " + api_path + " in the .env.yml")
        print("Error loading config file. Please provide .env.yml in the project root folder.")
        current_dir = os.getcwd()
        if platform.system() == 'Linux':
            print("The root folder is: " + current_dir[0:current_dir.rfind("/") + 1])
        elif platform.system() == 'Windows':
            print("The root folder is: " + current_dir[0:current_dir.rfind("\\") + 1])
        print(error)
    print(error)
    sys.exit(-1)
