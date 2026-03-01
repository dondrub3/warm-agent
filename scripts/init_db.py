#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化数据库
创建用户表和用量记录表
"""

import os
import sys
import psycopg2

def init_database():
    """初始化数据库"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/warm_agent")
    
    print(f"Connecting to database...")
    
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # 读取并执行迁移文件
            migration_file = os.path.join(
                os.path.dirname(__file__), 
                "migrations", 
                "001_create_user_tables.sql"
            )
            
            if os.path.exists(migration_file):
                with open(migration_file, 'r') as f:
                    sql = f.read()
                
                print("Executing migration...")
                cur.execute(sql)
                print("✅ Database initialized successfully!")
            else:
                print(f"❌ Migration file not found: {migration_file}")
                return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
