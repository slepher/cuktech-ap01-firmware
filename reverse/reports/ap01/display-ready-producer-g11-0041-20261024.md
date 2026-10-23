# G11：ready producer 与一次正常登记的字段连接

2026-10-24；基线 `173ee40`；分支 `codex/re-0041-g11`。**补齐 a010d7da 的记录 materialization，以及一个实际 fallback ADD→通知标志→记录→旧消费者的条件静态连接。** 此函数不直接调用 epoll_wait；不证明硬件 ready 已发生。作者静态验证通过，待独立技术复核；新增页面业务、整库来源认证均为 0。

## 继承结论：已有出处→行为→局限→精确缺口

|出处 / 证据|已有行为|局限及本轮范围|
|---|---|---|
|[G09](display-ready-dispatch-g09-0041-20261024.md)、[G10](display-ready-review-g10-0041-20261024.md)|返回记录 +0 events、+8 fd、stride16 的消费视图；同 fd bucket→watcher−14 别名→callback(loop,watcher,mask)|直接继承，不重导消费者、公共 poll/start/stop 或业务 callback。本轮认证生产写入与这个消费视图的来源|
|G07/G08 的显示 work/adapter 合同|state+60 poll、state+94 watcher，events2→mask4，adapter→a00806d0→stop/刷新/清 pending|沿用，不能据本题声称实际显示完成|
|factory-test/retained-initializer.json，`ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；来源 round3/whole-rom-round3-initial.evidence.json|a005c202..258 已有 pending 更新提交；c2c4..34e 已有解析 backend、rearm、等待、collect、释放借用对象的完整留存|这不是首次发现提交/等待。仅核字段和同一对象身份；旧原汇编/raw 不再复制|
|whole-rom-coverage round1 已有 extent/direct-call 证据|a010d7da extent `ev_ea8134c4fc96e80b69de66948d09a01a8f1d4ea1c54c90026afac08eb7fbb894` / calls `ev_b2bb62d2b4332f4f40b26d460a3f5989392f7775d096b67c92c78987220a26fa`；a010e722 extent `ev_7ffffe00ba625034e0ec16070fde9161cb63a71825abc1b79548e0574916530e`|已有函数定位不等于已有字段恢复。本轮只读取所需原字节窗口，不新开或切换任何共享 REA target|
|G09 的 complete/最终矩阵/ZIP/业务替代复用结果；本轮精确检索较晚 round3 retained|whole-rom-round3-initial 对 a010d7da/a010e722/a009e0e6 的命中均落在旧 initializer 的引用；sub64-no-return 有另一调用者 a0062d28|另一调用者不在本题展开。较晚命中没有 producer body；有界文本结果不声称此前从未分析。SIM/替代结果不能认证 ROM backend ABI|

## 本轮复核或纠正

旧 initializer 五个必要窗口共 206 B 与当前只读 ROM 逐字节相同，记为旧证据复核。a005c08c..094 得 `private = word(loop+14)`、提交附加上下文 `private+84`；c0da/e4 保存 `backend_fd = word(loop+20)`。同一个 backend_fd 同时进入 a009e0e6 和 a010e6cc，后者返回的 backend 指针保存 frame−128，随后传入 a010d738 和 a010d7da；collect 结束后按旧原序 a0027e54 释放解析函数取得的 file 借用。不是把整数 fd 直接当 backend 指针。

对 G09 消费视图作精度补充：**producer 的 +8 实质是 caller 登记的 data 低 word，在本 libuv 路径才等于 fd**，不是 backend 从节点 fd 字段自动填出的通用 fd 字段。记录 +4 在本 producer 中没有写入，不认证完整 C/system ABI。

## 真正新增：一个实际 backend 的正常 ADD

a009e0e6 的六参数偏移视图为 `(backend_fd, submit_ctx, scratch, op, fd, record)`。e104..110 保存 fd/record/backend_fd/op，并测试 submit_ctx+3c；**仅沿该 word 为 −1 的 fallback**，e114..11a 调 `a010e722(backend_fd,op,fd,record)`。另一个分支的 ring 提交不在本轮恢复。返回0走正常尾声；失败时 op2 直接尾声，op1 检查 errno==17 后以 op3 重试，否则走原断言路径。未假定断言必不返回，也未将所有失败解释成成功。

旧 c202..258 把 pending node−c 还原为 watcher，取 watcher+1c desired、+20 installed、+24 fd；installed==0 时初值 op1，否则 op3。遍历相同 fd 的 bucket 时，其他 watcher 的 installed 非0才把其 desired 合并，并改为 op3。本轮连接限于**首次登记、同 fd 无其他已安装 watcher、fallback 成立**的实际 ADD 路径。c248 在提交前已写 installed=desired，不能改写为成功后才写。

输入 16 B record 先由 c0da..ec 清零；c22c 写 events 到 frame−d0，c254 写 fd 到 frame−c8，即 record+8。故普通非负显示 fd 的数据高 word +c 为0。a010e722 先通过 a010e6cc 取得 backend：该解析检查 file+0c 所指对象+10 等于 `0xa060833c`，成功才返回 file+10；失败按原路径置 errno 并返回0。它提供了同类 backend 对象门，不构成整个驱动来源认证。

ADD 的必要节点视图如下，偏移名均为分析者表达：

|节点字段|生产位置及用途|
|---|---|
|+0/+4|链节点；ADD 成功后挂在 backend+24 哨兵链，collect 从 backend+28 的尾向前读取|
|+8/+c|e7d4..e7e2 从输入 record+8/+c 复制的 data64|
|+10 byte|e7dc 初始化0；通知 callback 写1；collect 的门|
|+14 word|e7ea 写 fd；底层登记/解除用它，与 opaque data 分开|
|+18 word|e7e4..f0 写 `record.events | 0x10000`|
|+1c word|e7fe 清0；collect 读取的 revents；本轮未沿设备实现认证它的非零写者|
|+20/+24|e7fa/fc 写 node 自身和 callback `a0109b8e`|
|+2c|e7d2 写同 backend 指针|

节点由 a010d70e 从 backend+3c 的空闲链取出；整块池分配/析构没有重新恢复。e802..80c 以 `(fd,node+14,1)` 调 a003e674；返回>=0 才在 e87c..88c 挂 backend+24，走 e902..910 解除对象内锁、释放 file 借用并返回0。负值走空闲链归还和 errno 路径，不能宣称仍登记成功。a003e674 自身解析 fd 后调用 a003e344，再释放 file 借用；具体设备 poll 方法与实际通知时序停在此边界。

安装的 callback 在 a0109b8e 从参数+0c 取 node（参数是嵌入的 node+14 视图），a0109b92 **只就此窗口认证写 node+10 byte=1**；它不是本轮找到的 revents 非零写者。其后有条件唤醒路径，不把唤醒或真实驱动执行当已发生。

## 真正新增：collect 的参数、返回值与写入

a010d7da 的正常 ABI 为 `(backend, out, signed_capacity)`；d7fc/d800/d802 保存至 s2/s6/s8，d80c 置 count=0，d844 返回 count。对象+8 的 a0027968/a00274b2 调用保持前后原序；collect 没有检查前者返回值，不能加上推测的失败返回−1。

下列伪代码只表达所核原指令，非原源码。链 helper 名称不表示重新实现了源码：

```c
enter(backend + 8);                 // 返回未检查
node = word(backend + 0x28);
previous = word(node + 4);          // 先保存，再处理节点
count = 0;
while (node != backend + 0x24) {
    if (byte(node + 0x10) != 0) {
        a003e674(word(node+0x14), node+0x14, 0); // 返回未检查
        unlink(node);              // 再将 node.next/prev 清0
        if (word(node+0x1c) != 0 && count < signed_capacity) {
            slot = out + (count << 4);
            word(slot+8) = word(node+8);
            word(slot+12) = word(node+12);
            events = word(node+0x1c); // 数据写后重新读取
            count++;
            word(slot+0) = events;  // 厂商 indexed store，+4 不写
            if (word(node+0x18) & 0x40000000)
                append_to(node, backend+0x34);
            else
                append_to(node, backend+0x2c);
        } else {
            append_to(node, backend+0x2c);
        }
    }
    node = previous;
    previous = word(previous+4);
}
leave(backend+8);
return count;
```

原指令 d874 是 signed `bge s3,s8`，容量8时输出0..8条；它会继续遍历，容量用尽的已通知节点仍被解除并放到 backend+2c，不能改写成满8立即退出或保证这些事件本轮返回。d868 的非零测试之后，d888 再读 revents，未把两次读合并。d878..886 将 data64 先写 +8/+c；d87c 的 count<<4 给出步长16。d88c 原字 `8b57db40` 拆为 opcode=0b/funct3=5/top5=8/rd=15/base=22/index=13/shift=0，按只读模型 `th.srw` 是32位写 `out + offset`，无 base 写回。它确证 events 写 slot+0，而非把 custom0 当未知函数跳过。

输出后的 node 在 bit0x40000000 分支挂 backend+34，否则+2c；无 revents或容量不足也挂+2c。本轮不据常见常量把它认证为某库标准 one-shot 枚举。a010d738 对+2c 链清 node+10、node+1c，以 `(fd,node+14,1)` 再登记；负值立即按旧返回路径退出，成功才移到+24。这给出重复等待所需的 rearm 顺序；producer 不释放节点，不把输出 record 当节点所有权转移。

旧 initializer 用相同 backend、栈上 out=frame−c0、capacity=8 调 collect；返回后释放 file 借用，再由既有消费者遍历 count 条。由于上述 ADD 把 record.data64 设为 fd/0，collect 的 slot+8 恰接 G09 的 fd 读取；slot+0 接 G09 的 events mask。输出是32位值复制，消费者不借用 node 本体；其后 watcher 间接 ABI 与业务行为完全继承 G09/G10/G07/G08。

## 未闭精确边与实际验证

- 未知：目标 fd 实际设备方法何时把 node+1c 写为非零、是否调用已安装 a0109b8e、是否真实达到 mask4。这是**底层登记已正常返回→真实通知/revents**的运行时及设备边；本轮不将返回>=0等同已有ready。
- 本题只认证 fallback 的首次 ADD 与必要 rearm/collect。完整 MOD/DELETE、submit_ctx+3c!=−1 分支、并发/重入及池析构不在闭包内；不扩全部 fd/libuv/网络。重复 fd 合并可走 op3，本报告的首次ADD条件明确排除此情形。
- fd复用、watcher是否仍挂、callback次数、默认display同一性、a009d382副作用和退出后drain继承旧未知。没有认证 NuttX/libuv 的精确源码版本或整库来源。

[verify.py](../../analysis/display-ready-producer-g11-0041-20261024/verify.py) 执行通过；[evidence.json](../../analysis/display-ready-producer-g11-0041-20261024/evidence.json) 留存334 B新必要窗口、206 B旧窗口比对索引、58项字段/调用/分支检查及较晚round3复用记录。常规I/S/压缩访存、signed分支、厂商srw独立按原编码核对；其余局部汇编来自只读ROM（VA−0x9ffff000）。没有重复导出旧整函数或修改模型。未开新REA会话、未运行固件/SIM/构建/历史回放/设备/网络；只改独占报告和analysis文件。

一个必要后继可独立复核本次 data64→fd身份、srw写入及节点重排/容量分支。若进一步研究真实ready，只沿已安装 node+14 的一个目标设备 poll 方法定位 node+1c 写者与正常通知接入；不能从通用 callback 已安装推断设备已触发。
