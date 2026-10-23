# B21：命令提交、固定槽消费及正常完成通知独立复核

2026-10-23；基线 `2ee39b3`，分支 `codex/re-0041-b21`。**限定接受 B20 的两个核心正常合同，没有需要纠正原报告的指令或 ABI 结论。** 本轮把生产描述符、活动副本、发送启动、匹配响应和 `0x24` 通知衔接起来，但不能把通知理解为无条件消费一槽或底座业务成功。协议模块仍部分恢复。

应用 `reverse-engineer-anything` skill，复用已有 REA 保留证据并独立只读核对 ROM；未打开共享数据库或切换 REA target。所有结构、字段名和伪代码都是分析视图，不是原始源码。

## 问题、范围和复核结果

原问题是：B20 的固定优先槽、复制 ABI、复制后重读、发送启动和释放顺序是否成立，以及它怎样与正常命令生产及完成通知相连。独立复核7个函数合同：完整核 `a01951e2/a01915bc/a00ee9ce/a00ee96c`；仅核 `a00a8330` 的正常分派尾、`a00a8582` 的入口/生产点/0x58/0x24分支和 `a0191652` 的入口清状态。已验收解析、缓存、轮询及构帧内部保留合同，不重做整个 dispatcher。

| 原结论或待核命题 | 结果与原指令依据 |
| --- | --- |
| B20 四槽按地址优先，每次最多一个，非 FIFO | 接受。`a01915d0/d6/dc/e2` 依次 lbu 四个占用byte；分支各选首个非零槽。全空到 `162c`；选择后没有继续取槽的循环。 |
| B20 活动忙时不搬运也不清槽 | 接受。`15f8` lbu state，`15fc` 非零到共同返回，绕过 memcpy、启动与 `1628` 清槽。 |
| B20 复制目的/来源/长度 | 接受。`15fe` lbu a2=slot[2]；`1606` a1=slot+1；`160a` a2+=2；`160c` a0=62fcb2f3；`1610/1614` 原编码到 a000589c。占用byte不复制。 |
| B20 保留复制后重读 | 接受。`1618` 再lbu state；`161c` 非零略过写1，但仍到 `1624` 启动调用。不得用复制前的旧state代替。 |
| B20 清槽时点及宽度 | 接受。`1624` 调启动器，正常返回后 `1628` **sb zero,0(s1)**。不是调用前释放，也不检查 callee 返回。command/length/payload残留不清。 |
| B20 启动器仅state1工作，调用后计数写入 | 接受。`ee9e2/e6/e8` 保存state并与1比较；相等依次 `ee9ec` 构帧、`ee9f0` 推进write，再 `ee9f4` sb保存的1至attempts，`ee9f8` sb wait=0。不是调用后重读state再写attempts。 |
| B20 无显式业务成功返回 | 接受。两函数统一恢复栈返回，没有定义成功/失败a0；内部调用可覆盖a0，故不能赋予其业务结果含义。 |
| 槽布局和活动副本独立 | 接受，生产点补证。`195268/5278/5280` 分别写槽occupied/cmd/len；复制目的slot+3。消费器目的为活动区，不保存槽指针。payload[45]是48 B槽布局的容量视图，不是认证的原始C声明。 |
| producer 会在发布 occupied 后填内容 | 接受且补明确次序。`195268` 先sb occupied=1，随后才写cmd/len和条件复制payload。不能把它改写成“最后发布occupied”，也不能据静态顺序宣称并发安全。 |
| 正常响应后固定调用同一个handler | 不接受这种扩大解释，B20未作此主张。`a00a8538`第一次间接调用后，`853a`重新lw槽；第二次目标可变化。第二次前没有新的NULL门。只记录正常目标有效时的顺序，不调查异常。 |
| 正常0x24总会取队列 | 不接受这种扩大解释，B20未作此主张。普通dispatcher `a00a885a..8868` 在OTA阶段byte=1时走a00a56d4；其他值才 `886a` 调消费器，消费器又要求state=0。 |
| 构帧、底层write来源、全部state写者、回调生命周期 | 未核/部分沿用。a01a4ff8保留已有帧合同；a0027e94仅核调用ABI；不认证驱动内部、并发及全部安装/卸载路径。 |

未改 B20 原文件。本报告的补充限制针对端到端解释，不把先前局部结论冒充为全协议验收。

## ABI、布局和资源归属

| 接口/区域 | 本轮可证明的合同 |
| --- | --- |
| a01951e2(a0=descriptor) | descriptor byte0=cmd，byte1=len，word+4=payload指针；+2/+3不被此入口消费。忙时对占用槽逐一比较cmd、len及n=len字节；比较返回0则抑制重复。随后按地址找空槽。没有显式入队成功返回。 |
| 固定槽 | 62fcb354/384/3b4/3e4，步长0x30；occupied@0、cmd@1、len@2、内嵌payload@3。不持有源payload指针。四槽都占用时直接返回，不覆盖旧槽。 |
| 活动区62fcb2f0 | state@0、attempts@1、wait@2、cmd@3、len@4、内嵌payload@5；响应副本cmd@0x32、len@0x33、payload@0x34。均为RAM字节视图，不推定完整类型。 |
| a01915bc()/a00ee9ce() | 无业务输入参数、无已认证业务返回；分别保存并恢复s0/s1/s2和ra。下游a0返回被忽略。 |
| a00ee96c()→a0027e94 | a0=word[62fc91b0]；a1=TX@62fcb48c+cursor；a2=(frame_len-cursor)&255；a0按有符号正返回解释。驱动是否复制/保留缓冲仍未知。 |
| 当前handler槽62fcb6c0 | word函数指针。正常响应调用(a0=cmd byte,a1=len byte,a2=payload或NULL)，随后重读槽调用(0x24,0,NULL)。本轮不认证实际目标恒为普通dispatcher。 |
| 普通dispatcher a00a8582 | 入口分别sb cmd/len至栈view偏移0/1，sw payload至+4，供缓存helper借用。view+2/+3没有入口初始化证据，不能称整个描述符已清零。 |
| a0191652(dest,n,view) | 本轮只核入口保存上下文后 `a0191668` 单byte清state0；缓存比较/复制/派生通知及参数生存期沿用已独立验收B03，不把本次入口切片当完整重验。 |

原payload由提交者借给a01951e2。正常格式len=1..45时，槽或活动区同步复制n=len字节；len0不调用该复制分支。生产器在空闲路径 `a0195302` 也在复制后重读state：仍0才写1；若已非0则保留并调用启动器。忙路径不保存descriptor或payload指针，没有allocator/free调用。因而“原槽释放”只指occupied清零；不能等同释放堆内存或清除数据。

消费器把cmd/len/payload复制到独立活动RAM后，槽在整个发送启动器期间仍占用，启动器返回才可重用。这不是底层发送完成时才释放槽；底层部分write后仍可能state1。活动缓冲、TX缓冲、响应缓冲各有独立地址，本轮没有发现通过保存slot指针维持发送的行为。没有锁、原子发布或完整调度证据，不增加串行化保证。

生产者局部实例如 `a00a8820..8834`：li 0x55后sh至栈描述符，表示小端cmd=0x55、len=0，再sw payload=NULL并把栈地址交a01951e2。此处是正常dispatcher内的一个生产点；该分支的全部到达条件不属本次认证范围。

## 正常状态和完成通知衔接

```c
// 分析伪代码，省略已验收分派与帧算法；不作为原源码。
submit(desc) {
    if (state != 0) {
        if (same_occupied_command(desc)) return;
        slot = first_empty_slot();
        if (!slot) return;
        slot.occupied = 1;        // 原先后顺序
        slot.cmd = desc.cmd; slot.len = desc.len;
        if (normal_nonzero_length(desc.len)) copy(slot.payload, desc.payload, desc.len);
        return;
    }
    active.cmd = desc.cmd; active.len = desc.len;
    if (normal_nonzero_length(desc.len)) {
        copy(active.payload, desc.payload, desc.len);
        if (load_u8(&state) == 0) state = 1;
    } else state = 1;
    start_if_state1();
}
consume_one() {
    slot = first_occupied_by_address();
    if (!slot || state != 0) return;
    copy(&active.cmd, &slot.cmd, (unsigned)slot.len + 2);
    if (load_u8(&state) == 0) state = 1;
    start_if_state1();
    slot.occupied = 0;            // 不根据返回值判断
}
// 已有CRC正确、传输state2且响应cmd匹配的局部路径：
copy_response_into_active_response();
state = 3;
handler = load_word(0x62fcb6c0);
if (handler != NULL) {
    handler(response.cmd, response.len, response.len ? response.payload : NULL);
    handler = load_word(0x62fcb6c0); // 必须重读
    handler(0x24, 0, NULL);        // 原程序没有第二次NULL检查
}
parser_stage = 0;                 // sb，未附加清N/E
start_if_state1();
```

state0→1来自生产器或消费器；启动器只有state1才构帧并推进write。write正返回后，`ee9a0` **重读**cursor，与返回值相加后截为byte；再读frame_len，`ee9b2` 必须**相等**才置state2并以**sh**同时清frame_len/cursor。不能把它扩写为“游标>=帧长”；非正返回不更新游标。该精确条件补明USB概述的“达到帧长”，不改变B20。

正常匹配响应在 `a00a84ee..8502` 检查state2和cmd相等后，`8506..8510`按声明len+2复制响应副本，再 `851a` 写state3。首次handler可以清state、生产下一命令、发派生通知或替换槽；它的返回值不控制第二次通知。以已验收cmd0x58为一个明确连接：dispatcher `8776/877a/877c/8780` 传 `(62fcb504,4,&stack_view)` 到a0191652，helper入口 `1668` 清state0；后续轮询selector及通知副作用仍保留原合同。因此handler返回后的state不必仍3，也不保证0。后来的 `0x24` 消费只尝试当前空闲状态，不负责无条件清state。

普通dispatcher对0x24在OTA阶段byte!=1时调a01915bc，否则交已有OTA启动边界。本报告不展开该边界。parser成功共同尾只清parser stage，再调用a00ee9ce；即使0x24已经启动新命令，第二次启动仍由当前state决定。没有静态证据允许删去任一次调用、合并两次handler或把所有这些步骤折成一个“完成成功”返回。

## 来源、实际验证和断边

本轮 [verify_review.py](../../analysis/queued-command-review-b21-0041-20261023/verify_review.py) 只读主仓库 `roms/0041/ap01-1.0.2_0041.bin`，映射为VA−9ffff000；六函数保留raw_ranges逐段与ROM相等，缓存helper入口另按已有B02字节逐条相等。由半字前缀独立推进普通RV32+C指令长度，再Capstone解码。实际运行 `python -B reverse/analysis/queued-command-review-b21-0041-20261023/verify_review.py` 通过：**7函数合同、329指令、47项精确操作数、15条原编码调用目标、10项独立S型写宽度/寄存器字段、68条控制流目标**。所核窗口无厂商扩展或未知指令。手工核过参数寄存器生存期、分支、后调用写入及所有权转移。

[review-evidence.json](../../analysis/queued-command-review-b21-0041-20261023/review-evidence.json)保存ROM文件偏移/原字节/独立解码/保留provider文本、Evidence ID与原dossier位置。来源是已有USB机器记录和B02入口窗口，历史profile及Evidence身份保持原样，不将新解码贴成新REA Evidence，不重复制作哈希清单。B20两核心原Evidence为ev_ad6980ba30e890b1edbd867ee513c9b556d5bd335ba0e9cb745945b2964585b9与ev_313ec1bbe3f041925d5f81e95f82eac99ccabf8b54ebeebb31fe2ad1b0536a2f，其他精确来源见JSON。

事实是原字节、地址、访问宽度、调用参数及局部控制流；“队列/活动副本/完成通知”等是由它们支持的分析命名。厂商原源码、精确版本、标准库来源、驱动实现及真实底座行为未知。a000589c/a00501be只沿用复制/比较合同并核调用ABI；a01a4ff8仅沿用既有构帧合同。没有新增经来源认证的开源排除项。

已闭合原问题的正常局部链与B20独立复核；不能认证的断边是：handler槽调用瞬间的完整目标集合与安装/销毁生命周期；间接调用改变state/槽的全部路径；底层write借用缓冲的生命周期；初始化/断连对所有活动字段的全局写者。静态通知不是线缆接收、底座接受或业务成功的观察。未执行固件、历史回放或旧采集脚本，未外连、编译项目、进行长度/漏洞审计，未改ROM、生产代码或模型。

建议后继小闭包：针对62fcb6c0的一条普通安装→替换→恢复/卸载路径，核安装参数、宽度、调用者和回调生存期；保留本轮队列合同，不展开完整OTA或异常路径。
