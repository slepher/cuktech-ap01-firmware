# Q-20 正常 miIO.unsub 删边与归还：非作者独立复核

结论：限定接受作者 `64326568681c7d1970e911e92a4e49de31cca825`，行为纠正0，复核新增私有函数本体0。有效 descriptor、有限 type、有效 reciprocal 图前提下，本阶段可作为重建合同；厂商未知指令仍为限定推断，完整接口未闭合。静态推断不是执行观察，伪代码不是原源码。

## 继承结论

本次为 Q-20 原认领下非作者复核，独占本报告及同 stem analysis。分支 `codex/app-subscription-review-01-20261025`，启动基线 `a4979f031d0799f97913c9496213394ab02abb58`。主树 reverse-design 3.1/3.2/5.1/7 及 rolling-management 顶部、Q-20 补位行只读继承。未改管理表或其他协作者文件。

原件主树 `roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，CATALOG SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−`0x9ffff000`。本轮核长度及7个精确窗口，未重算全ROM摘要。作者报告见 [研究报告](app-subscription-research-01-0041-20261025.md)。没有重做 sub 创建、旧 allocation-failure 缺陷或 N03 UiIFace。

根证据分账：

|来源|EID / profile|
|---|---|
|upper-miio-b，sub 根|`ev_c9c083522ddaa5a7c350aad4fd271a4e9fd7998e751e2f4db869cbe71d44272a`|
|upper-miio-b，unsub 根|`ev_d4942aedf1d2ed7b7ee29db9fb686a68f9f7155c6d5706b91f8c5b96da16a7c8`；两根 profile `04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`|
|upper-complete /records/245|`ev_c22e8476e961b1745b154b77d021ebafc0cedf6d943f1eb10ef9c9b712f6e21b`，仅必要 G/topic 哨兵身份片段|
|upper-complete /records/48|`ev_221426fb577a1866be99a4825a47510530b45aec1e8d468aed90c0e391e9f036`，根 flag、锁及响应片段；两项 profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，Ghidra12.1.4 / RISCV:LE:32:ap01thead2|

来源均为主树 `evidence/rea-0041-20261017/evidence/` 下同名文件。没有产生新 REA EID、运行共享 REA 或改变其 profile。

## 本轮复核或纠正

|核对连接|独立接受的事实与限制|
|---|---|
|G=`0x62fcab6c`|九个 word 为 type1..9；+0x24 peer count、+0x28 peer 哨兵 `0x62fcab94`、+0x30 topic count、+0x34 topic 哨兵 `0x62fcaba0`。`a0113cd4..3db4` 九次 word load、`a01188a6` 九终端路径及根245 `a01163cc..3e4/6410` 身份交叉支持。P+0x20、T+0x60 是 edge 数，不能混成 G 对象数。|
|`a011bfc4`|按 E+8 对侧指针删首匹配；`a011bfe2` unlink 先于 `a011bfe8` free；匹配1、未匹配0，不改外层 count。|
|`a011d10e`|P空或未找到 T 返回−9。两次 erase 分别经 `d192/d1a8` 非零门才各减一；P精确==0先 unlink/free，再检查T精确==0，type−1在T unlink/free之前。找到T后最终0，**不要求至少删边一条**；返回0不是图一致性或投递保证。|
|`a01abe54`|缓存当前 edge next，E+8取T并核type。`(type−5)&255 <=1` 进入 flag 门；flag0跳过5/6。type3/4目标T+0x18，其余非5/6为T+0x14，比最多0x47 B，比较0才精确删除。`abed4` 调用返回不检查，按缓存next推进；不据此保证任意生命周期安全。|
|`a0113c8a`|`a0113ca8` **先调 `a011bffe`**。后半是统计/peer/topic dump；不能把整调用称只读。根48的已持锁失败分支也到 `d66e`，故语义失败仍可能清理其他过期peer。|
|`a011bffe`|每peer重新调用 `a005fa1a`，RV32 unsigned差值>0x78才清理，等于保留；不猜单位。T侧erase后不查返回直接减，signed新Tcount<=0释放T/type−1；P侧erase同样不查返回直接减。不同于精确函数的结果门和精确==0，不能合并成同语义helper。|
|`a01188a6`|九类 word 读、加delta、写回。有效type路径无外部callback注销；type−1仅本层topic计数更新，外部注册生命周期未知。|
|根锁/响应|mutex `0x62fcaba8`，根48 `d450` 置s1=0，aggregate以s1作a2。进入锁域的出口先cleanup/dump、再unlock、dispose parser，随后100 B响应分配。result.code承载status；finalizer=0才调reply，响应free后outer0。删边先于响应分配，outer0不证明删边实际发生或reply送达。|

七窗为 `a011d10e`244、`a01abe54`170、`a0113c8a`738、`a0118b08`76、`a011bffe`220、`a011bfc4`58、`a01188a6`274 B，共1,780 B。独立逐窗读取原件，与作者留存的hex及局部SHA256一致；使用独立脚本重新作Capstone5.0.7静态解码，未运行作者脚本。

6个 UNKNOWN 原字原样保留：`a01abe7e:8bc7994c`、`a0118b1a:8bc7944c`、`a011c05e:8b479a4c`、`a0113e8c:8b47994c`、`a0113e54:8b48d380`、`a0113e58:770587df`。前四处仅按旧模型编码族/既存字段规则与普通callsite参数作“预增base再取首edge”的有限解释；未执行模型、未改模型，**没有独立认证厂商ISA**。后两处仅诊断DID拼接未知，不能充作图语义证据。P+0x24/T+0x64另有普通addi参数支持。

## 真正新增

新增业务0、行为纠正0、私有本体0。本轮增加独立字节比对、26个分支锚点、九类计数终端路径、11个直接JAL目标检查，以及根profile分账及上下游人工控制流核对。检查数量描述静态锚点，不表示执行路径覆盖。

[review.py](../../analysis/app-subscription-review-01-0041-20261025/review.py) 是本轮独立复核源码；[checks.json](../../analysis/app-subscription-review-01-0041-20261025/checks.json) 是必要简短清单；[本地忽略证据](../../analysis/app-subscription-review-01-0041-20261025/independent-evidence.json.tmp) 保存7窗重新解码与必要根摘录，交父窗按同相对路径转存。JSON解析、精确输出范围及diff检查通过。没有执行固件、作者脚本、指令模型、SIM/QEMU、回放、构建、设备或外网。

## 未闭精确边

完整 `a0118a40` matcher语法止API；公共 unlink/free 止API；fanout、其他writer、其他caller锁域/并发、外部type注册生命周期及manager总销毁未闭。四条厂商预增指令只有静态一致性推断；本轮没有相应独立ISA认证。诊断未知字不构成必追业务断边。下一步如有另行登记，针对四条原字寻独立ISA定义即可，不能把本次接受升级为全接口或全ROM完成。

时间口径：第一工具UTC起点 `2026-10-24 17:33:43 UTC`；技术完成UTC见下方追加记录，提交和停止UTC由交付分别报告。作者没有可靠起点，不能报作者全时。排队等待未观测；本任务无审批等待、无外部等待；token不可得，不估造。派发预测4–6分是预测，不冒充实测。
技术完成：2026-10-24 17:36:40 UTC；自第一工具起2分57秒。随后仅整理最小根摘录、Git提交与交付，不增加技术取证。
