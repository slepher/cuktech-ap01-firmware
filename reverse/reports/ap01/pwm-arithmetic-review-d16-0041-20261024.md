# 0041 D16：D15 PWM 算术独立复核

基线 `2844cc4`，独占树 `re0041-d16`，分支 `codex/re-0041-d16`。按 reverse-engineer-anything 技能复核 [D15](pwm-arithmetic-d15-0041-20261024.md) 真正新增的正常分频搜索、三个软件数值 helper ABI、MULA/移位/打包及缓存/MMIO 原序。结论：这些限定结论接受，没有发现应纠正的算术或 ABI 冲突；新增功能 **0**。接受不包含厂商 ISA 硬件独立认证、软件来源版本认证或实际 PWM 输出认证。

## 继承结论：先有证据与实际缺口

| 已有出处 | 已解释行为与本轮处理 | 证据局限 / 精确复核缺口 |
| --- | --- | --- |
| [round2](buzzer-backlight-round2-0041-20261023.md) 与 `reverse/analysis/buzzer-backlight-round2-20261023/capstone-windows.json` 的 `pwm-ops` | 已有 `a0136762..a0136997` 原窗口、lower/Info/通道表、MMIO 基址及两路映射，直接继承 | 通用反汇编有厂商 unknown；只核 D15 使用的字与数据连接，不重导函数 |
| [round3](buzzer-backlight-round3-0041-20261023.md)、D15 复用表 | upper ioctl、stop/shutdown、轮询、持久参数副本生命周期已解释；complete/ZIP/较晚请求的有界复用结果继承 | 不将旧 exact-address 未命中当作全库未恢复；不重新搜停机通知消费者 |
| D15 `review-result.json` 的九个稀疏窗口、三条 call、constant、vendor_words | 正常算术与实际 ABI 已恢复，本文是独立复核 | 重新读取主仓 ROM，对全部留存稀疏指令逐项比字节；核必要 helper 出口与字段 |
| 主仓 `evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc:25,6410,6596`；`tooling/scripts/qemu-ap01-cpu.patch:140,176` | 已有 THead MULA/索引访问及历史 PKBB16 编码合同 | 本地条款是解释依据，不升级为厂商原始硬件规范；没有修改或执行模型 |

主仓只读前缀 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。D15 已列的 whole-rom-graph records 652/668/692 仅证明 helper retained body 范围，不能单凭 procedure_info 证明算术；8702 的不连续错误合并不采用。独立检查结果见 [review-result.json](../../analysis/pwm-arithmetic-review-d16-0041-20261024/review-result.json)，过程见 [verify.py](../../analysis/pwm-arithmetic-review-d16-0041-20261024/verify.py)。

业务及所有权继承：入口 `a0=Lower*`、`a1=Info*`，借用两者及 lower+8 通道表；不分配、不接管 Info；复制两项 duty32 和频率，缓存 period16。正常出口 `a0=0` 不代表所有 MMIO 配置必已完成。upper 参数副本的持有/释放仍依旧报告，不从本入口推线程关闭。

## 本轮复核或纠正：逐项接受及证据边界

| D15 增量 | 独立复核结果 / 必要原字节锚点 | 判定 |
| --- | --- | --- |
| 80 MHz binary64 常量 | ROM `a061b5a8` 的 `00000000d0129341` 按 little-endian binary64 为 `80000000.0`；`6812/6816` 载入低/高 word，`682e/6830` 送到 a0/a1 | 接受。仅证明软件使用此数，不证明硬件输入时钟实测频率 |
| u32→binary64 `a001fa84` | `6820` 将 s2 送 a0；`6822/6826` 原 AUIPC/JALR 独立解到目标；入口保持原 u32，CLZ 后指数 `0x41e-clz`，没有按输入 bit31 负号处理；`faac..fac0` 将低/高 word 送 a0/a1 返回。CLZ 表与正常路径依据 D15 既有静态核读 | 接受无符号职责及整数寄存器 ABI，不认证 libgcc/newlib 版本 |
| binary64 除法 `a001d7fc` | `682a/682c` 把转换返回放 a2/a3；常量放 a0/a1。`6832/6836` 解到目标。`d814..d85c` 与 `d8ca..d92a` 分别拆两数指数/尾数、指数相减、符号异或；`d9ca` 正常路径有 divu/remu。`d81a` 原字 `73292000` 读 frm；`dbfc..dc34` 的舍入选择保留。`dcbc..dcc2` 组 a1:a0，另核 `dcc4..dce2` 只置 fflags/恢复保存寄存器/返回，不重写这对结果 | 接受数学职责、分子/分母次序及返回对；没有将稀疏窗口检查说成全舍入情形形式证明 |
| binary64→u32 `a001f042` | `683a/683e` 解到目标，中间无实参搬移，沿用商 a1:a0。`f07e..f0a0` 与 `f0b2..f0d2` 的逻辑移位/拼接产生 a0，丢位只走 fflags；开头虽 frrm，但其读值随后被指数覆盖，不参与正常整数加一 | 接受正有限正常路径向零截断；不把除法的 frm 依赖移植成此转换的舍入依赖 |
| 分频搜索宽度/比较 | `6844` 原字 `63688501` 是 unsigned period32<65536；`6848` divider++，`684a` 32 位 denominator+=原频率，`684c` 按 divider!=65536 回边。选定的是 divider 本身，未减1 | 接受。保留 D15 原穷尽分支描述，不做异常、溢出或零输入探测 |
| 两条 duty32→阈值链 | `67d2/68da` lhu period；`67da/68e2` lw duty；`67e4/68ec` 原字 `8b966520` 的 rd/rs1/rs2=13/11/6，按既有 MULA 条款为低32位 `0x8000+P*D`；`67ee/68f4` 原字 `c582` 逻辑右移17；half 是此前 P>>1；随后先加/减再打包 | 接受低32位乘加与精确偏置，不能提升为64位或换为通常四舍五入 |
| PKBB16 与写宽度 | `67fa/6900` 原字 `f797f50e`，opcode/f3/f7=`0x77/1/7`，rd/rs1/rs2=15/11/15；按旧合同，高16取 high 低16、低16取 low 低16。`6804/690a` 的 srw 写32位到 base+0x50+(channel<<2) | 接受既有历史编码合同下的截断语义，不饱和、不保留端点高位；厂商独立编码证明仍未核 |

正常成功选定路径可用以下必要关系表达（分析伪式，不是原源码）：`q = truncate_u32(div64_frm(80000000.0, u32_to_binary64(denominator)))`；从 denominator=freq、divider=1 开始，直到 q<65536。阈值是 `half=P>>1; delta=((0x8000+P*D) mod 2^32)>>17; high=half+delta; low=half-delta`，最终各取低16位打包。D15 对此无需纠正。

缓存和正常 MMIO 顺序逐项接受：

1. `67a8` 保存旧频率，`67ac/67b0` 仅在不同才写 lower+10；`67b6` 写第一 duty、`67bc` 写第二 duty，再于 `67be` 重读缓存频率；`67c4` 与旧频率比较。相同时只走两路阈值，再汇合到 `692c`。
2. 不同时算 divider/period32，`685c` 先 sh 到 lower+0xc，再 `687a` 写停止请求。继承轮询合同后，配置成功分支 `68bc` 写 `(old40&0x3fff0000)|divider|0x40000000`，然后 `68cc` 写 `(old48&0xffff0000)|period32`；两个 skip 分支仍到 `68d0`，不能以缓存已更新推出这两次 MMIO 已写。
3. 变化路径每一路先写阈值，随后重新加载设备基址、通道表和通道 byte；实际顺序为 `6916` 先读 base+44，再 `6918` 读 channel，`6926` 写回 base+44。不能把“重读通道、读改写 enable”误写成两个 load 的相反原序。表项前进到下一路，再重复同序。相同频率路径没有该 enable 写。
4. 两路径汇合后 `6934/6938` 构造 `0xf7ffffff`，`6944/694c` 清 base+40 bit27，再沿旧启动轮询，最后 `6992` 返回0。没有把阈值、enable 或缓存移到统一成功确认之后。

第3项是明确已有概述的精确 load 顺序，不构成 D15 语义纠错或新增功能。D15 没有声称两次 load 的具体先后。

来源层级另行接受其限制：本地候选 SDK `D:/Documents/PlatformIO/Projects/bouffalo_sdk/drivers/lhal/include/hardware/pwm_v2_reg.h:72..89,125..129,153..163` 提供 CLK_DIV/CLK_SEL/PERIOD/THREL/THREH 字段名；ROM 掩码及偏移与之对应。n900 `core_feature_dsp.h:6291..6304` 给 PKBB16 位片拼接说明。这些是候选 SDK 中的厂商说明文本，**不是已认证匹配本 ROM 芯片/ISA 版本的硬件原规范**；历史 opcode77 编码仍依本地旧合同解释。未读取或认证 SDK git HEAD，未把历史固定 revision 当成本轮版本证明，未取得 lower/helper 原源码来源证明，也不因局部相似排除整库。正常波形、时钟源硬件含义仍不可从字段命名推出。

## 真正新增

功能恢复新增 **0**。本轮是独立技术复核；新增留存仅为最小除法 epilogue 字节、必要 ABI/原序断言及接受范围。无生产源码、模型、ROM、配置变更，无完整函数重导、资源提取、全库排除或机械哈希清单。

## 未闭精确边与实际验证

未闭项为：历史 P opcode77 与真实芯片厂商 ISA 版本的独立认证；三个 helper/原 lower 的源码及库版本；设备当前 frm；实际输入时钟及输出波形。D15 原穷尽分支不在本轮正常数值验证范围；未测试异常、溢出或越界输入。旧停机消费者未知保持继承，没有以这次算术复核补闭。

实际执行 `python reverse/analysis/pwm-arithmetic-review-d16-0041-20261024/verify.py` 通过：旧 round2 窗口逐字节相符、D15 全部稀疏指令字节相符、80MHz常量、三条 AUIPC/JALR 的目标与 ra 字段、MULA/PKBB16 位域、缓存/MMIO锚点及除法返回 epilogue。该脚本只读主仓 ROM，写独占结果；没有固件/指令模型/SIM/构建/回放/设备/网络执行，没有打开共享 REA target。`git diff --check` 通过。

本轮问题已在上述证据层级闭包。一个后续闭包可限定为取得匹配芯片版本的厂商历史 P 编码原规范后认证 `f797f50e`；在获得新材料前无需再次恢复 PWM 主体、重搜消费者或追加相同字节导出。
