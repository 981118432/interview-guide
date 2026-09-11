# LoRA、QLoRA 与 PEFT

## LoRA 原理

LoRA 冻结基础权重 W，只训练低秩更新矩阵 A、B：`W' = W + α/r · BA`。它减少可训练参数、显存和适配器存储，适合多任务和多租户部署。

## QLoRA 与变体

QLoRA 将基础模型以 4-bit 量化加载，同时训练 LoRA 适配器；NF4、双重量化和分页优化器进一步降低显存。DoRA、rsLoRA 等变体分别改善权重方向/幅度或 rank 稳定性。

## Multi-LoRA Serving

共享一个基础模型，按请求加载 Finance、Legal、Medical 等适配器，可以节省重复权重成本，但要管理适配器版本、缓存、并发、租户权限和切换延迟。评估时同时比较适配效果和基础能力保持情况。
