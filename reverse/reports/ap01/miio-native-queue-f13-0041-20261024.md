# F13：MiIO native queue 正常 −1 路线的源指针消费边界

**已证调用原序：adapter 不复制源，而是把原 `&局部I` 与 `word(Q+0x18)` 长度传下去；正常下层先调用 `0xa000589c(M+0x0c,source,length)`，返回后才把候选消息 M 接入队列并改计数。尚不能无条件断言“同步复制4B I指针、caller栈可立即失效”。** 同一个Q的实际长度是否4、该输入所需的copy算法分支，以及M独立有效存储/寿命仍未认证。既有copy合同只明确对齐16/20B，不能因为函数名把它扩为任意长度。

2026-10-24；认领 **F11/3**，任务F13，作者 `/root/f12`；独占工作区 `re0041-f13`，分支 `codex/re-0041-f13`，固定基线 **`bd457a6`**。历史 `32f9c9e` 已按用户清理要求重写，本轮不移动基线。权限取自主仓[管理记录](rolling-management-0041-20261023.md)的“当前三席持续滚动”、F11/3行和两次必要增量登记，不以worktree旧表授权。采用 `reverse-engineer-anything` 技能，遵守最新 [reverse-design](reverse-design.md) 与[分析材料保留规则](../../analysis/README.md)。

仅写本报告及同名analysis的复验源码/语义合同；逐指令 [evidence.json](../../analysis/miio-native-queue-f13-0041-20261024/evidence.json) 生成物按忽略规则留在原相对路径，不要求提交。没有运行目标/指令/模型、固件、构建、SIM/QEMU、旧技术脚本、历史回放、设备或外部服务，没有切换共享REA或修改生产/ROM/配置/分析器，没有提交、推送、共享表修改或下级agent。作者交付待独立复核，不自称已验。

## 继承结论

|已有出处|已有行为与局限|本轮精确差集|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[upper-layer](upper-layer-0041-20261017.md)、[J06](miio-reuse-gap-j06-0041-20261024.md)|业务及event-loop既有覆盖，SIM替代不认证ROM native queue持有|不重做整个event-loop、页面/协议或SIM；本轮只追已明示的native断边|
|[F11](miio-request-ownership-f11-0041-20261024.md)/[F12非作者复核](miio-request-ownership-review-f12-0041-20261024.md)|I为独立invocation，payload含ctx/R；异线程分支在 `0xa011e33e` 以 `(word(loop+0x18),&局部I,−1)` 调 `0xa005f464`。同步链/worker持有已经限定接受|caller/I原样继承；不再重验D/Q/R构造、P匹配或S消息回调，不把source栈地址先认作已复制|
|[G03](invalidation-submit-g03-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)、[G21](pogo-poll-submit-g21-0041-20261024.md)/[G22](pogo-poll-submit-review-g22-0041-20261024.md)|`0xa000589c(dst,src,n)` 的正常分离、word对齐16/20B路径复制值，不持有源地址|只继承该域；B25/B26等其他调用端沿用copy接口，不构成任意length/本题4B算法认证；不重复1080B优化复制体|
|旧 whole-ROM 索引 `functions[1460]`、`[5812]`、`[5771]`|分别定位0xa005f464、0xa0197a8e、0xa01949f0，均无dossier、historical_dossier或已验本体合同|index只定位；不以extent或NuttX路径候选认证未改源码/ABI|

本题原件沿 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未重算机械摘要。映射 `file_offset=VA−0x9ffff000`；不是0031、unsigned候选或SIM ELF。

只读留存为主仓 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json`，保留原profiles `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`、`f71eaf7d63ce1b1fa1671fe1932e6a44e275d3716b51411a6bb6af26d7663a44`，不重标为同一profile：

- 0xa005f464，164B extent Evidence `ev_885ec6714c8dadd8a5641aa8ca23686fdae9921c3acef0ff70e91eadbfba6b4b`，directcall `ev_77434d7b28ab30c461a4b24bbd9438261a04a9978f1019e25b373d169ad0f31c`。
- 0xa0197a8e，164B extent `ev_aaac834ca5517d5c164e349c0d36d5245cc3349a46e0a8237d67ceac53f22671`，directcall `ev_5d23fe72e011665622e34aeace14710a8acb136cb50b5f1c18f681df13c0c075`。
- 0xa01949f0，366B extent `ev_0751127317c476184b3aba94117fc0100d4c9571ee5a7727db3e803153974b25`，directcall `ev_8a1e2637df7b7cf726e4ee25b3733ba7ef10f05364b4c3e1ce719865c267a0e7`。

以上是继承元数据，不充当本轮语义证据；本轮由原字节/独立字段得出的JSON没有新造REA Evidence ID。搜索边界为上述父级、近期AP01 Markdown精确地址和旧callee元数据；有限搜索无合同不等于全局不存在源码或研究。

## 本轮复核或纠正

**精度收紧：把“copy接口调用事实”与“该输入已证同步复制”分开。** 发现下层调用0xa000589c后，先核旧合同，确认16/20B限定域；本报告不把本题未知length套用该域。没有改写F11/F12原合同，没有新增库排除或ISA规则。

调查按管理者两次登记扩大，未自行沿新callee：初始只0xa005f464正常−1路线；发现 `0xa005f480/484→0xa0197a8e` 后先报实参和旧extent，获准其源/长度消费；再发现 `0xa0197b1a→0xa01949f0`，先报实际四参和旧extent，获准该callee正常copy/接链/返回原序。0xa0197b32定时路线、0xa01318de候选消息服务和0xa0131920等待服务本体均未展开；下层通知/唤醒/调度服务同样opaque。

本轮观察为原厂字节静态解码/位域，不是执行。工具 **Capstone 5.0.7，RV32+RVC**；没有厂商未知字或模型修改。探索读为adapter64B、首个获准callee164B（按控制流三段读）、第二callee稀疏236B，合计464B；没有读取0xa000589c本体。复验源码只记录语义必需的334B样本，不重复保存诊断窗口或整366B/1080B函数导出。[verify.py](../../analysis/miio-native-queue-f13-0041-20261024/verify.py) 实际 **54项PASS**，含两组独立AUIPC/JALR及三条独立JAL目标；每个样本有原字/VA/文件偏移，全部普通指令完整解码。探索范围与复验范围分别列明，不把334B当全部曾读字节。

## 真正新增

对象只按实参定义：`Q=word(loop+0x18)` 是本caller所传queue对象；`F=word(Q+0x0c)`、`K=word(F+0x18)` 是本次下层加载得到的对象；`S=&caller局部I指针`，`n=word(Q+0x18)`；`M` 是opaque服务返回的非零候选消息。本题Q/S与F11的descriptor Q/response S不同对象，不因别名相同混用。

|连接/地址/原字段锚点|参数、顺序与返回的已证事实|
|---|---|
|0xa005f464..0xa005f484|先对a0空门；a2与−1比较。本实际−1路线不写/不解引用a1，`104d`在0xa005f47e以 `LW a2,0x18(a0)` 替换wait参数为n；AUIPC/JALR独立解到0xa0197a8e，实参 `(Q,S,n)`|
|0xa005f488..0xa005f496|下层返回后恢复保存寄存器，`7d85` 在0xa005f492算术右移a0,31，保留符号折成0/−1；不是原下层状态码逐值返回，也不是consumer已执行证明|
|0xa0197a8e..0xa0197aba|先取F=word(Q+0x0c)，再K=word(F+0x18)；检查S/K非空、Q首word的bit mask2，读取 **U16(K+0x24)** 比n，n超过它走错误返回。s4保存n，s3保存原S，未加载`word(S)`|
|0xa0197abc..0xa0197ad0|以mask0x8通过CSRR C指令保存原mstatus并清相应位；调用opaque0xa01318de，非零返回跳0xa0197b12。这里的M只称候选，不由名称预设分配/所有权算法|
|0xa0197b12..0xa0197b1a|a1=M，a3=s4=n，a2=s3=S，a0=K；JAL目标独立解为0xa01949f0。源地址仍以值传入，不是在此先读出I指针|
|0xa0194a00..0xa0194a18|保存M/K；a1=S、a2=n；**SH n到M+0x0a**，**SB0到M+9**，a0=M+0x0c，再调用0xa000589c。准确三参是`(M+0xc,S,n)`，不是`(M+0xc,I,n)`或`(M+0xc,&S,n)`|
|0xa0194a1c..0xa0194a4a、0xa0194ac0..0xa0194ad8|copy接口返回后才读K+0x1c及K+0x18 sentinel、选择链插入点。消息M的+0/+4写链指针；队列/相邻节点写入的是M，而非S。最后 **LH K+0x22，+1，SH回同槽**；没有把消息长度word或count宽度合理化改写|
|0xa0194a60..0xa0194a64、0xa0194ada..0xa0194ade|接链后的通知门读K+0x28与−1比较，另一门读取signed halfword K+0x12。其服务本体/通知结果保持opaque，不据门值猜运行实例|
|0xa0194b3c..0xa0194b4c、0xa0197afe..0xa0197b10|所取共同正常尾声明确a0=0再返回；上层恢复原mstatus，恢复寄存器后返回，其后adapter折符号。其他通知/唤醒臂没有本轮完整展开；“进入并返回这个共同尾声”是本句前提|

原a1指针在本次adapter中不被直接归还/挂链；进入下层后，正常路径先把它作为copy接口的源，再发布M。**事实是这个接口和顺序；若S、M目的区有效分离、对齐/容量及n满足旧已验copy域，则可进一步推导在copy调用返回前按该域复制值、非持有S作为payload。** 本题没有证明这些运行前提，更没有证明n为4，因此还不能把条件推导升级为本caller栈可失效的无条件结论。

局部伪代码（非原源码，不省略opaque边界）：

```c
// F11 caller继承：S=&局部I；实际wait=-1。
n = word(Q + 0x18);
r = service_a0197a8e(Q, S, n);
return arithmetic_shift_right_31(r); // 0或-1

// 正常检查通过、候选服务成功返回M的分支；服务语义并不补猜。
F = word(Q + 0x0c); K = word(F + 0x18);
check_source_queue_flags_and_u16_size_limit();
saved_status = clear_mstatus_mask_8();
M = opaque_a01318de();
if (M != 0) {
    halfword(M + 0x0a) = n;
    byte(M + 9) = 0;
    copy_interface_a000589c(M + 0x0c, S, n); // 仅接口；copy域限制保留
    link_message_M_into_K();                // +0/+4链；非直接挂S
    halfword(K + 0x22) = signed_halfword(K + 0x22) + 1;
    opaque_post_link_notifications_and_waiter_services();
    // 观察到的共同正常尾声返回0；其他臂完整行为未恢复。
}
// 其他正常等待/错误返回依边界保留；本轮未恢复完整队列服务。
restore_mstatus(saved_status);
return service_result;
```

新增的是 **source从adapter到具体copy接口/候选消息发布的接线** 及原返回折叠，不是新恢复I业务或整个消息队列；没有新增标准库排除、并发保证或实机成功结论。G19/5的op3环、J08/3的registry writer与本Q/F/K/S/M没有已证身份交集；共享通用copy节点不构成同题研究。

## 未闭精确边

1. **首要未闭：同Q的 `word(Q+0x18)` 是否确为4。** caller从loop+0x18取Q并不认证Q.size，更不认证这个对象与某个相似queue实例相同。
2. 0xa000589c对本题实际n及S/M地址形状的算法域；旧对齐16/20B合同不能推4B/任意长度。没有helper域认证时，本轮只得到同步调用copy接口的事实，不无条件承诺复制效果。
3. M来自opaque服务，独立有效目的存储、对齐/容量、分配/释放及消息复用时刻仍未知；K的队列初始化、并发/锁/发布、等待/唤醒、实际consumer执行和I最终消费不在本体闭包。
4. 下层通知/等待其他分支的完整返回/状态；adapter的0/−1只能说明当前折叠，不能证明投递或业务成功。

一个有种子的后继：以 **`Q=word(loop+0x18)`、本体n=`word(Q+0x18)`** 为已知两端，先由管理窗口查重并登记“同Q初始化/创建时的size写入与loop保存身份桥”；先读旧initializer留存，不无种子扫描。只有绑定实际size后，才依据该输入决定是否另登记0xa000589c的4B等必要正常分支。这里没有展开初始化writer或复制算法，也不把报告标题当扩范围授权。

必要语义合同见 [contract.json](../../analysis/miio-native-queue-f13-0041-20261024/contract.json)。实际检查为54项静态字段/目标验证、JSON解析、报告引用在主仓或本独占输出中可定位、独占改动和`git diff --check`；没有重新跑F11/F12/G03或历史技术脚本。作者交付后停止，源码/合同/报告未提交，生成JSON按本地忽略规则保留，待非作者复核。
