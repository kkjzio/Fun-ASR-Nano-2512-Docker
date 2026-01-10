import os
import shutil
"""
Download FunASR Models
作者：凌封
来源：https://aibook.ren (AI全书)
二次更改：网笙久久(适配容器环境)
"""
from modelscope import snapshot_download

# 配置 - 统一使用 /app/models 作为模型存储目录
MODELS_ROOT = '/app/models'
FUNASR_MODEL_ID = 'FunAudioLLM/Fun-ASR-Nano-2512'
QWEN_MODEL_ID = 'Qwen/Qwen3-0.6B'
VAD_MODEL_ID = 'iic/speech_fsmn_vad_zh-cn-16k-common-pytorch'
PUNC_MODEL_ID = 'iic/punc_ct-transformer_zh-cn-common-vad_realtime-vocab272727'

def download_and_setup_models():
    if not os.path.exists(MODELS_ROOT):
        os.makedirs(MODELS_ROOT)

    print(f"=== 开始下载模型 ===")
    print(f"本地保存目录: {MODELS_ROOT}")

    # 1. 下载 Fun-ASR-Nano-2512
    print(f"\n[1/4] 正在下载主模型: {FUNASR_MODEL_ID}")
    try:
        funasr_dir = snapshot_download(FUNASR_MODEL_ID, cache_dir=MODELS_ROOT)
        print(f"主模型已就绪: {funasr_dir}")
    except Exception as e:
        print(f"[失败] 主模型下载出错: {e}")
        return

    # 2. 下载并配置 Qwen3-0.6B 子模块
    # FunASR 代码期望 Qwen3 位于 Fun-ASR-Nano-2512/Qwen3-0.6B 目录下
    qwen_target_dir = os.path.join(funasr_dir, 'Qwen3-0.6B')
    
    print(f"\n[2/4] 正在配置子模块: {QWEN_MODEL_ID}")
    print(f"目标子目录: {qwen_target_dir}")

    try:
        # 下载 Qwen3 到缓存
        print(f"正在下载 Qwen3 模型...")
        qwen_temp_dir = snapshot_download(QWEN_MODEL_ID, cache_dir=MODELS_ROOT)
        
        # 检查是否需要复制/更新
        # 如果目标目录不存在，或者为空，则进行复制
        if os.path.exists(qwen_target_dir):
            print("检测到目标子目录已存在，清理旧文件以确保完整性...")
            shutil.rmtree(qwen_target_dir)
        
        print(f"正在复制文件到子目录...")
        shutil.copytree(qwen_temp_dir, qwen_target_dir)
        print(f"子模块配置完成！")

    except Exception as e:
        print(f"[失败] 子模块配置出错: {e}")
        return

    # 3. 下载 VAD 模型
    print(f"\n[3/4] 正在下载 VAD 模型: {VAD_MODEL_ID}")
    try:
        vad_dir = snapshot_download(VAD_MODEL_ID, cache_dir=MODELS_ROOT)
        print(f"VAD 模型已就绪: {vad_dir}")
    except Exception as e:
        print(f"[失败] VAD 模型下载出错: {e}")
        return

    # 4. 下载 PUNC 模型
    print(f"\n[4/4] 正在下载 PUNC 模型: {PUNC_MODEL_ID}")
    try:
        punc_dir = snapshot_download(PUNC_MODEL_ID, cache_dir=MODELS_ROOT)
        print(f"PUNC 模型已就绪: {punc_dir}")
    except Exception as e:
        print(f"[失败] PUNC 模型下载出错: {e}")
        return

    print(f"\n=== 所有模型下载与配置完成 ===")
    print(f"主模型路径: {funasr_dir}")
    print(f"VAD模型路径: {vad_dir}")
    print(f"PUNC模型路径: {punc_dir}")
    print(f"Qwen子模块路径: {qwen_target_dir}")

if __name__ == '__main__':
    download_and_setup_models()




