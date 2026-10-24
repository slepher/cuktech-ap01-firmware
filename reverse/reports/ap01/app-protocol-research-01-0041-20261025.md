# Q11：MiIO packed 协议配置到普通提交接口

**接口已闭合（限定静态输入→本地转换→普通提交调用及 caller 通知，作者研究待独立复核）**。不含底座确认或协议物理生效。认领 Q-11，作者 `/root/app_protocol_research_01`；分支 `codex/app-protocol-research-01-20261025`，基线 `816b09d`。预计10–16分钟、中置信，实际可测 UTC 16:50:59 至文末时间；首次时间读数前另有规则/证据读取，完整启动时间不可得，不以该区间冒充完整工时。无排队或中断；工具调用同步等待，未单独计量。token 用量不可得。

本文伪代码及结构名是静态分析命名，不是原源码。使用 reverse-engineer-anything 技能的事实/推断/未知分离方法，仅只读留存和必要原字，没有打开或切换 REA、执行固件、模型、SIM/QEMU、回放、构建、联网或设备操作。

## 继承结论与查重

读取主仓未提交的 reverse-design 3.1/3.2/5.1/7、rolling-management 顶部与 Q11 行。针对检索主仓报告及 analysis 的 `a009c8a4/a009c662/62fc91a0/91a4`，未见较晚转换合同。buzzer-round3 只排除两槽为蜂鸣，E07 只把 `a009c6a4` 定为普通 item+14 读取；不能据此认证本轮 packed 转换。N01 mode 与 P14 开关/安心充为不同对象/入口；`a009cc0c` 自定义功率沿既验，不展开。

继承 [B10](basic-info-dispatch-caller-b10-0041-20261023.md)/[B11](basic-info-dispatch-review-b11-0041-20261023.md)：`a00a53c0(word index)` 返回借用 item 或 NULL；owner=`u32[62fcb2cc]`，owner 非空且 unsigned index < `u8[owner+6]` 时，按既有 MULA 模型返回 `u32[owner]+index*0x1a8`。不继承 item 有效性之外的新保证，不持有、不 free。

提交继承 `reverse/rehost/charge-complete-0041.json#/records/22` 的 `a01b272c`，EID `ev_d97cb7170ca8cb469dfadc2fa50720df6b6619ef04203b9e0d76a24f9154eaec`。本轮仅接合调用，未重算 wrapper/公共 submit、copy/queue/MCU。`a01951e2` 内部行为不作为本轮新增。

## 本轮复核或纠正

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；offset=VA−`0x9ffff000`。静态复验脚本重新核身份；供应商提取指令的文本省略 msb/lsb，本轮按原 word 取字段核对，避免把 `(p&0x3ff)>>9` 误读成多位字段。

完整留存来源（均相对主仓）：

| 函数 | 定位 / EID |
| --- | --- |
| `a009c8a4..cbdb`，824 B | `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-008.json#/structuredContent/normalized_result`；`ev_ed7e71f1bd106ab36710c56dfbcad813bb82ce7c1c69484bfd18f4da5eddf6d7` |
| `a009c662..c7cd`，364 B | 同目录 `whole-rom-private-20261023-006.json` 同 pointer；`ev_32edb8a17764f474455354c17df1d950e43cd7dbf42deeec64921a33c9ad23d7` |
| caller `a009d8bc` | `reverse/analysis/miio-deferred-settings-0041-20261023/retained-functions.json#/functions/1/normalized_result`；源 `whole-rom-private-20261023-015.json`，`ev_17a8de6820bfe771a96a269aef06904915c9fd915bf3dd149e40a78307a6e1e2` |

以上3份使用留存 Ghidra 12.1.4、私有 `RISCV:LE:32:ap01thead2`；profile digest `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。私有模型不等于独立上游 ISA 认证。[复验源码](../../analysis/app-protocol-research-01-0041-20261025/verify.py)与本地忽略的 [原字窗口](../../analysis/app-protocol-research-01-0041-20261025/instruction-evidence.json)保存原偏移、字节、提取字段及来源；后者需由父窗转存相同路径。

## 真正新增：两属性的同一转换合同

`a009d8bc(siid,piid,uint32 p)` 在 siid=4 的两分支均先保存完整 p，再无条件调用 `a009c8a4(p)`，没有先按属性选择 C1/C2：

| 属性 | caller 本地镜像 | 转换调用 | 通知调用 |
| --- | --- | --- | --- |
| 4/0x0e | `u32[62fcafe8]=p`，`dda6` SW | `ddaa → a009c8a4` | `a0195144(4,0x0e,p&0xff,0)` |
| 4/0x11 | `u32[62fcafec]=p`，`dde6` SW | `ddea → a009c8a4` | `a0195144(4,0x11,p&0xff,0)` |

二者差异仅为镜像地址、属性号及日志；转换覆盖端口相同。`ddcc/de0c` 的 ANDI 0xff 证明通知丢掉 C2 的 bits8–11；即使只改 C2，仍传低8位而非重建后的全 packed 值。分支返回0只表示接受本地分支，无等待、无 submit 成功门、无确认通知。caller 前导 `a009cbdc/a009d840` 保留为既有不透明前置，未扩 dispatcher。

两槽从 `62fc91a0` 开始，stride=4，C1=index0，C2=index1。表中命名 PD/PPS/UFCS/SCP 来自同函数日志，不是产品规格认证：

| 协议 | C1 输入 bit | C2 输入 bit | 每槽 byte0 bit | disable mask bit（0代表允许） |
| --- | --- | --- | --- | --- |
| PD | 0 | 8 | 7 | 3 (`0x08`) |
| PPS | 1 | 9 | 6 | 4 (`0x10`) |
| UFCS | 2 | 10 | 5 | 5 (`0x20`) |
| SCP | 3 | 11 | 4 | 7 (`0x80`) |

输入为完整32位按值标量，仅 bits0–3 与8–11有转换用途；bits4–7、12–31在转换器被忽略，caller 镜像仍原样保存，低8位通知仍可包含 bits4–7。输入 bit=1 将对应 byte0 bit 置1，生成 mask 时反向：缓存该 bit 为0才 OR 对应 disable 位。不是直接转发 packed，也不是8位 lane 的全部位生效。

`a009c8b8` 首先调 refresh，返回值不使用。随后每端口比较这4个 bit，仅不同时用 LBU/AND/OR/SB 修改 byte0 的相应 bit。byte0 低4位不变，槽 byte1/2/3 不由 setter 修改。虽比较读32位，原 SB 证明没有覆盖整槽。每端口独立变化门：任一 bit 变才计算该端口 mask 并调用 `a01b272c(0或1,mask)`，都不变则跳过；C1 在 C2 之前。门位于 `a009c9b2/a009ca54` 与 `a009cb24/a009cbc6`，不以输入整 word 差异触发。最多每端口1次调用。

```c
// 语义伪代码，不执行；保留 refresh 和两端口顺序。
refresh();                         // bool 返回被忽略
for (port = 0; port < 2; port++) {
    changed = false;
    for (k = 0; k < 4; k++) {
        desired = (p >> (port*8+k)) & 1;
        // slot=62fc91a0+port*4；仅改 byte0 的 bit(7-k)
        if (bit(slot[0],7-k) != desired) {
            slot[0] = replace_bit(slot[0],7-k,desired);
            changed = true;
        }
    }
    if (changed) a01b272c(port, inverse_mask(slot[0]));
}
```

原字例：`a009c92a:8b371904` 解出 EXTU msb=lsb=1；`a009cb1c:8b37b92c` 为11..11；`a009c90c` SB 到槽0 byte0；`a009cb38` SB 到槽1 byte0。`ca0e` 的 a0=0 和 `cb80` 的 a0=1 与紧接 AUIPC/JALR 指向 `a01b272c` 对应。mask 最大0xb8，不带其他 disable 位；不是从槽+2整体透传并保留未知 mask 位。

### 同对象 refresh 与提交接合

`a009c662()` 固定 index0、1 两次 getter；取 `u8[item+0x14]` 作为实际缓存来源，只同步借用，不保存 item 指针。NULL 仅日志然后继续，不改槽，不纳入返回 changed；NULL 日志可能带上一槽的临时 mask，不能当该槽状态。

每槽 byte2 是上次观察的完整8位 disable mask。只有新 mask != byte2 才反解表中4位到 byte0，最后 `slot[2]=mask`。byte1/3及byte0低4位不变。返回 bool 是两槽4个开关字段中是否至少一个实际改变；若只变未映射 mask 位，byte2仍更新但返回false。相同 byte2 时即使 byte0 被 setter 改过，也不会重算。setter 不更新 byte2，因此重复相同请求可能在尚无确认时因本地变化门而跳过；这是静态缓存机制，不是确认/重试合同。

继承 wrapper 的有限合同：`a01b272c(port,mask)` 先 getter(port)，NULL 则日志返回；`u8[item+0x14]==mask` 则日志返回；再要求 `a00a533a(port)!=0` 才构造栈 descriptor `{cmd=0x67,len=2,payload*}`，payload为 `{u8 port,u8 mask}`。`0x0267` little-endian 的首半字正是67,02。调用 `a01951e2(&descriptor)` 后返回，无业务成功返回。helper第二门不在本轮解释为全套在线/能力状态。

输入 p 按值，caller 镜像/两槽是静态存储，不建立输入指针持有。refresh item 只借用。wrapper 的 descriptor 与2B payload 属于 wrapper 栈，仅在同栈 submit 调用期间借用，不转移所有权；局部地址不能供后续异步持有，后续复制/队列遵循既有 submit 合同，本轮止于该边。无本轮新增 alloc/free、取消或超时对象；缺少确认不伪造超时结果。

## 未闭精确边与检查

本轮闭合的是本地配置到普通提交的接口阶段；底座响应如何更新 item+14、真实应用协议、物理协商结果、持久化及云端值格式均未认证。一个有种子的后继是沿既有 `a00a8582` 普通 item+14 生产路径与 cmd67 正常响应连接，先查 P17/既有 response 覆盖再定差集；不能由当前通知推定已闭合该往返。

实际运行 `verify.py` 通过：ROM尺寸/SHA，824/364 B 连续 body 原字覆盖，11个原字位提取字段，9个 SB 宽度，2个 caller JAL目标、2个 submit AUIPC/JALR目标和2个通知 ANDI255。人工核对完整两局部 body 的4位变化门、两端口顺序与 mask 方向，并针对核 caller/继承 wrapper；没有运行行为模型或历史回放。合同 JSON 可解析，`git diff --check` 通过。报告/合同 JSON/脚本为入库成果；`instruction-evidence.json` 是 ignored 中间产物。独立技术复核尚未进行。

完成检查 UTC **2026-10-24 16:54:59**（HKT 2026-10-25 00:54:59）；首次钟读数至检查完成 **240秒**，此前规则/证据读取未计入，完整墙钟不可精确恢复。预计10–16分钟高估，材料完整且三个业务节点较短；实际提前闭合后立即交付，不补扫凑时长。ignored 原字文件88271 B，SHA256 `8a3c386252b8746478971a3816461a6f6f562431a572b1c1d6ac784f879b1af2`，供父窗复制核对后再清理任务树。
