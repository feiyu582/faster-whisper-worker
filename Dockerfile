# 使用 RunPod 官方推荐的 PyTorch 镜像（支持 CUDA 12.1）
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_PREFER_BINARY=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
  && pip install --no-cache-dir -r requirements.txt

# 复制处理程序和启动脚本
COPY handler.py .
COPY start.sh .
COPY test_input.json .
RUN chmod +x start.sh

CMD ["./start.sh"]
