# B15：数字地区码判定及两个调用窗口独立复核

2026-10-23；分支 `codex/re-0041-b15`；固定基线 `f723db0`。结论：**限定接受[B14](numeric-location-setter-b14-0041-20261023.md)，无核心纠正；独立核准 `a009c5fc` 是 validator 而非 setter。** 完整102B函数接受32位数值，接受集合为闭区间 `100000..659012` 与 `659001000..659012000`，返回严格1或0；函数自身没有业务数据store。依授权精确更正[旧MiIO报告](miio-deferred-settings-0041-20261023.md)相关名称及3/8描述，保留原条件和顺序。

## 范围、来源与独立方法

只复核完整 `a009c5fc..a009c661`（102B）、属性3/8窗口 `a009db6e..a009dbaf`（66B）、kind5窗口 `a00a0dea..a00a0e5b`（114B），加 `a00a0c24..c25`（2B）确认s3常量3。合计284B；没有新增依赖函数体、扫描所有调用者或重扫kind2提交者。

独立脚本[verify.py](../../analysis/numeric-location-review-b15-0041-20261023/verify.py)从主仓库绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin` 只读原字节，以 `offset=VA-0x9ffff000`、Capstone 5.0.7重解全部88条普通指令（0厂商word）。重新按原位域计算16个直接branch/JAL的目标、分支条件和寄存器，独立解C.LUI符号扩展、区间常数、访存字段与压缩返回。B14 JSON只在新ROM解码之后用于地址/字节逐条交叉比较；没有执行或复用B14验证脚本。

新[review-evidence.json](../../analysis/numeric-location-review-b15-0041-20261023/review-evidence.json)保存88条地址/文件偏移/raw/decode、全部直接控制目标、普通访存字段及29组断言（含全表比较）。旧dossier定位沿用B14：主仓库 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-005.json`，Evidence `ev_065c3b82fb97e1d4a2a6582658c6e611107ea48157157f08e5b9ba956e8a3380`、profile `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`。该历史伪代码不作为原指令结论的替代；本次没有建立REA会话或可写数据库。

## 逐项判定

| B14项目 | 判定 | 独立原指令依据 |
| --- | --- | --- |
| a0为完整32位输入 | 接受 | `c606/c61a` 两个 `C.ADD a4,a0`；无byte/halfword掩码。`c620` 原a0复制到a5用于失败日志。原C signed/unsigned声明未核准。 |
| 第一闭区间 | 接受 | `c5fc` raw `2177` 的C.LUI立即数为-24，不是正0x28；结合 `c5fe -0x6a0` 得-100000，`c602/c608` 得559012；`c60c` raw位域为BGEU a3,a4→c65c。因此是 `u32(x-100000)<=559012`。 |
| 第二闭区间 | 接受 | `c610/c614` 得模2^32的-659001000；`c618/c61c` 得11000；`c624` BGEU a3,a4→c660。因此是 `u32(x-659001000)<=11000`。两者均不跨32位零点，区间解释成立。 |
| 返回严格1/0 | 接受 | 第一成功路径 `c65c LI a0,1; c65e JR ra`；第二成功在 `c622` 先置1，再 `c624→c660 JR ra`；失败logger返回后 `c656 LI a0,0; c65a JR ra`，不采用logger返回。 |
| 业务无store | 接受 | 全35条校验器指令只有 `c62a/c62c` 的s0/ra栈保存及 `c652/c654` 对应恢复。无业务全局load/store、输出指针、配置调用。logger内部未展开，不能声称全调用树无副作用。 |
| 日志边界 | 接受 | `c64e` JAL→a008b51a；a0=3、a1=ROM厂商路径、a2=0x74c、a3=函数日志名、a4=格式、a5=原输入。ROM NUL字符串重读核准。 |
| 3/8先缓存后条件配置 | 接受 | `db72 LW 62fc9160`；`db76 BEQ`跳dba8。不同值 `db82` a0=s1，`db84 SW s1,62fcafc0`，`db88` 调validator，`db8c BEQZ`跳dba8。非零才 `dba4` 调a0061848，参数 `ck_config/loc_id/&afc0/4`；该局部不根据配置返回回滚缓存，汇合后继续原通知参数。 |
| kind5天气条件及顺序 | 接受 | `df2` s6=62fcaf80，`df8` strlen，`e14` 先调用a0061848写 `loc_district`；`e1c..e26` LBU/OR2/SB到62fcb02c。`e2a` strlen→a2，`e34` a1=62fc9120，`e3a` 调a00501be。比较0在e3e离开；非0 `e42 LW a0,62fcafc0; e46` 调validator。返回0在e4a跳过；非0还需e50比较flags与s3相等，s3于c24置3，才e54调a00a5b90、e58清flags。 |
| 旧setter术语 | 纠正旧报告，接受B14建议 | `numeric_location_set_a009c5fc` 更名 `area_code_valid_a009c5fc`；“数字位置setter返回非0”改为校验器。3/8补明缓存先写及配置调用条件。未改kind5比较长度/目标/日志位置或其他任务分支。 |
| 来源与恢复程度 | 接受其保留界限 | ROM字符串 `PogoPinMng/MiIotMng.c`、`ck_miio_is_area_code_valid` 支持分析命名，不等同导出符号、原源码、准确版本或未修改开源认证。无新增开源排除；整体位置/MiIO仍部分恢复。 |
| 依赖内部/运行状态 | 未核 | a008b51a、a0061848、a00501be、a002dcae、a00a5b90仅核这些窗口的调用参数/控制边界；沿用旧合同不构成本次重认证。实际落盘、天气请求成功、完整对象生命周期/并发/可达性未知。 |

## 函数合同与必要投影

按RV32寄存器合同，`a009c5fc(a0=x)` 返回a0的0/1，无业务输出指针；调用者分别为属性函数 `a009d8bc` 的 `db88` 与callback `a00a0bd8` 的 `e46`。唯一直接callee为日志 `a008b51a`。下列为机器语义投影，非原始源码：

```c
uint32_t area_code_valid_a009c5fc(uint32_t x) {
    if ((uint32_t)(x - 100000u) <= 559012u) return 1;
    if ((uint32_t)(x - 659001000u) <= 11000u) return 1;
    log_invalid_area_code(x);
    return 0;
}
// 3/8局部，s1为原输入：
if (word_62fc9160 != s1) {
    word_62fcafc0 = s1;
    if (area_code_valid_a009c5fc(s1) != 0)
        config_write("ck_config", "loc_id", &word_62fcafc0, 4);
}
// kind5保留旧顺序：
config_write("ck_config", "loc_district", text_af80, strlen(text_af80));
flags_b02c |= 2;
if (compare_bytes(text_af80, ptr_62fc9120, strlen(text_af80)) != 0) {
    if (area_code_valid_a009c5fc(word_62fcafc0) != 0 && flags_b02c == 3) {
        weather_restart_bridge();
        flags_b02c = 0;
    }
    // 旧报告后续日志条件原样保留；本次窗口在e5c前结束。
}
```

字段地址与宽度、常量、控制流、字符串为ROM观察事实；“缓存”“门控”“配置写”“天气重排”是基于既有合同的解释。参数输入范围的行政区划/服务端意义、原始C类型、准确来源版本、日志内部副作用、配置实际持久化均未知。不能把validator返回非0解释成位置已应用，也不能把先前配置调用移到校验之后。`62fc9160` 在本范围只读，更新者未恢复。

## 实际验证与交付边界

运行本次verify.py退出0：284B/88条、16个直接控制目标、29组断言通过。人工逐条审阅全部解码，交叉核对算术、返回、栈访存、调用参数、两个调用窗口条件及先后顺序。未枚举/探测任何输入，未执行固件、连接设备或外部服务、验证缺陷、改安全检查/ROM/生产代码/分析模型。未新建哈希或复制清单。已检查工作树祖先、本树及reverse适用目录，无AGENTS.md；仅写B15独占报告/analysis及被明确授权的旧报告术语部分。JSON解析、`git diff --check`及差异范围核对通过。

Git初次明确路径暂存返回 `.git/worktrees/re0041-b15/index.lock: Permission denied`；依用户本地提交授权使用工具升级后暂存成功。没有改权限或绕过安全限制。

本函数完整正常合同及两个既有调用窗口达到本次限定复核要求；全模块未完成。一个小后继建议：只从现有inventory/引用选择 `62fc9160` 的一个直接写者，确认word写入值/条件；无明确现有证据则保留未知，不全ROM重扫、不扩完整位置或天气状态机。本任务不自行领取后继。
