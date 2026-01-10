# Fun-ASR-Nano-2512 Dockerfile
# 作者：网笙久久
# 来源：https://www.wsjj.top

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# 设置环境变量
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 更换清华大学加速源
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list && \
    sed -i 's@//.*security.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装 Python 依赖（使用真实环境，不使用虚拟环境）
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    torch torchaudio \
    funasr \
    websockets \
    numpy \
    modelscope \
    transformers \
    sentencepiece \
    protobuf \
    tqdm \
    requests \
    aiohttp

# 预下载模型到 /app/models 目录
RUN python3 download_model.py

# 暴露端口
EXPOSE 10096

# 启动服务
CMD ["/bin/bash", "./start_server.sh"]
