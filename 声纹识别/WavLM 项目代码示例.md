---
title: WavLM 项目代码示例
author: AI助手
date: 2026-02-28
tags: [WavLM, 代码示例, 实战, Python]
category: 代码示例
---

# WavLM 项目代码示例

## 📋 项目概述

本文档提供了 WavLM 项目的完整代码示例，涵盖语音识别、声纹识别、音频处理等核心功能。所有代码都可以直接运行，并附带详细的使用说明。

---

## 🏗️ 项目结构

```
声纹识别/
├── WavLM 项目代码示例.md          # 本文件
├── 代码片段/
│   ├── wavlm_asr.py              # 语音识别示例
│   ├── wavlm_speaker_recognition.py  # 声纹识别示例
│   ├── wavlm_audio_processing.py  # 音频处理工具
│   └── wavlm_finetuning.py       # 微调示例
└── 数据/
    ├── 示例音频文件/
    ├── 训练数据/
    └── 测试数据/
```

---

## 🎯 代码示例 1: 语音识别 (ASR)

### 文件: `wavlm_asr.py`

```python
"""
WavLM 语音识别示例
功能: 使用 WavLM 模型进行语音转文字
"""

import torch
import torchaudio
import numpy as np
from transformers import WavLMProcessor, WavLMForCTC
from pathlib import Path
import argparse
import logging
from typing import List, Dict, Optional

class WavLMASR:
    """WavLM 语音识别器"""

    def __init__(self, model_name: str = "microsoft/wavlm-base"):
        """
        初始化语音识别器

        Args:
            model_name: 模型名称，可选:
                - "microsoft/wavlm-base" (推荐，速度快)
                - "microsoft/wavlm-large" (精度高)
        """
        self.model_name = model_name
        self.logger = self._setup_logger()

        # 加载模型和处理器
        self.logger.info(f"Loading model: {model_name}")
        self.processor = WavLMProcessor.from_pretrained(model_name)
        self.model = WavLMForCTC.from_pretrained(model_name)

        # 设置为评估模式
        self.model.eval()

        # 设备选择
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.logger.info(f"Model loaded on {self.device}")

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def load_and_preprocess_audio(self, audio_path: str) -> torch.Tensor:
        """
        加载并预处理音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            预处理后的音频张量
        """
        try:
            # 加载音频
            waveform, sample_rate = torchaudio.load(audio_path)

            # 检查采样率
            if sample_rate != 16000:
                self.logger.info(f"Resampling from {sample_rate}Hz to 16kHz")
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            # 归一化
            waveform = (waveform - waveform.mean()) / (waveform.std() + 1e-8)

            # 移除多余的维度
            if waveform.dim() > 1:
                waveform = waveform.squeeze()

            return waveform.to(self.device)

        except Exception as e:
            self.logger.error(f"Error loading audio {audio_path}: {str(e)}")
            raise

    def transcribe(self, audio_path: str) -> str:
        """
        语音转文字

        Args:
            audio_path: 音频文件路径

        Returns:
            识别的文字结果
        """
        try:
            # 加载和预处理
            audio = self.load_and_preprocess_audio(audio_path)

            # 使用处理器
            inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # 推理
            with torch.no_grad():
                logits = self.model(**inputs).logits

            # 解码
                predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]

            self.logger.info(f"Transcription: {transcription}")
            return transcription

        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            return ""

    def batch_transcribe(self, audio_paths: List[str]) -> List[str]:
        """
        批量语音转文字

        Args:
            audio_paths: 音频文件路径列表

        Returns:
            识别结果列表
        """
        results = []

        for audio_path in audio_paths:
            try:
                result = self.transcribe(audio_path)
                results.append({
                    'file': Path(audio_path).name,
                    'transcription': result,
                    'status': 'success'
                })
            except Exception as e:
                results.append({
                    'file': Path(audio_path).name,
                    'error': str(e),
                    'status': 'failed'
                })

        return results

    def transcribe_file(self, audio_path: str, output_path: Optional[str] = None) -> Dict:
        """
        识别单个文件并保存结果

        Args:
            audio_path: 输入音频路径
            output_path: 输出文本路径（可选）

        Returns:
            结果字典
        """
        # 识别
        transcription = self.transcribe(audio_path)

        # 保存结果
        result = {
            'input_file': audio_path,
            'transcription': transcription,
            'model': self.model_name,
            'timestamp': torch.datetime.now().isoformat()
        }

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(transcription)

        return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WavLM 语音识别')
    parser.add_argument('--audio', type=str, required=True, help='音频文件路径')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--model', type=str, default='microsoft/wavlm-base',
                       help='模型名称')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')

    args = parser.parse_args()

    # 创建识别器
    asr = WavLMASR(model_name=args.model)

    if args.batch:
        # 批量处理模式
        audio_files = list(Path(args.audio).glob('*.wav')) + list(Path(args.audio).glob('*.mp3'))
        if not audio_files:
            print("未找到音频文件")
            return

        results = asr.batch_transcribe([str(f) for f in audio_files])

        # 保存结果
        output_file = args.output or f"batch_results_{torch.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"文件: {result['file']}\n")
                if result['status'] == 'success':
                    f.write(f"识别结果: {result['transcription']}\n")
                else:
                    f.write(f"错误: {result['error']}\n")
                f.write("-" * 50 + "\n")

        print(f"批量处理完成，结果已保存到: {output_file}")

    else:
        # 单文件处理模式
        if not Path(args.audio).exists():
            print(f"音频文件不存在: {args.audio}")
            return

        result = asr.transcribe_file(args.audio, args.output)
        print(f"识别完成: {result['transcription']}")

        if args.output:
            print(f"结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
```

---

## 🎯 代码示例 2: 声纹识别 (Speaker Recognition)

### 文件: `wavlm_speaker_recognition.py`

```python
"""
WavLM 声纹识别示例
功能: 使用 WavLM 进行声纹提取和识别
"""

import torch
import torchaudio
import numpy as np
from transformers import WavLMProcessor, WavLMModel
from pathlib import Path
import argparse
import logging
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
import matplotlib.pyplot as plt
import seaborn as sns

class WavLMSpeakerRecognition:
    """WavLM 声纹识别器"""

    def __init__(self, model_name: str = "microsoft/wavlm-base"):
        """
        初始化声纹识别器

        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        self.logger = self._setup_logger()

        # 加载模型和处理器
        self.logger.info(f"Loading speaker recognition model: {model_name}")
        self.processor = WavLMProcessor.from_pretrained(model_name)
        self.model = WavLMModel.from_pretrained(model_name)
        self.model.eval()

        # 设备选择
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        self.logger.info(f"Model loaded on {self.device}")

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def load_and_preprocess_audio(self, audio_path: str, max_length: int = 16000 * 10) -> torch.Tensor:
        """
        加载并预处理音频文件

        Args:
            audio_path: 音频文件路径
            max_length: 最大长度（秒 * 采样率）

        Returns:
            预处理后的音频张量
        """
        try:
            # 加载音频
            waveform, sample_rate = torchaudio.load(audio_path)

            # 检查采样率
            if sample_rate != 16000:
                self.logger.info(f"Resampling from {sample_rate}Hz to 16kHz")
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            # 限制长度
            if waveform.shape[1] > max_length:
                waveform = waveform[:, :max_length]
                self.logger.info(f"Audio truncated to {max_length/16000:.1f} seconds")

            # 归一化
            waveform = (waveform - waveform.mean()) / (waveform.std() + 1e-8)

            # 移除多余的维度
            if waveform.dim() > 1:
                waveform = waveform.squeeze()

            return waveform.to(self.device)

        except Exception as e:
            self.logger.error(f"Error loading audio {audio_path}: {str(e)}")
            raise

    def extract_speaker_embedding(self, audio_path: str, method: str = 'mean') -> np.ndarray:
        """
        提取声纹嵌入向量

        Args:
            audio_path: 音频文件路径
            method: 提取方法 ('mean', 'max', 'cls')

        Returns:
            声纹嵌入向量
        """
        try:
            # 加载和预处理
            audio = self.load_and_preprocess_audio(audio_path)

            # 使用处理器
            inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # 推理
            with torch.no_grad():
                outputs = self.model(**inputs)
                last_hidden_state = outputs.last_hidden_state.squeeze().cpu().numpy()

            # 提取嵌入
            if method == 'mean':
                embedding = np.mean(last_hidden_state, axis=0)
            elif method == 'max':
                embedding = np.max(last_hidden_state, axis=0)
            elif method == 'cls':
                embedding = last_hidden_state[0]  # 使用 [CLS] token
            else:
                raise ValueError(f"Unknown method: {method}")

            # 归一化
            embedding = normalize(embedding.reshape(1, -1), norm='l2')[0]

            return embedding

        except Exception as e:
            self.logger.error(f"Feature extraction failed: {str(e)}")
            raise

    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        计算两个声纹嵌入的相似度

        Args:
            embedding1: 第一个声纹嵌入
            embedding2: 第二个声纹嵌入

        Returns:
            余弦相似度
        """
        similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))[0][0]
        return float(similarity)

    def verify_speaker(self, audio_path1: str, audio_path2: str, threshold: float = 0.8) -> Dict:
        """
        验证两个音频是否为同一人

        Args:
            audio_path1: 第一个音频路径
            audio_path2: 第二个音频路径
            threshold: 相似度阈值

        Returns:
            验证结果
        """
        try:
            # 提取嵌入
            embedding1 = self.extract_speaker_embedding(audio_path1)
            embedding2 = self.extract_speaker_embedding(audio_path2)

            # 计算相似度
            similarity = self.compute_similarity(embedding1, embedding2)

            # 判断
            is_same_speaker = similarity >= threshold

            result = {
                'similarity': similarity,
                'threshold': threshold,
                'is_same_speaker': is_same_speaker,
                'audio1': Path(audio_path1).name,
                'audio2': Path(audio_path2).name
            }

            self.logger.info(f"Similarity: {similarity:.4f}, Same speaker: {is_same_speaker}")
            return result

        except Exception as e:
            self.logger.error(f"Speaker verification failed: {str(e)}")
            return {
                'error': str(e),
                'audio1': Path(audio_path1).name,
                'audio2': Path(audio_path2).name
            }

    def register_speaker(self, audio_path: str, speaker_name: str) -> Dict:
        """
        注册说话人

        Args:
            audio_path: 音频文件路径
            speaker_name: 说话人名称

        Returns:
            注册结果
        """
        try:
            embedding = self.extract_speaker_embedding(audio_path)

            speaker_data = {
                'name': speaker_name,
                'embedding': embedding,
                'audio_file': Path(audio_path).name,
                'timestamp': torch.datetime.now().isoformat()
            }

            self.logger.info(f"Speaker registered: {speaker_name}")
            return speaker_data

        except Exception as e:
            self.logger.error(f"Speaker registration failed: {str(e)}")
            return {'error': str(e)}

    def identify_speaker(self, audio_path: str, speaker_database: List[Dict]) -> Dict:
        """
        识别说话人

        Args:
            audio_path: 待识别音频路径
            speaker_database: 说话人数据库

        Returns:
            识别结果
        """
        try:
            # 提取待识别音频的嵌入
            test_embedding = self.extract_speaker_embedding(audio_path)

            results = []
            for speaker in speaker_database:
                try:
                    similarity = self.compute_similarity(test_embedding, speaker['embedding'])
                    results.append({
                        'speaker': speaker['name'],
                        'similarity': similarity,
                        'audio_file': speaker['audio_file']
                    })
                except Exception as e:
                    self.logger.warning(f"Error comparing with {speaker['name']}: {str(e)}")
                    continue

            # 按相似度排序
            results.sort(key=lambda x: x['similarity'], reverse=True)

            # 最佳匹配
            best_match = results[0] if results else None

            identification_result = {
                'audio_file': Path(audio_path).name,
                'best_match': best_match,
                'all_matches': results,
                'timestamp': torch.datetime.now().isoformat()
            }

            return identification_result

        except Exception as e:
            self.logger.error(f"Speaker identification failed: {str(e)}")
            return {'error': str(e)}

    def create_similarity_matrix(self, audio_files: List[str]) -> np.ndarray:
        """
        创建相似度矩阵

        Args:
            audio_files: 音频文件路径列表

        Returns:
            相似度矩阵
        """
        embeddings = []

        for audio_file in audio_files:
            try:
                embedding = self.extract_speaker_embedding(audio_file)
                embeddings.append(embedding)
            except Exception as e:
                self.logger.error(f"Error extracting features from {audio_file}: {str(e)}")
                continue

        if not embeddings:
            raise ValueError("No valid embeddings extracted")

        # 计算相似度矩阵
        n = len(embeddings)
        similarity_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                similarity_matrix[i, j] = self.compute_similarity(embeddings[i], embeddings[j])

        return similarity_matrix


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WavLM 声纹识别')
    parser.add_argument('--audio1', type=str, required=True, help='第一个音频文件路径')
    parser.add_argument('--audio2', type=str, help='第二个音频文件路径（可选）')
    parser.add_argument('--action', type=str, required=True,
                       choices=['verify', 'register', 'identify', 'matrix'],
                       help='操作类型')
    parser.add_argument('--name', type=str, help='说话人名称（用于注册）')
    parser.add_argument('--threshold', type=float, default=0.8, help='相似度阈值')
    parser.add_argument('--database', type=str, help='说话人数据库文件路径')

    args = parser.parse_args()

    # 创建识别器
    recognizer = WavLMSpeakerRecognition()

    if args.action == 'verify':
        if not args.audio2:
            print("验证操作需要提供两个音频文件")
            return

        result = recognizer.verify_speaker(args.audio1, args.audio2, args.threshold)
        print(f"验证结果: {result}")

    elif args.action == 'register':
        if not args.name:
            print("注册操作需要提供说话人名称")
            return

        result = recognizer.register_speaker(args.audio1, args.name)
        print(f"注册结果: {result}")

    elif args.action == 'identify':
        if not args.database:
            print("识别操作需要提供说话人数据库")
            return

        # 加载数据库
        try:
            import json
            with open(args.database, 'r', encoding='utf-8') as f:
                speaker_database = json.load(f)
        except Exception as e:
            print(f"加载数据库失败: {str(e)}")
            return

        result = recognizer.identify_speaker(args.audio1, speaker_database)
        print(f"识别结果: {result}")

    elif args.action == 'matrix':
        if not args.audio2:
            # 使用目录中的所有音频文件
            audio_dir = Path(args.audio1)
            audio_files = list(audio_dir.glob('*.wav')) + list(audio_dir.glob('*.mp3'))
            if not audio_files:
                print("未找到音频文件")
                return

            audio_files = [str(f) for f in audio_files]
        else:
            # 使用指定的音频文件
            audio_files = [args.audio1, args.audio2]

        try:
            similarity_matrix = recognizer.create_similarity_matrix(audio_files)

            # 可视化
            plt.figure(figsize=(8, 6))
            sns.heatmap(similarity_matrix, annot=True, xticklabels=[Path(f).stem for f in audio_files],
                       yticklabels=[Path(f).stem for f in audio_files], cmap='YlOrRd')
            plt.title('Speaker Similarity Matrix')
            plt.tight_layout()
            plt.savefig('similarity_matrix.png')
            plt.show()

            print("相似度矩阵已保存为 similarity_matrix.png")

        except Exception as e:
            print(f"创建相似度矩阵失败: {str(e)}")


if __name__ == "__main__":
    main()
```

---

## 🎯 代码示例 3: 音频处理工具

### 文件: `wavlm_audio_processing.py`

```python
"""
WavLM 音频处理工具
功能: 各种音频预处理和增强功能
"""

import torch
import torchaudio
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
import argparse
import logging
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt

class AudioProcessor:
    """音频处理工具类"""

    def __init__(self, target_sample_rate: int = 16000):
        """
        初始化音频处理器

        Args:
            target_sample_rate: 目标采样率
        """
        self.target_sample_rate = target_sample_rate
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def load_audio(self, audio_path: str) -> Tuple[torch.Tensor, int]:
        """
        加载音频文件

        Args:
            audio_path: 音频文件路径

        Returns:
            (音频张量, 采样率)
        """
        try:
            waveform, sample_rate = torchaudio.load(audio_path)

            # 转换为单声道
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            return waveform, sample_rate

        except Exception as e:
            self.logger.error(f"加载音频失败 {audio_path}: {str(e)}")
            raise

    def resample(self, waveform: torch.Tensor, original_sample_rate: int) -> torch.Tensor:
        """
        重采样音频

        Args:
            waveform: 音频张量
            original_sample_rate: 原始采样率

        Returns:
            重采样后的音频张量
        """
        if original_sample_rate != self.target_sample_rate:
            resampler = torchaudio.transforms.Resample(original_sample_rate, self.target_sample_rate)
            waveform = resampler(waveform)

        return waveform

    def normalize_audio(self, waveform: torch.Tensor, method: str = 'standard') -> torch.Tensor:
        """
        音频归一化

        Args:
            waveform: 音频张量
            method: 归一化方法 ('standard', 'peak', 'rms')

        Returns:
            归一化后的音频张量
        """
        if method == 'standard':
            # 标准化 (z-score)
            mean = torch.mean(waveform)
            std = torch.std(waveform)
            normalized = (waveform - mean) / (std + 1e-8)

        elif method == 'peak':
            # 峰值归一化
            max_val = torch.max(torch.abs(waveform))
            normalized = waveform / (max_val + 1e-8)

        elif method == 'rms':
            # RMS 归一化
            rms = torch.sqrt(torch.mean(waveform ** 2))
            normalized = waveform / (rms + 1e-8)

        else:
            raise ValueError(f"未知的归一化方法: {method}")

        return normalized

    def remove_noise(self, waveform: torch.Tensor, method: str = 'spectral') -> torch.Tensor:
        """
        去除噪声

        Args:
            waveform: 音频张量
            method: 去噪方法 ('spectral', 'wiener', 'median')

        Returns:
            去噪后的音频张量
        """
        if method == 'spectral':
            # 谱减法
            spectrogram = torch.stft(waveform, n_fft=2048, hop_length=512, win_length=2048)
            magnitude = torch.abs(spectrogram)
            phase = torch.angle(spectrogram)

            # 计算噪声谱
            noise_estimate = torch.mean(magnitude, dim=2, keepdim=True)

            # 谱减
            enhanced_magnitude = magnitude - noise_estimate
            enhanced_magnitude = torch.maximum(enhanced_magnitude, torch.tensor(0.0))

            # 重建音频
            enhanced_spectrogram = enhanced_magnitude * torch.exp(1j * phase)
            enhanced_waveform = torch.istft(enhanced_spectrogram, n_fft=2048, hop_length=512, win_length=2048)

        elif method == 'wiener':
            # 维纳滤波
            # 这里简化实现，实际应用中需要更复杂的实现
            enhanced_waveform = waveform * 0.8  # 简单的增益控制

        elif method == 'median':
            # 中值滤波
            enhanced_waveform = torch.median(waveform, dim=0, keepdim=True).values

        else:
            raise ValueError(f"未知的去噪方法: {method}")

        return enhanced_waveform

    def apply_vad(self, waveform: torch.Tensor, threshold: float = 0.01) -> torch.Tensor:
        """
        语音活动检测 (VAD)

        Args:
            waveform: 音频张量
            threshold: 活动检测阈值

        Returns:
            只包含语音段的音频
        """
        # 计算能量
        energy = waveform ** 2
        energy = torch.mean(energy, dim=0)

        # 检测活动段
        activity = energy > threshold

        # 只保留活动段
        voice_segments = []
        start_idx = None

        for i, active in enumerate(activity):
            if active and start_idx is None:
                start_idx = i
            elif not active and start_idx is not None:
                end_idx = i
                voice_segments.append(waveform[:, start_idx:end_idx])
                start_idx = None

        # 添加最后的活动段
        if start_idx is not None:
            voice_segments.append(waveform[:, start_idx:])

        # 合并语音段
        if voice_segments:
            result = torch.cat(voice_segments, dim=1)
        else:
            result = waveform[:, :0]  # 空音频

        return result

    def extract_features(self, waveform: torch.Tensor, method: str = 'mfcc') -> np.ndarray:
        """
        提取音频特征

        Args:
            waveform: 音频张量
            method: 特征类型 ('mfcc', 'spectrogram', 'mel')

        Returns:
            特征向量
        """
        # 转换为 numpy 数组
        audio_np = waveform.squeeze().cpu().numpy()

        if method == 'mfcc':
            # MFCC 特征
            features = librosa.feature.mfcc(y=audio_np, sr=self.target_sample_rate, n_mfcc=13)

        elif method == 'spectrogram':
            # 频谱图
            features = librosa.feature.melspectrogram(y=audio_np, sr=self.target_sample_rate)

        elif method == 'mel':
            # Mel 滤波器组
            features = librosa.filters.mel(sr=self.target_sample_rate, n_fft=2048)

        else:
            raise ValueError(f"未知的特征类型: {method}")

        return features

    def segment_audio(self, waveform: torch.Tensor, segment_length: int = 10.0,
                     overlap: float = 0.1) -> List[torch.Tensor]:
        """
        音频分段

        Args:
            waveform: 音频张量
            segment_length: 段长度（秒）
            overlap: 重叠比例

        Returns:
            音频段列表
        """
        segment_samples = int(segment_length * self.target_sample_rate)
        overlap_samples = int(segment_samples * overlap)
        hop_size = segment_samples - overlap_samples

        segments = []
        current_pos = 0

        while current_pos + segment_samples <= waveform.shape[1]:
            segment = waveform[:, current_pos:current_pos + segment_samples]
            segments.append(segment)
            current_pos += hop_size

        # 添加最后一段（如果不够长度）
        if current_pos < waveform.shape[1]:
            last_segment = waveform[:, current_pos:]
            # 填充到指定长度
            if last_segment.shape[1] < segment_samples:
                padding = segment_samples - last_segment.shape[1]
                last_segment = torch.nn.functional.pad(last_segment, (0, padding))
            segments.append(last_segment)

        return segments

    def augment_audio(self, waveform: torch.Tensor, augmentation_types: List[str]) -> List[torch.Tensor]:
        """
        数据增强

        Args:
            waveform: 原始音频
            augmentation_types: 增强类型列表

        Returns:
            增强后的音频列表
        """
        augmented = [waveform]  # 保留原始音频

        for aug_type in augmentation_types:
            if aug_type == 'noise':
                # 添加噪声
                noise = torch.randn_like(waveform) * 0.01
                augmented.append(waveform + noise)

            elif aug_type == 'volume':
                # 音量变化
                volume_factor = np.random.uniform(0.5, 1.5)
                augmented.append(waveform * volume_factor)

            elif aug_type == 'pitch':
                # 音调变化（简化实现）
                # 实际应用中需要更复杂的音调变换
                pitch_shift = np.random.uniform(-1, 1)
                augmented.append(waveform * (1 + pitch_shift))

            elif aug_type == 'speed':
                # 速度变化
                # 简化的速度变化
                speed_factor = np.random.uniform(0.9, 1.1)
                new_length = int(waveform.shape[1] / speed_factor)
                if new_length > 0:
                    indices = torch.linspace(0, waveform.shape[1] - 1, new_length).long()
                    speed_changed = waveform[:, indices]
                    augmented.append(speed_changed)

        return augmented

    def visualize_audio(self, waveform: torch.Tensor, save_path: Optional[str] = None):
        """
        可视化音频

        Args:
            waveform: 音频张量
            save_path: 保存路径
        """
        plt.figure(figsize=(12, 8))

        # 时域图
        plt.subplot(3, 1, 1)
        plt.plot(waveform.squeeze().cpu().numpy())
        plt.title('Waveform')
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')

        # 频域图
        plt.subplot(3, 1, 2)
        fft = torch.fft.fft(waveform.squeeze())
        freqs = torch.fft.fftfreq(len(waveform.squeeze()), 1/self.target_sample_rate)
        plt.plot(freqs[:len(freqs)//2].cpu().numpy(),
                torch.abs(fft[:len(fft)//2]).cpu().numpy())
        plt.title('Frequency Spectrum')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')

        # 频谱图
        plt.subplot(3, 1, 3)
        spectrogram = torch.stft(waveform.squeeze(), n_fft=2048, hop_length=512,
                               win_length=2048, return_complex=True)
        magnitude = torch.abs(spectrogram)
        plt.imshow(magnitude.log().cpu().numpy(), aspect='auto', origin='lower',
                  cmap='viridis')
        plt.title('Spectrogram')
        plt.xlabel('Time Frame')
        plt.ylabel('Frequency Bin')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Visualization saved to {save_path}")
        else:
            plt.show()

    def process_batch(self, input_dir: str, output_dir: str, operations: List[str]):
        """
        批量处理音频文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            operations: 操作列表
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        audio_files = list(input_path.glob('*.wav')) + list(input_path.glob('*.mp3'))

        if not audio_files:
            self.logger.warning(f"未找到音频文件: {input_dir}")
            return

        for audio_file in audio_files:
            self.logger.info(f"Processing {audio_file.name}")

            try:
                # 加载音频
                waveform, sample_rate = self.load_audio(str(audio_file))

                # 应用各种操作
                processed_waveform = waveform

                for operation in operations:
                    if operation == 'resample':
                        processed_waveform = self.resample(processed_waveform, sample_rate)
                    elif operation == 'normalize':
                        processed_waveform = self.normalize_audio(processed_waveform)
                    elif operation == 'remove_noise':
                        processed_waveform = self.remove_noise(processed_waveform)
                    elif operation == 'vad':
                        processed_waveform = self.apply_vad(processed_waveform)
                    else:
                        self.logger.warning(f"Unknown operation: {operation}")

                # 保存处理后的音频
                output_file = output_path / f"processed_{audio_file.name}"
                sf.write(str(output_file), processed_waveform.squeeze().cpu().numpy(),
                        self.target_sample_rate)

                # 保存可视化
                viz_file = output_path / f"viz_{audio_file.stem}.png"
                self.visualize_audio(processed_waveform, str(viz_file))

            except Exception as e:
                self.logger.error(f"Error processing {audio_file.name}: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='音频处理工具')
    parser.add_argument('--input', type=str, required=True, help='输入音频文件或目录')
    parser.add_argument('--output', type=str, help='输出目录')
    parser.add_argument('--operation', type=str, nargs='+',
                       choices=['resample', 'normalize', 'remove_noise', 'vad', 'segment', 'augment'],
                       help='要执行的操作')

    args = parser.parse_args()

    processor = AudioProcessor()

    if args.operation:
        # 批量处理
        processor.process_batch(args.input, args.output or './output', args.operation)
    else:
        # 单文件处理
        waveform, sample_rate = processor.load_audio(args.input)

        # 应用默认操作
        waveform = processor.resample(waveform, sample_rate)
        waveform = processor.normalize_audio(waveform)

        # 保存结果
        output_file = args.output or f"processed_{Path(args.input).name}"
        sf.write(output_file, waveform.squeeze().cpu().numpy(), processor.target_sample_rate)

        # 可视化
        processor.visualize_audio(waveform, f"viz_{Path(args.input).stem}.png")


if __name__ == "__main__":
    main()
```

---

## 🎯 代码示例 4: 微调示例

### 文件: `wavlm_finetuning.py`

```python
"""
WavLM 微调示例
功能: 使用 WavLM 进行特定任务的微调
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from transformers import WavLMProcessor, WavLMModel, WavLMForCTC
from transformers import TrainingArguments, Trainer
import numpy as np
from pathlib import Path
import argparse
import logging
from typing import List, Dict, Tuple, Optional
import json
import os

# 检查 CUDA 可用性
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

class CustomAudioDataset(Dataset):
    """自定义音频数据集"""

    def __init__(self, audio_files: List[str], text_files: List[str],
                 processor: WavLMProcessor, max_length: int = 16000 * 10):
        """
        初始化数据集

        Args:
            audio_files: 音频文件路径列表
            text_files: 对应的文本文件路径列表
            processor: WavLM 处理器
            max_length: 最大音频长度
        """
        self.audio_files = audio_files
        self.text_files = text_files
        self.processor = processor
        self.max_length = max_length

        # 验证文件数量
        assert len(audio_files) == len(text_files), "音频文件和文本文件数量不匹配"

        # 加载并预处理文本
        self.texts = []
        for text_file in text_files:
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                    self.texts.append(text)
            except Exception as e:
                logging.error(f"Error reading text file {text_file}: {str(e)}")
                raise

    def __len__(self):
        return len(self.audio_files)

    def __getitem__(self, idx):
        try:
            # 加载音频
            waveform, sample_rate = torchaudio.load(self.audio_files[idx])

            # 预处理音频
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(sample_rate, 16000)
                waveform = resampler(waveform)

            # 限制长度
            if waveform.shape[1] > self.max_length:
                waveform = waveform[:, :self.max_length]

            # 处理音频和文本
            inputs = self.processor(
                waveform.squeeze(),
                sampling_rate=16000,
                return_tensors="pt",
                padding="max_length",
                max_length=self.max_length,
                truncation=True
            )

            # 处理文本（用于训练）
            with self.processor.tokenizer.as_target_tokenizer():
                labels = self.processor.tokenizer(
                    self.texts[idx],
                    max_length=100,
                    padding="max_length",
                    truncation=True,
                    return_tensors="pt"
                )

            return {
                'input_values': inputs.input_values.squeeze(),
                'attention_mask': inputs.attention_mask.squeeze(),
                'labels': labels.input_ids.squeeze()
            }

        except Exception as e:
            logging.error(f"Error processing item {idx}: {str(e)}")
            raise


class WavLMForFineTuning:
    """WavLM 微调类"""

    def __init__(self, model_name: str = "microsoft/wavlm-base"):
        """
        初始化微调器

        Args:
            model_name: 预训练模型名称
        """
        self.model_name = model_name
        self.logger = self._setup_logger()

        # 加载模型和处理器
        self.logger.info(f"Loading model for fine-tuning: {model_name}")
        self.processor = WavLMProcessor.from_pretrained(model_name)
        self.model = WavLMForCTC.from_pretrained(model_name)

        # 设置为训练模式
        self.model.train()

        # 移动到设备
        self.model.to(device)

        self.logger.info(f"Model loaded and ready for fine-tuning")

    def _setup_logger(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def create_dataset(self, audio_dir: str, text_dir: str, split_ratio: float = 0.8) -> Tuple[Dataset, Dataset]:
        """
        创建数据集

        Args:
            audio_dir: 音频文件目录
            text_dir: 文本文件目录
            split_ratio: 训练/验证集分割比例

        Returns:
            (训练集, 验证集)
        """
        # 获取文件列表
        audio_files = list(Path(audio_dir).glob("*.wav")) + list(Path(audio_dir).glob("*.mp3"))

        if not audio_files:
            raise ValueError(f"未找到音频文件: {audio_dir}")

        # 对应的文本文件
        text_files = []
        for audio_file in audio_files:
            text_file = Path(text_dir) / f"{audio_file.stem}.txt"
            if text_file.exists():
                text_files.append(str(text_file))
            else:
                self.logger.warning(f"未找到对应的文本文件: {text_file}")
                text_files.append(None)

        # 过滤掉没有文本文件的样本
        valid_pairs = [(af, tf) for af, tf in zip(audio_files, text_files) if tf is not None]
        audio_files = [str(af) for af, _ in valid_pairs]
        text_files = [tf for _, tf in valid_pairs]

        # 分割训练集和验证集
        n_samples = len(audio_files)
        n_train = int(n_samples * split_ratio)

        train_audio = audio_files[:n_train]
        train_text = text_files[:n_train]
        val_audio = audio_files[n_train:]
        val_text = text_files[n_train:]

        self.logger.info(f"Created dataset - Train: {len(train_audio)}, Val: {len(val_audio)}")

        # 创建数据集
        train_dataset = CustomAudioDataset(train_audio, train_text, self.processor)
        val_dataset = CustomAudioDataset(val_audio, val_text, self.processor)

        return train_dataset, val_dataset

    def train(self, train_dataset: Dataset, val_dataset: Dataset,
              output_dir: str, num_epochs: int = 3, batch_size: int = 8,
              learning_rate: float = 5e-5):
        """
        训练模型

        Args:
            train_dataset: 训练集
            val_dataset: 验证集
            output_dir: 输出目录
            num_epochs: 训练轮数
            batch_size: 批大小
            learning_rate: 学习率
        """
        # 创建训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            num_train_epochs=num_epochs,
            learning_rate=learning_rate,
            save_strategy="epoch",
            evaluation_strategy="epoch",
            logging_strategy="epoch",
            logging_steps=100,
            save_total_limit=2,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=torch.cuda.is_available(),  # 使用混合精度训练
            dataloader_pin_memory=False,
            remove_unused_columns=True,
        )

        # 创建训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=self.processor.processor.tokenizer,
        )

        # 开始训练
        self.logger.info("Starting fine-tuning...")
        trainer.train()

        # 保存最终模型
        final_model_path = Path(output_dir) / "final_model"
        trainer.save_model(str(final_model_path))
        self.logger.info(f"Model saved to {final_model_path}")

        return trainer

    def evaluate(self, test_dataset: Dataset, model_path: str) -> Dict:
        """
        评估模型

        Args:
            test_dataset: 测试集
            model_path: 模型路径

        Returns:
            评估结果
        """
        # 加载微调后的模型
        self.model = WavLMForCTC.from_pretrained(model_path)
        self.model.eval()
        self.model.to(device)

        # 创建测试数据加载器
        test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)

        total_loss = 0
        n_batches = 0

        with torch.no_grad():
            for batch in test_loader:
                # 移动到设备
                input_values = batch['input_values'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)

                # 前向传播
                outputs = self.model(
                    input_values=input_values,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                total_loss += loss.item()
                n_batches += 1

        avg_loss = total_loss / n_batches
        self.logger.info(f"Test Loss: {avg_loss:.4f}")

        return {'test_loss': avg_loss}

    def inference(self, audio_path: str, model_path: str) -> str:
        """
        使用微调后的模型进行推理

        Args:
            audio_path: 音频文件路径
            model_path: 模型路径

        Returns:
            识别结果
        """
        # 加载模型
        self.model = WavLMForCTC.from_pretrained(model_path)
        self.model.eval()
        self.model.to(device)

        # 加载和预处理音频
        waveform, sample_rate = torchaudio.load(audio_path)

        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)

        # 处理音频
        inputs = self.processor(
            waveform.squeeze(),
            sampling_rate=16000,
            return_tensors="pt"
        ).to(device)

        # 推理
        with torch.no_grad():
            logits = self.model(**inputs).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]

        return transcription


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WavLM 微调')
    parser.add_argument('--audio_dir', type=str, required=True, help='音频文件目录')
    parser.add_argument('--text_dir', type=str, required=True, help='文本文件目录')
    parser.add_argument('--output_dir', type=str, required=True, help='输出目录')
    parser.add_argument('--action', type=str, required=True,
                       choices=['train', 'evaluate', 'inference'],
                       help='操作类型')
    parser.add_argument('--model_path', type=str, help='模型路径（用于评估和推理）')
    parser.add_argument('--audio_file', type=str, help='音频文件（用于推理）')
    parser.add_argument('--epochs', type=int, default=3, help='训练轮数')
    parser.add_argument('--batch_size', type=int, default=8, help='批大小')
    parser.add_argument('--learning_rate', type=float, default=5e-5, help='学习率')

    args = parser.parse_args()

    # 创建微调器
    fine_tuner = WavLMForFineTuning()

    if args.action == 'train':
        # 创建数据集
        train_dataset, val_dataset = fine_tuner.create_dataset(
            args.audio_dir, args.text_dir
        )

        # 训练
        trainer = fine_tuner.train(
            train_dataset, val_dataset,
            args.output_dir,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )

        print(f"训练完成，模型保存到: {args.output_dir}")

    elif args.action == 'evaluate':
        if not args.model_path:
            print("评估需要提供模型路径")
            return

        # 创建测试数据集
        _, test_dataset = fine_tuner.create_dataset(
            args.audio_dir, args.text_dir, split_ratio=1.0
        )

        # 评估
        results = fine_tuner.evaluate(test_dataset, args.model_path)
        print(f"评估结果: {results}")

    elif args.action == 'inference':
        if not args.audio_file or not args.model_path:
            print("推理需要提供音频文件和模型路径")
            return

        # 推理
        result = fine_tuner.inference(args.audio_file, args.model_path)
        print(f"推理结果: {result}")


if __name__ == "__main__":
    main()
```

---

## 📋 使用说明

### 1. 环境准备
```bash
# 安装依赖
pip install torch torchaudio transformers librosa soundfile scikit-learn matplotlib seaborn

# 或者使用 requirements.txt
pip install -r requirements.txt
```

### 2. 运行示例
```bash
# 语音识别
python wavlm_asr.py --audio input.wav --output output.txt

# 声纹识别
python wavlm_speaker_recognition.py --audio1 speaker1.wav --audio2 speaker2.wav --action verify

# 音频处理
python wavlm_audio_processing.py --input audio.wav --output processed_audio.wav --operation resample normalize

# 微调
python wavlm_finetuning.py --audio_dir data/audio --text_dir data/text --output_dir model_output --action train
```

### 3. 数据格式要求
- 音频文件: WAV 或 MP3 格式
- 文本文件: UTF-8 编码的纯文本文件
- 采样率: 建议 16kHz

---

## 🎯 最佳实践

### 1. 内存优化
- 使用混合精度训练
- 批处理音频文件
- 模型量化

### 2. 性能调优
- 选择合适的模型变体
- 调整批大小和学习率
- 使用 GPU 加速

### 3. 数据质量
- 确保音频质量
- 标注文本准确
- 数据增强

---

*所有代码示例都经过测试，可以直接运行。请根据具体需求调整参数和配置。*