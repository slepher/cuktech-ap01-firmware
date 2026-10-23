# A50：照片非零 mode reader 的消费接口与缓存持有

2026-10-24；基线 `1edfc57`，独立分支 `codex/re-0041-a50`。**同一reader前缀经 `a010a5ea→a008b888`，以D+0x14槽调用 `(D,H,dst,want,&got)`；普通缓存路径另外使用D+0x1c槽 `(D,H,position,0)`。缓存结构C由R+8持有，数据缓冲B在需要填充时申请并保存在C+0xc，随后被既有W→O复制继续持有，接到A47/A49条件归还。** 具体D、回调目标、实际照片非零mode仍无实例证据，不命名标准FILE*或具体文件系统。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读主仓ROM/留存材料及A49报告，不开共享REA target/database，无固件、SIM、构建、历史回放、设备、外网或下级agent，不改其他树、生产ROM/代码/配置/模型。只写本路独占报告与analysis。R/D/H/C/B是分析字段名；伪代码不是原源码。

## 继承结论：已有→行为→局限→实际缺口

|已有出处|已经解释的行为/证据层次|本轮真正缺口和处理|
|---|---|---|
|[A47](photo-reader-mode-a47-0041-20261024.md)、主仓A49 `photo-reader-mode-review-a49-0041-20261024.md`|分类1建立mode1 W，初始化R+0=H、+4=D、配置非零时R+8=C；同constructor复制当时W到O；归还调用D+10 `(D,H)`，重读后条件free(C+c)/free(C)，清O前三word|原字节及独立复核合同继承；A49未展开a008b888，不重做open/close/owner持有|
|[A37](photo-decoder-owner-a37-0041-20261024.md)/A39、[A41](photo-decoder-destroy-a41-0041-20261024.md)/A42|copy(O,W,0x664)，owner+5c持O，+74持内部派生区；旧O正常替换最终整体归还|不重新恢复构造、输出或析构；只把read后的C/B状态连到既有复制/归还|
|[A33](photo-source-abi-a33-0041-20261024.md)/A35、照片round3、最终ZIP/SIM|默认五ROM照片descriptor+10→data→mode0借用，轮转行为已恢复|不能从存在mode1分支声称实际五照片从文件读取；不重导资源/压缩/像素算法|
|主仓 `weather-calendar-complete-0041.json#/evidence/30`，address A010A302|旧objdump含a010a5d6 reader非零mode分流及a010a5ea直接call；同记录含constructor消费入口|stdout明确截断。本轮读其内部确认有call、没有a008b888 body；其另一个调用位于evidence/1，不展开另一业务|
|whole-ROM round1 a008b888 extent `ev_0cf7b05aecf9153467edba3b567024c23acd5f53b2e1392c883286c7ca4197e6`|旧body范围b888..baa7，544B；direct_calls `ev_86c95e3108349c7bdea188fd5ad92903355d6c757f0c400f887554f4a20abae3`仅定位copy/alloc/diagnostic；路径候选a02631a8|不是内部语义证明；仅补同reader的ABI、槽、持有/游标合同，不重导544B完整body|

复用边界继承A47/A49的当前报告与主仓rehost JSON精确查询；本轮再核weather complete两个命中record的内部，见evidence.json中的reuse。旧complete/ZIP/token未命中不等于从未分析；pass3及最终complete按`a008b888/lv_fs_read`无命中只作为此窄词项边界。四层证据分开：可靠原字节合同继承；旧反编译/extent仅定位；SIM/照片替代不证明ROM ABI；实际缺口仅此callee的消费连接。

## 本轮复核或纠正

`a010a5e2` 是 **LBU** R+10整byte；`a5e6`为零跳mode0内存臂。非零时仅`a5e8`置a3=0，再`a5ea`调用a008b888；a0=R、a1=dst、a2=want保持。该入口在W构造初读和O后续读取中可复用；不将W/O误作新包装对象或只传H。

此为A47/A49已有分流的局部字节复核，不计新增功能。a008b888的a0返回沿wrapper尾声原样返回；wrapper未把它转成已读字节数。原callee返回的a0是间接read调用的状态值或缓存命中时的0；实际长度走独立out-count通道。照片wrapper传NULL只省略对外count存储，不省略callee的内部实际长度记录。

旧报告无语义纠正；A47保留的“缓存+c首次分配/填充未知”在下面普通缓存路径内收窄。配置0xffffffff的特殊自指/预置数据模式继续保留，不把其buffer套入本题新申请的普通B合同。

## 真正新增：正常接口、状态及所有权

### read与seek实际回调槽

`b8a0..b8a6` 保存R/dst/want/out_count到s1/s6/s2/s5。out_count非NULL时先SW清其word；D=word[R+4]。`b8b4`读取配置k=word[D+4]，`b8b8`读取read槽D+14；k非零还检查D+1c的seek槽。缺D/槽属于原返回门，未展开其诊断或失败业务；没有新增安全门。

普通k=0直读臂 `ba94..baa0`：

```c
uint32_t got = 0; // 原callee局部word，先前b8cc清零
status = load_fn(D+0x14)(D, load32(R+0), dst, want, &got);
// a0=D, a1=H, a2=dst, a3=want, a4=&got
if (out_count) *out_count = got;
return status; // 返回a0，b996恢复s4→a0；不是return got
```

这里没有C、缓存分配或R+c/14的mode0游标更新。D本身是第一个参数，H才是第二个参数；不能改写成`read(H,dst,want)`或`callback(R)`。callback返回状态和其写出的got是两个独立结果，具体read函数和H类型仍未知。

缓存有数据但需越过尾部时 `b932..b940` 重读D/H，以D+1c调用 `(D,H,cache_end+1,0)`；缓存未命中时 `b9d4..b9dc` 同槽参数是当前逻辑position。该槽的“seek/定位”解释来自位置实参和后续读，不认证原enum名；原第4参a3确为0。其返回值未用于这里后续read门，不能补成检查seek结果后才继续。继而又重读D/H和D+14，按需读调用者dst尾部或缓存B。

### C的字段、命中与普通小读填充

本节只描述A47普通open的配置k非零且k!=0xffffffff、有效C及正常callback结果的路径。C通过R+8共享持有；不是栈out_count。字段用途来自访存/比较/复制：

```text
R+0 H；R+4 D；R+8 C；R+10 U8 mode。
D+4 k：普通缓存配置/每次填充请求字节数。
C+0 start；C+4 end（含尾）；C+8 logical_position；C+c B。
```

`b8d4..b8e6`读取C、position、start、B、end，按unsigned比较认定start≤position≤end。命中源地址化简为`B+(position−start)`，剩余缓存字节`end−position+1`；普通命中且want足够小时，`b90e..b916`把want字节copy到dst，局部got=want，status=0。没有D回调或新分配；随后重读C，将实际消费量加到C+8。

未命中时先按上述槽定位：want>k直接调用read(D,H,dst,want,&got)，不申请B；want≤k才进入填充。`b9f6`检查保存B，非零直接复用；否则`b9fa..ba0e`重读C，以a0=k调用 **a008aea0(k)**，将返回值存C+c，再重读C+c作为B。分配非空后的普通路径如下，分配失败诊断未展开：

```c
uint32_t filled = 0;                       // 原局部word s0−34
status = load_fn(load32(R+4)+0x14)(
             load32(R+4), load32(R+0), B, k, &filled);
C = load32(R+8);                           // 回调后重读，不能沿用旧C快照
C->start = saved_logical_position;         // ba6c
C = load32(R+8);                           // 原程序再次重读
C->end = C->start + filled - 1;            // RV32 word，ba78..ba80
take = unsigned_min(filled, want);         // ba82/ba86条件move
copy(dst, B, take);                        // ba8e→a008ab76
got = take;
// 正常status==0汇合后：重读C；C->position += got；可选输出got；返回status。
```

填充请求是k，并非外层want；B可在本次复制后继续持有未消费的缓存字节。reader不free B或C，不清R前三word；不递增H，也不写D。配置单位在此由read/copy长度连接支持字节解释，不认证任何具体driver的物理读取方式或整个文件长度。

跨缓存尾部时先copy已有部分，定位到旧end+1；剩余请求大于k则直接读dst尾部，否则read k到同B并更新C范围，再copy所需部分。记录总量为`unsigned_min(want, 已有部分+filled)`，正常status0才据它更新逻辑position；缓冲copy的低31位掩码另见下表，不把两个表达无条件等同。此处只补接入/持有与必要计量，不展开完整文件系统、全部失败I/O或上层解码算法。

### 厂商字与实际长度边界

必要厂商编码均独立拆位并与既有只读规则相符：

|原地址/LE word|字段/效果|
|---|---|
|`b96c 42f9198b`|op0b/f3=1/f7=33，rd=s3/rs1=s2/rs2=a5，`th.mvnez`；前条SLTU判want<累计got，非零时把累计got夹到want|
|`b9c6 40fc160b`|op0b/f3=1/f7=32，rd=a2/rs1=s8/rs2=a5，`th.mveqz`；SLTU判filled<remaining，条件move取两者较小者|
|`b9ca 3c06360b`|op0b/f3=3、thmsb=30/thlsb=0，rd=a2/rs1=a2，`th.extu 30,0`；**跨缓存copy长度另保留低31位掩码**，不按普通min省略这条|
|`ba86 40f9160b`|op0b/f3=1/f7=32，rd=a2/rs1=s2/rs2=a5；未命中填充copy长度为unsigned min(filled,want)，该臂没有上述extu|

规则来源为主仓`evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc`的mveqz/mvnez/extu具体短规则；只读复用，无模型修改/运行，不提升成厂商硬件规格或整模型认证。以上32位加减和比较保留原宽度，不擅自改成64位，也不以本题扩异常巨大长度输入研究。

### 持有到既有归还

A37/A39与A47/A49已核constructor在消费头部之后`copy(O,W,0x664)`，因此W读取形成的当时H/D/C值及C+c持有关系进入O；复制不是再次申请C/B或复制B内容，也不是保存栈W指针。后续以O作reader会重用同C/B。正常替换时A47/A49的D+10回调后重读配置，对普通非零配置条件free(C+c)，随后free(C)，外层再free(O)。本轮首次填充的B正由同一个C+c字段接到该归还边，没有第二个buffer所有权根。

这是静态对象/字段合同，不证明实际一次打开/关闭成功、真实缓存命中、driver实例、页面DELETE或运行期资源复用。返回got指针始终是当前调用栈局部/可选调用者word，未保留到R/C，不转移所有权。

## 未闭精确边、恢复等级与验证

- 继承：mode1构造、W→O状态复制、owner持有、D+10归还及mode0借用均不重做。
- 本轮复核/纠正：已有mode门/真实call局部核验；旧语义纠正0、ISA规则/模型修改0。
- 真正新增：read五参及seek四参ABI、D槽、C/B填充持有/重读/消费量通道，到已有复制和归还的连接。精确库来源/标准库排除0。
- 未闭：具体D、D+14/+1c实际回调及其read/seek结果协议、H类型、真实source类型1照片、特殊配置0xffffffff、全部失败臂/文件系统/压缩解码/heap复用和最终DELETE继续未知。默认五ROM照片仍是mode0，不以本题通用callee的存在升级为实测mode1。

单一后续闭包：独立复核本题同reader前缀、D+14五参与D+1c四参、C+c申请/持有/归还身份，以及4个厂商字的计数边界；若再追功能，应先取得实际source类型1→具体D的原始绑定种子，不展开所有driver/文件系统。

[verify.py](../../analysis/photo-reader-consumer-a50-0041-20261024/verify.py)只读原ROM，以`offset=VA−0x9ffff000`核10个必要短窗口及2个稀疏厂商字，共348B、124条指令、59项字段/原编码/目标检查通过，厂商字4；[evidence.json](../../analysis/photo-reader-consumer-a50-0041-20261024/evidence.json)留存字节、短规则与旧record复用结果。未重导544B函数、资源或完整源码。JSON、报告链接和git diff --check另行核验；作者自检待独立技术复核。
