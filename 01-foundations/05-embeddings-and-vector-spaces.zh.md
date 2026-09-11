# Embedding 与向量空间

## 核心概念

Embedding 把词、句子、文档或其他对象映射到向量空间，使语义相近的内容距离更近。Word2Vec 是静态表示，BERT 等模型提供上下文表示，Sentence/Document Embedding 面向检索和分类。

## 模型与指标

Bi-Encoder 分别编码查询和文档，速度快，适合大规模召回；Cross-Encoder 同时读取二者，精度高但成本更高，适合重排序。常用距离包括 Cosine、Dot Product 和 Euclidean，选择要与训练目标和向量归一化保持一致。

## 生产实践

关注批处理、缓存、分块、维度、量化、版本和漂移。Matryoshka Embedding 允许在不同维度截断向量，用于在质量、索引空间和延迟之间调整。Late Chunking 先编码更长上下文，再按块聚合，可保留跨段落信息。模型升级必须重新评测和管理索引版本。
