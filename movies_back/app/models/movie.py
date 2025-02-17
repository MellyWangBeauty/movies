from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class Movie(Base):
    __tablename__ = "movies_top250"

    id = Column(Integer, primary_key=True, index=True)
    douban_id = Column(String(20), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    rating = Column(Float)
    leader = Column(String(100))
    tags = Column(String(255))
    years = Column(String(10))
    country = Column(String(100))
    director_description = Column(String(100))
    cover_image = Column(String(500))
    view_count = Column(Integer, default=0) 