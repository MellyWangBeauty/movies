import requests
import json
import time
import pandas as pd
from datetime import datetime
import random
import logging
import pymysql
from typing import List, Dict, Optional
import os

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'qaz741',
    'database': 'movies_db',
    'charset': 'utf8mb4'
}

# 配置日志
logging.basicConfig(
    level=logging.WARNING,  # 将日志级别改为WARNING，减少INFO级别的输出
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MovieCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://movie.douban.com/explore'
        }
        self.url_base = 'https://m.douban.com/rexxar/api/v2/movie/recommend'
        self.session = requests.Session()
        self.data_dir = 'data'
        self.ensure_data_dir()
        self.db = None

    def connect_db(self):
        """连接数据库"""
        if not self.db or not self.db.open:
            self.db = pymysql.connect(**db_config)
        return self.db

    def close_db(self):
        """关闭数据库连接"""
        if self.db and self.db.open:
            self.db.close()

    def create_table(self):
        """创建数据表（如果不存在）"""
        connection = self.connect_db()
        try:
            with connection.cursor() as cursor:
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
        except Exception as e:
            logging.error(f"创建表失败: {str(e)}")
            connection.rollback()

    def save_to_db(self, movie_data: Dict) -> bool:
        """保存单条电影数据到数据库"""
        connection = self.connect_db()
        try:
            with connection.cursor() as cursor:
                # 检查是否已存在
                check_sql = "SELECT douban_id FROM movies_top250 WHERE douban_id = %s"
                cursor.execute(check_sql, (movie_data['douban_id'],))
                if cursor.fetchone():
                    return True  # 已存在，跳过

                # 插入数据
                sql = """
                INSERT INTO movies_top250 (
                    douban_id, title, description, rating, leader,
                    tags, years, country, director_description, cover_image, view_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    movie_data['douban_id'],
                    movie_data['title'],
                    '',  # description 默认为空
                    float(movie_data['rating']) if movie_data['rating'] else 0.0,
                    '',  # leader 默认为空
                    movie_data['tags'],
                    movie_data['years'],
                    movie_data['country'],
                    movie_data['director_description'],
                    movie_data['cover_image'],
                    0  # view_count 默认为0
                ))
                connection.commit()
                return True
        except Exception as e:
            logging.error(f"保存电影 {movie_data['title']} 失败: {str(e)}")
            connection.rollback()
            return False

    def ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_request(self, params: Dict, max_retries: int = 3, delay: float = 1.0) -> Optional[Dict]:
        """发送请求并获取响应，包含重试机制"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.url_base,
                    headers=self.headers,
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # 如果被限制，等待更长时间
                    wait_time = (attempt + 1) * 5
                    logging.warning(f"请求被限制，等待{wait_time}秒后重试")
                    time.sleep(wait_time)
                else:
                    logging.error(f"请求失败，状态码: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logging.error(f"请求异常: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(delay * (attempt + 1))
                continue
                
        return None

    def process_movie_data(self, movie: Dict) -> Dict:
        """处理单个电影数据，提取所需字段"""
        processed = {}
        
        # 提取douban_id
        if 'uri' in movie:
            uri = movie['uri']
            douban_id = uri.split('/')[-1]
            processed['douban_id'] = douban_id
            
        # 提取标题
        processed['title'] = movie.get('title', '')
        
        # 提取评分
        processed['rating'] = movie.get('rating', {}).get('value', '')
        
        # 提取封面图片
        if 'pic' in movie:
            processed['cover_image'] = movie['pic'].get('normal', '')
        elif 'cover_url' in movie:
            processed['cover_image'] = movie['cover_url']
        elif 'cover' in movie:
            if isinstance(movie['cover'], dict):
                processed['cover_image'] = movie['cover'].get('url', '')
            else:
                processed['cover_image'] = movie['cover']
        else:
            processed['cover_image'] = ''
        
        # 处理card_subtitle字段，格式通常为: "2024 / 中国大陆 / 喜剧 科幻 / 李阳 / 张若昀 钟楚曦"
        subtitle = movie.get('card_subtitle', '')
        if subtitle:
            parts = subtitle.split(' / ')
            if len(parts) >= 4:
                processed['years'] = parts[0].strip()
                processed['country'] = parts[1].strip()
                processed['tags'] = parts[2].strip().replace(' ', '/')
                processed['director_description'] = parts[3].strip()
        
        # 打印调试信息
        if not processed['cover_image']:
            logging.debug(f"未找到封面图片，原始数据: {json.dumps(movie, ensure_ascii=False)}")
        
        return processed

    def get_movies_data(self, page_cnt: int = 5) -> List[Dict]:
        """获取电影数据"""
        all_movies = []
        params = {
            'refresh': '0',
            'start': '0',
            'count': '20',
            'selected_categories': '',
            'uncollect': 'false',
            'tags': '2025',
            'sort': 'S'
        }

        print(f"开始爬取电影数据，共{page_cnt}页...")
        
        for i in range(page_cnt):
            params['start'] = str(i * 20)
            response = self.get_request(params)
            
            if response and 'items' in response:
                movies = response['items']
                processed_movies = [self.process_movie_data(movie) for movie in movies]
                all_movies.extend(processed_movies)
                print(f"已完成: {i+1}/{page_cnt} 页")
                time.sleep(random.uniform(1, 2))
            else:
                logging.error(f"第 {i+1} 页数据获取失败")

        return all_movies

    def save_to_csv(self, data: List[Dict], filename: Optional[str] = None) -> str:
        """保存数据到CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'movies_{timestamp}.csv'
            
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            
            # 指定要保存的列和顺序
            columns_to_save = [
                'douban_id',
                'title',
                'rating',
                'director_description',
                'tags',
                'years',
                'country',
                'cover_image'
            ]
            
            # 确保所有列都存在，如果不存在则填充空值
            for col in columns_to_save:
                if col not in df.columns:
                    df[col] = ''
            
            # 只保存指定的列
            df_to_save = df[columns_to_save]
            
            # 保存到CSV，确保中文正确显示
            df_to_save.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"\n数据已保存到: {filepath}")
            print(f"共保存 {len(df_to_save)} 条电影数据")
            
            return filepath
            
        except Exception as e:
            logging.error(f"保存CSV文件失败: {str(e)}")
            return ""

def main():
    try:
        crawler = MovieCrawler()
        
        # 创建数据表
        crawler.create_table()
        
        # 获取电影数据
        movies_data = crawler.get_movies_data(page_cnt=5)
        
        if movies_data:
            # 保存到数据库
            success_count = 0
            skip_count = 0
            for movie in movies_data:
                if crawler.save_to_db(movie):
                    success_count += 1
                else:
                    skip_count += 1
            
            print(f"\n数据已保存到数据库")
            print(f"新增: {success_count} 条")
            print(f"跳过: {skip_count} 条")
            print("\n爬虫任务完成！")
        else:
            print("未获取到任何数据！")
            
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
    finally:
        crawler.close_db()

if __name__ == '__main__':
    main()