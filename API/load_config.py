import os
import platform
import sys

import yaml


class Client:
    def __init__(self, filepath):
        try:
            try:
                filepath = conf_filename()
            except AttributeError:
                pass
            file = open(r'' + filepath)
            yaml_file = yaml.load(file, Loader=yaml.FullLoader)
            self._log_name = yaml_file['client']['logfile']
            self._log_path = yaml_file['logs']['path']
            self._max_size = yaml_file['logs']['maxSize']
            self._old_logs = yaml_file['logs']['oldLogs']
            self._update_port = yaml_file['server']['client']['port']
            self.error = None
        except (IOError, TypeError, KeyError) as e:
            self.error = e

    @property
    def log_name(self):
        return self._log_name

    @property
    def log_path(self):
        return self._log_path

    @property
    def max_size(self):
        # Load log size in MB and convert to KB and Byte
        return self._max_size * 1024 * 1024

    @property
    def old_logs(self):
        return self._old_logs

    @property
    def update_port(self):
        return self._update_port


class ClientBackend:
    def __init__(self, filepath):
        try:
            try:
                filepath = conf_filename()
            except AttributeError:
                pass
            file = open(r'' + filepath)
            yaml_file = yaml.load(file, Loader=yaml.FullLoader)
            self.port = yaml_file['client']['client-backend']['port']
            self.protocol = yaml_file['client']['client-backend']['protocol']
            self.path_playback = yaml_file['client']['client-backend']['path-playback']
            self.path_method = yaml_file['client']['client-backend']['path-method']
            self.error = None
        except (IOError, TypeError, KeyError) as e:
            self.error = e


class ClientClient:
    def __init__(self, filepath):
        try:
            try:
                filepath = conf_filename()
            except AttributeError:
                pass
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
        print("Please provide all required fields for: " + api_path + " in the config.yml")
        print("Error loading config file. Please provide config.yml in the project root folder.")
        current_dir = os.getcwd()
        if platform.system() == 'Linux':
            print("The root folder is: " + current_dir[0:current_dir.rfind("/") + 1])
        elif platform.system() == 'Windows':
            print("The root folder is: " + current_dir[0:current_dir.rfind("\\") + 1])
        print(error)
    print(error)
    sys.exit(-1)

def conf_filename():
    if len(sys.argv) > 1:
        # if len(sys.argv)%2 != 0:
        #     sys.exit("Arguments not valid")
        # for i in range(1, int((len(sys.argv)-1)/2)):
        #     pass
        return sys.argv[2]
    else:
        raise AttributeError()