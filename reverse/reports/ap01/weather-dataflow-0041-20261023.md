# 0041 WeatherApi：请求对象、TLS 适配、JSON 与 UI 发布

后续已补[位置持久化及请求构造](weather-location-request-0041-20261023.md)：两条 URL 路径、摘要输入顺序、RV32 可变参数布局和 MD5 算法识别。下文保留本轮当时的未知项；精确库来源、时钟和完整生命周期仍未闭合。

本轮继续全 ROM 非开源逻辑恢复，在[天气调度合同](weather-scheduling-0041-20261023.md)基础上新增传输与数据发布合同。原件仍为 `roms/0041/ap01-1.0.2_0041.bin`，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只做静态分析；未访问天气服务、运行固件、进行缺陷验证、改认证/校验、修改 ROM 或提交/推送。模块仍为**部分恢复**。

本文函数/字段名是分析命名，结构体是 ROM 存储视图，不是恢复出的原始源码。类型符号及职责有明确指令支撑的标为事实；库名称、温度有符号解释等为推断，来源未确认的代码不排除出范围。

## 证据入口

材料位于 `reverse/analysis/weather-dataflow-0041-20261023/`：

- [contracts.json](../../analysis/weather-dataflow-0041-20261023/contracts.json)：156 B 数据布局、请求视图、TLS 表与对象、UI 发布地址及 ROM 字符串。
- [instruction-windows.json](../../analysis/weather-dataflow-0041-20261023/instruction-windows.json)：8 个限定窗口的原字节、哈希和 Capstone RV32C 指令。前四个传输/解析窗口均没有未知指令；时钟窗口保留一个未知厂商字。
- [retained-functions.json](../../analysis/weather-dataflow-0041-20261023/retained-functions.json)：7 份既有修复模型观测及来源指纹，包含 connect、recv、请求调度、四个 UI 注册/发布函数。只将本轮审阅职责计入恢复，不把整个大函数自动标完成。
- [rea-generic.evidence.json](../../analysis/weather-dataflow-0041-20261023/rea-generic.evidence.json)：本轮连接式 REA 的 8 条成功观测；[失败返回](../../analysis/weather-dataflow-0041-20261023/generic-procedure-errors.json)另存。
- [analysis-limitations.json](../../analysis/weather-dataflow-0041-20261023/analysis-limitations.json)：函数识别和时钟/库来源局限。

原厂指令表项指向 `a00a47a8`、`a00a48ae`、`a00a4068`，请求代码指向 `a00aa13a`；通用 Ghidra 对这四个地址返回“没有对应 procedure”。指令事实和登记入口仍在 ROM 中，故按返回边界及调用形状人工审阅窗口，不虚构 Ghidra 已建立函数，也不把这些代码排除。未重复相同失败查询，未重启此前受限的私有客户端或更改访问权限。

## 请求视图与所有权

`a00aab1c` 中一次请求分配 4096 B IO 缓冲区，在栈上清零 0x74 B 请求对象。已确认字段如下，空缺字段暂不命名：

| 偏移 | 写入内容 | 意义 / 边界 |
| --- | --- | --- |
| `+0` | byte 0 | 请求模式原值，未认证原枚举名 |
| `+8` | URL 指针 | 构造函数选择 location ID 或地区/城市分支 |
| `+0x24` | 5 | 连接超时参数；TLS 回调将其放入 timeval 秒字段 |
| `+0x30` / `+0x34` | buffer / 4096 | IO 缓冲区及容量，不冒称完整响应累积区 |
| `+0x3c` | `a00aa13a` | body sink 回调 |
| `+0x40` | 0 | sink 用户参数初值 |
| `+0x54` / `+0x58` | TLS 操作表 / TLS 工作区 | 仅 HTTPS 分支写入 |
| `+0x60` | 请求后读取 | HTTP status |
| `+0x70` | byte 1 | 请求控制标志原值，枚举语义待核 |

URL 以 `https://` 开头时，外层另分配并清零 0x778 B 工作区，预设 `workspace+0x770` 的 fd=-1，再初始化其中的 TLS 子对象。执行接口为 `a00efb74(request)`；普通分支直接调用，HTTPS 分支附带下述操作表。URL 身份参数/签名构造仍待独立恢复，没有修改或替代它们。

HTTPS 请求返回后，外层按原顺序检查/关闭有效 fd，清理 TLS 子对象并 free 工作区；随后处理 status/计数/调度，free IO 缓冲区。body sink 的 JSON tree 和 156 B 输出对象是另外的生命周期，不能混成 IO buffer 所有权。

## TLS 私有适配表与生命周期

ROM `a028d804..a028d817` 是五个 32 bit 函数指针：

| 槽 | 入口 | 已恢复合同 |
| --- | --- | --- |
| 0 | `a00a9d64` | connect，成功输出 4 B session wrapper |
| 1 | `a00a47a8` | send，调用 TLS write 并转换两类等待返回值 |
| 2 | `a00a481c` | recv，转换等待/对端关闭返回值 |
| 3 | `a00a48ae` | close，清理 TLS、关闭 fd、释放 wrapper |
| 4 | `a00a4068` | 取得 poll 信息，输出 fd 与值为 3 的控制字 |

工作区分段入口为 `+0`、`+0x150`、`+0x22c`、`+0x380`、`+0x4e0`，fd 为 `+0x770`。根据调用形状和日志，依次对应 SSL、config、证书、DRBG、entropy 的候选对象；没有精确版本来源匹配，不认证全部内置库类型。

connect 的可确认步骤：

1. malloc 4 B wrapper；失败置状态位 `0x1000` 并返回 -12。
2. 初始化工作区中的子对象；配置/装配失败的路径置位 `0x2000`。这与外层的初始对象设置存在重复，原样记录，不擅自合并。
3. 读取内嵌 PEM 证书 `a037821c`、长度参数 `0x66f`；失败置位 `0x800`。config 内 `workspace+0x156` 写入 2；保留其验证模式原值，不替换安全检查。
4. 设置主机名/SSL 配置，创建 socket，将 fd 写到 `+0x770`。以 `{timeout_argument,0}` 的 8 B 参数调用两次 socket option（level=1，option=10/14）；原 option 名待平台头文件匹配。
5. 解析 hostname，整理地址列表；DNS 失败置 `0x100`，关闭 fd、free wrapper 并返回 -113。TCP connect 失败置 `0x200`，关闭 fd、free wrapper 并返回负 errno。
6. 将网络回调 `a00c6e4c`、`a00c6dde` 与 fd 地址接到 SSL 对象，再执行 handshake。失败置 `0x400` 并按原清理路径返回；成功时 `wrapper->context_address=workspace`，`*out_session=wrapper`，返回 0。

```c
// RV32 存储视图：不是宿主指针大小的结构体。
struct TlsSessionView { uint32_t context_address; }; // 4 B

int private_tls_send(void *unused, TlsSessionView *s, void *buf, uint32_t n) {
    if (!s || !s->context_address) return -22;
    int rc = tls_write(s->context_address, buf, n);
    return rc == -0x6900 || rc == -0x6880 ? -11 : rc;
}
int private_tls_recv(void *unused, TlsSessionView *s, void *buf, uint32_t n) {
    if (!s || !s->context_address) return -22;
    int rc = tls_read(s->context_address, buf, n);
    if (rc == -0x6900 || rc == -0x6880) return -11;
    if (rc == -0x7880) return 0;
    return rc;
}
```

read/write 候选分别为 `a00cdfc2` / `a00cdeea`；等待及关闭的名字由常见 Mbed TLS 语义与原日志支持，数值转换则是指令事实。close 的首个 TLS 关闭动作在 `a01adb74`，随后执行子对象清理，fd>=0 时 close 并写 -1，再 **free wrapper**，返回 0。它没有 free 外层工作区；外层仍按自己的清理流程处理工作区。本轮未用“应该去重”的假设改变这些调用顺序。

poll 回调要求 wrapper、内部 context 和输出指针均非空，否则返回 -22；成功将 fd 写到输出 `+0`，将 word 3 写到输出 `+4`，返回 0。这里保留写宽度，不根据常见 pollfd 类型猜造整个输出结构。

## JSON sink 与 156 B 天气对象

`a00aa13a` 首先计算 `length=end-start`；正长度时对 `*buffer_ref+start` 调 `a0195bfa(pointer,length)`。没有在本窗口累积多个调用的数据，不能把它改写成自建完整响应拼接器。解析失败时置状态位 `0x02000000` 并返回 0；未将它改成向 HTTP 层返回错误。

解析成功时读取 root 的 `code`、`cache` 并作日志记录，然后清零 156 B 输出对象。实际载荷字段名是 **`msg`**，类型低字节要求 `0x40`；不是根据常见接口猜出的 `data`。`msg` 下使用 `loc`、`now`、`daily` 等字段。数值节点读 `+0x18`，字符串通过 `a0098a5a` / `a0098a76` 判定和取值；完整 JSON node 结构及库版本仍待来源核对。

```c
// 以下布局由 sh/sw 偏移与接收方 memcpy(156) 双向印证。
// 温度 int16_t 是业务含义推断；实际指令事实为截取写入 16 bit。
struct CurrentWeatherView {              // 36 B
    uint16_t year, month, day;            // daily[0].dt 固定位置 0/5/8 转整数
    int16_t feels_like;                   // now.feel，+6
    int16_t temp_max, temp_min;           // daily[0].mx/mn，+8/+10
    int16_t temperature;                 // now.tmp，+12
    uint16_t sunrise_hour, sunrise_minute;// daily[0].sr，+14/+16
    uint16_t sunset_hour, sunset_minute;  // daily[0].ss，+18/+20
    uint16_t uv_level, aqi, humidity;     // now.uvlvl/aqi/hum，+22/+24/+26
    uint32_t icon_a, icon_b;              // now.ico 转整数，分别写 +28/+32
};
struct FutureDayView {                    // 20 B
    uint16_t year, month, day;            // dt
    int16_t temp_max, temp_min;           // mx / mn
    uint16_t reserved;                    // 保持初始 0
    uint32_t icon_a, icon_b;              // id 转整数，同值写两处
};
struct Weather7DayView {                  // 156 = 36 + 6*20
    struct CurrentWeatherView current;
    struct FutureDayView future[6];
};
```

具体字段映射与写入位置见机器合同。原转换为 `a0053f46` 的字符串转整数，随后 sh/sw；没有添加钳位、单位转换或格式纠正。日期在长度大于 9 时按 0/5/8 位置转整数；日出/日落在长度大于 4 时按 0/3 位置转整数。

`daily` 要求类型低字节 `0x20`，遍历链表计数，并最多处理索引 0..6。第 0 项补当日日期、最高/最低温及日出日落；其图标分支不覆盖 now.ico。索引 1..6 分别写六个 20 B 未来块，其 id 同值填两个图标槽。两个槽的最终 UI 区别未认证，不直接起名“昼/夜天气”。可选字段缺失时保留清零结果。

`frm`、`loc.city`、`nup`、`dup`、`now.wsc/wsp/txt` 还有日志/位置处理，但不存入上述 156 B 对象。`loc.id` 与旧 ID 查询/设置函数相连；其持久化和刷新触发内部语义待单独闭合。root 的 code/cache 日志不直接充当本窗口的解析分发成功开关。

## 回调注册、缓存及订阅生命周期

原始注册指令 `a005cde4..a005cdf0` 将 `a00b3c74` 写到全局单回调槽 `62fc998c`。sink 在完成 JSON 分支后删除 JSON tree，再从该槽取回调，以栈对象地址调用。已解析而缺少 msg/daily 的分支也会汇合到这个发布路径，保留其零值/部分值行为。

`a00b3c74` 的处理顺序：

1. 数据为 NULL 只记录日志。
2. 否则先 `memcpy(62fc98f0, data, 156)` 缓存，再记录各天日期/图标。
3. 调 `a00b3be6(data)` 同步分发。**这里传原 data 指针，而不是改传全局缓存。**
4. 查当前主题窗口 1 和天气页 4，存在对应对象时调用 `a00d8f7c(object,1)`；该标志具体 UI 含义本轮未认证，不冒称已经刷新显示。

注册表在 `62fcc370`，5 槽、每槽 8 B，保存 `{callback,user_arg}`。`a00b3a68(cb,arg)` 找第一个 callback 为 0 的槽插入；不做去重，无空槽时不插入，仍走共同日志。`a00b3abe(cb,arg)` 只清第一组同时匹配的两个 word；未命中走共同日志。同步触发 `a00b3be6` 逐槽检查 callback 和 user_arg 都非 0 后调用。

这里必须纠正旧反编译的参数遗漏：`a00b3c18` 明确将 user_arg 装入 a1，`a00b3c1c` 将 data 装入 a0，`a00b3c1e` 间接调用。因此合同为 **`callback(data,user_arg)`**，不能照旧伪代码写成单参数调用或说 user_arg 仅用于门控。

```c
void weather_publish_local(const Weather7DayView *data) {
    if (!data) { log_null(); return; }
    memcpy(global_weather_cache, data, 156);
    for (int i=0; i<5; ++i) {
        if (subscribers[i].callback && subscribers[i].user_arg)
            subscribers[i].callback(data, subscribers[i].user_arg);
        else
            log_empty_slot();
    }
    // 原厂后续窗口查找/对象调用保持独立，未在这里补造显示实现。
}
```

生产者传入的对象位于 sink 栈帧，发布是同步调用，handler 已先缓存；订阅者若想在返回后使用输入，仍须自行复制或访问约定缓存，不能从缓存存在就推导原栈指针可长期保留。各个订阅者的具体保存/注销与 UI 销毁链尚未全部核对。

## 本轮新增覆盖与未决项

已恢复局部职责：请求对象关键字段与 IO/TLS/workspace/wrapper 所有权、五个传输回调的适配合同、156 B 天气输出与七天分配规则、单回调注册、UI 缓存及五槽双参数订阅分发。与上一轮调度相连后，已形成 `timer → request → TLS adapter → JSON sink → stack weather view → UI cache → subscribers` 的静态数据流。

未决项仍包括 URL 签名构造、位置更新内部合同、HTTP 核心/完整 TLS 与 JSON 来源版本及厂商修改、天气 UI 的全部订阅者和图标变换、timer 停止/销毁闭包。时钟 helper 的调用参数 0、两次除 1000 和厂商字 `0xa4e91577` 已记录，但后者尚未精确解释，不能据通用反编译认证时钟源/epoch/完整计算式。

JSON 类型常量/接口形状与 cJSON 家族相似，TLS 日志含 mbedtls 名称；两者都还缺准确版本和未修改实现比对依据。本轮新增已验证开源排除为 0；不因库候选名排除适配和回调，也不继续重做已知通用解析算法。

核对结果见[review-index.json](../../analysis/weather-dataflow-0041-20261023/review-index.json)：原件 SHA256、8 个窗口及逐条指令字节、7 份既有来源/范围、5 槽 TLS 表、156 B 字段尺寸和订阅分发 a0/a1 寄存器赋值均通过；新增 8 条 REA 观测目标身份一致，报告链接及 `git diff --check` 通过。这些检查只支撑上述静态合同，不证明整模块或全 ROM 已完成。
