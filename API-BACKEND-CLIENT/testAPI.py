from flask import Flask, request
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class test(Resource):
    def get(self):
        print("api1 entry")
        return {'error': 'jo'}, 500


api.add_resource(test, "/api/v1/test")

if __name__ == '__main__':
    app.run(port=3020)
