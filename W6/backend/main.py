import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, Web!"}

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Hello, {name}!"}
# http://localhost:8000/hello/John

@app.get("/add")
async def add(a: int, b: int):
    await asyncio.sleep(3)
    return {"a": a, "b": b, "sum": a + b}
# http://localhost:8000/add?a=3&b=5
