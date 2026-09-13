# Late Interaction 与 ColBERT

本章介绍位于双编码器与交叉编码器之间的延迟交互检索。ColBERT 以 Token 级向量矩阵和 MaxSim 保留细粒度匹配，同时支持文档预编码；ColBERTv2 的残差压缩和 PLAID 的多阶段质心剪枝使其适合生产环境。文档还比较了 BM25、稠密检索、ColBERT 与交叉编码器的延迟、准确率、存储和扩展性，并通过 RAGatouille 代码说明实现方式。面试部分覆盖三类检索架构、Token 级存储权衡，以及 500 万篇法律文档场景下的方案选择。
