from tinydb.storages import Storage
import json


class CustomJSONStorage(Storage):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        with open(self.filename) as json_file:
            data = json.load(json_file)
            return data

    def write(self, data):
        with open(self.filename, "w+") as handle:
            json.dump(data, handle)

    def close(self):
        pass
