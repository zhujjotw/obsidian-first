"""
WavLM 示例数据生成器
用于生成测试用的音频和文本数据
"""

import torch
import torchaudio
import numpy as np
from pathlib import Path
import argparse
import random
import string

class SampleDataGenerator:
    """示例数据生成器"""

    def __init__(self, sample_rate: int = 16000):
        """
        初始化数据生成器

        Args:
            sample_rate: 采样率
        """
        self.sample_rate = sample_rate
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def generate_sine_wave(self, frequency: float, duration: float, amplitude: float = 1.0) -> torch.Tensor:
        """
        生成正弦波

        Args:
            frequency: 频率 (Hz)
            duration: 持续时间 (秒)
            amplitude: 振幅

        Returns:
            音频张量
        """
        t = torch.linspace(0, duration, int(self.sample_rate * duration), device=self.device)
        waveform = amplitude * torch.sin(2 * torch.pi * frequency * t)
        return waveform.unsqueeze(0)

    def generate_noise(self, duration: float, noise_type: str = 'white') -> torch.Tensor:
        """
        生成噪声

        Args:
            duration: 持续时间 (秒)
            noise_type: 噪声类型 ('white', 'pink', 'brown')

        Returns:
            噪声音频张量
        """
        t = torch.linspace(0, duration, int(self.sample_rate * duration), device=self.device)
        samples = int(self.sample_rate * duration)

        if noise_type == 'white':
            # 白噪声
            noise = torch.randn(samples, device=self.device)
        elif noise_type == 'pink':
            # 粉红噪声 (1/f)
            noise = self._generate_pink_noise(samples)
        elif noise_type == 'brown':
            # 棕色噪声 (1/f²)
            noise = self._generate_brown_noise(samples)
        else:
            raise ValueError(f"未知的噪声类型: {noise_type}")

        return noise.unsqueeze(0) * 0.5

    def _generate_pink_noise(self, samples: int) -> torch.Tensor:
        """生成粉红噪声"""
        # 简化的粉红噪声生成
        white = torch.randn(samples, device=self.device)
        pink = torch.zeros_like(white)
        for i in range(1, len(white)):
            pink[i] = pink[i-1] + white[i] * (1.0 - i/len(white))
        return pink

    def _generate_brown_noise(self, samples: int) -> torch.Tensor:
        """生成棕色噪声"""
        white = torch.randn(samples, device=self.device)
        brown = torch.cumsum(white, dim=0) * (1.0 - torch.arange(samples, device=self.device)/samples)
        return brown

    def generate_speech_like_signal(self, duration: float) -> torch.Tensor:
        """
        生成类似语音的信号

        Args:
            duration: 持续时间 (秒)

        Returns:
            音频张量
        """
        # 使用多个频率分量的组合模拟语音
        frequencies = [100, 200, 400, 800, 1500]  # Hz
        amplitudes = [0.8, 0.6, 0.4, 0.3, 0.2]

        signal = torch.zeros(int(self.sample_rate * duration), device=self.device)

        for freq, amp in zip(frequencies, amplitudes):
            segment = self.generate_sine_wave(freq, duration, amp)
            signal += segment.squeeze()

        # 添加调制效果
        modulation = torch.sin(2 * torch.pi * 5 * torch.linspace(0, duration, int(self.sample_rate * duration), device=self.device))
        signal = signal * (1 + 0.3 * modulation)

        return signal.unsqueeze(0)

    def generate_mixed_audio(self, clean_audio: torch.Tensor, noise_level: float = 0.1) -> torch.Tensor:
        """
        生成混合音频 (清洁信号 + 噪声)

        Args:
            clean_audio: 清洁音频
            noise_level: 噪声水平

        Returns:
            混合音频
        """
        noise = self.generate_noise(clean_audio.shape[-1], noise_type='white')
        mixed_audio = clean_audio + noise_level * noise
        return mixed_audio

    def save_audio(self, audio: torch.Tensor, output_path: str, normalize: bool = True):
        """
        保存音频文件

        Args:
            audio: 音频张量
            output_path: 输出路径
            normalize: 是否归一化
        """
        if normalize:
            audio = (audio - audio.mean()) / (audio.std() + 1e-8)

        # 确保音频在有效范围内
        audio = torch.clamp(audio, -1.0, 1.0)

        # 保存
        torchaudio.save(output_path, audio.cpu(), self.sample_rate)

    def generate_sample_texts(self, count: int = 10) -> list:
        """
        生成示例文本

        Args:
            count: 文本数量

        Returns:
            文本列表
        """
        sample_texts = [
            "你好，这是一个语音识别的测试示例。",
            "WavLM模型可以处理各种语音任务。",
            "声纹识别技术在安全领域应用广泛。",
            "音频处理需要专业的知识和技能。",
            "深度学习正在改变语音识别技术。",
            "Microsoft WavLM是一个强大的语音模型。",
            "语音转文字技术在今天非常实用。",
            "人工智能让机器能够理解人类的语言。",
            "多模态AI是未来的发展方向。",
            "开源技术推动了AI技术的发展。"
        ]

        # 重复和组合文本
        texts = []
        for i in range(count):
            if i < len(sample_texts):
                texts.append(sample_texts[i])
            else:
                # 组合现有文本
                combined = " ".join(random.sample(sample_texts, 2))
                texts.append(combined)

        return texts

    def create_test_dataset(self, output_dir: str, num_samples: int = 20):
        """
        创建测试数据集

        Args:
            output_dir: 输出目录
            num_samples: 样本数量
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成音频文件
        for i in range(num_samples):
            print(f"Generating sample {i+1}/{num_samples}")

            # 生成不同类型的音频
            audio_types = ['speech', 'mixed', 'noise']
            audio_type = random.choice(audio_types)

            if audio_type == 'speech':
                # 语音信号
                duration = random.uniform(3, 8)  # 3-8秒
                clean_audio = self.generate_speech_like_signal(duration)
                mixed_audio = clean_audio

            elif audio_type == 'mixed':
                # 混合信号
                duration = random.uniform(3, 8)
                clean_audio = self.generate_speech_like_signal(duration)
                noise_level = random.uniform(0.05, 0.3)
                mixed_audio = self.generate_mixed_audio(clean_audio, noise_level)

            elif audio_type == 'noise':
                # 噪声信号
                duration = random.uniform(2, 5)
                mixed_audio = self.generate_noise(duration, 'white')

            # 保存音频文件
            audio_file = output_path / f"sample_{i:03d}.wav"
            self.save_audio(mixed_audio, str(audio_file))

            # 保存对应的文本文件
            text_file = output_path / f"sample_{i:03d}.txt"
            text = self.generate_sample_texts(1)[0]

            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)

        print(f"Test dataset created at: {output_path}")

    def create_test_pairs(self, output_dir: str, num_pairs: int = 10):
        """
        创建声纹识别测试对

        Args:
            output_dir: 输出目录
            num_pairs: 测试对数量
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成说话人声音
        speakers = []
        for i in range(3):  # 3个说话人
            speaker_files = []
            # 每个说话人生成5个样本
            for j in range(5):
                duration = random.uniform(2, 6)
                base_audio = self.generate_speech_like_signal(duration)

                # 添加每个说话人的独特特征
                speaker_characteristics = {
                    0: {'base_freq': 120, 'modulation': 0.8},  # 说话人1
                    1: {'base_freq': 150, 'modulation': 1.0},  # 说话人2
                    2: {'base_freq': 180, 'modulation': 0.6},  # 说话人3
                }

                char = speaker_characteristics[i]
                # 调整基频
                modulation_freq = char['base_freq']
                modulation = char['modulation']

                # 应用调制
                t = torch.linspace(0, duration, int(self.sample_rate * duration), device=self.device)
                audio = base_audio.squeeze() * (1 + modulation * torch.sin(2 * torch.pi * modulation_freq * t / 100))
                audio = audio.unsqueeze(0)

                # 添加少量噪声
                noise = self.generate_noise(duration, 'white')
                audio = audio + 0.05 * noise

                # 保存文件
                audio_file = output_path / f"speaker_{i}_sample_{j:02d}.wav"
                self.save_audio(audio, str(audio_file))
                speaker_files.append(str(audio_file))

            speakers.append(speaker_files)

        # 创建测试对
        for i in range(num_pairs):
            # 同说话人对
            speaker_idx = random.randint(0, 2)
            file1 = random.choice(speakers[speaker_idx])
            file2 = random.choice(speakers[speaker_idx])
            while file2 == file1:
                file2 = random.choice(speakers[speaker_idx])

            # 保存测试对
            test_file = output_path / f"same_speaker_pair_{i:02d}.txt"
            with open(test_file, 'w') as f:
                f.write(f"{file1}\n{file2}\n")

        # 不同说话人对
        for i in range(num_pairs):
            speaker1_idx = random.randint(0, 2)
            speaker2_idx = random.randint(0, 2)
            while speaker2_idx == speaker1_idx:
                speaker2_idx = random.randint(0, 2)

            file1 = random.choice(speakers[speaker1_idx])
            file2 = random.choice(speakers[speaker2_idx])

            # 保存测试对
            test_file = output_path / f"different_speaker_pair_{i:02d}.txt"
            with open(test_file, 'w') as f:
                f.write(f"{file1}\n{file2}\n")

        print(f"Speaker recognition test pairs created at: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WavLM 示例数据生成器')
    parser.add_argument('--output_dir', type=str, required=True, help='输出目录')
    parser.add_argument('--samples', type=int, default=20, help='样本数量')
    parser.add_argument('--pairs', type=int, default=10, help='测试对数量')
    parser.add_argument('--task', type=str, required=True,
                       choices=['dataset', 'pairs'],
                       help='生成任务类型')

    args = parser.parse_args()

    generator = SampleDataGenerator()

    if args.task == 'dataset':
        generator.create_test_dataset(args.output_dir, args.samples)
    elif args.task == 'pairs':
        generator.create_test_pairs(args.output_dir, args.pairs)


if __name__ == "__main__":
    main()