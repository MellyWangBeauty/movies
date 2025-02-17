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
    def __init__(self, id, title, description, rating, leader, tags, years, country, director_description, cover_image, douban_id):
        self.id = id
        self.rating = rating
        self.description = description
        self.title = title
        self.leader = leader
        self.tags = tags
        self.years = years
        self.country = country
        self.director_description = director_description
        self.cover_image = cover_image
        self.view_count = 0
        self.douban_id = douban_id

# 创建数据库表
def create_table():
    # 创建数据库连接
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # SQL 语句创建电影信息表
            sql = """
                CREATE TABLE IF NOT EXISTS movies_top250 (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    douban_id VARCHAR(20) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    rating FLOAT,
                    leader VARCHAR(100),
                    tags VARCHAR(255),
                    years VARCHAR(10),
                    country VARCHAR(100),
                    director_description VARCHAR(100),
                    cover_image VARCHAR(500),
                    view_count INT DEFAULT 0,
                    INDEX idx_douban_id (douban_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            cursor.execute(sql)
            connection.commit()
            print("数据库表创建成功")
    except Exception as e:
        logging.error(f"Error creating table: {str(e)}")
        connection.rollback()
    finally:
        connection.close()

# 异步请求获取网页内容
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(response.status)  # 打印响应状态
            assert response.status == 200  # 确保请求成功
            return await response.text()  # 返回网页内容

# 解析页面内容
async def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    movies_info = soup.find('ol', {'class': 'grid_view'})
    movies = []

    for movie_info in movies_info.find_all('li'):
        pic = movie_info.find('div', {'class': 'pic'})
        picture_url = pic.find('img').attrs['src']
        movie_id = pic.find('em').text
        # 获取豆瓣ID
        movie_link = pic.find('a')['href']
        douban_id = movie_link.split('/')[-2]
        
        url = movie_info.find('div', {"class": "info"})
        title = url.find('span', {'class': 'title'}).text

        # 提取电影的其他信息
        info = url.find('div', {'class': 'bd'})
        movie_detail = info.find('p')
        quote = info.find('p', {'class': 'quote'})
        description = quote.find('span').text if quote else ''
        rating = info.find('div', {"class": 'star'}).find('span', {'class': 'rating_num'}).text
        tags = movie_detail.text.strip().split('\n')[-1].split('/')[-1].split(' ')
        tags = [tag.strip() for tag in tags]
        years = movie_detail.text.strip().split('\n')[-1].split('/')[0].strip()
        country = movie_detail.text.strip().split('\n')[-1].split('/')[1].strip()
        
        # 提取导演和主演信息
        director_description = ''
        leader = ''
        detail_text = movie_detail.text.strip()  # 获取详细信息文本

        # 提取导演信息
        if "导演:" in detail_text:
            director_info = detail_text.split("导演:")[1].split("主演:")[0].strip()  # 获取导演信息
            director_description = director_info.split(' ')[0]  # 取导演的中文名字部分

        # 提取主演信息
        if "主演:" in detail_text:
            leader_info = detail_text.split("主演:")[1].strip()  # 获取主演信息
            leader = leader_info.split('/')[0].strip()  # 取主演的中文名字部分
            # 只提取中文部分，直到遇到空格或其他字符
            leader = ''.join(filter(lambda x: '\u4e00' <= x <= '\u9fa5', leader))  # 过滤出中文字符
        
        # 创建 Movie 对象并添加到列表
        movies.append(Movie(
            id=movie_id,
            title=title,
            description=description,
            rating=rating,
            leader=leader,
            years=years,
            country=country,
            director_description=director_description,
            tags=tags,
            cover_image=picture_url,
            douban_id=douban_id
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
                INSERT INTO movies_top250 (id, douban_id, title, description, rating, leader, tags, years, country, director_description, cover_image, view_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                movie.id,
                movie.douban_id,
                movie.title,
                movie.description,
                movie.rating,
                movie.leader,
                '/'.join(movie.tags),
                movie.years,
                movie.country,
                movie.director_description,
                movie.cover_image,
                movie.view_count
            ))
            connection.commit()
    except Exception as e:
        logging.error(f"Error inserting movie {movie.title}: {str(e)}")
    finally:
        connection.close()

# 爬取电影信息并保存到数据库
async def get_results(url):
    html = await fetch(url)  # 获取网页内容
    movies, next_link = await parse(html)  # 解析网页内容
    for movie in movies:
        insert_movie(movie)  # 将每个电影数据插入 MySQL
    return next_link  # 返回下一页链接

# 处理任务的异步函数
async def handle_tasks(work_queue):
    while not work_queue.empty():
        current_url = await work_queue.get()  # 获取当前 URL
        print('current_url:', current_url)
        try:
            next_link = await get_results(current_url)  # 获取电影信息
            print('put link:', next_link)  # 打印下一页链接
            if next_link:
                work_queue.put_nowait(next_link)  # 将下一页链接放入队列
        except Exception as e:
            logging.exception('Error for {}'.format(current_url), exc_info=True)  # 记录异常

# 运行异步任务
def event_loop():
    create_table()  # 创建数据库表
    q = asyncio.Queue()  # 创建任务队列
    q.put_nowait(base_url)  # 放入初始的 URL
    loop = asyncio.get_event_loop()  # 获取事件循环
    tasks = [handle_tasks(q)]  # 创建任务
    loop.run_until_complete(asyncio.wait(tasks))  # 运行任务

# 执行程序
if __name__ == "__main__":
    event_loop()  # 启动事件循环