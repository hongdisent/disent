from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Initialize FastAPI app
app = FastAPI(
    title="Book API",
    description="A simple API for managing books",
    version="1.0.0",
)

# In-memory database
books_db = []

# Book model
class Book(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    published_year: int

# Create book model (without ID for POST requests)
class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    published_year: int

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Book API!"}

# Create a book
@app.post("/books/", response_model=Book, status_code=201)
def create_book(book: BookCreate):
    book_id = len(books_db) + 1
    new_book = Book(id=book_id, **book.dict())
    books_db.append(new_book)
    return new_book

# Get all books
@app.get("/books/", response_model=List[Book])
def read_books():
    return books_db

# Get a single book by ID
@app.get("/books/{book_id}", response_model=Book)
def read_book(book_id: int):
    for book in books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

# Update a book
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookCreate):
    for index, book in enumerate(books_db):
        if book.id == book_id:
            updated_book = Book(id=book_id, **book_update.dict())
            books_db[index] = updated_book
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

# Delete a book
@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for index, book in enumerate(books_db):
        if book.id == book_id:
            books_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Book not found")