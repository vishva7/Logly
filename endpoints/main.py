from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel, Field
import random
import time
from log_middleware import LogMiddleware


class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemUpdate(BaseModel):
    name: str
    description: str | None = None


class UserCreate(BaseModel):
    username: str


class UserUpdate(BaseModel):
    username: str


app = FastAPI()

app.add_middleware(
    LogMiddleware,
    kafka_bootstrap_servers="kafka:9092",
    request_topic="request-logs",
    response_topic="response-logs",
    error_topic="error-logs",
)


@app.get("/")
def read_root():
    time.sleep(random.uniform(0.01, 0.1))
    return {"message": "Welcome to the root endpoint!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    time.sleep(random.uniform(0.05, 0.2))

    if random.random() < 0.05:
        raise HTTPException(status_code=404, detail="Item not found")

    return {"item_id": item_id, "query": q}


@app.post("/create-item/")
def create_item(item: ItemCreate = Body(...)):
    time.sleep(random.uniform(0.1, 0.3))
    return {"name": item.name, "description": item.description}


@app.put("/update-item/{item_id}")
def update_item(item_id: int, item: ItemUpdate = Body(...)):
    time.sleep(random.uniform(0.1, 0.3))

    if random.random() < 0.03:
        raise HTTPException(status_code=400, detail="Invalid item data")

    return {"item_id": item_id, "name": item.name, "description": item.description}


@app.delete("/delete-item/{item_id}")
def delete_item(item_id: int):
    time.sleep(random.uniform(0.05, 0.15))
    return {"message": f"Item {item_id} has been deleted"}


@app.get("/users/")
def list_users():
    time.sleep(random.uniform(0.1, 0.2))
    return {"users": ["Alice", "Bob", "Charlie"]}


@app.post("/users/")
def create_user(user: UserCreate = Body(...)):
    time.sleep(random.uniform(0.1, 0.25))

    if random.random() < 0.02:
        raise HTTPException(status_code=409, detail="Username already exists")

    return {"message": f"User {user.username} has been created"}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    time.sleep(random.uniform(0.05, 0.15))

    if random.random() < 0.04:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user_id": user_id, "username": f"User{user_id}"}


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate = Body(...)):
    time.sleep(random.uniform(0.1, 0.3))
    return {"user_id": user_id, "updated_username": user.username}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    time.sleep(random.uniform(0.05, 0.15))
    return {"message": f"User {user_id} has been deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)