# G19：Pogo poll 的登记撤销与同 fd 后端接入

2026-10-24；基线 `0fa2089`；独占树/分支 `re0041-g19` / `codex/re-0041-g19`。**补齐实际取消端的软件状态/链持有合同，以及同fd剩余watcher掩码聚合和两个下层提交接口的原序。** 请求mask清零时，f442撤销更新链与fd bucket中的本watcher登记；请求mask仍非零时只保证它进入待更新链。随后的e212根据可选记录上下文处理同fd记录，并以原op2/op3或六参接口交给下层；没有以返回值判定成功。此为条件正常路径静态恢复，待非作者独立技术复核，不认证OS撤销、排空或完整Pogo关闭。

使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，遵守管理/历史共同规则及J05范围。只读主仓ROM/旧JSON和本地既存规则，未打开/切换共享REA target/database，未执行固件、SIM、模型、构建、历史回放、输入实验、设备或外部服务；无漏洞/异常输入/缺陷验证。仅写独占报告/analysis，不改生产代码、ROM、配置或分析器模型，不撤销他人修改，无下级agent。以下是分析字段/伪代码，不是原C源码。

## 继承结论：已有→行为→局限

|出处|直接继承的合同|本轮范围|
|---|---|---|
|[J05](transport-reuse-gap-j05-0041-20261024.md)|真实调用端与确切JSON pointer、索引Evidence、四complete/final SIM/ZIP和较晚报告去重；两个callee只有extent/directcall元数据，page-logic的e212命中只是caller元数据|不因旧无标题判缺失；不重复原complete/最终ZIP/全资源或全函数导出|
|[C05](pogo-close-dispatch-c05-0041-20261023.md)/[C06](pogo-close-dispatch-review-c06-0041-20261023.md)|Pogo type8 close将poll交a009f972，随后登记pending；最终callback收原poll，context/计数来自其业务callback|不重做close/callback/ctx计数；本题不证明后续再次消费pending|
|[G07](display-alternate-work-g07-0041-20261023.md)/[G08](display-alternate-review-g08-0041-20261023.md)|stop以 `(loop,poll+34,17h)` 调f442，之后清active/必要时减loop计数，再以 `(loop,word(poll+58))` 调e212|完整stop原序直接引用；只展开已留存种子对应的取消/同fd接入|
|[G09](display-ready-dispatch-g09-0041-20261024.md)/[G10](display-ready-review-g10-0041-20261024.md)|watcher=poll+34；watcher.fd@24=同poll+58；watcher+14是fd bucket节点；watcher+c是loop+2c更新链节点；+1c用于请求/ready过滤，+20与+1c比较；bucket地址loop+34+(fd<<3)，每登记节点增loop+3c|不再恢复注册/ready；两个mask是软件字段，不直接叫OS当前状态|
|[F03](miio-loop-close-f03-0041-20261023.md)/[F04](miio-loop-close-review-f04-0041-20261023.md)|a0098b4a(node)双链摘除，不free/不自环；回调ABI和pending消费已有|链helper不重导，不套MiIO业务；后续自环由本caller自身完成|
|page-logic record15，Evidence `ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`|a0024906为按字节填充服务的旧body；e212是其caller之一|这里只需要 `(stack16,0,16)` 初始化调用，不展开填充算法或认证标准库来源|

主仓只读根 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。f442/e212的旧extent及directcall Evidence沿J05，不把元数据变成旧body语义认证，也不发明新REA Evidence ID。可靠旧合同直接引用；新必要字段/门以原件稀疏核验。

## 本轮复核或纠正

旧语义纠正0。J05所列同对象连接得到必要接入支持：G10的watcher+24加poll偏移34正好为poll+58，f442取消对象与e212输入fd因此来自同poll，不能凭其他对象相同偏移替换。

本轮把“取消”精确拆成软件兴趣字段更新、节点持有撤销/待更新和下层服务调用。字段视图如下，均为十六进制偏移：

|对象|字段/用途及证据|
|---|---|
|watcher W|callback@0继承；更新节点@c/+10；fd bucket节点@14/+18；请求mask@1c；软件比较槽@20；fd word@24。f442写1c、清20，不写callback@0或fd@24|
|loop L|后端对象指针@14；下层handle数值@20；更新链哨兵@2c/+30；fd buckets指针@34；fd容量@38；登记节点计数@3c。计数对应G09逐watcher增量，不自动等同不同fd数|
|后端对象 B=word(L+14)|可选记录上下文R=word(B+114)；B+84作为六参服务的第二参，不擅自赋正式类型|
|R与记录|R+0下层六参服务第三参，R+4记录数组，R+8有符号比较消费的count；record stride16，word0为这里清/聚合的mask，word8为fd；其他字节不补含义|

`+20`称软件比较槽：G09注册端比较它与请求mask，本轮在取消端清零；没有证据把它升级为OS已成功应用的mask。R虽保存记录数组及count，本轮没有取得其producer/正式backend类型，故不命名Linux/NuttX事件结构或真实ready生产机制。

## 真正新增：软件撤销与同 fd 服务合同

### 1. a009f442(L,W,mask)：撤销或排队

`f442/f444/f446` 读取W.fd并与−1比较，相等直接返回。正常fd非负和fd<word(L+38)是必要前置；负fd另走assert调用，越容量在f474以BGEU跳出口。本题不研究assert返回/异常fd。

`f478..f484` 严格按原序执行 `W.mask1c = W.mask1c & ~mask`，不是把整个字段无条件置0。对于本stop传入17h，是否恰为0由原请求mask决定，不能先假定所有其他位为0。

|结果/位置|原序与责任|
|---|---|
|结果0，f488..f496|以W+c调a0098b4a摘更新节点，然后两次SW将W+c/+10均设为W+c，自环初始化；最后SW清W+20。不能把callee摘链本身当自环或free|
|结果0，f49a..f506|重读W.fd和L.buckets，按fd<<3取bucket。保存当前节点的next，比较 `node−14 == W`；相等才摘该bucket节点、检查/递减L+3c。继续按保存next遍历，反复重读fd/bucket哨兵。不是清整个同fd bucket，也不是对其他watcher作删除|
|结果非0，f508..f520|若W+c的next已不等于W+c则直接返回；否则将W+c尾插L+2c更新链。保留W+20和fd bucket登记，没有此处直接下层提交|

没有直接callback调用或对象释放，callback word0继续保存在W中；节点脱离某条软件链不证明OS事件已撤销，也不证明其他线程/已取出记录中没有这个callback。底层业务资源和context归还不在上述存储中。

### 2. a009e212(L,fd)：聚合剩余登记与记录处理

入口保存L、fd，取B=L+14和R=B+114。下列记录/掩码均为word；fd容量门用unsigned，R的记录下标与count比较用signed BGE，loop下层handle的部分分支用signed BLT零门。没有合并这些符号条件。

**R=0：** `e232/e23a` 先把本函数栈16 B填0。若fd超出容量或其bucket为空，直接以 `(word(L+20),2,fd,&stack16)` 调 `a010e722`。否则逐bucket节点把 `word(node+8)`（即watcher+1c）OR到stack.word0；读handle后若signed<0直接返回，非负才写stack.word8=fd，以相同服务的op3调用。该聚合路径没有另加“聚合mask必须非零”门；不能把另一分支的零mask门搬过来。op2直达路径也没有这个signed handle门。

**R非零：** `e27a` 建fd*8、下标0及−1常量；每轮以stride16取record，fd不匹配只推进下标。匹配时 `e29c` 先清record.word0，再遍历同fd bucket，将各仍登记watcher的请求mask聚合回record.word0。由此保留的是**同fd仍登记对象的集合**，不是只取刚关闭的W，也不以删除一个W自动撤销另一个W的兴趣。

|匹配记录的聚合结果|原行为|
|---|---|
|0|e2e8以SW把该record.fd写成−1，随后下标+1继续遍历。record count不在这里递减，也没有free记录数组|
|非0|若word(L+20) signed<0直接返回；否则将聚合mask与fd写进本函数栈记录，以op3调a010e722并直接返回。不是继续处理全部后续记录，也不进入下述扫描完成服务|

R非零而扫描完成时，重新把stack16填0，调用：

```text
a009e0e6(word(L+20), B+84, word(R+0), 2, fd, &stack16)
```

`e324` 随后重读容量；fd仍在容量内才重读bucket，将每个节点+c，即watcher+20软件比较槽清0。调用前后没有判断六参服务数值返回，不能把这个清槽视为已收到成功回执；其他watcher的请求mask@1c在此保持。R=0路径、R非零聚合非零早退路径不执行这段全bucket比较槽清零。

### 3. 提交 ABI、返回消费与所有权界限

`e25a..e266`、`e2ca..e2da`、`e30c..e320` 的寄存器锚点分别建立上述四参op2/op3与六参op2。op只是原立即数；没有正式服务语义或来源证据，本报告不把2/3命名为OS DELETE/MOD，不叫OS close。

16 B记录是当前函数栈对象；指针只作为a010e722或a009e0e6实参交出，本body没有把该栈指针保存到L/W/R。本轮未展开下层服务如何消费/复制或保留它，故同步借用完成、异步副本及实际提交成功都留作下层边界。R中的记录数组是已有指针；本函数原位修改mask/fd，不取得新heap所有权。

四参服务返回后 `e26a..e278` 仅恢复寄存器并返回，a0未被比较或替换。六参服务返回后继续容量/bucket清槽，同样无数值成功判断；其他早退路径没有统一业务返回值认证。G07旧stop在e212返回后也仅恢复/返回，C06 close接着进入pending登记，因此本正常close caller链没有通过此数值确认取消成功。不得用“函数已返回”替代完成/排空证明。

## 精确原字、来源与验证

[verify.py](../../analysis/pogo-poll-cancel-backend-g19-0041-20261024/verify.py) 只读主仓 `roms/0041/ap01-1.0.2_0041.bin`，映射 `VA−9ffff000`，保存必要字段锚点到 [evidence.json](../../analysis/pogo-poll-cancel-backend-g19-0041-20261024/evidence.json)，不导出226/312 B整函数、整fd backend或完整源码。原有callee元数据用于选址，不作为其指令语义依据。

10个indexed原字逐项拆opcode/funct3/top5/rd/rs1/rs2/shift；用现有只读 `ap01thead2.sinc` 的addsl/lrw/srw规则确定加法、word读/写。其中f4a0 `0x46e7c50b` 读bucket head；f4ae/f4f4 `0x06e7978b` 构造fd桶哨兵；e29c `0x40f6d00b` 向record.word0写zero；e2a4 `0x4106c68b` 读同fd bucket；e2e0 `0x40f5560b` 写聚合word。规则是既有本地profile，不等同独立厂商规范、原源码或精确libuv版本；未改模型，标准库/整库排除0。

实际运行独占脚本：**73项稀疏检查及10条厂商字段实例PASS**，含必要JAL、标准/压缩门和访存位域独立解算；没有模拟或执行这些指令。JSON解析、相对链接和 `git diff --check` 另行通过。作者自检待未参与研究者独立技术复核。

## 精确未闭与后继

继承内容不计新增；本轮真正新增是取消端的两类链持有/掩码转换，以及同fd剩余请求集合、R记录更新和下层实参/返回消费。没有新增设备执行、callback运行观察或来源认证。

未闭：a010e722/a009e0e6的服务实现、op正式语义、栈参数消费/复制与成功合同；B+114记录上下文的实际producer/生命周期、并发与重入；真正OS/设备撤销、已交付callback排空/恰好一次；Pogo timer停止、context最终释放和close后再次pending消费。软件bucket撤销与记录.fd=-1只认证这里的指令状态，不扩大成硬件停止或全模块完成。

后继仅保留一个真实新边：`a009e320→a009e0e6` 的六参提交，旧索引范围 `a009e0e6..a009e211`、extent Evidence `ev_5ecc1c04fd168340d2026dfe5ab76a4c73eb4b3fecea6f6f091e514dab87aa7f`、directcall Evidence `ev_054cff139263352630c77f72f9497086efffddf7ec56802fc1fa4b985e332e9d`。可先按本次实际op2输入核它是否消费/复制stack16、如何使用B+84与R.word0及何时向下提交；旧G09/G10也明确该服务成功合同未闭。不得顺此扩大整个882 B的a010e722或OS backend，主体已有覆盖则直接引用。主窗口决定派发，本路提交后停止。
