# A15：一个屏保天气订阅者及首个数据消费点

2026-10-23，基线 `92c9d2e`。本轮闭合一个局部链：`a00a7766` 内 `a00a7fc2` 注册 `a00ab6b0`，五槽分发以 `callback(data,user_arg)` 调入，回调把天气最高/最低温交给 `a008ce90`（ROM 名称 `lv_arc_set_range`）。只恢复注册分支的必要片段、该回调及首个 consumer 三个核心，不宣称恢复整个屏保构造器或天气 UI。

严格静态：未运行固件、连接设备/服务、验证缺陷、修改 ROM/生产代码/分析器模型。本轮只写独占报告/分析目录，没有新增哈希或复制 inventory；未开启共享可写 REA 会话。

## 入口与证据

- [weather-dataflow](weather-dataflow-0041-20261023.md) 已恢复五槽表 `62fcc370`、缓存、同步发布及双参数 ABI；其后续 weather-location、scheduling 报告没有恢复本次回调。对现有 `reverse/reports` 搜索 `a00ab6b0/a00ab754/a00b5cd4/a00a7766`，仅发现 `a00a7766` 屏保资源映射及 whole-ROM 的模型局限，不能视作本次语义已经完成。
- 原注册入口留存 `weather-dataflow/.../retained-functions.json` 的 `a00b3a68`，Evidence `ev_37f69171866916d2577d307574b9c125d6b82edabd9664fdb0b248cac14eea5b`，给出四个直接注册引用：`a005e1fc/a005e8dc/a00a7fc2/a00b8bc2`。本次仅取第三个，不推导全部订阅者。
- 具体调用者复用主仓库只读 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-064.json`，Evidence `ev_ac8900d80eb4c1a9ced9d9652a8a87e8406ef2059cabd2cb59272c0dfa080845`。分析参数是 `a00a7766`；只摘取本次注册所需片段，见 [retained-registration.json](../../analysis/weather-subscriber-a15-0041-20261023/retained-registration.json)。原反编译有 `unaff_s9`，故以原指令 `a00a7d58: mv s9,a0` 及后续 word 写确认局部联系，不扩大认证其完整控制流模型。
- [instruction-windows.json](../../analysis/weather-subscriber-a15-0041-20261023/instruction-windows.json) 留存 7 个限定窗口、原字节、文件偏移与 Capstone RV32C 解码；[strings.json](../../analysis/weather-subscriber-a15-0041-20261023/strings.json) 为 ROM 名称/路径原文。代码和所列字符串映射均为 `file_offset = VA - a0000000 + 1000`，不是直接拿 VA 低位作偏移。
- 原件只读绝对路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；身份沿用既有报告/留存 Evidence 的 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重新计算清单。

## 一个具体注册分支

这是 `a00a7766` 大函数内部的屏保子分支，不是新发现的独立函数入口。ROM 回调日志名为 `lv_ui_ssr_tim2_update_wx_data_cb`；调用者的大函数含多个屏保构造分支，不能由一个地址统一命名整函数为 tim2 constructor。

正常局部门：`a00a7d42..7d44` 比较进入此处的 `s8` 与 2，不等跳回 `a00a7996`。相等后以 `s3` 作 `a0` 调 `a00d91c6`，返回指针于 `a00a7d4e` 保存 `s1`；非零才继续。随后 `a00a7d52..7d5a` 以 0x14 调 `a008e362`，返回保存 `s9`，非零才去 `a00a7d70`；再以 0x28 调同函数，返回保存 `s2`，非零才去 `a00a7da8` 的正常构造段。这里仅证明两个分配形状的参数/返回与非零门，不展开分配器、失败分支，也不认证 `s8` 的原始枚举名。

`a00a7f52` 创建控件的返回在 `a00a7f56` 以 word 保存至 `s2+0x18`，构造 helper 内部不展开。注册附近原指令：

```text
a00a7fb8  lui a0,a00ab       a00a7fbc  mv a1,s1
a00a7fbe  addi a0,a0,6b0    a00a7fc2  jal a00b3a68
a00a7fca  sw s2,4(s9)       a00a7fce  sw s8,0(s9)  // s8 此时已是 0x2f
a00a7fde  sw s9,0x10(s1)
```

所以注册参数确定为 `(a00ab6b0,s1)`，不是全局缓存或 `s2`。注册之后才把 wrapper 的 `{kind=0x2f,context=s2}` 和 `object+0x10=wrapper` 接上。这个顺序是静态事实；没有据此推导运行时回调交错、对象已经可见或销毁安全性。既有注册器只填首个空槽且没有可靠成功返回合同；本调用点也不检查返回值，因此不能保证本次实际插入了表。

## 回调 ABI、字段宽度与借用边界

五槽分发的独立复核窗口 `a00b3c14..3c24`：`lw a5,0(s1)` 取函数，`lw a1,4(s1)` 取参数，二者均经过非零门；`a00b3c1c: mv a0,s3` 把发布的原数据指针放入 a0；`a00b3c1e: c.jalr a5` 调用。没有隐式第三参数。既有 handler 先复制缓存再同步分发，但此调用仍传原输入，不改成缓存。

`a00ab6b0..b753` 为本次完整回调窗口。入口只检查 `a1`（user_arg），为零直接返回；否则：

| 指令地址 | 操作 | 局部合同 |
| --- | --- | --- |
| `a00ab6c0/6ca` | 两次 `lw` | `wrapper=*(user_arg+0x10)`，`context=*(wrapper+4)`，均为 RV32 word 指针 |
| `a00ab6c2/6c6` | `lh a2,8(a0)` / `lh a1,10(a0)` | 最高/最低温各读取 16 bit 并符号扩展到 32 bit |
| `a00ab6cc` | `lh s2,12(a0)` | 当前温度同样符号扩展 |
| `a00ab6d0` | `lw s3,28(a0)` | icon_a 为完整 32 bit；不解释完整图标转换 |
| `a00ab6d4..6dc` | 有符号 `blt low,high` | 严格 low < high 时保留；否则范围改为 low=-60、high=60（不是钳制原始天气对象） |
| `a00ab6e0/6e2` | `lw a0,24(context)`；调用 `a008ce90` | 首个天气数据消费调用 `(arc,low,high)` |

这也把此前天气布局中 +8/+10/+12 的有符号温度解释进一步加强为**此订阅者的指令事实**。不是声称生产 JSON 转换保留了原始数值范围。

回调在首次下游调用前已把四个天气字段读入寄存器，完整回调没有存储输入天气地址、没有 memcpy 天气对象、没有写入天气对象。本地仅复制标量并立即消费；这支撑同步借用合同，不证明下游 helper 的全部所有权或其他订阅者行为。`a0` 输入非空由当前发布链提供，回调本身没有额外数据非空门。

首消费点之后的调用仅作为边界记录：`a00ab6ea -> a008ce16(arc,current)`；按 current 的符号选择字符串后 `a00ab6fc -> a019d0ae`，`a00ab70c -> a0091ee4(text,format,current)`；`a00ab714 -> a0198946(context+0x20,icon_a)`，最后日志。它们内部不计入本次恢复，不展开图标/文本/UI 生命周期。回调无经调用者使用的返回值；末尾经日志/恢复寄存器返回，不承诺 a0 为 0。

## 首个 consumer：a008ce90

ROM 中直接引用 `.../lvgl/src/widgets/arc/lv_arc.c` 与函数名 `lv_arc_set_range`。完整限定窗口 `a008ce90..cf09` 无未知或厂商指令。此函数正常路径以 a0 为控件、a1 为有符号 32 bit min、a2 为有符号 32 bit max：

```c
// RV32 存储视图；分析命名，非原始源码。
void callback(const uint8_t *weather, uint8_t *object) {
    if (!object) return;
    uint8_t *ctx = load32(load32(object + 0x10) + 4);
    int32_t high = load_s16(weather + 8);
    int32_t low  = load_s16(weather + 10);
    int32_t temp = load_s16(weather + 12);
    uint32_t icon = load32(weather + 28);
    if (!(low < high)) { low = -60; high = 60; }
    arc_set_range(load32(ctx + 0x18), low, high); // a008ce90
    // 后续 temp/icon 消费调用保留为上述边界，不展开实现。
}

void arc_set_range(uint8_t *arc, int32_t low, int32_t high) {
    // ROM 的非空门/诊断路径原样保留；本段仅描述正常对象路径。
    if (load32(arc + 0x44) == low && load32(arc + 0x48) == high) return;
    int32_t value = load32(arc + 0x40);
    store32(arc + 0x44, low);
    store32(arc + 0x48, high);
    if (value < low) store32(arc + 0x40, low);
    value = load32(arc + 0x40);
    if (value > high) store32(arc + 0x40, high);
    a008ccd2(arc);  // 直接更新依赖，内部未展开，不能冒称已经绘制到屏幕。
}
```

字段写是 `c.sw`（32 bit），不是把天气 halfword 原样写成 16 bit。`a008cede/cee4` 判断两范围字段是否相同；`a008ceea/ceec` 写边界；`a008ceee/cef6` 为有符号比较后条件写 `+0x40`，`a008cefc` 调 `a008ccd2`。参数先 low 后 high，未把回调读取的 +8/+10 顺序误当实参顺序。此函数不接收天气地址。返回值未被本调用者使用，不给稳定数值返回合同。

## 来源、恢复程度与实际验证

注册/回调日志指向 `lv_power_ui/lv_ui_scr_saver.c`，支持厂商 UI 胶合职责；未获得原始源码或精确版本。`a008ce90` 的路径/名称和布局支持 LVGL arc 候选归属，但本轮没有本地源码版本或未修改实现认证；不新增开源排除。三个核心范围的局部语义已恢复；整个 `a00a7766`、天气模块、全部订阅者与生命周期仍部分恢复/未知。

运行 [verify.py](../../analysis/weather-subscriber-a15-0041-20261023/verify.py) 通过，结果见 [review-index.json](../../analysis/weather-subscriber-a15-0041-20261023/review-index.json)：7 窗口/412 B/138 条完整 Capstone 指令；逐条字节与只读 ROM 相等；41 项独立原编码核验覆盖天气 lh/lw、上下文 sw/c.lw、arc 范围 c.sw、7 个直接调用目标及关键分支/间接 ABI 编码；34 条留存注册指令与本次窗口边界一致；6 条 ROM 字符串原文相等。`verify.py` 仅对静态字节做解码和断言，没有运行目标、仿真或回放。报告相对链接与 `git diff --check` 通过。

未知：未认证注册器实际插槽成功、s8 原始模式枚举、对象/上下文在异步调度中的存活、注销/销毁、图标处理、arc 下游更新/渲染、库版本及厂商改动。建议后继只独立复核本次注册切片、双参数 ABI、signed-halfword 到 word range 的首消费合同；不要扩展全量天气 UI。
