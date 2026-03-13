"""
WavLM 快速运行演示
用于快速体验 WavLM 的主要功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from demo_script import WavLMDemo
from sample_data_generator import SampleDataGenerator

def create_sample_data():
    """创建示例数据"""
    print("🎵 创建示例数据...")
    generator = SampleDataGenerator()

    # 创建测试数据集
    os.makedirs("sample_data", exist_ok=True)
    generator.create_test_dataset("sample_data", num_samples=5)

    # 创建声纹识别测试对
    os.makedirs("sample_pairs", exist_ok=True)
    generator.create_test_pairs("sample_pairs", num_pairs=3)

    print("✅ 示例数据创建完成")
    return "sample_data"

def run_asr_demo(audio_path):
    """运行语音识别演示"""
    print(f"\n🎤 语音识别演示: {audio_path}")

    try:
        demo = WavLMDemo()
        transcription = demo.speech_recognition_demo(audio_path)
        print(f"识别结果: {transcription}")
        return transcription
    except Exception as e:
        print(f"❌ 语音识别失败: {str(e)}")
        return None

def run_speaker_demo(audio_path1, audio_path2):
    """运行声纹识别演示"""
    print(f"\n👥 声纹识别演示:")
    print(f"  音频1: {audio_path1}")
    print(f"  音频2: {audio_path2}")

    try:
        demo = WavLMDemo()
        similarity, is_same = demo.speaker_recognition_demo(audio_path1, audio_path2)
        print(f"相似度: {similarity:.4f}")
        print(f"同一人: {'是' if is_same else '否'}")
        return similarity, is_same
    except Exception as e:
        print(f"❌ 声纹识别失败: {str(e)}")
        return None, None

def run_analysis_demo(audio_path):
    """运行音频分析演示"""
    print(f"\n📊 音频分析演示: {audio_path}")

    try:
        demo = WavLMDemo()
        features = demo.audio_analysis_demo(audio_path)
        print("✅ 音频分析完成")
        return features
    except Exception as e:
        print(f"❌ 音频分析失败: {str(e)}")
        return None

def run_comprehensive_demo():
    """运行综合演示"""
    print("\n🚀 综合演示开始...")

    # 获取示例音频文件
    sample_data_dir = "sample_data"
    sample_pairs_dir = "sample_pairs"

    if not os.path.exists(sample_data_dir):
        print("⚠️ 未找到示例数据，正在创建...")
        create_sample_data()

    # 获取音频文件
    audio_files = list(Path(sample_data_dir).glob("*.wav"))
    if len(audio_files) < 2:
        print("❌ 需要至少两个音频文件")
        return

    # 运行各种演示
    results = {}

    # 1. 语音识别
    print("\n1. 语音识别测试")
    for i, audio_file in enumerate(audio_files[:3]):
        transcription = run_asr_demo(str(audio_file))
        results[f'audio_{i}_transcription'] = transcription

    # 2. 声纹识别
    print("\n2. 声纹识别测试")
    if len(audio_files) >= 2:
        similarity, is_same = run_speaker_demo(str(audio_files[0]), str(audio_files[1]))
        results['speaker_similarity'] = similarity
        results['is_same_speaker'] = is_same

    # 3. 音频分析
    print("\n3. 音频分析测试")
    if audio_files:
        features = run_analysis_demo(str(audio_files[0]))
        results['audio_features'] = features

    print("\n🎉 综合演示完成!")
    return results

def main():
    """主函数"""
    print("🎯 WavLM 快速演示")
    print("=" * 50)

    # 检查依赖
    try:
        import torch
        import transformers
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {str(e)}")
        print("请运行: pip install torch torchaudio transformers")
        return

    # 运行演示
    try:
        results = run_comprehensive_demo()

        # 显示总结
        print("\n" + "=" * 50)
        print("📋 演示总结:")
        if results:
            for key, value in results.items():
                if key.endswith('_transcription') and value:
                    print(f"  {key}: {value}")
                elif key == 'speaker_similarity' and value:
                    print(f"  {key}: {value:.4f}")
                elif key == 'is_same_speaker' and value is not None:
                    print(f"  {key}: {'是' if value else '否'}")
                elif key == 'audio_features' and value:
                    print(f"  {key}: 完整分析")

        print("\n🎊 演示完成! 查看生成的图像文件了解详细信息。")

    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        print("请检查音频文件格式和网络连接")

if __name__ == "__main__":
    main()