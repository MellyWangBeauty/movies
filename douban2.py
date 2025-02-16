import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
import pymysql
import time

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
    def __init__(self, id, title, description, star, leader, tags, years, country, director_description, image_link):
        self.id = id
        self.star = star
        self.description = description
        self.title = title
        self.leader = leader
        self.tags = tags
        self.years = years
        self.country = country
        self.director_description = director_description
        self.image_link = image_link

# 异步请求获取网页内容
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(response.status)
            assert response.status == 200
            return await response.text()

# 解析页面内容
async def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    movies_info = soup.find('ol', {'class': 'grid_view'})
    movies = []
    for movie_info in movies_info.find_all('li'):
        pic = movie_info.find('div', {'class': 'pic'})
        picture_url = pic.find('img').attrs['src']
        movie_id = pic.find('em').text
        url = movie_info.find('div', {"class": "info"})
        title = url.find('span', {'class': 'title'}).text

        # 提取电影的其他信息
        info = url.find('div', {'class': 'bd'})
        movie_detail = info.find('p')
        quote = info.find('p', {'class': 'quote'})
        description = quote.find('span').text if quote else ''
        star = info.find('div', {"class": 'star'}).find('span', {'class': 'rating_num'}).text
        tags = movie_detail.text.strip().split('\n')[-1].split('/')[-1].split(' ')
        tags = [tag.strip() for tag in tags]
        years = movie_detail.text.strip().split('\n')[-1].split('/')[0].strip()
        country = movie_detail.text.strip().split('\n')[-1].split('/')[1].strip()
        
        # 处理导演和主演信息
        temp = movie_detail.text.strip().split('\n')
        try:
            director_description = temp[0].split('/')[0].strip().split(':')[1]
        except IndexError:
            director_description = ''
        try:
            leader = temp[0].split('/')[0].strip().split(' ')[-1]
        except IndexError:
            leader = ''
        
        movies.append(Movie(id=movie_id, title=title, description=description, star=star, leader=leader,
                            years=years, country=country, director_description=director_description,
                            tags=tags, image_link=picture_url))
    
    # 获取下一页链接
    next_page = soup.find('link', {'rel': 'next'})
    next_link = base_url + next_page.attrs['href'] if next_page else None
    return movies, next_link

# 插入电影数据到 MySQL
def insert_movie(movie):
    # 创建数据库连接
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO movie_info (id, title, description, star, leader, tags, years, country, director_description, image_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (movie.id, movie.title, movie.description, movie.star, movie.leader,
                                 '/'.join(movie.tags), movie.years, movie.country, movie.director_description, movie.image_link))
            connection.commit()
    finally:
        connection.close()

# 爬取电影信息并保存到数据库
async def get_results(url):
    html = await fetch(url)
    movies, next_link = await parse(html)
    for movie in movies:
        insert_movie(movie)  # 将每个电影数据插入 MySQL
    return next_link

# 处理任务的异步函数
async def handle_tasks(work_queue):
    while not work_queue.empty():
        current_url = await work_queue.get()
        try:
            next_link = await get_results(current_url)
            print('put link:', next_link)
            if next_link:
                work_queue.put_nowait(next_link)
        except Exception as e:
            logging.exception('Error for {}'.format(current_url), exc_info=True)

# 运行异步任务
def event_loop():
    q = asyncio.Queue()
    q.put_nowait(base_url)  # 放入初始的 URL
    loop = asyncio.get_event_loop()
    tasks = [handle_tasks(q)]
    loop.run_until_complete(asyncio.wait(tasks))

# 执行程序
event_loop()
