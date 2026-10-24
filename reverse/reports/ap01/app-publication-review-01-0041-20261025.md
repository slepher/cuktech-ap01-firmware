# Q24 publication 提交与事件归还：非作者复核

状态：**可独立使用阶段已闭合但接口未闭**。限定接受作者 b2c1453681afa24b306834a49286b045bd6e592f 的五窗阶段；行为纠正0，新增业务0。复核者未参与作者取证，仅本轮差集和必要SDK API前提；不复验Q23 matcher body。

认领Q24；分支 `codex/app-publication-review-01-20261025`，启动基线 `7e4f4dca88af733319500704ddfeb2046ec2006b`。独占本报告与同stem analysis。主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`，作者报告 [app-publication-research-01](app-publication-research-01-0041-20261025.md)。原件 `roms/0041/ap01-1.0.2_0041.bin` 6769704 B，继承CATALOG SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000；本轮核长度及实际五窗，不重算全ROM摘要。

预测3–5分钟，中置信；首工具UTC 2026-10-24 17:58:39，材料读取完成17:59:07，独立技术停止17:59:36（首工具至技术57秒，提前闭合即交付）。完整提交/停止时间另由交付消息给出；无人工等待或中断，工具等待未单独采样，墙钟不等于有效计算时间。input/cached/output/reasoning token不可得，不估造。

## 继承结论

遵循主仓 reverse-design 3.1/3.2/5.1/7、rolling-management顶部及Q24补位行；S-P36最小包415行起。Q19/Q21的D/P生产和caller返回消费为已交前提，不重复body。Q20 topic/edge对象布局及Q23 `a0118a40` 返回0匹配沿既有API，不展开matcher。

旧SDK来源为主仓 `evidence/rea-0041-20261017/evidence/miio-recovered.md:271` 及275行，Evidence `ev_3c1987c9d0b0223c28b66671236fb3303aea3c0ccb028253ec8660393dd03e02` / `ev_e7a80442abbf3a1af9636c77de5a9a5b9993e5b10a7b0758e6ffcff375d61317`。前者清message+0x10起8B后委托；后者在提交返回前为Q复制id/type/metadata/len、len+1 payload并补NUL，cb/ctx仅标量保存，失败销毁Q。继承API证据，不重做allocator、queue或session内部。较晚同文302行说明末参数是重试预算；本复核使用raw末参数0/2，不另赋时间单位。

## 本轮复核或纠正

独立 [review.py](../../analysis/app-publication-review-01-0041-20261025/review.py) 仅读ROM，使用Capstone RV32/RVC连续解码五个精确窗：0xa011c0da..0xa011c203 298B、0xa0113340..0xa011339b 92B、0xa0116b5a..0xa0116c23 202B、0xa0116db0..0xa0116de5 54B、0xa0116ad0..0xa0116b59 138B，总784B/279指令。逐窗原件与作者raw完全一致；9个核心JAL按原字立即数字段独立算目的地址，result NUL串亦独立读取。没有执行或导入作者extract.py/verify.py，没有目标执行、共享REA/profile改动。本轮Capstone 5.0.7解码属宿主静态证据，不冒用旧REA profile。

|验收连接|独立读得的证据及结论|
|---|---|
|recipient方向与sender|c15a置a1=K，c15c置a0=T+8，c160调用a0118a40，非0跳过。每匹配topic遍历edge，不见本层去重；c188从E+8取peer、c18a长度0x30复制到B。c1a4只读word(B+0x18)作门；c1aa长度8、c1ac源B+0x18、c1b0目的D+0x14。先缓存next再解锁，不证明跨unlock有效性。|
|direct SDK与返回|c1ba/c1be取D.ctx/cb；c1c8 message=D+4，c1ca session=C+0x174，c1cc原字ef30006a到a011f86c，末参数0/2000。c1d0失败跳过，c1ee成功置flag1，后续失败不撤销，出口c152返回flag。producer消费行为沿Q19/Q21，不新增已验caller。|
|两session选择|3348..3356计算C+0x1134 bit0x20，优先C+0x968、word(C+0x1a6c)、末参数0；否则337e..3396检查C+0x1c8 bit0x20，C+0x174、word(C+0x8e0)、末参数2。都无返回−12；3372原字efc08066到a011f9da，共用epilogue原样返回。此路清D+0x14 metadata，与direct f86c不同。|
|同步copy接合|message=D+4，因此message+0x10=D+0x14(sender8)，+0x1c=D+0x20(length)，+0x20=D+0x24(payload)。与旧f86c API接合后正常成功交接不保留临时D/P/B/K地址；ctx=C仍为借用，不能外推C寿命。|
|event result门|6b68/+6b72取reply payload/len；6b90 parse；非0直接恢复state0。6b9e构造0xa06124b8=result，6bb2 expected-type=0，6bb6 lookup；返回非空保留status0，空置−1。解析成功分支6bec cleanup在6bf6锁C+e4之前；6bfa读取reply.id，6c02置state2，6c04/06失败改0，6c08调用helper(C+dc,id,state)，unlock后返回0。只要求result存在，不检查内容成功。|
|所有同id恢复与归还|6ae6/6aec缓存节点/next；6b14比较R+0x74=id。6b1a先写pending字节，state0在6b22/26/28读增写retry word，保留record；非0经6b36 unlink、6b54 free，然后6b58继续缓存next。无pending前置门、无首命中break。所有同id均处理，retry无饱和门。|
|即时callback|6db0..6de5只取reply.id供日志，a1/ctx无使用，末尾返回0；不解析result，不释放事件。|

无行为修正。每peer提交的payload独立复制、同peer跨topic可能重复提交、flag0含无recipient及全部失败，均是上述控制流与继承API组合的静态结论，不是实际递送观察。

## 真正新增

新增业务0；新增独立复核结论为上述五窗阶段可限定接受。没有把字节重读、独立脚本或检查数记作新增功能，没有重开matcher、transport或公共库实现。

## 未闭精确边与交付

完整C创建/销毁、callback取消和持有、跨unlock缓存next的并发有效性、recipient实际递送、网络/云端接受及物理应用仍未知；局部锁、callback返回0及result存在不能补足这些断边。无新后继研究认领；后续若有实际种子应由主窗查重登记，不能沿未知自动扩扫。

检查：784B连续解码/作者raw一致、279指令、9核心JAL、result字串PASS，git diff --check另执行。未执行目标、模型、SIM、QEMU、回放、构建、设备或外网；未修改ROM、生产、配置、共享分析器/REA，未派下级。精确提交本报告及review.py，不推送。ignored中间产物为同stem `checks.json` 和 `disassembly.txt`，交主窗转存同相对路径后清理；作者产物已在主树，本复核不复制/覆盖。
