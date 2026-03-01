export CORS_ORIGINS=https://example.com
export SENTRY_DSN=your_sentry_dsn
export PROMETHEUS_MULTIPROC_DIR=/tmp
```

### 2. 配置文件

```yaml
# config/production.yaml
database:
  url: ${DATABASE_URL}
  pool_size: 20
  max_overflow: 10
  echo: false

redis:
  url: ${REDIS_URL}
  pool_size: 10
  decode_responses: true

api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  reload: false
  access_log: true

security:
  api_key_secret: ${API_KEY_SECRET}
  cors_origins: ${CORS_ORIGINS:-*}
  rate_limit: 100/分钟

cache:
  enabled: true
  ttl: 300  # 5分钟
  max_size: 1000

monitoring:
  enabled: true
  prometheus_port: 9090
  health_check_interval: 30

logging:
  level: ${LOG_LEVEL:-INFO}
  format: json
  file: /var/log/warm-agent/api.log
```

### 3. 密钥管理

#### 使用 HashiCorp Vault

```python
# vault_integration.py
import hvac
import os

class VaultConfigManager:
    """Vault配置管理器"""
    
    def __init__(self, vault_url: str, token: str):
        self.client = hvac.Client(url=vault_url, token=token)
    
    def get_secret(self, path: str) -> Dict:
        """获取密钥"""
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response['data']['data']
    
    def load_config_from_vault(self) -> Dict:
        """从Vault加载配置"""
        secrets = self.get_secret('warm-agent/config')
        
        config = {
            'database': {
                'url': secrets['database_url'],
                'pool_size': int(secrets.get('database_pool_size', 20))
            },
            'redis': {
                'url': secrets['redis_url']
            },
            'security': {
                'api_key_secret': secrets['api_key_secret']
            }
        }
        
        return config
```

#### 使用 AWS Secrets Manager

```python
# aws_secrets.py
import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_name: str, region_name: str = "us-east-1") -> Dict:
    """从AWS Secrets Manager获取密钥"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        
        if 'SecretString' in response:
            secret = response['SecretString']
            return json.loads(secret)
        else:
            decoded_binary_secret = base64.b64decode(
                response['SecretBinary']
            )
            return json.loads(decoded_binary_secret)
    
    except ClientError as e:
        raise Exception(f"获取密钥失败: {e}")
```

## 监控和告警

### 1. Prometheus 配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'warm-agent-api'
    static_configs:
      - targets: ['warm-agent-api:8000']
    metrics_path: /metrics
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
      
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 2. Grafana 仪表板

```json
// monitoring/grafana/dashboard.json
{
  "dashboard": {
    "title": "Warm Agent 监控",
    "panels": [
      {
        "title": "API请求率",
        "targets": [
          {
            "expr": "rate(warm_agent_api_requests_total[5m])",
            "legendFormat": "{{endpoint}}"
          }
        ]
      },
      {
        "title": "API响应时间",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(warm_agent_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95 - {{endpoint}}"
          }
        ]
      },
      {
        "title": "情感分析分布",
        "targets": [
          {
            "expr": "sum by (emotion) (warm_agent_emotion_analysis_total)",
            "legendFormat": "{{emotion}}"
          }
        ]
      }
    ]
  }
}
```

### 3. 告警规则

```yaml
# monitoring/alerts.yml
groups:
  - name: warm-agent-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(warm_agent_api_requests_total{status=~"5.."}[5m]) / rate(warm_agent_api_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高错误率检测"
          description: "API错误率超过5%"
          
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(warm_agent_request_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "高延迟检测"
          description: "95%分位响应时间超过2秒"
          
      - alert: DatabaseConnectionError
        expr: up{job="postgres"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "数据库连接失败"
          description: "PostgreSQL服务不可用"
```

## 备份和恢复

### 1. 数据库备份

```bash
#!/bin/bash
# backup.sh

# 设置变量
BACKUP_DIR="/backups/warm-agent"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="warm_agent"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U postgres -h localhost -d $DB_NAME \
  -F c -b -v -f $BACKUP_DIR/${DB_NAME}_${DATE}.dump

# 备份Redis
redis-cli --rdb $BACKUP_DIR/redis_${DATE}.rdb

# 压缩备份
tar -czf $BACKUP_DIR/backup_${DATE}.tar.gz \
  $BACKUP_DIR/${DB_NAME}_${DATE}.dump \
  $BACKUP_DIR/redis_${DATE}.rdb

# 清理旧备份（保留最近7天）
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

# 上传到云存储（可选）
# aws s3 cp $BACKUP_DIR/backup_${DATE}.tar.gz s3://your-bucket/backups/
```

### 2. 数据库恢复

```bash
#!/bin/bash
# restore.sh

# 设置变量
BACKUP_FILE="/backups/warm-agent/backup_20240228_120000.tar.gz"
DB_NAME="warm_agent"

# 解压备份
tar -xzf $BACKUP_FILE -C /tmp

# 停止应用服务
systemctl stop warm-agent-api
systemctl stop warm-agent-worker

# 恢复数据库
pg_restore -U postgres -h localhost -d $DB_NAME \
  --clean --if-exists \
  /tmp/${DB_NAME}_20240228_120000.dump

# 恢复Redis
redis-cli flushall
cat /tmp/redis_20240228_120000.rdb | redis-cli --pipe

# 启动应用服务
systemctl start warm-agent-api
systemctl start warm-agent-worker

# 清理临时文件
rm -rf /tmp/${DB_NAME}_*.dump /tmp/redis_*.rdb
```

### 3. 自动备份配置

```yaml
# backup/cron.yaml
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: warm-agent-backup
  namespace: warm-agent
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - /bin/sh
            - -c
            - |
              # 备份脚本
              pg_dump -U $POSTGRES_USER -h $POSTGRES_HOST \
                -d $POSTGRES_DB -F c -f /backup/backup.dump
              
              # 上传到S3
              aws s3 cp /backup/backup.dump s3://$S3_BUCKET/backups/$(date +%Y%m%d).dump
            env:
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: warm-agent-secrets
                  key: database-user
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: warm-agent-secrets
                  key: database-password
            - name: POSTGRES_HOST
              value: postgres
            - name: POSTGRES_DB
              value: warm_agent
            - name: S3_BUCKET
              value: your-backup-bucket
            volumeMounts:
            - name: backup-volume
              mountPath: /backup
          restartPolicy: OnFailure
          volumes:
          - name: backup-volume
            emptyDir: {}
```

## 安全配置

### 1. 网络安全

```yaml
# k8s/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: warm-agent-network-policy
  namespace: warm-agent
spec:
  podSelector:
    matchLabels:
      app: warm-agent-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### 2. TLS/SSL 配置

```nginx
# nginx/ssl.conf
server {
    listen 443 ssl http2;
    server_name api.warm-agent.example.com;
    
    ssl_certificate /etc/nginx/ssl/warm-agent.crt;
    ssl_certificate_key /etc/nginx/ssl/warm-agent.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    location / {
        proxy_pass http://warm-agent-api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. 身份验证和授权

```python
# security/middleware.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import time

security = HTTPBearer()

class AuthMiddleware:
    """认证中间件"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    async def __call__(self, request: Request, call_next):
        # 跳过健康检查
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # 验证API Key
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="缺少认证信息")
        
        try:
            # 提取Bearer token
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="无效的认证方案")
            
            # 验证token
            payload = self.verify_token(token)
            
            # 检查权限
            if not self.has_permission(payload, request):
                raise HTTPException(status_code=403, detail="权限不足")
            
            # 将用户信息添加到请求
            request.state.user = payload
            
            return await call_next(request)
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token已过期")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="无效的Token")
    
    def verify_token(self, token: str) -> Dict:
        """验证JWT token"""
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=["HS256"]
        )
    
    def has_permission(self, payload: Dict, request: Request) -> bool:
        """检查权限"""
        user_role = payload.get("role", "user")
        endpoint = request.url.path
        
        # 权限检查逻辑
        if user_role == "admin":
            return True
        
        if user_role == "user":
            # 用户只能访问特定端点
            allowed_endpoints = [
                "/v1/emotion/analyze",
                "/v1/warm-response/generate"
            ]
            return endpoint in allowed_endpoints
        
        return False
```

## 性能优化

### 1. 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_emotion_records_user_timestamp 
ON emotion_records(user_id, timestamp DESC);

CREATE INDEX idx_api_calls_user_endpoint 
ON api_calls(user_id, endpoint, created_at DESC);

-- 分区表
CREATE TABLE emotion_records_2024_02 PARTITION OF emotion_records
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 物化视图
CREATE MATERIALIZED VIEW emotion_summary_daily AS
SELECT 
    user_id,
    DATE(timestamp) as date,
    COUNT(*) as total_interactions,
    AVG(intensity) as avg_intensity
FROM emotion_records
GROUP BY user_id, DATE(timestamp);
```

### 2. 缓存优化

```python
# cache/redis_cache.py
import redis
import json
from functools import wraps
import hashlib

class RedisCache:
    """Redis缓存管理器"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 300  # 5分钟
    
    def cache(self, ttl: int = None):
        """缓存装饰器"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_key(func, args, kwargs)
                
                # 尝试从缓存获取
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
                
                # 执行函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                self.redis.setex(
                    cache_key,
                    ttl or self.default_ttl,
                    json.dumps(result)
                )
                
                return result
            return wrapper
        return decorator
    
    def _generate_key(self, func, args, kwargs) -> str:
        """生成缓存键"""
        key_parts = [
            func.__module__,
            func.__name__,
            str(args),
            str(sorted(kwargs.items()))
        ]
        
        key_string = ":".join(key_parts)
        return f"cache:{hashlib.md5(key_string.encode()).hexdigest()}"
```

### 3. 异步处理

```python
# tasks/async_processor.py
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

class AsyncProcessor:
    """异步处理器"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_batch(self, items: List[Dict]) -> List[Dict]:
        """批量处理"""
        tasks = [
            self._process_item_async(item)
            for item in items
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed.append({
                    "item": items[i],
                    "result": None,
                    "error": str(result)
                })
            else:
                processed.append({
                    "item": items[i],
                    "result": result,
                    "error": None
                })
        
        return processed
    
    async def _process_item_async(self, item: Dict):
        """异步处理单个项目"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._process_item_sync,
            item
        )
    
    def _process_item_sync(self, item: Dict):
        """同步处理单个项目"""
        # 这里执行CPU密集型操作
        # 例如：情感分析、文本处理等
