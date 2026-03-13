# 声纹识别 API 文档

> **版本**：v1.0.0
> **Base URL**：`https://api.voiceprint.example.com/api/v1`
> **关联文档**：[[声纹识别/云端部署与训练计划]]

---

## 🔐 认证

所有 API 请求需要在 Header 中携带 API Key：

```
Authorization: Bearer YOUR_API_KEY
```

或通过查询参数：

```
?api_key=YOUR_API_KEY
```

---

## 📋 API 端点

### 1. 健康检查

#### GET /health

检查服务健康状态。

**请求**
```http
GET /api/v1/health
```

**响应**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-28T10:00:00Z",
  "model": {
    "name": "wavlm-base-plus",
    "status": "loaded",
    "device": "cuda:0"
  },
  "stats": {
    "total_enrollments": 1523,
    "uptime_seconds": 86400
  }
}
```

---

### 2. 声纹注册

#### POST /enroll

注册新的用户声纹。

**请求**
```http
POST /api/v1/enroll
Content-Type: multipart/form-data

user_id: string (required)
  用户唯一标识，最大长度64字符

audio: file (required)
  音频文件，支持 WAV/MP3 格式
  - 最大文件大小: 10MB
  - 推荐时长: 3-10秒
  - 采样率: 16kHz

device_id: string (optional)
  设备标识，用于按设备分组

api_key: string (required)
  API 认证密钥
```

**curl 示例**
```bash
curl -X POST "https://api.voiceprint.example.com/api/v1/enroll" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "user_id=user_12345" \
  -F "device_id=tv_hisense_001" \
  -F "audio=@/path/to/audio.wav"
```

**响应 (成功)**
```json
{
  "status": "success",
  "user_id": "user_12345",
  "enrollment_id": "enroll_user_12345_a1b2c3d4",
  "message": "声纹注册成功",
  "timestamp": "2026-02-28T10:00:00Z"
}
```

**响应 (活体检测失败)**
```json
{
  "status": "error",
  "error_code": 400,
  "message": "活体检测失败，可能是录音攻击",
  "timestamp": "2026-02-28T10:00:00Z"
}
```

**错误代码**
| 代码 | 描述 |
|-----|------|
| 400 | 音频格式不支持或活体检测失败 |
| 409 | 用户已注册（使用 PUT /enroll/{user_id} 更新） |
| 413 | 音频文件过大 |
| 422 | 请求参数验证失败 |

---

### 3. 声纹验证 (1:1)

#### POST /verify

验证说话人是否为指定用户。

**请求**
```http
POST /api/v1/verify
Content-Type: multipart/form-data

user_id: string (required)
  要验证的用户ID

audio: file (required)
  音频文件

threshold: float (optional)
  相似度阈值，默认 0.85
  - 范围: 0.0 - 1.0
  - 推荐值: 0.80-0.90

api_key: string (required)
  API 认证密钥
```

**curl 示例**
```bash
curl -X POST "https://api.voiceprint.example.com/api/v1/verify" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "user_id=user_12345" \
  -F "threshold=0.85" \
  -F "audio=@/path/to/audio.wav"
```

**响应 (匹配成功)**
```json
{
  "status": "success",
  "request_id": "vprint_a1b2c3d4e5f6",
  "recognition_result": {
    "speaker_id": "user_12345",
    "score": 0.96,
    "confidence": "high",
    "is_matched": true
  },
  "liveness_check": {
    "is_live": true,
    "spoof_score": 0.02,
    "attack_type": "none"
  },
  "timestamp": "2026-02-28T10:00:00Z"
}
```

**响应 (匹配失败)**
```json
{
  "status": "success",
  "request_id": "vprint_a1b2c3d4e5f6",
  "recognition_result": {
    "speaker_id": "user_12345",
    "score": 0.65,
    "confidence": "low",
    "is_matched": false
  },
  "liveness_check": {
    "is_live": true,
    "spoof_score": 0.01,
    "attack_type": "none"
  },
  "timestamp": "2026-02-28T10:00:00Z"
}
```

**置信度等级**
| 等级 | 分数范围 | 描述 |
|-----|---------|------|
| high | ≥ 0.95 | 高度确信 |
| medium | 0.85 - 0.95 | 中等确信 |
| low | < 0.85 | 低确信，建议重试 |

**错误代码**
| 代码 | 描述 |
|-----|------|
| 404 | 用户未注册 |
| 400 | 活体检测失败或攻击检测 |

---

### 4. 声纹辨识 (1:N)

#### POST /identify

从所有已注册用户中识别说话人。

**请求**
```http
POST /api/v1/identify
Content-Type: multipart/form-data

audio: file (required)
  音频文件

top_k: integer (optional)
  返回前K个候选结果，默认 5

threshold: float (optional)
  最低相似度阈值，默认 0.80
  - 低于此阈值的结果将不返回

device_id: string (optional)
  设备标识，仅在该设备注册的用户中识别

api_key: string (required)
  API 认证密钥
```

**curl 示例**
```bash
curl -X POST "https://api.voiceprint.example.com/api/v1/identify" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "top_k=3" \
  -F "threshold=0.80" \
  -F "device_id=tv_hisense_001" \
  -F "audio=@/path/to/audio.wav"
```

**响应 (识别成功)**
```json
{
  "status": "success",
  "request_id": "vprint_a1b2c3d4e5f6",
  "recognition_result": {
    "speaker_id": "user_12345",
    "score": 0.93,
    "confidence": "high",
    "is_matched": true,
    "liveness_check": {
      "is_live": true,
      "spoof_score": 0.01,
      "attack_type": "none"
    }
  },
  "top_candidates": [
    {
      "user_id": "user_12345",
      "score": 0.93
    },
    {
      "user_id": "user_67890",
      "score": 0.72
    },
    {
      "user_id": "user_11111",
      "score": 0.68
    }
  ],
  "timestamp": "2026-02-28T10:00:00Z"
}
```

**响应 (无匹配)**
```json
{
  "status": "no_match",
  "request_id": "vprint_a1b2c3d4e5f6",
  "recognition_result": {
    "speaker_id": null,
    "score": 0.0,
    "is_matched": false,
    "liveness_check": {
      "is_live": true,
      "spoof_score": 0.01,
      "attack_type": "none"
    }
  },
  "top_candidates": [],
  "timestamp": "2026-02-28T10:00:00Z"
}
```

---

### 5. 更新声纹

#### PUT /enroll/{user_id}

更新已存在的用户声纹。

**请求**
```http
PUT /api/v1/enroll/{user_id}
Content-Type: multipart/form-data

audio: file (required)
  音频文件

device_id: string (optional)
  设备标识

api_key: string (required)
  API 认证密钥
```

**curl 示例**
```bash
curl -X PUT "https://api.voiceprint.example.com/api/v1/enroll/user_12345" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "audio=@/path/to/new_audio.wav"
```

**响应**
```json
{
  "status": "success",
  "user_id": "user_12345",
  "enrollment_id": "enroll_user_12345_a1b2c3d4",
  "message": "声纹更新成功",
  "timestamp": "2026-02-28T10:00:00Z"
}
```

---

### 6. 删除声纹

#### DELETE /enroll/{user_id}

删除用户的声纹数据。

**请求**
```http
DELETE /api/v1/enroll/{user_id}

api_key: string (required)
  API 认证密钥
```

**curl 示例**
```bash
curl -X DELETE "https://api.voiceprint.example.com/api/v1/enroll/user_12345" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**响应**
```json
{
  "status": "success",
  "user_id": "user_12345",
  "message": "声纹删除成功",
  "timestamp": "2026-02-28T10:00:00Z"
}
```

---

### 7. 批量操作

#### POST /batch/enroll

批量注册用户声纹。

**请求**
```http
POST /api/v1/batch/enroll
Content-Type: multipart/form-data

users: array of objects (required)
  [
    {
      "user_id": "user_001",
      "audio_file": "audio_001.wav",
      "device_id": "tv_001"
    },
    ...
  ]

api_key: string (required)
```

**响应**
```json
{
  "status": "success",
  "batch_id": "batch_a1b2c3d4",
  "total": 10,
  "succeeded": 8,
  "failed": 2,
  "results": [
    {
      "user_id": "user_001",
      "status": "success",
      "enrollment_id": "enroll_user_001_x1y2z3"
    },
    {
      "user_id": "user_002",
      "status": "error",
      "error": "活体检测失败"
    }
  ],
  "timestamp": "2026-02-28T10:00:00Z"
}
```

---

## 📊 响应状态码

| 状态码 | 描述 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突（如用户已存在） |
| 413 | 请求体过大 |
| 422 | 参数验证失败 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## ⚡ 限流策略

| 计划类型 | 请求限制 |
|---------|---------|
| 免费版 | 100 请求/分钟 |
| 标准版 | 1,000 请求/分钟 |
| 企业版 | 10,000 请求/分钟 |

超出限制将返回 429 状态码：

```json
{
  "status": "error",
  "error_code": 429,
  "message": "请求频率超限，请稍后重试",
  "retry_after": 60
}
```

---

## 🧪 测试环境

**测试 Base URL**：`https://api-test.voiceprint.example.com/api/v1`

**测试 API Key**：`test_key_a1b2c3d4e5f6`

测试环境限制：
- 数据保留时间：24小时后自动清理
- 请求频率：更严格的限制
- 不支持某些高级功能

---

## 📞 SDK 示例

### Python SDK

```python
from voiceprint_client import VoiceprintClient

# 初始化客户端
client = VoiceprintClient(
    api_key="YOUR_API_KEY",
    base_url="https://api.voiceprint.example.com"
)

# 注册声纹
enrollment = client.enroll(
    user_id="user_12345",
    audio_file="/path/to/audio.wav",
    device_id="tv_hisense_001"
)
print(f"Enrollment ID: {enrollment.enrollment_id}")

# 验证声纹
result = client.verify(
    user_id="user_12345",
    audio_file="/path/to/verify.wav",
    threshold=0.85
)
print(f"Matched: {result.is_matched}, Score: {result.score}")

# 辨识声纹
result = client.identify(
    audio_file="/path/to/identify.wav",
    top_k=5
)
print(f"Identified: {result.speaker_id}")
```

### JavaScript SDK

```javascript
import { VoiceprintClient } from '@voiceprint/sdk';

const client = new VoiceprintClient({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://api.voiceprint.example.com'
});

// 注册声纹
const enrollment = await client.enroll({
  userId: 'user_12345',
  audioFile: '/path/to/audio.wav',
  deviceId: 'tv_hisense_001'
});
console.log('Enrollment ID:', enrollment.enrollmentId);

// 验证声纹
const result = await client.verify({
  userId: 'user_12345',
  audioFile: '/path/to/verify.wav',
  threshold: 0.85
});
console.log('Matched:', result.isMatched);
```

---

## 🔗 相关文档

- [[声纹识别/云端部署与训练计划]]
- [[声纹识别/部署手册]]

---

**标签**：#声纹识别 #API #FastAPI #接口文档
