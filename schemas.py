from pydantic import BaseModel, field_validator, EmailStr, Field
from typing import List

class DepartmentCreate(BaseModel):
    name    : str

    @field_validator('name')
    def name_not_empty(cls,v):
        if not v.strip():
            raise ValueError('value cannot be empty')
        
        return v.lower()
    
class DepartmentResponse(BaseModel):
    id  : int
    name  : str

    class Config:
        from_attributes=True


class GradeCreate(BaseModel):
    subject     : str
    score       : float

    @field_validator('score')
    def score_not_empty(cls,v):
        if not 0 <= v <=100:
            raise ValueError('value must be between 0 to 100')
        return v
    
    
class GradeResponse(BaseModel):
    id      : int
    subject : str
    score   :  float


    class Config:
        from_attributes=True


#student
class StudentCreate(BaseModel):
    name        : str
    age         : int
    email       : EmailStr
    department_id : int

    @field_validator('age')
    def age_valid(cls,v):
        if not 5 <= v <=100:
            raise ValueError('age must be between 5 to 100')
        return v
    
    @field_validator('email')
    def email_valid(cls,v):
        if '@' not in v:
            raise ValueError('invaild email')
        return v
    

class StudentResponse(BaseModel):
    id          : int
    name        : str
    email       : str
    age         : int
    department_id: int
    grades      : List[GradeResponse] =Field(default_factory=list)

    class Config:
        from_attributes=True

