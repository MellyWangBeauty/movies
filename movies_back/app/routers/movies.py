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

@router.get("/search", response_model=List[MovieSchema])
async def search_movies(
    keyword: str = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db)
):
    """根据关键词搜索电影"""
    try:
        if not keyword:
            print("关键词为空")
            return []
            
        # URL解码并处理关键词
        keyword = keyword.strip()
        print(f"搜索关键词: {keyword}")  # 添加日志
            
        # 将搜索关键词分词
        keywords = list(keyword)  # 将字符串拆分成单个字符
        print(f"分词结果: {keywords}")  # 添加日志
            
        # 构建查询条件
        conditions = []
        for kw in keywords:
            conditions.append(
                or_(
                    Movie.title.like(f"%{kw}%"),
                    Movie.director_description.like(f"%{kw}%"),
                    Movie.leader.like(f"%{kw}%"),
                    Movie.tags.like(f"%{kw}%"),
                    Movie.country.like(f"%{kw}%")
                )
            )
        
        # 使用 or_ 连接所有条件
        query = db.query(Movie).filter(or_(*conditions)).order_by(desc(Movie.rating))
        
        movies = query.all()
        print(f"搜索到 {len(movies)} 条结果")  # 添加日志
        
        # 打印第一条结果用于调试
        if movies:
            print(f"第一条结果: {movies[0].title}")
            
        return movies
    except Exception as e:
        print(f"搜索电影失败: {str(e)}")
        print(f"错误类型: {type(e)}")  # 添加错误类型信息
        raise HTTPException(
            status_code=500,
            detail={
                "message": "搜索电影失败",
                "error": str(e)
            }
        ) 