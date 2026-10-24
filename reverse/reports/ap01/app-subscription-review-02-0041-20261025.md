# Q23 非作者复核：subscription 身份、owned 构造与正常重用

**可独立使用阶段已闭合，但完整 manager 接口未闭。** 限定接受作者 `97b1af4824514615b01ad40a2d0cb94a03f5a25a` 的 Q23；行为纠正0，新增业务0。七个 helper 604 B 为独立原字复核，不计新增恢复。仅正常有效 descriptor、有效 reciprocal 图前提。

分支 `codex/app-subscription-review-02-20261025`；启动基线 `9100a552b6862e9a3f884182b9da4f45eeac68ee`。独占本报告及同 stem analysis，不改认领表；遵循主树 reverse-design 3.1/3.2/5.1/7、rolling 顶部和 Q23 补位行。预测3–5分钟，中置信，依据作者完整215秒/技术180秒；本轮 UTC 起点 `2026-10-24 17:50:19`，技术冻结 `2026-10-24 17:52:43`（144秒，含取证、报告和技术检查）。完整结束及技术/提交/停止分列见同 stem session.json；提前闭合即交，不故意等待。token 与独立工具等待总量不可得，不估造；未发生已知排队或中断。

## 继承结论

作者报告主树相对路径 `reverse/reports/ap01/app-subscription-research-02-0041-20261025.md`；阅读时尚未转存，实际只读 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/subscription02/` 下同相对路径及 static-windows.json。未执行作者 extract.py。整合后应以主树同路径留存为准。

继承旧 version/classifier 746 B 与九类有效输入、Q20 删除/cleanup/stale、76 B peer matcher `0xa0118b08`、`0xa018eddc` 双 wrapper allocator 接口及 `0xa01188a6` type 计数合同；不重读这些 body。旧 classifier 的5/6不复制 target，与本轮 matcher 不读其 target 一致，不为未用字段增加语义。Q20 删除调用 `8a40(incoming D,stored T+8)` 直接继承已验合同，不重做删除原字。

原件主树 `roms/0041/ap01-1.0.2_0041.bin`，长度实核6,769,704 B；SHA256沿已登记原件身份 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，没有重算全ROM；offset=VA−`0x9ffff000`。root 仅继承必要原留存 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/245`，Evidence `ev_c22e8476e961b1745b154b77d021ebafc0cedf6d943f1eb10ef9c9b712f6e21b`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。root 不计新ROM窗口。

## 本轮复核

独立 [verify.py](../../analysis/app-subscription-review-02-0041-20261025/verify.py) 直接读取原件，以现有 Capstone RV32+C 解码；七窗 `89b8/62,89f6/74,8a40/200,8b8a/76,8bd6/74,8c20/38,8c46/80`（地址均 `0xa011` 前缀）累计604 B，逐窗完整解码、原字与作者留存一致。原字/局部摘要/逐指令及有限 root 留存见 [static-review.json](../../analysis/app-subscription-review-02-0041-20261025/static-review.json)。没有新 REA Evidence ID，未启动或修改共享 REA。Capstone 分支操作数是相对位移，须加指令地址解释。

|对象/门|独立核对与判定|
|---|---|
|`0xa01189b8(A,B)`|`89b8..89cc`比较 +0/+4 两 word，第一不同返回 RV32 减法差；相同才 strcmp(A+8,B+8)，`89e4/89e8`将字符串非零规范为−1。仅使用0/非0，不能当有序比较器。|
|`0xa01189f6(A,B)`|三 word +0/+4/+8，字符串 +0xc；`8a2e/8a32`同样规范0/−1。不是16位比较。|
|覆盖 `0xa0118a40(A,B)`|首参 byte type 控制分支，`8a54`首参9、`8a8c`首参7、`8ab6`首参8，不能换位。下表字段/第二type逐门接受。|
|peer DID 查询 `0xa0118c46(key8)`|`8c56..8c68`从 `0x62fcab94` 遍历；`8c80..8c88` memcmp(P+8,key8,8)，0借用返回首P，无匹配NULL。原始8B，不是文本/sender/target。|
|边存在 `0xa0118c20(H,target)`|`8c36/8c38`仅 word(E+8)==target；有1无0，提前读取next。无 descriptor/DID 比较，无插边计数；有效链前提。|
|owned T 构造 `0xa0118b8a(D)`|申请0x6c=108 B，全零；copy0x58=88 B至T+8；`8bc0..8bc6` T+0x64/+0x68均指T+0x64。T+0x60计数0由全零获得；输入D不持留。|
|owned P 构造 `0xa0118bd6(key8)`|申请0x30=48 B，全零；copy8 B至P+8；`8c0a..8c10` P+0x24/+0x28均指P+0x24。P+0x20计数0；不保存输入指针。|

两构造成功返回 owned 对象，分配NULL直接返回NULL；+0/+4全局链字段仍零，构造不插global链。malloc/zero/copy/memcmp/strcmp止API，不展开库；这只确认输入在copy期间借用及节点owned副本，不证明最终释放时刻。

|首参type|覆盖接受条件（返回0）|
|---|---|
|9|第二5/6直接0，不读target；第二3/4比较A+0xc与B+0x10；其它有效type比较A+0xc与B+0xc。|
|7|第二5直接0；第二1/7比较双方+0xc；第二3比较A+0xc与B+0x10；其余有效type非零。|
|8|第二6直接0；第二2/8比较双方+0xc；第二4比较A+0xc与B+0x10；其余有效type非零。|
|1/2|先同type，再 `89b8(A+4,B+4)`，即D+4/+8两word及D+0xc字符串。|
|3/4|先同type，再 `89f6(A+4,B+4)`，即D+4/+8/+0xc三word及D+0x10字符串。|
|5/6|先同type，再strcmp(A+4,B+4)，无target比较。|

`8ad0/8ad4`的type差作为非0；字符串经 `8a7c/8a80`成0/−1。type9入口本身不是输入验证器；这里只接受已有classifier的1..9前提。

root `0xa0115f7e` 的必要成功接合：`6312..6318`外mutex；`6320`按DID8查P；`644a..6456`明确 a0=T+8、a1=栈输入D 调覆盖谓词，与继承删除方向相反。命中经 `6468..6488`刷新sender8/update_ts/lastseen，status0，无新边；common cleanup仍继承，故不宣称整个root无变更。

全局topic搜索 `64e2/64e6`先要求同type，a0=T+0xc、a1=D+4；`64fc`对1/2/7/8/9调用89b8，`6510`对3/4调用89f6，`6516`对5/6调用strcmp。这是同型identity，不能用宽覆盖取代。7/8/9读取的数字word来自root零初始化，不给它们新增数字组件。

|P/T正常存在组合|确认的成功接口|
|---|---|
|无/无|`6418..6436` unsigned peer_count<=3才构造T、P；`65b8`已验pair接口成功后双链挂边、两对象计数各+1、插各global链及全局计数；`6652`仅type计数+1。|
|有/无|`66c0..66d0` signed P.edge_count<=9才构造T；pair成功双边各+1，仅T插global并增加topic/type计数。|
|无/有|`68c2..68d6` unsigned peer_count<=3才构造P；pair成功经`6658..66be`双边各+1，仅P插global及peer计数。|
|有/有|`6756`查询T哨兵是否含P，`6764/677c`查询P哨兵是否含T；双方存在刷新成功不重复插边；双方均无且`678e` signed count<=9，pair成功双边各+1，对象不重造。|

不混同 unsigned peer<4 与 signed edge<=9。单侧存在的−1接口只继承正常控制流边界，不制造异常图实验。成功的type变化沿Q20已验接口只加计数，不称外部callback注册。

## 真正新增

新增业务恢复0；本轮贡献是独立确认上述边界和原字一致性，接受Q23有效输入的身份/覆盖、借用查询、双owned构造与正常重用阶段。没有用仅交换callback变量名代替七helper核对。

## 未闭精确边及停止

manager最终销毁/root外同步、正式版本权限、投递/fanout、取消、损坏图及旧allocation失败缺陷均未验证，不能标完整manager闭合。后续种子仅保留已登记publication `0xa011c0da(C,D,K)` 对覆盖API的消费，属Q24，不在本题继续。未执行目标、模型、SIM、QEMU、回放、构建、设备、外网；不改ROM/生产配置/分析器，不派下级，不推送。

实际检查：独立七窗完整解码604 B、与作者raw_hex逐窗相等、必要root实参与四组合接合、报告路径/JSON结构、精确提交范围及git diff --check。技术结论无阻塞。ignored中间产物static-review.json/session.json由父窗口原路径转存，复核者交付后停止，不自行清理父树。
