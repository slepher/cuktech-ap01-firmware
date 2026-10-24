# A66：reader正常mode2 callback的路径参数与编码H

2026-10-24；认领 **J08/7**，作者 `/root/a56`；固定基线 `bd457a6`，独占 `re0041-a66` / `codex/re-0041-a66`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记两个精确callback地址及必要format literal/wrapper增量；采用主仓[流程](reverse-design.md)、[保留规则](../../analysis/README.md)和REA技能的有界静态方法。

**0xa00ef468在mode2时选flags数值1，把pathSuffix和literal `/%s`、256B上限参数交格式化wrapper，再以 `(buf,1,0x1b6)` 调已知fd-open接口。其非负返回fd被编码为 `H=low32(fd+1)`；H是word值，既不是FILE*，也不是callback另行分配的handle结构。0xa00ef502以 `low32(H−1)` 调fd-close接口，非负结果回调返回0；没有把H作独立free对象。** 底层格式化输出字节/路径解析/实际文件IO/最终资源释放仍有限定。

A64给D+0x0c/0x10到这两个地址的原字段候选，派发时仍待A65；本题独立恢复callback body，**不提前验收D槽绑定**，不重复A64的slot写窗口。旧J08/2的ROM POSIX路径owner与地址独立提供定位；路径family不能认证精确版本、未改源码或实际inode/文件系统。

不执行文件/设备IO、目标/固件/指令/模型、SIM/QEMU、构建、回放、异常输入或外部服务；不运行旧技术脚本、不切换共享REA、不改生产ROM配置模型或共享表，无下级agent、提交推送。底层open/close/allocator、error-map及a0053252 formatter body未读。新JSON保持analysis原相对路径并受Git忽略。

## 继承结论

|出处|已有行为及本题分界|
|---|---|
|[最终complete](application-rehost-complete-0041-20261017.md)、A33/A35及[J08/2盘点](reader-driver-reuse-gap-j08-0041-20261024.md)|默认五ROM照片mode0与业务/SIM已有覆盖，不因新callback可用就写成这些照片实际mode1。ROM `/src/libs/fsdrv/lv_fs_posix.c`路径及owner只定位代码family|
|[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)|真实接口为open `(D,pathSuffix,2)`、close `(D,H)`；source首字节/冒号后缀、W/O前缀、callback后重读、缓存归还/清槽已有合同。全段继承，不重读或重验|
|[A54/A55来源](photo-reader-source-a54-0041-20261024.md)|本地LVGL候选的通用fs前缀/槽角色相符，版本/载体差异保持|
|[A64候选槽绑定](reader-driver-slot-bind-a64-0041-20261024.md)|原字段候选D+0x0c→0xa00ef468、D+0x10→0xa00ef502，待A65的状态按派发基线保留；不把本body恢复当绑定复核|
|[D03](uart-write-object-d03-0041-20261023.md)|0xa003f4f6把pathname/flags交0xa003eb14，局部file安装/数值fd来源已解释；本题直接继承fd-open接口，不新取下层路径查找或文件安装body|
|[F05](miio-exit-callback-f05-0041-20261023.md)/[F06](display-exit-review-f06-0041-20261023.md)|0xa0026888以fd作实参的归还wrapper角色与调用端已验；底层最终file/device close成功没有据此认证。本题不展开该body|

原件身份沿[CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，VA映射`file_offset=VA−0x9ffff000`。只核长度、继承摘要，不重算哈希、不套0031/unsigned/SIM。

旧whole-ROM索引 `functions[3409/3410]` 两body无dossier/historical_contracts：open extent EID `ev_d2a3ffd68947171f29dbeae7f5b129090a577519f71016d41e3e86ce5907b124`，directcall `ev_fab46098efe4f4c609b8f5518194fcd9642bc21919400810bf422759b5473bee`；close extent `ev_eefcffbc335d62e6fc648ef3d03f64439f8f89408f8d5aca56b5fb0f578be3b4`，directcall `ev_d9545331811dc9e76377715d9e2eea9ed2f7076f06b9cdb634769dc3b50fecc2`。source_paths[321]的旧POSIX owner证据保持原出处；metadata不是本体语义或精确版本证明。新原字检查没有新REA ID/profile。

## 本轮复核或纠正

旧A47/A49接口语义纠正0；新精度为**该具体callback的H表示**。通用fs把H作为word保存/传递，此处的H由fd+1算出，不由名称推标准FILE*、指针结构或malloc所有权。H=1可表示fd数值0；正常fd>=0路径的计算按RV32低word，不替换为解引用句柄。

最初只见a008ab4c调用端时保持formatting候选；查旧metadata无body合同后先报管理者，才获准该42B wrapper与literal必要NUL数据。它不是本callback的allocator。D03/F05/F06已验接口直接复用，没有因新fs callback把底层open/close全重做。

格式事实与输出推断分层：原件literal在0xa06371e4，按“最多64B、遇NUL停”实际读到 **`2f257300`（`/%s\0`，4B）**。wrapper把pathSuffix值存成首vararg、转交原format/buf/256参数到a0053252，这是事实；按printf样式family解释，意图为斜杠前缀加pathSuffix，这是**推断**。a0053252未展开，故实际写入字节、截断/终止规则、返回计数以及所有路径长度域未认证。不能仅因有调用就写buf已被证明等于该拼接结果。

## 真正新增

### mode2路径与fd+1编码

|地址/必要字段|正常输入、顺序和返回|
|---|---|
|`0xa00ef476/47a`|s0=sp+0x110；a3保存原a1=pathSuffix。后续buf=`s0−0x110`，为本callback栈内工作区，不是返回H的对象|
|`0xa00ef478/47e/482/484/486`|比较mode与1失败；置a5=2、s1=1，mode2相等跳0xa00ef494。这里只恢复mode2的flags数值1，不据其他模式或头文件猜正式open flag宏|
|`0xa00ef494/498/49c/4a0/4a4`|a2=literal0xa06371e4，a1=256，a0=buf，a3=pathSuffix，JAL→0xa008ab4c。D在该正常路径未被显式解引用来构造路径|
|`0xa008ab54/56..66/6a`|wrapper先word保存原a3到其s0+0x0c，再令a3=&saved-varargs；其余a4..a7按word保存；以原a0/buf、a1/256、a2/format、a3/varargs地址调用0xa0053252|
|`0xa008ab6e..74`、callback`0xa00ef4a8..4b2`|wrapper尾声保留下层a0返回；callback不比较它，直接置a2=0x1b6、a1=s1=1、a0=同buf，调用0xa003f4f6。0x1b6是原数值，不由此认证底层权限/flag的完整ABI|
|`0xa00ef4b6/4ba`|先a5=low32(fd+1)，再按**signed fd>=0**分支到0xa00ef4f0。正常接受的原fd数值来自已知fd-open接口，不是buf指针或D内部对象|
|`0xa00ef4f0..500`|恢复ra/s0/s1，a0=a5，恢复sp并返回，故H=low32(fd+1)。没有callback独立H allocation、H字段初始化或指向栈buf的H返回|
|`0xa00ef4be/4c2/4ea/4ee`|fd负分支先调用0xa00267c0取槽并LW错误word，调用日志接口后明确置a5=0，再走H返回尾声。H0结论以这些opaque服务正常返回为前提，不假设诊断/日志必正常返回|

callback自身没有校验format返回或把它作为open门；真实pathname解析和文件资源归属按底层接口边界。即使H不指向buf，也不能从此证明底层绝不通过其他方式保留pathname；本题只认callback返回值的数据来源。

### close减1、返回与归还原序

|地址|正常H输入下的字段事实|
|---|---|
|`0xa00ef50c/510/512`|s1=low32(a1−1)=fd；a0=s1调用0xa0026888。原a0=D不作为本路径fd来源，H从第二参数解码；不解引用H|
|`0xa00ef516/518/51a`|把底层返回存a5，先a0=0；signed a5>=0直接到0xa00ef554。正常非负结果被callback折为0，不把底层正值逐值透传|
|`0xa00ef554..55c`|恢复ra/s0/s1/sp，不改a0，再返回；成功分支返回0|
|`0xa00ef51e/522/546/54a/54e/550`|负分支第一次slot getter→LW错误值交日志；**日志后再次slot getter/LW**，把此时错误word交0xa00ea524，尾声保留转换服务返回。不能缓存第一次错误值或假定两次同槽；转换body/正式返回枚举未展开|

本callback没有独立handle分配对象要free，没有把H作deallocator参数；资源关闭责任通过解码fd交既有close接口，不能把调用事实写成已观测物理资源回收成功。同次open→close的解释还要求传入确为前次H、fd未被其他路径提前关闭/复用以及相关服务正常返回；不是某个实际运行fd身份认证。

A47/A49的后续通用close行为直接继承：callback返回后重新读D/config/C，按原条件归还缓存并清reader前三word，外层再归还O；callback返回本身不作该清理是否执行的条件。缓存C/其buffer、O与编码H是不同角色，不将缓存free称为free(H)，本题不重验该字段/原序。

局部伪代码（非原源码，literal/格式结果强度分开）：

```c
// open(D,pathSuffix,mode=2)，服务正常返回与有效输入前提。
format_wrapper(buf, 256, "/%s", pathSuffix); // 参数事实；下层输出规则未认证
fd = known_open_interface(buf, 1, 0x1b6);
if (signed32(fd) >= 0) return low32(fd + 1);
read_error_and_log_boundary();
return 0;

// close(D,H)，H是同次open的编码值时：
fd = low32(H - 1);
r = known_close_interface(fd);
if (signed32(r) >= 0) return 0;
read_error_and_log_boundary();
return opaque_error_conversion(read_error_again());
```

新增为这两个callback的正常mode2参数/编码返回/close配对与format wrapper桥；无新库归属/版本认证、read/seek/dir、整FS或实机IO成功结论。A64绑定待A65不能由本体恢复替代，默认五ROM照片mode0继续保持。

## 未闭精确边、检查与后继

未闭：a0053252实际格式化输出/边界/返回规范、底层路径解析与具体inode/文件系统、实际fd运行身份/可用性/并发复用、close最终资源效果、错误值转换完整ABI、path/D/资源寿命、实际mode1路径实例和D绑定独立接受。H数字编码不等于完整文件生命周期；POSIX源路径或本地候选源码不认证未改版本。

有种子后继优先为原 **J08/7** 的非作者限定复核：核mode2→flags1、literal/vararg接口而非已证输出、fd>=0→H=fd+1、close H−1和返回折叠/错误槽重读，保持A64/A65绑定状态及D03/F05/F06继承界面；不得重开所有read/seek/dir/FS。若另追输出规则，已知下一跳为a008ab6a→a0053252(buf,256,"/%s",saved_varargs)，须先查旧证据并由管理者另登记，本作者未展开。

[verify.py](../../analysis/reader-driver-open-close-a66-0041-20261024/verify.py) 实际 **63项PASS，58个必要指令锚点/178B，加4B literal**。独立拆RV32/RVC参数寄存器、mode分支、word/byte宽度、JAL、signed返回门、H算术及wrapper argv/尾声；普通解码探索为两callback共246B及获准wrapper42B，另有短窗重读，样本不冒充全部曾读字节。literal按NUL停；没有新反编译、厂商模型修改或目标执行。

本地忽略 [evidence.json](../../analysis/reader-driver-open-close-a66-0041-20261024/evidence.json) 保存VA/偏移/原字、literal、旧extent/call EID、接口前提与局限，无新REA ID/profile。JSON、相对引用、Git忽略和diff检查通过。作者交付待非作者复核，完成后停止本题供管理窗口整合/补位，无提交推送。
