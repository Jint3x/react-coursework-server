import random
import string
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv() 
uri = f"mongodb+srv://{os.environ.get("dbUser")}:{os.environ.get("dbPassword")}@cluster0.euwe3xr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))
app_col = client.get_database("app").get_collection("app")

class UserCredentials(BaseModel):
    username: str
    password: str

app = FastAPI()

origins = [
    "http://localhost",         # For local development if your frontend runs on plain HTTP
    "http://localhost:3000",    # Example: If your frontend (React, Vue, Angular) runs on port 3000
    "http://localhost:9000",    # Example: Another common frontend development port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests.
    allow_credentials=True, # Support cookies and authorization headers.
    allow_methods=["*"],    # Allow all standard methods (GET, POST, PUT, DELETE, etc.).
                            # Or be specific: ["GET", "POST"]
    allow_headers=["*"],    # Allow all headers. Or be specific: ["Content-Type", "Authorization"]
)

@app.post("/api/register")
async def register_user(credentials: UserCredentials):
    if (app_col.find_one({"username": credentials.username}) is None):
        session = generate_random_string()
        app_col.insert_one({"username": credentials.username, "password": credentials.password, "session": session})
        return {"data": { "account": session }, "code": 0}
    else:
        return {"code": 1, "data": {"reason": "Account already exists"}}

@app.post("/api/login")
async def login_user(credentials: UserCredentials):
    user = app_col.find_one({"username": credentials.username})

    if user is None:
        return { "code": 1, "data": {"reason": "Account does not exist"}}
    elif user.get("password") != credentials.password:
        return { "code": 2, "data": {"reason": "Wrong password"}}
    else: 
        print(user)
        cookie = generate_random_string()
        app_col.update_one({"username": credentials.username}, {"$set": {"session": cookie}})
        print(f"User {credentials.username} was given the cookie {cookie}")
        return {"data": { "account": cookie }, "code": 0}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


def generate_random_string(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string