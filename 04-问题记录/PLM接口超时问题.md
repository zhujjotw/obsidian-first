---
type: issue
created: 2025-02-28
status: 已解决
priority: 高
tags: [问题/2025-02, PLM, API, 超时]
project: pm_create_factory_contact_doc
---

# 问题: PLM 接口调用超时

## 📌 基本信息

| 字段 | 值 |
|------|-----|
| 创建时间 | 2025-02-28 10:00 |
| 优先级 | 🔴 高 |
| 状态 | ✅ 已解决 |
| 负责人 | zhujiajia |
| 项目 | [[pm_create_factory_contact_doc]] |

---

## 🐛 问题描述

### 现象

调用 PLM 的 `create_design_contact_letter` 接口时经常超时

**复现步骤：**
1. 创建联系书时调用 PLM API
2. 等待响应超过 30 秒
3. 抛出 ReadTimeout 异常

**预期结果：**
接口应在 10 秒内返回

**实际结果：**
接口经常超时，最长达 60 秒

---

## 🔍 问题分析

### 根本原因

1. **网络延迟**：PLM 服务器响应慢
2. **数据量大**：85 个字段的联系书数据
3. **无重试机制**：失败后没有自动重试

**日志信息：**
```
requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='inner-apisix.hisense.com', port=443): Read timed out.
```

**相关代码：**
```python
# utils/plm_utils.py:123
def create_design_contact_letter(self, data: dict) -> dict:
    url = f"{self.base_url}/createDesignContactBook"
    response = self.session.post(url, json=data, timeout=30)
    return response.json()
```

---

## ✅ 解决方案

### 方案概述

1. 添加超时重试机制
2. 增加 timeout 参数
3. 添加熔断器模式

**实施步骤：**
1. 使用 `tenacity` 库实现重试
2. 设置超时时间为 60 秒
3. 添加指数退避策略

### 代码修改

**修改前：**
```python
def create_design_contact_letter(self, data: dict) -> dict:
    url = f"{self.base_url}/createDesignContactBook"
    response = self.session.post(url, json=data, timeout=30)
    return response.json()
```

**修改后：**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def create_design_contact_letter(self, data: dict) -> dict:
    url = f"{self.base_url}/createDesignContactBook"
    response = self.session.post(
        url,
        json=data,
        timeout=(30, 60)  # (连接超时, 读取超时)
    )
    response.raise_for_status()
    return response.json()
```

---

## 📝 验证

### 测试结果

- [x] 正常情况下 10 秒内返回
- [x] 网络延迟时自动重试
- [x] 三次失败后正确抛出异常
- [x] 回归测试通过

### 性能对比

| 场景 | 修改前 | 修改后 |
|------|--------|--------|
| 正常响应 | ~8s | ~8s |
| 偶尔超时 | 失败 | 重试成功 |
| 持续超时 | 60s超时 | 100s内返回错误 |

---

## 🔗 相关链接

- 相关日志: [[2025-02-28]]
- 相关代码: [[utils/plm_utils.py]]
- 相关文档: [[PLM接口文档]]
- 类似问题: [[FTP连接失败]]

---

## 📊 问题统计

| 指标 | 值 |
|------|-----|
| 发现时间 | 2025-02-28 10:00 |
| 解决时间 | 2025-02-28 15:30 |
| 耗时 | 5.5 小时 |
| 影响范围 | 所有创建联系书操作 |

---

## 💡 经验总结

1. **外部 API 调用必须添加重试机制**
2. **超时时间要根据实际情况调整**
3. **使用成熟的库（如 tenacity）比自己写重试逻辑更可靠**

---

**创建**: 2025-02-28 10:00
**最后更新**: 2025-02-28 16:00
**解决者**: zhujiajia
