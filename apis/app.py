from importlib.resources import path
import json
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import datetime, timedelta
from pymongo import MongoClient
import bson.json_util as json_util
from config import *
import pymongo
import os
from random import randint
from flask_cors import CORS, cross_origin
app = Flask(__name__)
print('init')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", path='api/chat/socket.io')
MONGO_HOST = os.environ['DB_HOST']
MONGO_PORT = os.environ['DB_PORT']
MONGO_DRIVE = f'mongodb://{MONGO_HOST}:{MONGO_PORT}'
print('-----------')
print(MONGO_DRIVE)
print('-----------')
cluster = MongoClient(
    MONGO_DRIVE)
db = cluster['chat']
message_collection = db['messages']
session_collection = db['sessions']


@app.route(API_PREFIX + '/chat/test')
def test():
    return 'test',200
@app.route(API_PREFIX + '/chat/get_messages/<string:sender_id>/<string:receiver_id>', methods=['GET'])
def get_messages(sender_id, receiver_id):
    data1 = message_collection.find({
        'sender_id': sender_id,
        'receiver_id': receiver_id
    }, sort=[('_id', pymongo.DESCENDING)])
    data2 = message_collection.find({
        'sender_id': receiver_id,
        'receiver_id': sender_id
    }, sort=[('_id', pymongo.DESCENDING)])
    s1 = json.loads(json_util.dumps(data1))
    s2 = json.loads(json_util.dumps(data2))
    s3 = []

    for data in s1:
        data['ts'] = datetime.fromtimestamp(
            data['timestamp']).strftime("%Y-%m-%d %H:%M")
        s3.append(data)
    for data in s2:
        data['ts'] = datetime.fromtimestamp(
            data['timestamp']).strftime("%Y-%m-%d %H:%M")
        s3.append(data)
    s4 = sorted(s3, key=lambda x: (float(x['timestamp'])))
    if s1 is not None or s2 is not None:
        return json.dumps(s4), 200
    return {'message': 'error with sender and/or receiver ID'}, 400


@app.route(API_PREFIX + '/chat/get_messages_channel/<string:sender_id>', methods=['GET'])
def get_messages_channel(sender_id):
    data1 = message_collection.distinct('receiver_id', {'sender_id': sender_id})
    data2 = message_collection.distinct('sender_id', {'receiver_id': sender_id})
    data3 = data1 + data2

    if data1 is not None or data2 is not None:
        return json_util.dumps(list(set(data3))), 200
    return {'message': 'no channel yet'}, 200



@ socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {} (): with message {}".format(data['sender_id'], data['receiver_id'],
                                                                                    #   data['room_id'],
                                                                                    data['message']))
    res = {
        'sender_id': data['sender_id'],
        'receiver_id': data['receiver_id'],
        'timestamp': datetime.timestamp(datetime.now()),
        'message': data['message']
    }
    session_id = session_collection.find_one(
        {'user': data['receiver_id']}, sort=[('_id', pymongo.DESCENDING)])

    message_collection.insert_one(res)
    socketio.emit('receive_message', data, room=session_id['session_id'])


@ socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(
        data['username'], data['room_id']))
    join_room(data['room_id'])


# FOR SESSION
@ app.route(API_PREFIX + '/chat/establish_conn/<string:sender_id>', methods=["GET"])
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
            'user': sender_id,
            'session_id': session_id
        }
        return res, 202
    return {'message': 'found session connection', 'session_id': found_session['session_id']}, 200


if __name__ == "__main__":
    print('test')
    print(os.environ['DB_HOST'])
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)
