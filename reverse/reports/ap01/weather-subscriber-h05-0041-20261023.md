# H05：0041 weather1 页面注册、主要天气消费及 DELETE 归还

2026-10-23，基线 `8a7807ec63348db2f2751d05d7f754e2844c698a`，分支 `codex/re-0041-h05`。按共同规则和 H05 任务书，使用 reverse-engineer-anything 技能，只做原 ROM 静态读取。结果为待独立技术复核的局部恢复，不自称验收通过。

结论：`a005e8dc` 是包含函数 `a005cc1e` 中 weather1 构造分支的调用点，真实登记键是 **`(a00abed2,page)`**。该 callback 通过 `page+0x10 → wrapper+4 → ctx` 找控件，消费当前温度、最高/最低、体感、当前 icon、日出及日落。真实 DELETE hook 是 **`a00abb62`**：依原序清 ctx 的前 16 个 word，**释放 ctx**，注销完全相同 callback/page 键，再释放 wrapper 并清 `page+0x10`。这不是 H01/H03 的 type19 详情页，也不能把这里明确的 ctx free 移植到 type19。正常上层动作如何最终送达此页 DELETE，仍止于精确断边。

## 范围、原件和来源

先检索全部天气报告及 analysis 的 `a005e8dc/a005e8/a005e1`。A15 仅恢复第三个登记点 `a00a7fc2`；H01/H02 恢复 `a00b8bc2`；A19 末尾只将 `a005e8dc` 列为未知候选。本轮并非重复已有订阅者。worktree 祖先和目标目录没有发现适用 AGENTS.md。不写共享索引、生产代码、ROM、模型或其他树；不打开/切换共享可写 REA 会话，不创建下级 agent。

原件只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，沿用已认证 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射 `file_offset=VA-0x9ffff000`。不另建哈希或复制清单。

历史 [whole-ROM inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json) 定位 `a005cc1e..a005eeb9` 的 provider body，extent Evidence `ev_1eda51b6357d5f686016de2a849770230b4026b4a8f49f1a4bb12d083a26240a`；其 dossier `ev_2f6c46cd278b33760dc15702309279178fd3b14a0bef128e4814088addec2866` 仅作为历史定位来源，未将整个 8860 B 函数当作本轮已恢复。`a019cbc0..a019cd13` 的 extent Evidence `ev_95e4ca2c57f740c237a543d7ae18c554a01f1775833e32478b6a7e1f401d0fee` 辅助核范围。`a00abed2/a00abb62` 用实际回调常量、分支、栈帧与返回确定入口，不凭相邻 inventory 名称拼接。

本轮 [verify.py](../../analysis/weather-subscriber-h05-0041-20261023/verify.py) 从原件直接取字节，Capstone 5.0.7 解 RV32/RV32C；另独立提取 LH/LHU/LW/SW、JAL、地址常量、资源常量及关键 ABI 编码。逐指令地址、文件偏移、原字节、新解码、84 项编码检查和 ROM 字符串见 [instruction-evidence.json](../../analysis/weather-subscriber-h05-0041-20261023/instruction-evidence.json)，便读列表见 [instructions.txt](../../analysis/weather-subscriber-h05-0041-20261023/instructions.txt)。这些本地文件不是新造的 REA Evidence ID。

本题核心/必要短依赖为以下六个新恢复入口及三个既有合同边界；只恢复构造必要片段、主要 callback 和直接图标 setter，不扩整个 UI 初始化、天气网络或其他订阅者。

| 入口 | 本轮合同 |
| --- | --- |
| `a005cc1e`，仅 `cfd8..cff7/e4e6..e523/e8d2..e909` | 创建 page、20 B wrapper、68 B ctx，失败原序，登记和事件挂接；包含函数整体返回不认证 |
| `a00abed2..a00abfe5` | `(a0=data,a1=page)`；page=0 直接返回；主要字段及直接消费者；无被分发者使用的返回 |
| `a00abb62..a00abbf5` | `(a0=event)`；仅 DELETE 码进入，清 ctx/free/注销/free wrapper/脱挂 |
| `a019cbc0..a019cd13` | `(image,icon_word)`；沿用分类器，移除隐藏位，选择特定 ROM 描述符或重新隐藏；调用者不查返回 |
| `a008e362..a008e38b` | `(size)`；下层分配非零后零填充相同 size，返回原分配结果 |
| `a0080d8e..a0080da5` | `(ptr,size)` → 下层零填充适配；不认证下层库来源 |
| `a00b3a68/a00b3abe` | 首空尝试登记/首个双 word 同键匹配注销，沿用 weather-dataflow/H02；本轮只核调用实参 |
| `a00b3be6` 的 `a00b3c14..25` | 重核同步 `callback(data,userdata)` 双参 ABI；返回不消费 |
| `a008ab8a` | 归还适配，沿用 E01/H04 既有合同；本轮核三次 free 的真实参数，不重做分配器 |

## 构造与所有权

`a005cfd8..cfec`：`a00d91c6(s4)` 创建的对象保存为 s5（page）；返回零跳到后续其他构造分支。非零时 `a008e362(0x14)` 返回 s8（wrapper）；非零跳到 `a005e4e6`。wrapper 分配零时 `a00d7806(page)` 后置 s5=0；`a00d7806` 沿用 H04 的 class walker 身份，不能把这一臂简写为完整公共删除或宣称对象已彻底归还。

`a005e4e6..e524`：`a008e362(0x44)` 返回 s2（ctx）。零分支日志后按原序 `a00d7806(page)`、`a008ab8a(wrapper)`，随后跳到后续构造分支；正常非零继续配置页面与构造控件。这里只保留失败控制流，不执行失败验证，也不自行修正原行为。

成功尾部原指令：

```text
a005e8d2 37c50aa0  LUI a0,a00ac000
a005e8d6 d685      MV a1,s5                    ; page
a005e8d8 130525ed  ADDI a0,a0,-0x12e           ; a00abed2
a005e8dc ef50c518  JAL a00b3a68
a005e8e0 9147      LI a5,4
a005e8e2 2320fc00  SW a5,0(s8)                 ; wrapper.type=4
a005e8e6 23222c01  SW s2,4(s8)                 ; wrapper.ctx
a005e8ee 23a88a01  SW s8,0x10(s5)              ; page.wrapper
a005e8f2 8146      LI a3,0
a005e8f4 13069002  LI a2,0x29
a005e8ea/e8f8     LUI/ADDI a1=a00abb62
a005e8fc 5685      MV a0,s5
a005e8fe/e902     AUIPC/JALR a01ad654
```

登记在所有 wrapper/page 挂接写入之前，调用者不检查插槽成功，不把尝试注册写成保证注册。随后事件安装实参是 `(page,a00abb62,0x29,0)`。wrapper 20 B 中仅 `+0 type`、`+4 ctx` 属本链；剩余12 B 不补造语义。ctx 分配68 B，主要消费者使用下表前64 B中的控件字段；尾 `+0x40` 不在本 callback 或 DELETE hook 的访问集合中。

| ctx word偏移 | 本轮观察到的职责 |
| --- | --- |
| `+0` | 当前温度文本的对齐参照对象 |
| `+0xc/+0x10/+0x14` | 温度数字及相邻两个控件；三次重新读取数字对象作对齐参照 |
| `+0x18/+0x1c` | 最高/最低文本、体感文本 |
| `+0x20/+0x24` | 图标对象、天气描述文本 |
| `+0x28/+0x2c` | 日出/日落文本 |
| 其他 `+4/+8/+0x30/+0x34/+0x38/+0x3c` | callback不读；DELETE按原序清零，不能凭此命名 |

ROM `a01c42a0` 为 `lv_page_ui_weather1_create`，callback 名称 `a037bce8` 为 `lv_ui_weather1_update_wx_data_cb`，对应日志和 `lv_power_ui/lv_ui_theme.c` (`a01c3b98`) 支持 weather1 厂商 UI 胶合职责；不是依据 type4 数字猜 UI 名称。

## 主要 callback 与数据借用

以下是定宽存储视图和分析命名，不是原源码；所有数值在调用任何文本 helper 前已按原指令取入保存寄存器。

```c
void weather1_cb(const Data *d, Page *p) { // a00abed2
    if (p == 0) return;
    Wrapper *b = LW(p+0x10);
    uint32_t icon = LW(d+0x1c);
    int32_t feels = LH(d+6);
    Context *c = LW(b+4);
    int32_t high = LH(d+8), low = LH(d+10);
    uint32_t rise_h=LHU(d+14), rise_m=LHU(d+16);
    uint32_t set_h=LHU(d+18), set_m=LHU(d+20);
    int32_t now=LH(d+12);
    label_fmt(LW(c+0x0c), "%d", now);                   // a0091ee4
    align(LW(c+0x0c), LW(c+0x00), 1, 20, 70);          // a00dbb68
    align(LW(c+0x10), LW(c+0x0c), 3, 12, 0);
    align(LW(c+0x14), LW(c+0x0c), 3, 46, 0);
    label_fmt(LW(c+0x18), "最高: %d 最低: %d", high,low);
    label_fmt(LW(c+0x1c), "体感温度: %d", feels);
    a019cbc0(LW(c+0x20), icon);
    a00a6d34(LW(c+0x24), icon);                         // 描述选择；内部未新恢复
    label_fmt(LW(c+0x28), "%02d:%02d", rise_h,rise_m);
    label_fmt(LW(c+0x2c), "%02d:%02d", set_h,set_m);
    log_update();
}
```

`a00abef2..bf14` 是实际 LW/LH/LHU；没有截 icon 成 halfword，也没有将日出/日落 unsigned halfword 当 signed。高低温在本 callback 没有 A15 arc 的 `low<high` fallback；不引入其他页的条件。显示字符串原字节分别来自 `a06130bc/a01c3cb4/a01c3ccc/a0564a9c`。`a00abf5a/5c` 确认为 `a3=low,a2=high`；日出/日落分别 `a2=hour,a3=minute`，保持 variadic ABI。各消费者的返回均不作为业务成功门，不能说返回即已经物理绘制。

数据指针不保存到 ctx/槽/堆中；本 callback 只同步借用 d 并加载数值，没有 H01 那样的天气结构复制或栈重排。上述控件指针每次按原序重新 LW，未将三次数字控件读取合并；weather字段是在调用前逐项读取的寄存器值，不宣称并发一致快照。控件 setter 内部是否复制格式化文本，由各 helper 合同决定，本题没有把输入借用等同字符串持久借用。

## 直接图标消费者的限定核对

`a019cbc0` 是本页真实 setter，不是 A19 的 `a0198946`。它先 `category=a00a6998(icon)`，再 `a00d9044(image,1)` 移除隐藏 bit0；分类器和 flag helper 沿用 A19 已核合同，不重做天气 code 分类或 PNG info。随后 category 的精确行为如下，ROM 地址通过 LUI/ADDI 原编码核对：

| category | 传入 `a00ed560(image,src)` 的 ROM 描述符 |
| --- | --- |
| 1 / 2 / 3 / 4 | `a0251fd4 / a063461c / a0633960 / a0633f50` |
| 5 / 6 / 7 / 8 | `a06318b0 / a06315bc / a0631f78 / a0632308` |
| 9 / 10 / 11 / 12 | `a0632968 / a0636644 / a0636130 / a06334ec` |
| 13 / 14 / 22 / 23 | `a06330b8 / a0631c68 / a0634fe4 / a0635878` |
| 15 | 不调用 image setter，改调 `a00d8f7c(image,1)` 重新隐藏 |
| 其他 | 移除隐藏位后直接返回，保留既有 source，不补造 fallback 资源 |

这些是16个静态源指针，不是复制/分配的图片数据；source/header解析沿用 A19/A20 的 setter/PNG info 合同。本轮不对资源做 PNG 解码/执行/CRC 重复验证，也不把静态 src 选择推成屏幕已显示。`a00a6d34` 在本页接收相同完整 icon word，只确认它将描述交给文本 setter 的既有调用角色；其1088 B分类文本决策树未在本题新恢复，不以名称假称全部覆盖。

## DELETE、注销和归还次序

`a00abb62` 按 `(LW(event+8)&0xffff7fff)==0x29` 进入；不是泛化为截16位。页面是 `LW(event+4)`；wrapper是 `LW(page+0x10)`，为零直接返回。非零才取 `ctx=LW(wrapper+4)`，不另加ctx非零门。

```c
void weather1_delete(Event *e) { // 分析伪代码
    if ((LW(e+8)&0xffff7fff) != 0x29) return;
    Page *p=LW(e+4);
    Wrapper *b=LW(p+0x10);
    if (!b) return;
    Context *c=LW(b+4);
    for (off in original_order) SW(c+off,0);
    a008ab8a(c);                   // a00abbcc；实际a0仍为ctx
    a00b3abe(a00abed2,p);         // a00abbda；同双word键，首匹配清槽
    a008ab8a(b);                   // a00abbe0；a00abbde MV a0,s2
    SW(p+0x10,0);                  // a00abbe4
}
```

clear 原序（十六进制偏移）：`1c,34,08,10,14,00,0c,30,28,2c,04,24,20,18,38,3c`，集合恰覆盖前64 B的16word；`+0x40` 未先清零，但 ctx 整块传给归还适配。本链的 free(ctx) 有直接原实参支撑，不是从清零动作推断。保留 **先free(ctx)再注销** 的原顺序，不改写成先安全脱挂或其他重排。

订阅槽持有 page，不直接持有 ctx；page 持有 wrapper，wrapper 持有 ctx。注销器仅清第一个完全匹配的 callback/page 双word槽，无去重/全部实例注销承诺；注册器无可消费成功返回。ctx和wrapper显式归还不等于page自身已free，清ctx控件地址也不等于删除这些widget。页面/控件归还由外层对象树删除框架负责；H03/H04的通用递归合同可作既有边界，但本题没有证明 type4 的具体正常根导航链已经走到该框架。

精确断边/有界范围：检查本登记的 page/wrapper创建片段、ctx分配/失败片段、成功登记与事件安装尾部、完整callback、完整DELETE hook、直接icon setter与分配短适配，并查看所在 `a005cc1e..a005eeb9` 的局部导航关系。没有搜索整个UI根退出、所有DELETE incoming、E05 app注销或所有allocator别名。已证退出入口是 **安装在此page的 `a00abb62(event*)`**；尚未连上“哪一个正常用户动作/根对象删除最终向此page送达0x29”，因而不以已安装回调推运行时执行，也不将E05根DELETE直接拼接到此page。无需重复H03的ctx最终free有界检索。

## 事实、推断、未知与实际验证

事实是原字节、真实调用地址、参数次序、LH/LHU宽度、重新读取顺序、登记与注销键、ctx/wrapper挂接与free实参、事件mask和category源常量。weather1名称有原日志支持；温度/日期业务字段沿用weather-dataflow生产布局，DELETE名称沿用已验收LVGL事件合同。图标物理显示、实际槽占用、全局退出动作、通用widget对象最终归还和allocator内部行为未由本轮运行观察证明。

来源：厂商UI胶合与LVGL toolkit候选由ROM路径、日志、调用结构支持；未认证精确上游版本或厂商未修改。分配/零填充/文本/image适配保留明确边界，不因看似标准而从范围静默排除。新增已认证开源排除为0。

实际运行 `python reverse/analysis/weather-subscriber-h05-0041-20261023/verify.py`：**pass，10窗口、1058 B、355条指令、84项原编码检查，未解码指令0**，见 [review-index.json](../../analysis/weather-subscriber-h05-0041-20261023/review-index.json)。所留选定窗口没有厂商opcode；未靠反编译补厂商语义。探索时曾在半字中间开始解码、临时脚本名与Python inspect模块冲突；改正确窗口和文件名后重新通过。首次verifier尝试完整既有注册器遇厂商指令，按既验收合同仅针对核改留callsite/dispatch片段，没有跳过未知指令冒充完整解码。没有执行目标、模拟器/设备、外连、异常输入/缺陷验证、历史回放或项目编译。

恢复程度：一个新订阅者的构造登记→主要callback/直接consumer→已注册DELETE中的ctx/wrapper归还和同键注销已恢复；正常上层离页动作保持上述精确断边。建议唯一后续闭包先由新agent独立技术复核这些新入口、free先于注销、双参数ABI与16word原序；后续根退出追踪须保持E05根对象身份未完全闭合的限制，不扩全天气/UI。
