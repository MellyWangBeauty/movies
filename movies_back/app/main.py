from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import users, movies, reviews
from .database import engine
from .models import user, movie, review
from statistics.movie_analysis import get_analysis_data

# 创建数据库表 - 添加 checkfirst=True 参数
user.Base.metadata.create_all(bind=engine, checkfirst=True)
movie.Base.metadata.create_all(bind=engine, checkfirst=True)
review.MovieReview.__table__.create(bind=engine, checkfirst=True)

app = FastAPI(
    title="电影数据可视化分析平台",
    description="基于FastAPI的电影数据可视化分析平台后端API",
    version="1.0.0"
)

# 配置CORS
origins = [
    "http://localhost:5173",  # Vue开发服务器
    "http://localhost:8080",
    "http://localhost:3000",  # 添加新的前端开发服务器地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])

@app.get("/api/statistics")
async def get_statistics():
    """获取电影统计数据"""
    try:
        data = get_analysis_data()
        return data
    except Exception as e:
        print(f"获取统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 