import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
import pymysql
import time
from datetime import datetime

# MySQL 配置
db_config = {
    'host': 'localhost',  # 数据库主机
    'user': 'root',       # 数据库用户名
    'password': 'qaz741',  # 数据库密码
    'database': 'movies_db',  # 你要操作的数据库
    'charset': 'utf8mb4'   # 数据库字符集，避免中文乱码
}

base_url = 'https://movie.douban.com/top250'

# 定义 Movie 类来存储电影信息
class Movie:
    def __init__(self, title, cover_image, description, rating, release_date, category):
        self.title = title
        self.cover_image = cover_image
        self.description = description
        self.rating = float(rating)
        self.release_date = release_date
        self.category = category
        self.view_count = 0

# 异步请求获取网页内容
async def fetch(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"Status: {response.status} - URL: {url}")
            assert response.status == 200
            return await response.text()

# 解析页面内容
async def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    movies_info = soup.find('ol', {'class': 'grid_view'})
    movies = []
    
    for movie_info in movies_info.find_all('li'):
        # 获取基本信息
        pic = movie_info.find('div', {'class': 'pic'})
        cover_image = pic.find('img').attrs['src']
        info = movie_info.find('div', {"class": "info"})
        title = info.find('span', {'class': 'title'}).text

        # 获取详细信息
        movie_detail = info.find('div', {'class': 'bd'})
        description = info.find('p', {'class': 'quote'})
        description = description.find('span').text if description else ''
        rating = info.find('div', {"class": 'star'}).find('span', {'class': 'rating_num'}).text

        # 获取年份和类型
        detail_text = movie_detail.find('p').text.strip()
        year_str = detail_text.split('\n')[1].strip().split('/')[0].strip()
        try:
            release_date = datetime.strptime(year_str, '%Y')
        except ValueError:
            release_date = datetime.now()

        # 获取类型
        genres = detail_text.split('\n')[1].strip().split('/')[-1].strip()
        category = genres.split(' ')[0] if genres else '其他'

        movies.append(Movie(
            title=title,
            cover_image=cover_image,
            description=description,
            rating=rating,
            release_date=release_date,
            category=category
        ))
    
    # 获取下一页链接
    next_page = soup.find('link', {'rel': 'next'})
    next_link = base_url + next_page.attrs['href'] if next_page else None
    return movies, next_link

# 插入电影数据到 MySQL
def insert_movie(movie):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO movies (title, cover_image, description, rating, release_date, category, view_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                movie.title,
                movie.cover_image,
                movie.description,
                movie.rating,
                movie.release_date,
                movie.category,
                movie.view_count
            ))
            connection.commit()
    except Exception as e:
        print(f"Error inserting movie {movie.title}: {str(e)}")
    finally:
        connection.close()

# 爬取电影信息并保存到数据库
async def get_results(url):
    html = await fetch(url)
    movies, next_link = await parse(html)
    for movie in movies:
        insert_movie(movie)
        print(f"Inserted: {movie.title}")
        # 添加延时避免请求过快
        await asyncio.sleep(1)
    return next_link

# 处理任务的异步函数
async def handle_tasks(work_queue):
    while not work_queue.empty():
        current_url = await work_queue.get()
        try:
            next_link = await get_results(current_url)
            if next_link:
                work_queue.put_nowait(next_link)
                # 添加延时避免请求过快
                await asyncio.sleep(2)
        except Exception as e:
            logging.exception('Error for {}'.format(current_url), exc_info=True)

# 创建数据库表
def create_table():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                CREATE TABLE IF NOT EXISTS movies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    cover_image VARCHAR(500),
                    description TEXT,
                    release_date DATETIME,
                    rating FLOAT DEFAULT 0.0,
                    view_count INT DEFAULT 0,
                    category VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """
            cursor.execute(sql)
            connection.commit()
    finally:
        connection.close()

# 主函数
def main():
    # 创建数据库表
    create_table()
    
    # 运行爬虫
    q = asyncio.Queue()
    q.put_nowait(base_url)
    loop = asyncio.get_event_loop()
    tasks = [handle_tasks(q)]
    loop.run_until_complete(asyncio.wait(tasks))

if __name__ == "__main__":
    main()
