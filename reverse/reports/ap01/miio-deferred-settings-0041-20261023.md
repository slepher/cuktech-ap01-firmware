# 0041 MiIO 延后设置：七种任务、位置数据与天气重排

后续已补[快照与订阅生命周期](uiiface-lifecycle-0041-20261023.md)和[两个 UI 消费者/模式显示名称](ui-total-consumers-0041-20261023.md)；本文保留当时的已核范围和未知项。

新增功能续作见[模式、自定义功率与 UI/UART 控制合同](mode-control-0041-20261023.md)；本文保留历史已核范围，后续不沿缺陷验证方向扩展。

数字地区码函数续作见[B14只读校验合同](numeric-location-setter-b14-0041-20261023.md)及[B15独立复核](numeric-location-review-b15-0041-20261023.md)：`a009c5fc` 是区域码有效性判定器（validator），不是位置 setter；下文仅据此更正该函数术语，保留原调用条件和配置调用顺序。

本轮在[蜂鸣/背光第三轮](buzzer-backlight-round3-0041-20261023.md)的 kind=0 合同基础上，展开 `PogoPinMng/MiIotMng.c` 中共享 timer 的全部任务分支与当前已定位的提交者。已恢复的局部职责还包括蜂鸣/背光、天气请求/UI 数据流、工厂门控/灯效；全局主要缺口仍有设备协议、UI/任务销毁、私有无线适配、内嵌 MCU 和来源未知代码。本轮选择此模块，因为它能把已经分散恢复的亮度、位置与天气调度连接起来。

状态为**部分恢复**。本文是分析命名的伪代码，不是原始源码。只做静态分析，未运行固件、访问实机/服务、验证缺陷、修改安全检查或正式 ROM、提交或推送。原件 SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。

## 证据范围与数据对象

- [保留函数观测](../../analysis/miio-deferred-settings-0041-20261023/retained-functions.json)：`a009d286`、`a009d8bc`、`a00a0bd8`、`a00a0e78`，复用修复模型，分别来自历史 `whole-rom-private-20261023-010/015/019/020.json`，保留来源 SHA256、profile、完整 dossier 和范围原字节。属性处理器仅核本文相关分支，其余分支未认证。
- [指令窗口](../../analysis/miio-deferred-settings-0041-20261023/instruction-windows.json)：完整 callback `a00a0bd8..a00a0e77`、scheduler、模式下游入口、天气重排桥，以及 timer 控制接口的限定前缀。callback 的证据 id 为 `ev_37aab69cd986e090eca0c8ab82e3cd2b78d6ce5806a641413fc3aa8453bb1e19`。
- [直接提交扫描](../../analysis/miio-deferred-settings-0041-20261023/direct-submission-scan.json)、[合同清单](../../analysis/miio-deferred-settings-0041-20261023/contracts.json)、[核对记录](../../analysis/miio-deferred-settings-0041-20261023/review-index.json)。[采集脚本](../../analysis/miio-deferred-settings-0041-20261023/collect-evidence.py)仅读取既存材料及原件字节。

字段名称为推断，地址/访问宽度为指令事实：

| 地址 | 局部职责 |
| --- | --- |
| `62fc9428` | 共享 timer；首个 word 为 callback 读取的 data 指针 |
| 分配的 8 B 请求 | `+0` kind byte、`+1..3` 未观察赋值、`+4` value word |
| `62fcaf00/40/80` | 各 64 B 的待处理位置 ID、城市、区县文本槽；字符串 setter 最多复制 63 并写末字节 NUL |
| `62fcafc0` | 数字位置值 word |
| `62fcafc8` | 期望亮度 byte |
| `62fcaff2` | 待处理模式 byte；产品层准确名称待核 |
| `62fcb02c` | 两位汇合标志 byte，kind=2 OR 1，kind=5 OR 2；不等同于线程退出同步 |
| `62fc90a0/62fc9120/62fc9160` | 既有位置文本、天气 city 文本、数字位置门控，见[位置合同](weather-location-request-0041-20261023.md) |

请求的 `value` 字段在 callback 入口被读取并记录日志；**全部 0..6 业务分支都从全局状态取业务数据，没有再次读取 `req+4`**。不能将它改写成每个请求携带独立业务快照。

## 提交者与调用顺序

完整 ROM 偶地址扫描标准 JAL 和相邻 AUIPC/JALR 的目标地址，得到 3 个直接提交点，均与保留模型的引用吻合。扫描不覆盖间接调用、非相邻地址构造或 RAM 中入口，故不是全调用者证明。

| 提交点 | 触发及提交参数 | 提交后原行为 |
| --- | --- | --- |
| `a009dacc` | 整数属性 `3/1`：保存输入低字节到 `afc8`，提交 `(0,value)` | 以当时 PWM 亮度 `94e5` 通知 `3/1`，并非等待异步应用后的值 |
| `a009de26` | 整数属性 `4/1`：保存输入低字节到 `aff2`；完整 32 bit 输入满足 `value-1 < 4` 的 unsigned 比较才提交 `(1,value-1)` | 以 `value!=0` 通知 `4/1`；不把通知值改成模式号 |
| `a00a0f32` | 字符串属性 `3/5`：复制到 `af00`，容量参数 63，`af3f=0`，提交 `(3,1)` | 用原输入指针及 strlen(input) 调字符串通知，再返回 0；不等待位置任务或天气请求完成 |

`3/6` 城市、`3/7` 区县字符串 setter 分别复制到 `af40/af80`、写末字节 NUL，然后**直接**用原输入和 strlen(input) 写 `ck_config/loc_city`、`loc_district`，最后发字符串通知。当前分支没有提交 kind=4/5。持久化和通知长度取原输入，而非复制后全局槽的长度。不要因为 callback 中有同名任务就替换实际直接调用路径。

整数属性 `3/8` 将输入与 `62fc9160` 的 word 比较，不同时先写 `afc0`，再调用只读区域码校验器 `a009c5fc`，仅返回非0时调用 `loc_id` 配置写接口；配置调用不等于已认证实际落盘成功。它不是本轮找到的 kind=2 提交点；相关完整属性函数仍仅部分恢复。kind=2/4/5/6 有真实分支，但当前已定位提交者集合未覆盖它们，不宣称不可达或删除代码。

scheduler `a009d286` 分配 8 B，将 kind/value 写入并覆盖 timer.data，以 delay=0、repeat=0 注册 `a00a0bd8`。分配失败直接返回；start 返回非 0 时记录并 free 请求，已核窗口未清 data。成功时请求借给 callback，callback 的所有分支最终到 `a00a0cce..a00a0cd4` free 并清 data。该结构是一个共享 timer/data 槽，没有恢复出链式或环形任务队列；ROM 日志 `work_queue_submit` 不能代替数据结构证据。重复提交、外部串行化与完整销毁仍未知，未进一步做异常验证。

## 七种任务的功能语义

```c
// 分析视图；省略日志内容，但保留业务条件与先后顺序。
void miio_handle_timer_cb_local(Timer *timer) {
    Request *req = timer->data;
    log_kind_value(req->kind, req->value);
    switch (req->kind) {
    case 0:
        brightness_business_set(u8_at(0x62fcafc8));
        BuzzerMngBeep(); // 仍受用户开关、busy、fd、running 条件控制
        break;
    case 1: {
        uint8_t mode = (uint8_t)(u8_at(0x62fcaff2) - 1);
        if (mode <= 3) mode_apply_a019537a(mode);
        break;
    }
    case 2:
        config_write("ck_config", "loc_id", ptr(0x62fcafc0), 4);
        flags_b02c |= 1;
        if (flags_b02c == 3) {
            weather_restart_bridge();
            flags_b02c = 0;
        }
        break;
    case 3:
        if (strlen(text_af00) == 9 && text_af00[0] == '1') {
            if (strcmp(text_af00, text_90a0) == 0) log_unchanged();
            else {
                location_set_a00a0ac2(text_af00);
                weather_restart_bridge();
                log_location_task();
            }
        }
        break;
    case 4:
        config_write("ck_config", "loc_city", text_af40, strlen(text_af40));
        break;
    case 5:
        config_write("ck_config", "loc_district", text_af80, strlen(text_af80));
        flags_b02c |= 2;
        if (compare_bytes_a00501be(text_af80, ptr(0x62fc9120), strlen(text_af80)) != 0) {
            if (area_code_valid_a009c5fc(word_afc0) != 0 && flags_b02c == 3) {
                weather_restart_bridge();
                flags_b02c = 0;
            }
            log_restart_weather();
        }
        break;
    case 6:
        weather_restart_bridge();
        break;
    default:
        log_default_kind();
        break;
    }
    free(req);
    timer->data = NULL;
}
```

关键证据：kind=1 的 `a00a0cf4..a00a0d02` 明确 load a0、减 1、AND 255、检查 `3 < a0`，然后带 a0 调 `a019537a`；旧反编译输出无参 `FUN_ram_a019537a()` 遗漏此参数，不能直接采用。kind=2 的 OR/等于 3/清零在 `a00a0d2e..a00a0d42`；kind=5 相应路径在 `a00a0e1c..a00a0e58`。

这里有几项须按原义保留：

- kind=3 只在本分支检查长度 9 和首字节 `'1'`，再与缓存比较；不补造更严格的内容检查。setter 的实际复制参数/持久化分支沿用已有位置报告；callback 不检查其状态结果就安排天气重排。
- kind=5 比较长度为新文本的 strlen，不包含 NUL，不是完整字符串相等判断；比较目标确实是 `62fc9120`，此前天气 URL 合同将它识别为 city 文本。不能为了字段名一致改成另一地址或“旧区县”。
- kind=2 达到 flags==3 就重排；kind=5 还需要字节比较非 0、数字地区码校验器返回非 0。两条路径不对称，不能简化为“两项更新齐全便必定刷新”。只有触发重排的内层分支清 flags，普通未触发路径保留已有位。
- kind=5 的“Restart weather service”日志在字节比较非 0 分支末尾，即使内层条件未满足也会输出；日志本身不证明当次实际重排。

## 模式下游与天气重排桥

`a019537a(mode)` 完整入口窗口显示：将 mode 低字节存 `62fcb512` 和 `62fcb01d`，调用 `a0195166`；随后用保存的原始参数与 3 比较。mode==3 时构造 4 B 临时块：`[3, u8(b000), u8(b001), u8(b002)]`，交 `a019530a`；其他值构造含半字 `0x0160` 和指向 `62fcb01d` 指针的临时描述符，交 `a01951e2`。尚未展开这些发送辅助的完整协议/同步合同，不将临时块当已认证线上帧。模式的产品名、枚举意义和端口字段含义待下游证据确认。

`a00a5b90` 是无参、46 B 的桥：先调 `a01b2b5c(&timer_62fc9520)`，再调 `a01b24c0(1,2000)`。前者已核前缀检查 timer `+0x2c` 的 bit2，并在活动分支清此位；结合调用上下文推断为停止/移出活动 timer 的控制接口，但完整内部 heap/库版本未认证，不写成对象 close/free。后者已有[天气调度合同](weather-scheduling-0041-20261023.md)：参数 1 绕过最近请求检查，以 2000 ms 安排单次 callback。故此处“重启天气”表示重新排定约 2 秒后的请求，不是同步发请求、重建 TLS 对象或立即请求成功；本桥没有显式重置历史成功时间及重试间隔。

## 剩余未知

本轮完成了已核 callback 全部分支的局部合同、三个直接提交点、请求取得/释放、字符串位置提交与城市/区县直接持久化路径、两位汇合条件及天气重排桥。仍缺所有间接提交者、timer 完整生命周期/重复提交约束、kind=2/4/5/6 实际触发入口、模式下发完整协议及参数含义、配置层内部行为、全部属性和通知消费者。蜂鸣正常停机与退出确认等待方仍未定位。

本轮没有新增“已认证未修改开源实现”排除。libuv/POSIX 形状和 memcmp/strlen 类行为只是接口/算法识别，准确版本、来源及厂商修改仍须核对；私有编排及回调继续在恢复范围内。全 ROM 私有恢复目标未完成，不使用此次局部合同更新历史总函数分母。
