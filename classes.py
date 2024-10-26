from typing import Union
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: str
    is_offer: Union[bool, None] = None


class User(BaseModel):
    name: str
    age: int
    weight: int
    goal: Union[int, None] = None
