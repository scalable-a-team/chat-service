from crypt import methods
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import datetime
from pymongo import MongoClient
import bson.json_util as json_util
from config import *
import pymongo
from random import randint
from flask_cors import CORS, cross_origin
app = Flask(__name__)
# app.config["CORS_HEADERS"] = 'Content-Type'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

cluster = MongoClient(
    'mongodb+srv://bossqii:1234@cluster0.3jgne.mongodb.net/?retryWrites=true&w=majority')
# 'mongodb+srv://bossqi:1234@cluster0.3jgne.mongodb.net/?retryWrites=true&w=majority')
# MONGO_URI)
db = cluster['chat']
message_collection = db['messages']
session_collection = db['sessions']


# @app.route('/')
# def home():
#     return render_template('index.html')


# @app.route(API_PREFIX + '/send_message', methods=['POST'])
# def send_message():
#     req_data = request.get_json()
#     sender_id = req_data['sender_id']
#     receiver_id = req_data['receiver_id']
#     message = req_data['message']

#     data = {
#         'sender_id': sender_id,
#         'receiver_id': receiver_id,
#         'message': message,
#         'timestamp': datetime.timestamp(datetime.now())
#     }
#     message_collection.insert_one(data)
#     res = {
#         'message': 'Succesfully sent',
#         'sent_message': message
#     }
#     return res, 202


# @app.route(API_PREFIX + '/get_message/<string:sender_id>/<string:receiver_id>', methods=['GET'])
# def get_message(sender_id, receiver_id):
#     # sender_id = request.args.get('sender_id')
#     # receiver_id = request.args.get('receiver_id')
#     # message = request.args.get('message')
#     data = message_collection.find({
#         'sender_id': sender_id,
#         'receiver_id': receiver_id
#     }, sort=[('_id', pymongo.DESCENDING)])
#     # data = message_collection.find_one({
#     #     'sender_id': sender_id,
#     #     'receiver_id': receiver_id,
#     # }, sort=[
#     #     ('_id', pymongo.DESCENDING)])
#     # print(data)
#     # response = {}
#     # response['data'] = []
#     # for result in data:
#     #     response['data'].append(result)
#     # print(response)
#     if data is not None:
#         return json_util.dumps(data), 200
#     return {'message': 'error with sender and/or receiver ID'}, 400
#     # data = message_collection.find_one({}, {
#     #     'sender_id': sender_id,
#     #     'receiver_id': receiver_id
#     # })
#     # data = {
#     #     'sender_id': sender_id,
#     #     'receiver_id': receiver_id,
#     #     'message': message,
#     #     'timestamp': datetime.timestamp(datetime.now())
#     # }

# @ app.route('/')
# def home():
#     return render_template("index.html")


@ app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))
# @app.route('/chat')
# def chat():
#     sender = request.args.get('sender')
#     receiver = request.args.get('receiver')
#     if sender and receiver:
#         return render_template('chat.html',  sender=sender, receiver=receiver)
#     else:
#         return redirect(url_for('home'))


# @app.route('/receiver')
# def receiver():
#     return render_template('receiver.html')


# @app.route('/chat_receiver')
# def chat_receiver():
#     sender = request.args.get('sender')
#     receiver = request.args.get('receiver')
#     return render_template('chat_receiver.html', sender=sender, receiver=receiver)
# class Message(Resource):
#     def get(self, message_id):
#         res = {"message_id": message_id}
#         return res


@ app.route('/get_session')
def get_session():
    sender = request.args.get('sender')[1:]
    receiver = request.args.get('receiver')[1:]
    print(sender, receiver)
    res = session_collection.find_one(
        {'sender': sender, 'receiver': receiver}, sort=['_id', pymongo.descending])
    # Vsort=[
    #     ('_id', pymongo.DESCENDING)])

    print(res)
    return json_util.dumps(res['session_id']), 200
    # print(sender, receiver)
    # return '''<h1>The source value is: {} {}</h1>'''.format(sender, receiver)
# @app.route('/get_message/<int:session_id>')


# @app.route('/get_message/<int:session_id>')
# def get_message(session_id):
#     # print(session_id)
#     # print(request.args.get('session_id'))
#     res = message_collection.find_one({'session_id': int(session_id)}, sort=[
#         ('_id', pymongo.DESCENDING)])
#     # print(results)
#     # response = {}
#     # response['data'] = []
#     # for result in results:
#     #     response['data'].append(result)
#     # print(response)
#     return json_util.dumps(res), 200

# api.add_resource(Message, '/message/<int:message_id>')
@ socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['sender_id'],
                                                                    data['receiver_id'],
                                                                    data['message']))
    res = {
        'sender_id': data['sender_id'],
        'receiver_id': data['receiver_id'],
        'timestamp': datetime.timestamp(datetime.now()),
        'message': data['message']
    }
    # res = session_collection.find_one(
    #     {'sender': sender, 'receiver': receiver}, sort=['_id', pymongo.descending])
    session_id = session_collection.find_one(
        {'user': data['receiver_id']}, sort=[('_id', pymongo.DESCENDING)])
    print(session_id['session_id'])

    # message_collection.insert_one(res)
    socketio.emit('receive_message', data, room=session_id['session_id'])


@ socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(
        data['username'], data['room']))
    join_room(data['room'])
    # socketio.emit('join_room_announcement', data, room=data['room'])


# @ socketio.on('leave_room')
# def handle_leave_room_event(data):
#     app.logger.info("{} has left the room {}".format(
#         data['username'], data['room']))
#     leave_room(data['room'])
#     socketio.emit('leave_room_announcement', data, room=data['room'])


# @socketio.on('send_message')
# def handle_send_message_event(data):
#     app.logger.info('{} has sent message to {}: {} in session {}'.format(
#         data['sender'], data['receiver'], data['message'], data['session_id']))
#     res = {'sender_id': data['sender'], 'receiver_id': data['receiver'],
#            'session_id': data['session_id'], 'message': data['message']}
#     message_collection.insert_one(res)
#     socketio.emit('receive_message', data, room=data['session_id'])


# @socketio.on('join_session')
# def handle_jon_session(data):
#     app.logger.info('welcome to session {}'.format(data['session_id']))
#     join_room(data['session_id'])
#     session_collection.insert_one({'session_id':
#                                    data['session_id'], 'sender': data['sender'], 'receiver': data['receiver']})


# @socketio.on('join_room')
# def handle_join_room_event(data):
#     app.logger.info("{} has joined the room {}".format(
#         data['sender'], data['receiver']))
#     join_room(data['receiver'])
#     res = {'session_id': int(data['receiver']), 'user_id': data['sender']}
#     session_collection.insert_one(res)
#     socketio.emit('join_room_announcement', data, room=data['receiver'])


# FOR SESSION
@app.route('/api/establish_conn/<string:sender_id>', methods=["GET"])
# @cross_origin()
def establish_conn(sender_id):
    session_id = randint(10000, 99999)
    found_session = session_collection.find_one({'user': sender_id})
    if found_session is None:
        data = {
            'session_id': session_id,
            'user': sender_id
        }
        session_collection.insert_one(data)
        res = {
            'message': 'establishing connection succesfully',
            'user': sender_id
        }
        return res, 202
    # response = jsonify({"order_id": 123, "status": "shipped"})
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return {'message': 'found session connection'}, 200


if __name__ == "__main__":
    socketio.run(app, debug=True)
