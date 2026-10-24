# F11：MiIO 普通请求复制、队列持有与回调消息寿命

**正常非空载荷路径会在提交返回前复制栈 descriptor 的必要字段，并把载荷复制到独立 `len+1` 缓冲区；队列持有的是独立 invocation `I` 和请求 `R`，不是 caller 的栈 descriptor。正常回执匹配后，已保存的 callback 接收的是另一个 response 对象 `S` 的 `S+4` 视图，而非原 `R`。消息仅在同步 callback 期间借用；callback 返回后才依次归还所匹配 session 的 `R` 和本次 `S`。** 同 ID 唯一性、实际执行/交付、下层队列和所有正常之外路径不因此获得认证。

2026-10-24；研究基线 `ee220d8`，独占树/分支 `re0041-f11` / `codex/re-0041-f11`。认领 **F11/1** 由管理基线 `02afb05` 确认，`2e203cc` 再准worker中R消息提前归还的28B寿命差集；**F11/2** 先待消歧，`cb4abfd` 仅准身份/寿命三桥，`608da2b` 再准 `0xa0116cea/0xa01ab82c` 的匹配依赖。均见主仓唯一[认领表](rolling-management-0041-20261023.md#链条认领表)。规则切换时立即停止新增取证，全文读取主仓 [reverse-design](reverse-design.md) 及管理顶部规则后才按逐次批准范围恢复；研究基线没有移动，不修改共享表。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。原件沿 CATALOG 既有0041身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射 `VA−0x9ffff000`。仅读本地旧证据与必要原字，未打开/切换共享REA，未执行固件、模型、模拟指令、输入实验、SIM、构建、历史回放、设备或外部服务；未做漏洞/异常输入/缺陷验证，未改生产代码、ROM、配置或分析器模型，无下级agent。本题不展开 parser、封装选择、加密、安全、凭据、网络、OTA、超时、取消或 native queue。伪代码不是原源码，作者自检待非作者独立复核。

## 继承结论

|旧出处|继承行为|与两认领的真正差集|
|---|---|---|
|[J06](miio-reuse-gap-j06-0041-20261024.md)及其 selector JSON|实际 caller、send/constructor完整旧body、callback `0xa005f222` 与普通回执入口已留存；旧父级明确 copy-versus-retain 未闭|F11/1只补字段位移/复制和 `R/I` 持有；F11/2只补 `session→R`、匹配与 `S+4` 实参/归还，不把旧body或新报告标题计首次发现|
|[upper-layer](upper-layer-0041-20261017.md)、旧 `upper-miio-b.md` 的 `0xa011e3d6` 卡片|type1消息 target==loop 时 `callback(loop,message)`；返回1转移持有，其余返回本地归还；同步列表与队列接收已有局部合同|直接引用 generic event-loop，不重做 type0 watcher/通用timer或全消息库。`0xa011f610` 本次装的是 type1 executor|
|旧 `miio-rpc-rea-0041.json#/native_rpc/reply_matching`、[协议报告](miio-mible-protocol-rea-0041-20261017.md)|32B pending-ID记录、`0xa01977cc` 的 `callback(fd,message,length)`、摘链后call/free；`0xa00626ea` 普通回执转发已有|不同于本题 `0x3c` 请求/response及 `0x14` session；这些既有匹配/三参/明文回执不重验、不新计、不叫timeout|
|旧 `upper-complete.evidence.json#/records/204`，`ev_a02f78caa6ed020d619136ab3859dd193c2c2b10b8f6bb77630675f643c18b7f`|`0xa0119720` 既有归还服务：对象非空时，条件归还其 `+0x24` 指针，再归还对象|先复用旧body，本轮仅补正常 `P.R/S` 的实参和原归还顺序；不凭函数名或伪码省参认证完整heap/实际归还成功|
|[F01/F02](miio-deferred-review-f02-0041-20261023.md)、[F03/F04](miio-loop-close-review-f04-0041-20261023.md)、[F05/F06](display-exit-review-f06-0041-20261023.md)|共享9428业务timer和显示退出是其他对象；F06的mask正式纠正为 `0xffff7fff`，候选来源/版本继续限定|不重开kind0..6、display+0x2b8、loop最终关闭、旧负搜索；不把本题 MiIO event-loop 当F01 caller栈loop|
|[最终应用验收](application-rehost-complete-0041-20261017.md)及J06的父级complete去重|绑定/设置等SIM业务已完成相应验收，物理无线/云端由服务替代|直接继承，passed-in-sim不证明本ROM持有/回执或完整恢复；不重新盘点页面、设置/CRC、地点或已验业务|

旧完整body统一只读主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。J06已经给出 `records[282]` caller、`[197]` send、`[91]` 适配、`[13]` 构造、`[163]` callback、`[278]` 既有回执的 Evidence ID；本题另复用 `[142]` 的 `0xa011f718`（`ev_6bef28a545502b1d067d8b5af289b13fa2bd4eb86a9cefd29cfb318ee59edb2a`）与 `[195]` event-loop。未重导这些完整函数。

F11/2 新三桥及匹配依赖的旧 whole-ROM 索引只有 extent、没有dossier：`0xa0119c8e` 176B / `ev_31927c0376e47cdb964d3e1058be2a8e8072d0286c398938e0fa0ef50e055ac7`；`0xa0119748` 80B / `ev_239bedbb83b4ba7e7b3f2721ab6d2fd649d904521daebe697a18ea0631267ec4`；`0xa0119b72` 284B / `ev_31cdb63e796e37a8ac41ad4344c48c9e5d48ddd0a5e4c496d71ec72c60b44dfb`；`0xa0116cea` 46B / `ev_f1cf5a3be74739419c2c0948a1e581315ee1505a8dc21d81c3c795016627979e`；`0xa01ab82c` 54B / `ev_2e5947e92b0f52d2cced3d81846e70f48b828fb35f9f10dbad5f9d8d4e9c7fe5`。元数据不当语义证据；新增必要原字在本题两份 evidence JSON，不伪造新REA ID。

## 本轮复核或纠正

语义纠正0；真正新证据是两认领必要字段/控制/所有权接线。旧 down 请求 `0xa0191872` 的 `0x3c` 形状不能套在 up 请求上；本题从 `D→Q→R` 实参和写入重建。F11/2在得到保存槽、predicate及遍历ABI之前没有先假定同R/S。

脚本开发修正过 `th.srb` 的手写预期f3/高字段、若干压缩寄存器编码和predicate地址计算笔误；最终原字/字段断言通过。实际predicate为 `0xa0117000−0x316=0xa0116cea`，不是 `0xa0117cea`；认领与最终脚本使用正确地址。没有修改原件或模型。

旧 `0xa0119b72` 的284B extent延伸到正常返回/分支之外的其他片段。本题仅采用 `0xa0119b7e..0xa0119bb4` 的正常链表摘除与归还路径；后续trap/非本问题片段不作单函数合同、缺陷结论或模型修复。关键普通指令独立取字段/JAL；唯一必要厂商字 `0xa011f93a=0b50f700` 拆得 op0b/f3=5/rd0/rs1=14/rs2=15/shift0，和既有 `th.srb` 的 byte store规则相符。该私有规则不是独立厂商ISA规范。

## 真正新增

### F11/1：栈descriptor复制、请求和invocation持有

正常caller在 `0xa01b62fc..0xa01b632a` 初始化栈 `D=s0−0x54`，写 `D+4=id`、`D+0x10=0` byte、`D+0x20=len`、`D+0x24=source`、`D+0x2c=0xa005f222`、`D+0x30=user`，以 `(manager,D)` 调 send。caller只在send返回非零时走既有失败接口；返回0不表示传输、云端或业务成功。

`0xa0111ff6` 先选已启用的context，再以 `Q=D+4`、cb=`D+0x2c`、user=`D+0x30` 交 `0xa011f9da`。first正常分支是 manager+0x968，另一正常分支是 manager+0x174；其余状态门仍按原字，不给通道取安全/协议成功名称。`0xa011f9da` **先清 `Q+0x10` 的8B**（即 `D+0x14..+0x1b`），恢复保存实参后才调用构造。不能把这8B描述为原caller未知内容原样保留。

|对象|本题已核的最小字段（hex偏移）|责任|
|---|---|---|
|`D` / `Q=D+4`|`Q+0=id`，`+0xc`来源byte，`+0x10`处8B适配清零，`+0x1c=len`，`+0x20=source`|caller栈；仅同步构造时借用，不存入最终请求 |
|`R`，申请0x3cB|`+4=id`，`+0x10` byte，`+0x14`处8B复制，`+0x20=len`，`+0x24=owned message`，`+0x2c=cb`，`+0x30=user`；另有条件word赋值 `+0/+0x34`|独立heap请求；user只复制指针/word，不深拷贝其目标|
|`I`，独立申请|`+0=next`，`+4=0xa011e2f0` dispatcher，`+8=1` byte，`+0xc=loop`，`+0x10=0xa011f718` executor，`+0x14=0`；payload地址=`(I+0x1b)&~3`|invocation及payload同次分配；payload两word为 `{ctx,R}`，不存D/Q |

`0xa011f86c` 的 `0xa011f8f6..0xa011f942` 给出：R的字段按指定宽度复制；正长度时申请 `len+1`，保存到 `R+0x24`，以 source/len 调既有复制服务，再按 byte 写 `message[len]=0`。因此source的字节在提交返回之前已经复制；不是延后保留原source或caller栈指针。本题不把正长度合同外推为所有输入域/长度审计；未赋字段和初始化默认值不补猜。

随后 `0xa011f964` 申请I，`0xa011f992` 取得对齐payload，写 `{ctx,R}`，`0xa011f9a0` 调提交。`0xa011f610` 对请求的payload8B计算总申请0x20B、清零该分配，再安装上述dispatcher/type/target/executor。`0xa011f84a` 写I+0x14参数，读I+4，以 **a0=I+4** 间接调用；dispatcher再减4取得I，所以这层参数不能误写为直接 `(I)`。

`0xa011e2f0` 的type1路径取I+0xc为loop。同线程分支把I挂到loop+0x2c的同步链：空链写head，非空沿next到尾、清I.next后挂尾，返回0。异线程分支把局部保存的I指针地址交 `0xa005f464(queue,&I,-1)`；**该native queue内部同步复制/保留合同仍为明确边界，本题未展开。** 不能把这一服务调用或返回0当实际consumer已经执行。

提交返回0时构造器不归还R/I；非零时先把保存I交既有归还接口，再把R交 `0xa0119720`；I申请未得对象则只交R归还服务。构造器保留非零提交返回，而非统一成功；这些是原正常服务失败臂的静态顺序，没有运行失败输入或作缺陷验证。既有event-loop按type1调用 `(loop,I)`；`0xa011f718`通过同payload取得ctx/R，后续session持有另见F11/2。旧完整worker尾声返回0，因此在其正常返回前提下，I走既有event-loop的本地归还，R的寿命不等同于I。

**R对象和R消息也不能视作同寿命。** 旧 `records[142]` 已有提前归还分支，但所查manual/近期合同未解释条件，因此先停该窗口并登记差集，再只核 `0xa011f79a` 与 `0xa011f818..0xa011f832`。前一服务返回非零才进该分支；实际读得 `R+0x34==0` 且 `R+0x24!=0` 时，以该消息指针作a0交既有归还接口，随后**重读payload的R并清R+0x24，再次重读R再清同R+0x24**。第二次不是清长度+0x20，不能为合理化而改写。这个分支不归还R对象；P仍保存R。`R+0x34!=0` 或消息槽为零则跳过这次消息归还。构造仅在传入word非零时写R+0x34；send的一条正常路线传0而跳写、另一条传2而明确写2，**跳写时不补猜初始化默认零**。不解释前一服务内部，也不将R消息一概延长到回执时刻。

### F11/2：session身份桥、首个匹配与临时reply视图

`0xa011f718@0xa011f73a..0xa011f740` 实际传 `(ctx,0,R)` 进入 `0xa0119c8e`。新session `P` 申请0x14B、清零；正常保存 `P+4=ctx`、byte `P+8=0`、`P+0x10=R`，接入 **ctx+0x20** 单链。空链置head，非空接尾；请求指针不是深拷贝的新R。此处明确是R进入session持有，而非I payload自身成为session。

response服务 `0xa01ac226` 另外构造 `S`（申请0x3cB）：从输入视图取id/来源byte/len；正长度时另外分配消息区并复制len字节，存 `S+0x24`，len存 `S+0x20`。本题只核这段已有观察的对象/复制字段，不向response parser、上层transport来源或消息编码扩展，也不为该缓冲增加原程序未有的终止/检查步骤。另一个I的payload为 `{ctx,S}`，executor在 `0xa01ac2cc` 安装为 `0xa011f67e`。

该executor的正常分支用 `(ctx,0,S.id)` 调 `0xa0119748`。lookup把 kind byte/id/out 指针域放在本地criterion，以ctx+0x20链和predicate `0xa0116cea` 交 `0xa01ab82c`。predicate先比 `P.kind`，再取 `P+0x10→R`，比较 `R+4` 与criterion.id；相等写criterion.out=P并返回 **-1**，不等返回0。遍历以 `(P,criterion)` 调predicate，返回0才继续，非零即停止；callback后先取当前P.next再按该返回结束。因此lookup所得是该ctx链中**首个 kind0 且 R.id==S.id 的P**，不是同ID唯一性或某次特定D的实际对应证明。

正常matched分支的原序：

```c
// 分析表达，非原源码；边界callee正常返回。
P = find_first(ctx->sessions, kind=0, id=S->id);
R = P->request;                      // P+0x10；由上述构造保存
cb   = load32(R+0x2c);
user = load32(R+0x30);
cb(S+4, user);                       // f6b8/f6ba；不是 cb(R,user)
existing_control_service(loop, P);   // 保留原中间调用，语义边界不展开
unlink_and_release_session(P);      // 先将P.R交归还服务，再P
existing_unlock(ctx+0x24);           // 边界
release_request_like_object(S);     // 条件归还S+0x24，再S
```

保存的cb确为caller写入的 `0xa005f222`。它从入参 `view+0x1c` 读入a1、从 `view+0x20` 读入a0，再同步调用既有 `0xa01b38dc`；因为view=`S+4`，这两地址分别是 **S+0x20长度、S+0x24消息**。a1=user在该适配中被长度覆盖，不因此转移user对象所有权。既有下层怎样解析/相关回执以及使用传入长度沿旧合同，不重复恢复。

callback返回之后，`0xa0119b72`从P+4取得原ctx并正常摘除P；从P+0x10取得保存R，交 `0xa0119720(R)`，随后把P交既有 `0xa002e14e`。原归还服务的必要原字 `0xa011972e..0xa0119738` 证实a0先取对象+0x24，非零时交归还接口，再以原对象作第二次归还实参；不是伪码省参的“无参free”。因此上述worker已清R消息槽时，本处不再交出该旧消息指针，而仍归还R对象。随后 `0xa011f6d4` 以S交同服务。这里的“归还”是原服务调用合同，未认证底层heap全部算法或实际物理回收观察。

所以同步回调期间，S和S消息尚未被本完成路径归还，P.R对象也尚在；R的原消息则可能早已按前述分支归还。回调返回后才发生R对象/P/S的上述归还。`0xa005f222`没有将该view或消息指针长存的本地动作；既有普通回执消费为同步边界。它不是原source、R消息或32B pending-ID节点的所有权转移。未证明所有外部callback都同步、不保留或不会改变对象；本题只认证这一已绑定callback正常调用。

## 未闭精确边与实际验证

F11/1的字段/载荷复制、I payload及同步链持有，F11/2的session保存R、正常首个匹配、临时S视图及归还原序已获得局部静态答案。仍未知：native `0xa005f464` 下层的指针复制/保留；实际consumer执行机会、完整锁/排队/并发保证；同ID唯一性与具体调用实例对应；输入context/user生命周期；response的上层来源、实际云端交付/业务成功；各分配器完整实现与精确来源版本。超时/取消、所有错误路径、完整session/网络协议不搭便车。无新增标准库排除或完整ROM宣称。

独占 [F11/1检查器](../../analysis/miio-request-ownership-f11-0041-20261024/verify_f11_1.py) PASS：**93项、188条必要稀疏指令、562B**，含1处厂商word与既有局部规则；[F11/1原字结果](../../analysis/miio-request-ownership-f11-0041-20261024/evidence-f11-1.json)。另按 `2e203cc` 登记运行 [消息寿命差集检查器](../../analysis/miio-request-ownership-f11-0041-20261024/verify_f11_1_lifetime.py)：**11项/28B**，只读新准的门/归还/两次清槽，不重跑前一组；[寿命原字结果](../../analysis/miio-request-ownership-f11-0041-20261024/evidence-f11-1-lifetime.json)。[F11/2检查器](../../analysis/miio-request-ownership-f11-0041-20261024/verify_f11_2.py) PASS：**102项、178条、486B**，均普通RV32/RVC；[F11/2原字结果](../../analysis/miio-request-ownership-f11-0041-20261024/evidence-f11-2.json)。脚本按已登记的地址窗口fence仅读必要原字，不执行目标、指令、输入或旧作者检查器；没有整函数/资源/源码/全表导出或机械哈希账。JSON、相对链接、差异和独占文件检查通过。

后继仅为同 **F11/1、F11/2** 认领下的非作者技术复核：核本轮D/Q/R与I持有差集、session-R身份及S视图/归还顺序，旧event-loop与pending回执合同直接继承。native queue若另追须先在唯一表按 `0xa011e33e→0xa005f464` 的具体指针复制问题登记，不自行扩展。本报告不是独立验收，作者交付后停止。
