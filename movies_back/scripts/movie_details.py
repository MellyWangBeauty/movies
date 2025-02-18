import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pymysql
import time
from typing import Optional, Dict, List

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'qaz741',  # 替换为你的数据库密码
    'database': 'movies_db',
    'charset': 'utf8mb4'
}

# 代理池
PROXIES = [
       {
        "ip": "125.125.238.72",
        "port": 59848
      },
      {
        "ip": "119.102.186.88",
        "port": 33661
      },
      {
        "ip": "121.205.213.146",
        "port": 45183
      },
      {
        "ip": "123.55.163.163",
        "port": 26200
      },
      {
        "ip": "117.69.10.241",
        "port": 51958
      },
      {
        "ip": "119.41.200.1",
        "port": 53218
      },
      {
        "ip": "121.224.217.232",
        "port": 49083
      },
      {
        "ip": "122.241.237.130",
        "port": 40335
      },
      {
        "ip": "119.101.108.81",
        "port": 40013
      },
      {
        "ip": "116.209.52.52",
        "port": 50951
      }
]

class ProxyManager:
    def __init__(self, proxies: List[Dict[str, str]]):
        self.proxies = proxies
        self.failed_proxies = set()  # 改用set存储失败的代理
        self.lock = asyncio.Lock()
        self.current_index = 0  # 用于轮换代理

    async def get_proxy(self) -> Optional[str]:
        async with self.lock:
            available_proxies = [p for p in self.proxies 
                               if f"{p['ip']}:{p['port']}" not in self.failed_proxies]
            if not available_proxies:
                print("警告：没有可用的代理！")
                return None
            
            # 轮换使用代理
            self.current_index = (self.current_index + 1) % len(available_proxies)
            proxy = available_proxies[self.current_index]
            return f"http://{proxy['ip']}:{proxy['port']}"

    async def mark_proxy_failed(self, proxy: str):
        async with self.lock:
            self.failed_proxies.add(proxy)
            print(f"代理 {proxy} 失败，已移除")
            self.proxies = [p for p in self.proxies 
                          if f"{p['ip']}:{p['port']}" not in self.failed_proxies]

proxy_manager = ProxyManager(PROXIES)

async def fetch(session, url, retries=3):
    last_error = None
    for attempt in range(retries):
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        proxy = await proxy_manager.get_proxy()
        if not proxy:
            await asyncio.sleep(5)  # 无可用代理时等待
            continue
            
        try:
            async with session.get(url, headers=headers, proxy=proxy, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 404:
                    print(f"请求失败: 404 - {url}，该电影可能已下架或不存在。")
                    return None
                elif response.status in [429, 403]:
                    print(f"请求被限制: {response.status} - {url}")
                    await proxy_manager.mark_proxy_failed(proxy)
                    await asyncio.sleep(random.uniform(5, 10))
                    continue
                else:
                    print(f"请求失败: {response.status} - {url}")
                    await proxy_manager.mark_proxy_failed(proxy)
                    continue
        except Exception as e:
            last_error = str(e)
            print(f"请求异常: {last_error} - 使用代理: {proxy}")
            await proxy_manager.mark_proxy_failed(proxy)
            if attempt < retries - 1:
                await asyncio.sleep(random.uniform(2, 5))
                continue
    
    print(f"所有重试都失败了，最后的错误: {last_error}")
    return None

# 解析电影详情页
def parse_movie_detail(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 获取主演列表 - 修改选择器
    actors = []
    actor_spans = soup.select('#info .attrs span a[rel="v:starring"]')
    if not actor_spans:
        # 备用选择器
        actor_spans = soup.select('#info .attrs a[rel="v:starring"]')
    for actor in actor_spans[:5]:  # 限制主演数量为5个
        actors.append(actor.text.strip())
    
    # 获取剧情简介
    plot = ''
    plot_element = soup.select_one('[property="v:summary"]')
    if plot_element:
        plot = plot_element.text.strip()
    
    # 获取片长
    duration = ''
    duration_element = soup.select_one('[property="v:runtime"]')
    if duration_element:
        duration = duration_element.get('content', '')
    
    # 获取短评
    comments = []
    comment_items = soup.select('.comment-item')
    for item in comment_items[:5]:  # 只取前5条
        comment = item.select_one('.short')
        if comment:
            comment_text = comment.text.strip()
        else:
            comment_text = ""  # 或者其他默认值
        comments.append(comment_text)
    
    # 补齐5条短评
    while len(comments) < 5:
        comments.append('')
    
    return {
        'actors': '|'.join(actors),
        'plot': plot,
        'duration': duration,
        'comments': comments
    }

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.connection = None
        
    def get_connection(self):
        if self.connection is None or not self.connection.open:
            self.connection = pymysql.connect(**self.config)
        return self.connection
        
    def close(self):
        if self.connection and self.connection.open:
            self.connection.close()
            
    def execute_query(self, sql, params=None):
        connection = self.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                connection.commit()
                return cursor.fetchall()
        except Exception as e:
            connection.rollback()
            raise e

db_manager = DatabaseManager(db_config)

def save_movie_detail(douban_id, detail):
    if not detail:
        return False
        
    try:
        # 检查是否已存在
        check_sql = "SELECT douban_id FROM movie_details WHERE douban_id = %s"
        results = db_manager.execute_query(check_sql, (douban_id,))
        
        if results:
            print(f"电影 {douban_id} 已存在，跳过")
            return True
            
        sql = """
            INSERT INTO movie_details 
            (douban_id, actors, plot, duration, comment1, comment2, comment3, comment4, comment5)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        db_manager.execute_query(sql, (
            douban_id,
            detail['actors'],
            detail['plot'],
            detail['duration'],
            detail['comments'][0],
            detail['comments'][1],
            detail['comments'][2],
            detail['comments'][3],
            detail['comments'][4]
        ))
        print(f"保存电影 {douban_id} 详情成功")
        return True
    except Exception as e:
        print(f"保存电影 {douban_id} 详情失败: {str(e)}")
        return False

def get_movies_to_crawl():
    """获取需要爬取的电影ID列表"""
    try:
        sql = """
            SELECT m.douban_id 
            FROM movies_top250 m 
            LEFT JOIN movie_details d ON m.douban_id = d.douban_id 
            WHERE d.douban_id IS NULL
        """
        results = db_manager.execute_query(sql)
        return [result[0] for result in results]
    except Exception as e:
        print(f"获取待爬取电影列表失败: {str(e)}")
        return []

def create_details_table():
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS movie_details (
            id INT AUTO_INCREMENT PRIMARY KEY,
            douban_id VARCHAR(20) NOT NULL UNIQUE,
            actors TEXT,
            plot TEXT,
            duration VARCHAR(10),
            comment1 TEXT,
            comment2 TEXT,
            comment3 TEXT,
            comment4 TEXT,
            comment5 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        db_manager.execute_query(sql)
        print("数据表创建成功")
    except Exception as e:
        print(f"创建数据表失败: {str(e)}")

def delete_empty_duration_records():
    """删除数据库中duration为空的记录"""
    try:
        sql = """
            DELETE FROM movie_details 
            WHERE duration IS NULL OR duration = ''
        """
        affected_rows = db_manager.execute_query(sql)
        print(f"已删除无效记录")
    except Exception as e:
        print(f"删除空duration记录失败: {str(e)}")

# 处理单个电影
async def process_movie(douban_id: str, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        async with aiohttp.ClientSession() as session:
            url = f'https://movie.douban.com/subject/{douban_id}/'
            html = await fetch(session, url)
            if html:
                detail = parse_movie_detail(html)
                if detail:
                    if save_movie_detail(douban_id, detail):
                        # 成功保存后随机等待0.5-1秒
                        await asyncio.sleep(random.uniform(0.5, 1))
                    else:
                        print(f"保存电影 {douban_id} 失败，跳过")
                else:
                    print(f"解析电影 {douban_id} 详情失败")
            else:
                print(f"获取电影 {douban_id} 页面失败")

# 主函数
async def main():
    try:
        # 创建数据表
        create_details_table()
        
        # 删除duration为空的记录
        delete_empty_duration_records()
        
        # 获取需要爬取的电影ID
        douban_ids = get_movies_to_crawl()
        if not douban_ids:
            print("所有电影都已爬取完成")
            return
            
        print(f"需要爬取 {len(douban_ids)} 部电影")
        
        # 增加并发数为5，因为有足够多的代理IP
        semaphore = asyncio.Semaphore(5)
        
        # 创建任务列表并分批执行，每批30个
        batch_size = 30
        for i in range(0, len(douban_ids), batch_size):
            batch = douban_ids[i:i + batch_size]
            tasks = [process_movie(douban_id, semaphore) for douban_id in batch]
            await asyncio.gather(*tasks)
            print(f"完成第{i//batch_size + 1}批爬取")
            # 批次间等待时间缩短到2秒
            await asyncio.sleep(2)
    finally:
        # 清理资源
        db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())