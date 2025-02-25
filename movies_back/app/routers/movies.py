from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, text
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models.movie import Movie
from ..schemas.movie import Movie as MovieSchema, MovieDetail
from sqlalchemy import or_

router = APIRouter()

@router.get("/hot", response_model=List[MovieSchema])
async def get_hot_movies(limit: Optional[int] = None, db: Session = Depends(get_db)):
    """获取热门电影（按年份排序）"""
    query = db.query(Movie).order_by(Movie.years.desc())
    if limit:
        query = query.limit(limit)
    return query.all()

@router.get("/rank", response_model=List[MovieSchema])
async def get_ranked_movies(limit: Optional[int] = None, db: Session = Depends(get_db)):
    """获取排行榜电影（按ID排序）"""
    query = db.query(Movie).order_by(Movie.id.asc())
    if limit:
        query = query.limit(limit)
    return query.all()

@router.get("/recommend", response_model=List[MovieSchema])
async def get_recommended_movies(limit: Optional[int] = None, db: Session = Depends(get_db)):
    """获取推荐电影（随机推荐）"""
    query = db.query(Movie).order_by(text('RAND()'))
    if limit:
        query = query.limit(limit)
    return query.all()

@router.get("/search", response_model=List[MovieSchema])
async def search_movies(
    keyword: str = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """根据电影名称搜索"""
    try:
        if not keyword:
            return []
            
        # 处理关键词
        keyword = keyword.strip()
        print(f"搜索关键词: {keyword}")  # 添加日志
            
        # 只搜索电影标题
        query = db.query(Movie).filter(
            Movie.title.like(f"%{keyword}%")
        ).order_by(desc(Movie.rating))  # 按评分排序
        
        movies = query.all()
        print(f"搜索到 {len(movies)} 条结果")  # 添加日志
            
        return movies
    except Exception as e:
        print(f"搜索电影失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="搜索失败，请重试"
        )

@router.get("/{movie_id}", response_model=MovieDetail)
async def get_movie_detail(movie_id: int, db: Session = Depends(get_db)):
    """获取电影详情，包含基本信息和详细信息"""
    try:
        # 联合查询两个表
        sql = """
            SELECT 
                m.id, m.douban_id, m.title, m.description, m.rating, 
                m.leader, m.tags, m.years, m.country, m.director_description, 
                m.cover_image, m.view_count,
                d.actors, d.plot, d.duration, 
                d.comment1, d.comment2, d.comment3, d.comment4, d.comment5
            FROM movies_top250 m
            LEFT JOIN movie_details d ON m.douban_id = d.douban_id
            WHERE m.id = :movie_id
        """
        
        result = db.execute(text(sql), {"movie_id": movie_id}).first()
        
        if result is None:
            raise HTTPException(status_code=404, detail="电影不存在")
        
        # 转换为字典，使用result._mapping来获取列名和值的映射
        movie_data = dict(result._mapping)
        
        # 更新浏览量
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if movie:
            movie.view_count += 1
            db.commit()
            # 更新返回数据中的浏览量
            movie_data['view_count'] = movie.view_count
        
        return movie_data
        
    except Exception as e:
        print(f"获取电影详情错误: {str(e)}")  # 添加错误日志
        raise HTTPException(status_code=500, detail=f"获取电影详情失败: {str(e)}") 