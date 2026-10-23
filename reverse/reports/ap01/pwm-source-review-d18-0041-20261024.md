# 0041 D18：D17 PWM lower 候选来源独立复核

基线 `6385a09ffb42acef904e3e6360200a9a5042ea21`，独占树 `re0041-d18`，分支 `codex/re-0041-d18`。按 reverse-engineer-anything 技能，只读复核 [D17](pwm-source-auth-d17-0041-20261024.md) 已指定的 NuttX BL602 与 SDK PWM v2 源行。**接受 D17 的有界结论：BL602 可见 lower 与 ROM 合同不等价；SDK v2 寄存器操作局部相容，不能认证 ROM 80MHz binary64 分频搜索或 duty 居中计算的来源。未发现需要纠正的源行比较。新增功能 0，新增整库排除 0。**

## 继承结论：已有出处、行为与本轮缺口

|已有出处|直接继承的行为或身份|证据局限及本轮缺口|
|---|---|---|
|[round2](buzzer-backlight-round2-0041-20261023.md)、[round3](buzzer-backlight-round3-0041-20261023.md)|upper 24B 副本、固定两路 PWM、lower/Info/通道表及正常启停合同|不重搜消费者，不重做旧 complete/ZIP 或通用 ioctl；本轮无该层新增|
|[D15](pwm-arithmetic-d15-0041-20261024.md)、[D16](pwm-arithmetic-review-d16-0041-20261024.md)|`a0136762` 的缓存频率门、80MHz binary64 搜索、helper ABI、低32位 duty 乘加、阈值打包及 MMIO 原序|已独立核过的 ROM 合同直接引用；本轮不读取 ROM、重导函数或重算厂商字，仅用于比对候选|
|D17 及其引用的 A13/A14/F07、D07/D11/D12|NuttX 候选 `/home/slepher/nuttx-ap01-sim/nuttx`，历史 HEAD `6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`、标签 `nuttx-12.10.0`；SDK `D:/Documents/PlatformIO/Projects/bouffalo_sdk`，历史 HEAD `41bf338a57be53919d99f6c6715a96100428c97d`、VERSION 2.3.36|身份为旧报告继承，不重复身份账，不表示本轮重新认证 HEAD、ROM 版本、芯片、ABI 或构建配置|
|D17 的源行表及 `source_check.py` / `source-check.json`|BL602 算术/对象/寄存器差异，v2 threshold/enable/start 局部对应，未匹配计算层保持未知|本轮直接读指定行及必要上下文，独立检查比较强度；不重复全候选发现、单文件 literal 负搜索或原脚本29项检查|

业务合同和所有权仅继承 D15/D16：入口 `a0=Lower*`、`a1=Info*`，借用对象及 lower+8 通道表；复制两项 duty32 和频率，缓存 period16，无分配或所有权接管。正常出口0不保证所有 MMIO 已配置。频率变化时搜索 `truncate_u32(div64_frm(80000000.0,u32_to_binary64(denominator)))<65536`；duty 使用 `half=P>>1; delta=((0x8000+P*D) mod 2^32)>>17` 后形成对称端点并各截16位。这是分析关系式，不是原源码，也不是 D18 新恢复。调用顺序、重读和失败/skip 分支仍以 D15/D16 为准。

## 本轮复核或纠正：逐项判定

下列 NuttX 路径相对 WSL Ubuntu-24.04 的上述根；SDK 路径相对上述 Windows SDK 根。全部为源文本事实，和继承的 ROM 合同比较；未将静态文本称为实际执行。

|D17 比较项|本轮直接检查的定位与结果|判定与限定|
|---|---|---|
|BL602 start 接口及顺序|`arch/risc-v/src/bl602/bl602_pwm_lowerhalf.c:363–394`，`include/nuttx/timers/pwm.h:238–244`：非 PULSECOUNT ops 为 dev/info 两参数、int 返回；start 在 NCHANNELS 分支按 channel 取值、遇 -1 退出，再调用 freq、duty、enable；另有单通道0分支|接受接口形状对应和 start 逻辑差异。只比较这些可见分支，不推定 ROM 的宏配置；ROM 固定两槽/缓存门不由候选接口证明|
|BL602 频率与对象|lower `:47–62,82–86,199–224,271–288`：40/80MHz 为条件选择；私有结构只有 ops 和 `uint32_t chan_pin[5]`；init 的 clk_div=0，freq 的 period 为 `uint16_t`，直接整数除法后写周期|接受。80MHz 字面共同出现不能证明同源；这里的直接除法与 ROM 的 binary64/分母累加搜索不是同一合同。对象也没有 ROM 已核的表指针、period/frequency 字段语义|
|BL602 duty|lower `:235–258`：读取 period 后设置 threshold1=0，threshold2 为 `(uint16_t)((uint32_t)period*duty/65535)`，依序写两个独立阈值寄存器|接受。与 ROM 偏置0x8000、低32位乘加、右移17、对称端点及单word打包有具体差异；不把通常 PWM 算法替代 ROM 算术|
|候选 Info|`include/nuttx/timers/pwm.h:162–189,203–207`：channel 条目首字段 duty，条件 overwrite/deadtime 字段，后有 cpol/dcpol/channel；Info 首字段 frequency，另有 arg|接受作为布局参考，**不接受完整类型认证**。本轮未编译、未取宏值，不能从两个 duty 偏移直接证明完整24B、padding、arg 或 ROM 未读字段|
|BL602 寄存器族差异|`arch/risc-v/src/bl602/hardware/bl602_pwm.h:39–63,83–88,125–139`：每通道0x20步长；分立 clkdiv/thre1/thre2/period/config，阈值各16位 mask；stop bit6|接受。与 ROM 共享+40/+44/+48、+50+4*channel 的打包阈值及 stop bit27 不同。没有将候选头的硬件命名作为 ROM 芯片认证|
|v2 init 的局部对应|`drivers/lhal/src/bflb_pwm_v2.c:8–65`，`drivers/lhal/include/bflb_pwm_v2.h:217–224`：caller 提供 uint16 clk_div/period，PBCLK 选值1；non-ROMAPI 可见体清/写分频和周期字段，BL616CL 另处理 counter_mode/update|接受局部对应。SDK API 消费已计算值，不能给出 ROM 的频率搜索来源；ROMAPI 委派目标、BL616CL 宏及实际构建未知。字段清除/写入不是整个 init 与 ROM 等价证明|
|v2 阈值及 positive enable|v2 source `:303–328`：setter 参数已是 uint16 low/high，打包 high<<16 \| low，写 `+PWM_MC0_CH0_THRE_OFFSET+ch*4`；positive_start 读+CONFIG1、OR `PWM_CH0_PEN<<(4*ch)` 后写回|接受与 ROM `a0136900/690a/6926` 末端局部相容（地址及原序继承 D15/D16）。候选没有在这些入口把 duty32 算为居中阈值；API 存在不能证明 ROM 调用、内联或复制了这些函数|
|v2 start 与位定义|v2 source `:139–161`，`drivers/lhal/include/hardware/pwm_v2_reg.h:46–53,72–107,125–163`：CONFIG0/1、period、threshold 偏移为40/44/48/50；stop bit27、status bit29、clock select shift30、positive enable 每4位；start 清 stop 后轮询 status 清零|接受启动局部形状对应及寄存器位解释的候选来源。SDK 返回 void、可超时早退；ROM lower 正常返回0，不能覆盖其 ABI，也不能用 SDK timer 名称认证 ROM 的等待单位|

纠正项：**无**。表中每个“接受”仅限直接检查的源行事实和 D17 已限定的比较结论。D17 明确只分析可见 non-ROMAPI 源体；此限制成立。BL616CL 的 `CENTER_ALIGNED` 是候选计数模式字段，不能据名字就认定其产生了 ROM 的软件对称阈值公式。

D17 的候选发现范围及 literal 未命中记录作为既有过程继承，本轮未重做发现或负搜索。因此本轮不声称独立证明未读候选、改名文件、ROMAPI 目标或 SDK 其他实现不存在对应算法。直接读到的具体差异足以支持“这些可见实现未认证原 lower”，不需要扩大成全库排除。

## 真正新增

新增功能 **0**，新增来源认证 **0**，新增整库排除 **0**。新增留存只有上述独立源行接受范围；不新增源码副本、哈希清单或重复29项锚点账。没有需要据此修改 D15/D16 或 D17 行为结论的证据。

事实：指定候选源行存在上述字段、公式、调用及寄存器操作。推断：ROM 与 SDK v2 寄存器操作局部相容，但计算层仍需准确来源材料。未知：该层来自哪个上游版本、芯片驱动或私有适配；不能先命名为厂商修改，也不能从局部相似宣布 SDK/lower 精确匹配。

## 未闭精确边、验证与一个后续闭包

`a0136762` →准确原 lower 文件/版本/编译条件及三个软件数值 helper 来源仍未认证；Info 完整布局、真实输入时钟、frm 当前状态、历史 ISA 版本及实际波形沿 D15/D16/D17 保持未知。upper 对象关闭/停机消费者生命周期不由源级局部比较补闭。本轮没有重新核 ROM 字节，因而不声称额外独立认证原 ABI、厂商字或全部原指令。

实际静态验证：WSL 用 Python 只读打印上述三份 NuttX 文件的指定窗口；PowerShell 只读打印上述 SDK 源及两必要头的指定窗口，逐项人工比较。未复制候选函数到交付物，未运行目标、SIM、历史回放、构建、设备或网络；没有打开/改变 REA target、模型、生产代码、ROM 或配置。工作树 HEAD 与分支核对为本报告基线及独占分支；`git diff --check` 通过。只提交本报告。

本题的独立复核闭包已完成。一个后续闭包仍须以新取得的、与0041 ROM对应的原 lower 文件及构建来源为种子，认证 binary64 分频搜索与 duty 居中公式的准确来源；新材料出现前无需再搜这两个同候选或重做 PWM 主体。该未知为来源证据缺口，不是本轮工具阻塞。
