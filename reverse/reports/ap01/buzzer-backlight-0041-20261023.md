# 0041 蜂鸣器与背光私有逻辑恢复

新增续作见[第三轮：退出检索复核与 MiIO 间接入口](buzzer-backlight-round3-0041-20261023.md)；历史未知项以各轮边界分别保留。

本轮目标为正常业务逻辑恢复。只读静态分析原厂 0041，未运行 ROM、连接设备或服务、构造异常输入、修改生产代码或提交。本文是分析者命名的语义伪代码，不是原始源码，也不承诺可直接编译。

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射基址 `0x9ffff000`。本模块状态：**部分恢复**。

后续进展见[第二轮：停机边界、PWM 通道及间接入口](buzzer-backlight-round2-0041-20261023.md)。现已确认配置块为 24 B，蜂鸣为 PWM2/GPIO18、背光为 PWM3/GPIO31，并补齐驱动最后一次 close→shutdown→stop 与设置页 timer 入口；下面保留第一轮当时的未知项，正常线程停机与退出确认消费方仍未找到。

## 进度与选择依据

历史已有 MiIO/MiBLE 局部合同、17 类 UI 的 SIM 重建、Wi-Fi 菜单/配置、UART/底座 OTA 及显示链路局部恢复；不等于完整模块认证。主要缺口为工厂测试、天气、设置/设备业务、私有无线/驱动适配、启动胶水、内嵌 MCU 固件及大量来源未知函数。全局 6487 节点是第一轮模型的枚举下界，不是实际函数总数。

本轮选择原先只有路径归属、尚无独立实现合同的 `PogoPinMng/BuzzerMng.c`。指令及字符串证实它还管理 LCD 背光，不能按文件名将背光排除。普通请求、工厂长鸣、工作线程、PWM 配置和持久化接口已形成局部数据流。

## 证据与解释规则

[机器证据](../../analysis/buzzer-backlight-0041-20261023.json)收录 8 份函数观测、原始范围字节/哈希、汇编、反编译、调用关系、来源文件哈希和完整亮度表；[新增 getter 观测](../../analysis/buzzer-getter-0041-20261023.json)保留本轮 REA 原始返回。历史完整材料位于 `evidence/rea-0041-20261017/`，不要求读者只凭本文相信结论。

| 标识 | 地址 / 范围 | 来源与用途 |
| --- | --- | --- |
| B1 | `a009ef48..a009f177` | `whole-rom-private-20261023-016.json`，`ev_0c01da465fa5fff0361a0c64bac4bbe6e6b50aaa6e6177dd46d1dd29e0bbd680`；工作线程 |
| B2 | `a01b29ec..a01b2b5b` | `...-158.json`，`ev_b2c26252f85f2f1e0cf0fd91f7405af20de7e7bf20f97ec7f0520e2eff627248`；背光 setter |
| B3 | `a01b7de0..a01b7ee3` | `...-160.json`，`ev_b3f15f179e267548bb9b4141ab9aa49fa110ba06ac8aa160f4aec4b959cbeb0f`；普通蜂鸣 |
| B4 | `a005a736` 中 `a005afac..a005b0fe`、`a005bc6c..a005bdc8` | round3 bundle，`ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`；内联初始化及清理 |
| B5 | `a00a8582` 中 `a00a90fc..a00a91a6`，busy 前置分支见完整函数 | round3 bundle，`ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`；内联工厂长鸣 |
| B6 | `a009d8bc` 中 `a009dc02..a009dc2c` | `...-015.json`；MiIot 蜂鸣开关 setter，完整 evidence id 见机器证据 |
| B7 | `a00a76e2..a00a7727` | `...-063.json`；UI 关屏调用背光 setter(0) |
| B8 | `a009d7a0..a009d7b3` | 新增 `ev_9010d7718b807a6dd6a2eb58615c7cc215c5b6d35f1f531bdfd0862d29d88421`；读 `62fc916e` |

B1/B2 的反编译带有“移除不可达块”警告，但对应 `divu` 指令仍在汇编中；本文按汇编保留除法，未据此删除分支。B4/B5 使用第三轮修复模型，B1/B2/B3/B6/B7 复用第一轮修复模型，B8 使用本轮通用 RV32 模型，只认证其简单字节读取。各 profile 分别保存，不合并统计全 ROM 完成率；大函数仅核本文相关窗口，其余代码仍未认证。

## 数据布局

以下偏移由 load/store 和初始化范围确认；字段名及结构体分组为推断。对象为全局静态存储，没有本模块堆分配证据。`sem_t` 内部结构未在本轮恢复，只保留实际槽位。

```c
// 位于 0x62fc9288，初始化清零 0x30 字节。
struct BeepStateView {
    uint8_t busy;             // +0x00：请求提交至完成期间占用
    uint8_t unknown01[3];
    uint32_t frequency_hz;     // +0x04
    uint32_t duration_ms;      // +0x08
    uint8_t duty_percent;      // +0x0c
    uint8_t unknown0d[3];
    uint8_t request_sem[12];   // +0x10，0x62fc9298
    uint8_t exited_sem[12];    // +0x1c，0x62fc92a4
    uint32_t thread_token;     // +0x28，pthread_create 输出槽
    uint8_t running;          // +0x2c
    uint8_t unknown2d[3];
};

// 位于 0x62fc94d8；保留观察视图，不声称原始 typedef。
struct PwmStateView {
    uint8_t configured;       // +0x00：一次性默认字段设置标志
    uint8_t unknown01[3];
    uint32_t device_path;     // +0x04："/dev/pwm0" 指针
    int32_t fd;               // +0x08
    uint8_t unknown0c;
    uint8_t brightness;       // +0x0d：0..100 的请求值
    uint8_t unknown0e[2];
    uint32_t frequency_hz;    // +0x10：默认 4000
    uint32_t default_duty;    // +0x14：初始化写 50；本轮未发现后续消费
};
// 0x62fc916e：独立 uint8_t buzzer_beep_enabled。
```

PWM ioctl 参数块中，已确认 `+0` 是频率、`+4` 是蜂鸣 duty、`+12` 是背光 duty。这三个语义有初始化、线程、setter 的相互印证。**参数块其余字节、完整长度、通道描述符及引脚映射未知**；线程/初始化没有为所有中间字节赋值，伪代码不能擅自将整块清零。

## 亮度映射与背光设置

指令事实：表起点 `a01c447c`，ROM offset `0x1c547c`，正常索引 0..100 共 101 B。映射为 ROM 常量，不能用线性百分比替代。

| 输入 | 表值 | PWM duty 整数 |
| ---: | ---: | ---: |
| 0 | 0 | 0 |
| 1 | 1 | 257 |
| 25 | 22 | 5654 |
| 50 | 65 | 16705 |
| 75 | 124 | 31868 |
| 100 | 255 | 65536 |

```c
uint32_t brightness_duty(uint8_t level) {
    uint32_t mapped = ROM_u8[0xa01c447c + level];
    return mapped == 0 ? 0 : (mapped << 16) / 255;
}

// B2，void 语义；失败仅记录日志，没有向调用者提供状态结果。
void backlight_set_duty_cycle(uint32_t level) {
    if (level > 100) { log_invalid(); return; }
    if (pwm.fd < 0) { log_not_initialized(); return; }
    uint32_t duty = brightness_duty(level);
    pwm.brightness = (uint8_t)level;  // 在 GET/SET 成功之前写入
    OpaquePwmBlock cfg;              // 大小/其余字段见限制
    if (ioctl(pwm.fd, 0xc02, &cfg) < 0) { log_get_failure(); return; }
    store_u32(cfg, 12, duty);        // 保留 GET 返回的其余字段
    if (ioctl(pwm.fd, 0xc01, &cfg) < 0) { log_set_failure(); return; }
    uint8_t level_low_byte = (uint8_t)level;
    if (config_write("ck_config", "lcd_backlight", &level_low_byte, 1) < 1)
        log_persist_failure();      // 不回滚 RAM 或已提交 PWM
    log_applied();
}
```

`0xc01/0xc02/0xc03` 分别具有 SETCHARACTERISTICS / GETCHARACTERISTICS / START 语义，结合 ROM 日志和实际调用顺序命名；本文未将整个驱动认证为未修改开源实现。setter 不重新 START，也不 STOP。B7 的关屏直接调用 setter(0)，随后清 `62fc4039`；因此这条路径会尝试持久化 0。

## 请求、线程与状态机

```c
// B3：无参数，void。普通请求检查独立的用户开关。
void BuzzerMngBeep(void) {
    if (get_enabled_u8() == 0) return;
    if (beep.busy) { log_already_in_progress(); return; }
    if (pwm.fd < 0) { log_not_initialized(); return; }
    if (!beep.running) { log_worker_not_running(); return; }
    beep.frequency_hz = 4000;
    beep.duration_ms = 200;
    beep.duty_percent = 50;
    beep.busy = 1;
    if (sem_post(beep.request_sem) != 0) {
        log_post_failure(); beep.busy = 0; return;
    }
    log_command_sent();
}

// B5 内联块：前置 busy、fd、running 检查后写同一请求槽。
// 与普通蜂鸣不同，此局部块未调用 get_enabled_u8()。
void FactoryTest10Sec_local_block(void) {
    if (beep.busy || pwm.fd < 0 || !beep.running) { log_reason(); return; }
    beep.frequency_hz = 4000;
    beep.duration_ms = 10000;
    beep.duty_percent = 50;
    beep.busy = 1;
    if (sem_post(beep.request_sem) != 0) { log_post_failure(); beep.busy = 0; }
}

// B1：pthread 入口；实际局部变量/参数块布局按汇编恢复。
uintptr_t buzzer_control_thread(void *unused) {
    while (beep.running) {
        if (sem_wait(beep.request_sem) != 0) {
            if (beep.running) log_wait_failure();
            continue;
        }
        if (!beep.running) break;
        if (pwm.fd < 0) { log_not_initialized(); beep.busy = 0; continue; }
        OpaquePwmBlock cfg;  // 未知字节保持未知，不能替换成零初始化
        store_u32(cfg, 0, beep.frequency_hz);
        store_u32(cfg, 4, (((uint32_t)beep.duty_percent << 16) - 1u) / 100u);
        store_u32(cfg, 12, brightness_duty(pwm.brightness));
        if (ioctl(pwm.fd, 0xc01, &cfg) < 0) {
            log_set_failure(); beep.busy = 0; continue;
        }
        if (ioctl(pwm.fd, 0xc03, 0) < 0) {
            log_start_failure(); beep.busy = 0; continue;
        }
        delay_us(beep.duration_ms * 1000);  // a01b4ff4，单位由日志和转换推断
        store_u32(cfg, 4, 0);
        store_u32(cfg, 12, brightness_duty(pwm.brightness)); // 睡眠后重新读
        if (ioctl(pwm.fd, 0xc01, &cfg) < 0) log_silence_failure();
        beep.busy = 0; log_beep_stopped();
    }
    log_thread_exit();
    sem_post(beep.exited_sem);
    return 0;
}
```

正常 duty=50 时计算结果为 **32767**，不是 32768；保留原指令的减 1 和整数截断。提示音结束只把蜂鸣 duty 清零，未调用 PWM STOP，背光继续保留。失败清 busy 的顺序及不回滚行为也按原实现记录。

状态流为 `running=1,busy=0 → 写参数并置busy → post → wait唤醒 → SET/START → 延时 → 蜂鸣duty清零 → busy=0`。只有一个共享请求槽，没有已观察到的提示音队列；busy 时新请求直接返回。退出行为仅确认线程检测 running 并向 exited_sem 发信号，未恢复谁清 running、唤醒及等待确认。不能由两只信号量推断完整 join/deinit 已恢复；也没有足够证据宣称请求提交是原子的。

## 初始化、失败清理与持久化接口

B4 是大函数内联片段，不虚构独立 `BuzzerMngInit` 函数入口或返回值。ROM 日志保留这个职责名称。

1. 以 1 B 读取 `ck_config/lcd_backlight`，预设及读取失败均使用 100；读到 0 也改用 100。仅当 `configured==0` 时，将该值写入 brightness，并设置 frequency=4000、default_duty=50、configured=1、path=`/dev/pwm0`。
2. 在栈参数块写频率、蜂鸣 duty=0、映射后的背光 duty；`open(path,1)` 输出存 fd，再 SET(`0xc01`)、START(`0xc03`)。open 失败记录并继续外层初始化；SET/START 失败会 close(fd)，本窗口没有将 fd 重置为 -1。
3. 成功 START 后清零 BeepStateView 的 0x30 B，分别对 request_sem、exited_sem 调用 `a01a8d2e(sem,0)`，然后 running=1，`a0052fee(&thread_token,0,buzzer_control_thread,0)` 创建线程。调用形状和日志支持 POSIX 信号量/线程语义，`a01a8d2e` 的双参数封装内部 ABI 尚未展开。
4. 第一只信号量初始化失败直接走 close；第二只失败先销毁 request_sem 再 close；创建线程失败清 running，按指令顺序销毁 request_sem、exited_sem，再 close。创建成功跳回外层初始化，不关闭 fd。不额外添加 STOP、默认恢复或错误传播。

MiIot 配置接口：B4 较早片段读取 1 B `ck_config/buzzer_beep_enabled`，返回值必须等于 1；否则将 `62fc916e=1` 并尝试回写。B6 中 `siid=3, piid=9` 将输入按有符号 `value>0` 归一成字节布尔值，写 RAM、写同一键，再调用 `a01950e4(3,9,value,0)` 通知；该局部分支没有按持久化返回值回滚。B8 getter 无参数，返回这个字节。其余属性分支及通知层内部语义不属于本轮认证。

B3 的静态直接调用者包括 `a00a0bd8` 和 `a00a2578`；后者成功处理至少一项属性设置后尝试提示音。B2 的直接调用者包括 `a00a769a`、`a00a76e2`、`a00ab4d8`、`a00f43d4`，本轮只恢复 B7 的关屏合同，其他调用者仅保留关系，不推测完整 UI 状态机。

## 开源边界、验证与剩余未知

本轮确认的是厂商业务编排、ROM 常量表和配置语义，没有新增“已验证且无厂商修改”的开源函数排除。NuttX/POSIX 的 ioctl、线程、信号量形状可识别，但精确版本和适配差异仍待按本地源码/指令匹配；不能把 SIM 使用的 NuttX 12.10.0 当原厂版本。LVGL/libuv 路径只说明来源候选，这里的回调、封装和业务逻辑仍在私有恢复范围。

验证仅包含原件 SHA256、已保留证据来源 SHA256、函数范围字节指纹、亮度表字节及正常域算术交叉核对；未把宿主算术当原厂执行。本轮没有安全限制拒绝；通用模型对厂商指令解释不足是工具模型局限，沿用已存修复模型观察，没有改模型或补 NOP。

本轮实际核对通过：8 份来源文件指纹、8 段函数原字节/哈希、101 项表字节、6 个正常亮度值算术和 50% 蜂鸣 duty 算术；新增报告链接有效，`git diff --check` 通过。REA 本轮打开的临时会话已正常关闭；未运行历史异常输入回放脚本。

剩余未知：完整停机/退出确认消费方、重复初始化的调用约束、所有 UI/间接入口、配置存储内部合同、PWM 参数块未赋值字节与驱动消费范围、实际通道/引脚、线程调度/调用串行化、精确开源版本和厂商修改。本模块仍为部分恢复；后续应优先从这些功能闭包扩展，再推进其他未恢复模块。
