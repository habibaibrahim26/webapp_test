from fastapi import FastAPI , HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv
from typing import List


load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client['library']
collection =db['books']

app = FastAPI()

class Book(BaseModel):
    name: str

class BookResponse(Book):
    id :str
    status: bool



@app.get('/books', response_model = List[BookResponse])
def get_books():
    books=list(collection.find())
    for book in books:
        book['id'] =str(book['_id'])
        del book['_id']
    return books



@app.get('/books/{book_id}', response_model = BookResponse)
def get_book(book_id : str):
    book = collection.find_one({'_id':ObjectId(book_id)})
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    book['id'] =str(book['_id'])
    del book['_id']
    
    return book



@app.post('/books/add', response_model=BookResponse, status_code=201)
def add_books(book:Book):
    
    if not book.name:
        raise HTTPException(status_code=400, detail ="Book name is required")

    new_book ={
        'name' : book.name,
        'status' : True
    }

    op= collection.insert_one(new_book)

    new_book['id'] = str(op.inserted_id)

    return new_book

@app.delete('/books/deleteone', status_code=200)
def delete_book(book:Book):
    if not book.name:
        raise HTTPException(status_code=400, detail ="Book name is required")
    
    op = collection.delete_one({'name': book.name})

    if op.deleted_count ==0:
        raise HTTPException(status_code=404, detail ="Book not found")
    
    return {"message": "Book deleted successfully"}
    


@app.patch('/books/status')
def update_book(book:Book):
    if not book.name:
        raise HTTPException(status_code=400, detail ="Book name is required")
    
    op = collection.update_one({'name':book.name}, { "$set": {"status": False}})

    if op.matched_count ==0: 
        raise HTTPException(status_code=404, detail ="Book not found")
    
    if op.modified_count > 0:
        return {"message":"Book's status successfully updated"}
    else:
        return {"message":"Book's status is already False"}








