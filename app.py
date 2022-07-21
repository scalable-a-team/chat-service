import json
from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_socketio import SocketIO, join_room, leave_room
from datetime import datetime, timedelta
from pymongo import MongoClient
import bson.json_util as json_util
from config import *
import pymongo
from random import randint
from flask_cors import CORS, cross_origin
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

cluster = MongoClient(
    MONGO_URI)
db = cluster['chat']
message_collection = db['messages']
session_collection = db['sessions']


@app.route(API_PREFIX + '/get_messages/<string:sender_id>/<string:receiver_id>', methods=['GET'])
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
            data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        s3.append(data)
    for data in s2:
        data['ts'] = datetime.fromtimestamp(
            data['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        s3.append(data)
    s4 = sorted(s3, key=lambda x: (float(x['timestamp'])))
    print('--------------')
    print(s4)
    print('--------------')
    if s1 is not None or s2 is not None:
        return json.dumps(s4), 200
    return {'message': 'error with sender and/or receiver ID'}, 400


@ app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')

    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))


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
@ app.route('/api/establish_conn/<string:sender_id>', methods=["GET"])
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
    socketio.run(app, debug=True)
