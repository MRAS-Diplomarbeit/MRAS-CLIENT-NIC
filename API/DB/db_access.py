from tinydb import TinyDB, Query, where
from DB import db_middleware, json_storage
# from db_middleware import BDMiddleWare
# from json_storage import CustomJSONStorage


class Access:
    def __init__(self):
        self.db = TinyDB('./API/DB/data.json', storage=db_middleware.BDMiddleWare(json_storage.CustomJSONStorage))
        self.db.default_table_name = "var"

    @property
    def get_db(self):
        return self.db

    def search(self, param):
        return self.db.search(where('name') == param)