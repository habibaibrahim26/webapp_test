from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client['library']
collection =db['books']

app = Flask(__name__)


@app.route('/books', methods =['GET'])
def get_books():
    books=list(collection.find())
    for book in books:
        book['_id'] =str(book['_id'])
    return jsonify(books), 200


@app.route('/books/add', methods =['POST'])
def add_books():
    data = request.json
    if not data.get("name"):
        return jsonify({'error': 'Book name is required'}), 400

    new_book ={
        'name' : data['name'],
        'status' : True
    }

    op= collection.insert_one(new_book)

    new_book['_id'] = str(op.inserted_id)

    return jsonify(new_book),201

@app.route('/book/deleteone', methods =['DELETE'])
def delete_book():
    data = request.json
    book = data.get("name")
    if not book:
        return jsonify({"ERROR ":"book name required"}),400
    op = collection.delete_one({'name': book})

    if op.deleted_count ==0:
        return jsonify({"ERROR":" book not found"}),404
    return jsonify({"message":"Book successfully deleted"}),200
    


@app.route('/book/status', methods =['PATCH'])
def update_book():
    data = request.json
    book = data.get("name")
    if not book:
        return jsonify({"ERROR ":"book name required"}),400
    op = collection.update_one({'name':book}, { "$set": {"status": False}})
    if op.matched_count ==0: 
        return jsonify({"ERROR":" book not found"}),404
    return jsonify({"message":"Book's status successfully updated"}),200








if __name__ == '__main__':
    app.run(debug=True)