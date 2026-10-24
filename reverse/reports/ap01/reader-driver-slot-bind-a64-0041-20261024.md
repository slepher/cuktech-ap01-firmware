# A64：J08/6 已注册D到盘符、配置及四个reader槽的实际写入绑定

2026-10-24；固定基线 `bd457a6`，分支 `codex/re-0041-a64`，认领 **J08/6**，作者 `/root/g23`。**已将A62/A63注册的D=0x62fc974c连到实际初始化写端：首byte写0x2f（字符`/`），D+4写word4096；open/close/read/seek的D+0x0c/+0x10/+0x14/+0x1c分别写0xa00ef468、0xa00ef502、0xa00ef55e、0xa00ef632。** 这些是地址构造和真实store的结果，没有靠POSIX路径或相似结构补身份。

关键基址关系为：`0xa008e5da`把s2从0x62fc9000加0x57c得到G=0x62fc957c；`e77a`的辅助基址 **B=G+0x180=0x62fc96fc=D−0x50**。B本身不等于D；B+0x5c/+0x60/+0x64/+0x6c才分别落在上述D槽。正常分支、callee保存s2及后续无其他s2普通定义的所选连续性前提保留，未读任何callback目标body，也不认证真实文件操作/默认五照片mode1。

已读主仓 [唯一认领表](rolling-management-0041-20261023.md#链条认领表) 的J08/6与两次原字段/连续性登记；沿本批已读 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)及 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。先旧A21/A25/A60/A62，旧s2定义缺口具体报出后才按登记读首gap及补充小窗；基址核定后才读slot短窗，找到四槽即停止，不接helper、第二轮未知caller或target body。

没有目标/指令/模型执行、固件、SIM/QEMU、构建、旧技术脚本、回放、异常输入、设备或外部服务，没有共享REA/数据库/profile变更；未改生产ROM配置模型、主树/共享表，无下级agent、提交或推送。本文是静态写入/调用端合同，非原源码或实际执行观察，作者自检待独立复核。

## 继承结论

|来源|已有行为及界限|本轮差集|
|---|---|---|
|[A62](reader-driver-register-gap-a62-0041-20261024.md)/[A63独立复核](reader-driver-register-review-a63-0041-20261024.md)，J08/5|实际list0x62fc9740交insert-head，N非零后保存D0x62fc974c；helper先接头、caller后填N.word0；正常s1保存前提|本题开始时A62待A63，复核期间A63已限定接受，直接继承不重验。这里仅补D字段与写端，不重开注册/节点生命周期|
|[A56](reader-driver-selection-a56-0041-20261024.md)/[A57](reader-driver-selection-review-a57-0041-20261024.md)|N.word0取D后，以U8(D)比较source首byte；可选ready、open非空及正常返回门后才保存reader D|写入盘符可接选择比较的数值，但不证明实际source匹配、letter唯一或运行走到该D|
|A47/A49、[A50](photo-reader-consumer-a50-0041-20261024.md)/A52|open经D+c传(D,pathSuffix,2)，close经D+10传(D,H)，read经D+14传(D,H,dst,want,&got)，seek经D+1c传(D,H,position,0)；缓存读取D+4|这些是已验调用端ABI/配置消费，不等同新目标函数声明、底层H类型、实际返回或IO成功|
|A21/A22、A25/A26、A60|G初始清零、早期s2高位、G基址/部分initializer正常门及两槽初始化局部合同|不能把A60的s1=G套成当前s2，也不能由缺少导出行说从未定义；本题补具体定义连续性|
|J08/2、A54/A55|POSIX源路径owner及本地LVGL候选局部合同|继续只作来源候选；不会因本题目标同地址就认证完整SDK/版本/实现未改|

原件沿 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射`file_offset=VA−0x9ffff000`。本轮只校长度并引用旧摘要，不重算hash，不混0031/SIM。旧原字段沿原载体，未生成新的REA生产Evidence ID。

## 本轮复核或纠正

### 旧定义不足与实际s2连续性

旧A25 initializer选窗e3ac..e4b8与A21选定片段中，普通s2定义只发布`e3c4 LUI s2,0x62fc9`；A60/A62最小锚点未提供后续更新。**旧输入只能给高位常量，不能用D布局推s2=G**。本题按管理登记在首gap找到以下正常点，并补必要连续性缺口，而不是重导整个initializer：

|必要地址/范围|本轮核到的定义/控制|限制|
|---|---|---|
|`0xa008e596`，`21e1`|C.BNEZ a0→0xa008e5d6，独立解目标|沿非零正常门跳过改写其他寄存器的诊断块，不把零路径拼成普通继续|
|`0xa008e5da`，`1309c957`|ADDI s2,s2,0x57c，独立I字段rd=rs1=18，imm0x57c|接旧s2=0x62fc9000得到G；不是沿用s1或同字段名认对象|
|4B[e4b8,e4bc)、12B[e52a,e536)、首gap必要正常段、尾段[e5f4,e612)|所选普通指令/控制中只有e5da定义s2；调用只沿正常callee保存约定，不展开其body|补齐旧A25/A60的短缺口，不把当时未存的探索当新证据|
|[e628,e6ea)与旧A21[e612,e628)、[e6ea,e768)|必要原字段/旧行未见其他普通s2定义；所读条件门前向，外部call保持边界|这是所选正常流的定义连续性核验，不是全错误路径、异常返回或任意caller的证明|
|旧A62 e768/e76c及新slot段|e768使用另一高位s1形成D；e76c正常callee保存s2，e770以后所读段未定义s2|寄存器s1与s2分别追踪，不因都指向同global区域合并它们的当前值|

边界校准：拟读[e5f6,e612)的起点实际落在e5f4的4B ADDI中部，Capstone停解后回到真实e5f4，仅重叠已在首gap探索的前2B；复验采用[e5f4,e612)真实边界。未把半条指令当伪压缩字、未知厂商指令或NOP，也未改变ROM/模型。

旧语义纠正0。B与D的关系在本题被具体化为`B=D−0x50`；A62原本就保留s2未知，未曾认证B等于D，不改写其历史未知项。

## 真正新增

### 盘符、配置和四槽写端

仅在上述正常基址/ABI前提下，以下有效地址与A63的同一个D相接。word是32位，byte是8位；各常量、U/I构造和C.SW/SB字段独立核过。

|写端/原字|实际有效地址|写入与已验接口的连接|
|---|---|---|
|e770 `9307f002`；e776 `2308f91c`|s2+0x1d0=**D=0x62fc974c**|ADDI a5,zero,0x2f后SB到D首byte。若此值未被改变，A56的source首byte匹配值为0x2f（`/`）；不是实际文件访问观察|
|e774 `0567`；e77e `f8cb`|B+0x54=**D+4=0x62fc9750**|C.LUI a4,1的实际word值是0x1000=**4096**，随后C.SW。它接A50读取的配置k，不是word1或分配/IO已成功证明|
|e780/e784；e788 `f8cf`|B+0x5c=**D+0x0c=0x62fc9758**|LUI/ADDI形成 **0xa00ef468**，word保存到已验open槽；调用端仍是(D,pathSuffix,2)|
|e78a/e78e；e792 `b8d3`|B+0x60=**D+0x10=0x62fc975c**|形成 **0xa00ef502**，word保存到已验close槽；调用端(D,H)|
|e794/e798；e79c `f8d3`|B+0x64=**D+0x14=0x62fc9760**|形成 **0xa00ef55e**，word保存到已验read槽；调用端(D,H,dst,want,&got)，状态与got仍是独立通道|
|e7a8/e7ac；e7b0 `f8d7`|B+0x6c=**D+0x1c=0x62fc9768**|形成 **0xa00ef632**，word保存到已验seek槽；所核上层普通路径第4参为0，不补目标实现/enum语义|

`e77a`本身是`ADDI a5,s2,0x180`；之后在所读slot段a5辅助基址未再定义，目标常量构造使用a4。因此这些word store从B+偏移到D字段的转换有实际寄存器/地址链，不由源码候选的结构体成员对齐替代。

这部分初始化写先于A62/A63注册N.word0=D。后续字段可能被其他写者/别名改动，本题只恢复所见初始化关系；不将写入值说成运行中永久不变，也不把D配置4096推广为缓存分配成功、请求均读满或底层H为标准FILE*。

局部静态表达（非原源码）：

```c
// 正常门与callee保存约定成立；注册D身份来自A62/A63。
s2 = 0x62fc9000 + 0x57c;            // e5da后G
B  = s2 + 0x180;                    // e77a，D之前0x50
store8(s2 + 0x1d0, 0x2f);
store32(B + 0x54, 4096);            // D+4
store32(B + 0x5c, 0xa00ef468);      // D+c
store32(B + 0x60, 0xa00ef502);      // D+10
store32(B + 0x64, 0xa00ef55e);      // D+14
store32(B + 0x6c, 0xa00ef632);      // D+1c
// 其余同窗字段不在本题恢复，之后注册连接沿A62/A63。
```

旧J08/2的POSIX路径owner含0xa00ef468，可与本open槽数值相互定位；来源路径仍不能认证该函数完整行为、ROM精确LVGL/SDK版本或其余callback实现。新增的是具体D/字段/目标地址身份，不是完整fsdrv、任一target body或完整IO生命周期。

## 未闭精确边、实际检查与后继

四个目标的参数解释/返回状态、H来源与关闭责任、实际read/seek行为、底层文件系统/设备、失败臂及注销/节点/D寿命仍未闭；optional ready等其他槽也未借本题认证。source与此D的运行匹配仍须A56全部门和相应callback正常返回，默认五ROM照片mode0结论保留。

[collect.py](../../analysis/reader-driver-slot-bind-a64-0041-20261024/collect.py) 实际 **67项检查PASS**：旧s2定义/注册端点、登记范围内正常连续性、s2 ADDI/正常门、U/I目标、C.LUI配置、SB byte与五条C.SW有效地址独立字段。使用Capstone 5.0.7离线RV32/RVC，无厂商模型执行或新反编译；必要原字/VA、连续性控制摘要及边界见本地忽略的 [evidence.json](../../analysis/reader-driver-slot-bind-a64-0041-20261024/evidence.json)。没有重跑A21/A25/A60/A62或其他旧技术脚本，没有读取任何callback/helper body。

探索仅已登记多段定义/控制及两slot短窗；slot段为[770,794)、[794,7b2)共66B。全部探索请求510B/唯一476B，其中有重叠/真实边界校准，绝非整initializer导出；复验只保留必要稀疏字段及s2定义/控制摘要，不把样本数当全部曾读字节。JSON、报告引用、Git忽略、独占状态及diff检查通过，报告/源码未提交，生成物留本地原路径。作者自检待非作者复核。

有种子后继先在原 **J08/6** 下安排非作者A65，只核s2→G、B=D−0x50、盘符/config及四槽有效地址/常量、正常门/保存约定；不重读注册或整initializer。若另追实际文件读取，新的真实调用连接是`D+0x14→0xa00ef55e`、ABI沿已验(D,H,dst,want,&got)，必须管理窗口查重并登记后再进body，不能本题自行展开。
