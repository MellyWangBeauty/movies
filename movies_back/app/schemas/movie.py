from pydantic import BaseModel
from typing import Optional, List

class MovieBase(BaseModel):
    title: str
    cover_image: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    leader: Optional[str] = None
    tags: Optional[str] = None
    years: Optional[str] = None
    country: Optional[str] = None
    director_description: Optional[str] = None
    douban_id: Optional[str] = None

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    id: int
    view_count: int = 0

    class Config:
        from_attributes = True

class MovieDetail(Movie):
    actors: Optional[str] = None
    plot: Optional[str] = None
    duration: Optional[str] = None
    comment1: Optional[str] = None
    comment2: Optional[str] = None
    comment3: Optional[str] = None
    comment4: Optional[str] = None
    comment5: Optional[str] = None

    class Config:
        from_attributes = True

# 用于更新的Schema
class MovieUpdate(BaseModel):
    title: Optional[str] = None
    cover_image: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    leader: Optional[str] = None
    tags: Optional[str] = None
    years: Optional[str] = None
    country: Optional[str] = None
    director_description: Optional[str] = None
    douban_id: Optional[str] = None 