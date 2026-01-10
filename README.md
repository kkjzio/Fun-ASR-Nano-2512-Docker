# Fun-ASR-Nano-2512 Docker版部署指南

基于[Fun-ASR-Nano-2512-Deploy](https://github.com/fengin/Fun-ASR-Nano-2512-Deploy)项目的二次修改，本仓库适配Docker环境

## 目录结构

- `install.sh`: 环境安装脚本
- `Dockerfile`: 用于构建本地镜像使用
- `start_server.sh`: 启动 Fun-ASR WebSocket 服务脚本
- `start_server.sh.bak`: 原作者启动 Fun-ASR WebSocket 服务脚本备份
- `funasr_wss_server.py`: WebSocket 服务主程序
- `funasr_wss_server.py.bak`: 原作者WebSocket 服务主程序备份
- `download_model.py`: 模型下载脚本（安装时下载模型）
- `download_model.py.bak`: 原作者模型下载脚本（安装时下载模型）备份
- `test_inference.py`: 本地推理测试脚本（验证环境）
- `funasr_wss_client.py`: 测试客户端（验证部署是否OK）
- `web_client`: Web 测试客户端目录，方便WEB页面测试（未实现VAD检测，仅用于测试流式识别）

## 部署步骤

在构建本项目前，请确认您已安装`NVIDIA Container Toolkit`

### 1.本地构建镜像

```bash
docker build -t fun-asr-nano-2512:latest .
```

### 2.运行容器

```bash
docker run -d --name=fun-asr-nano --restart=unless-stopped -p 10096:10096 -e PYTHONUNBUFFERED=1 --gpus=all fun-asr-nano-2512:latest
```

### 3.检查容器启动

```bash
docker logs <容器ID/fun-asr-nano>
```

## 客户端连接

Java 客户端或测试脚本可以通过 WebSocket 连接：

- URL: `ws://<SERVER_IP>:10096`
- 协议: FunASR 协议

## 显存优化说明

- 暂无 (FP16 模式目前在部分环境下存在兼容性问题，暂不推荐开启)

## WebSocket 接口文档

服务端提供基于 WebSocket 的实时语音识别服务，完全兼容 FunASR 客户端协议。

### 1. 连接地址

- **URL**: `ws://<SERVER_IP>:10095`
- **协议**: WebSocket (Binary Frames)

### 2. 通信流程

整个识别过程包含三个阶段：**握手配置 -> 音频流传输 -> 结果接收**。

#### a. 握手配置 (First Message)

建立连接后，客户端发送的**第一帧**必须是 JSON 格式的配置信息：

```json
{
  "mode": "2pass",                   // 推荐使用 2pass (流式+离线修正) 或 online
  "chunk_size": [5, 10, 5],          // 分块大小配置 [编码器历史, 当前块, 编码器未来]
  "chunk_interval": 10,              // 发送间隔 (ms)
  "encoder_chunk_look_back": 4,      // 编码器回溯步数
  "decoder_chunk_look_back": 1,      // 解码器回溯步数
  "audio_fs": 16000,                 // 音频采样率 (必须是 16000)
  "wav_name": "demo",                // 音频标识
  "is_speaking": true,               // 标记开始说话
  "hotwords": "{\"阿里巴巴\": 20, \"达摩院\": 30}", // 热词配置 (可选)
  "itn": true                        // 开启逆文本标准化 (数字转汉字等)
}
```

> **自动兼容**: 如果客户端请求 `mode: "online"`，服务端会自动将其升级为 `mode: "2pass"`，以确保在流式结束后能触发离线修正并返回最终结果（防止部分客户端死等 is_final: true）。

#### b. 音频流传输 (Streaming)

- 配置帧发送后，客户端持续发送**二进制音频数据 (Binary Frame)**。
- 格式：PCM, 16000Hz, 16bit, 单声道。
- 建议分块发送，每块大小约 60ms - 100ms 的数据。

#### c. 结束信号 (End of Stream)

- 当用户停止说话时，客户端发送一帧 JSON 结束信号：
  
  ```json
  {"is_speaking": false}
  ```

### 3. 服务端响应格式

服务端会通过 WebSocket 持续返回 JSON 格式的识别结果。

#### 流式中间结果 (Variable)

当 `mode="online"` 或 `mode="2pass"` 时，服务端会实时返回当前识别片段：

```json
{
  "mode": "2pass-online",
  "text": "正在识别的内容",
  "wav_name": "demo",
  "is_final": false // 通常为 false，但当检测到语音结束(is_speaking: false)时的最后一帧可能为 true
}
```

#### 最终结果 (Final)

当一句话结束 (VAD 检测到静音) 或收到 `is_speaking: false` 后，服务端会进行离线修正，并返回最终结果：

```json
{
  "mode": "2pass-offline",
  "text": "最终识别的修正结果。",
  "wav_name": "demo",
  "is_final": true
}
```

> **注意**: 
> 
> 1. 为了防止客户端超时，即使离线识别结果为空（如误触 VAD），服务端也会发送一个 `text: ""` 且 `is_final: true` 的空包。
> 2. Java 客户端通常只处理 `is_final: true` 的消息。

## 作者信息

- **作者**：凌封
- **来源**：[https://aibook.ren (AI全书)](https://aibook.ren)
- **二次修改**：[网笙久久](https://www.wsjj.top)
