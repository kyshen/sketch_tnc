# 本次修改说明

1. 重写并统一了 `sections/abstract.tex`、`sections/introduction.tex` 与 `sections/experiments.tex` 的实验叙事口径。
2. 将 ASTNC-L2 的定位统一修改为“主实验中的务实默认预设（pragmatic default preset）”，不再表述为经验全局最优。
3. 将 cache reuse 的结论统一修改为 workload-dependent / overhead-sensitive，不再写成稳定正收益。
4. 将跨尺度结论统一修改为：easy regime 稳定，medium 已出现 boundary-like behavior，timeout/failure 属于有意义的边界信号。
5. 重排实验部分表格，压缩宽表，减少溢出；新增两张图：
   - `figures/main_runtime.pdf`：四个核心实例上的端到端总时间（对数坐标）
   - `figures/regime_status.pdf`：跨拓扑跨尺度的 completion fraction 热图
6. 更新 `head.tex` 以加入更适合当前表格排版的宏包，并改用容器内可用字体以保证可编译。
7. 生成了可编译的 `paper.pdf` 作为当前修改后的预览版本。
