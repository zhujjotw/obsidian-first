# 管道总览（按功能理解）

**AEC（回声消除）**：消掉电视播放回声（远端参考信号必需）
**SE（语音增强）**：抑制环境噪声与残余回声，让单说话人更清晰
**SS（语音分离）**：多人同时说话时，拆分主说话人与干扰人声
**VAD（语音活动检测）**：控制 SE/SS 触发，降低误增强与算力

**完整管道顺序**：
`Mic + SpkRef → AEC → SE → (SS 触发) → VAD Gate → Output`

---

# AEC + 轻量 SE + 轻量 SS + VAD 端侧管道方案（Linux/CPU/TV/<30ms）

## 1) 模块与数据流（单通道）
- 输入：
  - mic_in（麦克风）
  - spk_ref（播放端参考信号，AEC 必需）
- 输出：
  - speech_out（净化后人声，或人声/背景双轨）

**Pipeline 顺序**
1) AEC3（回声消除）
2) SE（残余回声/噪声抑制）
3) SS（轻量分离，仅触发时启用）
4) VAD gate（控制降噪与静音门限）

## 2) 线程模型（低延迟）
- Audio I/O 线程（高优先级）
  - 采集 mic_in + 复制 spk_ref
  - 写入环形缓冲
- DSP 线程（实时优先级）
  - 每 10ms 取一帧 → AEC → SE → (SS) → VAD gate
  - 输出到播放器或上层业务

> 单线程 DSP 流水线最稳，避免上下文切换造成抖动。

## 3) 环形缓冲与对齐（AEC 关键）
- spk_ref 必须与 mic_in 对齐
- 方案：
  - spk_ref 按播放时间戳写入 ring buffer
  - DSP 线程取与 mic_in 同时间戳的一帧作为参考
  - 若无法精准对齐，允许 ±10ms 校准，但要保持稳定

## 4) 触发逻辑（VAD + SS）
- VAD = 1 → SE on
- VAD = 1 且 “多人同时说话概率高” → SS on
- VAD = 0 → SS off，SE 降权或旁路（降低抽吸感）

**多人说话判断（轻量）**
- energy_ratio：语音帧内能量波动大 + 高频能量占比提升
- 或 DTD：双讲检测标志（可来自 AEC3 或轻量估计）

## 5) 伪代码（每 10ms 帧）
```cpp
Frame mic = mic_ring.pop();
Frame ref = spk_ring.pop_aligned(mic.ts);

Frame aec_out = AEC3.process(mic, ref);

bool vad = VAD.process(aec_out);

Frame se_out = vad ? RNNoise.process(aec_out) : aec_out;

bool double_talk = DTD.estimate(se_out);  // 轻量逻辑
Frame ss_out = (vad && double_talk) ? SS.process(se_out) : se_out;

Frame out = vad ? ss_out : noise_floor_gate(ss_out);
output.write(out);
```

## 6) 默认参数建议
- 采样率：16 kHz
- 帧长：10 ms（160 samples）
- AEC3：echo_cancellation=on，high_pass_filter=on，内部 NS=off
- SE：RNNoise 默认参数
- VAD：WebRTC VAD mode=2，平滑窗口 200ms
- SS：仅触发时跑，默认关闭

## 7) 如果有双麦/阵列
- 在 AEC 前插入 Beamforming：
  `Mic Array → BF → AEC → SE → (SS) → VAD`

## 8) C/C++ 模块接口设计（建议）

### 8.1 基础数据结构
```cpp
// 10ms @16kHz = 160 samples, 单声道
struct AudioFrame {
  int16_t* data;
  int      samples;   // 160
  int      sample_rate; // 16000
  int64_t  ts_us;     // 时间戳（微秒）
};
```

### 8.2 统一模块接口
```cpp
class IAudioModule {
public:
  virtual ~IAudioModule() = default;
  virtual bool Init(int sample_rate, int frame_samples) = 0;
  virtual bool Process(const AudioFrame& in, AudioFrame& out) = 0;
  virtual void Reset() = 0;
};
```

### 8.3 AEC3 接口（带参考信号）
```cpp
class Aec3Module {
public:
  bool Init(int sample_rate, int frame_samples);
  bool Process(const AudioFrame& mic_in,
               const AudioFrame& spk_ref,
               AudioFrame& out);
  void Reset();
};
```

### 8.4 SE / SS / VAD 接口
```cpp
class SeModule : public IAudioModule {};
class SsModule : public IAudioModule {};

class VadModule {
public:
  bool Init(int sample_rate, int frame_samples);
  bool IsSpeech(const AudioFrame& in);  // 返回 VAD 判定
};
```

### 8.5 DTD（双讲检测）接口（轻量）
```cpp
class DtdModule {
public:
  bool Init(int sample_rate, int frame_samples);
  bool IsDoubleTalk(const AudioFrame& in);  // 轻量估计
};
```

### 8.6 Pipeline 组装示例
```cpp
class AudioPipeline {
public:
  bool Init(int sample_rate, int frame_samples);
  bool ProcessFrame(const AudioFrame& mic_in,
                    const AudioFrame& spk_ref,
                    AudioFrame& out);

private:
  Aec3Module aec_;
  SeModule   se_;
  SsModule   ss_;
  VadModule  vad_;
  DtdModule  dtd_;
};

bool AudioPipeline::ProcessFrame(const AudioFrame& mic_in,
                                 const AudioFrame& spk_ref,
                                 AudioFrame& out) {
  AudioFrame aec_out, se_out, ss_out;

  if (!aec_.Process(mic_in, spk_ref, aec_out)) return false;

  bool vad = vad_.IsSpeech(aec_out);
  se_out = vad ? se_.Process(aec_out, se_out), se_out : aec_out;

  bool dt = dtd_.IsDoubleTalk(se_out);
  ss_out = (vad && dt) ? (ss_.Process(se_out, ss_out), ss_out) : se_out;

  out = vad ? ss_out : ss_out;  // 可加 noise_floor_gate
  return true;
}
```

### 8.7 环形缓冲接口（对齐参考信号）
```cpp
class RingBuffer {
public:
  void Push(const AudioFrame& frame);
  bool PopAligned(int64_t ts_us, AudioFrame& out); // 按时间戳对齐取帧
};
```

## 9) 推理方案与接口（端侧 CPU）

### 9.1 推理方案总览
- AEC（WebRTC AEC3）：非神经网络，C++ API 直接调用
- VAD（WebRTC VAD）：C 接口，无需推理引擎
- SE（轻量）：RNNoise（纯 C）或 DeepFilterNet‑Lite（ONNX Runtime）
- SS（轻量）：Conv‑TasNet Tiny / SuDORM‑RF Small（ONNX Runtime）

**模型格式**：优先 ONNX，兼容性与性能平衡

### 9.2 统一推理接口
```cpp
struct AudioFrame {
  float*  data;        // [-1, 1] float
  int     samples;     // e.g. 160 for 10ms @16k
  int     sample_rate; // 16000
  int64_t ts_us;       // timestamp
};

class IModel {
public:
  virtual ~IModel() = default;
  virtual bool Init(int sample_rate, int frame_samples) = 0;
  virtual bool Process(const AudioFrame& in, AudioFrame& out) = 0;
  virtual void Reset() = 0;
};
```

### 9.3 AEC / VAD / SE / SS 接口
```cpp
class Aec3Module {
public:
  bool Init(int sample_rate, int frame_samples);
  bool Process(const AudioFrame& mic_in,
               const AudioFrame& spk_ref,
               AudioFrame& out);
  void Reset();
};

class VadModule {
public:
  bool Init(int sample_rate, int frame_samples);
  bool IsSpeech(const AudioFrame& in);
};

class SeModule : public IModel {};
class SsModule : public IModel {};
```

### 9.4 ONNX Runtime 推理模板（SE/SS 共用）
```cpp
class OrtModel : public IModel {
public:
  bool Init(const std::string& onnx_path,
            int sample_rate, int frame_samples,
            int intra_threads = 1);

  bool Process(const AudioFrame& in, AudioFrame& out) override;
  void Reset() override;

private:
  Ort::Env env_{ORT_LOGGING_LEVEL_WARNING, "audio"};
  std::unique_ptr<Ort::Session> session_;
  std::vector<int64_t> input_shape_;
  std::vector<int64_t> output_shape_;
};
```

**建议 ORT 选项**
- SetIntraOpNumThreads(1)
- EnableCpuMemArena()
- SetGraphOptimizationLevel(ORT_ENABLE_ALL)

### 9.5 推理流程（每 10ms 帧）
```cpp
Frame mic = mic_ring.pop();
Frame ref = spk_ring.pop_aligned(mic.ts_us);

Frame aec_out = aec.Process(mic, ref);

bool vad = vad.IsSpeech(aec_out);

Frame se_out = vad ? se.Process(aec_out, se_out) : aec_out;

bool dt = dtd.IsDoubleTalk(se_out);  // 轻量逻辑
Frame ss_out = (vad && dt) ? ss.Process(se_out, ss_out) : se_out;

output.write(ss_out);
```

### 9.6 SE / SS 推理要点
- SE（RNNoise）：无推理引擎、直接 C 调用
- SE（DeepFilterNet‑Lite）：按 chunk 推理（20–40ms）
- SS（轻量）：固定长度 chunk + overlap‑add 回拼

## 10) WebRTC AEC3 / VAD 开源链接

**AEC3（C++）源码入口**
- 目录：`modules/audio_processing/aec3/`
- 源码链接：
  - https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_processing/aec3/

**VAD（C API + C++ 封装）源码**
- C++ 封装：`common_audio/vad/vad.cc`
  - https://webrtc.googlesource.com/src/+/2406aaf475a6cf34facb0050ac79970a8b31b90c/common_audio/vad/vad.cc
- C API 头文件：`common_audio/vad/include/vad.h`
  - https://webrtc.googlesource.com/src/+/f54860e9ef0b68e182a01edc994626d21961bc4b/common_audio/vad/include/vad.h

## 11) 项目面试题参考回答（高分版）

**Q1：你如何把“指令→脚本→分镜→图生视频→配音→合成”串成可扩展流水线？**
A：我把整条链路拆成 6 个独立模块：LLM 脚本、分镜结构化、图生视频、插帧/超分、TTS、合成封装。模块间只传结构化 JSON（分镜/角色/时间码/素材清单），保证可替换与可追踪。调度层用 DAG + 任务队列实现并行与重试，所有产物带版本号与缓存键，失败可以局部回滚，保障端到端稳定。

**Q2：SVD 的输出帧数与 fps 的关系是什么？为什么需要插帧？**
A：SVD 输出的帧数是固定的（如 14/25 帧），fps 只是播放速度，所以要做到 30/60fps 必须做插帧或多段拼接。插帧本质是合成中间帧提升时间分辨率，能让 8–12fps 的基础视频提升到 30–60fps，减少抖动。

**Q3：FlowNet2 光流如何用于插帧？**
A：FlowNet2 估计相邻帧的像素级运动矢量（前向/后向光流），插帧时根据光流把两帧“对齐”并合成中间帧。关键风险是遮挡、错配导致鬼影和闪烁，所以需要做遮挡处理与融合权重控制。

**Q4：音色克隆 10s 微调的关键在什么？如何避免过拟合？**
A：关键是把说话人 timbre 特征对齐到目标音色，同时避免模型记住具体语句。做法是清洗数据、控制步数、加入正则/早停，并用多句式切片增强。评估上结合主观听评和相似度指标，确保“像但不死板”。

**Q5：多轨合成里，音频/视频/字幕如何对齐？**
A：以音频时间轴为主，所有素材转为统一时间戳体系（ms 或帧时间码）。字幕根据音频对齐，视频帧按时间戳对齐或做 time‑stretch。合成前先做 trim/pad 校正，最后用 FFmpeg 统一 mux，保证对齐可控。

**Q6：如何控制 3–5s 视频到 30–60fps 的性能成本？**
A：采用“低分辨率生成 → 插帧 → 超分”的流水线，插帧放在低分辨率以降低计算。并行化分段生成，复用模型权重与缓存，推理使用 FP16/量化，确保单卡吞吐稳定。

**Q7：如何处理生成质量不稳定（闪烁、人物漂移）？**
A：通过稳定化策略组合：保持同一角色参考图/seed，控制分镜长度，插帧前做去闪烁或在插帧后做 temporal smoothing。对漂移严重的段落，采用短片段重生成并替换。

**Q8：如何保证整条链路可观测、可追踪、可回放？**
A：每个模块都输出结构化日志（输入/输出 hash、模型版本、耗时、失败原因），并将关键产物存档。全链路打 traceId，可回放任何阶段。监控维度包括成功率、平均耗时、质量评分与重试率。

**Q9：如果客户要多语言、多风格、多规格如何快速适配？**
A：用配置化 pipeline 做模板化扩展，语言/风格/规格都通过策略层路由到不同模型与参数集。通过“场景配置 + 资源包”方式上线新业务，做到最小改动可复用。

**Q10：项目中你做的最关键优化是什么？为什么？**
A：我认为最关键的是“插帧 + 流水线并行化”。插帧把 8–12fps 提升到 30–60fps，显著改善观感；并行化让脚本生成、视频生成、音频合成流水作业，显著提升吞吐并降低单条成本，这是产品落地的核心。

