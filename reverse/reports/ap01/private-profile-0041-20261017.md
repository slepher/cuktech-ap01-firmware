# 0041 私有分析模型修复与完整任务逆向

日期：2026-10-17。状态：模型修复与关键函数恢复已验，两个任务的实现恢复及依赖闭包继续推进；不刷实机、不改变共享 REA 会话或原件。

## Plan / Task

续作（2026-10-17）：使用已冻结276函数Evidence继续MiIO/MiBLE上层实现。两个GPT-6.1 Sol代理分别负责尚未人工恢复的65个MiIO根，第三代理展开BLE可靠传输/认证依赖；父代理独占新REA采集、核验字段/ABI、合并新覆盖账本。旧manifest与报告不覆盖，新增`upper-*`文件保存逐函数合同、字段/分支/回调/错误和未决依赖，再更新交接。仍不刷实机。

1. 将 Ghidra 12.1.4 和 REA 6.5.0 运行文件复制到既有私有证据目录，独立语言、缓存、脚本与会话；原始 ROM SHA256 必须匹配 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。
2. GPT-6.1 Sol 分别实现并验证：实际 RETURN 证明支持的 no-return 清除与调用点重建；有原始 ISA 依据的 T-Head SLEIGH/p-code。未知指令保留失败，不用 NOP 替代。
3. 私有 REA profile 绑定处理器与修复脚本内容指纹。比较关键函数修复前后真实地址集合、反编译和调用点，不能以强行合并连续区间充作恢复完整。
4. 通过模型门槛后，从 MiIO 162 根和 BLE 80 种子推进代码级恢复，保留回调、动态调用、未收集与未知边界账本。
5. 更新 `0041-handoff.md`、`PROGRESS.md` 与 C9 的证据入口；不把伪代码导出数量称作完整 SDK 源码。

## Status

- 私有根：`artifacts/ap01-research/private-0041-20261017/`，目录已按 AGENTS 要求提权预建。
- 全局 Ghidra、旁仓 REA 源码及旧 Evidence 不修改；私有 `rea/node_modules` 只读复用依赖。
- 两轮独立语言均经真实 Ghidra 导入、p-code执行和 REA MCP 验证。v1修复2395调用点/6轮；v2补齐指令后修复639调用点/2轮，均达到受保护规则下的收敛。这些计数不相加。
- v1 `RISCV:LE:32:ap01thead:gcc`：226项检查、141项执行，蓝牙原始窗口68个厂商指令与旧13处缺口全部验证。profile `b6bd3fdddcd796bbbfc4e16727d1682dca624cdb69068bbec3978a509b174bd2`。
- v2 `RISCV:LE:32:ap01thead2:gcc`：387项检查、286项执行，新增REV/WEXTI/ADD64/MINW并验证12个新断点，原有8个HTTP/OTA坏指令截断全部消除。8项负向编码明确UNMODELED。profile `0ba751932e6730a6db2135e50d55bd95ec51a024426c4772add6d7c256bbc401`。
- 真实REA v2初次完整导出267函数、166804200 B；MiIO162根/BLE80根全采集，尚有546个未采集直接callee、153处未定向callsite。另有一个`unaff_`类型/寄存器问题，不把无坏指令当完整源码。
- 新发现两个实际注册但未定义的回调`0xa011f0bc`、`0xa011e11a`，使用新增私有种子manifest重新导入；不抢占其他body或手工补满字节区间。结果见后续manifest。
- 最终含两个晚发现回调的profile为`04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`，修复报告246根/639调用点/2轮收敛。`final-0041.evidence.json`同一profile276函数，168348248 B，SHA256 `80c93186458c90a7edd8a61beae8b1af4643ef6ce1ba695b87c9ea804bb1a6cc`；276函数有2360条直接边，550个未采集直接callee、156处未定向callsite。`analysis-ledger-final.json`为当前实际分母和未知清单，不与早期集合混算。
- 原件未修改；两个任务尚无完整可编译重建源码。模块恢复文件在私有根`evidence/miio-recovered.md/.json`、`mible-recovered.md/.json`，与按任务导出的Ghidra伪代码分开。

## 私有运行方法与证据

私有根下`rea/`与`ghidra/`分别复制自旁仓REA6.5.0运行文件及Ghidra12.1.4；只复用只读node_modules依赖。`scripts/patch_private_rea.py`只修改副本并校验预期源文本，MCP/CLI bundle和未打包API都有同样的三个hook：指定语言、绑定模型输入到profile、分析后运行修复脚本。共享Windows P0保护未删除。开发审阅修正了两处实际问题：Ghidra导入使用快照路径，校验应认相同SHA；模型输入必须在profile与启动时重新校验，配置变化要求重启。

已存在目录内复现当前模型：

```powershell
python artifacts/ap01-research/private-0041-20261017/scripts/freeze_private_profile.py --round2 --late-callbacks
& 'C:/Program Files/nodejs/node.exe' artifacts/ap01-research/private-0041-20261017/scripts/private_rea_client.mjs
```

运行会生成子目录，按根AGENTS必须从提权命令启动。freezer生成新的配置/修复报告名，运行前保留旧profile和Evidence；不要覆盖旧协议导出。client使用独立HOME/TMP/APPDATA、私有GHIDRA_INSTALL_DIR；通过私有根`request.json`提交有唯一id的串行工具命令。父代理独占队列，子代理仅读证据。退出用新id加`stop:true`，等待MCP关闭清理自己的临时项目；不影响已有NuttX SIM或Bridge。

`open_binary`成功只证明准入，首次`analyze_function`才启动Ghidra。必须同时核验新profile digest、实际语言、当前唯一修复报告、原件SHA和关键body后才采信结果。加载器内部imageBase可能为0；raw块起点与独立映射`0x9ffff000`才是校验对象。Java脚本需复制到私有REA bridge脚本路径才能被Ghidra脚本系统找到。

大函数的MCP完整响应可能超过10 MiB而返回resource_constraint；结果已留在REA内存，使用`export_evidence_bundle`导出，不能把它当函数缺失或截断。`index_recovered.py <bundle文件名> <输出后缀>`从真实Evidence生成逐函数范围、caller/callee、未定向调用和文本警告账本；`.c`仅为不可直接编译的Ghidra文本。静态`resolve_native_call_targets`当前只查看ReferenceManager，不能自动消除运行时函数指针。

## 官方资料与SDK

指令语义以[玄铁官方规范](https://github.com/XUANTIE-RV/thead-extension-spec)、版本固定的历史P草案为主要依据，QEMU为独立交叉核对。每份下载原文、内容哈希、用到的编码与实际执行向量均保存在`thead-model*`、`thead-round2-model*`与`thead-*-tests.json`。历史P与当前P草案不可混用；`0x2066978b`实际为MULA而非RV64-only MULSW。

用户随后指定官方[Bouffalo SDK](https://github.com/bouffalolab/bouffalo_sdk)，已浅克隆/部分稀疏检出到`D:/Documents/PlatformIO/Projects/bouffalo_sdk`，提交`41bf338a57be53919d99f6c6715a96100428c97d`。未递归初始化子模块、编译或刷写。优先检出BL616/BL618的drivers/lhal、drivers/soc/bl616、drivers/sys、cmake、bsp/board/bl616dk；同名CL/DG新变体不可代替原芯片。SDK仅作为底层源码对照，不假定其包含原厂MiIO/MiBLE私有实现，也不假定当前HEAD与0041编译时版本相同。具体有价值的源码路径、CSR和内核证据由`evidence/sdk-core-findings.md/.json`记录。

已确认SDK配置E907/`rv32imafcpzpsfoperand_xtheade`/`ilp32f`，`0x7c5=MHINT`，自定义ISA与cache启动序列有6段ROM直接匹配。bit20和reset值仍未证明。SDK同时揭示冻结Ghidra模型的FLEN8/D解码、fa参数宽度仍为超集；原0041浮点ABI未由新版SDK证明，需后续独立callsite验证，不能宣称严格E907全部ISA/ABI已验。选择源码时以实际芯片CMake/头文件优先于SDK内概览中混合的型号描述。

## Review / 验收门槛

- 原件前后 SHA256 一致，私有模型使用独立语言 ID 和新 profile digest。
- memset/memcpy 的有效返回路径由原始字节和 RETURN p-code 证明。
- 索引访存、条件移动、累积乘法和位操作核对操作数与寄存器更新行为。
- 关键入口不再在首个 memset/memcpy 处停止；残余未知指令和边界需明示。
- 所有产物均为离线分析；设备、Bridge 与原厂 ROM 不变。

已确认：蓝牙main5696 B、公共初始化7982 B、miio入口850 B、gateway10132 B均在真实REA记录中恢复；其他函数body和ABI、间接回调仍以逐函数账本为准。v1修复审阅明确列出30个未归属调用、18个保护fallthrough和1个body冲突；不以`fixed_point=true`掩盖这些边界。

私有profile准入7项正/负检查通过：语言、输入指纹、原件身份、映射、架构、快照与模型变化拒绝。两个新增回调已被真实REA采集；timer的NULL分支trap后邻接代码、GATT越body伪代码均在恢复报告中排除，不把body范围等同原始函数证明。最终`evidence/manifest-final.json`已复核57个模型输入、原件SHA及旧协议manifest全部14个文件不变，绑定当前Evidence/账本/报告。私有MCP已正常关闭，下一轮按复现步骤新建自己的临时会话；共享MCP未切换。SDK工作树干净，`git diff --check`通过；没有运行PIO/NuttX重编，因为本轮只修改分析模型/证据与文档。

## 上层续作验收（2026-10-17）

本轮57个模型输入不变，当前profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。同profile采集315函数；MiIO新增130根实现审阅，162已知根全部有局部合同；90描述符已关联，公共路由6份及MiBLE9份合同已落盘。`upper-manifest.json`验证190处Evidence引用、旧18文件与原件不变。当前2529直接边、537个未采集直接callee/161处未定向调用，无halt_baddata；完整ABI和依赖闭包仍开放。旧final-*文件保留，不能覆盖或把混合来源合同重标同profile。详见[上层恢复与验收](upper-layer-0041-20261017.md)。
