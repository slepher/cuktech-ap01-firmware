# REA RISC-V adapter 实施（2026-10-16）

## Plan
用户授权实现；基线更正为 rea-agents-6.5.0 (3b79af28e80785afce9f5998d8f03289402a1847)。克隆位置 D:/Documents/PlatformIO/Projects/rea，分支 codex/riscv-raw-adapter-6.5.0。沿用 rea-riscv-bin-plan.md 的范围与验收，不操作设备或安装全局工具。

## Task
1. 将显式 bit_width (32/64，仅 riscv) 与可选 base_address 从 CLI/MCP 传到准入、目标与 profile。
2. 复用 Ghidra raw loader，分离 base/entry，更新 Java seed、独立映射证明及快照。
3. 增补负向、旧路径兼容和身份回归；按本机可用工具执行真实 provider 验证。

## Status
实现及标准RV32/RV64真实验收完成；未提交/推送/全局安装。本机构建Node24.19.0/npm11.17.0，真实验收使用隔离Node24.18.0；npm与仓库锁定11.16.0有补丁版本差异。

## Review
已核对CLI/MCP参数贯通、ELF元数据分流、缓存语义和真实provider边界。标准RV32/RV64通过；Windows裸RISC-V不开放，AP01厂商指令/原始ABI及部分间接调用仍有限制。

## 已完成实现与确定性验证

- 以 `architecture=riscv` + `bit_width=32|64` 接入小端 generic Ghidra/gcc；原始 ABI 未知，ELF 准入保留。
- `base_address` 可选，省略保留 base=entry；2字节入口对齐、完整映射位宽、文件内入口校验。CLI/MCP/目标/输出/profile/快照/Java准备脚本及独立加载证据已贯通。
- 等价地址统一为规范值；base=entry不增加旧profile字段，保持旧路径缓存语义。不同base/位宽失效。没有伪造ELF元数据。
- 源测试89项（含文档一致性）通过；最终CLI/MCP/文件解析21项通过；launcher中22项通过，另4项因Windows原生模块manifest缺失而失败，不归为通过。
- `npm run build:cached`、`npm run check`、`npm run docs:check`、`npm run verify:test-discovery`（1274文件）及`git diff --check`已通过。后续Evidence说明文字已由最终构建、类型/格式及diff检查复核。
- 公开可再生样本 `tests/conformance/ghidra/riscv-raw-fixture.mjs`；正式验证命令 `npm run verify:ghidra:riscv-raw`。头部4096字节，已知调用/全局引用；不执行目标代码。
- 真实环境：WSL Ubuntu24.04、Ghidra12.1.4、隔离Node24.18.0及Temurin JDK21.0.12.1+1；工具保存在REA本地artifacts并由.git/info/exclude排除。未全局安装REA/改MCP配置。
- 初次使用系统JRE被REA拒绝；初版verifier工具名错误已修正；一次验证与构建重叠导致最终CLI启动遇dist暂缺，已改为稳定runtime重新完整运行。以上失败不作验收证据。
- 上游#4246在本轮仍为开放设计讨论，无关联PR；未将通用语言透传扩入本实现。

## 真实验收状态

RV32/RV64完整CLI/MCP与旧ARM/x86路径通过，已有AP01镜像映射verified；AP01已有函数可读，但已知间接调用目标未由本次Ghidra自动分析恢复，详情如下。

### 真实证据（持续核对）

- 旧ARM/x86/x86_64 raw verifier完整通过：`artifacts/rea-arm-raw-real.json`，真实CLI/stdio MCP、等价地址复用/改变入口替换、非法入口保留当前会话、原件不变、清理后无自有后代；Ghidra12.1.4 Linux。测试token/CPU/峰值内存未测，不作性能承诺。
- AP01 0041完整6769704字节镜像 `inspect-native-load-image` 返回 `verified`：`RISCV:LE:32:default`/gcc、base `0x9ffff000`、entry `0xa0000000`、file_offset4096，各独立检查匹配；SHA256前后均`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。私有证据`artifacts/rea-ap01-load-image.json`。这证明导入映射，不证明厂商指令语义完整。

- RV32/RV64最终稳定runtime全套通过：`artifacts/rea-riscv-raw-real.json`，run `5972bb2a-1d94-4c5c-a3e8-491e3b362c4c`。两种位宽均真实CLI/MCP、base/entry分离、直接调用、全局引用、伪代码、等价地址复用与原件不变；退出后运行目录为空且自有后代为空。样本hash RV32=`4010cad62b653a050c295cdbaa4742ac0bbe4933359bd5abe7c19fc8c7f6ea0e`，RV64=`c4536ec7efa04aaee4ef909b54b3d20b5e6237ff3e63168f6347ab4923cde185`。

- AP01已知入口`0xa006f5ce`解码`c.addi16sp sp,-0xb0`，procedure同地址，保留来自`0xa01bb0cc`的数据引用；已知`0xa006f7f0`解码`jalr ra,ra,-0x118`，但Ghidra仅报告COMPUTED_CALL、无目标引用。验证脚本的目标`0xa01976d4`断言失败，如实保留，不伪造引用或宣称全部AP01函数分析等价。私有证据`artifacts/rea-ap01-known-addresses.json`及`.err`。此项属于处理器/自动分析质量后续，未扩大本轮实现或额外逆向。

## 交付与边界

REA分支`codex/riscv-raw-adapter-6.5.0`，基线`3b79af28e80785afce9f5998d8f03289402a1847`，33个源码/文档/回归文件的工作区改动，未提交。使用见同级REA `docs/raw-binary.md`；正式公开回归`npm run verify:ghidra:riscv-raw`。

确定性验收110项（89源码/文档+21边界）通过，另launcher22通过/4因缺Windows native manifest失败；不声称Windows验收通过。无ROM、Bridge、设备、全局MCP配置改动。标准样本与完整镜像映射验收不证明原始ABI、厂商custom指令或所有间接调用的正确恢复。


## 后续Windows验收

上述Windows缺manifest失败已于同日补齐：原生RV32/RV64真实CLI/MCP和110项回归通过，详见[Windows实施记录](rea-windows-riscv-20261016.md)。历史POSIX验收保留，本轮未使用WSL。
