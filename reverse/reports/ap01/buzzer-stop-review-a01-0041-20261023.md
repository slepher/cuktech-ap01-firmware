# A01：蜂鸣 worker 退出生产方及停机断边复核

2026-10-23；分支 `codex/re-0041-a01`，起点 `7c17501`。结论为**部分恢复，待独立技术复核**。本文的 C 为分析命名的语义伪代码，不是原始源码。

本任务回答：已存的退出 post 是否确实属于 worker 退出；创建失败清理能否视为正常停机；能否从已知等待接口定位退出确认消费方。前两项已用 ROM 原字节复核；第三项仍未闭合。**没有恢复正常停机触发者，也没有找到可以证实等待 `62fc92a4` 的调用点**。不得将此结果改写成“ROM 没有消费者”。

只静态读取用户指定的 0041 ROM 与既存证据，未执行固件、连接设备/服务、运行历史异常回放或研究缺陷；未改生产代码、ROM、分析器模型或共享索引。原件身份沿用[第一轮证据](../../analysis/buzzer-backlight-0041-20261023.json)的既存校验信息，本任务不另制哈希清单。适用路径内未发现 AGENTS.md；已读取 reverse-engineer-anything 技能和滚动任务书。

## 范围与证据

仅三个核心入口：worker `a009ef48`、初始化容器 `a005a736` 的蜂鸣相关窗口，以及实际调用的 wait 包装 `a0028b0a`。对其他 wait 调用点仅记录直接参数形状，不恢复整个信号量系统或其他模块。

- [core-windows.json](../../analysis/buzzer-stop-a01-0041-20261023/core-windows.json)：worker 全体、初始化成功/失败窗口、同容器一个栈重载等待候选、wait 包装完整返回窗口。前三段与既存修复模型保存字节及 ROM 逐字节相等；保留原 evidence ID 和来源。
- [direct-call-candidates.json](../../analysis/buzzer-stop-a01-0041-20261023/direct-call-candidates.json)：新做的反向直接调用候选枚举，独立于旧 `LUI 62fc9` 状态前向检索。每项保存位置、编码形式及 128 B 导航窗口。窗口起点不是已认证代码边界，不能直接当 CFG。
- [collect-static.py](../../analysis/buzzer-stop-a01-0041-20261023/collect-static.py)：可重放的宿主静态采集脚本；只用 Capstone 解码，绝不执行 ROM 指令。
- [review-index.json](../../analysis/buzzer-stop-a01-0041-20261023/review-index.json)：实际验证和七个包装调用点的逐项评语。
- 旧直接字段读写边界沿用[第三轮检索及局限](buzzer-backlight-round3-0041-20261023.md)，本任务未重复运行旧扫描或扩大其结论。

## 指令事实：退出通知生产者

`a009ef48(void *unused)` 是初始化注册的线程入口，返回寄存器最终为 0。参数未在本函数使用；线程接口原 typedef 仍未知。

| 位置 | 指令事实 | 可支持的语义 |
| --- | --- | --- |
| `a009ef5e..a009ef7e` | `s1=62fc9288`，读 `s1+0x2c` | 独立 running byte 位于 `62fc92b4` |
| `a009ef82` | running 非零跳 `a009efca`；为零落入退出日志 | 入口/回环均检查 running |
| `a009efca..a009efd2` | `a0=62fc9298`，call `a0028b0a`，随后重新读 running | 等待的是请求信号量；退出决策使用 wait 返回后的新读值 |
| `a009efd6..a009efdc` | wait 返回 0 分支到 `a009f002`；非零且 running=0 回到顶部 | wait 非零并不绕过最终退出通知 |
| `a009f002` | running=0 直接跳 `a009ef84` | 成功 wait 后若关闭标志已清，跳过请求执行 |
| `a009efa6..a009efae` | `a0=62fc92a4`，call `a002747c` | 退出通知 post 的生产者确定 |
| `a009efb2..a009efc8` | 恢复寄存器、`a0=0`、return | post 返回值未成为线程的返回结果 |

与字段结合的最小控制流如下；请求体原有 PWM 设置/延时/清 busy 行为沿用前轮，不另恢复算术。

```c
uintptr_t buzzer_worker(void *unused) {
    for (;;) {
        if (load_u8(0x62fc92b4) == 0) goto exit;
        int r = wait_wrapper((void *)0x62fc9298);
        uint8_t running = load_u8(0x62fc92b4);
        if (r != 0) {
            if (running != 0) log_wait_failure();
            continue;
        }
        if (running == 0) goto exit;
        existing_beep_body(); // 原函数内联体；不是 ROM 的另一个函数调用
    }
exit:
    log_thread_exit();
    post((void *)0x62fc92a4);
    return 0;
}
```

事实：退出尾部没有清 busy、销毁信号量、close PWM、驱动 STOP 或 join。仅置 running=0 对“已经处于 wait”的线程能否唤醒，不由该 worker 证明；需要外部请求 post、其他唤醒或已返回的 wait，当前未找到相应正常停机调用边。对于已进入提示音延时的路径，正常清 duty/清 busy 后才回到顶部读 running；本轮没有恢复异步中止延时的机制。这是分支合同，不是运行观察或缺陷判断。

## 指令事实：创建失败清理不是正常停机

`a005a736` 是大初始化容器，不虚构独立 BuzzerMngDeinit/Init 地址或外层返回值。相关状态槽仍为 `base=62fc9288`、request `+0x10`、exit `+0x1c`、thread token `+0x28`、running `+0x2c`。

1. `a005bd02..a005bd14` 清零该状态的 0x30 B；`a005bd20/24` 初始化 request，`a005bd50/54` 初始化 exit。
2. 第二只初始化失败，`a005bd7a/7c` 只销毁 request，跳 `a005bcb6/ba` close 已打开 PWM，再跳 `a005b100`。
3. `a005bd82..a005bd98` 构造 worker=`a009ef48`、参数=0、token 输出=`62fc92b0`，先在 `a005bd94` 置 running=1，再创建线程。创建返回 0 直接跳 `a005b100`，不走清理。
4. 创建返回非零才进入 `a005bda2..a005bdc8`：日志、running=0、destroy(request)、destroy(exit)、close PWM。第二次 destroy 由 `a005bdc8` 跳回共用调用点 `a005bd7c` 完成。

这里没有 request post 或 exit wait。唯一已证实的显式清 running 发生在创建失败路径；它不能证明已成功创建 worker 的正常关闭流程。底层最后一次 close→shutdown→stop 合同沿用[第二轮](buzzer-backlight-round2-0041-20261023.md)，本任务不将驱动停机当应用线程停机。

## 新核对：wait 包装及反向直接调用

`a0028b0a..a0028b3d` 的序言、两处 return 路径和最后回跳完整可解码；下一个 `a0028b3e` 开始新序言。按原字节新增核对，不依赖反编译文本。

```c
// 参数与返回合同来自寄存器；名称是推断，精确开源版本未认证。
int wait_wrapper(void *sem) {
    if (sem == NULL) return call_a0026844(); // 本任务不展开其合同
    int r = call_a002786c(sem);             // a0028b24，保留原委托
    if (r >= 0) return 0;
    *call_a00267c0() = -r;                  // 与 errno_location 形状一致，命名为推断
    return -1;
}
```

对原 ROM 全部偶偏移，独立提取 `JAL ra`、RV32 `C.JAL` 和连续 `AUIPC/JALR ra`，目标限定为上面 wait/直接委托、已知 post/destroy、worker、thread-create。共 52 个候选：wait 7、委托 21、post 14、destroy 5、thread-create 5；没有直接 call worker 的候选，已知 worker 是 thread-create 的函数参数。所有命中的目标算术均与 Capstone 操作数字段交叉检查。数量是**编码候选数**，不是函数恢复数或已证实调用者总数。

七个 wait 包装调用候选的有界读数：

| 调用地址 | 紧邻参数依据 | 本任务处理 |
| --- | --- | --- |
| `a009efce` | worker 的 `s6+0x298=62fc9298` | 证实为 request wait，不是 exit 消费 |
| `a00b8c36` | 非空入口分支跳到 `a00b8c2e`，保留输入 a0；空分支中间调用未展开 | 保留转发候选，不排除跨函数 alias |
| `a0136208` | `a01361f8..fc` 形成 `62fc5470` | 该局部直接参数不是 `62fc92a4`；不认证整函数 |
| `a01991ca` | `s5=62fc5524`，`a0=s5+4` | 该局部直接参数为 `62fc5528` |
| `a0199234` | `a0=s5`，前段 s5=62fc5524，但路径经过厂商字 `1a8ad98b` 与其他调用 | 未独立认证跨该指令的 s5 值，仅保留候选 |
| `a01b3252` | `a0=load32(input+0x178)` | 内存重载 alias 未知；不能据此排除 exit |
| `a01b7d74` | `a0=load32(input+0x178)` | 同上；两个上下文是否同类型未认证 |

其中固定参数表述只到列示局部路径，不将导航窗口视为全函数支配关系证明。21 个直接委托候选完整保留，绝大多数参数来自对象/保存寄存器，未追全部上游。额外复核同一初始化容器内 `a005c3aa`：其参数从栈 `s0-0x12c` 重载，紧邻相关路径在 `a005c2d0` 得到 `a010e6cc` 的返回对象，`a005c2dc/e0` 将 `object+0x18` 存该槽；`a005c30a` 分支到实际 wait。由此只得到对象成员等待，**没有得到等于蜂鸣 exit 槽的指令证据**。来源函数/完整 CFG 没有在此展开，继续保留 alias 未知，不宣称该调用已经排除。

检索不覆盖非连续 AUIPC/JALR、寄存器间接调用、尾调用、其他等待 API、RAM 代码或任意跨函数/内存别名；偶偏移也可能落到数据或 32 位指令后半段。旧检索的厂商指令截断、状态上限和路径不可行候选限制继续有效。不得叠加两种检索后作全 ROM 不存在证明。

## 来源、恢复程度及验证

worker/初始化业务编排按厂商私有恢复；wait 包装具有 NuttX/POSIX 风格，但没有精确源码/版本及修改范围匹配，**仍记来源未知，不作开源排除**。厂商指令 `th.lrbu` 出现在 worker 提示音体；此处只复用既存已保存解码，本次退出决策和包装窗口均不需给未知厂商指令补义。三个核心入口以外仅做调用点导航。

实际完成：3 段既存原字节与 ROM 一致；wait 包装 52 B 完整解码；52 个直接目标编码算术交叉核对；七个包装调用点参数形状检查；报告本地链接检查；JSON 可解析；`git diff --cached --check` 通过。宿主脚本首轮曾因研究根目录 parents 下标错误找不到既存 JSON，已修正并成功重跑；不涉及目标执行。普通 `git add` 首次因主仓库 `.git/worktrees/re0041-a01/index.lock` 的沙箱写权限被拒绝；根据用户明确提交授权，使用工具升级后暂存成功，没有绕过权限。没有固件执行或整项目编译。

闭合部分：初始化→worker 注册，worker wait/退出判断→exit post，创建失败→running 清零/销毁/close。断边：成功创建后的正常停机入口→running=0；正常停机→唤醒 request；exit post→等待消费者；确认后销毁/close 的应用生命周期。建议下一小任务只追 `a00b8bfc` 转发 wait 的直接调用者与 a0 来源，或单独追一个 `input+0x178` 指针的写入者；不要把全部 21 个内核委托扩成一次任务。
