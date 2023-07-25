from typing import Union
from fastapi import FastAPI
from .routers import users

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

def config_router():
      app.include_router(users.router)

config_router()

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
