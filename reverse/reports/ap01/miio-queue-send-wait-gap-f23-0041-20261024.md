# F23：F11/8 send另一服务分支的旧caller ABI盘点

2026-10-24；认领 **F11/8**，作者 `/root/a56`；固定基线 `bd457a6`，独占 `re0041-f23` / `codex/re-0041-f23`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记首阶段仅查旧F13 caller/evidence及metadata；遵循主仓[流程](reverse-design.md)、[本地保留规则](../../analysis/README.md)和REA技能留存优先约束。

**旧caller没有把0xa0131920的返回值直接当M交copy。实际0xa0197af8以a0=K、a1=word(Q)调用；返回0在afc跳回0xa0197acc重试已知快速getter0xa01318de，非零则恢复mstatus并把该a0返回。只有快速getter非零结果才进入M→copy接线。** 未见显式构造的局部outM参数；word(Q)的类型/指向以及callee内部输出仍未知，不能先把它命名为outM或等待句柄。

首阶段只查旧caller，新ROM0B；定位缺口后先报管理者，再获准caller缺段22B与0xa0131920的200B状态/返回必要增量。本轮新增答案是该服务的counter重读、mode位/对象字段、opaque调用与返回原序，仍不展开定时send0xa0197b32、快速getter、三个下层服务或完整调度系统。未运行旧技术脚本、目标/指令/固件/模型、SIM/QEMU、构建、回放、异常输入、设备或外部服务；不切换共享REA、不改生产ROM配置模型或共享表，无下级agent、提交推送。生成JSON留原相对analysis路径并受Git忽略。

## 继承结论

|出处|已解释行为与本轮差集|
|---|---|
|[F11](miio-request-ownership-f11-0041-20261024.md)/F12|type1异线程提交以Q、`source=&局部I`、wait=−1调native adapter；I/请求与同步链持有直接继承，不重验|
|[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)，F11/3|0xa0197a8e的Q/F/K/source/n和候选M→copy/接链已解释；0xa0131920保持opaque。本轮只补已留caller的另一个flag/halfword门、实际call ABI和返回接线|
|F21/F22，F11/7|快速getter0xa01318de的正常来源是两gp链/条件申请，不能由非零推容量/寿命|不重复getter本体/取链/allocator；它在本题只是重试目标与候选M来源|
|旧whole-ROM索引|0xa0131920范围200B，无historical_dossier/dossiers/historical_contracts|extent/directcall不能证明“等待”语义或outM；本轮先登记后补本体状态/返回字段，不沿其下层body|

旧caller来源为主仓本地忽略 `reverse/analysis/miio-native-queue-f13-0041-20261024/evidence.json#/rows`，原厂字节静态留存、工具Capstone5.0.7 RV32/RVC，没有REA生产profile/EID。本轮独立解算其必要原字字段，不将旧raw改标成新ROM读取。F14 `review-result.json`沿其原profile/证据边界定位，不运行作者脚本。

原件身份沿F13/[CATALOG](../../../roms/CATALOG.md)：0041 `ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`；登记升级时仅校长度，不重算摘要。

## 本轮复核或纠正

不纠正F13/F14既验copy顺序或未知服务边界。需要消歧的是“服务是否输出M”的候选问题：caller观测只支持**零返回→重试getter、非零→原返回**，没有服务a0直接进copy的边；名称不能替代其body合同。也不能因为没有局部`&outM`构造就断言callee绝不会经word(Q)或其他对象写出消息，后者类型/内部行为未读。

所选F13 rows最初缺 `[0xa0197ad2,0xa0197ae8)`，F14已存必要检查也未给该段原字；报告后由管理者明确登记新22B补证。现已查明它设置 `(0xa062c874,line0x79,0)` 并AUIPC/JALR到 **0xa0019672诊断边界**。不是普通getter失败返回；不能沿线性后续a0197ae8假定诊断返回、Q仍保留a0或寄存器仍为入口值。旧“缺片段”仅描述当时所选载体，不是全局不存在代码。

分析中独立AUIPC/JALR核算纠正过两个下层目标的速报次序：实际a0131996/199a→a002772e(T,1)，a01319a8/19ac→a00272d4(T,K+8)。最终脚本和本报告采用独立字段结果；这是本轮分析预期纠正，不是原件或旧已验语义错误，未改模型。

**旧caller覆盖强度需纠正。** F21/F22关于“caller先读flag非零才调用getter，稳定flag时不走332B申请”的判断，只适用于 **0xa0197aca直接落入0xa0197acc** 那一条边，不能当作该caller全部正常进入getter的条件。本轮独立复核旧原字 `0xa0197af0=e34ef7fc`，B-format字段为signed BLT(a4,a5)→0xa0197acc；这条边在flag零且LH(K+0x22)<LH(K+0x20)时正常进入getter。因此 **flag稳定为0、第一链为空时也可进入F21既有332B申请分支，无需flag变化**。另外服务零返回也经afc重试getter。F21/F22的getter本体三臂、地址来源/容量局限保持不变，只纠正caller前驱边的覆盖强度；原冻结文件不改，本轮保存新连接和原字段供F24复核。这不是原件缺陷或输入实验结论。

## 真正新增：旧caller的精确分支/寄存器合同

定义沿F13：Q为native queue，F=word(Q+0x0c)，K=word(F+0x18)，source为原源指针，n为word(Q+0x18)。这些不是F11栈descriptor的同名字母。原字只作静态字段解算，没有执行路径：

|旧地址|实际连接与界限|
|---|---|
|`0xa0197ab8/7aba`|s4保存n、s3保存原source。后续服务调用前不先解引用source取得I，不换成&source|
|`0xa0197abc/7abe`|按既验原序保存mstatus并清mask8。只继承寄存器操作，不认证完整锁/并发系统|
|`0xa0197ac2/7ac6/7aca`|LUI/LW解得flag=word(0x62fc6034)；flag零跳0xa0197ae8，非零走快速getter。不能从MiIO线程名称推实际flag值|
|`0xa0197ae8/7aec/7af0`|分别signed LH K+0x22与K+0x20；若前者小于后者，BLT到0xa0197acc调快速getter；否则进入下述服务调用。没有把两者改成unsigned或把“未小于”先命名为队列满|
|`0xa0197af4/7af6/7af8`|直接flag零路线此前a0仍为原Q；C.LW a1,0(a0)取得word(Q)，然后a0=K，JAL独立算得0xa0131920。a1不是Q、source或&局部M|
|`0xa0197afc`|C.BEQZ a0→0xa0197acc；即服务返回零才重试快速getter，非零落到共同restore，不把它直接解释为成功或失败状态枚举|
|`0xa0197afe..7b10`，继承F13/F14|恢复mstatus/保存寄存器并返回，服务非零值a0沿此返回；adapter再按既验符号折叠。没有把该a0保存为M或copy参数|
|`0xa0197acc/7ad0`|快速getter返回非零才跳0xa0197b12；零落入旧rows最初缺失、后经登记补证的line0x79诊断边界，不能当普通失败继续|
|`0xa0197b12..7b1a`|getter的M移a1；s4→a3=n，s3→a2=source，s1→a0=K，调用0xa01949f0。copy/interface的真正来源仍是这条M接线，不是0xa0131920返回值|

实际callsite处完整寄存器可知域与正式ABI必须分开：

|寄存器|直接flag零路线的已知值|ABI限制|
|---|---|---|
|a0|K|明确构造的首寄存器输入|
|a1|word(Q)|明确加载，类型/是否为句柄或输出指针未知|
|a2|原n仍在|caller没有在此重写；不能认证callee真的把它当第三参数|
|a4/a5|分别为sign-extended LH(K+0x22)/LH(K+0x20)|是比较遗留值，不擅自加入正式参数表|
|a3/a6/a7|所选caller路线未赋新值，无法指定对象/数值|正式参数总数仍未知，不写“全部其余参数为0”|
|s3/s4|source/n|普通callee保存约定成立时跨该服务与getter保留数值，之后传copy接口；不由此保证所指源区域一直有效|

因此本caller静态保留的是**源地址和长度的寄存器值**。callee是否阻塞、是否临时/持久保存源或其他对象、是否改Q/K、真实调用期间源栈的寿命，仍需新body/对象证据。不能把名字“wait”写成已观察等待，也不能把caller寄存器保存等同callee无内存副作用。

局部伪代码（非原源码，缺段和opaque语义保留）：

```c
saved_source = source; saved_n = n;
if (word(0x62fc6034) == 0) {
    if (signed16(K+0x22) >= signed16(K+0x20)) {
        r = opaque_a0131920(K, word(Q), /* formal remainder unknown */);
        if (r != 0) goto restore_and_return_r;
    }
}
M = known_getter_a01318de();
if (M == 0) goto getter_zero_diagnostic; // 升级已核：path/line0x79 -> a0019672
opaque_a01949f0(K, M, saved_source, saved_n); // 继承copy/发布界面
```

### 登记后的服务状态与返回增量

新原字段工具为独立RV32/RVC位域检查；探索用Capstone5.0.7只解普通指令。曾有固定小窗落在指令中部的预览，已丢弃并从0xa0131920按编码宽度重新定位；没有采用该中部解码、NOP化未知字或改模型。以下只恢复本函数状态/返回和下层调用端，不读下层body。

|地址|正常状态、原序及边界|
|---|---|
|`0xa0131938/193a/1944`|保存K到s2、mode=`a1 & 0x40`到s3、s7=K+8；不把位0x40命名为正式O_NONBLOCK。s3是本callee自己的mode寄存器；原caller的source/s3已在prologue保存|
|`0xa0131948/194c/1950`|每轮重新signed LH(K+0x22)、LH(K+0x20)；前者小于后者时a0=0到尾声，未小于才到0xa0131958。两次计数可随下层调用改变，不能沿首次比较缓存|
|`0xa0131958/19e4`|mode非零直接a0=−11到尾声。这里返回的是本函数常量，不认证系统错误枚举/线程状态|
|`0xa013195c/1960/1964`|mode零时s4=0x62fc6c18，T=word(s4)，SW K到T+0x44。这里没有T非零门，正常有效T是前提；不将T与G27某次运行对象认同|
|`0xa0131968/196c/196e/1974`|U16(K+0x10)读出后+1、SH写回；再SH0到T+0x22。只认证原width/顺序，不给字段追加资源所有权解释|
|`0xa0131972/1978`|word(T+0x0c)>0的signed门才直达0xa0131992；其他分支设置诊断参数后调用a0019672。不能穿越诊断假定正常寄存器保持|
|`0xa0131992..199e`|以a0=T、a1=1交 **0xa002772e**，保存其返回值到s8。剩余正式参数/副作用未知，不按名字定义调度语义|
|`0xa01319a0..19ac`|先SB8到T+0x1c，再以a0=T、a1=K+8交 **0xa00272d4**。保留先写byte再调用的原序，下层是否阻塞/排队/修改对象均未知|
|`0xa01319b0..19be`|s8=0跳过第三服务；非零时重读word(0x62fc6c18)作a0，以保存T作a1交0xa001ad30。不把重读global当恒定T；三服务body全部opaque|
|`0xa01319c2/19c6/19c8`|signed LH(T+0x22)到a0；零回0xa0131948重读K两半字；非零返回其32位相反数。若原halfword为负，相反数可为正，不能改写成所有非零都为负错误码|
|prologue/epilogue|实际保存并恢复原caller s3/s4；本callee正常返回且下层遵守普通ABI时，外层source/n的寄存器值维持，之后重试getter/交copy。不是源区域有效性或callee不存指针的证明|

该本体没有构造M返回或outM槽；正常返回值来源是0、−11或所读signed halfword的相反数。它对K/T字段及opaque服务的作用可能影响后续状态，但没有取得M的本层直接边。只有caller零返回重试getter之后，getter非零才进入继承copy；旧outM候选据此撤销，不作为原件语义错误。

局部伪代码（非原源码，服务正常返回和有效对象前提保留）：

```c
mode = word(Q) & 0x40;
for (;;) {
    if (signed16(K+0x22) < signed16(K+0x20)) return 0;
    if (mode != 0) return -11;
    T = word(0x62fc6c18);
    word(T+0x44) = K;
    halfword(K+0x10) = u16(K+0x10) + 1;
    halfword(T+0x22) = 0;
    if (!(signed32(T+0x0c) > 0)) diagnostic_boundary();
    r = opaque_a002772e(T, 1);
    byte(T+0x1c) = 8;
    opaque_a00272d4(T, K+8);
    if (r != 0) opaque_a001ad30(word(0x62fc6c18), T);
    h = signed16(T+0x22);
    if (h != 0) return -h;
    // 下一轮必须重新读K的两半字；不证明循环必结束。
}
```

新增是已登记服务的正常状态/返回及caller诊断边界合同，不是新业务、完整调度/等待系统或库来源认证；无新反编译、ISA规则或整库排除。source指针和n在外层callee-saved寄存器/本层保存栈的值保持，不认证底层阻塞行为、源内存寿命、并发或最终消息交付。

## 未闭精确边、检查与后继

0xa0131920的旧extent EID `ev_1bec9a08b90ab3a5a5e5df3aebd762aca00d8189db3a3050492eb9af24e4d5d3`，范围0xa0131920..0xa01319e7（200B）；directcall EID `ev_3c7ff280f2e61f99733408917fc04191f5ab1220ee3137e9dbaa342361b3419c`列0xa0019672/0xa001ad30/0xa00272d4/0xa002772e，仅作metadata定位，未沿任何callee取证。

仍未闭：三下层服务对K/T/同步对象的实际持有/副作用/返回语义、T/global writer和生命周期、真实mode/flag/counter状态、循环进展与异步保证、source实际存储寿命、getter零后诊断是否返回及其寄存器合同、实际M取得/copy/consumer执行。不能把局部状态恢复升级为caller栈无条件可失效或队列交付成功。

唯一有种子后继为原 **F11/8** 下非作者限定复核：核旧caller的7af0/7afc getter回边及F21/F22 guard覆盖范围纠正、新22B诊断边界、服务signed重读/mode/返回三域和三opaque调用的实际目标/原序，不读三个下层body或全调度。本作者已回报精确下层callsite，但管理窗口要求在此收敛，没有自行派生新callee研究。

[reuse.py](../../analysis/miio-queue-send-wait-gap-f23-0041-20261024/reuse.py) 首阶段实际 **27项PASS，22条旧rows，新ROM0B**；初始 [evidence.json](../../analysis/miio-queue-send-wait-gap-f23-0041-20261024/evidence.json) 冻结当时缺段/未取body状态，不能脱离后续增量当最终未知。其后获准 [verify_increment.py](../../analysis/miio-queue-send-wait-gap-f23-0041-20261024/verify_increment.py) 实际 **49项PASS，53条必要指令/170B样本**，包含22B caller诊断及200B服务中的必要状态/返回/调用锚点；探索覆盖已登记22B+200B，固定窗重读另有重叠，不把170B当全部曾读字节。新 [increment-evidence.json](../../analysis/miio-queue-send-wait-gap-f23-0041-20261024/increment-evidence.json) 保存原字段/偏移和opaque边界，均本地忽略。

两阶段JSON、相对引用、Git忽略和diff检查通过，不运行F13/F14作者脚本、不新开REA/复制大导出。交付后停止本项，供管理窗口独立复核/补位；作者自检不是非作者验收，无提交推送。
