# 0041 蜂鸣器与背光：停机边界、通道及间接入口

新增续作见[第三轮：退出检索复核与 MiIO 间接入口](buzzer-backlight-round3-0041-20261023.md)；历史未知项以各轮边界分别保留。

沿用[第一轮报告](buzzer-backlight-0041-20261023.md)的原厂 0041 身份与证据分级。原件 SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。本轮只做静态分析，新增内容只写研究目录，未执行固件、访问设备或外部服务、进行缺陷验证、修改正式 ROM 或提交/推送。

主要新增结果：固定的蜂鸣/背光 PWM 通道与引脚、24 B 参数接口、最后一次 close 的驱动 shutdown 路径，以及设置页定时器间接入口。**蜂鸣线程的正常停机调用者和退出确认等待方仍未找到**；这是有界检索结果，不能据此补造 deinit 或断言整个 ROM 不存在消费者。模块仍为部分恢复。

## 证据入口与模型限制

本轮材料位于 `reverse/analysis/buzzer-backlight-round2-20261023/`：

- [mapping-and-boundaries.json](../../analysis/buzzer-backlight-round2-20261023/mapping-and-boundaries.json)：通道表、操作表、初始化数据及重定位事实，包含原字节/哈希和 67 项旧模型输入指纹。
- [capstone-windows.json](../../analysis/buzzer-backlight-round2-20261023/capstone-windows.json)：7 个明确限定的指令窗口，逐条保留原字节；未知厂商指令不跳过、不改写。
- [rea-followup.evidence.json](../../analysis/buzzer-backlight-round2-20261023/rea-followup.evidence.json)：本轮通用 RV32 REA 会话的完整 25 条观测，包含函数、引用和模型局限。25 是观测条数，不是已恢复函数数。
- [bounded-state-search.json](../../analysis/buzzer-backlight-round2-20261023/bounded-state-search.json)、[literal-pointer-search.json](../../analysis/buzzer-backlight-round2-20261023/literal-pointer-search.json)：状态及常量指针的有界检索，不能当全程序别名分析。
- [diagnostics.json](../../analysis/buzzer-backlight-round2-20261023/diagnostics.json)：私有会话故障与访问限制记录，失败产物保留。

以下“指令事实”指 ROM 字节、指令及常量表；“推断”指给数据/职责起名及关联；未知项单列。通用 Ghidra 把 `a0136762` 合入 `a0136700`、把 `a0136a5e` 合入 `a0136998`，并在厂商指令处截断。本文使用操作表中的精确入口、独立函数序言和返回指令限定人工窗口，**不认证错误合并的函数 body，也不把伪代码截断当原程序行为**。

## PWM 通道、引脚及数据布局

指令事实：启动初始化 `a0029d2e..a0029d46` 及循环 `a0029e40..a0029e48` 将 `a00027d4..a0005123` 复制到 `62fc2cc0..62fc560f`。循环的两个厂商字 `5847460b`、`5847d60b` 按既有已核验模型分别解释为 `th.lwia a2,a4,4,0` 和 `th.swia a2,a5,4,0`，执行读/写后各将地址加 4；本轮没有更改解码器。

据此，ROM `a0003ac0` 的下层对象初始化到 RAM `62fc3fac`；其 `+8` 指向 `62fc3f9c` 的两项通道表。ROM 通道初值位于 `a0003ab0..a0003abf`。

| 下层槽 | 通道表地址 | 通道号 | GPIO | 初始 duty | start 从配置块读取 | 业务职责 |
| --- | --- | ---: | ---: | ---: | --- | --- |
| 0 | `62fc3f9c` | 2 | 18 | `0x8000` | `+4`，写通道项 `+4` | 蜂鸣器 |
| 1 | `62fc3fa4` | 3 | 31 | `0x8000` | `+12`，写通道项 `+12` | LCD 背光 |

通道号/GPIO/初值是原始数据事实。业务职责是将下层固定槽顺序与第一轮上层 duty 写入交叉关联后的推断。这里确认的是 ROM 配置，不是实测引脚电平或板外接线。

`a0136700` 的 setup 依次读取两项 `pin`（`+1`、`+9`），以 `a002573e(pin,0x1d10)` 配置 GPIO。没有由未赋值的配置块通道标识决定引脚的证据：start 在 `a01367b2..a01367bc` 明确只取两个 duty 写入这两项固定配置。

```c
// 分析视图；原始 typedef 和未消费字段名称未知。
struct PwmChannelView {       // 每项 8 B
    uint8_t channel;           // 2 / 3
    uint8_t pin;               // 18 / 31
    uint8_t unknown02[2];
    uint32_t duty;
};
struct PwmInfoView {          // 上层确切复制 0x18 B
    uint32_t frequency;       // +0
    uint32_t buzzer_duty;     // +4
    uint8_t unconsumed08[4];
    uint32_t backlight_duty;  // +12
    uint8_t unconsumed16[8];
};
```

`unconsumed` 仅指本轮所审阅下层 start 未读取这些字节；上层仍完整复制 24 B，不能据此改变原参数块、补零或证明整个驱动不会消费它们。下层对象 `+0xc` 为缓存周期半字、`+0x10` 为缓存频率，shutdown 会清零它们；对象 `+4` 的 `0x41` 暂保留原值，不虚构字段意义。

硬件注册表：启动入口设 `gp=62fc34c0`，`a0025e1e` 从 `gp-0x2d0` 遍历 40 个、每项 16 B 的设备描述符。`pwm_v2_0` 对应 ROM `a0002d74` / RAM `62fc3260`，MMIO 基址 `0x2000a400`。板级 `a0056212..a0056228` 查找它并保存到 `62fc8f70`。该基址也与仓库 `reverse/sdk/sdk-bl616_memorymap.h` 相符；不能把 SDK 头文件一致当整段驱动来源/版本认证。

## 驱动间接调用与停机路径

ROM 文件操作表位于 `a01c1460`：open=`a012fc20`，close=`a012fcae`，ioctl（表 `+0x14`）=`a012fd1e`。板级代码 `a005622c..a0056264` 分配 0x30 B 上层对象，在 `+0x2c` 保存下层 `62fc3fac`，并用该文件操作表注册 `/dev/pwm0`。

下层操作表位于 `a01c1488`：

| 偏移 | 职责 | 精确入口 | 人工审阅范围 |
| --- | --- | --- | --- |
| `+0` | setup | `a0136700` | `a0136700..a0136761` |
| `+4` | shutdown | `a0136a5e` | `a0136a5e..a0136b3f` |
| `+8` | start / 应用配置 | `a0136762` | `a0136762..a0136997`，厂商算术未全部恢复 |
| `+12` | stop | `a0136998` | `a0136998..a0136a5d` |
| `+16` | 额外 ioctl | `a0135216` | 仅恢复表项，未展开 |

上层结构观察：`+0` 为打开引用计数 byte，`+1` 为 started byte，`+4` 为锁，`+0x14` 为 24 B 配置副本，`+0x2c` 为下层对象指针。上层 ioctl 有锁；这不证明应用请求槽或全部跨函数事务原子化。

```c
// a012fd1e；省略仅用于断言的参数前置分支，保留正常业务及返回语义。
int pwm_ioctl_local(Upper *u, int cmd, void *arg) {
    int ret = lock(u->lock);
    if (ret < 0) return ret;
    switch (cmd) {
    case 0xc01:  // SET
        memcpy(u->info, arg, 24);
        if (u->started) ret = lower->ops->start(lower, u->info);
        break;
    case 0xc02:  // GET
        memcpy(arg, u->info, 24);
        break;
    case 0xc03:  // START
        if (!u->started) {
            ret = lower->ops->start(lower, u->info);
            if (ret == 0) u->started = 1;
        }
        break;
    case 0xc04:  // STOP
        if (u->started) {
            ret = lower->ops->stop(lower);
            u->started = 0;
        }
        break;
    default: ret = lower->ops->ioctl(lower, cmd, arg); break;
    }
    unlock(u->lock);
    return ret;
}
```

这也解释第一轮“蜂鸣停止”的实际效果：初始化已 START，因此线程后来 SET duty=0 会再次进入下层 start 应用配置；后续 START 命令在 started 已为 1 时不重复启动。背光 setter 的 GET→只改第二路 duty→SET 路径会保留其余已缓存配置。GET 与 SET 是两个分别加锁的调用，不额外推断跨调用事务。

最后一次 close 的确定路径是：`a012fcae` 加锁，若引用计数大于 1 就减 1；否则将引用计数置 0，间接调用 `lower.ops[1] = a0136a5e`，解锁并返回 0。该 close 窗口没有清上层 started byte，也没有访问蜂鸣 worker 或退出信号量。

下层 stop `a0136998` 清 MMIO `base+0x44` 中通道 2、3 的 enable 位（位号 `channel*4`，即 8、12），在 `base+0x40` 置位 bit27，随后按 bit29 和计时差轮询后返回 0。时间函数为 RAM `62fc18c6`，比较阈值 100；其时间单位本轮未认证。

shutdown 先调用 stop，再次请求/等待停止条件。条件满足时对 `base+0x40/44/48/4c/50/54/58/5c/64/68/6c` 写入固定复位值；等待提前结束的分支跳过寄存器复位。两路缓存 duty、周期和频率最终都会清零，并返回 0。未擅自将所有分支都写成“复位成功”，也未修改返回行为。

## 蜂鸣线程停机与退出确认：已查到的边界

指令事实：worker `a009efae` 向 `62fc92a4` 调 `a002747c`（sem_post）。初始化创建 request_sem=`62fc9298`、exited_sem=`62fc92a4`；创建线程失败时清 running，销毁两只信号量，再 close PWM。第一轮报告已保存这些原始指令。

本轮进行了两种额外检索：

1. 扫描整个 6769704 B ROM 的字节常量指针，未找到上述状态地址、worker 或公开蜂鸣/背光入口的原样指针字节；PWM 操作表则有命中。**这不覆盖指令拼接出的地址。**
2. 在所有偶地址找 `LUI 0x62fc9`，共 455 个种子；向后最多 512 B 做标准 RV32C 常量传播、遇未知指令停止、调用丢弃 caller-saved 常量，得到 18 个候选事件，再回看相关原指令。退出信号量命中初始化与 worker post；running 的写命中创建前置 1 与创建失败清 0，没有得到正常停机的清零/唤醒/等待链。

此算法不追内存重载指针、长距离别名或间接写入，线性窗口也不等于完整 CFG；保留全部限制。没有证据支持把 `exited_sem` 命名为“已恢复的 join 协议”。当前区分为：**硬件 stop/shutdown 已恢复局部合同；线程退出通知生产者已恢复；通知消费方与正常应用停机入口仍未知**。不能把注册在文件操作表里的 shutdown 当作应用已调用它的证明。

## 背光 UI 与线程间接入口

已核入口：

- worker 注册：`a005bd82..a005bd98` 将 `a009ef48` 作为 `pthread_create` 第三个参数，thread token 输出到 `62fc92b0`。这条入口由原始寄存器赋值确认，不依赖反编译调用者列表能否识别。
- 唤醒包装 `a00a769a`：`62fc4039==0` 时取期望亮度 `62fc909c` 调背光 setter，置屏幕状态 1，返回 1；状态 2 时进入关屏保/返回正常页流程，也返回 1；其他状态返回 0。这不是蜂鸣线程停机。
- 亮度业务 setter `a00ab4d8(value)`：值改变时更新 `62fc909c`，调用背光 setter(value)，再尝试写 `ck_config/lcd_backlight`、发类型 5 工作请求并更新显示。第二次配置写属于原调用行为，不删掉或合并。
- 设置页 `a00f5eb6(ctx,mode,value)`：有效值 1..100 更新 UI 与 `ctx+0x8c` 的待提交亮度。若 `ctx+0x84` 没有 timer，创建 `a008bc64(a00f43d4,2000,ctx)`，记创建 tick 到 `ctx+0x88`，调用 `a008c280(timer,1)` 设置 repeat_count=1。已有 timer 时不重启它，因此是从首次创建计时的延后提交，不能改写成每次操作都重置的 debounce。
- timer 回调 `a00f43d4(timer)`：从 `timer+0xc` 取 ctx，从 `ctx+0x8c` 取 byte，调用背光 setter，随后构造 2000 ms 的 UI 动画。ctx 缺失只记录日志。其后动画/UI 所有权未全部恢复。
- `mode==0` 的设置页分支：若 timer 非空且当前 tick 减创建 tick 小于 2000，调用 timer 删除接口 `a008ae58`；随后清 ctx 的 timer 槽，再处理动画及 UI。条件和顺序按原分支记录，没有补造无条件取消。

`a008c280` 的 ROM 日志名明确为 `lv_timer_set_repeat_count`，正常分支将计数写入 timer `+0x10`；只核其与私有回调的接口，不把 LVGL 算法作为新增私有恢复工作。上述入口不等于全部设置页和动画回调生命周期闭包。

## 工具故障与未决项

新私有客户端在研究目录启动并完成 67 项模型指纹核验、原件导入和既有修复脚本，但没有返回函数查询。一次读取临时 `session.json` 得到 `PermissionError: [Errno 13] Permission denied`；另一次 CIM 进程查询返回无法访问资源。未再读取受限文件、调整 ACL、提权或关闭沙箱；中断了本轮命令单元，保留日志。没有把修复脚本完成说成采集完成，也没有自动重启或重复失败请求。可用的连接式 REA 通用会话已正常关闭。

仍缺：线程正常停机的实际触发者/消费者；全部间接入口与 UI 动画销毁闭包；PWM 分频、阈值计算中的厂商算术；轮询计时单位；上游准确版本与厂商改动。新增 GPIO/通道结论只到静态配置层。本轮在这些有界结果后，已转入[天气调度局部恢复](weather-scheduling-0041-20261023.md)，不将本模块虚标为完成。

最终[核对记录](../../analysis/buzzer-backlight-round2-20261023/review-index.json)：原件 SHA256、67 项模型输入、12 个原字节窗口/表、25 条 REA 观测的目标身份、两份天气来源/范围及报告链接均通过；通道表、重定位、设备注册及操作表已交叉核对，`git diff --check` 通过。未执行异常输入回放或固件运行验证。
