# Q-31 / S-P46：OT owner 事件到周期请求及解除交接

本批恢复同一 owner 的本地接入阶段；作者静态研究，待非作者复核。七逻辑 body 共3658B（八连续片段、1139条记录），不声称完整owner寿命、云端接收或真实调度已闭。七个标准解码器未知厂商字及非body间隙形成下列显式断边。

- 分支 `codex/app-ot-integration-research-01-20261025`，启动基线 `5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd`。原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。
- 第一工具UTC `2026-10-24 18:14:37 UTC`。技术/提交/停止时间分列于交付消息；无有效token计量，不造数。派发预测9–13分钟，中低置信；不是半小时有效工时。
- 采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只离线读取原件与旧材料、标准Capstone逐指令解码；未打开或修改共享REA、分析器/ISA模型、ROM、生产代码或配置；未执行目标/模型/模拟指令/回放/SIM/构建/设备/外网，无下级代理。
- 原字与指令：[extract.py](../../analysis/app-ot-integration-research-01-0041-20261025/extract.py)、同目录本地 `evidence.json` / `instructions.txt`；语义清单 [contract.json](../../analysis/app-ot-integration-research-01-0041-20261025/contract.json)。本地生成物随交付清单由父窗转存。

## 继承及去重

最小派发S-P46在prep报告527行；认领精确ID Q-31。先读主仓reverse-design §3.1/3.2/5.1/7与管理当前Q-31行。元数据 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` 的七地址项只提供extent/directcall，不作为函数语义证据。

直接继承主仓 `evidence/rea-0041-20261017/evidence/upper-miio-b.md`：

|旧根|已存在合同|
|---|---|
|a01106f2 / ev_3b006d151d60a4c0666a982a7b583c03eb17cb2a375bf8bdedba72ac6bdc9884|B+8c、B+880两child；event_on第二child的1/5/9/10→a0112dae，其他parent API保持数字|
|a0110788 / ev_fed264e8febd84155f55a3ea96b02d2f198fbc22194ca0bf56d1850b312f38df|注册/解除调用：a01ab462(parent,a010fd4e,B)、a01ab462(B+40,a01129be,B)；event_off第二child四数字；a01ab634(*(B+884),a01137f6,B+880)及a0110aca；两child交a01ab368；不free owner，固定返回0|
|a0111420 / ev_715f044e905ca51fde778ab4788da1775244f18bf1a3c47f5513b8840ace9a25|dyna_params的pull秒*1000，仅变化时写ctx+110c并以ctx重新schedule a0110aca；无范围/溢出认证|

SDK沿 [F11](miio-request-ownership-f11-0041-20261024.md) / F12与Q24限定接受合同：a0111ff6使用D+4进入a011f9da；正常正长payload在a011f86c同步复制到独立len+1缓冲，callback/user只复制指针值，user指向对象不深拷贝；提交0不证明消费/传输成功。没有再读SDK body，也没有把其合同推广到a010d8ca或其他框架API。

## 本轮观察及修正

没有对旧报告作语义修订。以下对象关系来自实际减常数及调度实参，不从名称推：B=两接入根的owner，C=B−0xe8，E=B+0x880=C+0x968。event a1=E（s1=E−880=B，s3=E−968=C）；periodic a1=E并求C；owner callback a1=B并求C。根注册值与此局部布局一致，框架真实回调ABI/持有/整个寿命仍止API。

特别区分：a01109d6不是本批请求的云reply callback。它由a01137f6同步调用，输入(C,栈descriptor)，构造 `_otc.info` 并返回序列化结果。本批a0110aca真正提交的callback地址为a01102d8，a01137f6为a0112260；两者不在本批body范围。

## 真正新增：有限阶段合同

```text
旧根 B / children B+8c,E
  event 1/5/9/10 -> a0112dae(event,E)
     9: latch 0->1 -> schedule(periodic,E) + schedule(pull,E)
                      + 框架定时(B+40,...,B) + 可选syncfixedip提交
    10: latch 1->0 -> cancel(periodic,E),cancel(pull,E)
                      + cancel本层B定时 + 框架通知/计数
  a010fd4e(...,B) -> C列表/数字状态/1000阈值 -> API，返回1000
  a01129be(...,B) -> C同latch门/OTA时间门 -> a0112734(B) -> SDKcopy
  a01137f6(...,E) -> a01109d6(C,D) -> SDKcopy -> 临时资源归还 -> 返回1800000
  a0110aca(...,E) -> pull JSON -> SDKcopy -> 临时资源归还 -> 返回E+110c
旧解除根 -> event_off/cancel/child API；不代表全owner或排队callback终止
```

### 1. 事件数字门及状态宽度

`a0112dae@2e02..2e3c`读event+1c（word），只分支1、5、9、10，其余走恢复寄存器返回，未见固定返回码；不将残留a0命名业务返回。字符串日志不认证事件生产者语义。

|ID|本层字节/word与控制（地址均0xa011前缀）|
|---|---|
|1|2e70清B+1a0c word；2e78 raw未知影响后续a4==2门，故不能认证该门来源。该门满足时从*(E+1018)取函数表+18，以(instance,栈4B,4)取值，mod16000后schedule(*(E+4),a010fadc,delay,E)；非0调用a010fadc(0,E)。随后a010d8ca(C+2390,a010f702,C)，B+1a68 word递增。未知门不吞掉，a010fadc不展开。|
|5|2f38检查B+20 byte；零则返回，非零以sh清B+20和+21两字节，再a01abcb6(E,B+4)。不以名称推该API是成功/恢复。|
|9|2f54读B+1a08 byte；已非零只日志后返回，0才写1（changed门）。delay=unsigned(B+1a0c)%1800000；a01ab648(*(E+4),a01137f6,delay,E)，再a01ab648(*(E+4),a0110aca,1000,E)。a01196d6(B+40,a010fd4e,1000,B)。通过*(B+1a10)的函数表+18向B+1a0c写4B种子。通知a010d8ca(C+2390,a010f6be,C)，B+1a60 word递增。上述schedule返回未被当作成功保证。|
|10|2e46检查同byte，零则直接返回，非零到32ac清0。a01ab634(*(E+4),a01137f6,E)、同a0110aca；a01ab462(B+40,a010fd4e,B)、同a01129be；a010fcf8(B)止API；清B+1a58/+1a5c两word；通知a010d8ca(C+2390,a010f6e0,C)，B+1a64 word递增。|

ID9可选支路：B+21 byte为零时申请32B X，清其前24B，调用a01201fe(X)，写X+18=a0113428、X+1c=B；申请0x558B JSON区，id来自a0110984(C)，method=`_otc.syncfixedip`，params.version的值穿过3154未知字，params.httpdns数组元素来源穿过322a未知字。循环上界X+14 word，元素以栈64B转换/长度API加入JSON；不能从未解码字补出数组布局。序列化后D的id、来源byte0、len/payload、callback=a011ea12、user=X送a0111ff6(C,D)。提交非0归还X；0保留X供callback浅ctx使用；payload不论提交结果均交free。序列化失败走同归还；payload分配失败也归还X。X申请失败只日志后继续。最后a010db36(C)非0或a010db68(C)非0时a01196d6(B+40,a01129be,60000,B)，否则返回；这些API含义不展开。

### 2. 两个本地callback和OTA同步适配

`a010fd4e`：a1=B，C=B−e8；取C+d8锁API(-1)，遍历C+d0链，哨兵地址B−18=C+d0。node+34 word取低16位；==1且a005fa54(node+3c)>1000时a01af166(C,0,1)；==2且同阈值时a01af166(C,node+38,2)。其他状态/未超阈值取node.next继续。到哨兵解锁并a01af798(C)，返回1000。锁、elapsed API、node生命周期/真实tick wrap止边；不能推锁外其他callback串行。

`a01129be`：a1=B，C=B−e8；C+1af0 byte（即事件B+1a08）为0返回60000。取C+b8/+bc的64位值，若全0，以ot_config/ota_start_time读8B，返回恰8才接受，否则清0；同样C+c0/+c4与ota_dura_time。任一结果为0则调用a0112734(B)并返回600000。非零路径取得a005fa36()的低word并以高word0比较开始值，部分比较可见；2ad0/2b0e未知，且后者之后进入12B非body间隙，故完整时间算式/返回不能恢复。可见另一路2b2e也调用a0112734(B)并返回600000。不得补NOP或猜64位加减语义。

`a0112734(B)`：C=B−e8；id=a0110984(C)。申请40B X，再申请0x558B payload；X+0=id、X+c byte=0、X+20=payload，27bc未知使X+1c长度初值/某写入保留未知。JSON字段：id同id，method=`_sync.ota_sync_update`，params.type_mark=1；did由C+0/+4两word交a01b3af8写栈32B再以实际strlen加入；params.sync_firmware=a010db36(C)，sync_mcu=a010db68(C)，gmt_offset=a010d922(C)。三API只返回值来源，不认证含义/单位。序列化API(Ctx,0,X)成功后由X字段填栈D，callback=a011493e、user=C，a0111ff6(C,D)。不论返回0/非0均归还payload和X；payload先归还。序列化失败也归还两者；payload申请失败只归还X；X申请失败无后续。正常正长SDKcopy保证caller临时payload无需保持到reply；厂商字导致本层长度初始化不闭，不能无条件认证任意提交数据有效。原函数无固定业务成功返回约定。

### 3. 周期请求：字段、id、返回与归还

`a01109d6(C,Q)` 是同步serializer，Q至少承载id、len、payload：先id=a0110984(C)写Q+0；取Q+20 payload、Q+1c容量建栈writer。method=`_otc.info`，id字段的实际a2来源越过0a14未知字，保留断边；params由a01ac7c8(C,writer)填；再a010d8ca(C+2390,a010f604,{writer地址,C})，只承认栈descriptor同步传入，是否被该API深copy/留存未知。终结并以a00602e6(writer,0,Q)序列化，0返回0，非0转换−1。Q/payload为caller借用，不在本函数free；未展开params大容器。

`a01137f6(...,E)`：C=E−968，栈Q清40B；申请0x558B payload，置Q+1c=0x558、Q+20=payload，调用上serializer。成功后以a01aef64按字面`"token"`找替换字符串，结果为空则用payload继续按`"bindkey"`；临时结果仅用于日志并在提交前free，不把该日志字符串当发送payload。以a011f9da(E,Q,a0112260,E,load32(E+1104),0)提交；提交结果仅日志。成功/失败之后均归还payload并清槽。若payload申请或serializer失败，仍走随后a01137d6(C)转发API；该API返回0才a01ab648(*(E+4),a0110894,5000,C)。固定返回1800000，不能等同已成功设置周期或云接受。

`a0110aca(...,E)`：id=a0110984(E−968)，申请0x558B payload；栈writer建JSON `{id,method:"_otc.pull_ip_list",params:[]}`，栈Q除id/len/payload外先清36B；序列化成功才a011f9da(E,Q,a01102d8,E,load32(E+1104),0)。无论提交0/非0、序列化失败均归还payload；分配失败不提交。所有本地出口返回load32(E+110c)，即旧dyna_params变化更新的周期槽；不认证单位或真实timer调度。SDK callback=user E是浅持有，需要E后续仍有效，而本批未证明该寿命。

## 未闭边界和检查

七个unknown逐字保留：2e78=`0b475981`、3154=`0bc64c58`、322a=`0bc57c45`、2ad0=`7717c7c0`、2b0e=`7715e5c0`、27bc=`0b50ea4a`、0a14=`0b46e95a`（地址前缀0xa011）。没有修改ISA模型或套用私有规则认证。a01129be仅29be..2b11与2b1e..2b5d为body，中间2b12..2b1d共12B只存raw不解码、不计body；2b0e后续控制不能跨空隙补猜。

框架a010d8ca/d922/db36/db68、a01196d6、a01201fe、a01137d6及公共JSON/allocator/parser/formatter/SDK均止API，没有扩新大容器、网络/OTA下层。事件真实意义及生产者、同步通知是否copy、owner/child全寿命、callback排队/取消并发、完整OTA时间条件、定时器运行/溢出、云端实际接受和设备动作未闭。新七body的有限阶段可重建，但不标全接口闭合。

检查仅静态：原件大小/SHA、VA映射、八片段边界和3658B总数、逐指令raw/size走到精确end、1139条和七unknown清单、JAL目标及字符串原件核对、git diff --check、精确路径提交范围。未跑目标或历史脚本。报告相对链接应随父窗原路径整合；主仓绝对旧证据无需在worktree复制。

技术完成UTC：2026-10-24 18:18:58 UTC（首工具至技术完成261秒）。技术静态校验通过：18个普通JAL字段独立取位、19个字符串原件匹配。工具调用正常返回，无单独排队/中断等待计量；不把墙钟等同有效计算工时。提交与停止UTC另由交付回执记录。
