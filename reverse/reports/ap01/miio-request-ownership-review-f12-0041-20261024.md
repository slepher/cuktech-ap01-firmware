# F12：MiIO 请求持有与回调消息寿命的非作者复核

**限定接受 F11/1、F11/2 本轮差集，语义纠正0、新增业务功能0。** 栈 descriptor 的字段与正常非空消息在提交前进入独立请求 R；独立 invocation I 的 payload 保存 `{ctx,R}`。session P 保存同一个 R 指针；正常首个匹配后，callback 从 R 取得函数/user，却接收另一个 response S 的 `S+4` 视图。callback 返回后，正常完成路径才依次归还 P.R、P 和 S。R 消息可在此前的 worker 分支先行归还，不能把 R 对象寿命等同于 R 消息寿命。

2026-10-24；非作者复核者 `/root/f12`，独占工作区 `re0041-f12`，分支 `codex/re-0041-f12-resume`，固定基线 `32f9c9e`。原认领为 **F11/1、F11/2**，不是另开同题研究。权限依据是主仓[管理记录](rolling-management-0041-20261023.md)顶部“当前三席恢复”及两行的 F12 本轮复核状态；独占 worktree 中的旧停止表不作授权。本报告遵循主仓 [reverse-design](reverse-design.md)，采用 `reverse-engineer-anything` 技能，只读留存和必要原字，不打开/切换共享 REA。

本轮只写本报告及[同名 analysis](../../analysis/miio-request-ownership-review-f12-0041-20261024/review.py)。没有提交或推送；没有修改主树、共享认领、生产代码、ROM、配置或模型；没有执行固件/指令、模拟输入、旧作者脚本、构建、SIM/QEMU、历史回放、设备或外部服务，没有下级 agent。

## 继承结论

|已有出处|已解释行为|本次复核边界|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[upper-layer](upper-layer-0041-20261017.md)、[J06](miio-reuse-gap-j06-0041-20261024.md)|业务/SIM相应范围及旧完整 caller/send/constructor/callback 已留存，SIM 服务替代不认证 ROM 队列/云端行为|不重做页面、协议、绑定或完整业务；完整body存在不自动成为已验持有合同|
|[F11作者交付](miio-request-ownership-f11-0041-20261024.md)，整合 `4bff422`|F11/1 字段复制、I 持有和提前消息归还；F11/2 session 身份桥、首个匹配、S 视图与归还顺序|只独立核上述差集及必要继承前提；作者检查器不运行、不导入|
|`upper-complete.evidence.json` records `[13]`、`[142]`、`[204]`|请求分配0x3c、worker payload 接入及尾声返回0、旧请求归还服务|仅保留必要汇编行，见本轮 evidence 的 `retained`；不重导整函数|
|旧 type1 event-loop、32B pending-ID 和三参回执合同（F11继承表/J06）|type1 executor 正常返回非1后本地归还 I；另一种 pending 节点回调为 `(fd,message,length)`|直接继承，P/R/S/I 不套用32B pending或其他 loop/watcher 布局；不扩 native queue|

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，实读长度 **6,769,704 B**；身份继承 [CATALOG](../../../roms/CATALOG.md) 的 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，未另算机械摘要。映射为 `file_offset = VA − 0x9ffff000`；本结论不用于0031、unsigned候选或SIM ELF。

留存来源为主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`，profile digest `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。本轮读取的必要继承记录为：

- `[13]` / `ev_09ba96583c93925e0301a9306f6eadd2d3a1f14159f5682a40e236b7886125c7`：分配与 R 保存寄存器。
- `[142]` / `ev_6bef28a545502b1d067d8b5af289b13fa2bd4eb86a9cefd29cfb318ee59edb2a`：worker 取得 payload、条件边和尾声返回0。
- `[204]` / `ev_a02f78caa6ed020d619136ab3859dd193c2c2b10b8f6bb77630675f643c18b7f`：非空对象先条件归还 `+0x24` 消息，再以对象本身归还。

这些是继承 REA 证据；本轮 Capstone/原字段检查没有新造 REA Evidence ID。F11 所列 whole-ROM extent 仍只作定位，不凭范围补齐单函数语义。

## 本轮复核或纠正

[独立检查器](../../analysis/miio-request-ownership-review-f12-0041-20261024/review.py) 直接打开原件，按明确的稀疏窗口读取 **656 B**，以 **Capstone 5.0.7 / RV32+RVC** 解码235条普通指令，另独立拆分1处厂商word。**106项检查PASS**，包括13个独立 JAL 位域目标、两条独立 S-format word store字段。没有用作者脚本、作者断言函数或作者输出作为实际读取字节的替代。机器结果及全部读取边界见 [evidence.json](../../analysis/miio-request-ownership-review-f12-0041-20261024/evidence.json)；其中每条均有VA、原字和文件偏移。

|复核问题与锚点|独立观察（原厂字节/静态推导）|裁定|
|---|---|---|
|caller D 与适配 Q：`0xa01b6304..0xa01b632a`、`0xa0112052..0xa0112062`、`0xa011f9f0..0xa011f9f4`|callback 常量由 `lui a005f`/`addi 0x222` 形成，存 D+0x2c；user存D+0x30。适配读二槽，a1=D+4=Q；清零服务参数为 `(Q+0x10,0,8)`，然后调用构造|接受D/Q关系；不是原栈字段全部原样保留|
|构造 R：`0xa011f886..0xa011f890`、`0xa011f8f6..0xa011f952`|保存Q/cb/user到s2/s3/s7；Q.id→R+4、Q byte+0xc→R byte+0x10、8B Q+0x10→R+0x14。Q.len→R+0x20，非零分支以len+1申请并存R+0x24，再以source和len调用既有复制服务；cb/user写R+0x2c/+0x30|接受正常非空载荷复制与独立缓冲区；user只有word复制，不深拷贝对象|
|厂商尾字节：`0xa011f93a` 原字 `0b50f700`|独立字段为 opcode=0x0b/f3=5/rd=0/base=14/index=15/top5=0/shift=0；前两条加载a4=R.message、a5=R.len|接受与既有本地 `th.srb` byte-store规则相符的 `message[len]=0`；未独立认证厂商ISA规范，也未把未知字NOP化|
|I：`0xa011f622..0xa011f658`、`0xa011f674..0xa011f676`、`0xa011f992..0xa011f9a0`|8B payload导致 `((8+3)&~3)+0x18=0x20` 分配；dispatcher/type/loop/executor各槽按F11。payload=`(I+0x1b)&~3`，写ctx和R；提交调用目标为0xa011f84a|接受I独立于D/Q；不把异线程native queue的内部复制当已证|
|间接ABI：`0xa011f850..0xa011f856`、`0xa011f862`|先写I+0x14，再读I+4 callback；实际a0加4后 `c.jalr a5`，入口空槽门仍在|接受dispatcher实参 **I+4**；不能写为直接 `(I)`|
|R消息提前归还：`0xa011f79a`、`0xa011f818..0xa011f82e`|前服务非零分支到0xa011f818；R+0x34非零或R+0x24空均跳过。正常调用0xa002e14e后重读R，`23a20702`在0xa011f828和0xa011f82e **两次写R+0x24=0**，中间再次读payload.R|接受两门和重复清同槽；不是清长度+0x20，也不是归还R对象。构造a5=0时跳过写R+0x34，不能补猜默认零|
|session保存：`0xa011f73a..0xa011f740`、`0xa0119ca6`、`0xa0119d02..0xa0119d3c`|worker以 `(ctx,0,R)` 调0xa0119c8e；保存原a2于s5，写P+0x10=s5、P+4=ctx、P byte+8=kind；ctx+0x20空链置head，非空遍历尾部插入|接受P保存同一R指针，非另一份R或I本体；只认证这条正常保存连接|
|首个匹配：`0xa0119768..0xa0119786`、`0xa0116cf0..0xa0116d16`、`0xa01ab838..0xa01ab860`|`0xa0117000−0x316=0xa0116cea`；criterion含kind/id/out。predicate比P.kind及P.R.id，相等写out=P、返回−1；遍历用 `(P,criterion)`调用，取next后只有返回0才再调|接受首个kind0且id相等的P，拒绝外推同ID唯一性或某次运行实例对应。正确地址不是0xa0117cea|
|callback视图：`0xa011f6ae..0xa011f6ba`、`0xa005f22a..0xa005f232`|从P+0x10取R，再读R.callback/user；另从payload取S，加4才间接调用。绑定callback读view+0x1c为长度、view+0x20为消息，即S+0x20/+0x24；a1被长度覆盖|接受S视图与R分离；user无所有权转移。没有把所有外部callback都认证成不保留消息|
|归还原序：`0xa011f6bc..0xa011f6d4`、`0xa0119b7e..0xa0119bb4`、`0xa011972e..0xa0119738`|callback后先中间控制服务，再0xa0119b72(P)；正常摘链后0xa0119720(P.R)，再0xa002e14e(P)；原ctx解锁服务后0xa0119720(S)。归还服务先条件交对象+0x24，再交原对象|接受R/P/S归还调用原序，不省略中间服务或回调后重读；不把callee调用当实测物理回收|

本轮脚本开发中纠正过一处**检查地址**：I间接调用在 `0xa011f862`，`0xa011f858` 实际是空槽条件门；随后只补原题已有的2B调用窗口，最终检查通过。它不改变F11报告合同，不是ROM/模型修改，也不计语义纠正。235条普通指令均在明确窗口内完整解码，厂商字独立留存；未手工扩body、未把旧0xa0119b72的284B extent后续片段强行归为本正常路径。

局部所有权表达（非原源码，边界callee正常返回）为：

```c
Q = D + 4; clear8(Q + 0x10);
R = construct_and_copy(Q, cb, user);  // source字节复制，user仅复制word
I.payload = { ctx, R }; submit(I);    // 同步链合同继承；native queue仍opaque
P = append_session(ctx, kind0, R);    // P.request == R
if (prior_nonzero && R.word34 == 0 && R.message != NULL) {
    return_message(R.message);
    reload_payload_R()->message = NULL;
    reload_payload_R()->message = NULL;
}
// 另一正常response完成路径；不是把R消息当作S消息
P = first_matching_session(ctx, kind0, S.id);
R = P.request;
R.callback(S + 4, R.user);
existing_control_service(loop, P);
unlink_and_return_session(P);        // R.message条件归还，再R，再P
existing_unlock(ctx);
return_request_like_object(S);       // S.message条件归还，再S
```

## 真正新增

**新增业务0、库排除0、ISA规则0、ROM功能恢复0。** 本轮产生的是非作者独立证据与限定接受意见，原来F11交付的静态合同获得复核，不把同字节重读计为新功能。语义纠正0。

与当前G19/4（G23）提交环及J08/1（A56）driver选择窗口的地址、对象和问题无交集；与F11/1–2重叠是登记允许的非作者复核。J06/旧event-loop/旧pending已解释部分直接继承，没有另派或重开。

## 未闭精确边

限定接受不认证以下内容：`0xa011e33e→0xa005f464(queue,&I,-1)` 内部指针复制/持有与真实consumer执行；同ID唯一性、具体某次D与某个P/S的运行对应；完整锁/排队/并发发布；ctx/user所有权和寿命；parser/transport/云端成功；全部失败/超时/取消路径；分配器完整实现及物理free。R消息的提前归还条件仍按实际读取的R+0x34处理，跳写不补默认值。静态指令不是实机观察。

有种子的后续建议只保留一条：若需跨线程持有闭包，由管理窗口先对 **`0xa011e33e→0xa005f464`，a1=&局部I指针、a2=−1** 的正常queue复制/持有问题查重、登记后另派；本轮没有读该callee正文。除此不以新题名扩全消息库。

实际检查为独立字段/分支/JAL静态验证、JSON可解析、报告相对引用存在、`git diff --check`和独占文件检查。没有技术脚本以外的目标运行；没有运行F11三个作者检查器或旧复核脚本。交付时本分支只新增本报告、`review.py`、`evidence.json`，全部未提交，等待管理窗口整合后按流程清理。
