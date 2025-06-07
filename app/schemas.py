from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class BookBase(BaseModel):
    title: str
    author: str
    year: int | None = None
    isbn: str | None = None
    copies: int = 1

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    class Config:
        orm_mode = True

class ReaderBase(BaseModel):
    name: str
    email: EmailStr

class ReaderCreate(ReaderBase):
    pass

class Reader(ReaderBase):
    id: int
    class Config:
        orm_mode = True

# Для возврата книги
class ReturnBookBase(BaseModel):
    book_id: int
    reader_id: int

class BorrowedBookBase(BaseModel):
    book_id: int
    reader_id: int