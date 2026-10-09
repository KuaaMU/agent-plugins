# Profile：Ascend / CANN 算子攻坚

本文件是领域 profile：内核（SKILL.md + references/）领域无关，
做 Ascend/CANN 算子任务时**额外加载**本文件。
用法：`init_mission.py --profile ascend-cann`。

## 数值正确性门禁（补充 `gates.md` 第一道）

- 记录 precision/accumulation mode、允许的重排与融合、FMA/收缩开关、
  溢出/下溢/次正规数/NaN-Inf 行为；
- 误差口径：ULP、相对/绝对误差、匹配率、outlier 规则，按任务书来；
- 整数/索引/状态/元数据优先精确一致；
- fast/fallback 对相同输入必须一致；内部 marker 不得复用用户可见输出；
- 改变算术顺序或精度后，重跑完整正确性门，不沿用旧精度结论。

## 优化顺序（7 层，由上到下）

1. 删除不必要的工作（不读无用数据、不写无用中间结果、合并重复 transform）；
2. 降低数据搬运（中间量放大倍数、读写次数、有效带宽、片上往返）；
3. 改善 locality 与布局（连续访问服务搬运单元、对齐、padding 成本）；
4. 选择执行单元（按算术强度、数据连续性、launch 固定成本，不迷信理论峰值）；
5. 重叠独立阶段（只重叠真独立的依赖，警惕同步税）；
6. tiling/partition/并行映射（由资源预算驱动：`tile = f(片上容量, 单元素工作量, 复用距离, 对齐)`，
   而不是 benchmark 常数；每个 route 回答边界/尾块/非整除/stride 怎么走）；
7. 指令级微调（只在 profile 指向此处时做；记录源码+编译选项+device binary，
   警惕"源码等价、产物不等价"）。

WHEN 想从第 6/7 层开始 THEN 打回——参数扫描只有在关键路径、floor、
route 明确后才有意义。

复用优先级：目标仓库已有公共 primitive → 官方高阶 API →
官方低层 instruction → 自研 kernel（需独立测试与回退路径）。

## 官方工具（用前先 `discover_environment.py` 确认存在）

- Profiling：回答总时间由哪些 kernel/task 组成，各阶段占比，
  compute/memory/搬运/launch gap 比例；至少记录过滤条件、采样、warmup、
  device time vs host/wall time；
- Logging/错误解码：先存原始错误码与设备上下文，再查文档；
- Sanitizer/竞态检查：诊断构建≠生产构建，诊断报错未解释前不 promote；
- Debugger/Dump：带 case/阶段/shape/路由/版本，大文件不进交付树；
- Compiler 诊断：解释"源码相同、device 行为不同"；与运行时冲突时以
  目标设备行为为准，两边证据都保留。

版本优先级：当前安装头文件/样例/帮助 > 对应版本官方在线文档 >
官方仓库源码与 issue > 任务书/测试包 > 二手文章。

## 算子专属失败家族（补充 `failure-patterns.md`）

- **Floor 忽略**：目标比 launch/搬运/同步 floor 还小，反复优化不可压缩部分。
  防护：单独测各类 floor；floor 超目标则改执行图或重核目标。
- **Raw primitive 当完整路径**：用单阶段 microbench 推断完整 API 过门，
  忽略 transform/combine/launch/host。防护：四段对照，以目标 API 口径验收。
- **内容型 shortcut**：利用 benchmark 输入的特殊分布走捷径，
  fast path 无严格证明或完整 fallback。防护：只允许结构性 gate；
  未命中 exact fallback；加对抗分布用例。
- **状态污染**：内部状态复用用户可见字段；连续调用行为不一致；
  cache key 缺维度。防护：内部状态独立分配；cache key 覆盖全部影响参数。
- **并行神话**："加流/加核一定更快"。防护：先做串行 phase 预算；
  证明可重叠依赖；同构建 A/B；看 critical path 不看平均利用率。

## 交付注意

- 生产代码禁：实验开关、`/tmp` dump、调试打印、硬编码路径、
  `.orig/.bak`、未接线 kernel、单 shape 白名单；
- 一个提交一个逻辑变更；上游基线只读，实验分支短生命周期；
- 随代码提交：构建命令、完整正确性测试、目标性能测试、回归测试、
  原始日志路径、源码/构建 hash、已知限制。
