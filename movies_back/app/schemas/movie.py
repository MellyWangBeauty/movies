from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MovieBase(BaseModel):
    title: str
    cover_image: str
    description: str
    release_date: datetime
    category: str

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[datetime] = None
    category: Optional[str] = None

class Movie(MovieBase):
    id: int
    rating: float
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 