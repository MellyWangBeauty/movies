from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.review import MovieReview
from ..models.user import User
from ..models.movie import Movie
from ..schemas.review import ReviewCreate, ReviewResponse, ReviewList
from ..dependencies import get_current_user
from sqlalchemy import desc

router = APIRouter()

@router.post("/{movie_id}", response_model=ReviewResponse)
async def create_review(
    movie_id: int,
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查电影是否存在
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    # 检查用户是否已经评价过这部电影
    existing_review = db.query(MovieReview).filter(
        MovieReview.user_id == current_user.id,
        MovieReview.movie_id == movie_id
    ).first()
    
    if existing_review:
        # 更新已有评价
        existing_review.rating = review.rating
        existing_review.content = review.content
        db.commit()
        db.refresh(existing_review)
        return {
            **existing_review.__dict__,
            "username": current_user.username
        }
    
    # 创建新评价
    db_review = MovieReview(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=review.rating,
        content=review.content
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return {
        **db_review.__dict__,
        "username": current_user.username
    }

@router.get("/{movie_id}", response_model=ReviewResponse)
async def get_user_review(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查用户是否已登录
    if not current_user:
        return None  # 未登录返回空

    # 获取当前用户对该电影的评价
    review = db.query(MovieReview).filter(
        MovieReview.user_id == current_user.id,
        MovieReview.movie_id == movie_id
    ).first()
    
    if not review:
        return None  # 未找到评价返回空
    
    return {
        **review.__dict__,
        "username": current_user.username
    }

@router.delete("/{movie_id}", status_code=204)
async def delete_review(
    movie_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    review = db.query(MovieReview).filter(
        MovieReview.user_id == current_user.id,
        MovieReview.movie_id == movie_id
    ).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    
    db.delete(review)
    db.commit()

@router.post("/movies/{movie_id}/rate")
async def rate_movie(
    movie_id: int,
    rating: float,
    content: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 检查电影是否存在
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="电影不存在")
    
    # 检查评分范围
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="评分必须在1-5之间")
    
    # 检查是否已经评价过
    existing_review = db.query(MovieReview).filter(
        MovieReview.user_id == current_user.id,
        MovieReview.movie_id == movie_id
    ).first()
    
    if existing_review:
        # 更新已有评价
        existing_review.rating = rating
        existing_review.content = content
        db.commit()
        return {"message": "评价已更新"}
    
    # 创建新评价
    new_review = MovieReview(
        user_id=current_user.id,
        movie_id=movie_id,
        rating=rating,
        content=content
    )
    db.add(new_review)
    db.commit()
    return {"message": "评价成功"}

@router.get("/users/me/reviews")
async def get_user_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reviews = db.query(MovieReview, Movie)\
        .join(Movie, MovieReview.movie_id == Movie.id)\
        .filter(MovieReview.user_id == current_user.id)\
        .order_by(desc(MovieReview.created_at))\
        .all()
    
    return [
        {
            "id": review.id,
            "movie_id": review.movie_id,
            "movie_title": movie.title,
            "rating": review.rating,
            "content": review.content,
            "created_at": review.created_at,
            "tags": movie.tags,
            "year": movie.years,
            "country": movie.country
        }
        for review, movie in reviews
    ] 