from fastapi import FastAPI, Depends, HTTPException
from . import models, schemas, crud, auth
from .database import SessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/books/", response_model=list[schemas.Book])
def get_books(db: Session = Depends(get_db)):
    return crud.get_books(db)

@app.post("/readers/", response_model=schemas.Reader)
def create_reader(reader: schemas.ReaderCreate, db: Session = Depends(get_db)):
    return crud.create_reader(db, reader)

@app.post("/return/")
def return_book(return_data: schemas.ReturnBookBase, db: Session = Depends(get_db)):
    try:
        return crud.return_book(db, return_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db, user)
    return {"message": "User created"}

@app.post("/books/")
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    return crud.create_book(db, book)

@app.post("/borrow/")
def borrow_book(borrow: schemas.BorrowedBookBase, db: Session = Depends(get_db)):
    try:
        return crud.borrow_book(db, borrow)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))