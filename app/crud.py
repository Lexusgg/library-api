from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas

def get_book(db: Session, book_id: int):
    """Получить книгу по ID"""
    return db.query(models.Book).filter(models.Book.id == book_id).first()

def get_books(db: Session, skip: int = 0, limit: int = 100):
    """Получить список книг с пагинацией"""
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_book(db: Session, book: schemas.BookCreate):
    """Создать новую книгу"""
    db_book = models.Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_reader(db: Session, reader_id: int):
    """Получить читателя по ID"""
    return db.query(models.Reader).filter(models.Reader.id == reader_id).first()

def get_readers(db: Session, skip: int = 0, limit: int = 100):
    """Получить список читателей с пагинацией"""
    return db.query(models.Reader).offset(skip).limit(limit).all()

def create_reader(db: Session, reader: schemas.ReaderCreate):
    """Создать нового читателя"""
    db_reader = models.Reader(**reader.dict())
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader

def get_borrowed_books(db: Session, reader_id: int = None):
    """Получить список выданных книг (можно фильтровать по reader_id)"""
    query = db.query(models.BorrowedBook).filter(models.BorrowedBook.return_date == None)
    if reader_id:
        query = query.filter(models.BorrowedBook.reader_id == reader_id)
    return query.all()

def borrow_book(db: Session, borrow: schemas.BorrowedBookBase):
    """Выдать книгу читателю"""
    # Проверка существования книги и читателя
    book = db.query(models.Book).filter(models.Book.id == borrow.book_id).first()
    reader = db.query(models.Reader).filter(models.Reader.id == borrow.reader_id).first()
    
    if not book:
        raise ValueError("Книга не найдена")
    if not reader:
        raise ValueError("Читатель не найден")
    if book.copies <= 0:
        raise ValueError("Нет доступных экземпляров книги")

    # Проверка лимита книг у читателя (не более 3)
    borrowed_count = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.reader_id == borrow.reader_id,
        models.BorrowedBook.return_date == None
    ).count()
    
    if borrowed_count >= 3:
        raise ValueError("Читатель уже имеет максимальное количество книг (3)")

    # Создание записи о выдаче
    db_borrow = models.BorrowedBook(
        book_id=borrow.book_id,
        reader_id=borrow.reader_id,
        borrow_date=datetime.utcnow()
    )
    db.add(db_borrow)
    book.copies -= 1
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

def return_book(db: Session, return_data: schemas.ReturnBookBase):
    """Вернуть книгу в библиотеку"""
    # Находим активную запись о выдаче
    borrowed = db.query(models.BorrowedBook).filter(
        models.BorrowedBook.book_id == return_data.book_id,
        models.BorrowedBook.reader_id == return_data.reader_id,
        models.BorrowedBook.return_date == None
    ).first()
    
    if not borrowed:
        raise ValueError("Активная выдача книги не найдена")

    # Обновляем запись
    borrowed.return_date = datetime.utcnow()
    book = db.query(models.Book).filter(models.Book.id == return_data.book_id).first()
    if book:
        book.copies += 1
    db.commit()
    return borrowed