#!/bin/bash

echo "🚀 Warm Agent 服务状态检查"
echo "=========================="
echo "检查时间: $(date)"
echo ""

# 检查Docker服务
echo "🔧 Docker服务状态:"
if systemctl is-active --quiet docker; then
    echo "✅ Docker服务运行中"
else
    echo "❌ Docker服务未运行"
fi

echo ""

# 检查容器状态
echo "🐳 容器状态:"
docker-compose ps 2>/dev/null || echo "⚠️  docker-compose命令不可用"

echo ""

# 检查端口占用
echo "🔌 端口占用情况:"
echo "端口 5432 (PostgreSQL):"
if netstat -tlnp 2>/dev/null | grep :5432 > /dev/null; then
    echo "✅ 端口5432被占用 (PostgreSQL)"
else
    echo "❌ 端口5432未被占用"
fi

echo "端口 6379 (Redis):"
if netstat -tlnp 2>/dev/null | grep :6379 > /dev/null; then
    echo "✅ 端口6379被占用 (Redis)"
else
    echo "❌ 端口6379未被占用"
fi

echo "端口 8000 (API):"
if netstat -tlnp 2>/dev/null | grep :8000 > /dev/null; then
    echo "✅ 端口8000被占用 (API服务)"
else
    echo "❌ 端口8000未被占用 (API服务未启动)"
fi

echo ""

# 检查数据库连接
echo "🗄️ 数据库连接测试:"
echo "PostgreSQL连接测试..."
if docker-compose exec -T postgres psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL连接成功"
else
    echo "❌ PostgreSQL连接失败"
fi

echo "Redis连接测试..."
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis连接成功"
else
    echo "❌ Redis连接失败"
fi

echo ""

# 检查磁盘空间
echo "💾 磁盘空间:"
df -h / | tail -1

echo ""

# 检查内存使用
echo "🧠 内存使用:"
free -h | head -2

echo ""
echo "📊 总结:"
echo "1. Docker服务: $(systemctl is-active --quiet docker && echo '✅' || echo '❌')"
echo "2. PostgreSQL: $(docker-compose exec -T postgres psql -U postgres -c 'SELECT 1;' > /dev/null 2>&1 && echo '✅' || echo '❌')"
echo "3. Redis: $(docker-compose exec -T redis redis-cli ping | grep -q PONG && echo '✅' || echo '❌')"
echo "4. API服务: $(netstat -tlnp 2>/dev/null | grep :8000 > /dev/null && echo '✅' || echo '❌')"
echo ""
echo "🎯 建议:"
if systemctl is-active --quiet docker && \
   docker-compose exec -T postgres psql -U postgres -c "SELECT 1;" > /dev/null 2>&1 && \
   docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ 基础服务正常，等待API构建完成"
else
    echo "⚠️  部分服务异常，请检查日志"
fi