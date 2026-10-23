# H02：天气详情页生命周期独立复核

2026-10-23；新 agent 独立复核，分支 `codex/re-0041-h02`，基线 `c9336de77a7a349614049e6edf065ff42fbaa78b`。结论：**H01 所述订阅→同步重排→当前/七行消费→同键注销及 wrapper 清理，限定接受，无核心语义纠正。** context 最终释放、上层离页如何产生事件和控件递归析构仍未核。接受的是已恢复的指令合同，不是页面完整堆回收或运行时成功证明。

使用 reverse-engineer-anything 技能，读取共同规则、H02 完整任务书、[H01](weather-subscriber-lifecycle-h01-0041-20261023.md)、[A16](weather-subscriber-review-a16-0041-20261023.md)及[A17](weather-current-consumer-a17-0041-20261023.md)。检查 worktree 祖先和目标目录，未发现适用 AGENTS.md。没有改 H01、共享索引、生产代码、ROM 或分析器模型；没有打开或切换 REA 全局 target/数据库。

## 原件、方法与独立证据

原件只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`；身份沿用既有 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不新增散列清单。映射 `file_offset=VA-0x9ffff000`。

本轮[verify.py](../../analysis/weather-lifecycle-review-h02-0041-20261023/verify.py)直接读取 ROM，用 Capstone 5.0.7 重新解码 RV32/RV32C；对 JAL、I/S 型访存、compressed move/branch、函数地址 LUI+ADDI 和厂商字自行提取位域。没有执行或导入 H01 verifier，也没有把 H01 汇编文本当成新解码来源。新解码后再与 H01 所留 647 条原字节比较，全部一致。普通解码器不认识的厂商字先按原 word 分类，随后读取原主仓库只读 `ap01thead2.sinc` 的确切六个规则核语义；没有靠厂商助记符猜字段。

[review-evidence.json](../../analysis/weather-lifecycle-review-h02-0041-20261023/review-evidence.json)保留本轮实际检查、选定决定性指令的地址/文件偏移/原字节、新解码、14 条厂商字位域、六条 profile 规则和三个 ROM 字符串。为避免机械复制完整旧证据，仅留决定窗口，完整解码覆盖在该文件 `decoded_ranges` 中列明：构造前缀/尾部、注册与注销、完整删除 hook、分发 ABI 窗口、完整主要消费者、重排和短 callback、完整星期 helper，共 8 个连续范围、647 条指令。

H01 的六份 retained dossier 只作为被复核对象及历史来源：注册 Evidence `ev_37f69171866916d2577d307574b9c125d6b82edabd9664fdb0b248cac14eea5b`，注销 `ev_b01c9bd1363658594f90e3d063fff42fc67f5732cd4d251f613d2808b8fe1ee0`，消费者 `ev_b35fd250fe92c17c7cc51c60e047baf7f66743489971ddd848c58484029d0fd3`，重排 `ev_710cdcdc3b7c65ca0e83b59cf3a93487360aca60057d05836a5a292ba6cee08e`，构造 `ev_1918e8f911a15a34dfeb3de693941a3f265dd1f809986850f3786b407ef8563e`。本轮新结论的主证据是原 ROM 和上述独立验证结果，未新建伪称 REA Evidence ID。

## 逐项判定

| H01 主张 | 判定 | 本轮原指令依据与边界 |
| --- | --- | --- |
| `a00b8bc2` 为 `a00b821e` 内部注册调用点 | 接受 | 前缀 `821e` 建栈，`8240` 保存 page=s1；尾部 `8bb4/8bbe` 合成 `a00b5cd4`，`8bb8` 将 s1 放入 a1，`8bc2` 的 JAL 目标为 `a00b3a68`。未把调用点当函数入口，也未恢复整个控件构造体。 |
| wrapper 0x14/context 0x74 分配及失败原序 | 接受 | `8244` 置 a0=0x14、`8246` 调 `a008e362`；失败 `824e/8250` 以 page 调 `a00d7806` 后置 s1=0返回。`8276/827a` 分配0x74，失败臂先日志、`82a4/82a6` 删除 page、`82aa/82ac` free(s4=wrapper)，再经 `82b0→8254` 置返回0；不颠倒 delete/free，不声称失败时已注册。分配器/删除器内部未核。 |
| 注册先于 wrapper 挂接 | 接受 | `8bc2` 后才 `8bd8` 写 ctx+0x70 byte，`8bde/8be2/8be6` 写 type=0x19、ctx 与 page+0x10；`8bf4` 安装 `(page,a00b3b26,0x29,0)`。未检查注册或事件安装返回，不能保证实际有空槽或 hook 安装成功。 |
| 真正 callback 是 `a00b5cd4(data,page)` | 接受 | `5cd4` C.BEQZ 的 rs1'=a1，目标 `5cea` 直接返回；非零时 `5cde` JAL 到 `a00b5b58`，此前仅建栈保存 s0/ra，未改 a0/a1。`3c18/3c1c/3c1e` 是取 userdata→a0=data→间接 JALR，限已验收双参数合同。没有额外 weather 指针检查或稳定数值返回。 |
| userdata/page/wrapper/context 不能混同 | 接受 | 注册 a1=page；`5b84` 读 page+0x10，`5b96` 读 wrapper+4为 ctx；最后 `5c7c/7e/80` 形成 `(a0=ctx,a1=page,a2=view)`。没有直接把 ctx 注册进槽。 |
| 当前块先复制，再重读源；六日先复制再重排 | 接受 | 七个 JAL 均到 `a000589c`：当前36 B、六个未来块各20 B；`5b9e..5bd8` 在首次复制后重新从原data读日期、温度和icon；六块来源依次data+0x24/+0x38/+0x4c/+0x60/+0x74/+0x88。保留读取/复制顺序，不能合成一次一致快照。copy-like函数内部沿用旧合同，来源未认证。 |
| view 是借用的栈输入 | 接受，限直接存储/调用 | `5b86` 将 s4=s0-0xc4，`5c7c` 把该地址作为 a2传给消费者，随后日志、恢复栈返回；未见将原data/view写进ctx或订阅槽。输入天气总长156 B=36+6×20；显示view有效读写最高为+0x92的halfword，即至少148 B，二者不应混称同一布局。H01没有把156 B写成已证实view分配尺寸，此处明确区分。下游通用文本函数是否内部复制字符串未重做。 |
| future icon 的厂商存储寻址 | 接受 | `5c38` s5=0x60-view；s2从view起每轮+2；`5c72` 原word `0x432ad78b`：srw rd=15,base=21,index=18,shift=1，EA=(0x60-view)+2×(view+2j)=view+0x60+4j，按RV32模数成立。不是双倍栈指针地址。循环由s2到view+12终止，正好六轮。 |
| 日期/星期和七行步长及符号 | 接受 | 星期helper两处分支调入同一 `a00eeae6`，DIVU/REMU而非有符号除法；输出SH。行对象由 `5930` lrw shift=2取；日期/星期 `596e/597e` lrhu shift=3；图标 `5998` lrw shift=2；最低/最高 `59ac/59be` lrh shift=1并符号扩展。i从0到6，i=0跳过日期/星期文本，图标模式1；i=1..6模式0。 |
| 当前图标第二参数为零扩展16位 | 接受 | `5736` 原 `8355c901` 为 LHU a1,28(s2)，`573a` C.LW a0,40(s1)，`5740` JAL `a0190da4`；a1在此前未被覆盖。`573c` 保存该word，`5744`重载后传给 `a00a6d34`，不能采信反编译漏参。预报图标则读完整word，并走另一个 `a00a6afa` 合同。 |
| 温度、日出日落、AQI/UV/湿度宽度 | 接受 | 当前温度/最高最低/体感 LH；日出日落两对LHU；AQI+0x18、UV+0x16、湿度+0x1a均LHU。三次arc调用目标都为 `a008ce16`，对象从ctx+0x30/+0x38/+0x40读入。湿度s3作为callee-saved寄存器保留零扩展word，普通文本分支 `58ee/591a` 是a2=s3，等100分支则显式a2=100。 |
| AQI与湿度分支/字体/对齐顺序 | 接受，限参数及调用 | AQI先arc、数字文本，再unsigned与99比较选两字体及y=12/17。湿度先arc、比较100，另路 `58c0` 减10再 `58c8` extu15..0，与89作unsigned比较；10..99与其余分支分别(-4,-1)/(-5,-1)，后缀共同(1,3)，100分支(-5,1)/(1,0)。这些是原调用参数，不认证实际屏幕排版效果。 |
| DELETE hook只清28word，按同键注销后free wrapper | 接受 | `3b26..32` 事件码&0xffff7fff==0x29；`3b42/44/4c` 取page、wrapper、ctx。28条SW zero集合恰为0..0x6c，原序见证据。`3bca`注销，`3bce` a0=s2，`3bd0` free，`3bd4` SW zero,16(s1)。s2仍为wrapper，ctx只在a5中作清零基址。 |
| 五槽注册/注销匹配合同 | 接受，针对核 | `3a7a`数5，注册先空callback槽；注销 `3ad6/3ada`比callback、`3ade/3ae2`比userdata，首匹配清两word后走返回；首参常量由两处独立LUI+ADDI都得到a00b5cd4，次参均page。未再恢复整个publisher，也不证明此次槽占用。 |
| ctx最终free、递归控件析构及离页触发 | 未核，保留断边 | 此hook的唯一释放参数为wrapper；清零不是析构。构造大函数和本次完整hook/callback消费者内没有证据连接上层导航到DELETE或ctx释放者，不对未搜索的全GUI作否定结论。 |

## 复核后的布局、ABI与状态伪代码

以下是分析存储视图，地址为RV32 word，不是原始C声明。`page+0x10→Wrapper{type32@0,ctx32@4,其余12B未核}`，wrapper分配20B。ctx分配116B：`controls[21]@0..0x50`、`rows[7]@0x54..0x6c`、`date_pending8@0x70`，尾3B未核。DELETE只写前112B，保留+0x70及尾部。

view当前块+0..0x23；当前日期四个u16在+0x24..0x2a，六日日期四元组在+0x2c+8j；七个icon32在+0x5c+4i；七个low16在+0x78+2i，high16在+0x86+2i。日期、icon和温度独立数组不是原天气156B布局。消费者把温度按signed16取出，icon32仅预报路径保留完整32位，当前主图标特意LHU截取。

```c
// 省略控件构造；调用原序不能重排。
page = create_page(original_arguments);
if (!page) return 0;
wrapper = alloc(0x14);
if (!wrapper) { delete_page(page); return 0; }
ctx = alloc(0x74);
if (!ctx) { log(); delete_page(page); free(wrapper); return 0; }
construct_controls_and_rows(page,ctx); // 仅本范围所需产出已核
register_weather(a00b5cd4,page);       // 不检查返回，未先挂wrapper
store8(ctx+0x70,construction_year==0x7b2);
store32(wrapper,0x19); store32(wrapper+4,ctx);
store32(page+0x10,wrapper);
add_event(page,a00b3b26,0x29,0);
return page;

callback(data,page) {                  // a00b5cd4，a0/a1 ABI
    if (!page) return;
    normalize_and_update(data,page);   // a00b5b58；不检查返回
}

normalize_and_update(data,page) {      // a00b5b58的0x140 B栈帧
    ctx = load32(load32(page+0x10)+4);
    view = stack(s0-0xc4); future = stack(s0-0x13c);
    copy_like(view,data,36);
    // 重读原data的日期、温度及icon；各six future先复制20B
    // 再依上列布局写数组，weekday输出截成16位；不持有原data。
    normalize_current_and_six_copies_in_original_order();
    a00b564e(ctx,page,view);            // 同步借用view
    log();                            // 不把a0当稳定返回值
}

delete_hook(event) {
    if ((load32(event+8)&0xffff7fff)!=0x29) return;
    page=load32(event+4); wrapper=load32(page+0x10);
    if (!wrapper) return;
    ctx=load32(wrapper+4);             // 原件没有新增ctx非空门
    for (off in original_clear_order) store32(ctx+off,0);
    unregister_weather(a00b5cd4,page);
    free(wrapper);                    // 不能替换成free(ctx)
    store32(page+0x10,0);
}
```

状态关系是“page已创建→wrapper已分配→ctx已分配及控件已构造→尝试注册→挂接wrapper→尝试安装hook”。已安装hook接收指定码且wrapper非零时，进入“控件地址清空→尝试移除首个同键槽→wrapper释放→page脱挂”；不能把该终态命名为ctx已释放。注册表借用page地址，天气数据由同步分发传入；本层栈复制不转移源所有权。DELETE和formatter/图标/arc底层是否另行持有资源，限已有合同而非本轮全库证明。

## 来源、验证与恢复程度

事实是原字节、参数寄存器、访存宽度、重读顺序、清理次序与实际free参数。字段业务名沿用已验收天气生产布局；星期业务名由公式与星期表消费推断，DELETE名称沿用既有LVGL事件合同。原ROM字符串 `a0561db8` 为 `lv_ui_wx1_dtl1_update_wx_data_cb`，`a0562020` 为 `j_ui_wx1_dtl1_update_wx_data`，`a037b710` 为 `lv_power_ui/lv_ui_wx1_dtl.c`，支持厂商天气页面胶合身份。部分日志正文仍写time1，不能单凭其文案另换函数身份。精确LVGL版本、厂商原源码和allocator/copy/通用格式化来源未认证；没有新增标准库排除。

实际运行 `python reverse/analysis/weather-lifecycle-review-h02-0041-20261023/verify.py`：**passed，647条原ROM指令、146项检查、14条厂商字**。检查含失败臂/正常路径JAL、复制次数、图标与湿度零扩展、清零集合、free实参、相同注册/注销键、view传参、两条厂商步长族及profile来源，H01所留原字节全部匹配。报告相对链接存在，`git diff --check`通过。检查只读并解码原件，不运行任何固件指令、仿真、历史回放或输入样例；未外连、未做漏洞/异常/设备验证，未编译项目。

复核闭包达到H02范围：一个订阅者的构造必要失败臂、注册、短callback、栈重排、主要当前与七行消费、DELETE同键注销与wrapper释放均有独立原字节支持。H01保留的ctx最终释放、离页事件触发、递归控件删除断边合理，未将其包装成已闭合。建议唯一后继为type=0x19页面的ctx所有权：从 `a00b3b26` 上层事件交付及wrapper类型分派追到最终释放或一个明确常驻边界，不扩全部天气订阅者或完整UI。
