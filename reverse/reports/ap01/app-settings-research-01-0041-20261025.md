# Q12：原厂 sysconfig 启动读取、校验门与默认回写

2026-10-25；基线 `11c90bc`；独占分支 `codex/app-settings-research-01-20261025`、工作树 `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/settings01`。**`a00ab2e8` 先初始化通知注册头并安装 callback，再尝试从 `/data/sysconfig.bin` 读8B到 live G。read返回不检查；校验匹配则保留，open返回0或校验不匹配则进入默认 helper 并尝试既有 writer。非零读handle始终先交close服务，再决定保留/默认；默认仅写前6B，不是清零完整8B。** 本文是有界静态合同，作者检查通过，待独立复核；不证明真实文件读写或硬件持久化成功。

使用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读取主仓原件与已留存证据；不打开、切换或关闭共享REA目标。未执行固件、模型、SIM、QEMU、回放、构建、设备或外网；无输入实验、漏洞/异常绕过、ROM/生产配置/分析器改动或下级agent。只写本报告及同stem analysis，不撤销他人文件。

## 继承与本题增量

|既有证据|直接继承|本题差集|
|---|---|---|
|[L03](settings-mode-contract-l03-0041-20261024.md)/[L04](settings-mode-review-l04-0041-20261024.md)、[L05](settings-off-mode-l05-0041-20261024.md)/[L06](settings-off-mode-review-l06-0041-20261024.md)|G=`62fc9098`；G+2/G+3的两个setter、reason3/4通知及writer连接；既有消费者|补启动默认值与这些byte接合，不重导UI/通知/消费者|
|[M01](system-settings-halfword-m01-0041-20261024.md)/[M02](system-settings-halfword-review-m02-0041-20261024.md)|`a00a46e8` 以seed0/G/6调用旧算法，原样返回a0；正长度结果数值0..65535；writer以SH保存低16位|补reader如何消费返回和成功/失败门；算法、表、向量求值0|
|071旧writer，`ev_cf4c97ae60f1edbe9156a19d0427799c7c068d79ed1d916e7d8cdc3dd61c3c58`|`a00ab274..ab2e7`完整116B早有：同pathname `a026a21c`，`wb`，非零H后算校验、SH、写8/1、close；结果不检查|不把既有writer重计为新恢复；只补init→默认→writer顺序与读写handle接合|
|072旧reader，`ev_85099f331255aab9e146bc35df48bcdbe3e38160b9802c06864c877f036f7d00`|`a00ab2e8..ab433`完整332B已留存；默认helper仅有32B extent|旧body不是本轮新发现；补其业务/返回/资源合同，必要新读默认32B原件窗口|
|J03/最终应用与已知8B样本、SIM服务|SIM保存/读回仅在原验收范围成立|不替代ROM启动证据，不重跑SIM，不将文件混为PSM或AP01SCF1|

派发的Q12为唯一认领；另对主仓近期非管理报告精确token `a00ab2e8/a00a3a96/SysSettingsInit` 有界查询无命中，L03..M02明确未闭启动策略。此限定查询不是历史从未分析的证明。种子来自071/072实际共享pathname，不是地址相邻猜测；本题未扩到FS/校验算法/GUI/线程/NVS。

主仓只读原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6769704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；`offset=VA−0x9ffff000`。证据文件在主仓 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-071.json` / `-072.json`，真body位于 `structuredContent.normalized_result`（同时可解析 `content[0].text`）。无新REA Evidence ID。

## 启动合同与资源顺序

|地址/原指令事实|结论与限制|
|---|---|
|`ab2fa/ab302`构造 `62fcb4ec`；`ab310/314` SW zero到+4/+8；`ab318` C.SW 8到+0|注册头三个word初始化为`{8,0,0}`，连接L04已验通知读取的同一头；本窗没有节点分配、释放或旧节点回收证据。不能据清头声称完整subscriber生命周期|
|`ab2fe/30c`构造callback `a00a40c4`；`ab308` a1=100；`ab31a/31e` AUIPC/JALR→`a01b2474`|只认证该注册/安装调用边与实参；返回被后续路径/参数装载覆盖。未展开callee或callback，不认定100的时间单位、调度线程或注册成功|
|`ab322..332` pathname=`a026a21c`、mode=`a026a258="rb"`，调用`a0134856`；`ab336`存H到s4；`ab348` H==0→`ab418`|0门走open失败诊断，`ab432`→默认段，无read、无close读handle；非零门进入read。只称既有open类服务，不认证精确libc版本|
|`ab34c..356` a0=G、a1=8、a2=1、a3=H，调用`a0132acc`；下一条`ab35a`立即call校验wrapper|read返回既不保存也不分支；没有读数量成功门、重试或读前清G。8/1是服务实参，不从它们推实际读足8B|
|`ab35e` LHU a6,6(s1)，`ab362`复制校验a0到日志参数a5；`ab364` BNE a0,a6→`ab3fa`|比较完整32位a0与零扩展G+6的u16，调用者本窗无mask/符号扩展。继承M02数值范围后，两边都在0..65535；不应误写为“先截低16再比较”或比较read返回|
|匹配日志后`ab382` s5=1；不匹配日志后`ab414` s5=0，`ab416`回共同`ab384`；`ab384/386` close(H)|校验结论通过s5跨日志/close保存；close返回不是成功门。两种非零H路径各有一次close服务调用，不把静态调用等同下层必然释放成功|
|`ab38a` s5非零→`ab3b0`；否则默认日志→`ab3a8`默认→`ab3ac`writer|close在默认helper与writer之前；读H不传给writer。保留分支没有writer；open失败和校验失败汇合到同一默认路径|

本层未调用setter或`a00a5bbe`通知：启动直接read/default修改live G，与L03/L05交互setter的“先字节发布→通知→writer”顺序不同。共同尾部`ab3b0..ab3e4`仅以LBU/LHU取G+0,+1,+2,+3,+4,+6供诊断；格式中的字段文字不是完整结构定义，不为G+5赋未证名称。

## 默认宽度、读写接合与消费者

默认入口 `a00a3a96..a00a3ab5` 的32B来自原件 `offset=0xa4a96`，原字为：

```text
411122c60008b797fc6223ac070813074016938787092392e700324441018280
```

常规RV32/RVC离线解码与独立字段检查一致：`3a9c` LUI a5,62fc9000；`3aa0` **SW zero,0x98(a5)**；`3aa4` ADDI a4,zero,0x164；`3aa8` ADDI a5,a5,0x98；`3aac` **SH a4,4(a5)**；其余为建栈/恢复/ret，没有其他store/call。故依序写G+0..3为0，再写G+4=0x64、G+5=0x01（小端），总共6B，不覆盖G+6/+7，不额外算校验，不通知。该helper无显式持久成功返回。

```c
// 行为表达，非原源码；服务别名不代表精确库身份。
head.word4 = 0; head.word8 = 0; head.word0 = 8;
install_callback(a00a40c4, 100);
H = open_service("/data/sysconfig.bin", "rb");
keep = false;
if (H != 0) {
    read_service(G, 8, 1, H);             // 不消费返回
    calculated = settings_halfword();    // 继承seed0/G前6B
    keep = (calculated == load_u16(G+6)); // 完整a0比零扩展halfword
    close_service(H);                    // 不消费返回
}
if (!keep) {
    store_u32(G, 0);
    store_u16(G+4, 0x0164);
    known_writer();                     // 独立open("wb")，不是复用H
}
```

writer沿L04/M02：独立open非零W才计算当前G前6B，并以SH更新G+6，再以`(G,8,1,W)`尝试写服务，最后close(W)，两个返回均不消费。若writer open返回0，则默认前6B已发布，但该writer没有更新G+6；本题不将整8B说成已重置/有效/成功持久化。writer无成功返回门可反馈init；init无失败回滚、读回或再次校验。G+6先前值来源在不同启动前提下未由本窗建立，不能假定其为0。

G+2/G+3默认都是0，精确接到L03/L05已验byte及其既有constructor/显示消费者；其与3的比较选择条件沿旧合同即可，不新建枚举或重导GUI。加载且匹配路径则这两byte沿read之后的live G保留。本轮不认证这些值对应的完整时长、所有枚举、显示效果或启动时实际consumer执行。

## 检查、断边与交付

[verify.py](../../analysis/app-settings-research-01-0041-20261025/verify.py)只用Python标准库读取原件，核ROM身份、37条原字记录、I/S/B/J目标/字段、注册AUIPC/JALR目标、默认32B完整窗口、路径/mode与071/072身份/extent；[result.json](../../analysis/app-settings-research-01-0041-20261025/result.json)为PASS。压缩原字与旧332B assembly及离线Capstone解码交叉核对；没有执行目标或算法输入/向量。无新ISA规则、算法、整库来源认证；旧writer/算法/消费者和旧body留存不重计。JSON解析、报告链接及`git diff --check`通过。作者自检不替代独立技术复核。

本接口已回答：read返回不检查、全a0/u16比较、匹配/失败门、默认写宽度与顺序、读H与独立写W的调用寿命、注册头初始化及callback调用边。精确未闭：底层open/read/write/close实际返回和释放/持久保证、G全8B正式字段及所有writer、注册者身份/节点所有权/注销/并发与旧节点处置、callback/安装内部及100单位、真实重启效果。没有必要新业务种子要求扩入库内部；独立复核仅需上述reader/default/资源门与既验连接。

计时：起点工具UTC `2026-10-24 16:56:19`；静态分析/成稿终点 `2026-10-24 16:59:50 UTC`，起点至此墙钟约211.1秒（提交检查在后）；无刻意等待，工具等待仅各本地静态命令回包，未据墙钟推有效工作时长；运行时未提供input/cached/output/reasoning token计数，未编造。预计5–8分钟为派发估计，不据预算延长或扩范围。
