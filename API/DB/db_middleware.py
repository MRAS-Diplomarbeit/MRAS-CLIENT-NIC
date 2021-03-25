from tinydb.middlewares import Middleware


class BDMiddleWare(Middleware):
    def __init__(self, storage_cls):
        # super(self).__init__(storage_cls)
        super().__init__(storage_cls)

    def read(self):
        data = self.storage.read()

        for table_name in data:
            table_data = data[table_name]

            for doc_id in table_data:
                item = table_data[doc_id]

                if item == {}:
                    del table_data[doc_id]

        return data

    def write(self, data):
        for table_name in data:
            table_data = data[table_name]

            for doc_id in table_data:
                item = table_data[doc_id]

                if item == {}:
                    del table_data[doc_id]

        self.storage.write(data)

    def close(self):
        self.storage.close()