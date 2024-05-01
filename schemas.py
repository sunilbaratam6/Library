from fastapi import FastAPI, HTTPException, Depends
from database import Students, Books, Inventory, Records, session
from sqlalchemy import func
from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional


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


class StudentResponse(BaseModel):
    name: str
    standard: str
    roll_no: int


class BookResponse(BaseModel):
    book_name: str


class InventoryResponse(BaseModel):
    message: str


class RecordResponse(BaseModel):
    student_id: int
    book_id: int
    status: str


class PopularBookResponse(BaseModel):
    book_name: str
    # count: int
