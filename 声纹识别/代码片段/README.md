# WavLM 代码片段目录

本目录包含了 WavLM 项目的完整代码示例，涵盖语音识别、声纹识别、音频处理等核心功能。

## 📁 目录结构

```
代码片段/
├── README.md                        # 本说明文档
├── requirements.txt                 # 依赖包列表
├── demo_script.py                   # 完整演示脚本
├── run_demo.py                      # 快速运行演示
├── sample_data_generator.py          # 示例数据生成器
├── wavlm_asr.py                     # 语音识别示例
├── wavlm_speaker_recognition.py      # 声纹识别示例
├── wavlm_audio_processing.py        # 音频处理工具
└── wavlm_finetuning.py              # 微调示例
```

## 🚀 快速开始

### 1. 安装依赖
```bash
# 安装基础依赖
pip install -r requirements.txt

# 或手动安装
pip install torch torchaudio transformers
pip install librosa soundfile numpy scikit-learn
pip install matplotlib seaborn
```

### 2. 运行快速演示
```bash
# 一键运行完整演示
python run_demo.py
```

### 3. 运行单独示例
```bash
# 语音识别
python wavlm_asr.py --audio sample.wav --output result.txt

# 声纹识别
python wavlm_speaker_recognition.py --audio1 speaker1.wav --audio2 speaker2.wav --action verify

# 音频处理
python wavlm_audio_processing.py --input audio.wav --output processed.wav --operation normalize

# 微调
python wavlm_finetuning.py --audio_dir data/audio --text_dir data/text --output_dir model --action train
```

## 📊 代码示例说明

### 1. `demo_script.py` - 完整演示脚本
- **功能**: 完整的 WavLM 功能演示
- **特点**: 包含语音识别、声纹识别、音频分析、性能测试
- **用途**: 了解 WavLM 的完整功能

### 2. `run_demo.py` - 快速运行演示
- **功能**: 一键式快速演示
- **特点**: 自动生成示例数据，运行所有功能
- **用途**: 快速体验 WavLM

### 3. `wavlm_asr.py` - 语音识别
- **功能**: 语音转文字
- **特点**: 支持单文件和批量处理
- **用途**: 实际项目中的语音识别任务

### 4. `wavlm_speaker_recognition.py` - 声纹识别
- **功能**: 说话人身份识别和验证
- **特点**: 支持注册、识别、相似度计算
- **用途**: 安全验证、身份识别

### 5. `wavlm_audio_processing.py` - 音频处理
- **功能**: 音频预处理和增强
- **特点**: 包含重采样、去噪、VAD、数据增强
- **用途**: 音频数据预处理

### 6. `wavlm_finetuning.py` - 微调示例
- **功能**: 模型微调
- **特点**: 支持自定义数据集训练
- **用途**: 领域自适应

### 7. `sample_data_generator.py` - 示例数据生成
- **功能**: 生成测试数据
- **特点**: 生成语音、噪声、混合信号
- **用途**: 测试和演示

## 🎯 使用指南

### 环境准备
```bash
# 检查 CUDA 支持
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# 下载预训练模型（首次运行时自动下载）
from transformers import WavLMProcessor, WavLMModel
```

### 数据格式要求
- **音频文件**: WAV、MP3 格式
- **采样率**: 推荐 16kHz
- **声道**: 单声道
- **文本文件**: UTF-8 编码

### 性能优化建议
```python
# 使用 GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 批处理
def batch_inference(audio_files):
    results = []
    for batch in chunk(audio_files, batch_size=8):
        # 批量处理
        results.extend(process_batch(batch))
    return results

# 模型量化
model = torch.quantization.quantize_dynamic(model, {nn.Linear}, dtype=torch.qint8)
```

## 🔧 故障排除

### 常见问题

#### 1. 模型下载失败
```bash
# 手动下载模型
from transformers import WavLMProcessor, WavLMModel
processor = WavLMProcessor.from_pretrained("microsoft/wavlm-base")
model = WavLMModel.from_pretrained("microsoft/wavlm-base")
```

#### 2. 内存不足
```python
# 使用梯度检查点
from torch.utils.checkpoint import checkpoint

def memory_efficient_forward(x):
    return checkpoint(model.forward, x)
```

#### 3. 音频格式问题
```python
# 音频格式转换
import torchaudio.transforms as T

resampler = T.Resample(old_rate, new_rate)
waveform = resampler(waveform)
```

### 调试技巧
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查输入形状
print(f"Input shape: {inputs.input_values.shape}")

# 监控内存
import psutil
print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024} MB")
```

## 📈 性能监控

### 推理性能
```python
import time

start_time = time.time()
# 推理代码
inference_time = time.time() - start_time
print(f"Inference time: {inference_time:.3f}s")
print(f"FPS: {1/inference_time:.2f}")
```

### 内存使用
```python
import torch
import psutil

def get_memory_usage():
    memory = psutil.Process().memory_info()
    return memory.rss / 1024 / 1024  # MB

print(f"Memory usage: {get_memory_usage():.2f} MB")
```

## 🚀 进阶应用

### 企业级部署
```python
# 模型导出
from transformers import WavLMForCTC
import torch

model = WavLMForCTC.from_pretrained("microsoft/wavlm-base")
torch.save(model.state_dict(), "wavlm_model.pth")
```

### API 服务化
```python
from fastapi import FastAPI
import torch

app = FastAPI()

@app.post("/asr")
async def transcribe_audio(audio_file):
    # 语音识别逻辑
    return {"transcription": result}
```

### 边缘设备部署
```python
# 模型量化
quantized_model = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)

# ONNX 导出
torch.onnx.export(model, input, "model.onnx")
```

## 📚 学习资源

### 官方文档
- [Hugging Face 文档](https://huggingface.co/docs/transformers/model_doc/wavlm)
- [PyTorch 文档](https://pytorch.org/docs/)
- [Torchaudio 文档](https://pytorch.org/audio/stable/index.html)

### 示例和教程
- 本目录中的所有代码示例
- [WavLM 论文](https://arxiv.org/abs/2109.01159)
- [Microsoft Research 官网](https://www.microsoft.com/en-us/research/)

### 社区支持
- [GitHub Issues](https://github.com/microsoft/unilm/issues)
- [Hugging Face 论坛](https://discuss.huggingface.co/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/wavlm)

## 📄 许可证

本代码示例遵循 MIT 许可证。原始 WavLM 模型遵循其原始许可证。

---

**提示**: 建议先运行 `run_demo.py` 快速体验，然后根据具体需求选择相应的代码示例进行学习和使用。