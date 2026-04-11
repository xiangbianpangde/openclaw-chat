#!/bin/bash
# 开发环境启动验证脚本

set -e

echo "=========================================="
echo "  泰迪杯 B 题 - 开发环境启动验证"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
echo "📦 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 已安装：$(docker --version)${NC}"

# 检查 Docker Compose
echo "📦 检查 Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose 已安装：$(docker-compose --version)${NC}"

# 检查 Python
echo "🐍 检查 Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 已安装：$(python3 --version)${NC}"

# 检查项目文件
echo "📁 检查项目文件..."
REQUIRED_FILES=(
    "docker-compose.yml"
    "Dockerfile"
    "requirements.txt"
    "src/api/main.py"
    "config/settings.py"
    "scripts/init_mysql.sql"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✅ $file${NC}"
    else
        echo -e "${RED}  ❌ $file 缺失${NC}"
        exit 1
    fi
done

# 创建必要目录
echo "📁 创建必要目录..."
mkdir -p logs data/raw data/processed data/models
touch logs/.gitkeep data/raw/.gitkeep data/processed/.gitkeep data/models/.gitkeep
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 检查端口占用
echo "🔌 检查端口占用..."
PORTS=(8000 3306 6379 9000 9001 9090 3000 9200 5601)
for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}  ⚠️  端口 $port 已被占用${NC}"
    else
        echo -e "${GREEN}  ✅ 端口 $port 可用${NC}"
    fi
done

# 创建 .env 文件
echo "⚙️  创建环境配置..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env 文件已创建${NC}"
else
    echo -e "${YELLOW}⚠️  .env 文件已存在，跳过${NC}"
fi

echo ""
echo "=========================================="
echo "  启动服务"
echo "=========================================="
echo ""

# 询问是否启动服务
read -p "是否启动 Docker Compose 服务？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 启动服务..."
    docker-compose up -d
    
    echo ""
    echo "等待服务启动..."
    sleep 10
    
    echo ""
    echo "=========================================="
    echo "  服务健康检查"
    echo "=========================================="
    
    # 检查 API 服务
    echo "🔍 检查 API 服务..."
    if curl -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API 服务正常 (http://localhost:8000)${NC}"
    else
        echo -e "${YELLOW}⚠️  API 服务未响应，可能需要更多启动时间${NC}"
    fi
    
    # 检查 MySQL
    echo "🔍 检查 MySQL 服务..."
    if docker-compose ps mysql | grep -q "Up"; then
        echo -e "${GREEN}✅ MySQL 服务正常 (localhost:3306)${NC}"
    else
        echo -e "${YELLOW}⚠️  MySQL 服务未正常启动${NC}"
    fi
    
    # 检查 Redis
    echo "🔍 检查 Redis 服务..."
    if docker-compose ps redis | grep -q "Up"; then
        echo -e "${GREEN}✅ Redis 服务正常 (localhost:6379)${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis 服务未正常启动${NC}"
    fi
    
    # 检查 MinIO
    echo "🔍 检查 MinIO 服务..."
    if docker-compose ps minio | grep -q "Up"; then
        echo -e "${GREEN}✅ MinIO 服务正常 (http://localhost:9000, 控制台：http://localhost:9001)${NC}"
    else
        echo -e "${YELLOW}⚠️  MinIO 服务未正常启动${NC}"
    fi
    
    echo ""
    echo "=========================================="
    echo "  服务访问地址"
    echo "=========================================="
    echo ""
    echo "📡 API 文档：   http://localhost:8000/docs"
    echo "📊 Grafana:    http://localhost:3000 (admin/caiwu123)"
    echo "💾 MinIO:      http://localhost:9001 (caiwu/caiwu123456)"
    echo "📈 Prometheus: http://localhost:9090"
    echo "📝 Kibana:     http://localhost:5601"
    echo ""
    echo "=========================================="
    echo "  运行测试"
    echo "=========================================="
    echo ""
    
    read -p "是否运行单元测试？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🧪 运行单元测试..."
        pip install -q pytest pytest-cov
        pytest tests/ -v --cov=src --cov-report=term-missing
    fi
fi

echo ""
echo "=========================================="
echo "  验证完成"
echo "=========================================="
echo ""
echo -e "${GREEN}✅ 阶段一基础架构搭建完成！${NC}"
echo ""
echo "下一步："
echo "  1. 完善 PDF 解析引擎（阶段二）"
echo "  2. 开发 NL2SQL 引擎（阶段三）"
echo "  3. 实现 RAG 增强（阶段四）"
echo ""
echo "查看执行日志：cat EXECUTION_LOG.md"
echo "查看技术文档：docs/"
echo ""
