#uvicorn main:app --reload

import os
from typing import Optional, List

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field
from pydantic.functional_validators import BeforeValidator

from typing_extensions import Annotated

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from routers import users

app = FastAPI()

app.include_router(users.router)

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
PyObjectId = Annotated[str, BeforeValidator(str)]

db = client.get_database("main")
user_collection = db.get_collection("users")


class UserModel(BaseModel):
    """
    Container for a single user record.
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    age: int = Field(...)
    weight: float = Field(...)
    dream_weight: float = Field(...)
    problems: str = Field(...)
    reccomendations: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": 27,
                "weight" : 100.0,
                "dream_weight" : 80.0,
                "problems": "obese, high blood pressure",
                "reccomendations": "eat less, exercise more",
            }
        },
    )

class UpdateUserModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    dream_weight: Optional[float] = None
    problems: Optional[str] = None
    reccomendations: Optional[str] = None
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": 27,
                "weight" : 100.0,
                "dream_weight" : 80.0,
                "problems": "obese, high blood pressure",
                "reccomendations": "eat less, exercise more",
            }
        },
    )

class UsersCollection(BaseModel):
    """
    A container holding a list of `UserModel` instances.

    This exists because providing a top-level array in a JSON response can be a [vulnerability](https://haacked.com/archive/2009/06/25/json-hijacking.aspx/)
    """

    users: List[UserModel]

@app.post(
    "/users/",
    response_description="Add new user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: UserModel = Body(...)):
    """
    Insert a new user record.

    A unique `id` will be created and provided in the response.
    """
    new_user = await user_collection.insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await user_collection.find_one(
        {"_id": new_user.inserted_id}
    )
    return created_user


@app.get(
    "/users/",
    response_description="List all users",
    response_model=UsersCollection,
    response_model_by_alias=False,
)
async def list_users():
    """
    List all of the users data in the database.

    The response is unpaginated and limited to 1000 results.
    """
    return UsersCollection(users=await user_collection.find().to_list(1000))


@app.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=UserModel,
    response_model_by_alias=False,
)
async def update_user(id: str, user: UpdateUserModel = Body(...)):
    """
    Update individual fields of an existing user record.

    Only the provided fields will be updated.
    Any missing or `null` fields will be ignored.
    """
    user = {
        k: v for k, v in user.model_dump(by_alias=True).items() if v is not None
    }

    if len(user) >= 1:
        update_result = await user_collection.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": user},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"user {id} not found")

    # The update is empty, but we should still return the matching document:
    if (existing_user := await user_collection.find_one({"_id": id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"user {id} not found")


@app.delete("/users/{id}", response_description="Delete a user")
async def delete_user(id: str):
    """
    Remove a single user record from the database.
    """
    delete_result = await user_collection.delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"user {id} not found")


@app.get("/")
def read_root():
    return {"todo": "main page"}