# I01：启动 ready 替代背后的既有 ROM 条件

2026-10-24；基线 `92e733a`，独立分支 `codex/re-0041-i01`。**本题主体早已覆盖，新增功能恢复0。** 原启动callback不是等待一个硬件ready接口：它调用 `a009d7b4` 取得`ck_config/wifi_configured`对应缓存byte，并结合已恢复的端口活动word `62fc4034`、userdata byte计数及另一个启动标记决定完成分支。SIM固定2000ms是替代；不表示原ROM存在固定2秒硬件就绪合同。本轮只作旧证据整合、必要ABI/字段复核，补旧getter缺失的2B尾跳，不重导callback或扩硬件初始化。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读主仓ROM、旧证据和ZIP成员；无共享REA target/database，无固件、SIM、构建、历史回放、设备、外网、下级agent或生产代码/配置/模型修改。只写本路独占报告/analysis；未改其他任务或主树共享文件。以下伪代码是局部行为表达，不是原源码。

## 继承结论：已有出处→行为→局限→精确缺口

|已有出处|已有行为及证据等级|本轮处理|
|---|---|---|
|主仓`guide-complete-0041.json#/boot`；`bounded_local_disassembly/boot_timer_asm`、`boot_delete_asm`、`boot_cb_asm`|已有1000ms timer、userdata计数两次、a00a73fe完成、boot页面删除和callback正常条件原汇编|直接继承主体；“device-ready/no-device”只是旧替代语境简写，须对齐实际getter和word门|
|主仓`system-complete-0041.json#/local_disassembly/0xa00a73fe`|此key不只含a00a73fe，还含a00a7472..75e4 callback原bytes/普通指令；门、byte计数、configured分支与完成顺序已有|不因键名或近期报告未写就当新发现；只选必要39条旧锚点中的相应条目回源|
|同system的`local_disassembly/0xa009d7b4`|42条原bytes到d83a，含配置读取调用、返回判1、失败清缓存、U8返回|旧记录遗漏d83e尾跳2B；只补该跳至d812的返回合流，不重导140B函数|
|同system的`native_semantics/overview_gates/boot_final`及`local_disassembly/0xa00b2ea6`|configured→保留root预选；未configured→a00b2ea6/a00b2f48 index8已解释|全部继承，不重新恢复GUI/选择算法|
|[theme-total-state](theme-total-state-0041-20261023.md)、[theme-online](theme-online-0041-20261023.md)|62fc4034是活动位图word；在线callback可整word置1/0，item bit(i+1)更新；不是纯端口数量或一般指针|boot只判整word非零，不把bit0/所有位重新认证，不称物理device-ready|
|[buzzer-backlight-round2](buzzer-backlight-round2-0041-20261023.md)|a008c280原日志`lv_timer_set_repeat_count`及timer+10 word已闭|继承；boot中`a008c280(timer,0)`应写置repeat_count=0，不能说此call立即free timer|
|pass3第2892行；main-knob round2 records/1 `ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`|旧pass3已写`a008bc64(a00a7472,1000,one_byte_userdata)`；main旧callee已有a009d7b4范围|既有挂接行为/范围，不当新函数；本轮只核原寄存器实参|
|较晚round3 initial records/5 `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`；page-logic 24 records|round3已有62fc919c初始化相关references；page-logic精确本题地址词项无命中|有界复用，不将reference当writer完整合同，也不进入初始化/驱动；无命中不证明此前未分析|
|最终ZIP `tools/ap01/ap01-ui-guide.h:281..307`，尤其299行|SIM以`lv_tick_elaps(boot_start)<2000`阻止完成，随后置host boot/saver状态|明确是host替代源码；SIM验收/照片不能认证ROM原条件、硬件ready效果或真实时间|

四类证据分列：可靠旧原bytes直接引用；旧反编译/extent/refs只定位或需局部ABI校验；SIM/照片/替代只证明替代实现；本轮精确缺口只有旧getter尾跳及接入宽度/顺序的必要核实。boot creator/logo、timer库、计数算法和index8已闭，不重复算成果。

## 本轮复核或纠正

### 真实getter与返回值：已有条件的精确称呼

旧system bytes表明 `a009d7b4()`：

```c
// 只表达既有getter正常局部，不展开底层配置服务。
if (load_i8(0x62fc3fec) == 0) {
    rc = a0060946("ck_config", "wifi_configured", (void*)0x62fc919c, 1);
    if (rc != 1) store_u8(0x62fc919c, 0);
}
return load_u8(0x62fc919c);
```

`d7c2`是LB，后面只判非零，不是signed正值门；非零时跳过配置调用直接读缓存。`d7d4` a3=1、`d7d6` a1=`a01c3058`字符串wifi_configured、`d7da` a2=`62fc919c`、`d7de` a0=`a01c3068`字符串ck_config，`d7e2`真实JAL目标a0060946。下层返回**精确等于1**才保留读取结果；不能把它归一化成“任意非零成功”或把下层返回值当最终configured值。getter真正返回`d816 LBU`的缓存整byte，没有`&1`或bool归一化。

本轮不需要认证a0060946内部持久化/文件系统；相应旧whole-ROM已有historical dossier `ev_f42a44506e5d82db35927ec71aaf854d5a8e878c05c1f05b4f9619c58c2b9eb1`，并非无历史覆盖。本题只用它的真实调用ABI和caller比较。

旧记录在成功日志call `d83a`后截断；新增原字`d83e:d1bf`解为C.J到`d812`，后者恢复ra/s0、LBU返回cache、恢复s1/sp、ret。故成功、失败清0、非零bypass三条路径确实合流到同一返回，而不是日志call后落到下一函数。无厂商未知字，无新ISA模型。

### 挂接与完成顺序：都是旧行为复核

pass3已明确挂接；稀疏原字 `a005ce80..ce9b` 再核：以1调用a008e362取得P，a2=P，SB清P[0]，a0=a00a7472，a1=1000，`ce98`调a008bc64。callback `a00a7488`以LW从timer+0xc取P。P是独立1B userdata，不是root、设备对象或getter返回指针；不补分配安全门或扩大timer实现。

callback在`74d0`**先**把G+8 (`G=62fc402c`，地址62fc4034)的word保存为s4，随后`74fa`调用getter、`7502`保存返回为s7，日志调用后`751c`才按s7==0分流。因此端口word是本次callback提前取的快照；不改成getter之后再读。`74d8`的wifi-status byte只参与日志，本门并不据它判断硬件ready。

|既有正常分支|已证字段/动作顺序|
|---|---|
|getter缓存byte非零，端口word快照非零|`753e a00a73fe()`→`7542/44/46 a008c280(timer,0)`→`754a/4c a008ab8a(P)`→callback返回|
|getter非零，端口word快照为0|`7552` LBU P[0]，加1后`&0xff`，`755e` SB写回；值≤1返回，值>1转同一753e完成链。初始0的正常连续两次该分支才完成，不是所有输入/调度都固定2秒|
|getter为0|读byte `62fc909d`。非零时先SB `G+25=1`；为0时SB `G+c=1`后a00a5cea。之后重新LBU该byte给a00b2ea6→a00a73ac→同一a008c280(timer,0)→free(P)。index8选择与boot删除内部全继承system/guide|

`a00a73fe`已有设置`G+c=1`、a00a5cea、查找应用窗口及后续boot删除helper a00a73ac的合同；不在此重导。两个完成分支都在释放P前置timer repeat_count=0；callback没有直接free timer对象，未新增timer最终归还或调度器时序保证。P归还、boot窗口删除与timer对象生命周期是不同责任。配置getter只读/写持久缓存byte，不分配P或转移其所有权。

此处“ready”只表示这些原UI条件走到完成动作。配置是否真的对应已连网、端口word是否反映当前物理设备、服务何时更新和显示何时可见，都不能由本局部静态门证明。

## 真正新增与精确未闭边

- 继承结论：原timer/两次byte计数/完成helper/configured→index8/端口word/置repeat_count语义全部既有覆盖。
- 本轮复核或纠正：39个必要旧raw锚点与当前ROM一致；getter调用ABI、U8返回、snapshot原序和userdata挂接核实。术语收紧为“配置缓存与端口活动门”，不把通用ready当硬件接口；旧机器行为纠正0。
- 真正新增：**功能恢复0、完整函数导出0、开源排除0**。新增原件只有旧getter遗漏2B尾跳；另28B挂接窗口是旧行为原字复核，不计功能增量。
- 未闭精确边：`62fc3fec`缓存bypass标记的完整设置政策、持久配置实际更新时机、端口word全部writer/物理含义、真实timer调度/最终timer归还和硬件ready效果仍未知。round3对62fc919c的真实初始化writer references已有定位种子，但本题无需再恢复它；不把留存reference升级为其完整合同。没有剩余待恢复的本题callback正常条件，按覆盖收缩结束。

唯一后续闭包建议：如需独立验收，只核本题三条getter返回合流、配置byte/端口word与timer/P身份、repeat_count0→free(P)原序即可；不重做整个boot。若将来单立配置更新任务，可从round3 records/5现存`a005acf0`参数传递/`a005ad28`写62fc919c种子开始，当前不扩初始化/驱动。

[verify.py](../../analysis/boot-ready-increment-i01-0041-20261024/verify.py)只读主仓ROM、system/guide JSON与最终ZIP明确成员；结果 [evidence.json](../../analysis/boot-ready-increment-i01-0041-20261024/evidence.json)：39个旧raw锚点、67项原编码/宽度/目标/字符串/挂接断言PASS；新增getter尾跳2B、旧挂接复核28B，无厂商字。未导出整callback/getter、配置服务或资源；未执行固件/模型/时间输入。JSON解析、报告链接、git diff --check另行检查。这是作者静态自检，不冒称独立技术验收。
