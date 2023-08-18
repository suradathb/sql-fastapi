from typing import Union
from fastapi import FastAPI
# from app.routers import users,socket
from routers import users,socket,permissiondata

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

def config_router():
      app.include_router(users.router)
      app.include_router(socket.router)
      app.include_router(permissiondata.router)
config_router()

