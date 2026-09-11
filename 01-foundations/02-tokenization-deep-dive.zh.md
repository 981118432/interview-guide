# Tokenization 深入理解

Tokenization 是把文本转换为模型能够处理的离散单元（token）的过程。它会直接影响模型能力、成本和性能。

## 目录

- [Tokenization 为什么重要](#tokenization-为什么重要)
- [Tokenization 算法](#tokenization-算法)
- [词表设计的权衡](#词表设计的权衡)
- [特殊 token](#特殊-token)
- [多语言 Tokenization](#多语言-tokenization)
- [用于成本估算的 token 计数](#用于成本估算的-token-计数)
- [常见 Tokenization 问题](#常见-tokenization-问题)
- [实用 Tokenization 模式](#实用-tokenization-模式)
- [面试问答](#面试问答)
- [参考资料](#参考资料)

---

## Tokenization 为什么重要

### 对系统设计的影响

1. **成本**：LLM API 按 token 收费，Tokenization 效率会直接影响成本。
2. **上下文限制**：决定文本能否放入上下文的是 token 数，而不是词数。
3. **模型能力**：有些任务（数字符、字谜）之所以困难，是因为 Tokenization 的方式造成的。
4. **一致性**：同一段文本在不同模型中可能被切分成不同 token。

### 对理解 LLM 行为的影响

**经典面试题**：为什么 GPT 很难数清 “strawberry” 中有几个字母？

因为 “strawberry” 会被切分成多个子词。模型看到的不是单独的字符，而是子词单元。数出字母个数，需要推理 token 的内部结构。

---

## Tokenization 算法

### 字节对编码（BPE）

最常见的算法，GPT 系列、Llama 和 Claude 都使用它。

**训练算法：**
1. 从单个字节组成的词表开始（256 个 token）
2. 统计训练语料中所有相邻 token 对的出现次数
3. 把出现频率最高的 token 对合并为一个新 token
4. 重复上述过程，直到达到目标词表大小

**示例：**
```
Corpus: "low lower lowest"
Initial: ['l', 'o', 'w', ' ', 'l', 'o', 'w', 'e', 'r', ' ', 'l', 'o', 'w', 'e', 's', 't']

Step 1: Most frequent pair is ('l', 'o'). Merge to 'lo'.
['lo', 'w', ' ', 'lo', 'w', 'e', 'r', ' ', 'lo', 'w', 'e', 's', 't']

Step 2: Most frequent pair is ('lo', 'w'). Merge to 'low'.
['low', ' ', 'low', 'e', 'r', ' ', 'low', 'e', 's', 't']

Step 3: Most frequent pair is ('low', 'e'). Merge to 'lowe'.
['low', ' ', 'lowe', 'r', ' ', 'lowe', 's', 't']

Continue until vocabulary size target...
```

**特性：**
- 给定训练好的词表后，Tokenization 是确定性的
- 常见词往往是单个 token
- 罕见词会被拆成子词

### WordPiece

BERT 系列模型使用 WordPiece。

**与 BPE 的关键区别：**
- BPE：根据频率进行合并
- WordPiece：根据似然提升进行合并

```
Score = freq(AB) / (freq(A) * freq(B))
```

这种方法倾向于选择比随机共现更有意义的合并。

**可视化标记：**WordPiece 使用 `##` 前缀标记延续 token：
```
"embedding" becomes ["em", "##bed", "##ding"]
```

### Unigram（SentencePiece）

T5、ALBERT 和部分多语言模型使用 Unigram/SentencePiece。

**训练算法：**
1. 从一个较大的候选词表开始
2. 计算删除每个 token 后的损失
3. 删除使损失增加最少的 token
4. 重复上述过程，直到达到目标词表大小

**关键区别：**它使用概率而不是频率，可以从早期不理想的合并结果中恢复。

### 对比

| 算法 | 合并标准 | Tokenization | 使用者 |
|-----------|-----------------|--------------|---------|
| BPE | 频率 | 确定性 | GPT、Llama、Claude |
| WordPiece | 似然 | 确定性 | BERT、DistilBERT |
| Unigram | 概率 | 概率性 | T5、mT5、XLNet |

---

## 词表设计的权衡

### 词表大小

| 大小 | 示例 | 优点 | 缺点 |
|------|---------|------|------|
| 小（10K） | 一些早期模型 | Embedding 更小 | token 序列更长 |
| 中（32K） | Llama 2 | 平衡较好 | 多语言效率较低 |
| 大（128K） | Llama 3/4、Claude Sonnet 4.6、Mistral Medium 3.5 | **当前标准。**压缩率高 | Embedding 表更大 |
| 超大（200K+） | GPT-5.5（o200k）、Claude Opus 4.7 | 原生多模态和多语言效率高 | LM Head 的内存压力更大 |

**词表扩展深入看：**
- **Llama 3/4（128K）**：从 32K 增加到 128K 后，Meta 让英文压缩率提升约 15%，让印地语等非英语语言的效率提升 3–4 倍。
- **GPT-4o/5.2（o200k_base）**：Tiktoken 的最新编码对代码和多语言文本提供了更好的压缩，同样含义使用更少 token，间接降低 API 成本。

### 字符级、子词级与词级

| 粒度 | 示例 | “running”的 token | 权衡 |
|-------------|---------|---------------------|-----------|
| 字符 | ByT5 | ['r','u','n','n','i','n','g'] | 可以处理任意文本，但序列很长 |
| 子词 | GPT | ['running'] 或 ['run','ning'] | 平衡较好 |
| 词 | 早期 NLP | ['running'] | 序列短，但无法处理 OOV |

现代 LLM 几乎都使用子词级 Tokenization，在词表大小和序列长度之间取得平衡。

### 字节级 BPE

GPT-2 引入了字节级 BPE：
- 基础词表是 256 个字节，而不是字符
- 可以表示任意文本，不需要 UNK token
- Unicode 会自然地作为字节序列处理

```python
# Character-level: Needs explicit handling of characters
text = "cafe"  # Unknown character might become [UNK]

# Byte-level: Works with any text (no UNK needed)
text = "cafe"  # Becomes bytes, then BPE operates on bytes
```

---

## 特殊 token

特殊 token 用于表示普通文本之外的结构信息：

| Token | 用途 | 示例 |
|-------|---------|---------|
| BOS | 序列开始 | 标记生成开始 |
| EOS | 序列结束 | 标记生成完成 |
| PAD | 填充 | 将一个 batch 填充到相同长度 |
| UNK | 未知 token | OOV 的回退方案（字节级 BPE 很少需要） |
| SEP | 分隔符 | 分隔多个片段（BERT 风格） |

### Chat Template

现代聊天模型使用特殊 token 表示对话结构：

**Llama 2 格式：**
```
[INST] <<SYS>>
You are a helpful assistant.
<</SYS>>

User message here [/INST] Assistant response here
```

**ChatML（OpenAI 风格）：**
```
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Hello!<|im_end|>
<|im_start|>assistant
Hi there!<|im_end|>
```

**为什么重要：**
- 格式错误会导致结果变差
- 特殊 token 不在预训练数据中以普通文本的方式出现
- transformers 等库使用 `chat_template` 自动格式化

---

## 多语言 Tokenization

### 挑战

主要用英语训练的 Tokenizer 对其他语言的效率较低：

| 语言 | “Hello”的 token 数 | 等价问候语的 token 数 |
|----------|-------------------|-------------------------------|
| 英语 | 1（“Hello”） | - |
| 中文 | - | 2–3+ |
| 日语 | - | 3–5+ |
| 韩语 | - | 2–4+ |

**成本影响：**非英语用户为相同语义单元支付的成本可能高出 2–3 倍。

### 解决方案

1. **多语言训练语料**：使用均衡的多语言数据训练 Tokenizer
2. **更大的词表**：为非英语 token 留出更多空间
3. **语言专用 Tokenizer**：按语言族使用独立 Tokenizer

**多语言支持较好的模型：**
- mT5、XLM-R：使用 100+ 种语言训练
- GPT-4、Claude 3.5：词表大，覆盖多种语言
- Gemini：从一开始就按多语言设计

| 模型 | 中文 | 日语 | 韩语 | 印地语 |
|-------|---------|----------|--------|--------|
| GPT-2 | 2.5x | 3.0x | 2.8x | 6.0x |
| GPT-4（cl100k） | 1.4x | 1.6x | 1.5x | 3.2x |
| GPT-5.2（o200k） | 1.1x | 1.2x | 1.1x | 1.4x |
| Llama 3/4（128k）| 1.2x | 1.3x | 1.2x | 1.5x |

---

## 多模态 Tokenization（从像素到 token）

现代原生多模态模型并不是简单地“看”图像，而是会对图像进行 Tokenization。

### 图像 Tokenization（视觉 Transformer）

图像会被拆分成图像块（例如 14×14 像素）。每个图像块会经过视觉编码器（如 SigLIP），生成一个视觉 token。
- **固定 token 成本**：在特定分辨率下，大多数模型为每张图片使用固定数量的 token（例如每张图片 256 或 729 个 token）。
- **动态分辨率**：有些模型（Gemini 3）会根据图片宽高比和细节等级使用数量可变的 token。

### 音频/视频 Tokenization
- **音频**：使用 EnCodec 等编解码器压缩为离散单元，再表示为音频 token 序列。
- **视频**：视为图像帧序列（时间维度上的 Tokenization）。1 秒、1 FPS 的视频，成本可能与一张高分辨率图片相当。

---

## 用于成本估算的 token 计数

### 快速估算规则

对于英文文本：
- **词到 token**：每个词约 1.3 个 token
- **字符到 token**：每个 token 约 4 个字符
- **页到 token**：每页约 500–800 个 token

```python
def estimate_tokens(text: str) -> int:
    # Rough estimation for English
    word_count = len(text.split())
    return int(word_count * 1.3)
```

### 精确计数

使用模型专用 Tokenizer：

```python
import tiktoken

# For OpenAI models
encoding = tiktoken.encoding_for_model("gpt-4")
tokens = encoding.encode("Your text here")
token_count = len(tokens)

# For Llama/Anthropic, use transformers
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")
tokens = tokenizer.encode("Your text here")
token_count = len(tokens)
```

### 成本计算

```python
def calculate_cost(input_text: str, output_text: str, model: str) -> float:
    pricing = {
        "gpt-4o": {"input": 2.50, "output": 10.00},  # per 1M tokens
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
    }

    encoding = tiktoken.encoding_for_model(model)
    input_tokens = len(encoding.encode(input_text))
    output_tokens = len(encoding.encode(output_text))

    cost = (
        (input_tokens / 1_000_000) * pricing[model]["input"] +
        (output_tokens / 1_000_000) * pricing[model]["output"]
    )
    return cost
```

---

## 常见 Tokenization 问题

### 问题 1：Token 边界不对齐

**问题：**文本操作可能与 token 边界不一致。

```python
text = "Hello world"
# Tokens: ["Hello", " world"]  # Note: space is part of second token

# Truncating at character 6 ("Hello ") splits a token
```

**解决方案：**管理上下文时始终在 token 边界截断。

### 问题 2：Tokenization 不一致

**问题：**同一段文本可能因为上下文不同而被不同地切分。

```python
# GPT tokenizer example
"New York"     # Might be ["New", " York"]
"NewYork"      # Might be ["New", "York"]
" New York"    # Might be [" New", " York"]
```

**影响：**token 数会因周围文本变化。始终对完整上下文进行 Tokenization。

### 问题 3：代码和结构化数据

**问题：**代码和 JSON 往往 Tokenization 效率很低。

```python
# Python code often tokenizes poorly
"def calculate_average(numbers):"
# Becomes many tokens: ["def", " calculate", "_", "average", "(", "numbers", "):", ...]

# JSON keys tokenize individually
'{"firstName": "John"}'
# Many tokens for structure
```

**缓解方式：**
- 有些模型使用针对代码优化的 Tokenizer
- 可以考虑在发送前压缩 JSON
- 如果可用，使用结构化输出模式

### 问题 4：空白字符处理

**问题：**不同 Tokenizer 对空白字符的处理方式不同。

```python
# Leading spaces often become separate tokens
" Hello"  # [" ", "Hello"] or [" Hello"]

# Multiple spaces may merge or stay separate
"Hello  world"  # Behavior varies by tokenizer
```

**最佳实践：**Tokenization 前先规范化空白字符。

---

## 实用 Tokenization 模式

### 模式 1：上下文窗口管理

```python
def fit_to_context(
    system_prompt: str,
    user_message: str,
    history: list[str],
    max_tokens: int = 8000,
    reserve_for_output: int = 2000
) -> str:
    encoding = tiktoken.encoding_for_model("gpt-4")

    available = max_tokens - reserve_for_output

    # System prompt always included
    tokens_used = len(encoding.encode(system_prompt))
    available -= tokens_used

    # User message always included
    tokens_used = len(encoding.encode(user_message))
    available -= tokens_used

    # Add history from most recent, drop oldest if needed
    included_history = []
    for msg in reversed(history):
        msg_tokens = len(encoding.encode(msg))
        if msg_tokens <= available:
            included_history.insert(0, msg)
            available -= msg_tokens
        else:
            break

    return format_prompt(system_prompt, included_history, user_message)
```

### 模式 2：在 token 边界分块

```python
def chunk_at_token_boundaries(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        start = end - overlap

    return chunks
```

### 模式 3：Token 预算分配

```python
class TokenBudget:
    def __init__(self, total: int):
        self.total = total
        self.allocated = {}

    def allocate(self, component: str, tokens: int) -> bool:
        used = sum(self.allocated.values())
        if used + tokens > self.total:
            return False
        self.allocated[component] = tokens
        return True

    def remaining(self) -> int:
        return self.total - sum(self.allocated.values())

# Usage
budget = TokenBudget(total=8000)
budget.allocate("system_prompt", 500)
budget.allocate("retrieved_context", 2000)
budget.allocate("user_message", 200)
budget.allocate("output_reserve", 2000)
# Remaining: 3300 tokens for conversation history
```

---

## 面试问答

### 问：为什么 GPT-4 很难完成简单的字符计数？

**强回答：**
Tokenization 把文本转换为子词单元，而不是字符。当被问到“strawberry 中有几个 r”时，模型看到的可能是 ["str", "aw", "berry"] 这样的 token，而不是单独的字母。

模型必须推理自己无法直接观察到的 token 内部结构。这要求它记住或计算 token 的字符构成，是一种并不总是可靠的涌现能力。

解决办法是先提示模型逐个字符拼写单词，再进行计数。这样会迫使模型生成字符级的中间表示。

### 问：如何为成本规划估算 token 数？

**强回答：**
粗略估算时，英文文本可以用词数乘以 1.3。

精确计数时，使用模型专用 Tokenizer：
- OpenAI：tiktoken 库
- 其他模型：transformers 的 AutoTokenizer

重要考虑因素：
- 非英语文本会使用多出 1.5–3 倍的 token
- 代码和结构化数据的 Tokenization 效率较低
- 始终为输出 token 预留额外预算（通常输出价格更高）
- 把系统提示和格式化 token 计算在内

在生产成本估算中，应抽样真实请求并测量实际 token 用量，再加上安全余量。

### 问：在不同模型之间切换 Tokenizer 会发生什么？

**强回答：**
每个模型家族都有自己的 Tokenizer。不同模型之间不能复用 token，原因包括：

1. **词表不同**：相同的 token ID 代表的字符串不同
2. **合并规则不同**：同一段文本会被切分成不同结果
3. **特殊 token 不同**：聊天格式不同

实际影响：
- 始终使用正确的 Tokenizer 进行 token 计数
- 缓存的 Embedding 与模型绑定
- Prompt 模板需要按模型调整
- 微调模型继承基础模型的 Tokenizer

### 问：如何处理 RAG 分块中的 Tokenization？

**强回答：**
关键考虑因素：

1. **在 token 边界分块**：在 token 中间切分，解码时会破坏文本
2. **计算模板 token**：系统提示和格式化内容都会消耗 token
3. **预留余量**：检索到的分块和问题必须能共同放入上下文

实现方式：
```python
# Determine available tokens for chunks
available = max_context - system_prompt_tokens - question_tokens - output_reserve

# Chunk with overlap at token boundaries
chunks = chunk_at_token_boundaries(document, chunk_size=500, overlap=50)

# Select chunks until budget exhausted
selected = []
tokens_used = 0
for chunk in ranked_chunks:
    chunk_tokens = count_tokens(chunk)
    if tokens_used + chunk_tokens <= available:
        selected.append(chunk)
        tokens_used += chunk_tokens
```

---

## 参考资料

- Sennrich 等：《Neural Machine Translation of Rare Words with Subword Units》（BPE，2016）
- Wu 等：《Google's Neural Machine Translation System》（WordPiece，2016）
- Kudo、Richardson：《SentencePiece: A simple and language independent subword tokenizer》（2018）
- OpenAI tiktoken 库：https://github.com/openai/tiktoken
- HuggingFace tokenizers：https://github.com/huggingface/tokenizers

---

*上一篇：[LLM 内部机制](01-llm-internals.md) | 下一篇：[Attention 机制](03-attention-mechanisms.md)*
