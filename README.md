# APIs REST

## Descripción del proyecto

Este repositorio incluye la actividad 1: APIs REST del Módulo 2. Fundamentos de Backend con Python
del Máster de Desarrollo Web de la UEM.

Se implementa una API RESTful haciendo uso del framework **FastAPI** para gestionar usuarios. Adicionalmente,
se integra con la **API de Spotify** para obtener información musical.

## Funcionalidades

1. **Gestión de Usuarios**:
   - Crear, leer, actualizar y eliminar usuarios.
   - Los usuarios tienen los siguientes atributos definidos en el modelo de datos: nombre, apellido, correo electrónico, edad, país y géneros musicales favoritos.

2. **Integración con la API de Spotify**:
   - Buscar información de artistas, canciones y álbumes.
   - Obtener los "top tracks" de un artista.


## Endpoints disponibles

Podrás encontrar más información sobre los endpoints documentado en Swagger en la siguiente ruta: http://127.0.0.1:8000/docs#/


### **1. Gestión de Usuarios (USER ENDPOINTS)**

#### **GET /api/users**

#### **GET /api/users/{id}**

#### **POST /api/users**

#### **POST /api/users/{id}**

#### **DELETE /api/users/{id}**


### **2. Integración con Spotify (SPOTIFY ENDPOINTS)**

#### **GET /api/spotify/artist-top-tracks/{artist}**

#### **GET /api/spotify/search/{item}/{type}**

## Instrucciones de uso

### 1. Clonar el Repositorio

Primero, clona el repositorio del proyecto a tu máquina local

### 2. Instalar dependencias 

Instala las dependencias que se encuentran en el archivo requirements.txt

```bash
pip install -r requirements.txt
```

### 3. Levantar los endpoints

Finalmente, levanta las rutas para poder utilizarlas

```bash
uvicorn main:app --reload
```