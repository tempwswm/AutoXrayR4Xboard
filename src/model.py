from pydantic import BaseModel


class Node(BaseModel):
    id: int
    type: str
