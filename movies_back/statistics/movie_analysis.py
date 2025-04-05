import pymysql
import pandas as pd
from collections import Counter
import json
from typing import Dict, List, Any

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'qaz741',  # 替换为你的数据库密码
    'database': 'movies_db',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        return pymysql.connect(**db_config)
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        raise e

def execute_query(sql, params=None):
    """执行SQL查询"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            connection.commit()
            return cursor.fetchall()
    except Exception as e:
        connection.rollback()
        print(f"执行SQL失败: {str(e)}")
        raise e
    finally:
        connection.close()

def create_analysis_table():
    """创建分析结果表"""
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS movie_analysis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            analysis_type VARCHAR(50) NOT NULL,
            analysis_data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        execute_query(sql)
        print("分析结果表创建成功")
    except Exception as e:
        print(f"创建分析结果表失败: {str(e)}")
        raise e

def analyze_movie_data():
    """分析电影数据并返回统计结果"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 创建分析结果表（如果不存在）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movie_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                analysis_type VARCHAR(50) NOT NULL,
                analysis_data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 获取所有电影数据
        cursor.execute("SELECT year, tags, rating, country FROM movies")
        movies = cursor.fetchall()
        
        # 初始化统计数据
        year_distribution = {'years': [], 'counts': []}
        tag_distribution = {'tags': [], 'counts': []}
        rating_distribution = {'ratings': [], 'counts': []}
        country_distribution = {'countries': [], 'counts': []}
        
        # 年份分布统计
        year_counts = {}
        for movie in movies:
            year = movie[0]
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        
        # 按年份排序
        sorted_years = sorted(year_counts.items(), key=lambda x: x[0])
        year_distribution['years'] = [str(year) for year, _ in sorted_years]
        year_distribution['counts'] = [count for _, count in sorted_years]
        
        # 标签分布统计
        tag_counts = {}
        for movie in movies:
            tags = movie[1].split('/') if movie[1] else []
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按数量排序并取前10个
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        tag_distribution['tags'] = [tag for tag, _ in sorted_tags]
        tag_distribution['counts'] = [count for _, count in sorted_tags]
        
        # 评分分布统计
        rating_counts = {}
        for movie in movies:
            rating = movie[2]
            if rating:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        # 按评分排序
        sorted_ratings = sorted(rating_counts.items(), key=lambda x: x[0])
        rating_distribution['ratings'] = [str(rating) for rating, _ in sorted_ratings]
        rating_distribution['counts'] = [count for _, count in sorted_ratings]
        
        # 国家分布统计
        country_counts = {}
        for movie in movies:
            country = movie[3]
            if country:
                country_counts[country] = country_counts.get(country, 0) + 1
        
        # 按数量排序并取前10个
        sorted_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        country_distribution['countries'] = [country for country, _ in sorted_countries]
        country_distribution['counts'] = [count for _, count in sorted_countries]
        
        # 构建分析结果
        analysis_data = {
            'year_distribution': year_distribution,
            'tag_distribution': tag_distribution,
            'rating_distribution': rating_distribution,
            'country_distribution': country_distribution
        }
        
        # 保存分析结果
        for analysis_type, data in analysis_data.items():
            # 检查是否存在该类型的分析结果
            cursor.execute(
                "SELECT id FROM movie_analysis WHERE analysis_type = %s",
                (analysis_type,)
            )
            result = cursor.fetchone()
            
            if result:
                # 如果存在，更新数据
                cursor.execute(
                    "UPDATE movie_analysis SET analysis_data = %s, created_at = CURRENT_TIMESTAMP WHERE analysis_type = %s",
                    (json.dumps(data), analysis_type)
                )
            else:
                # 如果不存在，插入新数据
                cursor.execute(
                    "INSERT INTO movie_analysis (analysis_type, analysis_data) VALUES (%s, %s)",
                    (analysis_type, json.dumps(data))
                )
        
        conn.commit()
        print("分析结果已更新")
        
        return analysis_data
        
    except Exception as e:
        print(f"分析电影数据时出错: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_analysis_data():
    """从数据库获取分析结果"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'movie_analysis'")
        if not cursor.fetchone():
            # 如果表不存在，执行分析
            return analyze_movie_data()
        
        # 获取最新的分析结果
        cursor.execute("""
            SELECT analysis_type, analysis_data 
            FROM movie_analysis 
            ORDER BY created_at DESC 
            LIMIT 4
        """)
        
        results = cursor.fetchall()
        if not results:
            # 如果没有数据，执行分析
            return analyze_movie_data()
        
        # 构建返回数据
        analysis_data = {}
        for analysis_type, data in results:
            analysis_data[analysis_type] = json.loads(data)
        
        return analysis_data
        
    except Exception as e:
        print(f"获取分析数据时出错: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def analyze_year_distribution() -> Dict[str, Any]:
    """分析电影年份分布"""
    try:
        query = "SELECT years, COUNT(*) as count FROM movies_top250 GROUP BY years ORDER BY years"
        results = execute_query(query)
        
        # 转换为Echarts需要的格式
        years = []
        counts = []
        for row in results:
            years.append(row[0])
            counts.append(row[1])
            
        return {
            "analysis_type": "year_distribution",
            "data": {
                "years": years,
                "counts": counts
            }
        }
    except Exception as e:
        print(f"分析年份分布失败: {str(e)}")
        return None

def analyze_tag_distribution() -> Dict[str, Any]:
    """分析电影标签分布"""
    try:
        query = "SELECT tags FROM movies_top250"
        results = execute_query(query)
        all_tags = []
        for row in results:
            if row[0]:
                tags = row[0].split(',')
                all_tags.extend([tag.strip() for tag in tags])
        
        tag_counter = Counter(all_tags)
        top_tags = tag_counter.most_common(10)  # 只取前10个标签
        
        # 转换为Echarts需要的格式
        tags = []
        counts = []
        for tag, count in top_tags:
            tags.append(tag)
            counts.append(count)
            
        return {
            "analysis_type": "tag_distribution",
            "data": {
                "tags": tags,
                "counts": counts
            }
        }
    except Exception as e:
        print(f"分析标签分布失败: {str(e)}")
        return None

def analyze_rating_distribution() -> Dict[str, Any]:
    """分析电影评分分布"""
    try:
        query = "SELECT rating, COUNT(*) as count FROM movies_top250 GROUP BY rating ORDER BY rating"
        results = execute_query(query)
        
        # 转换为Echarts需要的格式
        ratings = []
        counts = []
        for row in results:
            ratings.append(float(row[0]))
            counts.append(row[1])
            
        return {
            "analysis_type": "rating_distribution",
            "data": {
                "ratings": ratings,
                "counts": counts
            }
        }
    except Exception as e:
        print(f"分析评分分布失败: {str(e)}")
        return None

def analyze_country_distribution() -> Dict[str, Any]:
    """分析电影国家分布"""
    try:
        query = "SELECT country, COUNT(*) as count FROM movies_top250 GROUP BY country ORDER BY count DESC"
        results = execute_query(query)
        
        # 转换为Echarts需要的格式
        countries = []
        counts = []
        for row in results:
            countries.append(row[0])
            counts.append(row[1])
            
        return {
            "analysis_type": "country_distribution",
            "data": {
                "countries": countries,
                "counts": counts
            }
        }
    except Exception as e:
        print(f"分析国家分布失败: {str(e)}")
        return None

def save_analysis_result(analysis_result: Dict[str, Any]):
    """保存分析结果到数据库"""
    if not analysis_result:
        return False
        
    try:
        sql = """
            INSERT INTO movie_analysis (analysis_type, analysis_data)
            VALUES (%s, %s)
        """
        execute_query(sql, (
            analysis_result["analysis_type"],
            json.dumps(analysis_result["data"], ensure_ascii=False)
        ))
        print(f"保存 {analysis_result['analysis_type']} 分析结果成功")
        return True
    except Exception as e:
        print(f"保存分析结果失败: {str(e)}")
        return False

def main():
    """主函数，执行所有分析并保存结果"""
    try:
        # 创建数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先删除表
        cursor.execute("DROP TABLE IF EXISTS movie_analysis")
        
        # 重新创建表
        cursor.execute("""
            CREATE TABLE movie_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                analysis_type VARCHAR(50) NOT NULL,
                analysis_data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 执行各项分析
        analyses = [
            analyze_year_distribution,
            analyze_tag_distribution,
            analyze_rating_distribution,
            analyze_country_distribution
        ]
        
        for analysis_func in analyses:
            result = analysis_func()
            if result:
                save_analysis_result(result)
            else:
                print(f"执行 {analysis_func.__name__} 失败")
                
    except Exception as e:
        print(f"执行分析时出错: {str(e)}")
    finally:
        # 关闭数据库连接
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 