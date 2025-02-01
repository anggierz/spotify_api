from fastapi import FastAPI, HTTPException, Path, Body
from pydantic import BaseModel
from typing import List, Dict
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


@app.get("/api/users", tags=["USER ENDPOINTS"], summary="Obtener toda la lista de usuarios",
         description="Este endpoint devuelve todos los usuarios de la base de datos JSON")
def get_users():
    users = read_json(json_file_path)
    return users


@app.get("/api/users/{id}", tags=["USER ENDPOINTS"], summary="Obtener un usuario mediante ID",
         description="Este endpoint devuelve un usuario por ID si este existe en base de datos")
def get_user_by_id(id: int = Path(..., description="El ID único del usuario que deseas obtener")):
    users = read_json(json_file_path)
    
    result = [ existingUser for existingUser in users if existingUser['id'] == id ]
    
    if result == []:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found in database")
    
    return result

@app.post("/api/users", tags=["USER ENDPOINTS"], summary="Crear un usuario",
         description="Este endpoint crea un usuario en la base de datos.")
def create_user(user: User = Body(..., description="El objeto User que contiene los detalles del nuevo usuario. Debe incluir 'name', 'lastname', 'email', 'age', 'country' y opcionalmente una lista 'favorite_genres'.")):
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


@app.delete("/api/users/{id}", tags=["USER ENDPOINTS"], summary="Eliminar un usuario",
         description="Este endpoint elimina un usuario por ID")
def delete_user(id: int = Path(..., description="El ID único del usuario que deseas eliminar")):
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

@app.post("/api/users/{id}", tags=["USER ENDPOINTS"], summary="Actualizar un usuario",
         description="Este endpoint actualiza un usuario por ID")
def update_user(id: int = Path(..., description="El ID único del usuario que deseas actualizar"),
                user: User = Body(..., description="El objeto User que contiene los detalles del usuario a actualizar")):
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

@app.get("/api/spotify/artist-top-tracks/{artist}", tags=["SPOTIFY ENDPOINTS"], summary="Obtener top tracks de un artista",
         description="Este endpoint devuelve los top tracks de un artista a partir del nombre del artista.")
def get_artist_top_tracks(artist: str = Path(..., description="Nombre del artista del cual quieres recuperar sus top tracks. Ejemplo: Taylor Swift")):
    response = search_artist_top_tracks(artist)
    
    return response

@app.get("/api/spotify/search/{item}/{type}", tags=["SPOTIFY ENDPOINTS"], summary="Hacer una búsqueda genérica de items en Spotify",
         description="Este endpoint devuelve resultados de Spotify a través de un item y un tipo de búsqueda.")
def search_item(item: str = Path(..., description="Query que quieres realizar"),
                type: str = Path(..., description="Tipo de búsqueda a realizar. Las opciones son: artist, track, album")):
    response = spotify_search_for_item(item, type)
    
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
def get_artist_id_by_name(artist: str, token: str):
    SPOTIFY_SEARCH = os.getenv("SPOTIFY_ENDPOINT_SEARCH")
  
    url = f"{SPOTIFY_SEARCH}?q={artist}&type=artist"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    req = requests.get(url, headers=headers)

    artist_id = req.json()['artists']['items'][0]['id']
    
    return artist_id


def search_artist_top_tracks(artist: str):
    SPOTIFY_ARTISTS_URL = os.getenv("SPOTIFY_ENDPOINT_ARTISTS")
    
    spotify_token = get_spotify_token()
    artist_id = get_artist_id_by_name(artist, spotify_token['access_token'])
    url = f"{SPOTIFY_ARTISTS_URL}/{artist_id}/top-tracks"
    
    headers = {
        "Authorization": f"Bearer {spotify_token['access_token']}"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from Spotify")
    
    # Limpiar la respuesta
    clean_response = clean_spotify_response(response.json(), "top-tracks")
    
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
    
    # Limpiar la respuesta
    clean_response = clean_spotify_response(response.json(), type)
    
    return clean_response




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
                "artist": track.get("artists", [{}])[0].get("name"), #Solo devolvemos primer artista
                "album": track.get("album", {}).get("name"),
                "track_number": track.get("track_number"),
                "release_date": track.get("album", {}).get("release_date"),
                "spotify_url": track.get("external_urls", {}).get("spotify")
            })
    
    elif type == "album":
        for album in data.get("albums", {}).get("items", []):
            clean_response.append({
                "name": album.get("name"),
                "artist": album.get("artists", [{}])[0].get("name"), #Solo devolvemos primer artista
                "release_date": album.get("release_date"),
                "spotify_url": album.get("external_urls", {}).get("spotify")
            })
    
    else:
        raise HTTPException(status_code=400, detail="Invalid type. Supported types: artist, track, album")
    
    return clean_response