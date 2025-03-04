from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class MovieReview(Base):
    __tablename__ = "movie_reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies_top250.id"))
    rating = Column(Float, nullable=False)  # 评分 1-5
    content = Column(Text, nullable=True)   # 评论内容(可选)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 