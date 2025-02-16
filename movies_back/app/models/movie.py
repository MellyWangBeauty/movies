from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func
from ..database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True)
    cover_image = Column(String(500))  # 封面图片URL
    description = Column(Text)
    release_date = Column(DateTime)
    rating = Column(Float, default=0.0)  # 评分
    view_count = Column(Integer, default=0)  # 浏览量
    category = Column(String(50))  # 分类
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 