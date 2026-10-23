# 0041 底座接入判定、五相调度与命令轮询

本轮先核对内嵌 MCU 数据，未得到可靠架构/入口证据，因此保留为不透明载荷；再恢复能从 AP01 指令直接证明的 PogoPin 接入判定、采样调度、轮询表、数据更新和断连清理。这补充了此前以 UART/OTA 为主的局部合同，没有回到缺陷验证方向。

状态：**部分恢复**。所有字段名及伪代码为分析视图，不是原始源码。原厂 0041 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只做静态分析；未运行 AP01 或 MCU 载荷、连接设备/服务、构造异常输入、修改正式 ROM/安全检查；本次 B01 复核仅提交授权的研究文件，未推送。

## 证据入口

- [两份完整观测及复用清理器](../../analysis/dock-presence-polling-0041-20261023/retained-functions.json)：`a00a41f2` ID ADC callback、`a00a805a` timer callback，历史 `whole-rom-private-20261023-037/066.json`；复用已有 `a00a3ab6` 缓存释放。保留来源/模型指纹、汇编、伪代码和原字节。
- [9 个指令窗口](../../analysis/dock-presence-polling-0041-20261023/instruction-windows.json)、[20 ms 注册来源](../../analysis/dock-presence-polling-0041-20261023/timer-registration-source.json)、[轮询初始数据](../../analysis/dock-presence-polling-0041-20261023/poll-initializers.json)、[两条厂商指令模型](../../analysis/dock-presence-polling-0041-20261023/poll-vendor-model.json)。
- [MCU 载荷边界/统计](../../analysis/dock-presence-polling-0041-20261023/mcu-carrier-boundaries.json)、[合同清单](../../analysis/dock-presence-polling-0041-20261023/contracts.json)、[核对记录](../../analysis/dock-presence-polling-0041-20261023/review-index.json)和[只读采集脚本](../../analysis/dock-presence-polling-0041-20261023/collect-evidence.py)。

## MCU 载荷：边界已核，架构仍未知

沿用[UART/OTA 报告](usb-interface-ota-0041-20261023.md)的 18 B 头部与 16 B 项目流消费合同。下表统计的是头部后的完整项目流，不是解出的代码：

| 目标视图 | ROM 头部地址 | 数据区字节数 | Shannon 熵 bit/B | 不同 16 B 块 / 全部块 |
| --- | --- | ---: | ---: | --- |
| 公共 selector1 | `a026adb0` | 49152 | 约 7.996100 | 3072 / 3072 |
| TA1208 selector0 | `a0276dc4` | 42624 | 约 7.995661 | 2664 / 2664 |
| TA1408 selector0 | `a0281458` | 50048 | 约 7.996590 | 3128 / 3128 |

项目流均无重复的 16 B 块，也没有长于等于 12 字节的连续可打印 ASCII 段。头部和主体指纹均已固定，但高熵/块统计不能证明具体压缩、加密算法或架构。本轮没有将它们强行导入 AP01 的 RV32 地址映射，也未开展解密尝试。MCU 入口、原始内存布局和内部程序仍列来源未知/尚未分析；下一步需封装来源或 MCU 侧解析器的证据。

## 20 ms timer 与五相轮转

初始化容器 `a005a736` 的 `a005ab4c..a005ab63` 明确调用 `a008bc64(a00a805a,20,context)` 并将返回 timer 保存到 context `+0`。20 ms 单位沿用已核 LV timer 接口；这里只认证注册与私有 callback，不排除未认证的库修改。

timer callback 从 `timer+0x0c` 取 context，检查 word `context+0x190`：

| 相位 | 行为 |
| ---: | --- |
| 0 | `ioctl(context.fd_at_0x64,0xb01,0)`，日志对应 ID ADC trigger |
| 1 | 同命令触发 `fd@+0xc8`，日志对应温度 ADC |
| 2 | 同命令触发 `fd@+0x12c`，日志对应端口 ADC |
| 3 | 处理 USB interface，并维护内存日志计数 |
| 4 | 不执行上述相位工作 |

末尾统一 `phase++`，大于 4 置 0，触发失败只记录后仍推进。按正常 0..4 循环、忽略调度延迟推导，每种相位约隔 100 ms；不能将注册周期当实测精确定时。

相位3在 ID presence byte `context+0xc5` 非零时检查 USB 阶段 `62fcb50c`：

| 阶段值 | 已核行为 |
| ---: | --- |
| 0 | 清 RX 50 B、TX 96 B、活动区 97 B，设 `b4f8=2`、响应函数 NULL、传输状态0；再走连接子流程 |
| 2 | 走连接子流程，不执行上述整段缓冲区清零 |
| 1 | 调已核发送/重试推进接口 `a00eea08`；若轮询 round_done 非零，清标志、phase byte加1、各组sent清0，选择下一命令 |
| 3 | 只有 interface_index `b51c==0` 时调用发送/重试推进接口 |
| 其他 | 跳过这段 USB 处理和 interface_index 推进 |

连接子流程只有 interface_index=0 时执行：调用 `a00a5558` 复位业务缓存字段、恢复响应函数为 `a00a8582`、清四个待发槽占用 byte，再提交 `{cmd=0xd1,len=0,payload=NULL}`。有效阶段处理后 interface_index 加1，大于10归0，即11个取值；presence 为0时不推进此 index。

相位3还独立维护 context `+0x194` 的计数：值0时记录内存信息，随后加1，大于100归0。这部分不依赖 presence。内存日志并非每个20 ms回调都执行。USB 阶段的全部进入/退出条件和任务关闭仍未闭合，不凭数值补造完整枚举名。

## ID ADC：平均值、迟滞与六次有效确认

`a00a41f2(handle,status,events)` 从 `handle+0` 取 context。status<0只记日志；只有 events bit0 置位才从 `fd@context+0x64` 读最多40 B。

输入记录步长为5 B，程序取每条 `+1` 的32 bit样本累加，首字节在本判定中未消费。成功读非零且字节数为5的倍数时，按 `uint32` 累加；在记录累加后检查阶段3，未跳过时再用 unsigned 整数除法求平均。不改成浮点/有符号平均。样本数最多8是40 B读取上限及此格式的静态推导，ADC的物理单位仍未确认。

字段视图：context `+0xc4` 为确认计数 byte，`+0xc5` 为 presence byte。USB阶段 `b50c==3` 时该判定跳过，计数不清。

```c
// 省略读/日志包装，只展开取得有效记录后的判定。
void judge_id_local(Context *ctx, uint32_t mean) {
    if (u8_at(0x62fcb50c)==3) return;
    bool candidate;
    if (ctx->presence_c5==0)
        candidate = (mean-1500u < 301u);       // 1500..1800
    else
        candidate = (mean-1480u > 340u);       // 离开1480..1820

    if (!candidate) { ctx->counter_c4=0; return; }
    int8_t n = (int8_t)(ctx->counter_c4+1);
    ctx->counter_c4=(uint8_t)n;
    if (n<6) return;
    if (ctx->presence_c5==0) {
        log_id_online();
        store_u16(ctx+0xc4,0x0100); // little-endian：counter0、presence1
    } else {
        log_id_offline();
        store_u16(ctx+0xc4,0);
        ui_deinit_a00a3d22();
        usb_data_cleanup_a00a3ab6();
    }
}
```

在线进入区间比在线保持区间窄，形成数值迟滞。六次是正常计数0..6的有效确认；读失败、空数据、不整条记录、无读事件或阶段3的跳过均不会在本 callback 清计数，所以不宣称“六个连续 timer tick”或固定600 ms。均未构造输入验证这些错误路径。

确认在线在这里仅写 presence，并不直接发 UiIFace online=1；后续基础信息初始化链再创建/通知 UI。确认离线则先经 UiIFace deinit 同步通知0并释放快照，再释放底座缓存，顺序与[主题离线消费者](theme-online-0041-20261023.md)连接起来。

## 静态轮询表与命令选择

启动 `.data` 复制将 ROM `a0004644` 的控制器放到 RAM `62fc4b30`。其8 B视图为 `{groups_ptr@0, unknown04, phase@5, group_count@6, round_done@7}`；初值为 ptr=`62fc4b20`、byte4=10、phase0、count2、done0。byte4 在本轮已核选择/完成逻辑中未消费，不解释为硬上限。

```c
struct PollGroupView {        // 8 B
    uint32_t commands;       // 指向 command byte数组
    uint8_t limit;           // +4
    uint8_t period;          // +5
    uint8_t sent;            // +6
    uint8_t unknown07;
};
```

| 组地址 | 命令 byte数组 | limit | period | 初始sent |
| --- | --- | ---: | ---: | ---: |
| `62fc4b20` | `62fc4b38: 58` | 1 | 1 | 0 |
| `62fc4b28` | `62fc4b3c: 50 51 57 59` | 4 | 10 | 0 |

`a0191746()` 按固定组顺序检查 `phase % period == 0 && sent < limit`。相位不匹配的组将 sent 写为 limit；相位匹配但 sent>=limit 的组跳过而不重写 sent。首个满足的组取 `commands[sent]`，提交长度0、payload=NULL的命令，再将sent加1并返回1；无可选项返回0。不是每次调用同时发五个命令，也没有原子成功回执：发送队列入口本身无明确入队成功返回，sent仍按原逻辑推进。

两个厂商字由既有哈希绑定模型确认：`a0191786` 为 `th.addsl s1,a1,a5,3` 选8 B组，`a01917a6` 为 `th.lrbu a5,a5,a3,0` 取命令 byte；后者不是发送 commands 指针的低字节。原模型摘录和指纹已保存，未修改解码器。

round_done 被 timer 消费时 phase 是 byte自增，没有按10归零。慢组的准确条件始终是 `phase%10==0`，计数回绕边界按原字节行为保留。完整基础信息分支还会写 phase=1等状态，所有写入者未全部认证。

## 响应缓存、派生事件与状态发布

`a0191652(destination,n,response_view)` 先清传输状态 `62fcb2f0=0`，检查是否还有满足相位/计数条件的组；没有时置 round_done=1，有时保留原值。它随后比较 destination 与 `response_view.payload@+4` 的 n B；不同才复制相同 n B，并在活跃响应函数 `62fcb6c0` 非空时同步调用：

```c
active_handler((response_view.command + 0x20) & 255, 0, NULL);
```

response_view 的最小布局由普通响应入口 `a00a8582` 栈存储确认：command byte@0、length byte@1、payload指针@4。这里 n 来自私有调用者预期字段大小，不以“比较相等/完成回调”猜造设备业务成功；完整派生事件消费者仍未知。本轮仅恢复正常数据更新，未展开长度异常验证。

`a0191700()` 遍历 `62fcb524` 订阅表，调用 `callback(userdata,62fc4b1c)`。它传固定的全局状态视图指针，没有本地复制/分配；该视图三字节字段的全部生产者和ADC语义尚未恢复，不能将其与总快照混作同一通知对象。

## 缓存复位与释放边界

`a00a5558` 清端口数 `b01c`、两个半字缓存 `b51e/b516`、期望模式 `b01d`、`b414`、`aef0`，经 `a00a5506(0)` 更新内部状态 `b508`；设自定义模式缓存 `b518=3`，将 `b2dc` 起7 B填 `ff`。这与总快照销毁不是同一职责。

复用的 `a00a3ab6` 依次对非空 `b2d0/b2d4/b6c4` 调释放接口并清指针；端口数 b01c 仅在 b2d0 非空的分支内清零，最后清 aef0、b51d、b50c。未添加额外清理、线程退出或恢复行为。ID断连链由此得到局部所有权合同；底层设备fd/poll/timer的完整销毁和蜂鸣线程停机仍未知。

本轮新增开源认证排除0。三份 MCU 载荷仍未恢复内部程序；库函数形状也不等于准确来源/版本已认证。全部非开源逻辑目标继续保持未完成。


## B01 独立静态复核（2026-10-23）

验收结论：**原范围接受，修正一处选择器叙述；模块仍为部分恢复**。完整逐项结论及保留未知见 `review-index.json`。复核使用保留证据及主仓库原 ROM 的只读字节，未打开/修改 REA 共享会话或数据库。

修正的指令事实：`a0191796` 的相位余数非零分支到 `a0191766`，写 `sent=limit`；`a019179c` 的 `sent>=limit` 分支到 `a019176a`，直接推进组索引。因此原先“未满足的组均写 limit”范围过宽：相位匹配但已耗尽的组不重写 sent。报告、合同和既有采集脚本的描述已同步修正，未改变原程序。默认有效表及正常 sent 取值下通常观察不到差别，但不能据此替换指令行为。

| 核心入口 | 本地参数/返回合同与直接调用关系 | 验收 |
| --- | --- | --- |
| `a00a41f2` | `handle,status,events`；无业务返回值；`*(handle+0)` 为 context，离线依次调用 `a00a3d22`、`a00a3ab6` | 接受本地平均、迟滞与确认；不重新认证完整 UI deinit |
| `a00a805a` | timer 指针；无业务返回值；取 `timer+0x0c`，驱动 ioctl、`a00eea08`、`a0191746` | 接受五相、USB 局部分支和计数；timer 销毁仍未闭合 |
| `a0191746` | 无显式输入；返回0无可选命令、返回1已调用 `a01951e2`；返回1不证明队列成功 | 选择器叙述已修正 |
| `a0191652` | `destination,n,response_view`；未认证业务返回；比较/复制后可间接调用活跃 handler | 接受本地合同，间接目标所有写入者/消费者未知 |
| `a0191700` | 无显式输入；未认证业务返回；遍历订阅项并间接调用 `callback(userdata,62fc4b1c)` | 接受固定全局视图指针，不补造完整状态语义 |

厂商指令额外核对：除了两条既有轮询模型摘录，复核将原始 word 的 rd/rs1/rs2、位域和已有模型定义对照，确认 `a00a42d0/a00a4372` 为 `th.ext a5,a5,7,0`（8 bit 符号扩展）、`a00a4338` 为 `th.mula a0,a1,a6`（5 B 步长）、`a00a8090/a00a82b4` 为条件清零 `th.mvnez`、`a00a830a` 为8 B组步长 `th.addsl`。摘录与地址在核对记录中，不修改分析器模型。普通反汇编显示 `.unknown32` 的位置不能单靠普通解码器判义。

事实、推断与引用边界：参数20、字段偏移、条件分支、字节自增和静态表字节均为本轮核对的指令/数据事实；毫秒单位沿用此前 LV timer 接口识别，本轮未独立认证其完整来源、版本或时基实现。约100 ms轮转为正常0..4相位与该接口单位下的推导，非运行测量。`a00a85a0/a00a85a4/a00a85a8` 的原始栈存储另核对 command@0、length@1、payload@4；UI离线同步通知、发送重试接口职责沿用所链接的既有研究，本轮未复核全部内部函数。新增开源排除仍为0，未知来源的回调/适配逻辑继续保留。

实际验证：运行同目录 `review-evidence.py <主仓库绝对路径>`，通过6个既有来源指纹、3个保留原始范围、9个指令窗口、573条普通指令解码、8个厂商word位域、4处初始化数据映射、3份不透明载荷已有统计及11条报告链接检查；未另制哈希清单或复制基线。脚本只写本目录的核对记录，未执行固件；`git diff --check` 通过。现有采集脚本仅修正合同文字，未重跑全套采集。

剩余未知保持：ADC物理单位与配置、USB阶段完整写入者、轮询控制器其他写入者及byte4意义、完整派生事件消费者、fd/poll/timer销毁及MCU内部程序。后续建议只追 `62fc4b35` 在 timer 以外的一个直接写入者及其 phase 赋值合同，不扩展为整个USB状态机。
