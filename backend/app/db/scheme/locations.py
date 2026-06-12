from pydantic import BaseModel, Field


class LocationBase(BaseModel):
    location_name:str
    zone:str

class LocationCreate(BaseModel):
    location_name:str
    zone:str=Field(min_length=1, max_length=2)

class LocationUpdate(BaseModel):
    location_name:str | None=None
    zone:str | None=Field(default=None, max_length=2)

class LocationInDB(LocationBase):
    location_id:int
    
    class Config:
        from_attributes = True

class LocationRead(LocationInDB):
    pass
