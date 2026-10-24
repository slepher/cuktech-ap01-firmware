# Q-24：publication recipient 路由、同步复制与事件完成归还

状态：**可独立使用阶段已闭合但接口未闭**；作者静态研究，待非作者复核。本阶段连接 Q19/Q21 的临时 D/P 到 SDK owned request，并恢复事件按 id 的正常完成/失败回收。完整 C 生命周期、并发、recipient 实际递送及云端应用仍未知。伪代码是业务合同表达，不是原源码或执行观察。

分支 `codex/app-publication-research-01-20261025`；基线 `a4979f031d0799f97913c9496213394ab02abb58`。主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`；独占本报告和同 stem analysis。预测5–8分钟中低置信；完整首工具 UTC `2026-10-24 17:42:30 UTC`，冻结/提交结束另列；token数据不可得。

## 继承结论

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，沿 CATALOG SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，`offset=VA-0x9ffff000`。本轮仅核长度，未重算整件摘要。遵循主仓 reverse-design 3.1/3.2/5.1/7、rolling-management 顶部和 Q24；未修改共享记录、生产代码、ROM、模型或配置。

- [Q19](app-event-research-01-0041-20261025.md)：即时 event 先 `a011c0da(C,D,K)` 后 free P；flush `a0113340(C,D)` 后 free P，非0时锁内 `a0116ad0(C+0xdc,id,0)`。D+4=id、+0x20=length、+0x24=P、+0x2c=callback、+0x30=context；即时 cb=`a0116db0`/ctx0，flush cb=`a0116b5a`/ctxC。K.tag6；本轮不重读 producer body。
- Q21 作者报告 `app-named-property-research-01-0041-20261025.md`（读取作者 named-property01 只读副本）：同 D 布局、即时 cb/ctx，K.tag5；本地 entry 与 event record 不混同。本轮不重做 name/value 持有或 report 构造。
- 主仓 `evidence/rea-0041-20261017/evidence/miio-recovered.md` 的 session 合同：`a011f9da(session,message,cb,ctx,time,mode)` 清 message+0x10 起8 B后委托 `a011f86c`。后者 malloc60 B请求 Q，复制 message id/type/metadata/len，malloc(len+1)复制消息并补 NUL，保存 cb/ctx；工作项持 `(session,Q)`，失败销毁 Q。Evidence 分别 `ev_3c1987c9d0b0223c28b66671236fb3303aea3c0ccb028253ec8660393dd03e02`、`ev_e7a80442abbf3a1af9636c77de5a9a5b9993e5b10a7b0758e6ffcff375d61317`；直接继承，不重验 allocator/queue/JSON 内部。
- [Q20](app-subscription-research-01-0041-20261025.md)：topic T+8 descriptor，T+0x64 peer-edge head；E+8=P；P+0x18 sender8。`a011bffe` stale 清理和 matcher `a0118a40(descriptor,descriptor)` 的返回0匹配合同继承；本题未读这两个 body。Q23 matcher live 差集不抢占。
- JSON公开API合同继承 `upper-miio-a.md`：`a0060cac(JsonDoc*)` 返回0解析成功；d+0 input/+4 length/+20 owned tokens；`a0061d20(doc,start,path,count)` 返回非空 token 表示路径存在，expected type0为 wildcard；`a01b38b6` 释放解析文档。该卡对应 Evidence `ev_ef671cfe67f99dd21ef27cd00e2cdc899ef9290bb26bcf3eda835733efdad3e6`、`ev_e2fddcc18b0cb267920386c48c0532eb64af7a17b28b70619d951fba00af4a2d`，其 final profile `04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`；与本轮无 REA profile 的离线解码分账。

## 本轮复核或纠正

旧 upper-miio-a/b、upper-routing 卡按本五地址有限搜索未见本体业务合同；这不是全历史负证明。本轮新取五个已登记窗口，298+92+202+54+138=784 B，覆盖279条指令，Capstone5.0.7/RV32/RVC，无 UNKNOWN 或厂商指令争议，无新 REA Evidence ID。未借旧 profile 给新解码背书。

Q19/Q21 caller 的临时资源断边在本阶段接上：不是由“异步”名称推 copy，而是新实参等式加旧 f86c 真 body 合同证明。`a011c0da` **直接**调用 f86c，保留每 peer sender metadata；`a0113340` 通过 f9da，先清该 metadata。两者不能合成完全相同的包装器。

## 真正新增：匹配、每 peer 输出及同步持有

`a011c0da(C,D,K)`：可选锁句柄 `word(0x62fcaba8)`，非空则 lock(-1)，先调用继承 stale API `a011bffe()`；随后从 topic sentinel `0x62fcaba0` 遍历，预读 next。调用 `a0118a40(T+8,K)`，非0跳过，0才从 T+0x64 遍历 peer-edge；匹配语法不在本题展开。tag5/6 的选择来自实际 K 入参，不能凭标签推额外权限或 recipient 保证。

每 edge 读取 E+8 的 peer P，以 copy API复制 **0x30 B** 到当前栈快照 B（`c188..196`）；先保存当前 edge 的 next。随后解全局锁，检查 `word(B+0x18)` 非0；只检查sender8的首word，不能改成整个8 B非零检测。该门为0直接跳到重新加锁；非0则复制 `B+0x18` 起8 B到 `D+0x14`，调用：

```c
rc = a011f86c(C+0x174, D+4, word(D+0x2c), word(D+0x30), 2000, 0);
if (rc == 0) any_success = 1;
// 重新读可选全局锁句柄并加锁，再按已缓存 next 继续。
```

`c1cc:ef30006a` 为原字 JAL 到 f86c；`c1c2:8147` mode0、`c1c4:1307007d` time2000。一次调用尝试所有匹配 topic 的所有 edge；不在本层按 peer 去重。同一 peer 若在多个匹配 topic 中出现可产生多次独立提交；这是循环结构推断，不声称已观察这种图。

函数初始 flag0，任一次 rc0就设1，后续失败不清零，结束返回0/1。0包含无匹配、全部 sender 门失败、全部 submit失败；不是逐 peer错误码。调用端 Q19/Q21 忽略该返回。锁在 snapshot 完成后释放、copy D metadata和submit期间不持全局锁，完成后重新读取句柄加锁；不把 cached-next 与解锁间隙解释成并发安全保证。

SDK copy 的实参等式：`message=D+4`，所以 `message+0x1c=D+0x20=length`、`message+0x20=D+0x24=P`、metadata=`message+0x10=D+0x14=sender8`。旧 f86c 在返回前把这些内容写入独立 Q及 len+1副本。于是正常成功交接不保留 borrowed D/P/B/K 的栈地址；SDK持 cb/ctx标量，ctx指向 C 时仍是借用 C。每 peer submit 独立拥有消息副本，后续 D metadata改写不改先前 Q。

`a0113340(C,D)`：byte(C+0x1134)&0x20 优先选 `session=C+0x968,time=word(C+0x1a6c),mode=0`；否则 byte(C+0x1c8)&0x20 选 `session=C+0x174,time=word(C+0x8e0),mode=2`；都无则返回−12。两条到同一 `a011f9da(session,D+4,D.cb,D.ctx,time,mode)`，返回值原样返回。这个函数没有 topic matcher，也不是 c0da 的逐 peer fallback。f9da 对 message+0x10 的清8 B就是 D+0x14 metadata；随后仍由 f86c同步复制 payload。时间数值不赋单位。

## 真正新增：callback ABI、成功门与事件恢复

`a0116db0(reply,ctx)` 即时回调仅读取 word(reply+0)作为日志 id，调用日志能力，返回0；不读 ctx、不解析reply result、不访问 event H、不释放事件。不能把日志回调当成事件记录完成。

`a0116b5a(reply,C)` 以 reply+0x20消息指针及 +0x1c长度构造栈 JsonDoc，并调用 parse。parse失败时保留 local_status=−1，直接去事件恢复；成功时先置 local_status=0，查单路径 `result`，expected type byte=0。ROM `0xa06124b8` 精确 NUL字串为 `result`。lookup非空保留0；lookup空改−1（日志级别只控制日志）。成功 parse 后在恢复前调用文档 cleanup；未把 reply buffer释放或保存到 R。

随后 lock(word(C+0xe4),−1)，读取 **word(reply+0)** 作为 id，调用 `a0116ad0(C+0xdc,id,local_status==0 ? 2 : 0)`，重读锁句柄并unlock，最后始终返回0。因此有效JSON仅要求存在 result键，wildcard不检查值类型或其内容；不能升级成“result.ok”或“云端设备物理应用成功”。正常 error-only reply 因缺 result走恢复0；两个键同时存在时本层只以 result存在判定，未实验异常输入。

`a0116ad0(H,id,state)` 从 word(H)沿 +0遍历至H，每节点先缓存 next，对 **所有** word(R+0x74)==id 的节点执行，不限定 R.pending 原值、不在第一匹配后停止：

|state|原序和结果|
|---|---|
|0|先 byte(R+0x70)=0，再 word(R+0x84)读加1写回；保留 R、id、时间戳及 payload argv；继续遍历|
|非0（本callback传2）|先 byte(R+0x70)=state，再 unlink API `a006929a(R)`、日志、free(R)；按缓存next继续|
|无同id|只遍历，无记录修改|

关键原字 `6b14:fc58`读id、`6b1a:23884407`写pending byte、`6b22:83a74408`/`6b28:23a2f408`读写retry，`6b36` unlink先于`6b54` free。retry是RV32 word加1，无饱和门。这里不改 id；继承 Q19下次flush在retry>0且旧id非零时沿用。unlink内部止公共API；本报告不声称已展开四链写。

于是 Q19 submit非0的立即恢复与正常reply失败回调共用 state0，均允许记录以后重新 flush；成功回调state2删除全部同id记录。R没有跨回调借用reply payload。C仍需活到回调，实际callback调度/重入及关闭竞态不由本局部锁证明。

## 未闭精确边、验证和停止

已闭独立阶段：临时 D/P→每 peer/优先session提交→SDK自有副本→borrowed callback reply→按id成功归还或失败恢复。Q19/Q21生产和旧session合同为继承前提，当前成果不是完整publication/event接口验收。

未闭：C的创建/终止和所有 callback取消/持有协议；全局图解锁窗口的并发有效性；recipient实际路由递送、传输及云端接受/应用；matcher完整语法沿Q23，不重复读取。下一有种子建议是对本报告五窗与继承 copy实参作合批非作者复核，尤其 result存在门、全同id处理、c0da direct f86c与3340 f9da的metadata差异；不默认展开库内部或新transport研究。

[extract.py](../../analysis/app-publication-research-01-0041-20261025/extract.py) 固定五窗保留raw逐条指令，[verify.py](../../analysis/app-publication-research-01-0041-20261025/verify.py) 独立解JAL立即数并核11个目标、16处精确指令、result字串、全部784 B连续覆盖和0 UNKNOWN，PASS。`git diff --check`另行执行。仅宿主静态读原件，未执行固件/模型/SIM/QEMU/回放/构建/设备/外网；无共享REA操作、无下级代理。

tracked交付本报告、extract.py、verify.py；ignored中间产物 `raw.json`、`checks.json`、`__pycache__/extract.cpython-314.pyc` 留同stem analysis待父窗转存，未推送。工作树与最终commit由交付消息给出。完整UTC始于2026-10-24 17:42:30 UTC，技术冻结为17:45:59 UTC，墙钟209秒；最终提交时间见交付消息；无排队/中断/人为等待，工具等待未独立采样，不能把墙钟冒作有效计算时间；input/cached/output/reasoning token均不可得。技术、提交、停止分别交付，完成后停止不接后继。
