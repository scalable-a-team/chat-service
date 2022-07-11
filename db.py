from pymongo import MongoClient

cluster = MongoClient(
    'mongodb+srv://bossqi:1234@cluster0.3jgne.mongodb.net/?retryWrites=true&w=majority')
db = cluster['chat']
collection = db['messages']

post = {'sender_id': 'boss', 'receiver_id': 'yuqi',
        'session_id': 1, 'message': 'hiii'}

# collection.insert_one(post)
# collection.insert_one({})
# results = collection.find({'session_id': 1})
# for result in results:
#     print(result['sender_id'], result['receiver_id'])
# results = collection.delete_one({'id':0})
# collection.update_one({'session_id': 1}, {'$set': {'message': 'i luv you'}})
# post_count = collection.count_documents({})
