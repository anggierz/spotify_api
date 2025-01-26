from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import requests
import json
import os
import base64
from dotenv import load_dotenv

load_dotenv()

json_file_path = "users.json"

class User(BaseModel):
    name: str
    lastname: str
    email: str
    age: int
    country: str
    favorite_genres: List[str] = []
    
app = FastAPI()

#OK recuperar usuarios de JSON
@app.get("/api/users")
def get_users():
    users = read_json(json_file_path)
    return users

#OK user que no existe.
#OK user que existe.
@app.get("/api/users/{id}")
def get_user_by_id(id: int):
    users = read_json(json_file_path)
    
    result = [ existingUser for existingUser in users if existingUser['id'] == id ]
    
    if result == []:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found in database")
    
    return result

#OK intentar crear un user con mismo email
#OK crear user con lista favorite_genres
#OK crear user sin lista favorite_genres
@app.post("/api/users")
def create_user(user: User):
    users = read_json(json_file_path)
    
    for existingUser in users:
        if (existingUser['email'] == user.email):
            raise HTTPException(status_code=400, detail="Email already exists")
        
    new_user = {
        "id": len(users)+1,
        "name": user.name,
        "lastname": user.lastname,
        "email": user.email,
        "age": user.age,
        "country": user.country,
        "favorite_genres": user.favorite_genres
    }
    
    users.append(new_user)
    
    write_json(json_file_path, users)

    return {"response": "User successfully created!", "user": new_user}


#OK intento eliminar usuario que no existe
#OK eliminar usuario que existe
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

#OK  intentar actualizar usuario que no existe
@app.post("/api/users/{id}")
def update_user(id: int, user: User):
    users = read_json(json_file_path)
    
    # Verificar si el usuario con el ID proporcionado existe
    user_to_update = None
    for existing_user in users:
        if existing_user["id"] == id:
            user_to_update = existing_user
            break
    
    if not user_to_update:
        raise HTTPException(status_code=404, detail=f"User with id {id} does not exist.")
    
    
    # Verificar si el nuevo email ya está en uso por otro usuario
    for existing_user in users:
        if existing_user["email"] == user.email and existing_user["id"] != id:
            raise HTTPException(status_code=400, detail="Email already exists.")
        
        
    # Actualizar los datos del usuario
    user_to_update["name"] = user.name
    user_to_update["lastname"] = user.lastname
    user_to_update["email"] = user.email
    user_to_update["age"] = user.age
    user_to_update["country"] = user.country
    user_to_update["favorite_genres"] = user.favorite_genres
        
    write_json(json_file_path, users)
    
    return {"response": f"User updated successfully", "user": user}


# PARTE DE LA ACTIVIDAD RELACIONADA CON SPOTIFY

@app.get("/api/spotify/artist-top-tracks/{artist}")
def get_artist_top_tracks(artist: str):
    response = search_artist_top_tracks(artist)
    
    return response

@app.get("/api/spotify/search/{item}/{type}")
def search_item(item: str, type: str):
    response = spotify_search_for_item(item, type)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Spotify")
    
    return response


# JSON HELPER FUNCTIONS

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
        

# SPOTIFY HELPER FUNCTIONS
       
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
    
#Recupera el id de spotify de un artista y devuelve el primer resultado
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
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Spotify")
    
    tracks = response.json().get("tracks", [])
    
    # Limpiar la respuesta
    clean_response = clean_spotify_response(response.json(), "top-tracks")
    # for track in tracks:
    #     element = {
    #         "name": track.get("name"),
    #         "album": track.get("album", {}).get("name"),
    #         "track_number": track.get("track_number"),
    #         "release_date": track.get("album", {}).get("release_date"),
    #         "spotify_url": track.get("external_urls", {}).get("spotify")
    #     }
    #     clean_response.append(element)
    
    return clean_response

def spotify_search_for_item(item: str, type: str):
    SPOTIFY_SEARCH_URL = os.getenv("SPOTIFY_ENDPOINT_SEARCH")
    spotify_token = get_spotify_token()
    
    url = f"{SPOTIFY_SEARCH_URL}?q={item}&type={type}"
    
    headers = {
        "Authorization": f"Bearer {spotify_token['access_token']}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Spotify")
    
    return response.json()




# Función para limpiar la respuesta de Spotify según el tipo
def clean_spotify_response(data: Dict, type: str):
    clean_response = []
    
    if type == "artist":
        for artist in data.get("artists", {}).get("items", []):
            clean_response.append({
                "name": artist.get("name"),
                "id": artist.get("id"),
                "spotify_url": artist.get("external_urls", {}).get("spotify")
            })
            
    elif type == "top-tracks":
        for track in data.get("tracks", []):
            clean_response.append({
                "name": track.get("name"),
                "album": track.get("album", {}).get("name"),
                "track_number": track.get("track_number"),
                "release_date": track.get("album", {}).get("release_date"),
                "spotify_url": track.get("external_urls", {}).get("spotify")
            })
    
    elif type == "track":
        for track in data.get("tracks", {}).get("items", []):
            clean_response.append({
                "name": track.get("name"),
                "album": track.get("album", {}).get("name"),
                "track_number": track.get("track_number"),
                "release_date": track.get("album", {}).get("release_date"),
                "spotify_url": track.get("external_urls", {}).get("spotify")
            })
    
    elif type == "album":
        for album in data.get("albums", {}).get("items", []):
            clean_response.append({
                "name": album.get("name"),
                "release_date": album.get("release_date"),
                "spotify_url": album.get("external_urls", {}).get("spotify")
            })
    
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Supported types: artist, track, album")
    
    return clean_response