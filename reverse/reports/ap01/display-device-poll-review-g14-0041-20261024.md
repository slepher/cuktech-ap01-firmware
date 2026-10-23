# G14：fb0 poll / revents 通知条件链独立复核

2026-10-24；基线 `72c84b7`；独立树/分支 `re0041-g14` / `codex/re-0041-g14`。**限定接受 G13 的正常 fb0 注册 ops+20=`a0132116`、P 双槽及 `a003e2a0` 到已安装 callback 的条件连接；无语义纠正，新增功能 0，来源认证 0。** 实际 open 命中哪个 inode、硬件异步事件及实际 mask4 仍未知。以下是静态恢复视图，非原源码、运行证明或完整结构体。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|已有行为和本轮取用|局限与本轮缺口|
|---|---|---|
|[G13](display-device-poll-g13-0041-20261024.md)、[evidence.json](../../analysis/display-device-poll-g13-0041-20261024/evidence.json)|fb0 正常注册、inode ops/private 写入、表 poll 槽、设备两槽、立即通知 helper|独立核表绑定、P/slot 别名、word 宽度、callback 参数和条件；不把静态表等同实际 fd 身份|
|[G11](display-ready-producer-g11-0041-20261024.md)、[G12](display-producer-review-g12-0041-20261024.md)|fallback ADD 把 P=node+14，requested=node+18；arg=node+20、callback=node+24、revents=node+1c；已装 callback a0109b8e 读参数+c 后写 byte(node+10)=1|注册/materializer 原序与对象生命周期直接继承；不再次恢复 ADD、rearm、collect 或旧 initializer|
|[G09](display-ready-dispatch-g09-0041-20261024.md)/G10、[G07](display-alternate-work-g07-0041-20261023.md)/G08|同 fd 桶、watcher、输出消费者及显示业务 mask4/刷新链|消费者和显示业务全部继承；callback flag 不证明 collect 得到非零事件|
|F05/F07、G13 引用的 coverage 和较晚 round3 有界复用记录|配置 `/dev/fb0`、正常 open 的 pathname/flags3 与后端首 word fd；旧 body 范围及来源边界|不重检全部 ZIP、完整阶段或设备；不将 G13 的有界未命中扩大成历史从未恢复|

REA skill 按留存 Evidence 与主树绝对路径只读 ROM 复用；没有打开、共享、切换 REA target/database。G13 沿用的 extent Evidence 为 `ev_8a2b060d0845dc16c99a4cdbbbe48e775d0ede8a16577048097c3a78e52e83f2`（a0132116）和 `ev_564da8a679b82c09090d06388230fb67447ca45c5bf47baf9fb0022885ac9f14`（a003e2a0）；本轮不虚构新 REA ID。

## 本轮复核或纠正

|核查项|判定|原指令与对象依据|
|---|---|---|
|正常 fb0 注册绑定|接受|6a14..6a2a 的 plane 数==1分支用 `/dev/fb%d`、格式实参0；6a32 把 s3 给 a2，6a34 得 ops=`a01c1368`，6a3c 调 a01b5a12。该函数5a20保存 a1至s1、5a22保存a2，5a4a/5a4c写 inode+10/+18。不能由调用存在推注册成功|
|具体 poll 方法与间接 ABI|接受|只读表 `word(a01c1388)=a0132116`；e388 读 inode+10，e38c 取 ops+20，e394恢复P，e398 `jalr a6`。file/setup 的既有 G11 分派合同继承。2122/2124取 inode=file+c、D=inode+18；2126取F=file+10；D/F身份依赖实际正常open|
|设备两槽与私有回指|接受|214e读F+8，2152读F+c；216c构造i+2。2170原字04e7970b字段为 addsl a4,a5,a4,2，2174写word(F+i*4+8)=P；2176原字0497948b得到slot=F+(i+2)*4，217a写word(P+14)=slot。两者同槽，P+14不是事件字段|
|正常 setup 条件与返回|接受|2180调用a01320e0，2184调用a0059678，2188按返回**非零**才到218e；218e/2190/2192/2194为 `(slot,1,4)`→a003e2a0。通知后218a返回0，恢复mstatus；满两槽路径返回−16。helper内部算术沿G13继承，不将未认证字段命名为硬件ready|
|teardown/所有权|接受|219a从P+14取slot；219e先清word(slot)，21a2再清word(P+14)。不free；F槽借用P，P借用槽地址。node/file后续归还沿G11/G12，不因通知转移所有权|
|通知参数解引用|接受|e2cc原字4499450b解为32位 indexed load `P=word(array+i*4)`；实际array=slot,count=1。既有只读lrw规则无base回写，不能把slot本体误作P|
|revents写入宽度和重读|接受|e2d2/e2d4分别word读P+4/P+8；e2d6..e2dc得 `r=((requested\|0x18)&mask)\|old`；e2de/e2e2检查r&0x18。e31e `c.andi a5,-5` 后e320回e2e4，故错误位存在时清bit4。e2e4 **word**写P+8=node+1c，e2e6再word重读，不能合并|
|通知条件及callback ABI|接受|e2b4原字69c1为s3=0x10000；e2e8算 requested&s3，e2ec再OR重读revents，e2ee非零门。e2f0取word(P+10)，非空才e2fc `jalr a5`，a0保持P。因此恰好接G11/G12安装的a0109b8e：P+c=node+20存node自身，再写byte(node+10)=1|
|flag和ready的区别|接受|requested包含0x10000且revents=0仍可通知，故flag=1不足以证明ready。mask4这条具体路径只有requested含4且未被0x18错误位抑制时才可得到revents bit4；实际条件/执行均未观测。materializer仍按G12两次读取合同处理|

不需要修改 G13 伪代码或结论。保留的局部条件式是 `reread | (requested & 0x10000)`；不是仅 `revents!=0`。回调发生在 setup 返回/ADD 挂链之前的可能顺序沿 G13 原指令保留，不推并发结果。

## 真正新增

新增 ROM 功能 **0**。独立审查只验证 G13 新接入合同，未重导 G07/G09/G11/G12。补留 e2b4 的2B及 e31e..e322 的4B，分别消除原报告稀疏窗口未包含 0x10000 常量和清bit4尾部分支的审查缺口；这6B属于旧结论复核，不计新增行为。

[review.py](../../analysis/display-device-poll-review-g14-0041-20261024/review.py) 实际通过：G13 的99条留存raw逐条与原ROM相同；49项独立I/S/压缩访存/寄存器移动/JAL/厂商字段及别名检查通过。[review-result.json](../../analysis/display-device-poll-review-g14-0041-20261024/review-result.json) 保存结果、检查索引和上述6B，不复制整函数。映射VA−0x9ffff000，主仓 `roms/0041/ap01-1.0.2_0041.bin` 只读。厂商语义仅引用现有 `ap01thead2.sinc` 的 addsl/lrw 规则，未改模型或认证完整ISA。未执行ROM、SIM、构建、回放、设备或外网；只写本独占报告/analysis。提交前检查差异和 `git diff --check`。

## 未闭精确边

- **未核，继承**：实际板上选择单plane fb0分支、注册成功、open命中对应inode且ops/private未更换、F初始化及fd复用。静态正常注册表身份不能升级成运行时同一性。
- **未核，继承**：a0059678条件何时实际非零、硬件异步生产者何时通知、实际mask4及显示刷新触发；mstatus临界区不是IRQ观测。G12原“具体设备方法未知”已由G13条件连接补齐，其运行事实限制仍保留。
- **未核，继承**：精确NuttX/LVGL版本、编译配置/完整来源，其他设备、完整VFS/IRQ、ring/MOD/DELETE与并发/重入。不将同名source路径作为未修改源码认证。

事实限原字节、表值、宽度/调用/对象别名；所选显示fd的设备poll身份是依正常fb0注册/open条件成立的推断。一个后继闭包可只追同F槽数组的一个已定位异步通知调用者到a003e2a0；本轮不扩搜索或自行承接。若无实际caller种子，应保持这一精确断边。
