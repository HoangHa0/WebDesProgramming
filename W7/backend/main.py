import asyncio
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemPublic(BaseModel):
    id: int
    name: str
    price: float
    
app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

_items: list[ItemPublic] = []
_next_id: int = 1

def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None

@app.get("/")
def read_root():
    return {"message": "Hello World"}  

# Get an item
@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

# Get items
@app.get("/items")
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, min_length=2)
):
    return _items[skip : skip + limit]

# Create an item
@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
    global _next_id
    newItem = ItemPublic(id=_next_id, name=data.name, price=data.price)
    _items.append(newItem)
    _next_id += 1
    return newItem 

# Update an item
@app.put("/items", response_model=ItemPublic)
def update_item(item_id: int, data: ItemCreate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    updated = ItemPublic(id=item.id, name=data.name, price=data.price)
    index = _items.index(item)
    _items[index] = updated
    return updated

# Delete an item
@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    _items.remove(item)
    return item
