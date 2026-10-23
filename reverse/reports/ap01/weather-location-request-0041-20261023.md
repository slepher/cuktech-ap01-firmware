# 0041 天气位置状态与请求构造

后续补充：[MiIO timer 全部任务分支、位置提交者与天气重排桥](miio-deferred-settings-0041-20261023.md)；本文保留当时已核范围。

本轮沿[天气请求/UI 数据流](weather-dataflow-0041-20261023.md)补位置持久化、请求分支与 token 构造。依据仍是原厂 0041，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。只做静态分析和原字节/常量核对；未发送请求、连接设备、运行固件、验证缺陷、修改安全检查、提交或推送。所有新增文件位于研究目录。

本模块仍为**部分恢复**。以下是分析命名的伪代码和状态合同，不是原始源码。特殊返回值、复制参数和写入顺序均按指令保留，不按期望业务修正。

## 证据入口

材料位于 `reverse/analysis/weather-location-request-0041-20261023/`：

- [contracts.json](../../analysis/weather-location-request-0041-20261023/contracts.json)：字段、格式模板、请求输入顺序、MD5 识别与剩余未知。
- [retained-functions.json](../../analysis/weather-location-request-0041-20261023/retained-functions.json)：位置 getter/setter、天气大函数的 3 份修复模型观测，附原字节和来源 SHA256。对应历史 `whole-rom-private-20261023-017/018/070.json`。
- [instruction-windows.json](../../analysis/weather-location-request-0041-20261023/instruction-windows.json)：复制接口、MAC 获取、摘要封装/压缩/结束的 5 个原字节窗口，未知厂商指令显式保留。
- [rea-generic.evidence.json](../../analysis/weather-location-request-0041-20261023/rea-generic.evidence.json)：本轮通用 RV32 的 3 条观测，仅用作接口/汇编交叉核对，反编译中 memcpy/memset 的错误 no-return 截断不作为原行为。

## 位置对象、持久化及返回合同

| 地址 / 键 | 已确认的读写 |
| --- | --- |
| `62fc90a0` | 文本位置 ID 的缓存，同时复用于 `loc_province` 文本；相关调用长度上限为 64 |
| `62fc90e0` | 地区/行政区文本，URL 模板的 adm |
| `62fc9120` | 城市文本，URL 模板的 city |
| `62fc9160` | 旧式地区/城市请求的数值门控，要求大于 100000；字段原名待核 |
| `ck_config/location_id` | 4 B 数值形式的持久化 ID |
| `ck_config/loc_province` | 原字节文本写入，写长度使用 strlen，不包含结尾 NUL |

getter `a00a0906(out)` 的输入是输出缓冲区地址，返回使用 a0；其所有路径不能统一还原成“成功返回 bool 并填 out”：

```c
uint32_t get_location_id_view(char *out) {
    if (location_cache[0] == 0) return 0;   // 这里没有读持久化
    log_cache_and_length();
    if (strlen(location_cache) == 9 && location_cache[0] == '1') {
        char *end;
        int32_t n = parse_signed_decimal(location_cache, &end, 10);
        log_numeric_value(n);
        if (*end != 0 || (uint32_t)n - 100000000u > 99999999u)
            return A0_AFTER_LAST_LOG;      // ABI 值未认证为 bool；不补写 0
        copy_with_limit(out, location_cache, 64);
        return 1;
    }

    uint32_t n = 0;
    if (config_read("ck_config", "location_id", &n, 4) != 4) {
        log_read_failed(); return 0;
    }
    if (n - 100000000u <= 99999999u) {
        snprintf(location_cache, 64, "%u", n);
        config_write("ck_config", "loc_province",
                     location_cache, strlen(location_cache));
        log_psm_value();
    } else {
        log_not_nine_digit_value();
    }
    return n != 0;                         // 原指令条件，不改成上述范围条件
    // 此回退路径没有向 out 复制；只在范围内修复全局文本。
}
```

关键地址：空缓存直接返回 `a00a0922→a00a0abe`；文本快路复制在 `a00a09c2..a00a09d4`；读持久化在 `a00a09ea..a00a0a0e`；范围检查、格式化和文本写回在 `a00a0a12..a00a0a7c`；返回 `n!=0` 在 `a00a0a80..a00a0a88`。快路拒绝分支直接去寄存器恢复/ret，没有在日志之后重新赋 a0，因此返回值保留为 ABI 未决项，未猜造错误码。

setter `a00a0ac2(input)` 无可用状态返回。NULL 仅记日志；非 NULL 时读取 strlen。长度 9 且首字节 '1' 的分支按以下顺序执行：

1. `copy_with_limit(62fc90a0,input,4)`，随后显式将 `62fc90df` 写 0。**传入复制函数的长度事实是 4**（`a00a0b08`），不能依据后续日志里的 64 改成 64。
2. 以完整输入和 strlen(input) 写 `ck_config/loc_province`。
3. 调 `a002fba6(input,NULL,10)` 转成 32 bit 值，以 4 B 写 `ck_config/location_id`。
4. 记录原输入、转换值、长度及日志参数 64。配置写入结果在此分支未用于回滚或状态返回。

不满足长度/首字节条件的非 NULL 分支仍将完整输入写入 `loc_province`，但不更新上述缓存和数值键。getter 与 setter 的筛选规则、输出写入及返回合同分别记录，没有合并成一个推测的“有效位置 ID”辅助函数。

复制接口 `a01b406c` 有字节循环、字循环和源 NUL 后补零分支；本轮以“带长度的复制接口”描述它，不凭形状认证其具体开源名称/版本。setter 长度 4 与显式第 63 字节写 NUL 的事实独立于该名称。

## URL 分支和请求对象关联

天气大函数 `a00aab1c` 在创建 GET 请求和缓冲区后先调用 getter：

- getter 返回非 0，走 location ID 分支。调用者在取得的文本末尾第 63 字节置 NUL，然后使用该输出区构造请求；getter 的所有返回路径/输出合同见上文，不用理想化规则替换调用。
- getter 返回 0，检查 `*(u32*)62fc9160 > 100000`，且 `adm[0]` 或 `city[0]` 至少一项非 0，才走地区/城市分支。两个文本从 RAM 复制到栈临时区。检查失败记录 URL 构造失败，置天气状态位 `0x1`，释放 IO 缓冲区并转入已有重试调度。

位置 ID 分支的静态 URL 存储起点为 `62fcb8ac`，地区/城市分支为 `62fcbaac`；两者是全局存储，地址差 512 不单独作为完整对象容量证明。构造完成后指针写入请求对象 `+8`（见上一轮 0x74 B 请求视图），本次同步请求流程借用该指针，不 free URL。

ROM 原始格式模板：

```text
https://iot.cuktech.net/api/weather2?
%slocid=%s&mac=%s&timestamp=%lld&token=%s

https://iot.cuktech.net/api/weather?
%scity=%s&adm=%s&mac=%s&timestamp=%lld&token=%s
```

字段以原字符串进入模板。这里仅保存 ROM 格式合同，没有构造或发送实际服务请求。

## MAC、时间和摘要输入

`a005f240(out6)` 的调用者先将 6 B 临时区清零。helper 创建 `socket(2,2,0)`，将接口名 `wlan0` 放入临时请求，以 ioctl `0x714` 查询；返回 0 时从请求偏移 22 复制 6 B 到 out6。有效 socket 随后 close；socket/ioctl 未成功的分支不写 out6，因此保留调用者原有零值。helper 没有向这里的调用者提供有效的成功状态检查。

MAC 六个 byte 依次按 ROM 模板 `%02x` 格式化，形成 **12 个小写十六进制字符**，不带分隔符。时间来自 `a00a9d1e` 的 a0/a1 两个返回寄存器，以 `%lld` 的有符号 64 bit 十进制表示。本轮不越过上一轮保留的厂商时钟指令未知项，未认证其 epoch 或具体时钟源。

固定后缀是 ROM `a0269f3c` 的 7 字节 ASCII 字符串 `D3#8F&n`，名称“后缀”是分析命名，不将它说成用户账号凭据。摘要消息顺序由拼接模板和汇编参数共同确认：

```text
ID 分支：
  message = locid || signed_decimal(timestamp) || mac_hex12 || "D3#8F&n"
  token   = lower_hex32(digest16(message))

地区/城市分支：
  message = adm || city || signed_decimal(timestamp) || mac_hex12 || "D3#8F&n"
  token   = lower_hex32(digest16(message))
```

拼接符号 `||` 只表示连接，没有额外分隔字节。ID 分支初始格式 `%s%lld` 在 `a00aacc0` 调用；地区/城市分支 `%s%s%lld` 在 `a00aaebc` 调用。然后两条路径分别 append MAC 和固定后缀，再传 strlen(message) 给摘要封装。输出的 16 B 摘要逐 byte 以 `%02x` 转成 32 字符 token。

必须保留 RV32 可变参数的对齐：ID 初始格式调用的 locid 在 a2，时间 low/high 在 a4/a5，a3 不是遗漏的业务参数；最终 ID URL 的时间在 a6/a7，token 指针位于栈参数槽。地区/城市最终 URL 依次用 a3=city、a4=adm、a5=MAC、a6/a7=时间，token 指针同样在栈上。旧反编译中缺失/错位的参数已按这些寄存器赋值解释，不能将其抄成丢失时间或参数顺序不同的参考实现。

## 摘要算法识别与开源边界

`a00b4e1a(input,length,out)` 清零 0x58 B 上下文，写入四个初值 `67452301 / efcdab89 / 98badcfe / 10325476`，随后调用 update=`a00791c6`、final=`a0079270`。压缩函数窗口 `a0078904..a00791c5` 中，LUI/C.LUI 与 ADDI/C.ADDI 构造的 **64 个轮常量全部匹配 MD5 常量**；final 窗口可见 0x80 填充及块内 56 字节边界处理，调用者消费 16 B 输出。

这些是“摘要为 MD5 家族实现”的高置信静态识别依据，详细常量及指令位置保存在机器合同中。它们不能证明某个精确上游版本或整段实现未经修改。因此本轮不重新实现通用 MD5 算法，也不把该函数族自动列为“已验证开源、全部排除”；厂商包装、输入拼接、参数和生命周期仍是恢复范围。

## 剩余未知与范围

位置读写和请求构造已经获得逐分支、逐字段的局部合同；仍需补全所有位置字段写入者、重启初始化与刷新触发、getter 特殊路径的日志后 ABI 返回值、摘要实现的准确来源/修改、时钟厂商指令，以及天气全部订阅者和 timer 停止/销毁闭包。原有调度、TLS 适配、156 B 数据和 UI 发布合同继续复用。

本轮没有执行原件或对服务输入做验证；所有特殊分支只按静态语义记录，未继续缺陷调查。整个 ROM 的工厂测试、其他私有协议、无线/驱动/启动胶水、内嵌固件及来源未知代码仍在持续目标范围，未将完成标准缩小为天气模块。

最终[核对记录](../../analysis/weather-location-request-0041-20261023/review-index.json)：原件 SHA256、3 份来源/函数原字节范围、5 个指令窗口、13 个 ROM 字符串、64 个摘要轮常量、setter 的长度 4 和 URL 参数寄存器赋值均通过；新增 3 条 REA 观测目标身份一致，报告链接及 `git diff --check` 通过。它们只证明本文静态合同，不替代整模块和全 ROM 完成审计。
