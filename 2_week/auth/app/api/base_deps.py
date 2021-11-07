from app.database import Database
from starlette.requests import Request



def get_db_client(request: Request) -> Database:
    return request.app.state.db


