from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the root endpoint!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

@app.post("/create-item/")
def create_item(name: str, description: str = None):
    return {"name": name, "description": description}

@app.put("/update-item/{item_id}")
def update_item(item_id: int, name: str, description: str = None):
    return {"item_id": item_id, "name": name, "description": description}

@app.delete("/delete-item/{item_id}")
def delete_item(item_id: int):
    return {"message": f"Item {item_id} has been deleted"}

@app.get("/users/")
def list_users():
    return {"users": ["Alice", "Bob", "Charlie"]}

@app.post("/users/")
def create_user(username: str):
    return {"message": f"User {username} has been created"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "username": f"User{user_id}"}

@app.put("/users/{user_id}")
def update_user(user_id: int, username: str):
    return {"user_id": user_id, "updated_username": username}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"message": f"User {user_id} has been deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)