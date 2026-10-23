# 0041 蜂鸣与背光：退出检索复核及 MiIO 间接入口

后续补充：[MiIO timer 全部任务分支、位置提交者与天气重排桥](miio-deferred-settings-0041-20261023.md)；本文保留当时已核范围。

本轮沿用 `reverse-engineer-anything` 的证据分级，以原厂 ROM 原字节和既存修复模型为准。仅静态分析，未执行固件、缺陷验证、访问实机或外部服务、修改正式 ROM、提交或推送。ROM SHA256 为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。

已恢复的局部职责包括普通蜂鸣提交/worker、背光映射及持久化、驱动停机与设置页 timer。全局仍缺设备业务、无线私有封装、UI/任务销毁闭包、内嵌 MCU 和大量来源未知函数。本轮先复核用户指定的四个蜂鸣/背光缺口，再推进[工厂测试模块](factory-test-0041-20261023.md)；两者均保持“部分恢复”。

## 停机、退出确认与 PWM 映射

[第二轮报告](buzzer-backlight-round2-0041-20261023.md)已经用初始化数据重定位、通道表和上层 duty 写入确认：蜂鸣为 PWM2/GPIO18，背光为 PWM3/GPIO31；这是静态配置，未认证板外接线或实测波形。配置复制长度为 24 B，`+4`/`+12` 分别是两路 duty。此次没有改变这一结论。

驱动链仍是：最后一次 close `a012fcae` → 下层操作表 `+4` → shutdown `a0136a5e` → stop `a0136998`。STOP ioctl `0xc04` 经上层操作表 `+12` 调 stop。worker 的一次提示音完成仅 SET 蜂鸣 duty=0，保持背光；它不调用驱动 STOP。**硬件停机链不能替代应用线程停机链。**

此次补齐操作表 `a01c1488+16` 的额外 ioctl 入口 `a0135216..a0135223`。完整 14 B 只有栈帧建立/恢复、`li a0,-25` 和返回：

```c
// 分析命名；未认证该驱动的准确开源来源、版本或修改范围。
int pwm_extra_ioctl(Lower *unused_lower, int unused_cmd, uintptr_t unused_arg) {
    return -25;
}
```

因此，在已核上层 switch 中未匹配的命令走该默认返回；这个入口没有额外关闭通道、清 running、唤醒 worker 或等待退出的行为。参数个数由调用接口推断，原始 typedef 未恢复。入口原字节见[新增指令窗口](../../analysis/buzzer-backlight-round3-20261023/instruction-windows.json)。

退出确认仍只找到生产方：worker 检测 `running=0` 后向 `62fc92a4` post。创建失败分支清 running、销毁信号量及 close，不是已创建线程的正常退出协议。

此次新增[分支跟随候选检索](../../analysis/buzzer-backlight-round3-20261023/cfg-state-candidates.json)，并保留[检索程序](../../analysis/buzzer-backlight-round3-20261023/scan-state-cfg.py)。与旧 512 B 线性扫描不同，本次从全部 455 个 `LUI 0x62fc9` 种子分别跟随直接分支，范围为种子前后各 4096 B、每种子最多 10000 个状态；调用丢弃 caller-saved 常量，未知指令终止该路径。得到 63 个候选事件，**不是 63 个已证实引用**。其中：

- `a000c2fc/a000c30a` 的候选来自数组遍历。原指令将 s2 限定为 `62fc87b4` 至 `62fc88f4` 之前、步长 20 B，`a0024906` 是清零调用；无视循环条件才产生与蜂鸣槽重叠的候选。
- `a009c6b0` 的候选来自两槽循环：s5 从 `62fc91a0` 开始，每次加 4，s2=0/1 控制结束；不能将不受条件约束的地址增长当蜂鸣状态访问。
- `a00598b0` 是 `a002db16` 字符串比较调用，参数随表项前移；表项数量的完整约束未在本轮恢复。这不是 sem_wait/退出确认消费的证据。
- 其余命中回到已知初始化、失败清理、worker、普通/工厂蜂鸣提交，或下述 MiIO 亮度接口。running 的显式清零仍落在创建失败分支；退出信号量仍未命中等待消费方。

方法不追踪内存重载指针、栈别名、跨函数别名或动态写入；27 个种子到达状态数量上限，未知/厂商指令也截断路径，详细计数保留在 JSON。故本次仍不能宣称 ROM 没有 deinit，也不能恢复一个没有证据的 join 实现。下一步需靠跨函数/内存别名证据继续补这一缺口，而非重复同一有界扫描。

## 新增 MiIO → timer → 亮度/蜂鸣入口

指令事实：初始化容器 `a005a736` 的 `a005ac04..a005ac38` 用外层 loop 初始化 RAM `62fc9428` 的 timer，失败仅记录日志。MiIO 设置属性函数 `a009d8bc` 的 `siid=3, piid=1` 分支先将输入低字节存入 `62fcafc8`，调用 `a009d286(0,value)`，随后用当时的 `62fc94e5`（PWM 亮度 byte）做属性通知 `a0195144(3,1,current_brightness,0)`。因此这里的通知值不能直接改写成输入值或“异步提交已成功”。分支选择及原始完整来源见[第一轮机器证据](../../analysis/buzzer-backlight-0041-20261023.json)中的 `a009d8bc`。

```c
// 8 B 分配由 a009d294..a009d29a 确认；padding 未观察到赋值。
struct MiioDeferredRequestView {
    uint8_t kind;        // +0
    uint8_t unknown[3];
    uint32_t value;      // +4；不是所有 kind 都消费此字段
};

// a009d286..a009d303；返回寄存器没有统一业务状态合同，暂不写 bool。
void schedule_local(uint32_t kind, uint32_t value) {
    Request *req = alloc(8);                 // a002fcc8
    if (req == NULL) return;
    req->kind = (uint8_t)kind;
    req->value = value;
    timer_at_62fc9428.data = req;
    int r = timer_start(&timer_at_62fc9428, callback_a00a0bd8, 0, 0);
    if (r != 0) {
        log_start_failure(r);
        free(req);                          // a002e14e
    }
}

// 只展开 kind=0 和共同清理；其他 kind 属于后续设备业务模块。
void callback_kind0_local(Timer *timer) {
    Request *req = timer->data;              // callback a00a0bf0
    log_kind_and_value(req->kind, req->value);
    // 原 callback 另有 kind=1..6 分支，此处不是完整函数替代实现。
    if (req->kind == 0) {
        log_desired_brightness(global_u8_62fcafc8);
        brightness_business_set(global_u8_62fcafc8); // a00ab4d8
        BuzzerMngBeep();                     // a01b7de0，仍检查用户开关等
    }
    free(req);
    timer->data = NULL;
}
```

timer_start 的调用为 `a009d146`，RV32 的 delay/repeat 两个 64 位值均为 0，callback 地址由 `LUI a1,a00a1` 加 `-0x428` 构成，而非 ROM 中的字面指针；这是原样指针检索无法覆盖的间接入口。回调 kind=0 在 `a00a0cc2` 调 `a00ab4d8`，在 `a00a0cc6..a00a0cca` 通过 AUIPC/JALR 调 `a01b7de0`，`a00a0cce..a00a0cd4` 释放请求并清 timer data。

分析推断：这是将 MiIO 设置移交到事件循环的业务编排。kind=0 实际从全局 `62fcafc8` 取值，而不是 `req+4`；后者只在此分支的入口日志中读取。应保留这一数据源区别。`a00ab4d8` 后续的 PWM/配置/UI 工作合同沿用第二轮，不将所有 UI 工作都当此 timer 同步完成。成功提交后请求由 callback 释放；启动失败只观察到 free，未观察到紧随其后的 data 清零。未进一步开展异常路径验证。

剩余未知：该共享 timer 的所有提交者、重复提交所有权及调用串行化、全部 kind 分支、timer 销毁闭包、正常蜂鸣停机触发者与退出确认消费方、PWM 厂商算术和计时单位、准确上游来源/修改范围。本轮新增开源排除为 0。原字节、旧证据指纹及链接核对见[核对记录](../../analysis/buzzer-backlight-round3-20261023/review-index.json)。
