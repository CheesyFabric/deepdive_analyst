# DeepDive Analyst Dockerfile
# 基于 Python 3.13 官方镜像
FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 设置 Python 模块搜索路径
ENV PYTHONPATH=/app  
# 禁用 Python 缓冲
ENV PYTHONUNBUFFERED=1  
# 禁用 .pyc 文件生成 避免在容器中生成 Python 字节码文件
ENV PYTHONDONTWRITEBYTECODE=1  

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY main.py .
COPY src/ ./src/
COPY examples/ ./examples/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# 安装 Python 依赖 先升级 pip 到最新版本
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 创建非 root 用户
# 安全意义：后续所有命令都以 deepdive 用户身份执行，即使容器被攻击，攻击者也只能获得普通用户权限
RUN useradd --create-home --shell /bin/bash deepdive && \
    chown -R deepdive:deepdive /app

# 切换到非 root 用户
USER deepdive

# 设置默认命令
CMD ["python", "main.py", "--help"]

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python main.py version || exit 1

# 暴露端口（如果需要 Web 服务）
EXPOSE 8000

# 标签信息
LABEL maintainer="DeepDive Analyst"
LABEL description="AI技术专家调研与分析智能体"
LABEL version="1.0.0"
