# Warm Agent Dockerfile
# 多阶段构建：开发和生产环境

# ==================== 基础镜像 ====================
FROM python:3.11-slim as base

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# ==================== 开发环境 ====================
FROM base as development

# 复制依赖文件
COPY requirements.txt requirements-dev.txt ./

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt -r requirements-dev.txt

# 复制源代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 8000

# 开发环境启动命令
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ==================== 生产环境构建阶段 ====================
FROM base as builder

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt


# ==================== 生产环境运行阶段 ====================
FROM python:3.11-slim as production

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# 复制源代码
COPY --chown=appuser:appuser . .

USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 生产环境启动命令
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]


# ==================== Celery Worker ====================
FROM production as celery-worker

# Celery worker启动命令
CMD ["celery", "-A", "src.tasks.celery_app", "worker", "--loglevel=info"]


# ==================== Celery Beat ====================
FROM production as celery-beat

# Celery beat启动命令
CMD ["celery", "-A", "src.tasks.celery_app", "beat", "--loglevel=info"]


# ==================== 测试环境 ====================
FROM development as test

# 安装测试依赖
RUN pip install pytest pytest-cov pytest-asyncio

# 设置测试环境变量
ENV TESTING=1 \
    DATABASE_URL=sqlite:///:memory: \
    REDIS_URL=redis://localhost:6379/0

# 运行测试
CMD ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"]