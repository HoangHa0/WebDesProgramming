import asyncio
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemPublic(BaseModel):
    id: int
    name: str
    price: float
    
class ItemUpdate(BaseModel):
    name: str | None
    price: float | None

class ItemListResponse(BaseModel):
    items: list[ItemPublic]
    total: int
    skip: int
    limit: int
    
class HousePriceRequest(BaseModel):
    area_sqm: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    distance_to_center_km: float

class HousePricePrediction(BaseModel):
    predicted_price: float
    currency: str = "VND"
    
app = FastAPI()
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

_items: list[ItemPublic] = []
_next_id: int = 1

def _find(item_id: int) -> ItemPublic | None:
    for item in _items:
        if item.id == item_id:
            return item
    return None

def _check_duplicate_name(name: str):
    for item in _items:
        if item.name.lower() == name.lower():
            raise HTTPException(
                status_code=409, detail="Item with this name already exists"
            )

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
    q: str | None = Query(None, min_length=2),
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = Query("id", pattern="^(id|name|price)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
):
    filtered = _items

    if q is not None:
        filtered = [i for i in filtered if q.lower() in i.name.lower()]
    if min_price is not None:
        filtered = [i for i in filtered if i.price >= min_price]
    if max_price is not None:
        filtered = [i for i in filtered if i.price <= max_price]

    filtered = sorted(
        filtered,
        key=lambda i: getattr(i, sort_by),
        reverse=(order == "desc"),
    )
    
    total = len(filtered)  # Part D: count after filtering, before slicing
    sliced = filtered[skip : skip + limit]

    return ItemListResponse(items=sliced, total=total, skip=skip, limit=limit)

# Create an item
@app.post("/items", response_model=ItemPublic, status_code=201)
def create_item(data: ItemCreate):
    global _next_id
    _check_duplicate_name(data.name)
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

@app.patch("/items/{item_id}", response_model=ItemPublic)
def patch_item(item_id: int, data: ItemUpdate):
    item = _find(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updates = data.model_dump(exclude_unset=True)
    
    # Part C: only check for name collisions if name is actually changing
    if "name" in updates and updates["name"].lower() != item.name.lower():
        _check_duplicate_name(updates["name"])
    
    updated = item.model_copy(update=updates)
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

# Lab bonus: House price prediction endpoint
@app.post("/predict/house-price", response_model=HousePricePrediction)
def predict_house_price(data: HousePriceRequest):
    price = (
        data.area_sqm * 15_000_000
        - data.distance_to_center_km * 5_000_000
        + data.bedrooms * 20_000_000
    )
    return HousePricePrediction(predicted_price=price, currency="VND")