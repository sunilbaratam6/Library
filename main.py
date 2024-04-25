from fastapi import FastAPI, HTTPException
from database import Students, Books, Inventory, Records, session
from sqlalchemy import func

app = FastAPI()


@app.get('/')
async def get_books():
    books = session.query(Books)
    return books.all()


@app.post("/register-student")
async def student_reg(name: str, standard: str, roll_no: int):
    S = Students(name=name, standard=standard,
                 roll_no=roll_no, count_of_books=0)
    session.add(S)
    session.commit()
    return {"User Added": S.name}


@app.post("/add-book")
async def add_book(book_name: str, author: str):
    B = Books(book_name=book_name, author=author)
    session.add(B)
    # session.query(Books).delete()
    session.commit()
    return {"Book Added": B.book_name}


@app.post("/add/inventory")
async def add_inventory(book_name: str, stock: int):
    books = session.query(Books)
    book = books.filter(Books.book_name == book_name).first()
    Invent = session.query(Inventory)
    invent = Invent.filter(Inventory.book_id == book.id)
    if invent is None:
        I = Inventory(book_id=book.id, stock=stock)
        session.add(I)
        session.commit()
        return {"Inventory Added": book_name}
    return {"Already Present"}


@app.post("/issue")
async def issue(book_name: str, student_roll_no: int):
    students = session.query(Students)
    student = students.filter(
        Students.roll_no == student_roll_no).first()
    count = student.count_of_books
    books = session.query(Books)
    book = books.filter(Books.book_name == book_name).first()
    Invent = session.query(Inventory)
    invent = Invent.filter(Inventory.book_id == book.id).first()
    if invent.stock == 0:
        raise HTTPException(status_code=400, detail="Out of Stock")
    if count > 3:
        return {"Max limit reached"}
    if book is None:
        raise HTTPException(status_code=400, detail="Book is not present")
    R = Records(student_id=student_roll_no, book_id=book.id, status='Issue')
    session.add(R)
    student.count_of_books += 1
    session.commit()
    return {"Book Issued"}


@app.post("/return")
async def return_back(book_name: str, student_roll_no: int):
    students = session.query(Students)
    student = students.filter(
        Students.roll_no == student_roll_no).first()
    count = student.count_of_books
    books = session.query(Books)
    book = books.filter(Books.book_name == book_name).first()
    R = Records(student_id=student_roll_no, book_id=book.id, status='Return')
    session.add(R)
    student.count_of_books -= 1
    session.commit()
    return {"Book returned"}


@app.put("/update/{id}")
async def update_inventory(
    book_name: str,
    new_stock: int
):
    books = session.query(Books)
    book = books.filter(Books.book_name == book_name).first()
    l = book.id
    Invent = session.query(Inventory)
    invent = Invent.filter(Inventory.book_id == l).first()
    # print(invent.stock)
    if invent is not None:
        invent.stock += new_stock
        session.commit()
        return {"Updated"}
    return {"Not Found"}


@app.get('/get_popular_books')
async def get_popular_books():

    popular_books = session.query(Records.book_id, func.count(Records.book_id)).filter(
        Records.status == 'Issue').group_by(Records.book_id).order_by(func.count(Records.book_id).desc()).limit(5).all()
    l = []
    for each in popular_books:
        book_id = each[0]
        books = session.query(Books)
        book = books.filter(Books.id == int(book_id)).first()
        l.append(book.book_name)

    return {"Popular Books": l}
