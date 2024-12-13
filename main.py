from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import requests
import json
import os
import base64
from dotenv import load_dotenv

load_dotenv()

json_file_path = "users.json"

class MusicTaste(BaseModel):
    artist: str
    top_songs: str | None = None
    

class User(BaseModel):
    name: str
    lastname: str
    email: str
    age: int
    country: str
    music_taste: list[MusicTaste] = []
    
app = FastAPI()

@app.get("/api/users")
def get_users():
    users = read_json(json_file_path)
    return users

@app.get("/api/users/{id}")
def get_user_by_id(id: int):
    users = read_json(json_file_path)
    
    result = [ existingUser for existingUser in users if existingUser['id'] == id ]
    
    if result == []:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found in database")
    
    return result

@app.post("/api/users")
def create_user(user: User):
    users = read_json(json_file_path)
    
    for existingUser in users:
        if (existingUser['email'] == user.email):
            raise HTTPException(status_code=404, detail="Email already exists")
        
    new_user = {
        "id": len(users)+1,
        "name": user.name,
        "lastname": user.lastname,
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
    
    idExistsInDatabase = False
    
    for existingUser in users:
        if (existingUser['id'] == id):
            idExistsInDatabase = True
            users.remove(existingUser)
        
    write_json(json_file_path, users)
    
    if idExistsInDatabase == False:
        raise HTTPException(status_code=404, detail=f"User with id {id} does not exist.")
    
    return {"response": f"User deletion completed successfully"}


@app.post("/api/users/{id}")
def update_user(id: int, user: User):
    users = read_json(json_file_path)
    
    idExistsInDatabase = False
    
    for existingUser in users:
        if (existingUser['email'] == user.email):
            raise HTTPException(status_code=404, detail="Email already exists")
        
        if (existingUser['id'] == id):
            idExistsInDatabase = True
            existingUser['name'] = user.name
            existingUser['lastname'] = user.lastname
            existingUser['email'] = user.email
            existingUser['age'] = user.age
            existingUser['country'] = user.country
        
    write_json(json_file_path, users)
    
    if idExistsInDatabase == False:
        raise HTTPException(status_code=404, detail=f"User with id {id} does not exist.")
    
    return {"response": f"User updated successfully", "user": user}


@app.get("/api/spotify/artist-top-tracks/{artist}")
def get_artist_top_tracks(artist: str):
    response = search_artist_top_tracks(artist)
    
    return response

@app.get("/api/spotify/search/{item}/{type}")
def search_item(item: str, type: str):
    response = spotify_search_for_item(item, type)
    return response

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
        
        
def get_spotify_token():
    CLIENT_ID = os.getenv("SPOTIFY_DEVELOPMENT_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIFY_DEVELOPMENT_CLIENT_SECRET")
    URL_TOKEN = os.getenv("SPOTIFY_TOKEN_URL")
    
    client_credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_credentials_base64 = base64.b64encode(client_credentials.encode())

    token_headers = {
        "Authorization": "Basic " + client_credentials_base64.decode(),
    }

    token_data = {
        "grant_type": "client_credentials",
    }

    req = requests.post(URL_TOKEN, data=token_data, headers=token_headers)
    
    token = req.json()
    
    return token
    
  
def get_artist_id_by_name(artist: str):
    SPOTIFY_SEARCH = os.getenv("SPOTIFY_ENDPOINT_SEARCH")
    
    spotify_token = get_spotify_token()

    
    url = f"{SPOTIFY_SEARCH}?q={artist}&type=artist"
    
    headers = {
        "Authorization": f"Bearer {spotify_token['access_token']}"
    }
    
    req = requests.get(url, headers=headers)

    artist_id = req.json()['artists']['items'][0]['id']
    
    return artist_id


def search_artist_top_tracks(artist: str):
    SPOTIFY_ARTISTS_URL = os.getenv("SPOTIFY_ENDPOINT_ARTISTS")
    
    artist_id = get_artist_id_by_name(artist)
    spotify_token = get_spotify_token()
    url = f"{SPOTIFY_ARTISTS_URL}/{artist_id}/top-tracks"
    
    headers = {
        "Authorization": f"Bearer {spotify_token['access_token']}"
    }
    
    req = requests.get(url, headers=headers)
    
    return req.json()

def spotify_search_for_item(item: str, type: str):
    SPOTIFY_SEARCH_URL = os.getenv("SPOTIFY_ENDPOINT_SEARCH")
    spotify_token = get_spotify_token()
    
    url = f"{SPOTIFY_SEARCH_URL}?q={item}&type={type}"
    
    headers = {
        "Authorization": f"Bearer {spotify_token['access_token']}"
    }
    
    req = requests.get(url, headers=headers)
    
    return req.json()