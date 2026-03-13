"""
WavLM 演示脚本
快速演示 WavLM 的主要功能
"""

import torch
import torchaudio
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import WavLMProcessor, WavLMForCTC, WavLMModel
import argparse
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WavLMDemo:
    """WavLM 演示类"""

    def __init__(self, model_name="microsoft/wavlm-base"):
        """
        初始化演示

        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        logger.info(f"Loading WavLM model: {model_name}")

        # 加载模型和处理器
        self.processor = WavLMProcessor.from_pretrained(model_name)
        self.model_asr = WavLMForCTC.from_pretrained(model_name)
        self.model_speaker = WavLMModel.from_pretrained(model_name)

        # 设备
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_asr.to(self.device)
        self.model_speaker.to(self.device)

        # 评估模式
        self.model_asr.eval()
        self.model_speaker.eval()

        logger.info(f"Model loaded on {self.device}")

    def load_audio(self, audio_path):
        """加载音频文件"""
        waveform, sample_rate = torchaudio.load(audio_path)

        # 转换为单声道
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        # 重采样到16kHz
        if sample_rate != 16000:
            resampler = torchaudio.transforms.Resample(sample_rate, 16000)
            waveform = resampler(waveform)

        return waveform.squeeze().to(self.device)

    def speech_recognition_demo(self, audio_path):
        """语音识别演示"""
        logger.info(f"=== Speech Recognition Demo ===")
        logger.info(f"Audio file: {audio_path}")

        # 加载音频
        waveform = self.load_audio(audio_path)
        logger.info(f"Audio shape: {waveform.shape}")

        # 处理和推理
        start_time = time.time()
        inputs = self.processor(waveform, sampling_rate=16000, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            logits = self.model_asr(**inputs).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.processor.batch_decode(predicted_ids)[0]

        inference_time = time.time() - start_time

        logger.info(f"Transcription: {transcription}")
        logger.info(f"Inference time: {inference_time:.3f}s")

        return transcription

    def speaker_recognition_demo(self, audio_path1, audio_path2):
        """声纹识别演示"""
        logger.info(f"=== Speaker Recognition Demo ===")
        logger.info(f"Audio 1: {audio_path1}")
        logger.info(f"Audio 2: {audio_path2}")

        # 加载音频
        waveform1 = self.load_audio(audio_path1)
        waveform2 = self.load_audio(audio_path2)

        # 提取声纹特征
        def extract_embedding(waveform):
            inputs = self.processor(waveform, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model_speaker(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1)
            return embedding.squeeze()

        # 提取特征
        start_time = time.time()
        embedding1 = extract_embedding(waveform1)
        embedding2 = extract_embedding(waveform2)

        # 计算相似度
        similarity = torch.cosine_similarity(embedding1, embedding2, dim=0)
        inference_time = time.time() - start_time

        logger.info(f"Similarity: {similarity:.4f}")
        logger.info(f"Inference time: {inference_time:.3f}s")

        # 判断是否同一人
        threshold = 0.8
        is_same_speaker = similarity > threshold

        logger.info(f"Same speaker: {is_same_speaker} (threshold: {threshold})")

        return similarity, is_same_speaker

    def audio_analysis_demo(self, audio_path):
        """音频分析演示"""
        logger.info(f"=== Audio Analysis Demo ===")
        logger.info(f"Audio file: {audio_path}")

        # 加载音频
        waveform = self.load_audio(audio_path)

        # 生成可视化
        plt.figure(figsize=(12, 8))

        # 时域波形
        plt.subplot(3, 1, 1)
        plt.plot(waveform.cpu().numpy())
        plt.title('Time Domain Waveform')
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')

        # 频域分析
        plt.subplot(3, 1, 2)
        fft = torch.fft.fft(waveform)
        freqs = torch.fft.fftfreq(len(waveform), 1/16000)
        plt.plot(freqs[:len(freqs)//2].cpu().numpy(),
                torch.abs(fft[:len(fft)//2]).cpu().numpy())
        plt.title('Frequency Spectrum')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')

        # 频谱图
        plt.subplot(3, 1, 3)
        spectrogram = torch.stft(waveform, n_fft=2048, hop_length=512,
                               win_length=2048, return_complex=True)
        magnitude = torch.abs(spectrogram)
        plt.imshow(magnitude.log().cpu().numpy(), aspect='auto',
                  origin='lower', cmap='viridis')
        plt.title('Spectrogram')
        plt.xlabel('Time Frame')
        plt.ylabel('Frequency Bin')

        plt.tight_layout()

        # 保存可视化
        viz_path = Path(audio_path).stem + '_analysis.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        logger.info(f"Analysis saved to: {viz_path}")

        # 计算音频特征
        features = {
            'duration': len(waveform) / 16000,
            'rms': torch.sqrt(torch.mean(waveform ** 2)),
            'peak': torch.max(torch.abs(waveform)),
            'zero_crossings': torch.sum(torch.diff(torch.sign(waveform)) != 0)
        }

        logger.info("Audio features:")
        for key, value in features.items():
            logger.info(f"  {key}: {value:.4f}")

        return features

    def performance_benchmark(self, audio_dir, num_samples=5):
        """性能基准测试"""
        logger.info(f"=== Performance Benchmark ===")

        # 获取音频文件
        audio_files = list(Path(audio_dir).glob('*.wav'))[:num_samples]

        if not audio_files:
            logger.error("No audio files found")
            return

        results = []

        for audio_file in audio_files:
            logger.info(f"Testing: {audio_file}")

            # 测试语音识别
            start_time = time.time()
            transcription = self.speech_recognition_demo(str(audio_file))
            asr_time = time.time() - start_time

            # 测试声纹提取
            start_time = time.time()
            waveform = self.load_audio(str(audio_file))
            inputs = self.processor(waveform, sampling_rate=16000, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model_speaker(**inputs)
                _ = outputs.last_hidden_state.mean(dim=1)

            speaker_time = time.time() - start_time

            results.append({
                'file': audio_file.name,
                'transcription_length': len(transcription),
                'asr_time': asr_time,
                'speaker_time': speaker_time,
                'total_time': asr_time + speaker_time
            })

        # 打印结果
        logger.info("Benchmark Results:")
        for result in results:
            logger.info(f"  {result['file']}: ASR={result['asr_time']:.3f}s, "
                       f"Speaker={result['speaker_time']:.3f}s, "
                       f"Total={result['total_time']:.3f}s")

        # 计算平均
        avg_asr = np.mean([r['asr_time'] for r in results])
        avg_speaker = np.mean([r['speaker_time'] for r in results])
        avg_total = np.mean([r['total_time'] for r in results])

        logger.info(f"Average times - ASR: {avg_asr:.3f}s, Speaker: {avg_speaker:.3f}s, Total: {avg_total:.3f}s")

    def comprehensive_demo(self, audio_path1, audio_path2):
        """综合演示"""
        logger.info("=== Comprehensive WavLM Demo ===")

        # 1. 音频分析
        features1 = self.audio_analysis_demo(audio_path1)

        # 2. 语音识别
        transcription1 = self.speech_recognition_demo(audio_path1)
        transcription2 = self.speech_recognition_demo(audio_path2)

        # 3. 声纹识别
        similarity, is_same = self.speaker_recognition_demo(audio_path1, audio_path2)

        # 4. 总结
        logger.info("=== Demo Summary ===")
        logger.info(f"Audio 1 transcription: {transcription1}")
        logger.info(f"Audio 2 transcription: {transcription2}")
        logger.info(f"Speaker similarity: {similarity:.4f}")
        logger.info(f"Same speaker: {is_same}")

        return {
            'transcription1': transcription1,
            'transcription2': transcription2,
            'similarity': similarity,
            'is_same_speaker': is_same,
            'audio1_features': features1
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='WavLM 演示脚本')
    parser.add_argument('--audio1', type=str, required=True, help='第一个音频文件')
    parser.add_argument('--audio2', type=str, help='第二个音频文件（可选）')
    parser.add_argument('--mode', type=str, default='comprehensive',
                       choices=['asr', 'speaker', 'analysis', 'benchmark', 'comprehensive'],
                       help='演示模式')
    parser.add_argument('--data_dir', type=str, help='数据目录（用于基准测试）')
    parser.add_argument('--samples', type=int, default=5, help='基准测试样本数')
    parser.add_argument('--model', type=str, default='microsoft/wavlm-base',
                       help='模型名称')

    args = parser.parse_args()

    # 创建演示实例
    demo = WavLMDemo(args.model)

    # 根据模式执行不同演示
    if args.mode == 'asr':
        if not args.audio1:
            print("ASR模式需要提供音频文件")
            return
        demo.speech_recognition_demo(args.audio1)

    elif args.mode == 'speaker':
        if not args.audio1 or not args.audio2:
            print("声纹识别模式需要提供两个音频文件")
            return
        demo.speaker_recognition_demo(args.audio1, args.audio2)

    elif args.mode == 'analysis':
        if not args.audio1:
            print("音频分析模式需要提供音频文件")
            return
        demo.audio_analysis_demo(args.audio1)

    elif args.mode == 'benchmark':
        if not args.data_dir:
            print("基准测试模式需要提供数据目录")
            return
        demo.performance_benchmark(args.data_dir, args.samples)

    elif args.mode == 'comprehensive':
        if not args.audio1 or not args.audio2:
            print("综合演示模式需要提供两个音频文件")
            return
        demo.comprehensive_demo(args.audio1, args.audio2)


if __name__ == "__main__":
    main()