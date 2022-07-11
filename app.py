import re
from flask import Flask, redirect, render_template, request, url_for
from flask_socketio import SocketIO, join_room
# from flask_restful import Api, Resource
from pymongo import MongoClient
import bson.json_util as json_util
import json

import pymongo

app = Flask(__name__)
socketio = SocketIO(app)

cluster = MongoClient(
    'mongodb+srv://bossqi:1234@cluster0.3jgne.mongodb.net/?retryWrites=true&w=majority')
db = cluster['chat']
message_collection = db['messages']
session_collection = db['sessions']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat')
def chat():
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')
    if sender and receiver:
        return render_template('chat.html',  sender=sender, receiver=receiver)
    else:
        return redirect(url_for('home'))


@app.route('/receiver')
def receiver():
    return render_template('receiver.html')


@app.route('/chat_receiver')
def chat_receiver():
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')
    return render_template('chat_receiver.html', sender=sender, receiver=receiver)
# class Message(Resource):
#     def get(self, message_id):
#         res = {"message_id": message_id}
#         return res


@app.route('/get_session')
def get_session():
    sender = request.args.get('sender')[1:]
    receiver = request.args.get('receiver')[1:]
    print(sender, receiver)
    res = session_collection.find_one(
        {'sender': sender, 'receiver': receiver})
    # Vsort=[
    #     ('_id', pymongo.DESCENDING)])

    print(res)
    return json_util.dumps(res['session_id']), 200
    # print(sender, receiver)
    # return '''<h1>The source value is: {} {}</h1>'''.format(sender, receiver)
# @app.route('/get_message/<int:session_id>')


@app.route('/get_message/<int:session_id>')
def get_message(session_id):
    # print(session_id)
    # print(request.args.get('session_id'))
    res = message_collection.find_one({'session_id': int(session_id)}, sort=[
        ('_id', pymongo.DESCENDING)])
    # print(results)
    # response = {}
    # response['data'] = []
    # for result in results:
    #     response['data'].append(result)
    # print(response)
    return json_util.dumps(res), 200

# api.add_resource(Message, '/message/<int:message_id>')


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info('{} has sent message to {}: {} in session {}'.format(
        data['sender'], data['receiver'], data['message'], data['session_id']))
    res = {'sender_id': data['sender'], 'receiver': data['receiver'],
           'session_id': data['session_id'], 'message': data['message']}
    message_collection.insert_one(res)
    socketio.emit('receive_message', data, room=data['session_id'])


@socketio.on('join_session')
def handle_jon_session(data):
    app.logger.info('welcome to session {}'.format(data['session_id']))
    join_room(data['session_id'])
    session_collection.insert_one({'session_id':
                                   data['session_id'], 'sender': data['sender'], 'receiver': data['receiver']})
# @socketio.on('join_room')
# def handle_join_room_event(data):
#     app.logger.info("{} has joined the room {}".format(
#         data['username'], data['room']))
#     join_room(data['room'])
#     res = {'session_id': int(data['room']), 'user_id': data['username']}
#     session_collection.insert_one(res)
#     socketio.emit('join_room_announcement', data, room=data['room'])


if __name__ == "__main__":
    socketio.run(app, debug=True)
