#!/bin/bash
# 作者：凌封
# 来源：https://aibook.ren (AI全书)
# 二次更改：网笙久久

# 设置启动后其他依赖的模型下载缓存目录，不设置默认会下载到这个目录：/root/.cache/modelscope
#export MODELSCOPE_CACHE=/your/custom/path

set -e

# 应用程序目录下的模型路径
APP_MODELS_DIR="/app/models"
MODEL_PATH="$APP_MODELS_DIR/FunAudioLLM/Fun-ASR-Nano-2512"
QWEN_SUBMODEL_PATH="$MODEL_PATH/FunAudioLLM/Fun-ASR-Nano-2512/Qwen3-0.6B"
VAD_MODEL_PATH="$APP_MODELS_DIR/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"
PUNC_MODEL_PATH="$APP_MODELS_DIR/iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727"


echo "=== 启动 FunASR WebSocket 服务 ==="
echo "主模型路径: $MODEL_PATH"
echo "Qwen子模型路径: $QWEN_SUBMODEL_PATH"
echo "VAD模型路径: $VAD_MODEL_PATH"
echo "PUNC模型路径: $PUNC_MODEL_PATH"
echo "端口: 10096"
echo "模式: online (流式)"

# 启动服务
python3 funasr_wss_server.py \
  --port 10096 \
  --asr_model_online "$MODEL_PATH" \
  --asr_model "$MODEL_PATH" \
  --vad_model "$VAD_MODEL_PATH" \
  --punc_model "$PUNC_MODEL_PATH" \
  --device cuda

# 注意：如果需要 HTTPS/WSS，请配置 --certfile 和 --keyfile 指向有效的 SSL 证书
