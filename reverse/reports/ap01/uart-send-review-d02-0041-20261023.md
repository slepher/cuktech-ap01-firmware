# D02：正常UART发送闭包独立技术复核

2026-10-23；基线 `919051d5d8ba930b7e15ca2883bca2c71c692353`，分支 `codex/re-0041-d02`。**限定接受D01新增构帧、部分写和两层write ABI结论；没有发现需要纠正的指令语义。** 接受的是正常提交到匹配响应、普通cmd58归还状态的局部链；驱动和全局生命周期仍部分恢复。D01与B21原文件均未修改。

应用 `reverse-engineer-anything` skill，复用保留证据，独立从主仓库ROM取字节、解码并检查关键编码；未打开共享REA target或可写数据库。没有执行固件、历史回放、外连、项目编译、异常长度或超时研究；没有修改ROM、生产代码或分析器模型。

## 范围与逐项裁定

本轮核10个函数身份：`a01951e2/a01915bc/a00ee9ce/a01a4ff8/a00ee96c/a0027e94/a0025874/a00a8330/a00a8582/a0191652`。其中新增完整核构帧、推进器、两层write；B21已验收提交/槽/启动和解析/普通handler只核本链连接窗口，不重验全dispatcher、CRC算法、缓存或轮询算法。

| D01命题 | 复核裁定、原指令依据 |
| --- | --- |
| 描述符同步转入活动字节副本，启动器只在state1工作 | 接受，与B21一致。`1952cc/52da`字节写cmd/len；`195302`在复制后重读state；`ee9e2..9f8`门控并在两个调用后写保存的1和wait0。槽的布局/发布/去重仍沿用B21，不重复完整证据。 |
| CRC先处理未转义00，再处理cmd/len/payload | 接受。`1a502e`半字写00A5；`5032`以initial0、frame+1、count1调用CRC；`5036/503e/5042/5046`以返回CRC、active+3、初读len+2接着调用同函数。不是对转义后字节计算CRC。 |
| CRC低高字节地址和循环长度有独立len读取 | 接受。低字节使用`5036`的s4；`5056`重读用于高字节地址；`5068`再读后加4、截byte作为循环上限。`5052/5064`均为单byte store，第二次先`5062`右移8。 |
| A5/5A/AA前插AA，原byte不异或 | 接受。`50ba/50be/50c2`三个比较，`50ca`写a7低byte=AA；`50ce`输出索引截byte后`50da`原样写a0。`50b6`是unsigned byte load。 |
| builder只初始化frame_len，不清cursor；完成尾重读frame_len | 接受。`501a` sb至frame+5e=2；完整函数无frame+5f写。循环结束`509c`条件发布索引，`50a0`重读frame_len后加1、sb长度、写5A。`50de..50e2`可先发布索引并直接返回，不保证每次都追加尾。保留原分支形状，不研究触发输入。 |
| 部分write以调用后重读及byte宽推进 | 接受。`ee984`初读cursor，`ee992`count截byte；`ee9a0/9a6`调用后重读cursor/length，`9aa/9ae`截byte并sb cursor。调用前的值不能替代调用后读取。 |
| 正返回且新cursor精确等于重读长度才完成 | 接受。`ee99c`原编码是signed `bge zero,a0`，`ee9b2`是`bne a5,a0`；不是阈值比较。`ee9bc`写state2，`ee9c0` sh zero同时清length/cursor。本地全部写出不等同对端业务成功。 |
| write wrapper保存buf/count，取得对象、调用、归还、返回保存结果 | 接受。`27ea4/7eaa`保存输入；`7eae`调取得；`7eb8/7ebc/7ec0`恢复三个实参；`7ec2`调操作；`7ec6`保存返回；`7ec8/7ecc`归还相同局部对象；`7ee6`返回保存结果。负结果转errno/-1路径存在；不把取得/归还函数内部称作已恢复引用计数或锁。 |
| 操作表write ABI不改变三个输入实参 | 接受。`25874/5876`测试object.flags bit1，`587a→5880→5884`依次取object+0xc、link+0x10、ops+0xc。三个非NULL门后`5890 c.jalr a4`，沿途没有改a0/a1/a2；a0仍object、a1仍buf、a2仍count。返回a0由具体callee给出。 |
| 匹配响应先state3，再两次同步通知；第二次重读handler | 接受，与B21一致。`a84ee..8502`state2/cmd门；`851a`写3；`852e/8538`首次装载/调用；`853a/8546`重新装载/第二调用，无新增NULL门；`8548/854c`仅清parser stage并启动。 |
| cmd58清空闲、可先提交后继，0x24仅尝试消费 | 接受且只限此例。`a8776..8780`传(cache=62fcb504,n=4,&view)；`191668`写state0。`a8786/a8792`共同汇至`a8aae`，独立解原J编码到`a0191746`。后继实际选择沿用轮询合同；`a885a..886a`只有OTA阶段不为1才到槽消费者，后者仍要求state0。 |
| 冷启动cursor、实际驱动、callback寿命、全局销毁均已闭合 | 未核且不能这样扩大。D01已经明确这些断边，本轮保留，不以局部正常循环消除它们。 |

## 可读恢复视图与所有权

名称和伪代码是分析视图，不是原始源码。RV32描述符为`cmd:u8@0,len:u8@1,payload:ptr32@4`，未证明+2/+3初始化。活动静态区`62fcb2f0`的state/attempts/wait/cmd/len/payload分别位于+0/+1/+2/+3/+4/+5；响应cmd/len/payload位于+32/+33/+34。TX为`62fcb48c`，length@+5e、cursor@+5f，均byte；FD槽`62fc91b0`和handler槽`62fcb6c0`均word。

```c
// 已验收CRC接口：crc_step(initial, bytes, n)，算法本轮沿用合同。
build_frame() {
    store_u8(&frame_len, 2);       // cursor没有初始化写
    store_u16(frame, 0x00a5);
    crc = crc_step(0, frame + 1, 1);
    low_n = load_u8(&active.len);
    crc = crc_step(crc, &active.cmd, low_n + 2);
    active.payload[low_n] = (uint8_t)crc;
    high_n = load_u8(&active.len);
    active.payload[high_n + 1] = (uint8_t)(crc >> 8);
    n = (load_u8(&active.len) + 4) & 255;
    i = 0; out = 2; dirty = false;
    while (i < n) {
        b = load_u8((&active.cmd) + i);
        if (b == 0xa5 || b == 0x5a || b == 0xaa) {
            frame[out] = 0xaa;
            out = (out + 1) & 255;
        }
        frame[out] = b;
        next = (out + 1) & 255;
        if (next > 0x5e) { frame_len = next; return; }
        out = next; i++; dirty = true;
    }
    if (dirty) frame_len = out;
    out = load_u8(&frame_len);
    store_u8(&frame_len, out + 1);
    frame[out] = 0x5a;
}
progress() {
    n = load_u8(&frame_len);
    if (n == 0) return;
    c = load_u8(&cursor);
    r = write_wrapper(load32(fd_slot), frame + c, (n - c) & 255);
    if ((int32_t)r <= 0) return;
    next = (r + load_u8(&cursor)) & 255;
    n = load_u8(&frame_len);
    store_u8(&cursor, next);
    if (n == next) { state = 2; store_u16(&frame_len, 0); }
}
```

两层ABI的正常路径为`wrapper(fd,buf,n) → acquire(fd,&local) → dispatch(local,buf,n) → local.ops.write(local,buf,n) → release(local)`。wrapper在release前保存write返回，再把非负返回原样交上层。acquire不成功不进入该归还路径，NULL buffer门和负结果转换保持原分支，不补造业务成功码。dispatch链上没有更换object为link的参数操作；对象链仅用于找函数指针。

state0→1归提交者或槽消费者；1→2归正write且精确等长；2→3归CRC通过并匹配活动cmd的parser；3→0由具体handler负责，cmd58示例通过缓存helper完成。parser统一尾不负责清传输state。普通handler可以在第一次通知内同步提交后继，随后0x24见到的状态不保证空闲；不推断所有命令都响应同样责任。

源descriptor/payload由提交者拥有，同步复制后不保留其指针；固定槽、活动、TX与响应都是不同的静态字节地址。槽occupied在starter返回后清零；不是等整个发送或响应结束。TX全写只清两个进度byte，不擦帧，也不证明底层已放弃buf引用。wrapper的对象归还只在本地取得/调用/归还次序层面成立。两次handler获得静态响应payload借用地址，没有证明它可以跨回调保存。没有allocator/free证据支撑为这些静态区域构造堆生命周期。

## 独立证据、实际验证及限制

[verify_review.py](../../analysis/uart-send-review-d02-0041-20261023/verify_review.py)直接只读原ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，VA映射`offset=VA−9ffff000`；不是调用D01脚本或接受其pass输出。由原半字前缀独立推进2/4byte边界，对普通RV32+C用Capstone解码。新证据[review-evidence.json](../../analysis/uart-send-review-d02-0041-20261023/review-evidence.json)逐条保留地址、文件偏移、原字节和解码；本轮与D01窗口交集逐条raw比较，另新增`a00a8aae..8ab3`共同尾确认selector调用。

实际运行`python -B reverse/analysis/uart-send-review-d02-0041-20261023/verify_review.py`通过：**12窗口、286指令、46精确操作数、16原编码J/B目标、6项原S型写宽/寄存器/位移、6个厂商原字**。signed正返回门、精确相等门、构帧提前返回门另直接检查funct3/源寄存器；核心ABI同时手工追踪寄存器保存和恢复。没有使用固件运行验证这些语义。

六个厂商字分别为`a01a5052:0b55fa00`、`5064:0b55f700`、`50b0:8bd6e700`、`50b6:0bc53581`、`50ca:8bd8e700`、`50da:0bd5e700`（内存字节序）。独立拆出opcode=0x0b、funct3、bits27..31、rd/rs1/rs2、shift=0。五条store模式funct3=5、高位=0；load模式funct3=4、高位=16。保留模型`ap01thead2.sinc:6442/6410`给出的`rs1+(rs2<<shift)`、1byte写/无符号读与这些原字段一致。它是现有本地模型的语义依据，不是新增厂商文档来源认证；未修改模型，也没有让Capstone猜未知指令。

历史来源沿用主仓库`reverse/analysis/usb-interface-ota-0041-20261023.json`与D01列出的dossier；JSON保存原Evidence ID、profile和body定位，不发明新的REA Evidence ID。构帧原`ev_6f837cbc62bd40c5a13276f71d9f1c6343a9399687e53d49e76fbb13bb841b69`，推进器原`ev_2dd7fa785883e602e5643f9c4b2790d32a63979b30fe6664a4ddded5329838a7`；原profile为`b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。两层write入口仍为D01按返回/邻接入口推定的边界，不冒称有历史函数Evidence身份。缓存入口字节来源由D01指向dock保留窗口，实际与ROM相等。

事实是上述原编码、字节访问、局部调用顺序与ABI。prepared/等待响应/对象取得归还等为据此形成的分析命名。CRC、复制/比较、槽、缓存与轮询只保留明确已有合同；本轮没有新增经过来源认证的标准库排除项。厂商原源码、版本和编译配置仍未知。

保留的可定位断边为：`a0025904/a0027e54`内部所有权和实际write安装者；冷启动、断连及其他cursor/state写者；handler槽的替换约束、完整目标集和响应借用寿命；write实际复制/异步借用及可写唤醒；最终销毁/卸载。正常前帧完成的halfword清零不能证明冷启动cursor，wrapper返回不能证明硬件发出或底座接受。未扩大到超时或异常输入。

建议后继仅做一个闭包：从`a0025904(fd,&object)`和`a0027e54(object)`接到具体write安装/调用/归还，恢复正常对象生命周期与buffer消费合同；继续保留本轮队列、CRC、parser和cmd58连接合同，不扩成整个驱动库。
