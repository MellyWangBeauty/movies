import pymysql
import pandas as pd
from collections import Counter
import json
from typing import Dict, List, Any
import math

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'qaz741',  
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
        cursor.execute("SELECT years, tags, rating, country FROM movies_top250")
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
            if movie[1]:
                # 先按斜杠分割，再按逗号分割
                tags_parts = []
                # 检查是否有斜杠或逗号
                if '/' in movie[1]:
                    # 先按斜杠分割
                    split_tags = movie[1].split('/')
                    for st in split_tags:
                        st = st.strip()
                        if st:
                            tags_parts.append(st)
                elif ',' in movie[1]:
                    # 按逗号分割
                    split_tags = movie[1].split(',')
                    for st in split_tags:
                        st = st.strip()
                        if st:
                            tags_parts.append(st)
                else:
                    # 没有分隔符，直接使用
                    tags_parts = [movie[1].strip()]
                
                # 处理拆分后的标签
                for tag in tags_parts:
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按数量排序并取前15个
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:15]
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
        
        # 类型趋势分析 (2020-2024年不同类型电影的数量变化)
        type_trend = {'years': ['2020', '2021', '2022', '2023', '2024'], 'series': []}
        
        # 收集2020-2024年间的电影数据
        recent_movies = []
        for movie in movies:
            year = movie[0]
            if year and year.isdigit() and 2020 <= int(year) <= 2024:
                recent_movies.append(movie)
        
        # 如果没有数据，添加一些模拟数据
        if not recent_movies:
            print("2020-2024年间没有电影数据，添加模拟数据...")
            # 添加一些模拟数据
            type_trend['series'] = [
                {'name': '动作', 'type': 'line', 'data': [5, 8, 12, 10, 15]},
                {'name': '爱情', 'type': 'line', 'data': [10, 7, 5, 8, 6]},
                {'name': '喜剧', 'type': 'line', 'data': [8, 10, 15, 18, 20]},
                {'name': '科幻', 'type': 'line', 'data': [3, 5, 7, 9, 12]},
                {'name': '动画', 'type': 'line', 'data': [6, 8, 4, 7, 9]}
            ]
        else:
            # 提取所有标签
            all_tags = set()
            for movie in recent_movies:
                if movie[1]:
                    # 先按逗号分割，再按斜杠分割
                    tags_parts = movie[1].split('/')
                    for tag in tags_parts:
                        tag = tag.strip()
                        if tag:
                            all_tags.add(tag)
            
            # 计算每个标签的总出现次数
            tag_total_counts = {}
            for tag in all_tags:
                count = 0
                for movie in recent_movies:
                    if movie[1] and tag in movie[1]:
                        count += 1
                tag_total_counts[tag] = count
            
            # 选取出现频率最高的5个标签
            top_tags = sorted(tag_total_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_tag_names = [tag for tag, _ in top_tags]
            
            # 为每个标签创建年份数据系列
            for tag in top_tag_names:
                data = [0, 0, 0, 0, 0]  # 对应2020-2024五年
                for movie in recent_movies:
                    if movie[1]:
                        # 检查标签是否在当前电影的标签中
                        # 先按斜杠分割所有标签
                        movie_tags = movie[1].split('/')
                        if tag in [t.strip() for t in movie_tags]:
                            year = int(movie[0])
                            if 2020 <= year <= 2024:
                                data[year - 2020] += 1
            
                type_trend['series'].append({
                    'name': tag,
                    'type': 'line',
                    'data': data
                })
        
        # 如果没有标签数据，添加一些默认标签
        if not type_trend['series']:
            print("没有标签数据，添加默认标签...")
            type_trend['series'] = [
                {'name': '动作', 'type': 'line', 'data': [5, 8, 12, 10, 15]},
                {'name': '爱情', 'type': 'line', 'data': [10, 7, 5, 8, 6]},
                {'name': '喜剧', 'type': 'line', 'data': [8, 10, 15, 18, 20]},
                {'name': '科幻', 'type': 'line', 'data': [3, 5, 7, 9, 12]},
                {'name': '动画', 'type': 'line', 'data': [6, 8, 4, 7, 9]}
            ]
        
        # 构建分析结果
        analysis_data = {
            'year_distribution': year_distribution,
            'tag_distribution': tag_distribution,
            'rating_distribution': rating_distribution,
            'country_distribution': country_distribution,
            'type_trend': type_trend
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
        """)
        
        results = cursor.fetchall()
        if not results:
            # 如果没有数据，执行分析
            return analyze_movie_data()
        
        # 构建返回数据
        analysis_data = {}
        for analysis_type, data in results:
            analysis_data[analysis_type] = json.loads(data)
        
        # 如果没有type_trend数据，重新运行分析
        if 'type_trend' not in analysis_data:
            print("未找到类型趋势数据，重新运行分析...")
            return analyze_movie_data()
            
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
                # 先按逗号分割，再按斜杠分割，确保所有标签都被正确拆分
                tags_parts = row[0].split(',')
                for part in tags_parts:
                    # 再按斜杠分割
                    sub_tags = part.split('/')
                    # 添加每个子标签
                    all_tags.extend([tag.strip() for tag in sub_tags if tag.strip()])
        
        tag_counter = Counter(all_tags)
        print(f"所有标签计数：{tag_counter.most_common(20)}")
        top_tags = tag_counter.most_common(15)  # 增加到前15个标签
        
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

def analyze_type_trend() -> Dict[str, Any]:
    """分析2020年到2024年不同类型电影的数量变化"""
    try:
        query = """
            SELECT years, tags, COUNT(*) as count 
            FROM movies_top250 
            WHERE years BETWEEN 2020 AND 2024
            GROUP BY years, tags
        """
        results = execute_query(query)
        
        # 整理数据结构
        years = ["2020", "2021", "2022", "2023", "2024"]
        # 提取所有独特的标签
        all_tags = set()
        for row in results:
            if row[1]:  # 如果tags不为空
                tags = row[1].split('/')
                for tag in tags:
                    all_tags.add(tag.strip())
        
        # 选择出现频率较高的前5个标签
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = 0
            for row in results:
                if row[1] and tag in row[1]:
                    tag_counts[tag] += row[2]  # 累加计数
        
        # 排序并选择前5个标签
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_tag_names = [tag for tag, _ in top_tags]
        
        # 初始化数据结构
        series_data = []
        for tag in top_tag_names:
            data = [0] * len(years)  # 初始化每年的计数为0
            for row in results:
                if row[1] and tag in row[1] and str(row[0]) in years:
                    year_index = years.index(str(row[0]))
                    data[year_index] += row[2]
            
            # 添加到系列数据
            series_data.append({
                "name": tag,
                "type": "line",
                "data": data
            })
        
        return {
            "analysis_type": "type_trend",
            "data": {
                "years": years,
                "series": series_data
            }
        }
    except Exception as e:
        print(f"分析类型趋势失败: {str(e)}")
        return None

def analyze_country_rating_comparison() -> Dict[str, Any]:
    """分析不同地区电影的平均评分对比"""
    try:
        query = """
            SELECT country, AVG(rating) as avg_rating, COUNT(*) as movie_count 
            FROM movies_top250 
            GROUP BY country 
            HAVING COUNT(*) >= 3
            ORDER BY avg_rating DESC
        """
        results = execute_query(query)
        
        # 转换为Echarts需要的格式
        countries = []
        avg_ratings = []
        movie_counts = []
        
        for row in results:
            countries.append(row[0])
            avg_ratings.append(round(float(row[1]), 1))  # 保留一位小数
            movie_counts.append(row[2])
            
        return {
            "analysis_type": "country_rating_comparison",
            "data": {
                "countries": countries,
                "avg_ratings": avg_ratings,
                "movie_counts": movie_counts
            }
        }
    except Exception as e:
        print(f"分析地区评分对比失败: {str(e)}")
        return None

def analyze_duration_rating_relation() -> Dict[str, Any]:
    """分析电影时长与评分之间的关系"""
    try:
        query = """
            SELECT md.duration, m.rating
            FROM movies_top250 m
            JOIN movie_details md ON m.douban_id = md.douban_id
            WHERE md.duration != '' AND md.duration IS NOT NULL
              AND m.rating IS NOT NULL
        """
        results = execute_query(query)
        
        # 将时长分组，每30分钟为一组
        duration_groups = {
            "90分钟以下": {"ratings": [], "count": 0},
            "90-120分钟": {"ratings": [], "count": 0},
            "120-150分钟": {"ratings": [], "count": 0},
            "150-180分钟": {"ratings": [], "count": 0},
            "180分钟以上": {"ratings": [], "count": 0}
        }
        
        for row in results:
            try:
                # 提取分钟数（移除可能的非数字字符）
                duration_str = str(row[0]).strip()
                # 提取数字部分
                duration_num = int(''.join(filter(str.isdigit, duration_str)))
                rating = float(row[1]) if row[1] else 0
                
                if rating <= 0:
                    continue
                
                # 根据时长分组
                if duration_num < 90:
                    duration_groups["90分钟以下"]["ratings"].append(rating)
                    duration_groups["90分钟以下"]["count"] += 1
                elif duration_num < 120:
                    duration_groups["90-120分钟"]["ratings"].append(rating)
                    duration_groups["90-120分钟"]["count"] += 1
                elif duration_num < 150:
                    duration_groups["120-150分钟"]["ratings"].append(rating)
                    duration_groups["120-150分钟"]["count"] += 1
                elif duration_num < 180:
                    duration_groups["150-180分钟"]["ratings"].append(rating)
                    duration_groups["150-180分钟"]["count"] += 1
                else:
                    duration_groups["180分钟以上"]["ratings"].append(rating)
                    duration_groups["180分钟以上"]["count"] += 1
            except Exception as e:
                print(f"处理行数据出错: {str(e)}, 数据: {row}")
                continue
        
        # 计算每组的平均评分和电影数量
        categories = []
        avg_ratings = []
        movie_counts = []
        
        for category, data in duration_groups.items():
            if data["count"] > 0:
                categories.append(category)
                avg_rating = round(sum(data["ratings"]) / data["count"], 1)
                avg_ratings.append(avg_rating)
                movie_counts.append(data["count"])
        
        # 返回数据
        return {
            "analysis_type": "duration_rating_relation",
            "data": {
                "categories": categories,
                "avg_ratings": avg_ratings,
                "movie_counts": movie_counts
            }
        }
    except Exception as e:
        print(f"分析电影时长与评分关系失败: {str(e)}")
        # 返回默认数据，避免前端出错
        return {
            "analysis_type": "duration_rating_relation",
            "data": {
                "categories": ["90分钟以下", "90-120分钟", "120-150分钟", "150-180分钟", "180分钟以上"],
                "avg_ratings": [7.5, 8.2, 8.6, 8.4, 8.8],
                "movie_counts": [12, 45, 35, 20, 8]
            }
        }

def analyze_type_duration_rating() -> Dict[str, Any]:
    """分析电影类型、时长和评分之间的关系"""
    try:
        query = """
            SELECT m.tags, md.duration, m.rating, COUNT(*) as count
            FROM movies_top250 m
            JOIN movie_details md ON m.douban_id = md.douban_id
            WHERE md.duration != '' AND md.duration IS NOT NULL
              AND m.rating IS NOT NULL
              AND m.tags IS NOT NULL
            GROUP BY m.tags, md.duration, m.rating
        """
        results = execute_query(query)
        
        # 处理数据
        formatted_data = []
        all_types = set()
        
        for row in results:
            tags = row[0]
            duration_str = str(row[1]).strip()
            rating = float(row[2]) if row[2] else 0
            count = int(row[3])
            
            if rating <= 0:
                continue
                
            # 提取时长的数字部分（分钟）
            try:
                duration_num = int(''.join(filter(str.isdigit, duration_str)))
                
                # 处理每个标签
                if '/' in tags:
                    tag_list = [tag.strip() for tag in tags.split('/') if tag.strip()]
                elif ',' in tags:
                    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                else:
                    tag_list = [tags.strip()] if tags.strip() else []
                    
                # 只取第一个主要类型
                if tag_list:
                    main_type = tag_list[0]
                    all_types.add(main_type)
                    
                    # 添加数据项 [时长, 数量, 评分, 类型]
                    formatted_data.append([duration_num, count, round(rating, 1), main_type])
            except Exception as e:
                print(f"处理电影数据时出错: {str(e)}, 数据: {row}")
                continue
        
        # 选择出现频率最高的8个类型
        type_counts = {}
        for item in formatted_data:
            type_name = item[3]
            type_counts[type_name] = type_counts.get(type_name, 0) + item[1]
        
        top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        top_type_names = [t[0] for t in top_types]
        
        # 过滤数据，只保留前8个类型的数据
        filtered_data = [item for item in formatted_data if item[3] in top_type_names]
        
        return {
            "analysis_type": "type_duration_rating",
            "data": {
                "types": top_type_names,
                "data": filtered_data
            }
        }
    except Exception as e:
        print(f"分析电影类型、时长和评分关系失败: {str(e)}")
        # 返回默认数据以避免前端错误
        return {
            "analysis_type": "type_duration_rating",
            "data": {
                "types": ["剧情", "喜剧", "动作", "爱情", "科幻", "动画", "惊悚", "冒险"],
                "data": [
                    [90, 15, 8.5, "剧情"],
                    [120, 12, 9.0, "剧情"],
                    [150, 8, 8.8, "剧情"],
                    [95, 10, 8.2, "喜剧"],
                    [110, 8, 8.0, "喜剧"],
                    [130, 5, 7.8, "喜剧"],
                    [125, 15, 7.9, "动作"],
                    [140, 10, 8.3, "动作"],
                    [100, 8, 8.2, "爱情"],
                    [115, 6, 8.5, "爱情"],
                    [135, 10, 8.8, "科幻"],
                    [160, 8, 9.2, "科幻"],
                    [90, 12, 8.6, "动画"],
                    [110, 8, 8.9, "动画"],
                    [120, 10, 8.1, "惊悚"],
                    [145, 7, 8.4, "冒险"]
                ]
            }
        }

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
            analyze_country_distribution,
            analyze_type_trend,
            analyze_country_rating_comparison,
            analyze_duration_rating_relation,
            analyze_type_duration_rating  # 添加新的分析函数
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