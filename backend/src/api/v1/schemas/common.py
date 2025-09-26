from pydantic import BaseModel


class MessageResponseSchema(BaseModel):
    message: str
