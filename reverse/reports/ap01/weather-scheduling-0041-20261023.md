# 0041 WeatherApi：启动节流与后续调度

后续补充：[MiIO timer 全部任务分支、位置提交者与天气重排桥](miio-deferred-settings-0041-20261023.md)；本文保留当时已核范围。

继蜂鸣器/背光续作后，本轮选择下一个尚无独立功能报告的私有模块 `PogoPinMng/WeatherApi.c`，先恢复定时调度合同。静态复用原厂指令及已有修复模型证据，未访问天气服务、发送请求、执行固件或修改安全检查。状态：**部分恢复**；本文不是原始源码。

后续已补[请求、TLS 适配、156 B 天气对象和 UI 发布](weather-dataflow-0041-20261023.md)。下面保留本轮调度分析时的范围；请求对象/解析数据/订阅分发已有新增局部合同，完整库来源和销毁闭包仍未认证。

[机器证据](../../analysis/weather-scheduling-0041-20261023.json)保存 2 份函数观测、模型/来源指纹、原始字节和汇编。原件 SHA256 与[全 ROM 目标](whole-rom-0041.md)一致。入口 `a01b24c0` 使用第三轮 `ev_7fbfe06c4fd42cba1566477dac4d2768c174d596b4c44e0a51849df76a980564`，回调 `a00aab1c` 复用 `whole-rom-private-20261023-070.json` 的观测，**只审阅调度尾部及其分支条件，未认证整段请求/TLS/解析实现**。

## 数据与职责

| 地址 | 指令事实 / 分析命名 |
| --- | --- |
| `62fc9520` | 天气 timer 对象，start 调用的第一个参数 |
| `62fcb418..41f` | 64 bit 上次请求返回 0 的时间；不能一概命名“HTTP 成功时间” |
| `62fc4aec` | 下次失败使用的重试间隔，初值 30000 ms |
| `62fcaee8..eef` | callback 末尾计算的 `当前时间+本次delay`；本轮未展开其读者 |
| `62fcb020` | 请求过程状态字，每次开始时清零；字段全集待恢复 |
| `62fcb024` / `62fcb028` | 请求失败计数 / HTTP 200 分支计数；不代替 timer 重试条件 |
| `62fcae90` | 请求返回非负后记录的 HTTP status |

30000 的初值来自 ROM `a0004600`（file offset `0x5600`），按启动 `.data` 复制关系对应 `62fc4aec`。时间 helper 为 `a00a9d1e`，单位 ms 由调用换算及日志支持；时钟源/校时行为仍未核实。

## 可读调度伪代码

```c
// a01b24c0，void。第一个参数是是否绕过“最近请求”检查，
// 不直接意味着马上发请求，实际仍使用所选 delay。
void start_weather_service(int bypass_recent_check, int32_t requested_delay_ms) {
    uint64_t now = clock_ms();
    int32_t delay = requested_delay_ms;
    if (bypass_recent_check == 0 && last_zero_return_ms != 0) {
        uint64_t elapsed = now - last_zero_return_ms; // 按 64 bit 原指令相减
        if ((elapsed >> 32) == 0 && (uint32_t)elapsed < 3600000)
            delay = 3600000 - (uint32_t)elapsed;
        else
            delay = 2000;
    }
    if (timer_start(&weather_timer, weather_callback,
                    sign_extend_64(delay), 0 /* repeat */) != 0)
        log_start_failed();
}

// a00aab1c 的调度尾部；不是从 ROM 分离出的独立 fetch 函数。
void weather_callback_schedule_tail(Timer *timer, AttemptResult attempt) {
    uint32_t delay;
    if (attempt.reached_request_result && attempt.request_return == 0) {
        last_zero_return_ms = clock_ms();
        retry_ms = 30000;
        // 原指令使用 signed rem，不擅自改成 unsigned rem。
        delay = (int32_t)interval_generator() % 3600001 + 3600000;
    } else {
        delay = retry_ms;            // 本轮等待用旧值
        uint32_t next = (uint32_t)((float)retry_ms + (float)retry_ms);
        retry_ms = next > 7200000 ? 7200000 : next;
    }
    next_deadline_ms = clock_ms() + (uint64_t)delay;
    timer_start(timer, weather_callback, (uint64_t)delay, 0);
    // 此末尾调用的返回值在本窗口未检查。
}
```

`AttemptResult` 是分析用分支摘要，不声称存在这个原始结构体；它区分分配/URL/TLS 初始化等早退与实际请求返回。后续需继续恢复请求和解析对象的真实布局。

指令核对：`a01b24ee` 的 SUB64 和后续高低字比较支持上述最近一小时检查；`a00ab186` 明确以请求返回寄存器 `s4 != 0` 进入失败间隔，`a00ab19a..a00ab1a4` 在返回 0 时恢复 30000。`a00aabc4..a00aabe4` 明确通过 `fcvt.s.wu → fadd.s → fcvt.wu.s(rtz)` 加倍并封顶，不能照搬旧反编译中的浮点符号转换伪影。

## 正常业务含义与边界

- 无最近记录或显式绕过检查时保留调用者给的延迟；有记录且不足一小时时等满余下时间，超过该范围时改为 2000 ms。
- 初始连续失败的等待依次为 30、60、120、240、480、960、1920、3840、7200 秒，其后保持 7200 秒。本次使用旧间隔，再更新下一次间隔。
- 请求返回 0 后清重试间隔，并按上述 signed rem 公式选常规刷新延迟。**只有在 interval_generator 返回非负整数的条件下**，范围才是 3600000..7200000 ms（1..2 小时）；生成器的范围本轮未认证。
- HTTP status 非 200 时会记录状态和失败计数，但之后仍按请求函数返回值是否等于 0 来选择调度。不能把调度条件擅自改成 status==200。
- timer 使用 repeat=0，callback 末尾重新注册；这是逐次安排的调度，不是固定周期定时器。完整 timer 所有权/停止入口仍待追。

本轮未新增开源实现排除。libuv 形状的 timer 接口只作为边界，厂商节流、重试、状态记录与回调继续在私有范围。TLS 组件、签名参数、JSON/天气数据布局、资源所有权及 UI 数据发布将在后续分开恢复；不调整认证或校验。

本轮核对通过两份来源文件指纹、函数原字节/范围哈希和 30000 ms 初始化数据；详见[同轮核对记录](../../analysis/buzzer-backlight-round2-20261023/review-index.json)。没有将静态算术或日志含义冒称原件执行结果。
