import asyncio
import time
from fastapi import FastAPI, Query, HTTPException, Request, Header, APIRouter, Depends, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
# app.mount("/static", StaticFiles(directory="../frontend"), name="static")

_items: list[ItemPublic] = []
_next_id: int = 1

# Middlewares
_cart = []

@app.post("/cart/add")
def add_cart_item(item: str):
    _cart.append(item)
    return _cart

@app.get("/cart")
def get_cart():
    return _cart

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return response

@app.get("/boom")
def boom():
    return 1/0

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        print(f"Unhandled error with {request.url.path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

# @app.middleware("http")
# async def m1(request: Request, call_next):
#     print("m1 before")
#     response = await call_next(request)
#     print("m1 after")
#     return response

# @app.middleware("http")
# async def m2(request: Request, call_next):
#     print("m2 before")
#     response = await call_next(request)
#     print("m2 after")
#     return response

# Dependencies
def pagination(
    skip: int = Query(0, ge=0), 
    limit: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, min_length=2),
):
    return {"skip": skip, "limit": limit, "q": q}

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "secret-api-key":
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

def verify_session_cookie(session_id: str | None = Cookie(default=None)):
    if session_id != "abc123":
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session_id
    
@app.get("/secure-data", dependencies=[Depends(verify_api_key)])
def get_secure_data():
    return {"ok": True}

@app.post("/login")
def login(response: Response):
    response.set_cookie(key="session_id", value="abc123", httponly=True)
    return {"message": "Logged Success"}

# Admin router group
admin = APIRouter(prefix="/admin", dependencies=[Depends(verify_session_cookie)])


# Helper functions
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
# @app.get("/items")
# def list_items(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1, le=100),
#     q: str | None = Query(None, min_length=2),
#     min_price: float | None = None,
#     max_price: float | None = None,
#     sort_by: str = Query("id", pattern="^(id|name|price)$"),
#     order: str = Query("asc", pattern="^(asc|desc)$"),
# ):
#     filtered = _items

#     if q is not None:
#         filtered = [i for i in filtered if q.lower() in i.name.lower()]
#     if min_price is not None:
#         filtered = [i for i in filtered if i.price >= min_price]
#     if max_price is not None:
#         filtered = [i for i in filtered if i.price <= max_price]

#     filtered = sorted(
#         filtered,
#         key=lambda i: getattr(i, sort_by),
#         reverse=(order == "desc"),
#     )
    
#     total = len(filtered)  # Part D: count after filtering, before slicing
#     sliced = filtered[skip : skip + limit]
    
#     return ItemListResponse(items=sliced, total=total, skip=skip, limit=limit)

@admin.get("/items")
def list_items(page: dict = Depends(pagination)):
    print("--> getting items")
    skip = page["skip"]
    limit = page["limit"]
    return _items[skip : skip + limit]

app.include_router(admin) # You only need to include the router once after defining all its routes

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




