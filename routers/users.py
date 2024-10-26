from fastapi import APIRouter


router = APIRouter()


@router.get("/users/{id}", tags=["users"])
async def read_users(id: int):
    return [{"username": "Rick"}, {"username": "Morty"}, {"id" : id}]
