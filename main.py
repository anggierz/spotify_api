from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional #hacer campos opcionales en pydantic
import uvicorn
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

json_file_path = "users.json"

class MusicTaste(BaseModel):
    song_name: str
    artist: Optional[str] = None
    genre: Optional[str] = None
    

class User(BaseModel):
    name: str
    surname: str
    email: str
    age: int
    country: str
    music_taste: list[MusicTaste] | None = None
    
app = FastAPI()

@app.get("/api/users")
def get_users():  
    users = read_json(json_file_path) 
    return users


@app.post("/api/users")
def create_user(user: User):
    users = read_json(json_file_path)
    
    for existingUser in users:
        if (existingUser['email'] == user.email):
            raise HTTPException(status_code=400, detail="Email already exists")

    new_user = {
        "id": len(users)+1,
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "age": user.age,
        "country": user.country
    } 
    users.append(new_user)
    
    write_json(json_file_path, users)
      
    return {"response": "User successfully created!", "user": new_user}



@app.delete("/api/users/{id}")
def delete_user(id: int):
    users = read_json(json_file_path)
    
    print(users)
    
    for existingUser in users:
        if (existingUser['id'] == id):
            users.remove(existingUser)
        
    write_json(json_file_path, users)
    
    return {"response": f"User deletion completed successfully"}


def read_json(filepath: str):
    if not os.path.isfile(filepath):
        with open(filepath, "w") as f:
            json.dump([], f)
    with open(filepath, "r") as f:
        data = json.load(f)
    return data



def write_json(filepath: str, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    