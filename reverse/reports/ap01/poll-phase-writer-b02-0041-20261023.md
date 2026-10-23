# B02：timer 之外的轮询 phase 写入者，cmd 0x58 局部合同

2026-10-23；基线 `5cc052a`，分支 `codex/re-0041-b02`。状态：**本任务局部合同已恢复，待独立技术复核；整体轮询模块部分恢复**。这是可读分析伪代码，不是原始源码。

## 问题与结论

确认 timer 之外一个直接写入者：响应 callback `a00a8582` 的 **cmd=0x58** 分支，在 `a00a878e` 对 RAM `62fc4b35` 执行 `sb zero`，只清 phase 的一个 byte。触发条件是调用缓存更新辅助函数 `a0191652(62fcb504,4,&response_view)` **返回之后**，32-bit `*(62fcb504)` 非零。值为0时跳过写入；两条路径都立即调用轮询选择器 `a0191746`。

因此不能表述为“收到0x58总清phase”，也不能把条件改为“payload第一个byte非零”“数据有变化”或“缓存函数返回成功”。这条分支没有直接重置各组 sent，也没有直接清 round_done；按[B03复核](poll-phase-review-b03-0041-20261023.md)，此负结论仅限局部直接写入，不推广到选择器或间接 handler 的副作用。直接 helper 的同步 handler 调用发生在条件读取之前，故本报告保留后调用读取语义，不将它替换成读取原 payload。

本次只恢复此分支、直接缓存依赖和直接间接调用点，不展开整个响应分派、USB状态机或0x58字段的业务含义。已知存在的 phase=1 分支留作后续小任务；其余写入者集合不宣称完备。

## 证据与来源

- [逐指令证据及核对结果](../../analysis/poll-phase-writer-b02-0041-20261023/instruction-evidence.json)：7个有界窗口，保留原字节、ROM文件偏移、既有REA Evidence ID及来源、Ghidra汇编与独立Capstone普通指令解码。
- [只读复核脚本](../../analysis/poll-phase-writer-b02-0041-20261023/verify-evidence.py)：输入主仓库绝对路径，仅写本任务证据文件。不生成新哈希清单或基线副本。
- 既有 `usb-interface-ota-0041-20261023.json`：`functions[9]` 为 `a00a8330`（来源 `whole-rom-private-20261023-067.json`），`functions[10]` 为 `a00a8582`（`...-068.json`，Evidence ID `ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`）。`functions[14]` 的 `a00a4708` 仅复用4条callback槽安装指令，不恢复其完整生命周期。
- 既有 `uart-response-0041-20261023.json functions[1]` 提供 helper `a0191652`；其局部语义已在 [B01复核报告](dock-presence-polling-0041-20261023.md) 接受。此次重新核对整个174 B helper普通指令窗口，保留其Evidence ID于JSON。

来源状态：上述 callback、私有封装、phase逻辑仍属于厂商/来源未知恢复对象。本任务没有新增开源识别、版本认证或排除项。普通内存比较/复制职责沿用既有识别；未借此认证完整库来源。

## 核心函数与调用关系

| 地址及本次恢复范围 | 参数、返回合同 | 直接关系 |
| --- | --- | --- |
| `a00a8330`，仅 `a00a8514..a00a8547` 的回调分派；前置base构造4条指令 | 外层已有poll callback形状；本次仅确认被调用者参数为command byte、length byte、payload或NULL；不认证外层业务返回值 | `a00a8538` 对槽 `62fcb6c0` 间接调用；随后重新读取槽并以 `(0x24,0,NULL)` 再调用 |
| `a00a8582`，入口和cmd0x58分支 | 输入 `a0=command`、`a1=length`、`a2=payload`；入口存byte command/length及word pointer；本分支无业务返回值 | `a00a8780 -> a0191652`，可选phase清零，`a00a8aae -> a0191746`，返回共同尾部 |
| `a0191652`，直接缓存依赖 | `a0=destination`、`a1=n`、`a2=response_view`；此调用n=4；不使用业务返回值 | 扫轮询组、可能置round_done；比较/复制缓存，变化时可同步间接通知handler |

回调槽安装证据是 `a00a4718..a00a4724`：构造 `a00a8582` 并以 `sw` 写 `62fcb6c0`。这只证明一个安装点；timer中的安装沿用B01既有证据。已保留的直接caller列表为空，不能据此说 callback 不可达：这里明确存在间接调用。实际是否执行该目标取决于调用时槽的当前值。

`a00a8330` 的局部指令先从 `s3+0x33` 取length，零时payload=NULL，否则payload=`s3+0x34`；从`s3+0x32`取command，在 `a00a8538` 调用。`a00a83fc/a00a8404` 将`s3`设为`62fcb2f0`，即command/length/payload分别为`62fcb322/62fcb323/62fcb324`。其上游帧接受条件沿用既有报告，**本次没有重新认证整个解析器**。第二次固定0x24通知不会进入本报告的0x58分支。

## 指令事实与局部伪代码

最小视图：

```c
struct ResponseView {      // 栈局部分析视图
    uint8_t command;       // +0
    uint8_t length;        // +1
    uint8_t padding[2];
    const void *payload;   // +4, RV32
};

// a00a8582 的局部投影；省略其他command分支。
void response_58_local(uint32_t command, uint32_t length, const void *payload) {
    ResponseView v;
    v.command = (uint8_t)command;
    v.length = (uint8_t)length;
    v.payload = payload;
    if (command != 0x58) return; // 仅表示本投影范围
    cache_update_a0191652((void *)0x62fcb504, 4, &v);
    if (*(uint32_t *)0x62fcb504 != 0)
        *(uint8_t *)0x62fc4b35 = 0;
    poll_select_a0191746();
}
```

原指令未初始化两个padding byte，此视图也不消费它们。

关键指令：

| 地址 | 指令事实 |
| --- | --- |
| `a00a85a0/a4/a8` | `sb a0,-0x50(s0)`、`sb a1,-0x4f(s0)`、`sw a2,-0x4c(s0)`，response_view布局 |
| `a00a8766/a` | 常量0x58与原command寄存器比较；不匹配回共同返回尾部 |
| `a00a876e..a00a8780` | 构造destination=`62fcb504`、n=4、view=`s0-0x50`并直接调用helper |
| `a00a8784/86` | `c.lw a5,0(s1)`；word为0则跳到`a00a8aae` |
| `a00a878a/8e` | `lui a5,0x62fc5`；`sb zero,-0x4cb(a5)`，地址`62fc5000-4cb=62fc4b35` |
| `a00a8792`及`a00a8aae` | 汇合后调用`a0191746`，随后到共同返回尾部；不检查选择器返回值 |

helper清传输状态、检查旧phase及组sent/limit，必要时先写round_done=1；随后比较/复制4 B缓存。比较相等不会复制/通知，但并不阻止调用者读取现有非零缓存并清phase。不同则复制，槽非NULL时同步调用handler `((view.command+0x20)&255,0,NULL)`；本调用得到0x78通知。**这些操作发生在调用者phase写入之前**，本分支没有倒回helper重算round_done，也没有直接重置sent；不据此排除后续选择器或间接handler的副作用（见B03复核）。选择器的详细规则沿用B01，不补造发送成功确认。

事实：上述地址、读写宽度、常量、先后顺序与分支均由原字节/指令支持。推断：称该字段为轮询phase沿用静态表及选择器合同；“恢复起始轮询相位”是描述性命名，并不证明重新执行完整初始化。未知：0x58四字节缓存的业务含义、实际回调时序、完整slot写入者、其他phase写入者、基础信息phase=1的完整触发条件。

## 实际验证与剩余工作

执行 `python reverse/analysis/poll-phase-writer-b02-0041-20261023/verify-evidence.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`：通过7个窗口共138条普通指令的连续边界/长度、既有raw_ranges与ROM逐字节一致、普通指令独立解码、关键跳转目标、8-bit store字段及地址计算核对。窗口内没有厂商指令，不修改模型；函数全边界沿用既有provider记录，只声明局部恢复。Capstone将PC相对目标打印为偏移，脚本显式加PC后核对，不混用绝对目标。未执行固件、构造输入、连接设备/服务或修改共享REA状态。

本任务3条Markdown链接存在，JSON可解析；明确路径暂存后的 `git diff --cached --check` 通过。只新增本任务报告、证据JSON和只读复核脚本三个文件。

下一小任务建议：只追同一callback中已知phase=1写入点的前置分支及sent/round_done复位顺序，限定该分支的直接依赖；不要接管整个响应分派。本任务不声称全部phase写入者已找齐。
