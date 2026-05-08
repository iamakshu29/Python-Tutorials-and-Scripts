from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ExpenseCreate(BaseModel):
    title: str = Field(min_length=3, description="Enter the Expense Title",example="Groceries")
    amount: float = Field(gt=500,lt=10000, description="Enter the Expense Amount", example=1200)

    # add set if can be added like category can be added from these in DB 
    category: str = Field(min_length=3, description="Enter the Expense Category", example="Food")
    paid: bool = Field(description="Expense Paid or Not",example=False)

class ExpensePaid(BaseModel):
    paid: bool = Field(description="Expense Paid or Not",example=False)