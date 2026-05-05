from typing import Annotated
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path, Query, Body
from starlette import status
from DB.models import Expenses
from Expenses import ExpenseCreate, ExpensePaid
from DB.db import engine, SessionLocal, Base

app = FastAPI()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()   
    try:
        yield db          
        db.commit()       
    except:
        db.rollback()     
        raise            
    finally:
        db.close()
DbDependency = Annotated[Session, Depends(get_db)]

@app.get("/expenses", status_code=status.HTTP_200_OK)
def get_all_expenses(db: DbDependency):
    try:
        data = db.query(Expenses).all()
        return data
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.get("/expenses/category", status_code=status.HTTP_200_OK)
def get_category(db: DbDependency, category: str = Query(min_length=3)):
    try:
        category_list = db.query(Expenses).filter(Expenses.category == category).all()
        return category_list
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.get("/expenses/summary", status_code=status.HTTP_200_OK)
def get_summary(db: DbDependency):
    try:
        total_amount = db.query(func.sum(Expenses.amount)).scalar()
        return f"Total Amount Spend: {total_amount}"
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.get("/expenses/{id}", status_code=status.HTTP_200_OK)
def get_expense_by_id(db: DbDependency, id: int = Path(gt=0)):
    try:
        get_matched_expense = db.query(Expenses).filter(Expenses.id == id).first()
        return get_matched_expense
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def add_expense(db: DbDependency,new_expense: ExpenseCreate):
    try:
        data = Expenses(**new_expense.dict())
        db.add(data)
        return "Data added to the DB"
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.put("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def update_expense(db: DbDependency,data: ExpenseCreate, id: int = Path(gt=0)):
    try:
        db_data = db.query(Expenses).filter(Expenses.id == id).first()
        db_data.title = data.title
        db_data.amount = data.amount
        db_data.category = data.category
        db_data.paid = data.paid
        db.add(db_data)
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.patch("/expenses/{id}",status_code=status.HTTP_202_ACCEPTED)
def update_paid_field(db: DbDependency,data: ExpensePaid, id: int = Path(gt=0)):
    try:
        db_data = db.query(Expenses).filter(Expenses.id == id).first()
        db_data.paid = data.paid
        db.add(db_data)
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")

@app.delete("/expenses/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(db: DbDependency, id: int = Path(gt=0)):
    try:
        db.query(Expenses).filter(Expenses.id == id).delete()
        return "Data Deleted Successfully"
    except:
        raise HTTPException(status_code=404, detail="Todo not found..")