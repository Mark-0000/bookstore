import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient(
    "mongodb+srv://nine:root@nine-nfire.f9yn8.mongodb.net/bookstore?retryWrites=true&w=majority")
db = client['bookstore']
col_users = db['users']
col_books = db['books']

to_delete = {
    '_id': ObjectId("603c0d134b689bdc5270dda4")
}

col_books.delete_one(to_delete)