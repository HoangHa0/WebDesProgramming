from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


app = FastAPI()


# Task 1
def predict_price(area: float, bedrooms: int, location: str) -> float:
    base_price = 500_000_000
    area_price = 15_000_000 * area
    bedroom_price = 50_000_000 * bedrooms
    total_price = base_price + area_price + bedroom_price
    
    if location.lower() == "hanoi":
        location_multiplier = 1.3
    elif location.lower() == "hcmc":
        location_multiplier = 1.25
    else:
        location_multiplier = 1.0
    
    total_price *= location_multiplier
    return round(total_price, -6)


# Task 2
@app.get("/predict")
def predict(area: float, bedrooms: int, location: str = "other"):
    price = predict_price(area, bedrooms, location)
    return {"area": area, "bedrooms": bedrooms, "location": location, "predicted_price": price}


# Task 3: See image[number]_task03.png for the API documentation screenshots.

"""
Q: Returned JSON for area=80, bedrooms=3, location=hanoi: [image01_task03.png]
A: `{"area":80.0,"bedrooms":3,"location":"hanoi","predicted_price":2405000000.0}`
  
Q: Why does calling `/predict` without a location work? [image02_task03.png] 
A: It works because the `location` parameter in the endpoint definition is given a default value (`location: str = "other"`). 
FastAPI automatically treats parameters with default values as optional.
  
Q: Why does calling `/predict` without an area return a 422 error? [image03_task03.png] 
A: It returns a 422 Unprocessable Entity error because `area` does not have a default value in the function parameters (`area: float`). 
FastAPI flags it as a required parameter and automatically blocks the request if it is missing, citing a validation error.
"""


# Task 4
app.mount("/static", StaticFiles(directory="../frontend"), name="static")


# Task 5: See frontend/house_form.html 
"""
Q: Why does a relative URL (`fetch('/predict?...')`) work here?
A: Because the HTML file is mounted and served by the exact same FastAPI server (`127.0.0.1:8000`) that hosts the API. 
The browser resolves the relative path against the current origin, meaning it automatically directs the fetch request to 
`http://127.0.0.1:8000/predict`. This inherently avoids CORS issues.
"""


# Task 6
class HouseInput(BaseModel):
    area: float
    bedrooms: int
    location: str = "other"

@app.post("/predict")
def predict_post(house: HouseInput):
    predicted = predict_price(house.area, house.bedrooms, house.location)
    return {
        "area": house.area,
        "bedrooms": house.bedrooms,
        "location": house.location,
        "predicted_price": predicted
    }

"""
Q: Difference between Query Parameters and JSON Body:?
A: Query parameters are appended directly to the end of the URL (e.g., `?area=80`), which makes them visible in the browser
history and limits how much data you can send. A JSON request body packages the data inside the HTTP request payload itself, 
which allows for sending complex, nested data structures and larger amounts of data without cluttering the URL.
"""


