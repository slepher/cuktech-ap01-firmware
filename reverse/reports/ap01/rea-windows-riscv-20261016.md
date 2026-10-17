# REA Windows 原生 RISC-V（2026-10-16）

## Plan
用户明确授权在既有6.5.0分支补齐Windows原生RV32/RV64裸BIN和真实CLI/MCP验收，不使用WSL。延续同级REA现有未提交改动，不提交/推送/改全局MCP配置。

## Task
1. 复用Windows P0 native PE/6502现有ACL、不可变快照、Job Object和认证TCP路径，扩大准入到显式位宽RISC-V raw；保持只读能力。
2. 从官方同版本npm包提取已发布Windows native模块并校验manifest/sha；本机Windows JDK21.0.10、Ghidra12.1.4，无需WSL构建模块。
3. 准入/旧目标拒绝回归；Windows真实RV32/RV64 CLI/MCP验证映射、调用/数据引用、反编译、复用、错误与清理；必要时既有AP01只读映射核验。
4. 更新REA使用说明和本项目交接，明确真实结果、运行限制和原生启动配置。

## Status
已完成Windows x64原生实现与真实验收，全程未调用WSL。

- 环境：Windows Node24.19.0、JDK21.0.10、Ghidra12.1.4；native addon来自官方npm `rea-agents@6.5.0`，manifest/ABI/sha校验通过，SHA256 `665c57ab90aef0712a6aafc423c7992a88bf608bea63b370cb30c695900f9aed`。二进制仅留本地忽略目录。
- RV32/RV64真实CLI/MCP全套通过：base `0x9ffff000`、entry `0xa0000000`、offset4096；独立映射、直接调用、全局引用、伪代码、规范地址复用、原件不变、运行目录清理。证据[JSON](../../artifacts/rea-windows-riscv-real.json)，run `750c79b8-df22-426b-a86a-90939c180ea2`。
- 110项回归通过：provider69、launcher26、CLI5、MCP10。包含无位宽/非法入口错误、既有目标拒绝和会话保护；[日志](../../artifacts/rea-windows-focused.log)。
- Windows native真实conformance通过：DACL、快照、junction/ADS拒绝、取消、子孙进程终止、无关进程保留、owner关闭清理和内存预算；[JSON](../../artifacts/rea-windows-native-real.json)。
- `npm run check`、`npm run build:cached`、`npm run docs:check`（含5项README一致性测试）及`git diff --check`均通过。

## Windows运行

PowerShell设置 `JAVA_HOME=C:/Program Files/Java/jdk-21.0.10`、`GHIDRA_INSTALL_DIR=D:/tools/ghidra_12.1.4_PUBLIC`，从REA目录运行 `npm run verify:ghidra:riscv-raw` 可复验。
自建stdio MCP进程为 `C:/Program Files/nodejs/node.exe`，参数为 `D:/Documents/PlatformIO/Projects/rea/scripts/rea.mjs`、`mcp`，环境增加 `REA_ANALYSIS_PROVIDER=ghidra`。这是本轮真实MCP验收所用Windows入口；全局Codex配置未修改。

## Review
已核对：只扩展raw RV32/RV64准入，Windows RISC-V ELF与其他raw家族仍拒绝，数据库修改权限未开放，native授权检查保留。Windows verifier自身没有Job lease，报告process_lineage=unavailable；清理依据是运行目录为空和独立native Job conformance，不冒称POSIX lineage验证。原始ABI、厂商扩展和AP01间接调用恢复仍不承诺。基线6.5.0，分支codex/riscv-raw-adapter-6.5.0；未提交/推送，未改设备与Bridge。


## Codex MCP注册（后续用户授权）

用户明确要求接入自建版并移除旧安装。`D:/CodexHome/config.toml` 的唯一 `mcp_servers.rea` 已改为 Windows Node + 同级rea/scripts/rea.mjs mcp，增加REA_ANALYSIS_PROVIDER=ghidra，保留原JDK/Ghidra和超时。配置备份为 `D:/CodexHome/config.toml.rea-backup-20261016-201818`；结构化比较确认其余设置不变。Codex `mcp get rea --json`读回正确。

按保存的实际配置启动MCP：server rea6.5.0、207工具、open_binary有bit_width/base_address、binary_session真实调用通过。证据 `artifacts/rea-codex-mcp-smoke.json`。当前聊天的既存连接未热切换，重启Codex后使用新入口。

旧全局rea-agents6.4.0已通过npm卸载；核对完整命令行后停止6个旧MCP进程，清理npm锁定模块残留。旧安装目录与残留目录均不存在。
