#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块
处理用户注册、认证、API Key管理
"""

import os
import re
import uuid
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import psycopg2
from psycopg2.extras import RealDictCursor

# 密码加密
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    PASSLIB_AVAILABLE = True
except ImportError:
    PASSLIB_AVAILABLE = False
    # 备用：使用简单的哈希（仅用于开发测试）
    import hashlib
    def pwd_context_hash(password):
        return hashlib.sha256(password.encode()).hexdigest()
    def pwd_context_verify(password, hash):
        return hashlib.sha256(password.encode()).hexdigest() == hash


@dataclass
class User:
    """用户数据模型"""
    id: str
    email: str
    api_key: str
    plan: str
    quota_used: int
    quota_limit: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    password_hash: Optional[str] = None
    email_verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        usage_pct = round(self.quota_used / self.quota_limit * 100, 2) if self.quota_limit > 0 else 0
        return {
            "id": self.id,
            "email": self.email,
            "api_key": f"{self.api_key[:8]}...{self.api_key[-8:]}",  # 部分隐藏
            "plan": self.plan,
            "quota_used": self.quota_used,
            "quota_limit": self.quota_limit,
            "quota_remaining": self.quota_limit - self.quota_used,
            "usage_percentage": usage_pct,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_full_dict(self) -> Dict[str, Any]:
        """转换为完整字典（包含完整API key）"""
        usage_pct = round(self.quota_used / self.quota_limit * 100, 2) if self.quota_limit > 0 else 0
        return {
            "id": self.id,
            "email": self.email,
            "api_key": self.api_key,  # 完整API key
            "plan": self.plan,
            "quota_used": self.quota_used,
            "quota_limit": self.quota_limit,
            "quota_remaining": self.quota_limit - self.quota_used,
            "usage_percentage": usage_pct,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class UserManager:
    """用户管理器"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
    
    def _get_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(self.database_url)
    
    def _generate_api_key(self) -> str:
        """生成随机API key"""
        # 生成32字节随机字符串，转十六进制得到64字符
        return secrets.token_hex(32)
    
    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        if PASSLIB_AVAILABLE:
            return pwd_context.hash(password)
        else:
            return pwd_context_hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        if not password_hash:
            return False
        if PASSLIB_AVAILABLE:
            return pwd_context.verify(password, password_hash)
        else:
            return pwd_context_verify(password, password_hash)
    
    def create_user(self, email: str, password: str, plan: str = "free") -> Optional[User]:
        """
        创建新用户
        
        Args:
            email: 用户邮箱
            password: 用户密码
            plan: 套餐类型 (free/pro/enterprise)
            
        Returns:
            User对象 或 None（如果邮箱已存在）
        """
        if not self._validate_email(email):
            raise ValueError("Invalid email format")
        
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        
        # 根据套餐设置额度
        quota_limits = {
            "free": 1000,
            "pro": 10000,
            "enterprise": 100000
        }
        quota_limit = quota_limits.get(plan, 1000)
        
        api_key = self._generate_api_key()
        password_hash = self._hash_password(password)
        
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 检查邮箱是否已存在
                cur.execute(
                    "SELECT id FROM users WHERE email = %s",
                    (email,)
                )
                if cur.fetchone():
                    return None  # 邮箱已存在
                
                # 创建用户
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, api_key, plan, quota_limit)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (email, password_hash, api_key, plan, quota_limit)
                )
                row = cur.fetchone()
                conn.commit()
                
                return User(
                    id=str(row['id']),
                    email=row['email'],
                    api_key=row['api_key'],
                    plan=row['plan'],
                    quota_used=row['quota_used'],
                    quota_limit=row['quota_limit'],
                    is_active=row['is_active'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    password_hash=row['password_hash'],
                    email_verified=row['email_verified']
                )
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """通过API key获取用户"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE api_key = %s AND is_active = TRUE",
                    (api_key,)
                )
                row = cur.fetchone()
                
                if not row:
                    return None
                
                return User(
                    id=str(row['id']),
                    email=row['email'],
                    api_key=row['api_key'],
                    plan=row['plan'],
                    quota_used=row['quota_used'],
                    quota_limit=row['quota_limit'],
                    is_active=row['is_active'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    password_hash=row.get('password_hash'),
                    email_verified=row.get('email_verified', False)
                )
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取用户"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM users WHERE email = %s",
                    (email,)
                )
                row = cur.fetchone()
                
                if not row:
                    return None
                
                return User(
                    id=str(row['id']),
                    email=row['email'],
                    api_key=row['api_key'],
                    plan=row['plan'],
                    quota_used=row['quota_used'],
                    quota_limit=row['quota_limit'],
                    is_active=row['is_active'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    password_hash=row.get('password_hash'),
                    email_verified=row.get('email_verified', False)
                )
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        验证用户邮箱和密码
        
        Returns:
            User对象 如果验证成功
            None 如果验证失败
        """
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not user.password_hash:
            return None
        
        if self.verify_password(password, user.password_hash):
            return user
        
        return None
    
    def regenerate_api_key(self, user_id: str) -> Optional[str]:
        """重新生成API key"""
        new_api_key = self._generate_api_key()
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET api_key = %s, updated_at = NOW() WHERE id = %s RETURNING api_key",
                    (new_api_key, user_id)
                )
                row = cur.fetchone()
                conn.commit()
                
                return row[0] if row else None
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_user(self, user_id: str) -> bool:
        """注销用户账户"""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # 先删除用量记录（外键关联）
                cur.execute(
                    "DELETE FROM usage_logs WHERE user_id = %s",
                    (user_id,)
                )
                
                # 删除用户
                cur.execute(
                    "DELETE FROM users WHERE id = %s",
                    (user_id,)
                )
                
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def increment_quota(self, api_key: str) -> bool:
        """
        增加用量计数
        
        Returns:
            True: 成功
            False: 超出额度
        """
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                # 检查额度
                cur.execute(
                    "SELECT quota_used, quota_limit FROM users WHERE api_key = %s",
                    (api_key,)
                )
                row = cur.fetchone()
                
                if not row:
                    return False
                
                quota_used, quota_limit = row
                
                if quota_used >= quota_limit:
                    return False  # 超出额度
                
                # 增加计数
                cur.execute(
                    "UPDATE users SET quota_used = quota_used + 1, updated_at = NOW() WHERE api_key = %s",
                    (api_key,)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def log_usage(self, api_key: str, endpoint: str, 
                  request_size: int = 0, response_size: int = 0,
                  processing_time_ms: int = 0):
        """记录用量日志"""
        # 先获取用户ID
        user = self.get_user_by_api_key(api_key)
        if not user:
            return
        
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO usage_logs (user_id, endpoint, request_size, response_size, processing_time_ms)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user.id, endpoint, request_size, response_size, processing_time_ms)
                )
                conn.commit()
        except Exception as e:
            conn.rollback()
            # 日志记录失败不影响主流程
            print(f"Failed to log usage: {e}")
        finally:
            conn.close()
    
    def get_usage_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """获取用量统计"""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 获取总用量
                cur.execute(
                    """
                    SELECT COUNT(*) as total_requests,
                           AVG(processing_time_ms) as avg_processing_time
                    FROM usage_logs
                    WHERE user_id = %s AND created_at > NOW() - INTERVAL '%s days'
                    """,
                    (user_id, days)
                )
                total_stats = cur.fetchone()
                
                # 按端点统计
                cur.execute(
                    """
                    SELECT endpoint, COUNT(*) as count
                    FROM usage_logs
                    WHERE user_id = %s AND created_at > NOW() - INTERVAL '%s days'
                    GROUP BY endpoint
                    ORDER BY count DESC
                    """,
                    (user_id, days)
                )
                endpoint_stats = cur.fetchall()
                
                # 按天统计
                cur.execute(
                    """
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM usage_logs
                    WHERE user_id = %s AND created_at > NOW() - INTERVAL '%s days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    """,
                    (user_id, days)
                )
                daily_stats = cur.fetchall()
                
                return {
                    "period_days": days,
                    "total_requests": total_stats['total_requests'] or 0,
                    "avg_processing_time_ms": round(total_stats['avg_processing_time'] or 0, 2),
                    "by_endpoint": [{"endpoint": row['endpoint'], "count": row['count']} for row in endpoint_stats],
                    "by_day": [{"date": row['date'].isoformat(), "count": row['count']} for row in daily_stats]
                }
        finally:
            conn.close()


# 全局用户管理器实例
_user_manager = None

def get_user_manager() -> UserManager:
    """获取用户管理器实例（单例）"""
    global _user_manager
    if _user_manager is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/warm_agent")
        _user_manager = UserManager(database_url)
    return _user_manager
