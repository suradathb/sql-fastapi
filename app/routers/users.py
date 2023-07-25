from fastapi import APIRouter
from pydantic import BaseModel
# import mysql.connector

router = APIRouter(
    prefix='/database',
    tags=['Setup DB API'],
    responses={404:{
        'message':'Not found'
    }}
)

# mydb = mysql.connector.connect(
#   host="127.0.0.1",
#   user="root",
#   password="",
#   database="posdb"
# )
# @app.get("/users")
@router.get("/users")
def get_user():
    return {"Users": "Test User"}
