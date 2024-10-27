from pydantic import BaseModel


class DialogQuery(BaseModel):
    prompt: str
