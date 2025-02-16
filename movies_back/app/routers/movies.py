from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
from typing import List
from datetime import datetime, timedelta
from ..database import get_db
from ..models.movie import Movie
from ..schemas.movie import Movie as MovieSchema

router = APIRouter()

@router.get("/hot", response_model=List[MovieSchema])
async def get_hot_movies(limit: int = 6, db: Session = Depends(get_db)):
    """获取热门电影（近五年内发布的，按ID排序）"""
    # 计算5年前的日期
    five_years_ago = datetime.now() - timedelta(days=5*365)
    
    movies = db.query(Movie).filter(
        Movie.release_date >= five_years_ago
    ).order_by(
        desc(Movie.id)
    ).limit(limit).all()
    
    if not movies:  # 如果没有数据，返回随机电影
        movies = db.query(Movie).order_by(text('RAND()')).limit(limit).all()
    return movies

@router.get("/rank", response_model=List[MovieSchema])
async def get_ranked_movies(limit: int = 6, db: Session = Depends(get_db)):
    """获取排行榜电影（按ID正序排序）"""
    movies = db.query(Movie).order_by(
        Movie.id
    ).limit(limit).all()
    
    if not movies:  # 如果没有数据，返回随机电影
        movies = db.query(Movie).order_by(text('RAND()')).limit(limit).all()
    return movies

@router.get("/recommend", response_model=List[MovieSchema])
async def get_recommended_movies(limit: int = 6, db: Session = Depends(get_db)):
    """获取推荐电影（随机推荐）"""
    movies = db.query(Movie).order_by(text('RAND()')).limit(limit).all()
    return movies

@router.get("/{movie_id}", response_model=MovieSchema)
async def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """获取电影详情"""
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    # 增加浏览量
    movie.view_count += 1
    db.commit()
    
    return movie 