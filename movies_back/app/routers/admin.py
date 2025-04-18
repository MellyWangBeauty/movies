from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from ..database import get_db
from ..models.user import User
from ..models.review import MovieReview
from ..models.movie import Movie
from ..schemas.user import User as UserSchema, UserCreate, UserUpdate
from ..utils.auth import get_password_hash
from ..dependencies import get_current_user

router = APIRouter()

# 验证是否管理员
def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有管理员权限"
        )
    return current_user

# 获取所有用户
@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    users = db.query(User).all()
    return users

# 编辑用户信息
@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新用户信息
    if user_update.username is not None:
        # 检查新用户名是否已存在
        db_user = db.query(User).filter(User.username == user_update.username).first()
        if db_user and db_user.id != user_id:
            raise HTTPException(
                status_code=400,
                detail="用户名已被使用"
            )
        user.username = user_update.username
    
    if user_update.email is not None:
        # 检查新邮箱是否已存在
        db_user = db.query(User).filter(User.email == user_update.email).first()
        if db_user and db_user.id != user_id:
            raise HTTPException(
                status_code=400,
                detail="邮箱已被使用"
            )
        user.email = user_update.email
    
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)
    
    if user_update.avatar is not None:
        user.avatar = user_update.avatar
    
    if user_update.bio is not None:
        user.bio = user_update.bio
    
    db.commit()
    db.refresh(user)
    return user

# 删除用户
@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # 禁止删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="管理员不能删除自己的账号")
    
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    try:
        # 先删除用户所有评论（解决外键约束问题）
        db.query(MovieReview).filter(MovieReview.user_id == user_id).delete()
        
        # 再删除用户
        db.delete(user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")

# 获取特定用户的评论
@router.get("/users/{user_id}/reviews")
async def get_user_reviews(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # 查找用户
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取评论
    reviews = db.query(MovieReview, Movie)\
        .join(Movie, MovieReview.movie_id == Movie.id)\
        .filter(MovieReview.user_id == user_id)\
        .order_by(desc(MovieReview.created_at))\
        .all()
    
    return [
        {
            "id": review.id,
            "movie_id": review.movie_id,
            "movie_title": movie.title,
            "rating": review.rating,
            "content": review.content,
            "created_at": review.created_at
        }
        for review, movie in reviews
    ]

# 删除特定评论
@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    # 查找评论
    review = db.query(MovieReview).filter(MovieReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 删除评论
    db.delete(review)
    db.commit() 