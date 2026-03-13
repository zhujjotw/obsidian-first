---
tags: [AI模型/计算机视觉, 模型/SAM3, Meta, 图像分割, 部署教程]
created: 2026-03-13
---

# SAM3 模型分析与部署

## 概述

**SAM3 (Segment Anything with Concepts)** 是 Meta AI 发布的统一基础模型，用于图像和视频中的可提示分割。

### 基本信息

| 属性 | 值 |
|------|-----|
| 全称 | Segment Anything with Concepts |
| 发布方 | Meta AI (Facebook Research) |
| 参数量 | 848M |
| 发布时间 | 2025年 |
| GitHub | [facebookresearch/sam3](https://github.com/facebookresearch/sam3) |

### 演进路径

```
SAM1 → SAM2 (统一视频/图像) → SAM3 (语义+视觉融合)
```

---

## 核心原理

### 架构特点

1. **双编码器-解码器Transformer架构**
   - 视觉编码器处理图像/视频
   - 多模态融合层
   - 解码器输出分割掩码

2. **Promptable Concept Segmentation (PCS)**
   - 支持文本提示: "红苹果"、"条纹猫"
   - 支持视觉提示: 点、框、掩码
   - 支持图像示例提示

3. **Presence Token机制**
   - 改进相关文本提示的区分能力
   - 例如区分"穿白色球衣的球员"vs"穿红色球衣的球员"

### 核心突破

| 维度 | SAM2 | SAM3 |
|------|------|------|
| 输入模态 | 仅视觉 | 视觉 + 语言 |
| 理解层次 | 视觉识别 | 语义理解 |
| 任务类型 | 分割 | 统一检测、分割、跟踪 |
| 概念覆盖 | - | 约400万概念 |
| 性能 | - | 100个检测对象30ms |

### 性能指标

**图像分割性能** (SA-Co/Gold benchmark):

| 模型 | cgF1 |
|------|------|
| Human | 72.8 |
| OWLv2 | 24.6 |
| DINO-X | 21.3 |
| Gemini 2.5 | 13.0 |
| **SAM3** | **54.1** |

**视频分割性能** (SA-V test):

| 模型 | cgF1 | pHOTA |
|------|------|-------|
| Human | 53.1 | 70.5 |
| **SAM3** | **30.3** | **58.0** |

---

## 环境要求

| 组件 | 要求 |
|------|------|
| Python | 3.12+ |
| PyTorch | 2.7+ |
| CUDA | 12.6+ |
| GPU | CUDA兼容显卡 (建议16GB+显存) |

---

## 部署步骤

### 1. 创建Conda环境

```bash
conda create -n sam3 python=3.12
conda deactivate
conda activate sam3
```

### 2. 安装PyTorch (CUDA 12.6)

```bash
pip install torch==2.7.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```

### 3. 克隆仓库并安装

```bash
git clone https://github.com/facebookresearch/sam3.git
cd sam3
pip install -e .
```

### 4. 安装额外依赖

```bash
# 运行示例notebook
pip install -e ".[notebooks]"

# 开发环境
pip install -e ".[train,dev]"
```

### 5. 获取模型权重

**⚠️ 重要**: 需要先在Hugging Face申请权限

1. 访问 [SAM3 Hugging Face](https://huggingface.co/facebook/sam3)
2. 接受模型许可证
3. 登录Hugging Face:

```bash
# 安装huggingface-cli
pip install huggingface_hub

# 登录（需要access token）
huggingface-cli login
```

---

## 使用示例

### 图像分割

```python
import torch
from PIL import Image
from sam3.model_builder import build_sam3_image_model
from sam3.model.sam3_image_processor import Sam3Processor

# 加载模型
model = build_sam3_image_model()
processor = Sam3Processor(model)

# 加载图像
image = Image.open("path/to/image.jpg")
inference_state = processor.set_image(image)

# 文本提示分割
output = processor.set_text_prompt(
    state=inference_state,
    prompt="一只红色的猫"
)

# 获取结果
masks, boxes, scores = output["masks"], output["boxes"], output["scores"]
```

### 视频分割

```python
from sam3.model_builder import build_sam3_video_predictor

video_predictor = build_sam3_video_predictor()
video_path = "path/to/video.mp4"

# 启动会话
response = video_predictor.handle_request(
    request=dict(
        type="start_session",
        resource_path=video_path,
    )
)

# 添加文本提示
response = video_predictor.handle_request(
    request=dict(
        type="add_prompt",
        session_id=response["session_id"],
        frame_index=0,
        text="穿白色球衣的球员",
    )
)

output = response["outputs"]
```

---

## 示例Notebook

| 文件 | 说明 |
|------|------|
| `sam3_image_predictor_example.ipynb` | 图像文本+框提示 |
| `sam3_video_predictor_example.ipynb` | 视频文本提示+交互式点选 |
| `sam3_image_batched_inference.ipynb` | 批量推理 |
| `sam3_agent.ipynb` | SAM3 Agent复杂文本分割 |

运行方式:

```bash
jupyter notebook examples/sam3_image_predictor_example.ipynb
```

---

## 支持的任务

1. **PCS (Point-level Concept Segmentation)**: 概念级别的点分割
2. **PVS (Panoptic Video Segmentation)**: 全景视频分割
3. **统一目标检测、分割、跟踪**

---

## 应用场景

- **图像编辑**: 通过文本描述选择编辑对象
- **视频分析**: 自动跟踪特定概念的所有实例
- **内容审核**: 识别并标记特定类型的违规内容
- **数据标注**: 辅助构建训练数据集
- **电商应用**: 商品识别和分割
- **医疗影像**: 病变区域识别

---

## 注意事项

1. **模型较大**: 848M参数，建议使用GPU
2. **Hugging Face认证**: 必须先登录才能下载模型
3. **CUDA版本**: 必须使用CUDA 12.6+
4. **内存需求**: 推荐至少16GB显存
5. **许可证**: 使用SAM3 License

---

## 参考资源

- [GitHub官方仓库](https://github.com/facebookresearch/sam3)
- [SAM3快速上手指南 - CSDN](https://blog.csdn.net/gitblog_02759/article/details/145138008)
- [SAM3文本提示分割 - 知乎](https://zhuanlan.zhihu.com/p/1995541507541852701)
- [Meta AI官方页面](https://ai.meta.com/research/sam3/)
- [论文](https://arxiv.org/abs/2511.16719)

---

## BibTeX引用

```bibtex
@misc{carion2025sam3segmentconcepts,
      title={SAM 3: Segment Anything with Concepts},
      author={Nicolas Carion and Laura Gustafson and Yuan-Ting Hu and Shoubhik Debnath and Ronghang Hu and Didac Suris and Chaitanya Ryali and Kalyan Vasudev Alwala and Haitham Khedr and Andrew Huang and Jie Lei and Tengyu Ma and Baishan Guo and Arpit Kalla and Markus Marks and Joseph Greer and Meng Wang and Peize Sun and Roman Rädle and Triantafyllos Afouras and Effrosyni Mavroudi and Katherine Xu and Tsung-Han Wu and Yu Zhou and Liliane Momeni and Rishi Hazra and Shuangrui Ding and Sagar Vaze and Francois Porcher and Feng Li and Siyuan Li and Aishwarya Kamath and Ho Kei Cheng and Piotr Dollár and Nikhila Ravi and Kate Saenko and Pengchuan Zhang and Christoph Feichtenhofer},
      year={2025},
      eprint={2511.16719},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2511.16719},
}
```

---

**最后更新**: 2026-03-13
