from flask import Flask
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)


class Message(Resource):
    def get(self, message_id):
        res = {"message_id": message_id}
        return res


api.add_resource(Message, '/message/<int:message_id>')

if __name__ == "__main__":
    app.run(debug=True)
