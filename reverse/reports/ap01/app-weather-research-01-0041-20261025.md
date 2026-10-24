# Q-10：天气绑定配置启动加载与首次位置选择（0041）

状态：启动位置缓存阶段部分恢复，待非作者复核。本文是静态行为合同，不是原始源码或实机结果。认领 Q-10；作者 app_weather_research_01。基线 `816b09d0035f0931e9b1266575179e4030512760`，独占分支 `codex/app-weather-research-01-20261025`。

## 范围与继承

主树当前 `reverse-design.md` 3.1/3.2/5.1/7 与管理表 Q-10 只读适用。本轮差集仅 `0xa005a736` 内的天气启动读入窗口 `0xa005b8a4..0xa005b9ae`（末地址不含）及真实绑定门前驱；有限追加三个寄存器基址定义，共核 358 B。没有重新导出整个 initializer，没有打开/切换共享 REA。

继承 [天气位置与请求](weather-location-request-0041-20261023.md) 的 getter / URL 合同，以及 [deferred settings](miio-deferred-settings-0041-20261023.md) 与后续 B14/B15 已验运行 setter/刷新接线。本轮不重做 setter、天气 H 页生命周期、I05 的其他配置槽或 Q09 的其他 N。配置后端、formatter、MD5、TLS 均止于 API 边界；未执行固件、构建、模型、SIM、QEMU、回放、设备或外网，也未读取实际用户位置/账号配置。

原件沿既有身份：`roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，文件 offset = VA − `0x9ffff000`。

## 证据与复验

- 主树绝对留存 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/analysis/buzzer-backlight-0041-20261023.json#/functions/6`，真实 body、assembly/pseudocode/raw_ranges；Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。没有以 extent 代替 body。
- [verify.py](../../analysis/app-weather-research-01-0041-20261025/verify.py) 只读复验原件身份、选定原字与留存一致、7 个 JAL 目标、2 个分支、默认常数、存储字及 6 个 ROM 键；输出 [evidence.json](../../analysis/app-weather-research-01-0041-20261025/evidence.json) 是本地 ignored 导出，需主窗转存。
- getter 继承 Evidence `ev_1fec2a04b869df31515a29b8ef1a531ed5b05dfc1f3fb10b10b53537c058dbf2`；URL 继承 Evidence `ev_c8cd305edf249153fdd712550910d2a60b3450092ab9dd7bbdca0aa4df2bca1b`，均来自主树 `reverse/analysis/weather-location-request-0041-20261023/retained-functions.json`。本轮只读必要条件窗口，不计新增 body。

## 启动输入、门与 RAM 映射

`0xa005ac8c` 建立 `s10=0x62fc9000`；`0xa005ad02` 建立 `s4=s10+0xa0=0x62fc90a0`；`0xa005acde` 的 `s5=0xa01c3000`，因此 `s5+0x68` 为 ROM `ck_config`。

真实前驱 `0xa005ae7c..0xa005aec8`：`0xa005ae90` 以 `(ck_config, bind_flag, 0x62fc916d, 1)` 调 `0xa0060946`，`0xa005ae96` 只在返回恰好 1 时跳 `0xa005b8a4`。返回不等于 1：记录日志，然后 `0xa005aec4` 以相同槽/长度调写接口 `0xa0061848`，直接续至 `0xa005aec8`；此失败路径没有本地先写 bind 默认值，也不加载四个位置键、不走 `0xa005b988`。不能把这次回写认成“必定写零”。

读返回等于 1 时，`0xa005b8a4` 再按字节读取 `0x62fc916d`。值为零跳 `0xa005b982`，跳过所有位置读取；值非零按下表顺序执行。

| callsite | namespace/key | a2 目标 RAM | a3 长度 | 本层对返回值的处理 |
| --- | --- | --- | --- | --- |
| `0xa005b8be` | `ck_config/loc_province` | `0x62fc90a0` | 64 | 忽略；继续下次读取 |
| `0xa005b8d6` | `ck_config/loc_city` | `0x62fc90e0` | 64 | 忽略；继续下次读取 |
| `0xa005b8ee` | `ck_config/loc_district` | `0x62fc9120` | 64 | 忽略；继续下次读取 |
| `0xa005b906` | `ck_config/loc_id` | `0x62fc9160` | 4 | 仅等于 4 为读满分支 |

三段文本的键名与后续 URL 参数名不能混同：既验 URL 中 `0x62fc90e0` 作为 adm 文本，`0x62fc9120` 作为 city 文本，虽启动键分别叫 `loc_city`、`loc_district`。`0x62fc90a0` 同时是既验 getter 使用的位置文本缓存；不能把它只解释成省份名。

数值读返回不等于 4 时，`0xa005b92a/0xa005b92c` 构造 `0x186a0=100000`，`0xa005b930` 以 32 bit 写 `0x62fc9160`。随后 `0xa005b944` 以 `(ck_config, loc_id, &RAM[0x62fc9160], 4)` 调写接口；本层不检查写返回。读满 4 时 `0xa005b990` 从 RAM 读该数值并日志，不另做数值范围检查，然后 `0xa005b9ac` 回 `0xa005b948`。两路均先位置日志，再到完成标志。

`0xa005b988` 字节写 `0x62fc3fec=1`，`0xa005b98c` 续至 `0xa005aec8`。这一写在 bind 读取成功且 bind 为零时也发生；它只能解释为本阶段成功门后的标志写，不能命名为“天气已定位/请求成功/绑定非零”。

可供重建的局部顺序合同：

```c
r = config_read("ck_config", "bind_flag", &bind_ram, 1);
if (r == 1) {
    if (bind_ram != 0) {
        config_read("ck_config", "loc_province", cache, 64);
        config_read("ck_config", "loc_city", adm_ram, 64);
        config_read("ck_config", "loc_district", city_ram, 64);
        if (config_read("ck_config", "loc_id", &legacy_id, 4) != 4) {
            legacy_id = 100000;
            config_write("ck_config", "loc_id", &legacy_id, 4);
        }
        log_positions();
    }
    stage_flag_byte = 1;
} else {
    config_write("ck_config", "bind_flag", &bind_ram, 1);
}
```

省略日志只为呈现控制流；写调用仍在原序。这里的变量名是分析名，持久化成功、短读实际写入内容及后端错误语义均未认证。

## 文本终止与首次 getter / URL 接线

观察：在该读取窗口内没有先清零三段 64 B 文本，没有检查其读返回，也没有补写末字节 NUL。故只可确认传给配置读接口的容量参数为 64，不能确认文本读满/截断、失败保留、初始 RAM 清零或终止策略；本轮没有扩扫全启动/BSS/配置后端来填补这些未知。后续调用 strlen 的事实也不能反证这些前提已经满足。

继承 getter `0xa00a0906(out)` 的真实分支，并应用到上述正常来源：

| 首次 getter 输入状态 | 已验行为 | 对 out 的影响 |
| --- | --- | --- |
| `cache[0]==0` | `0xa00a0922→0xa00a0abe` 返回 0，不读 `location_id` | 不复制 |
| 缓存长 9、首字节 '1'，完整解析且数值落 `100000000..199999999` | `0xa00a09c2..0xa00a09d4` 复制上限 64 并返回 1 | 写 out |
| 缓存不走上述文本快路，读 `ck_config/location_id` 不等于 4 | 返回 0 | 不复制 |
| 回退读满 4 | 范围内格式化回 `cache`，按 strlen 写 `loc_province`；返回原数值 `n!=0`，范围外同样按 `n!=0` 返回 | 该次回退不复制 out；修复缓存不能等同本次输出已填好 |
| 进入快路但解析/范围拒绝 | 经日志后退栈，a0 ABI 值仍未认证为 bool | 不补造成功或错误码 |

**启动键 `loc_id` 与 getter 回退键 `location_id` 是两个不同 ROM 键。** 启动读入 `0x62fc9160` 不能当作 getter 读取的 `location_id`，也不能说启动默认 100000 会转换成文本缓存。该区分来自指针/键/槽，而非业务命名推测。

天气 `0xa00aab1c` 在 `0xa00aac5e` 调 getter，`0xa00aac68` 仅按返回是否为零选路。非零走位置 ID URL；`0xa00aac86` 将调用者 out 的第 63 字节写零，但没有弥补回退分支未拷 out 的事实。这里不推断未初始化内容或验证异常输入。

返回零后 `0xa00aae04..0xa00aae28` 的原条件是 **无符号** `*(u32*)0x62fc9160 > 100000`，且 `RAM[0x62fc90e0] | RAM[0x62fc9120]` 的首字节组合非零，才进入既验地区/城市 URL 构造。失败走 `0xa00aaf9a` 的既验构造失败/重排路径。故 loc_id 读失败后的默认 100000，恰好不能满足该旧 URL 的严格大于门；读满 4 本身则不保证它满足门。getter 返回非零的路径并不检查这份 legacy_id。

调用次序在本次入口内已证；“启动在第一次实际天气任务前完成”的跨线程/调度时序仍继承既有生命周期边界，本轮不把局部顺序升格为全系统先后保证。

## 验收与精确断边

已回答：四键到 RAM 的真实映射/参数顺序；bind read 返回与 RAM 字节双门；文本读返回忽略；数值默认值、先写 RAM 后调用配置写；标志写的成功门；首次 getter 读键差异与不拷 out 分支；URL 的真实无符号严格门。

仍未知：配置 API 后端及持久化/失败保证、文本终止及启动前槽内容；getter 拒绝分支日志后 ABI；全系统首次调用先后、其他 writer 和真实服务成功。下一步只需非作者核该启动差集及继承 getter/URL 必要前提；没有无种子 writer 搜索请求。API 调用存在不证明保存成功，更不证明天气服务成功。

实际验证：运行 `verify.py` 通过；`git diff --check`、报告相对链接/JSON 解析见交付消息。本地 JSON 导出列入主窗转存清单，不强加 ignored 文件到 commit。报告、复验源码为唯一提交路径。UTC 计时与工作树状态在交付合同更新；token 与异常等待用量不可得，不编造。

UTC 开始（首个可用时钟）`2026-10-24T16:49:08.995899+00:00`，结束（交付检查）`2026-10-24T16:52:11.323000+00:00`；可观测墙钟 182.3 秒。未发生已知排队、中断或异常等待；普通读取/工具耗时包含在墙钟内，有效工作时长未单独测量，token 用量不可得。
