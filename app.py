from fastapi import FastAPI, HTTPException, Depends
from database import Students, Books, Inventory, Records, session
from sqlalchemy import func
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional
from schemas import *


app = FastAPI()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.post("/register-student", response_model=StudentResponse)
async def student_reg(student: StudentCreate, db: Session = Depends(get_db)):
    student = Students(name=student.name, standard=student.standard,
                       roll_no=student.roll_no, count_of_books=0)
    db.add(student)
    db.commit()
    return StudentResponse(name=student.name, standard=student.standard, roll_no=student.roll_no)


@app.post("/add-book", response_model=BookResponse)
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    book = Books(book_name=book.book_name, author=book.author)
    db.add(book)
    db.commit()
    return BookResponse(id=book.id, book_name=book.book_name, author=book.author)


@app.post("/add/inventory", response_model=InventoryResponse)
async def add_inventory(inventory: InventoryCreate, book_name: str, db: Session = Depends(get_db)):
    books = db.query(Books).filter(Books.book_name == book_name).first()

    if books is None:
        raise HTTPException(status_code=404, detail="Book not found")
    inventory = Inventory(book_id=books.id, stock=inventory.stock)
    db.add(inventory)
    db.commit()
    response_message = f"Stock for book '{books.book_name}' has been updated"

    return InventoryResponse(message=response_message)


@app.post("/issue", response_model=RecordResponse)
async def issue(issue_return: IssueReturn, db: Session = Depends(get_db)):
    student = db.query(Students).filter(Students.roll_no ==
                                        issue_return.student_roll_no).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    book = db.query(Books).filter(Books.book_name ==
                                  issue_return.book_name).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    inventory = db.query(Inventory).filter(
        Inventory.book_id == book.id).first()
    if inventory.stock == 0:
        raise HTTPException(status_code=400, detail="Out of Stock")
    if student.count_of_books > 3:
        return {"Max limit reached"}
    record = Records(student_id=issue_return.student_roll_no,
                     book_id=book.id, status='Issue')
    db.add(record)
    student.count_of_books += 1
    inventory.stock -= 1
    db.commit()
    return RecordResponse(student_id=record.student_id, book_id=record.book_id, status=record.status)


@app.post("/return", response_model=BookResponse)
async def return_back(issue_return: IssueReturn, db: Session = Depends(get_db)):
    student = db.query(Students).filter(Students.roll_no ==
                                        issue_return.student_roll_no).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    book = db.query(Books).filter(Books.book_name ==
                                  issue_return.book_name).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    inventory = db.query(Inventory).filter(
        Inventory.book_id == book.id).first()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    record = Records(student_id=issue_return.student_roll_no,
                     book_id=book.id, status='Return')
    db.add(record)
    student.count_of_books -= 1
    inventory.stock += 1
    db.commit()
    return BookResponse(book_name=issue_return.book_name)


@app.put("/update/{id}", response_model=InventoryResponse)
async def update_inventory(update_inventory: UpdateInventory, db: Session = Depends(get_db)):
    book = db.query(Books).filter(Books.book_name ==
                                  update_inventory.book_name).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    inventory = db.query(Inventory).filter(
        Inventory.book_id == book.id).first()
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory not found")
    inventory.stock += update_inventory.new_stock
    db.commit()
    response_message = f"Stock for book '{update_inventory.book_name}' has been updated"

    return InventoryResponse(message=response_message)


@app.get('/get_popular_books', response_model=List[PopularBookResponse])
async def get_popular_books(db: Session = Depends(get_db)):
    popular_books = db.query(
        Records.book_id,
        func.count(Records.book_id).label('count')
    ).filter(
        Records.status == 'Issue'
    ).group_by(
        Records.book_id
    ).order_by(
        func.count(Records.book_id).desc()
    ).limit(5).all()

    book_ids = [book_id for book_id, _ in popular_books]

    books = db.query(Books).filter(Books.id.in_(book_ids)).all()
    print(type(books))
    return books
    # print(popular_books)
    # response_data = [{"book_name": db.query(Books).get(
    #     book_id).book_name, "count": count} for book_id, count in popular_books]
