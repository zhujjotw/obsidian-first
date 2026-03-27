# ComfyUI 学习笔记

## 基础概念

- **Node（节点）**：每个操作单元，如加载模型、采样、解码等
- **Workflow（工作流）**：节点连接组成的完整流程，可保存为 JSON
- **Link（连接线）**：节点间的数据流，颜色代表数据类型

## 模型相关

- **Checkpoint**：主模型文件（.safetensors/.ckpt），包含 UNet + VAE + CLIP
- **VAE**：图像编码/解码器，latent space 和像素空间的转换
- **CLIP**：文本编码器，将 prompt 转为 embedding
- **LoRA**：轻量微调模型，叠加在主模型上
- **ControlNet**：控制生成结构（姿势、边缘、深度等）

## 生成流程

- **Latent Image**：潜空间中的图像表示
- **KSampler**：核心采样节点，控制去噪过程
  - `steps`：采样步数
  - `cfg`：提示词引导强度
  - `sampler/scheduler`：采样算法（euler、dpm++ 等）
  - `denoise`：去噪强度（img2img 时关键）
- **Positive/Negative Prompt**：正负向提示词

核心主线：`CLIP → KSampler → VAE Decode`

## 进阶概念

- **img2img**：以图生图，通过 VAE Encode 输入图像
- **Inpainting**：局部重绘，需要 mask
- **Upscale**：放大，分 latent 放大和像素放大两种
- **IPAdapter**：图像风格/内容参考
- **Custom Node**：社区扩展节点（通过 ComfyUI-Manager 安装）

## IPAdapter

IPAdapter（Image Prompt Adapter）让模型参考图像风格或内容来生成图片。

### 工作原理

```
参考图 → CLIP Image Encoder → Image Embedding
                                      ↓
文字 Prompt → CLIP Text Encoder → Text Embedding
                                      ↓
                              KSampler（两者融合）→ 生成图
```

通过在 UNet 的 attention 层插入适配器，把图像特征注入生成过程，不改变原始模型权重。

### 用途

- 风格迁移：参考一张画风图，生成同风格的新内容
- 人物一致性：保持角色脸部/外貌一致（配合 FaceID 变体）
- 构图参考：参考图的构图/色调影响输出

### 关键参数

- `weight`：参考图影响强度，0~1，通常 0.5~0.8
- `start_at / end_at`：在哪些采样步骤生效

### 常见变体

- **IPAdapter Plus**：特征提取更精细
- **IPAdapter FaceID**：专门针对人脸一致性
- **IPAdapter Style Transfer**：专注风格而非内容

> 需安装 `ComfyUI_IPAdapter_plus` 自定义节点及对应模型权重
