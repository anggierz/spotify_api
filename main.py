from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import json

class User(BaseModel):
    name: str
    email: str
    
    
class Users(BaseModel):
    count: int
    users: User

app = FastAPI()

@app.get("/api/users")
def get_users():
    try:
        with open('users.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    
    return data

@app.post("/api/users")
def create_user(user: User):
    try:
        with open('users.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    
    if any(u["email"] == user.email for u in data):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = {
        "name": user.name,
        "email": user.email
    }
    
    with open('users.json', 'w') as file:
        json.dump(new_user, file, indent=4)
        
    return new_user
    