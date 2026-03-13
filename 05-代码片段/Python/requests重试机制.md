---
type: snippet
language: python
category: 网络请求
tags: [代码片段/Python, 重试, requests]
created: 2025-02-28
---

# Python requests 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
from requests.exceptions import RequestException

@retry(
    stop=stop_after_attempt(3),           # 最多重试3次
    wait=wait_exponential(                # 指数退避
        multiplier=1,                     # 基础等待时间
        min=4,                            # 最小等待4秒
        max=10                            # 最大等待10秒
    ),
    retry=retry_if_exception_type(        # 只重试特定异常
        (requests.exceptions.Timeout,
         requests.exceptions.ConnectionError)
    )
)
def fetch_with_retry(url: str, data: dict = None) -> dict:
    """
    带重试机制的HTTP请求

    Args:
        url: 请求URL
        data: 请求数据

    Returns:
        响应JSON数据

    Raises:
        RequestException: 重试3次后仍然失败
    """
    session = requests.Session()

    try:
        response = session.post(
            url,
            json=data,
            timeout=(30, 60)  # (连接超时, 读取超时)
        )
        response.raise_for_status()
        return response.json()

    except RequestException as e:
        print(f"请求失败: {e}")
        raise
```

---

## 📝 说明

**功能描述**：为 requests 请求添加指数退避重试机制

**使用场景**：
- 调用外部 API
- 网络不稳定环境
- 需要容错的服务调用

---

## 📖 示例

### 输入

```python
# 正常调用
result = fetch_with_retry(
    "https://api.example.com/create",
    data={"name": "test"}
)

# 失败重试场景
# 第1次失败 -> 等待4秒
# 第2次失败 -> 等待8秒
# 第3次失败 -> 等待10秒后抛出异常
```

### 输出

```
成功返回: {'status': 'success', 'id': '123'}

或重试3次后抛出: RequestException
```

---

## 🔗 相关

- 语言文档: [[Python]]
- 相关项目: [[pm_create_factory_contact_doc]]
- 相关笔记: [[PLM接口超时问题]]
- 官方文档: [tenacity](https://tenacity.readthedocs.io/)

---

**创建时间**: 2025-02-28
