# A68：J08/8 reader实际read/seek callback的参数、输出及返回

2026-10-24；固定基线 `bd457a6`，分支 `codex/re-0041-a68`，认领 **J08/8**，作者 `/root/g23`。**read入口0xa00ef55e把第二参H按低word减1作fd，原buffer/count转交0xa003f6a2；底层a0按signed32非负时，word写原out_count并回调返回0，底层0也走同一门。负分支没有callback自身的out_count写入，日志后重新取错误槽值交0xa00ea524，返回其结果。**

**seek入口0xa00ef632先以unsigned origin>2返回数值11；其余路径把H−1、原position word、原origin word分别置a0/a1/a2交0xa00281d8，signed32的返回a0非负时回调返回0，负时同样经二次错误槽读取/映射返回。** callback没有补position高word/符号扩展；底层off_t精确位宽、参数数目和返回ABI仍需其自身证据，不能照标准原型修成64位调用。

已读主仓 [管理记录](rolling-management-0041-20261023.md#链条认领表) J08/8、A64/A66及必要旧metadata，沿本批已读 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)与 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只取两个实际callback入口的必要正常/失败分支原字；未读邻近write callback、底层IO、error-map、copy、logger或getter body，不执行IO/设备、目标/指令/模型、固件、SIM/QEMU、构建、回放、异常输入或外部服务，不运行旧技术脚本。

没有共享REA/数据库/profile变更、生产ROM配置模型或主树/共享表修改，无下级agent、提交推送。本文静态表达非原源码/实机观察，作者自检待非作者复核。

## 继承结论

|来源|已有连接与本题界面|
|---|---|
|[A64槽绑定](reader-driver-slot-bind-a64-0041-20261024.md)，派发时待A65|D+0x14写0xa00ef55e、D+0x1c写0xa00ef632是实际入口种子；本体恢复不代A65独立接受，也不重新取slot写端|
|A47/A49、[A50](photo-reader-consumer-a50-0041-20261024.md)/A52|真实read接口(D,H,dst,want,&got)，seek接口(D,H,position,0)；返回状态/实际got独立，缓存/owner持有已验。只继承调用端，不重读cache算法|
|[A66 open/close](reader-driver-open-close-a66-0041-20261024.md)，派发时待A67|作者候选H=low32(fd+1)；本题独立核read/seek自己从H−1形成fd，不重读open/close或提前验收其全部合同|
|B18旧UART正常read调用端|同0xa003f6a2曾接(fd,&byte,1)，只提供read-like接口定位，不证明本题底层缓冲/返回/资源算法|
|J08/2、A54/A55|POSIX源路径/本地LVGL候选帮助定位family；不能代替本体字段、H/off_t类型或精确版本认证|

原件沿 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`。仅核长度、引用旧摘要，不重算hash，不混0031/SIM。

## 本轮复核或纠正

旧索引functions3411的read范围`0xa00ef55e..0xa00ef5c7`为106B，extent Evidence `ev_d52a57d277f473200206c4ce0bdfd6e3c0409bba50f9f97ef14732600bafe5ee`、directcall `ev_6aa402a850a383d7eaa4c2e1401089905a83552ba65c4a1a6dc5741e606026f4`，无dossier/历史合同，只作定位。

**seek的真实slot入口0xa00ef632没有旧独立function entry。** 邻近write owner0xa00ef5c8的旧extent恰止0xa00ef631，其参数/IO callee不能套到本seek。本题从slot给出的632入口核到平衡栈、前向origin门及698/69a两返回点；没有手填provider函数边界、改分析器或把未识别范围宣称旧已完整恢复。邻近write原字未读。

独立JAL字段校正过中途速报的手算目标，最终`0xa00ef64e→0xa00281d8`；原字及模型未改。旧functions494确有该88B入口，extent EID `ev_e4e78eb4b960e25ba685f036fa7a7a8c2229928f73834c72008e6130df1781fb`、directcall `ev_9e014f662c301c4d3990b4c938f78d0748a37dbb4e95d8a26748bf6ed75ab4f0`，无dossier。本体仍未读取；原型/位宽不能靠这个metadata补猜。

原A47/A50接口语义纠正0。新精度是两callback实际H变换、输出word条件、错误槽重读、数值状态返回及off_t边界。Capstone 5.0.7只作离线RV32/RVC，关键JAL、signed/unsigned分支、word局部槽与C.SW另独立拆字段；没有新REA生产ID/profile、厂商模型执行或整库排除。

## 真正新增

### read五参到fd/buffer/count及实际输出

|地址/关键原字|本体实际原序与宽度|
|---|---|
|`0xa00ef562/56a` `ae84/fd14`|第二参H→s1，再低word减1。D不作为fd来源，H不被解引用；同次A66编码H解释还须其正常open及fd未被关闭/复用前提|
|`ef56c/56e/570` `b285/2685/3686`|a1=原buffer(a2)，a0=解码fd，a2=原want(a3)。本层传的是寄存器word，没有额外count符号扩展/截断；不由此认证底层size_t/ssize_t定义|
|`ef572/57a`|原a4=out_count指针word存到局部s0−0x14，底层返回后重读；不是把输出计数当底层第三参，也不直接传H作为buffer|
|`ef576` `ef00c592`|独立JAL目标0xa003f6a2；只确认这组显式寄存器实参，下层实际读/持有/返回仍为边界|
|`ef57e` `63520504`|signed BGE a0,zero→ef5c2；只用a0这个word判返回，不消耗a1作为返回高word|
|`ef5c2/5c4/5c6` `08c3/0145/cdbf`|非负时C.SW原a0到word(out_count)，然后a0=0、跳共同epilogue。没有把read字节数作为callback状态逐值返回|
|`ef582/586→ef5aa→ef5ae/5b2→ef5b4`|负分支先getter→LW错误word用于日志；日志返回后**再次getter/LW**，把这次word作为a0交0xa00ea524。尾声不覆盖转换服务a0|

因此底层a0=0与正数同门：out_count写0且callback返回0。若底层用0表示EOF，本callback也按这一路处理；它没有独立EOF标志/判别，本题未认证底层0是否来自EOF、零长度请求或其他正常条件。负分支callback自身没有out_count store，也没有先清零；上层A50先清其local got是另一个已验动作，不应挪进callback。底层/日志/别名对内存的副作用未知，不能把“本体无该store”扩大成所有服务都不改此地址。

缓冲地址只被转交底层接口；callback没有分配/归还buffer、直接把它发布到global或复制I式消息。本callback的可见直接借用跨底层调用；底层是否另行持有、实际数据写入、输入容量/对齐和输出与buffer分离仍未证，不能宣称整个IO栈无借用。

### seek四参、origin门和position/off_t边界

|地址/原字|参数及返回事实|
|---|---|
|`ef632/634/636` `8947/2d45/63e2d706`|a5=2，先a0=数值11；unsigned `2<origin(a3)`直接到ef69a RET。此臂在栈帧、H−1和底层IO之前返回，不补成errno-map调用|
|`ef63e/646`|H从a1保存再低word减1，不解引用/申请handle对象|
|`ef648/64a/64c` `b285/3686/2685`|显式置a1=原position word(a2)，a2=原origin word(a3)，a0=fd。a3仍是原origin的寄存器残值；没有为另一个独立高word/额外参数专门构造它|
|`ef64e` `ef80b3b8`|独立JAL→**0xa00281d8**；原字没有在callback中对position做算术右移/符号扩展或置高word|
|`ef652/654/656`|保存下层a0到a5，先置callback a0=0，再signed BGE a5,zero→ef690尾声。非负下层结果（含正位置值）折为callback0，不返回该位置值|
|`ef65a/65e→ef682→ef686/68a→ef68c`|负分支第一次getter/LW用于日志；日志后第二次getter/LW交同0xa00ea524；尾声透传映射a0。没有缓存首个错误word或证明两次同槽/同值|

本题能认证的是**callback输入/显式转交均为word，以及仅a0 signed判定**。底层0xa00281d8的实际off_t有无高word、符号扩展责任、返回pair或其他ABI约定尚未读取；不能因为标准lseek原型或未清的a3残值就认证它的参数数目/类型，也不能为合理化而改写调用。origin只按原unsigned门允许数值0/1/2，正式enum名称没有认证。

两callback的错误路径都以相关opaque服务正常返回为前提。0xa00267c0正常getter的更早合同不能自动证明日志前后状态稳定；映射0xa00ea524本体仍opaque，不能把callback最终错误返回命名为精确LVGL枚举或下层负errno。

局部伪代码（非原源码）：

```c
// read(D,H,buffer,want,out_count)，有效正常调用域。
r = opaque_a003f6a2(low32(H-1), buffer, want_word);
if (signed32(r) >= 0) {
    store32(out_count, r);
    return 0;
}
first_error = load32(error_slot());
opaque_log(first_error, fd);
return opaque_a00ea524(load32(error_slot())); // 重新取槽/word

// seek(D,H,position,origin)：这里只表达显式寄存器转交。
if (unsigned32(origin) > 2) return 11;
r = opaque_a00281d8(low32(H-1), position_word, origin_word);
if (signed32(r) >= 0) return 0;
first_error = load32(error_slot());
opaque_log(first_error, fd);
return opaque_a00ea524(load32(error_slot()));
```

伪码的下层参数列是显式设置的word，不认证C函数原型/完整ABI；没有偷偷把position改为64位、将负路径out_count置0或把EOF当错误。H、buffer、reader缓存及caller输出槽仍是不同角色，未新增H/buffer所有权转移或释放。

## 未闭精确边、实际检查与后继

底层read 0xa003f6a2、seek 0xa00281d8及error-map 0xa00ea524的返回/副作用/IO实现仍未闭。前者旧functions948只有88B extent `ev_c47eee869674cbf188a66a42cebdda7db330a6ca52e9398a638e0d7aef484064`；映射旧functions3328只有140B extent `ev_c45212c04d6f0d4df9dca25e571b40d05e3508d5ddc8867f30925bac3eda87c2`、无callee，均无dossier。它们已先报管理窗口锚点/旧不足，未读新body。

H的实际同次open来源/fd身份、底层off_t/ssize_t定义、count/position完整值域、buffer有效/容量/分离/持有、错误槽稳定性、映射enum、实际FS/设备及资源关闭成功未知；默认五ROM照片mode0保持。派发时A64/A66待A65/A67，本题自己独立解码H−1而不代这些作者成果验收。

[verify.py](../../analysis/reader-driver-read-seek-a68-0041-20261024/verify.py) 实际 **58项稀疏原字段检查PASS**，含十个JAL、三个signed/unsigned门、word局部槽和输出C.SW独立字段。探索四个短窗合216B请求/212B唯一，分别落两callback原字段，没有邻近write或下层IO字节；没有完整伪码反编译/模型修补。结果与精确旧边界局限见本地忽略 [evidence.json](../../analysis/reader-driver-read-seek-a68-0041-20261024/evidence.json)，必要语义见 [contract.json](../../analysis/reader-driver-read-seek-a68-0041-20261024/contract.json)。JSON/引用、Git忽略、独占状态及diff通过，源码/报告/合同未提交推送。作者自检待非作者复核。

有种子后继先同 **J08/8** 安排非作者核这两入口的实际word转换、out_count/返回门、两次错误槽重读及seek未定义旧entry边界。若另补off_t问题，精确连接为`ef64e→0xa00281d8`的显式(a0,a1,a2)/(返回a0)与该88B服务正常ABI；必须主窗查重登记，不借本题扩write/dir/cache或全FS。
