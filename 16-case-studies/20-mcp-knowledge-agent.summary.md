# 案例研究：企业 MCP 知识 Agent：中文概要

本篇设计通过 MCP 连接 Snowflake、Confluence、Jira 和 Slack 的企业知识 Agent。每个 Server 使用 OAuth 2.1 Resource Server 语义和 RFC 8707 受众绑定，遗留 STDIO Server 放入无共享文件系统的 Sandbox，工具参数和工具结果都经过信任标记与能力门禁。

面试重点是逐调用权限校验、Token 重放防御、IPI、审计链、身份级限流、MCP Server 迁移和不使用单一向量索引的原因。
