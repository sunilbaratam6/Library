from fastapi import FastAPI, HTTPException, Depends
from database import Students, Books, Inventory, Records, session
from sqlalchemy import func
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker


app = FastAPI()


class StudentCreate(BaseModel):
    name: str
    standard: str
    roll_no: int


class BookCreate(BaseModel):
    book_name: str
    author: str


class InventoryCreate(BaseModel):
    stock: int = 50


class RecordCreate(BaseModel):
    student_id: int
    book_id: int
    status: str


class InventoryUpdate(BaseModel):
    new_stock: int


class IssueReturn(BaseModel):
    book_name: str
    student_roll_no: int


class UpdateInventory(BaseModel):
    book_name: str
    new_stock: int


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


@app.post("/register-student")
async def student_reg(student: StudentCreate, db: Session = Depends(get_db)):
    student = Students(name=student.name, standard=student.standard,
                       roll_no=student.roll_no, count_of_books=0)
    db.add(student)
    db.commit()
    return {"User Added": student.name}


@app.post("/add-book")
async def add_book(book: BookCreate, db: Session = Depends(get_db)):
    book = Books(book_name=book.book_name, author=book.author)
    db.add(book)
    db.commit()
    return {"Book Added": book.book_name}


@app.post("/add/inventory")
async def add_inventory(inventory: InventoryCreate, book_name: str, db: Session = Depends(get_db)):
    books = db.query(Books).filter(Books.book_name == book_name).first()
    if books is None:
        raise HTTPException(status_code=404, detail="Book not found")
    inventory = Inventory(book_id=books.id, stock=inventory.stock)
    db.add(inventory)
    db.commit()
    return {"Inventory Added": book_name}


@app.post("/issue")
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
    return {"Book Issued"}


@app.post("/return")
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
    return {"Book returned"}


@app.put("/update/{id}")
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
    return {"Updated"}


@app.get('/get_popular_books')
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
    l = []
    for each in popular_books:
        book_id = each[0]
        book = db.query(Books).filter(Books.id == int(book_id)).first()
        l.append({"Book": book.book_name, "count": each[1]})
    return {"Popular Books": l}
