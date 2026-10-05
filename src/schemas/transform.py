from pydantic import BaseModel


class CreateTransformRequest(BaseModel):
    """POST /payload body: two equal-length string lists, per the task sample."""
    input_lst1: list[str]
    input_lst2: list[str]


class CreateTransformResponse(BaseModel):
    """POST reply: only the id, since the payload itself is fetched via GET."""

    created_id: int


class GetTransformResponse(BaseModel):
    """GET reply: the generated payload for the requested id."""
    output: str
