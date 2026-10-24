# F21：F11/7 候选消息M的链节点来源与容量边界

2026-10-24；认领 **F11/7**，作者 `/root/a56`；固定基线 `bd457a6`，独占 `re0041-f21` / `codex/re-0041-f21`。主仓[唯一认领表](rolling-management-0041-20261023.md#链条认领表)已登记本题及必要增量：先核F13真实调用端，再核0xa01318de；发现两个gp链参数后先报管理者，获准只补 `0xa010d70e(gp+0xb8/gp+0xc0)` 的取节点/返回原字段。0xa002fcc8仅保留请求接口，不读allocator、池初始化、等待/调度或完整heap。

**M并不由K+0x24 guard或n决定分配。0xa01318de先从以gp+0xb8为哨兵的链取尾节点，非零直接返回；空则重读word(0x62fc6034)，非零改从gp+0xc0链取节点并直接返回，零则向0xa002fcc8请求0x14c(332)B，非零时仅标byte(M+8)=1后返回。** 链helper会摘除节点、清其两个链word并返回节点值。链初始化/节点大小未知；332B也只是申请值，不能直接认证M有效、容量充分、不别名或独占寿命。

遵循主仓最新[流程](reverse-design.md)、[本地保留规则](../../analysis/README.md)及REA技能。未运行作者/旧技术脚本、目标/指令/固件/模型、SIM/QEMU、构建、回放、异常输入、设备或外部服务；不切换共享REA、不改生产ROM配置模型或共享表，无下级agent、提交或推送。只读主仓留存与获准必要原字段；新JSON本地原路径忽略保留。

## 继承结论

|出处|已有行为与局限|本题差集|
|---|---|---|
|[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)，F11/3|正常候选M来自0xa0197acc→0xa01318de；非零后以 `(K,M,source,n)` 交0xa01949f0，再copy(M+0x0c,source,n)及接链。消息M与本manager M不是同一命名对象|只继承调用端/消息交接，不重验copy、队列接链、计数/notify或I业务|
|F11/4–5相关工作|正常setup size4、copy n4等是独立问题|不能由queue size4或copy域推目的M的容量/来源；本题不接这些算法/状态证明|
|[G11](display-ready-producer-g11-0041-20261024.md)/[G12](display-producer-review-g12-0041-20261024.md)|另一backend的+0x3c空闲链调用0xa010d70e；整池分配/析构未恢复|其留存仅caller连接，没有本体字段合同；不能把backend+0x3c当本gp两链、套该节点大小或ownership|
|旧whole-ROM索引|0xa01318de范围66B，0xa010d70e范围42B，均无historical_dossier/dossiers/已验合同|extent/directcall只是定位；本轮获准补必要正常来源和无callee链helper，不从函数名认证分配器|

原件身份沿[CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；映射`file_offset=VA−0x9ffff000`。只核长度、继承摘要，不重算哈希或混其他基线。

旧metadata来自主仓忽略 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json`：0xa01318de extent EID `ev_1f1e3392319d6066dfa0ec7153bc38011175d4593b14a5c98911e7e25e0ddfc8`、directcall `ev_bf2124b1c8f7a4884a8d71ba4cc962d18dc9ee9e7b0e244fb5be4ac81c9ae0e8`；0xa010d70e extent `ev_307bfa85996bc49ba8033818c20586927cfad86def6317ebd4804f3be509ed03`、directcall `ev_460634c36b25a27df15c7629aa1ba0823995e3bc867a320cfd2a893f3fe38c0f`（无callee）。旧profile不重标，新原字段证据没有伪造REA ID。

## 本轮复核或纠正

F13/F14的opaque边界没有语义错误。本轮将正常M来源缩小为具体两条链及一个有条件申请接口，**没有把“非零候选”提升为有效容量/独占对象**。精确caller旧字直接从F13本地忽略evidence.json必要rows复用，不重跑其脚本：

- 0xa0197a8e以Q读Q+0x0c；所选正常前缀至0xa0197acc没有列出a0的普通覆写。因此call时a0仍是原Q，a1/source及a2/n也不能被误写成新分配尺寸。
- `0xa0197ac2/7ac6/7aca`先读 **word(0x62fc6034)**，非零才落到0xa0197acc；本体入口随后**明确覆盖a0为gp+0xb8**，不以这个原Q/a2尺寸直接分配。
- 0xa0197ad0接受非零结果，0xa0197b12将其移a1=M，之后a3=n、a2=source、a0=K再调0xa01949f0。M不是源指针、`&source`或原Q本身。

本体在第一链返回零后又读取同flag。若两次flag稳定且第一链操作不通过别名影响它，则这个已验caller进入时flag非零，本次会走第二链而不走332B申请。**本题没有证明flag稳定、链地址分离或无异步修改，故不能把申请分支对本caller的可达性当已发生，也不能排除其条件路径。** 保存重读和实际分支，比给getter强行命名为单一allocator更精确。

G11/G12使用同helper但其池对象不同，不能以节点名或helper地址相同合并身份。先查两份旧合同/脚本窗口及index，确认未留本题helper正文合同，再按管理批准取42B必要分支。没有新下层callee或模型规则。

## 真正新增

### 返回来源与原序

|地址/原字段锚点|参数、门与返回合同|
|---|---|
|`0xa01318e6/18ea`|a0=`gp+0xb8`；JAL→0xa010d70e。没有把Q/K/n传作池尺寸或对象。gp绝对值和链对象初始化未认证，继续用gp相对身份|
|`0xa01318ee`|返回a0非零到0xa0131902尾声，原值返回；第一链成功时不读本体flag、不调用第二链/申请服务|
|`0xa01318f0/18f4/18f8`|第一链空返回0才以LUI/LW重读word(0x62fc6034)，flag零→0xa013190a，非零落到第二链|
|`0xa01318fa/18fe`|a0=`gp+0xc0`；JAL同0xa010d70e，随后直接共同尾声。第二链空时直接返回0，**不再转332B申请**|
|`0xa013190a/190e/1912`|只有上述flag零路径设置a0=0x14c，再AUIPC/JALR→0xa002fcc8。这是固定332B请求，非由queue n/K+0x24计算，allocator内部保持opaque|
|`0xa0131916/1918/191a`|申请返回0直接尾声；非零设a5=1，SB到返回地址+8，再汇尾声。不会在本层清M整块或认证分配根大小；不为byte标记赋正式释放策略名|
|`0xa0131902..1908`|恢复ra/s0/sp后JR ra，未写a0；返回服务的原指针数值，无局部地址转义、额外retain/free或本层payload复制|

### 两gp哨兵链取节点

记H为实际传入的gp+0xb8或gp+0xc0，N/P/R为当次读值；仅在这些正常链指针有效及服务ABI成立时表达：

|地址|必要行为|
|---|---|
|`0xa010d714/716`|N=word(H+4)，若N==H则跳0xa010d734把返回候选置0；这是哨兵空链判定，不是N==0门|
|`0xa010d71a/71c/71e`|先取P=word(N+4)，再取R=word(N+0)，把R写到P+0|
|`0xa010d720/722`|**重读N+4**取得P，再把P写到R+4；不把重读优化为首次P恒定值|
|`0xa010d724/728`|依原序先SW0到N+4，再SW0到N+0，摘除节点的两条链字段被清零|
|`0xa010d72c..732`、`734/736`|恢复s0、a0=N、恢复sp并JR；空链a5=0也汇此尾声。helper无callee，不申请/复制节点，不另保留调用者参数或给出大小|

因此从第一或第二链成功返回的M是这个当次被摘出的节点N的原地址，不是N+0x0c、不分配新节点或转移源payload。两个word清槽/邻接修复说明链上解除连接；不能由此证明全系统没有其他别名或已获独占所有权。F13随后以同M作消息header并使用M+0x0c是继承连接，本题不再重验接链和释放。

局部伪代码（非原源码）：

```c
M = remove_last_from_sentinel(gp + 0xb8);
if (M != 0) return M;
if (word(0x62fc6034) != 0)
    return remove_last_from_sentinel(gp + 0xc0); // 空则直接0
M = opaque_a002fcc8(0x14c);
if (M != 0) byte(M + 8) = 1;
return M;

// remove_last_from_sentinel(H)，保留原重读/清槽顺序：
N = word(H + 4);
if (N == H) return 0;
P = word(N + 4); R = word(N);
word(P) = R;
P = word(N + 4);
word(R + 4) = P;
word(N + 4) = 0; word(N) = 0;
return N;
```

### 可定位的容量及持有边界

两链helper没有node stride、payload长度或分配尺寸字段，故不能认证M+0x0c之后有多少字节。申请分支只见0x14c请求；仅在另有allocator“正常返回至少该连续请求区”的合同及地址有效性时，才可算请求区从+0x0c起的名义剩余 **0x14c−0x0c=0x140（320）B**。本题未取该allocator body，不把算式升级成实际可写容量，也不套到两链节点。K+0x24 guard是继承的queue尺寸门，不建立池node容量。

getter直接把N/申请服务返回值交caller，没有本层最终归还。链摘除不证明M独立于source/Q/K、有效对齐、容量充分或持续有效；无src持有也不是释放M/源栈的授权。Msg+8标记用途、节点回收/再入池/queue关闭及consumer持有仍未知。

新增恢复为 **该正常候选服务的两链/条件申请来源、摘链/清槽/原值返回及请求尺寸边界**；不新增业务、ISA、完整heap、来源认证或整库排除。两个小helper原件合计108B仅覆盖本题所需返回候选来源，无全库或任意分配器扫描。

## 未闭精确边、检查及后继

未闭：gp绝对值与两哨兵初始化/节点填充、节点存储来源和大小、池访问同步及独占/别名、flag跨读稳定、申请服务的实际容量/对齐/寿命、Msg+8的释放策略、实际候选实例/queue发布/consumer执行。不能由非零M/size4/摘链推定目的存储安全或caller栈失效；不由本题推任何缺陷或异步试验。

唯一有种子后继优先为本 **F11/7** 下的非作者限定复核：核0xa01318e6/18fa两gp身份、flag重读/第二链空直接返回、332B请求与+8标记、0xa010d714..736哨兵/邻接重读和清槽。若另追容量，需以**gp+0xb8/gp+0xc0节点初始化写入者**的新可定位证据登记，而不是展开完整heap；本作者未取初始化/allocator新body。

[verify.py](../../analysis/miio-queue-message-source-f21-0041-20261024/verify.py) 实际 **52项PASS，41条必要普通指令、108B**：66B候选服务及获准42B链helper，独立RV32/RVC字段/分支/JAL/AUIPC-JALR、word/byte宽度、原值返回及caller旧行接线。两个小函数各正常返回分支均为本题必要来源，不复制大dossier；未运行旧脚本、目标或模型。探索对66B函数有2B边界重叠读，对42B函数按指令补齐，复验字节数指唯一必要样本，不冒称全部I/O字节。

本地忽略 [evidence.json](../../analysis/miio-queue-message-source-f21-0041-20261024/evidence.json) 保存VA/文件偏移/原字/独立字段及旧caller/index出处；无新REA ID或profile。JSON、相对引用、Git忽略与diff检查通过。作者交付待独立复核，交付后停止本题，无提交推送，供管理窗口整合/补位。
