# A67：reader mode2 open/编码H/close的非作者复核

**限定接受A66在J08/7的callback合同，语义纠正0、新增业务0。** mode2选flags数值1，以buf/256/literal `/%s\0`/首vararg pathSuffix交42B wrapper；callback不检查format返回，随后调用fd-open接口。非负fd按RV32低word编码H=fd+1；close以H−1交fd-close接口，非负结果折0，负结果在日志后重新取得错误槽/值再转换。H是数值编码，callback没有独立H对象或free(H)路径。

**格式输入与实际输出分开：literal/参数包是原字事实，斜杠前缀拼接只是printf-family意图推断。** formatter内部、实际buf字节/截断/NUL终止、路径解析/IO、错误转换和最终资源效果不在本复核。D槽绑定按派发条件由A64/A65独立维护，本body复核不前置接受slots或默认五照片mode1。

2026-10-24；非作者 `/root/f12`，任务A67挂原认领 **J08/7**；固定基线 `bd457a6`，独占 `re0041-a67` / `codex/re-0041-a67`。A66作者 `/root/a56` 已交付停止，主仓[唯一管理记录](rolling-management-0041-20261023.md)已登记本轮复核。遵守最新 [reverse-design](reverse-design.md)、[材料规则](../../analysis/README.md)及REA技能。

只写本报告、[独立源码](../../analysis/reader-driver-open-close-review-a67-0041-20261024/review.py)、[必要合同](../../analysis/reader-driver-open-close-review-a67-0041-20261024/contract.json)；[生成证据](../../analysis/reader-driver-open-close-review-a67-0041-20261024/evidence.json)忽略保留在本地原路径。不跑A66/历史技术脚本，不执行目标/指令/模型、固件、SIM/QEMU、构建、回放、文件/设备IO或外部服务；不读formatter下层/底层IO/errno-map，不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，无下级agent、提交或推送。

## 继承结论

|已有出处|已解释行为/实际边界|本轮处理|
|---|---|---|
|[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)|generic open `(D,pathSuffix,2)`、close `(D,H)`，后续cache条件归还/重读/清槽已有合同|不重做generic接口/缓存/O释放，也不把缓存free叫free(H)|
|[A64槽候选](reader-driver-slot-bind-a64-0041-20261024.md)、A65独立任务|候选D+c/10指向这两个body；A66及本题派发时绑定仍以待A65条件继承|只复核给定地址body，不代验D基址/盘符/slots。绑定状态后续由原行维护|
|[D03](uart-write-object-d03-0041-20261023.md)|0xa003f4f6是沿既验局部文件安装角色的fd-open接口，pathname/flags往下层传，返回数值fd有安装切片支撑；完整路径查找未认证|直接继承角色，不新读0xa003eb14/文件安装/allocator或把本次buf绑定到具体inode|
|[F05](miio-exit-callback-f05-0041-20261023.md)/[F06](display-exit-review-f06-0041-20261023.md)|0xa0026888的fd归还接口角色已解释，不能据接口调用认证最终file/device效果|直接引用接口，不读底层close/driver|
|[A66作者交付](reader-driver-open-close-a66-0041-20261024.md)|mode2、format接口、H编码、close/负分支getter重读|本轮只非作者核这些差集，不扩其他mode、read/seek/dir或source-path版本认证|

原件按 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；`file_offset=VA−0x9ffff000`，不套0031/unsigned/SIM。

旧whole-ROM index仅定位两callback，未有dossier：open extent EID `ev_d2a3ffd68947171f29dbeae7f5b129090a577519f71016d41e3e86ce5907b124`/directcall `ev_fab46098efe4f4c609b8f5518194fcd9642bc21919400810bf422759b5473bee`；close extent `ev_eefcffbc335d62e6fc648ef3d03f64439f8f89408f8d5aca56b5fb0f578be3b4`/directcall `ev_d9545331811dc9e76377715d9e2eea9ed2f7076f06b9cdb634769dc3b50fecc2`。ROM POSIX源路径只定位family，不认证精确版本/未改源码。本轮原字段与Capstone不产生新REA ID或重标旧profile。

## 本轮复核或纠正

独立检查器读取两callback共246B及wrapper42B，共 **288B**用于mode/负分支/原序与返回连续性，只保留 **140B必要锚点**；另读literal **4B**。**54项PASS**，普通指令用 **Capstone 5.0.7 / RV32+RVC** 解码，JAL、signed B-format、H的I-format±1和literal地址另独立位域解算；没有UNKNOWN、厂商模型或目标执行。没有运行或导入A66验证器。

|复核点/地址|独立接受的原字段与前提|
|---|---|
|mode2与suffix：0xa00ef476..486|s0为sp+0x110，原a1先移a3=pathSuffix；mode1门对mode2不成立，s1=1后mode2相等跳0xa00ef494。仅接受该mode2的flags数值1，不给它加正式宏名|
|buf/format界面：0xa00ef494..4a4|LUI/ADDI独立得format地址0xa06371e4；原件4B **2f257300**确为`/%s\0`。a1=256、a0=s0−0x110为本栈工作区、a3仍原suffix，调用0xa008ab4c|
|42B wrapper：0xa008ab54..ab74|先SW原a3到s0+0xc作为首vararg，再改a3=&saved-args，其余a4..a7顺序word保存；原buf/256/format通过到0xa0053252。wrapper尾声保留其a0，不新解formatter算法/完整variadic语义|
|不检format返回：0xa00ef4a8..4b2|format wrapper回来之后只有设置a2=0x1b6、a1=保存flags1、a0=同buf，然后调用0xa003f4f6。无比较/分支使用format返回；不是据此认证buf已形成预期pathname|
|fd→H：0xa00ef4b6/4ba/4fc|先a5=low32(fd+1)，再signed fd>=0门到返回尾声；返回a0=a5。H数据源是fd运算，非D字段、buf地址或独立分配的handle|
|open负分支：4be/4c2/4ea/4ee|先getter0xa00267c0→LW错误word用于日志接口0xa008b51a；其正常返回后显式a5=0再走H尾声。未假定日志一定返回；不解error来源或实际IO资源状态|
|H→fd：0xa00ef50c..512|从第二参数a1算low32(H−1)保存s1，再以a0=此fd调用0xa0026888，不解引用H或D作fd来源|
|close非负：0xa00ef516..51a/554..55c|保存底层r到a5，先a0=0；signed r>=0跳共同尾声，保留0返回。不是将底层正值原样透传或证明设备资源已经释放|
|close负：0xa00ef51e/522、546/54a/54e/550|第一次getter/LW只给日志；日志后 **再次调用getter并LW当前错误word**，把它交0xa00ea524，尾声保留转换a0。不能缓存第一次值、假定两次同槽/同值或补正式状态枚举|
|H所有权|callback直接callee集合只有formatter、open/close接口、getter、日志、转换；没有以H作deallocator参数。H无本callback独立对象分配/字段初始化，资源责任经fd接口边界；不宣称下层不分配/不释放其他资源|

实际H编码按RV32低word；同一配对输入时close可恢复对应fd数值，但运行时fd未提前关闭/复用、H确来自该次open以及服务正常返回仍是额外前提。数字往返不是实际文件身份或完整生命周期证明。

本轮未发现A66语义错误。精度保留：格式化“意图”与“输出效果”分开，H“编码值”与FILE*/heap对象分开，底层接口“正常返回”与真实IO成功分开。并非用外部LVGL/SDK头文件替换原厂返回宽度/模式值。

局部表达（非原源码；只mode2及服务正常返回前提）：

```c
format_wrapper(buf, 256, "/%s", pathSuffix); // literal/参数事实，返回被忽略
fd = known_fd_open(buf, 1, 0x1b6);
encoded = low32(fd + 1);                           // 原先算，再按fd判门
if (signed32(fd) >= 0) return encoded;
log_boundary(load32(error_slot_getter()));
return 0;

fd = low32(H - 1);
r = known_fd_close(fd);
if (signed32(r) >= 0) return 0;
log_boundary(load32(error_slot_getter()));
return opaque_a00ea524(load32(error_slot_getter())); // 日志后重新getter/读
```

`/%s`支持printf-family斜杠前缀/字符串参数的推断，但不证明formatter截断、实际NUL、返回计数、path解析/长度或下层是否保留pathname。有效pathSuffix、buf、底层资源和错误槽条件沿接口边界；没有为补“合理行为”加入format返回门或free(H)。

## 真正新增

**非作者复核新增业务0、语义纠正0、ISA/来源认证0、整库排除0。** A66给定地址body获得限定接受，不把本轮重新读字节、literal或复核JSON计新功能。A47/A49清理及D03/F05/F06接口不重验；D槽绑定不是这次验收对象。

默认五ROM照片mode0结论保持；callback可解释不证明实际source类型1调用、特定路径/driver/文件系统或实机open/close成功。缓存C/buffer、O与编码H是不同对象/角色，不合并释放合同。

## 未闭精确边

未闭：0xa0053252实际格式输出/截断/NUL及返回规范；真实path/inode/文件系统、fd有效性/并发复用、close最终效果、错误转换的数值域；D/路径/资源寿命和实际mode路径；D槽绑定由J08/6/A64/A65独立状态维护。不能由literal存在或H数值往返替代这些前提。

一个有种子的数值后继是 **0xa00ef550→0xa00ea524(第二次getter读出的error_word)** 的返回映射。管理窗口已将其预备为 **J08/9、A70**；本报告只注明边和预备状态，不派发/读取映射函数或errno getter/IO。formatter输出同样保留边界，不在本复核打开新body。

实际检查为54项原字段/目标/字面量/返回原序检查，JSON解析、引用在本树或整合主树存在、空白/独占范围及`git diff --check`；未跑作者/旧脚本或IO。报告/源码/合同未提交，证据JSON忽略留本地原路径，复核者交付后停止。
