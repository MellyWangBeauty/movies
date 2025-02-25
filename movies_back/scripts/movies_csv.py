import requests
import json
import time
import pandas as pd
from datetime import datetime
import random
import logging
from typing import List, Dict, Optional
import os

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
                processed['tags'] = parts[2].strip().replace(' ', '|')
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
            'tags': ['2025','2024','2023','2022','2021','2020'],
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
        # 创建爬虫实例
        crawler = MovieCrawler()
        
        # 获取电影数据
        logging.info("开始爬取电影数据...")
        movies_data = crawler.get_movies_data(page_cnt=2)
        
        if movies_data:
            # 保存到CSV
            saved_file = crawler.save_to_csv(movies_data)
            if saved_file:
                logging.info("爬虫任务完成！")
            else:
                logging.error("保存数据失败！")
        else:
            logging.error("未获取到任何数据！")
            
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")

if __name__ == '__main__':
    main()