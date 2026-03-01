#!/usr/bin/env python3
"""
测试数据库连接脚本
"""

import psycopg2
import redis
import time

def test_postgres():
    """测试PostgreSQL连接"""
    print("🔍 测试PostgreSQL连接...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL连接成功: {version}")
        
        # 创建warm_agent数据库
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'warm_agent'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE warm_agent")
            print("✅ 创建warm_agent数据库成功")
        else:
            print("✅ warm_agent数据库已存在")
            
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        return False

def test_redis():
    """测试Redis连接"""
    print("🔍 测试Redis连接...")
    try:
        r = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True
        )
        # 测试连接
        r.ping()
        print("✅ Redis连接成功")
        
        # 测试基本操作
        r.set("test_key", "test_value")
        value = r.get("test_key")
        if value == "test_value":
            print("✅ Redis读写测试成功")
        else:
            print("❌ Redis读写测试失败")
            
        r.delete("test_key")
        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

def main():
    print("🚀 开始测试数据库连接...")
    print("-" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 测试PostgreSQL
    postgres_ok = test_postgres()
    
    # 测试Redis
    redis_ok = test_redis()
    
    print("-" * 50)
    if postgres_ok and redis_ok:
        print("🎉 所有数据库连接测试成功！")
        print("📊 服务状态:")
        print("  • PostgreSQL: ✅ 运行中 (localhost:5432)")
        print("  • Redis: ✅ 运行中 (localhost:6379)")
        print("  • warm_agent数据库: ✅ 已创建")
    else:
        print("⚠️  数据库连接测试失败，请检查服务状态")
        
    return postgres_ok and redis_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)