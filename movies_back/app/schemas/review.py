from pydantic import BaseModel, confloat
from typing import Optional, List
from datetime import datetime

class ReviewBase(BaseModel):
    rating: confloat(ge=1, le=5)  # 限制评分在1-5之间
    content: Optional[str] = None

class ReviewCreate(ReviewBase):
    pass

class ReviewInDB(ReviewBase):
    id: int
    user_id: int
    movie_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewResponse(ReviewInDB):
    username: str  # 添加用户名字段用于显示

class ReviewList(BaseModel):
    results: List[ReviewResponse]
    total: int 