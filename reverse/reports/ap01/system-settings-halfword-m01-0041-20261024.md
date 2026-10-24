# M01：系统设置 halfword 的输入覆盖与既有算法接入

**`a00a46e8()` 把初值0、指针 `G=62fc9098`、长度6传给既有 `a00ee8fc`，返回后不覆盖 a0。因下层正长度递推/unsigned16返回合同已由旧 UART/OTA 专项解释，本题只补 wrapper 输入覆盖和返回接线：结果覆盖 `G+0..G+5` 六字节，排除输出槽 `G+6/G+7`，再沿 L03/L04 已验的 SH 写到 G+6。** 不重做 CRC 算法/表或向量，不认证真实落盘、结构全部字段或原始源码来源。

2026-10-24；基线 `1dcbfe6`，独占树/分支 `re0041-m01` / `codex/re-0041-m01`。采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只有静态只读原件和旧报告/留存证据；未打开/切换共享 REA target/database，未运行固件、SIM、构建、历史回放、算法输入、模拟指令、分析器模型、设备或外部服务，未做漏洞/异常输入/缺陷验证，未改生产代码、ROM、配置或分析器模型，没有下级 agent。伪代码是合同表达，非原源码。作者自检待新的独立技术复核。

## 继承结论

| 已有出处 | 行为与证据层次 | 本轮范围 |
|---|---|---|
| [L03](settings-mode-contract-l03-0041-20261024.md)、[L04](settings-mode-review-l04-0041-20261024.md) | 两 UI→G+2 byte发布→同步通知→writer，非零 H 时 `ab2c2` 调本 helper，低16位 SH 至 G+6，随后 `(G,8,1,H)` 写服务/关闭；返回不消费已独立限定接受 | 直接继承，不重验 UI、通知、SH、8B服务/关闭顺序，不把写服务调用提升为持久成功 |
| [USB/UART/OTA 旧 CRC 合同](usb-interface-ota-0041-20261023.md:71)，`ev_98903ff50cb2f96b342e6df43357e470de464e58dd13257922d9d3e9efaad342` | `a00ee8fc` 原汇编修正了 void 伪码；正长度按字节递推，ROM表匹配多项式1021h，a0被截为unsigned16返回；旧宿主表/逐位校核不等于目标运行 | 完整算法和512B表直接引用，不重读/重导表、不运行旧校验器或输入。长度固定6，沿其正长度合同，不展开其他长度 |
| [B18](uart-normal-parser-b18-0041-20261023.md)、[B19](uart-normal-parser-review-b19-0041-20261023.md) | 较晚 parser 及独立复核均明确继承同 `a00ee8fc(0,base,N-2)` 算法/返回，未重审内部 | 保留该认证等级：旧局部原件算法合同可复用；不是上游来源/版本认证，不重复 parser/OTA |
| whole-ROM round1 与旧 `whole-rom-graph-20261023-4848/4849.json` | wrapper extent32B，callee唯一 `a00ee8fc`；extent ID `ev_3bcf00da99c5d52c17dc1a58ed99b4afbe07cc190433785bf92ce17c4265d5d4`，callee ID `ev_97d720acc602281482b0bf36aa2a4ffe072e3115f1e73faccfe5d0bd4123cbd7` | 元数据只证明定位；本轮只核实际实参和返回尾声，不重新导32B整函数 |
| [最终应用验收](application-rehost-complete-0041-20261017.md)、[J03](settings-persistence-reuse-gap-j03-0041-20261024.md)、[已有 sysconfig 样本](knowledge/0041-sim-wifi-selection-gaps.md:65) | SIM 保存服务与8B原厂系统配置样本已留存；sysconfig与PSM区分 | passed-in-sim、宿主CRC格式、样本存在不证明本ROM wrapper算法或文件成功；这些不重计 |

按地址/字段精确检索近期非管理报告后，L03/L04明确留下本 helper 算法未命名边；旧 USB 专项已经有真正下层算法合同，因此缺口收缩到这一个 wrapper 的参数/覆盖/返回。四份旧 system/guide complete、settings-round2b、page-logic 的精确 token `a00a46e8/62fc909e/62fc9098` 有界查询中，只有 guide complete 命中 G 基址，局部上下文为 `a00a5ce8` 读取 G+2/+3 的显示业务，不是 wrapper 输入/算法。见 [reuse.json](../../analysis/system-settings-halfword-m01-0041-20261024/reuse.json)。无命中不证明历史从未解释，不以新报告名重做通用CRC。

## 本轮复核或纠正

只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−9ffff000`。9个必要稀疏锚点/24B见 [evidence.json](../../analysis/system-settings-halfword-m01-0041-20261024/evidence.json)。没有读取完整通用CRC体、表或重新导wrapper的栈建立段。

| 地址/原字 | 字段或控制事实 | 合同含义 |
|---|---|---|
| 46f0 `b795fc62` | LUI rd=a1，upper=62fc9000 | 输入指针高部 |
| 46f6 `93858509` | ADDI rd=a1,rs1=a1,imm=98h | a1=62fc9098=G，不从传入指针或某个栈快照取得 |
| 46f4 `1946` | C.LI a2,6 | 固定覆盖6字节，非8字节；包含G+5，不因其正式字段名未知而排除 |
| 46fa `0145` | C.LI a0,0 | 本次初值固定0，不继承调用者残留a0 |
| 46fc `efa00420` | JAL rd=ra，独立解算目标a00ee8fc | 连接到已有算法，不从函数名猜CRC身份 |
| 4700 `b240`；4702 `2244`；4704 `4101`；4706 `8280` | 依次恢复ra/s0、sp加10h、经ra返回；无a0写 | 原样返回下层a0，没有额外xor、符号扩展或状态码覆盖 |

本轮没有推翻已接受行为。L03/L04的“未在本题认证算法”是其准确范围；现在借旧下层合同闭合本正常调用，无需新增算法。旧0x1021合同是原指令/表加宿主静态校核所得的局部恢复，不是厂商源码、精确上游版本、厂商规范或目标运行验收；本轮没有提升该证据等级，也没有新标准库排除。

## 真正新增

唯一新的接入解释是：**无参 wrapper 自行选择 live G前6B、seed0，原样交回既有 unsigned16结果**。可以在继承边界内写成：

```c
// 非原源码；crc16_positive 是旧报告合同名，不是新识别源码符号。
settings_halfword():
    return crc16_positive(initial=0, bytes=G, count=6);

// 以下全部沿 L03/L04，列出只为说明输出接线，不重计恢复。
// 非零H路径：
store16(G+6, settings_halfword());
existing_write_service(G, 8, 1, H);
```

旧递推为 `c0=0`、`c(i+1)=((ci<<8)^T[(ci>>8)^load8(G+i)])&ffffh`，此调用只取 i=0..5；T和unsigned16返回直接继承旧合同。无输入枚举/算法执行。结果已在0..65535，writer的低16位SH不丢失这一路结果。覆盖范围为62fc9098..62fc909d；输出槽62fc909e..62fc909f不作为本次输入，因而不需要把它们清零后再算，也不添加这种原程序未有的操作。

指针直接指向全局live G；wrapper没有本段新分配/复制/保留输入指针或所有权移交。读取过程由旧下层逐字节合同限定，不宣称六字节原子快照。通知/写调用原序、G+6更新在通知之后及本层不检查服务结果均沿L03/L04，不重新恢复或延伸到subscriber、文件后端。

新增通用算法、CRC表/向量、ISA规则、来源认证、整函数导出均为0；新增只有这个已定位接入合同。识别为旧CRC调用来自真实JAL目标和已存在合同，不是把未知halfword预设为安全校验。

## 精确未闭与实际验证

M01的正常输入来源、覆盖范围、初值、返回宽度与必要算法合同已得到可定位答案。G各byte（尤其+5）的正式结构定义、所有writer和并发/快照政策、下层精确源码来源、系统初始化的完整使用策略、物理保存/读回/重启保证仍未知。本题不展开sysconfig初始化/比较/复位分支，不向NVS、driver或其他算法消费者扩扫；8B写服务实参不等于真实持久成功。

[verify.py](../../analysis/system-settings-halfword-m01-0041-20261024/verify.py) 运行 PASS：9个稀疏锚点24B、9项独立LUI/ADDI/C.LI/JAL/尾声原字检查；只核旧extent/callee/算法证据身份和已有报告合同存在性，算法求值次数0。没有运行旧CRC向量、table生成器、L03/L04脚本、输入样例或SIM。JSON解析、报告链接和差异检查通过。

一个后继仅为新独立agent复核本题9个锚点、seed0/G/6与a0直返及旧算法复用等级；SH和服务接入继续引用L04，不重验整CRC库。没有新增payload/调度/后端种子，因此本路不自行派单位、初始化或落盘研究。
