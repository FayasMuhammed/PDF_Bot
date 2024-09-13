from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List



class UserCreate(BaseModel):
    name: str
    mail: str
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    mail: str
    password:str
    created_date:datetime
    updated_date:datetime
    is_active:bool

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    name:Optional[str]=None
    mail:Optional[str]=None
    password:Optional[str]=None

    class Config:
        orm_mode=True


class UserLogin(BaseModel):
    username:str
    password:str

class UserOut(BaseModel):
    id:int
    name:str
    mail:str
    is_active:bool

    class Config:
        orm_mode = True



class QuestionRequest(BaseModel):
    question: str
    user_id: int



class SearchResponse(BaseModel):
    results: list



class SearchResult(BaseModel):
    id: int
    score: float
    payload: dict
    vector: Optional[List[float]]
    shard_key: Optional[str]

