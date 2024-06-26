from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship


DATABASE_URL = "sqlite:///databases.db"


engine = create_engine(DATABASE_URL)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session = session()

Base = declarative_base()


class Students(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    standard = Column(String)
    roll_no = Column(Integer)
    count_of_books = Column(Integer)


class Books(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    book_name = Column(String)
    author = Column(String)
    inventory = relationship(
        "Inventory", back_populates="book", uselist=False)
    record = relationship("Records", back_populates="book")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), unique=True)
    stock = Column(Integer, default=50)
    book = relationship("Books", back_populates="inventory")


class Records(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('books.id'))
    book_id = Column(String)
    status = Column(String)
    book = relationship("Books", back_populates="record")


Base.metadata.create_all(engine)
