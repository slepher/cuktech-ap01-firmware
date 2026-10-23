# C06：PogoPin 关闭分派独立限定复核

2026-10-23；分支 `codex/re-0041-c06`，基线 `6802ed6`。**限定接受 C05，未发现需纠正的核心语义；不代表完整关闭或 timer 生命周期验收。** 仅静态复核，不执行固件、不连接设备/外部服务、不进行缺陷验证。本文伪代码是分析者表达，不是原始源码。

## 问题、范围与证据

只复核 [C05](pogo-close-dispatch-c05-0041-20261023.md) 三个核心函数的 type8 登记、pending 链与 consumer callback 实参；initializer 仅复核已有摘链和消费窗口。未展开整个 dispatcher/event loop/timer。适用任务书及 REA 技能已读；本树及所检查的适用祖先、reverse/reports/analysis 目录未发现 AGENTS.md。

本次 [review-evidence.json](../../analysis/pogo-close-dispatch-review-c06-0041-20261023/review-evidence.json) 由 [review-static.py](../../analysis/pogo-close-dispatch-review-c06-0041-20261023/review-static.py) 生成。只读主仓库 `roms/0041/ap01-1.0.2_0041.bin`，VA 基址 `9ffff000`；与 C05 保留的 12 个窗口共490 B逐指令原字节比较，另独立人工解读70处原编码，13个32位分支/JAL直接从位域重建有符号目标。没有运行 C05 会写证据的脚本，没有打开共享可写 REA 会话/数据库，没有修改分析器模型。沿用已有ROM身份记录，不增加哈希清单。

## 逐项验收

| 项目 | 判定 | 原指令与限制 |
| --- | --- | --- |
| `a009fb96(a0=handle,a1=cb)` 的前置条件和保存 | 接受 | `fbaa/fbac/fbb0` 检查 flags@+2c 低2位；为0才直接转 `fbc2`。`fbc2/fbc6` 写 OR 1，`fbc8` LBU type@+8，`fbcc` SW cb@+c，`fbd0` 保存原 handle 到 s2。assert异常路径不作返回保证。 |
| type8 分支实际可达 | 接受 | type=8 不走 `fbd2` 的9分支，也不满足 `fbd6` 的9<type；在 `fbe0` 满足4<type，至 `fbfe`，不匹配7，`fc04/fc06` 比较8后转 `ffbe`。`ffbe` JAL `a009f972`；此前正常路径未改a0；`ffc2` 回 `fcde`，后者恢复a0=s2并调用 `a009c228`。callee实际停止行为未核。 |
| `a009c228(a0=handle)` 链表合同 | 接受 | `c230..c24c` 要求 flags bit0=1、bit1=0，异常走assert。`c256` 取 handle+4 的 loop；`c258` 读 loop+d4；`c25c` 写旧head到handle+28；`c25e` 写原handle为新head。即头插链；不把+10的另一链节点误当pending next。 |
| initializer 摘链与先存next | 接受局部 | `a005c166/c16a` 先读 loop+d4 到a0，再清head；`c16e` 非空转 `c802`。`c802` LW s5,28(a0)，`c806` JAL `a009f524`，`c80a/c80c` 以保存的s5进入下一次非空测试。s1=loop沿用已有容器合同；这里只核此窗口，不证明登记后必再次到达。 |
| `a009f524(a0=handle)` type8 路由 | 接受 | `f538..f564` 核bit0=1/bit1=0并设置bit1；`f566` LBU type，`f56c` 保存原handle到s1。type8落入 `f580..f58e`，`1<<8 & 0x275e = 0x100`，跳 `f8b6`。此前type15、type>15、type14、type0分支对8均不成立。 |
| 共用尾部flags与计数 | 接受局部 | `f8b6..f8c2` 在bit3非零时清bit3；`f8c4/c8` 使用该尾部原flags bit0，为1则跳过loop计数减一。type8此处之前没有调用其他清理函数，且本函数前置已要求bit0=1，因此C05的局部分支说明成立；不能推广为其他type或全链计数不变式。 |
| list helper和callback实参 | 接受 | `f8d6` a0=s1+10，`f8da` JAL `a0098b4a`；helper副作用未展开。`f8de` LW cb@+c，空转返回；`f8e4` a0=s1，`f8e6` 原编码 `8297` 为 C.JALR a5。传入原handle，不是其首word。`f8e8` 直接转恢复返回，未消费callback业务返回值。 |
| poll类型与context入口短佐证 | 接受局部 | `a009e5f6/e5fc` 将8按byte写poll+8；`e600` flags=8，`e604` loop写poll+4。`a00a3bd0` 原编码 `0441` 为 C.LW s1,0(a0)，故context由callback自己读取。四个poll具体容器和注册关系沿用已验收C03/C04，不重复全函数验收。 |
| 业务返回值、全局生命周期与来源 | 未核、保持未知 | 三个核心函数业务返回值均未确认；assert是否返回、opaque callee副作用、关闭后调度机会、退出路径、timer删除及全局所有权均不在本轮范围。没有来源/版本证据，不因布局相似认定libuv或排除底层函数。 |

## 接受的最小视图

```c
// 仅满足前置条件的type8局部；偏移为十六进制。
close_type8(h, cb):
    h.flags_at_2c |= 1;
    h.cb_at_0c = cb;
    opaque_a009f972(h);
    h.next_at_28 = h.loop_at_04.head_at_d4;
    h.loop_at_04.head_at_d4 = h;

// 既有initializer片段；不表达完整event loop。
h = loop.head_at_d4;
loop.head_at_d4 = 0;
while (h != 0) {
    next = h.next_at_28;
    finish_a009f524(h); // type8末端: cb = h.cb_at_0c; if(cb) cb(h)
    h = next;
}
// a00a3bc6(h) 内部才读 h.word_at_00 为context。
```

字段事实：handle+04为这里取出的loop地址，+08为8位type，+0c为32位callback，+28为32位next，+2c为32位flags；loop+d4为32位head。字段命名和“关闭待处理链”为用途推断，受登记/消费调用关系支持，不宣称完整ABI。loop+4与PogoPin ctx+198仍是不同字段。已核局部普通指令没有直接覆盖handle+0，但未展开callee不包含于这一否定结论。

恢复程度：type8局部登记→入队→既有消费片段→`cb(poll)`静态调用及实参合同可接受；“必定调用”“恰好一次”“释放前全局时序”仍未知。完整PogoPin关闭/timer停止删除未完成。来源状态：PogoPin私有封装与底层分派/链函数仍按私有或来源未知管理；新增确认开源排除为0。

## 实际验证与下一任务

运行本C06脚本：12个已有窗口490 B与ROM完全一致；70处独立选定编码比较通过，13个32位branch/JAL位域目标重建通过，type8掩码结果为0x100。脚本是静态核对辅助，不替代上述地址级指令判断；没有执行目标或编译生产项目。提交前执行 `git diff --check`，检查独占新增文件范围。C05报告无需修改。

下一小任务建议：只选既有PogoPin deinit返回后的一条直接调用链，检查是否可到达已知head消费窗口；限定1～3核心函数，保留无法闭合的边，不扩展完整event loop或timer系统。
