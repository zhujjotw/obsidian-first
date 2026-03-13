---
tags: [AI框架/LangGraph, Python, 状态管理, Agent开发, 开发指南]
created: 2026-03-13
---

# LangGraph State 对象设计指南

## State 基本概念

State 是 LangGraph 中节点间传递的数据结构，使用 `TypedDict` 定义。

```python
from typing import TypedDict, List, Annotated
from operator import add

# 基础 State 定义
class AgentState(TypedDict):
    messages: List[dict]
    user_input: str
    response: str
```

---

## 设计原则

### 1. 最小化原则

只包含节点间真正需要传递的数据

```python
# ✅ 好的设计
class MinimalState(TypedDict):
    query: str
    results: List[str]

# ❌ 不好的设计（包含不需要的数据）
class BloatedState(TypedDict):
    query: str
    results: List[str]
    huge_unused_data: dict  # 不需要传递
```

### 2. 类型明确

使用明确的类型注解

```python
from typing import Literal, Optional

class TypedState(TypedDict):
    status: Literal["pending", "processing", "completed"]
    error: Optional[str]
    retry_count: int
```

### 3. 使用 Annotated 处理累积数据

对于需要累积的字段（如消息列表）

```python
from typing import Annotated
from operator import add

class MessageState(TypedDict):
    # 每次执行会追加，而不是覆盖
    messages: Annotated[List[dict], add]
    # 其他字段正常覆盖
    current_step: str
```

---

## 常见设计模式

### 模式 1: 对话式 Agent

```python
from typing import TypedDict, List, Annotated
from operator import add

class ChatState(TypedDict):
    """对话状态"""
    messages: Annotated[List[dict], add]  # 累积对话历史
    user_input: str                       # 当前用户输入
    context: dict                         # 对话上下文
    next_action: str                      # 下一步动作
```

### 模式 2: RAG 检索增强

```python
class RAGState(TypedDict):
    """RAG 状态"""
    question: str                         # 用户问题
    retrieved_docs: List[dict]            # 检索到的文档
    context: str                          # 组装的上下文
    answer: str                           # 生成的答案
    sources: List[str]                    # 引用来源
```

### 模式 3: 多 Agent 协作

```python
class MultiAgentState(TypedDict):
    """多 Agent 协作状态"""
    task: str                             # 主任务
    assigned_to: List[str]                # 分配给哪些 agent
    agent_outputs: dict                   # 各 agent 的输出
    final_result: str                     # 最终结果
    status: Literal["pending", "in_progress", "completed", "failed"]
```

### 模式 4: 工具调用 Agent

```python
class ToolAgentState(TypedDict):
    """工具调用状态"""
    messages: Annotated[List[dict], add]
    tool_calls_made: List[dict]           # 已调用的工具
    tool_results: dict                    # 工具执行结果
    next_tool: Optional[str]              # 下一个要调用的工具
    max_iterations: int                   # 最大迭代次数
```

### 模式 5: 条件分支状态

```python
class ConditionalState(TypedDict):
    """条件分支状态"""
    input_data: dict
    classification: str                   # 分类结果
    route: Literal["route_a", "route_b", "route_c"]  # 决定路由
    output: dict
```

---

## 实际使用示例

### 完整的 RAG 应用示例

```python
from typing import TypedDict, List, Annotated
from operator import add
from langgraph.graph import StateGraph, END

class RAGState(TypedDict):
    question: str
    retrieved_docs: List[dict]
    context: str
    answer: str
    sources: List[str]

# 定义节点
def retrieve_node(state: RAGState):
    """检索文档"""
    docs = vector_store.search(state["question"])
    return {
        "retrieved_docs": docs,
        "sources": [doc["source"] for doc in docs]
    }

def generate_context_node(state: RAGState):
    """组装上下文"""
    context = "\n".join([doc["content"] for doc in state["retrieved_docs"]])
    return {"context": context}

def answer_node(state: RAGState):
    """生成答案"""
    prompt = f"Context: {state['context']}\nQuestion: {state['question']}"
    answer = llm.invoke(prompt)
    return {"answer": answer}

# 构建图
workflow = StateGraph(RAGState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("generate_context", generate_context_node)
workflow.add_node("answer", answer_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate_context")
workflow.add_edge("generate_context", "answer")
workflow.add_edge("answer", END)

app = workflow.compile()
```

### 多 Agent 协作示例

```python
class ResearchState(TypedDict):
    research_topic: str
    researcher_findings: dict
    writer_draft: str
    reviewer_feedback: List[str]
    final_output: str
    iteration: int

def researcher_node(state: ResearchState):
    findings = research_agent.search(state["research_topic"])
    return {"researcher_findings": findings}

def writer_node(state: ResearchState):
    draft = writer_agent.write(state["researcher_findings"])
    return {"writer_draft": draft}

def reviewer_node(state: ResearchState):
    feedback = reviewer_agent.review(state["writer_draft"])
    return {"reviewer_feedback": feedback}

# 条件边：决定是否需要修改
def should_continue(state: ResearchState):
    if len(state["reviewer_feedback"]) == 0:
        return "end"
    return "writer"
```

---

## 高级技巧

### 1. 嵌套 State 处理复杂结构

```python
from typing import TypedDict

class DocumentMetadata(TypedDict):
    source: str
    page: int
    confidence: float

class ProcessedDocument(TypedDict):
    content: str
    metadata: DocumentMetadata

class ComplexState(TypedDict):
    documents: List[ProcessedDocument]
    summary: str
```

### 2. 使用 Pydantic 模型（LangGraph 0.2+）

```python
from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    role: str
    content: str
    timestamp: float

class PydanticState(BaseModel):
    messages: List[Message]
    current_step: str
    error_message: str = ""
```

### 3. 状态缩减（减少 Token 消耗）

```python
def compress_messages(messages: List[dict]) -> List[dict]:
    """只保留最近的重要消息"""
    # 只保留最后 5 条 + 系统提示
    if len(messages) > 6:
        return [messages[0]] + messages[-5:]
    return messages

def node_with_compression(state):
    compressed = compress_messages(state["messages"])
    return {"messages": compressed}
```

---

## 最佳实践

| 实践 | 说明 |
|------|------|
| 使用 TypedDict | 提供类型检查和 IDE 提示 |
| 命名清晰 | state 字段名应清晰表达含义 |
| 避免嵌套过深 | 超过 3 层嵌套难以维护 |
| 分离关注点 | 不同类型的数据分开存储 |
| 文档化 | 为复杂 state 添加 docstring |
| 考虑序列化 | 避免存储不可序列化的对象 |

---

## 常见错误

```python
# ❌ 错误 1: 存储不可序列化的对象
class BadState(TypedDict):
    database_connection: object  # 无法序列化

# ✅ 正确做法
class GoodState(TypedDict):
    connection_string: str  # 存储配置而非对象

# ❌ 错误 2: 忘记使用 Annotated 导致覆盖
class BadMessageState(TypedDict):
    messages: List[dict]  # 每次会覆盖而非追加

# ✅ 正确做法
class GoodMessageState(TypedDict):
    messages: Annotated[List[dict], add]

# ❌ 错误 3: State 过于庞大
class HugeState(TypedDict):
    # 包含 50+ 个字段，难以维护
    ...

# ✅ 正确做法：拆分成多个子图或使用嵌套结构
```

---

## State 与 Checkpoint 的关系

State 可以通过 Checkpoint 持久化，实现断点续传和时间旅行：

```python
from langgraph.checkpoint.memory import MemorySaver

# 创建带持久化的图
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# 使用 thread_id 持久化状态
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"question": "你好"}, config)

# 可以恢复之前的对话状态
result = app.invoke({"question": "再见"}, config)
```

---

## State 更新机制

### 覆盖更新（默认）

```python
def my_node(state):
    return {"current_value": "new_value"}  # 完全覆盖
```

### 累积更新（Annotated）

```python
from operator import add

class AccumulatingState(TypedDict):
    items: Annotated[List[str], add]  # 追加而非覆盖

def my_node(state):
    return {"items": ["new_item"]}  # 追加到列表
```

### 删除字段

```python
from typing import TypedDict, Annotated
from operator import itemgetter

def my_node(state):
    # 返回 None 可以删除字段（某些实现）
    return {"field_to_remove": None}
```

---

## 完整示例：客服机器人

```python
from typing import TypedDict, List, Annotated, Literal
from operator import add

class CustomerServiceState(TypedDict):
    """客服机器人状态"""
    messages: Annotated[List[dict], add]
    user_query: str
    intent: Literal["faq", "complaint", "request", "unknown"]
    confidence: float
    retrieved_answer: str
    needs_human: bool
    ticket_id: str

def classify_intent(state: CustomerServiceState):
    """分类用户意图"""
    # ... 分类逻辑
    return {
        "intent": "faq",
        "confidence": 0.95
    }

def retrieve_answer(state: CustomerServiceState):
    """检索FAQ答案"""
    # ... 检索逻辑
    return {"retrieved_answer": "答案内容"}

def escalate_to_human(state: CustomerServiceState):
    """升级到人工"""
    # ... 创建工单
    return {
        "needs_human": True,
        "ticket_id": "T-12345"
    }

def route_intent(state: CustomerServiceState):
    """根据意图路由"""
    if state["confidence"] < 0.7 or state["intent"] == "complaint":
        return "escalate"
    return "answer"
```

---

**最后更新**: 2026-03-13
