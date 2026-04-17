# use pydantic map data 
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class UserStatus (str, Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    deleted = "deleted"
    
    
    
class UserCreate(BaseModel):
    first_name : str = Field(min_length = 3, max_length = 100)
    last_name : str = Field(min_length = 3, max_length = 100)
    email : str = Field( emails = True , min_length = 5, )
    status : UserStatus = UserStatus.active
    
    
class UserUpdate(BaseModel):
    first_name : Optional[str] = Field(default = None, max_length = 100)
    last_name : Optional[str] = Field(default = None, max_length = 100)
    email : Optional[str] = Field( default=None, emails = True , min_length = 5, )
    status : Optional[UserStatus] = UserStatus.active
    
class UserOut(BaseModel):
    id: str
    first_name: str
    last_name : str
    email: str
    status: UserStatus