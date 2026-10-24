# F27：同Q创建参数到首word mode初始化写点

**找到实际写端，结论限所取正常前缀到达该写块时：`0xa010e3fc`将保存的请求7按完整word写入同Q首槽，故在这一写点 `word(Q)&0x40=0`。** 这来自明确的Q/请求寄存器保存与SW，不由Q+0x18的size4推mode，也不只凭调用参数7猜Q内容。

**尚不无条件认证完整接口成功返回时、所有创建分支或后续实际send中的mode都保持0。** 未读name/创建其他臂，写点之后还有optional归还接口；其别名副作用、实际执行及后续writer不在本题。只保留数值位，不命名正式O_NONBLOCK等flag。

2026-10-24；认领 **F11/10**，任务F27，作者 `/root/f12`；独占 `re0041-f27` / `codex/re-0041-f27`，固定基线 `bd457a6`。沿主仓[唯一管理记录](rolling-management-0041-20261023.md)、最新 [reverse-design](reverse-design.md)/[材料规则](../../analysis/README.md)及REA技能先查旧证据：初始只有F15字段和metadata；creator16B参数/wrapper48B、再到0xa010e320正常写端，均先报旧不足/实际连接、登记后读取，找到写端即收缩。

不执行queue/file接口、目标/指令/模型、固件、SIM/QEMU、构建、旧技术脚本、回放、设备或外部服务；不读FS/driver/allocator/新callee正文，不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，无下级agent、提交或推送。只写本报告和独占analysis源码/合同；生成JSON原路径忽略保留。作者交付待独立复核。

## 继承结论

|出处|已有行为与界限|本次差集|
|---|---|---|
|[F15](miio-queue-size-gap-f15-0041-20261024.md)/[F16独立接受](miio-queue-size-review-f16-0041-20261024.md)|同M正常setup的L/ctx/Q身份、creator成功时Q+0x18=4；Q是creator申请返回的s1、正常输出到原槽|全部继承，不重验size/attach/配置/线程；size与首word是**不同字段**|
|[F23](miio-queue-send-wait-gap-f23-0041-20261024.md)/[F24](miio-queue-send-wait-review-f24-0041-20261024.md)|服务使用word(Q)&0x40；caller既有直接/计数/返回零getter进入边及范围纠正已限定接受|只找mode写端，不重读状态服务；不复用旧“仅首次flag非零”整体caller误述，也不把global flag0x62fc6034等同Q.mode|
|F15持久原字段|保留attrs的cap/size stack写、0xa005f122/126调用目标和成功size/out提交；未保留调用前16B a0..a4参数组|旧保存不足具体到[f10a,f11a)，不因历史探索曾读过就冒称已有持久字段合同|
|旧whole-ROM metadata|0xa01974de只有48B extent/directcall；0xa010e320只有530B extent/directcall/来源候选，无dossier|只作定位，不依文件名/候选库认证mode或完整接口，登记后仅核必要参数/写端|

原件沿 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；映射 `file_offset=VA−0x9ffff000`。不套0031/unsigned/SIM。

旧F15同Q必要行只读主仓本地忽略 `reverse/analysis/miio-queue-size-gap-f15-0041-20261024/creator-evidence.json`，不运行F15脚本。正常setup旧master/callback的REA profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`沿F15/F16保留，本题不重新采集或重标。新字段为原件/Capstone/位域证据，无新REA生产ID。

旧index `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json`：

- `functions[5799]` 0xa01974de，extent EID `ev_dc1299415c0f66d3c859a6e1a230a2d8a35db294e684cbeab5271de37edc8098`，directcall `ev_86042dc2a4874c283c5900e2db0a6d3742c71fcbb403ae4620427725d9d419c7`→0xa010e320。
- `[3840]` 0xa010e320，530B extent `ev_1ae31bd9673fe052005725f2f591e68ab775f2c90180395a1d2879b61bedc772`，directcall `ev_a845241c3211d927686eee382e64da00fe42b76d6c9e76f73e4b6f3b4de5c448`。来源路径metadata仅候选，不替代本题对象/field证据。

## 本轮复核或纠正

旧size或mode使用端没有语义纠正。需要分清三层：**创建参数7**、**同Q写点SW7**、**完整成功返回/后续使用值仍7**。本题补前两层的具体连接，只在写点承诺数值；第三层有未读控制臂、callee/别名和后续writer前提，不悄然合并。

本轮新字段工具 **Capstone 5.0.7 / RV32+RVC** 与独立JAL/S-format位域，无UNKNOWN/厂商模型依赖。 [verify_params.py](../../analysis/miio-queue-mode-init-gap-f27-0041-20261024/verify_params.py) **18项/64B PASS**：creator16B与wrapper48B，另复用F15必要对象行；[verify_mode_write.py](../../analysis/miio-queue-mode-init-gap-f27-0041-20261024/verify_mode_write.py) **30项PASS**：只读目标530B函数的前284B用于所选正常控制/保存寄存器连续性，保留84B必要写端锚点与宽度检查点，找到Q首word SW及其本地success cleanup/return即停。其余246B/所有callee没有取证，没有全函数导出或全FS/heap扫描。

## 真正新增

### creator→wrapper→同Q/请求与参数包

|地址|真实参数与顺序|
|---|---|
|0xa005f10a..f118|a0=F15已验Q（s1），a1=局部name地址s0−0x40，a2=7，a3=0x180，a4=attrs地址s0−0x50；F15已验attrs前两word为请求cap/size。这里不把0x180或7命名为正式OS枚举|
|旧0xa005f122/126|目标为0xa01974de，正常成功门与之后Q.size/out提交沿F15/F16，不重验|
|0xa01974e6..74fa|将原a3/a4/a5/a6/a7依次保存到本地连续包；原a3=0x180、原a4=attrs，其他原值不补猜。a0同Q/a1原name未在wrapper中改写|
|0xa01974ec..7502|a4=&原a3包，明确重置a5=0、a3=0、a2=7，再JAL到0xa010e320。因此下层可见值为 `(Q,name,7,0,&packed_args,0)`，不是把原a3/a4原样留在同寄存器|
|0xa0197506..750c|恢复frame后返回，没有替换a0。wrapper无Q首word写；参数包的完整正式variadic声明/下层消费不由该小wrapper全认证|

### 正常前缀到首word初始化写点

|地址|原字段/条件与同对象结论|
|---|---|
|0xa010e338/344/348|保存a5到s5（此实际wrapper给0）、保存原a0到s3=Q、原a2到s6=7。先有name非空门；正常callee保存这些寄存器为前提|
|前缀控制|沿所取前缀，request mask4、attrs正常门、name首字符/格式处理后进入lookup。name另一臂0xa010e392→0xa010e43c及后续创建臂未读，不能当作已认证的共同正常到达路径。所读区间中s3/s6未有显式重定义；opaque服务正常返回/保存寄存器前提保留|
|0xa010e3d2..e3ea|lookup-like服务保持opaque；其返回非负且所取对象halfword低4位为5时，落入本题正常公共初始化块。仅保留数值门，不认证inode/文件类型正式枚举或资源成功|
|0xa010e3ee..e3f4|以 `(Q,0,0x18)` 调既有清零接口0xa0024906。只引用接口，不再读其body或由24推整个Q大小；正常返回后仍使用保存Q/请求|
|**0xa010e3fc** 原字 **23a06901**|独立S-format `(op,f3,base,src,off)=(0x23,2,s3,s6,0)`：**完整SW请求7到同Q+0**，不是OR/byte store/Q+0x18。故在所述前缀/保存前提下，此精确写点 `word(Q)=7`、`word(Q)&0x40=0`|
|0xa010e400/404|另SW对象指针到Q+0x0c；wrapper给s5=0，所以正常选中分支跳过aux output store到e40e。Q+0x0c不是mode首槽，不与size槽混合|
|0xa010e40e..e43a|可选以另一局部加载指针交既有归还接口，然后清其局部槽、恢复mstatus、设置正常status0并返回。所取本地尾段无直接Q首word再写；该callee/别名副作用、其他成功返回臂和全程mode保持仍未认证|

局部表达（非原源码；只描述所取正常前缀到写点，不替代完整接口）：

```c
// 同Q creator与wrapper的真实值：
wrapper(Q, name, 7, 0x180, attrs);
// wrapper以局部参数包交下层：
lower(Q, name, 7, 0, &packed_original_arg3, 0);

// lower的所选正常公共写块，正常保存Q/flags及可达性为前提：
saved_Q = Q; saved_request = 7;
opaque_lookup_and_gates();
clear_interface(saved_Q, 0, 0x18);
word(saved_Q) = saved_request;       // e3fc；此时mask0x40清
word(saved_Q+0x0c) = selected_object;
optional_cleanup_boundary();        // 不省略，不认证其全部别名效果
restore_saved_mstatus();
return 0;                           // 仅所取本地success尾段
```

在该写点，Q首word与Q.size4是两个独立恢复的字段。若要把写点mode0带到F23使用端，还须证明完整实际控制路径、正常返回保持和后续写入/替换条件；本题不从“参数7”直接跳到“所有typed调用必走mode零臂”。同理global flag0x62fc6034控制getter的条件与Q首word的mask0x40无同对象/同字段关系。

新增恢复为**真实创建参数包→同Q正常首word SW初值7的条件写端**；旧size/attach/caller/getter/状态服务直接继承，业务功能新增0，ISA/库来源认证/整库排除0。没有实际执行任何open/queue服务。

## 未闭精确边与后继

仍未知未读name/新建/错误臂到此写块的完整可达性和是否另写Q首word、写点后的callee/资源别名效果、所有成功返回与后续运行值保持、后续writer/替换/关闭、实际mode/正式flag名、对象/资源生命周期和服务执行。尤其不能把初始SW7当运行期总不变，或从size4推出mode零。

一个有种子的后继可限 **0xa010e392→0xa010e43c的实际name臂到已定位Q首word写块的保存/汇合**，由管理窗口查重登记后仅补必要控制/寄存器桥；不展开FS/driver/allocator。若要升级到完整返回mode保持，仍须针对同Q正常尾段的具体别名/写入边另作证据，不泛扫全FS。本作者找到写端后停止，未读该新臂。

实际检查为18项参数/wrapper、30项正常写端字段/目标及保存寄存器连续性，均PASS；两份生成 `parameter-evidence.json`、`mode-write-evidence.json` 本地忽略保留，包含VA/原字/偏移和未知边。[contract.json](../../analysis/miio-queue-mode-init-gap-f27-0041-20261024/contract.json)只保留必要语义。JSON解析、引用在本树或整合主树可定位、空白/独占文件及`git diff --check`已检查，源码/合同/报告未提交；作者交付后停止，待非作者复核。
