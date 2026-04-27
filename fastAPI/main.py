from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

class Item(BaseModel):
    title: str
    content: str

storeItem: list[dict[str,str]] = []

@app.post("/item")
def send_item(myItem: Item):
    storeItem.append(myItem.dict())
    return {"data":myItem}

@app.get("/item")
def send_item():
    print(f"Store Items are : {storeItem}")
    return {"data":storeItem}

