# A16：天气订阅首消费合同独立复核

2026-10-23；基线 `f966a5e`，分支 `codex/re-0041-a16`。结论为 **接受，附一处边界文字纠正**。A15 的三个核心局部 `a00a7fc2` 注册 → `a00ab6b0(data,obj)` → `a008ce90(arc,low,high)` 经原 ROM 字节独立核对成立。范围只含构造器的必要注册切片、完整回调和首个 range consumer；不扩天气 UI、图标实现或生命周期。

使用 reverse-engineer-anything skill；只读共同规则/A16 任务书、A15 及天气数据流相关证据。逐级检查本 worktree 祖先与 reverse/reports/ap01、reverse/analysis 的 AGENTS.md，未发现适用文件。只使用离线 Python/Capstone 读取主仓库 ROM 和本树已有证据；未开 REA 可写会话/数据库，未执行固件、仿真、回放、连接设备或外部服务，未改生产代码/安全检查/ROM/模型，未新建哈希或 inventory。

## 证据与验证方法

- 原件只读路径：`D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`。身份沿用 A15 / 既有 dossier 的 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，本轮不重新散列。代码/字符串映射为 `file_offset = VA - 0xa0000000 + 0x1000`。
- [A15 报告](weather-subscriber-a15-0041-20261023.md)及其 [instruction-windows.json](../../analysis/weather-subscriber-a15-0041-20261023/instruction-windows.json)、[retained-registration.json](../../analysis/weather-subscriber-a15-0041-20261023/retained-registration.json)、[strings.json](../../analysis/weather-subscriber-a15-0041-20261023/strings.json)为被复核材料。注册 slice 的历史来源为 `whole-rom-private-20261023-064.json`，Evidence `ev_ac8900d80eb4c1a9ced9d9652a8a87e8406ef2059cabd2cb59272c0dfa080845`，参数 `a00a7766`；本轮不把历史整个构造器的反编译模型重新认证。
- 本轮 [verify.py](../../analysis/weather-subscriber-review-a16-0041-20261023/verify.py)直接从原件重新解码，不执行 A15 脚本；逐字节/逐指令比较 A15 七窗口，并自行按 RV32 I/S/B/J、RV32C load/store/branch 位域提取 40 项关键编码。不能仅凭反编译类型或反汇编助记符接受 signed、参数或分支结论。
- [instruction-review.json](../../analysis/weather-subscriber-review-a16-0041-20261023/instruction-review.json)保存原字节、文件偏移、140 条解码指令及独立编码结果；八窗口共 420 B，其中原七窗口 412 B，另加 `a00a7fb0..7fb7` 的 kind 赋值/相邻调用边界，不恢复该相邻 helper。六条 A15 名称/路径字符串与原件相等。[review-index.json](../../analysis/weather-subscriber-review-a16-0041-20261023/review-index.json)为实际运行结果 `passed`。

## 逐项判定

| A15 主张 | 判定 | 原指令依据与边界 |
| --- | --- | --- |
| 选取的是 `a00a7766` 内部一个注册点，非独立 constructor 入口 | 接受 | `a00a7d42..7d5a` 是已有构造器切片；`s8!=2` 的门与 `s1/s9` 返回保存可见。未认证完整函数控制流或原始模式枚举。 |
| `a00a7fc2` 注册参数为 `(a00ab6b0,s1)` | 接受 | `7fb8` LUI 与 `7fbe` ADDI 构成函数地址，`7fbc` 把 `s1` 放入 a1，JAL 位域目标 `a00b3a68`。调用后才写 wrapper/context 链接，注册结果未检查。注册器的首空槽规则/成功返回未重做，沿用天气数据流合同，不能证明实际插槽成功。 |
| context 与 object 链接是 word | 接受 | `7f56` 写返回控件至 `s2+0x18`；`7fca/7fce/7fde` 分别写 `s2→s9+4`、`s8→s9+0`、`s9→s1+0x10`，均 SW。新增原字节 `7fb0` 确认 `s8=0x2f`；此前分配参数 0x14/0x28 及非零门与 A15 相符，不展开分配器/失败臂。 |
| 双参数间接 ABI `callback(data,user_arg)` | 接受，限直接窗口 | `a00b3c14/3c18` 两个 C.LW，函数/参数各经过非零门，`3c1c` 为 `a0=s3`，`3c1e` 为 `c.jalr a5`。此窗口没有第三参数的设置，不认证未指定寄存器值或完整分发时序。原数据而非缓存的来源沿用天气数据流已有合同，本轮未重做全发布函数。 |
| 回调只对 obj 非空设入口门 | 接受 | `a00ab6b0` 的 C.BEQZ 位域目标 `a00ab752`，即直接 `jr ra`；非空后 `6c0/6ca` 两次 C.LW 取得 `*(obj+0x10)` 与 `*(wrapper+4)`，没有额外天气指针/内部指针非空门。 |
| +8/+10/+12 是 signed halfword，+28 是 word | 接受 | `6c2/6c6/6cc` 的 load opcode=3、funct3=1（LH），基址 a0，分别扩展到 a2/a1/s2；`6d0` funct3=2（LW），读入 s3。+8/+10 的业务最高/最低温名沿用已解生产布局；signed 读取本身是此回调事实。 |
| `low>=high` 时用 [-60,60] 局部回退 | 接受 | `6d4` 是 signed BLT a1,a2，目标 `6e0`；否则 `6d8` 置 a2=60、`6dc` 置 a1=-60。无两端各自限制到 ±60 的指令，不写回天气对象。严格有序时原值保留，即使超出 ±60；这里只是静态分支语义，未构造输入或执行测试。 |
| 首消费调用 `(arc,low,high)` | 接受 | `6e0` C.LW a0,0x18(s1)，`6e2` JAL 目标 `a008ce90`；因此 a1=low、a2=high，与天气读取先 high 后 low 的指令顺序不同。 |
| range 字段写入、value 钳位及早退 | 接受 | `a008cedc/cee2` 读 +0x44/+0x48；`cede` BNE 在 low 不同即去 `cee8`，`cee4` BEQ 在两项均相同时去 `cf00` 返回。改变时 `ceea/ceec` 用 C.SW 写边界；`ceee` signed BGE 检查 value>=low，否则 `cef2` 写 low；`cef4` 重读，`cef6` signed BGE 检查 high>=value，否则 `cefa` 写 high；`cefc` JAL 到 `a008ccd2`。范围 helper 本身不执行 low/high 重排，不能外推所有调用者都保证 low<high。 |
| 回调只借用天气地址，局部复制标量 | 接受，限直接行为 | 完整 `a00ab6b0..b753` 的存储均为保存被调用者保存寄存器到栈；没有保存输入天气地址、天气对象 memcpy 或直接写输入。四字段在首次下游调用前进入寄存器，range helper 不接收天气地址。callee 是否持有内部 UI 指针/标量和其他订阅者所有权仍未核。 |
| 后续图标调用 `a0198946(context+0x20,icon_a)` | **纠正记法** | `a00ab710` 原编码 `8850` 是 C.LW a0,0x20(s1)，所以首参为 `load32(context+0x20)`，不是 `context+0x20` 这个地址；`712` 将 s3 放入 a1，`714` JAL 到 `a0198946`。仅纠正调用边界，不解释其实现。A15 此处为简写歧义，核心 range 结论不受影响。 |
| 两函数有稳定数值返回 | 未核且不主张 | 回调空 obj 路直接保留 a0；正常路径调用日志后恢复返回。range 无变更直接返回、变更路径调用更新 helper；本调用者不消费返回值，不能统一承诺 0 或其他值。 |

## 可读存储视图与边界

以下均为分析名和 RV32 存储视图，不是恢复的原源码；指针宽度固定 32 bit。

```c
callback(weather, obj) {
    if (obj == 0) return; // a0 无稳定数值合同
    wrapper = load32(obj + 0x10);
    ctx = load32(wrapper + 4);
    high = sign_extend16(load16(weather + 8));
    low  = sign_extend16(load16(weather + 10));
    current = sign_extend16(load16(weather + 12));
    icon = load32(weather + 28);
    if (!(low < high)) { low = -60; high = 60; }
    a008ce90(load32(ctx + 0x18), low, high);
    // 后续 current/icon 的消费存在；实现不在本次范围。
}

a008ce90(arc, low, high) {
    // 仅正常非空对象路径；保留 ROM 中非空门/诊断路径，不推定诊断会返回。
    if (load32(arc + 0x44) == low && load32(arc + 0x48) == high) return;
    value = load32(arc + 0x40);
    store32(arc + 0x44, low);
    store32(arc + 0x48, high);
    if (signed(value) < signed(low)) store32(arc + 0x40, low);
    value = load32(arc + 0x40);
    if (signed(value) > signed(high)) store32(arc + 0x40, high);
    a008ccd2(arc); // 内部未核，不能等同屏幕完成绘制
}
```

这闭合了 signed 16 bit 天气标量到 signed 32 bit range 参数及 32 bit arc 字段的局部消费链。局部回退写寄存器、range helper 写 arc 字段；没有因此获得整个天气对象的复制/持有权证明。注册后才接上对象字段的事实不证明运行时无交错或生命周期安全。

## 来源、恢复程度、实际验证与后继

ROM 字符串 `lv_power_ui/lv_ui_scr_saver.c`、`lv_ui_ssr_tim2_update_wx_data_cb` 支持厂商 UI 胶合职责，但原源码及版本未知。`lv_arc_set_range` 与 `.../lvgl/src/widgets/arc/lv_arc.c` 支持 LVGL 候选来源；本轮未找到/认证精确源码版本或无厂商修改实现，不新增开源排除，也不以来源未知自动称其私有。只接受原字节可见语义，不把名称相同当成来源匹配。

实际运行本轮 verify.py：8 窗口、420 B、140 条指令完整解码；A15 七窗口的原字节与解码行全部相等；40 项独立原编码核对通过；六条路径/名称字符串相等。检查报告相对链接全部存在，`git diff --check` 通过。验证未调用目标函数、未仿真分支、未做输入回放或异常验证。无未知厂商字位于本轮解码窗口；此结论仅限这些窗口。

恢复程度：三个核心范围的局部合同接受，附上述图标调用边界记法纠正；已在 A15 原报告对应操作数处精确改为 `load32(context+0x20)` 并加 A16 引用，未改其余语义。整个大构造器、所有天气订阅者、注销/销毁、异步对象存活、下游渲染/图标实现、库版本与厂商改动仍未知。建议后继只选回调在 `a00ab6ea` 调用的 `a008ce16(arc,current)` 正常参数/字段/返回合同（最多一个直接依赖）；这是当前温度的另一个首消费点，未在 A15/A16 展开。先查既有成果避免重复，不重复已复核的 range consumer，不扩图标或 UI 生命周期。
