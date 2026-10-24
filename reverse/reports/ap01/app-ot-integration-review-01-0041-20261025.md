# Q-31 / S-P49：OT owner 接入独立静态复核

结论：限定接受作者 `a5abd029fc1a59b550c4c20b5a45ab73892e2fb2` 的七逻辑 body / 八片段合同，语义纠正0，新增业务原字0。只接受本层事件→周期请求、同步 OTA 适配与解除 API 接合，不标完整 owner 寿命或端到端接口闭合。

复核者 `app_ot_integration_review_01` 非本批作者；分支 `codex/app-ot-integration-review-01-20261025`，实际基线 `5a5b732235c5b0d1654c8bc543b92c9cc5331e0b`。派发沿主仓管理记录 Q-31 行及281行补位，S49条件模板583行、成熟动态611行。先读统一流程3.1/3.2/5.1/7和管理顶部规则。作者尚未合并时读取其 `ot-integration01` 树的同路径报告、contract.json、evidence.json、instructions.txt、extract.py/validate.py（只读，不运行作者脚本）；后续主树整合优先使用主树同相对路径。

采用 [reverse-engineer-anything](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 留存证据工作流；未连接共享 REA。原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。

## 独立核对与接受依据

[复验源码](../../analysis/app-ot-integration-review-01-0041-20261025/verify.py) 和 [机器结果](../../analysis/app-ot-integration-review-01-0041-20261025/review.json) 仅静态读原件。独立核七函数八片段全部原字、每条地址/长度连续性、片段 SHA 和精确末端：3658B / 1139条；从原件取位核163条普通 JAL 相对立即数，其中18条关键调用绝对目标一致；19个字符串原件匹配。七处对象计算 I 指令另核寄存器和有符号立即数。没有运行作者脚本、目标或模型。

|检查对象|独立静态观察与接受范围|
|---|---|
|对象身份|a0112dca..2ddc 中 −0x1000+0x780=−0x880、−0x1000+0x698=−0x968；event a1=E，s1=B，s3=C。a010fd64、a01129d0、a0112748求C=B−0xe8；a0113806及0ada求C=E−0x968。故E=B+0x880=C+0x968，不能把三基址统称同一个owner。|
|event数字分派|event+0x1c以word读取，只1/5/9/10；其他恢复寄存器返回。ID5先读B+0x20 byte，非零才以sh清0x20/0x21并调用a01abcb6(E,B+4)。不从日志/名字推云鉴权意义。|
|changed门与schedule|ID9读B+0x1a08 byte，0才写1；B+0x1a0c unsigned余1800000作为periodic delay。两a01ab648的a0=*(E+4)、a3=E，callbacks为a01137f6及a0110aca，pull delay1000。a01196d6的实参是B+0x40、a010fd4e、1000、B。后读*(B+0x1a10)表+0x18填4B种子，并更新B+0x1a60 word。|
|解除|ID10只在同byte非零时清0；两a01ab634第三实参E，两个a01ab462第三实参B、对象B+0x40；清B+0x1a58/+0x1a5c，递增B+0x1a64。旧解除根的event_off/child API及“不free owner”继承；这些API调用不能证明已经排队任务退出。|
|ID1及可选syncfixedip|ID1清B+0x1a0c；2e78未知导致a4==2来源不闭。已见取值/mod16000、schedule的E及非零返回时本地调用a010fadc(0,E)，通知C+0x2390和B+0x1a68递增。ID9可选X=32B、前24B清零、X+0x18/+0x1c callback/user，提交非零归还X，零保留其浅ctx；payload提交后归还。version及httpdns来源经过未知字，不能认证具体值/布局。|
|parent callback|a010fd4e的C+0xd8锁、C+0xd0链与B−0x18哨兵一致；node+0x34低16位为1/2且elapsed unsigned>1000才调用相应API，结束解锁/转发，返回1000。节点寿命和真实时间语义止API。|
|OTA时间与同步适配|a01129be读C+0x1af0，与event latch同字节；关闭返回60000。两个64位配置只接受返回恰8B，零值走a0112734(B)/600000。2ad0/2b0e未知与12B间隙使完整非零时间公式不闭。a0112734的method、id、did双word、type_mark=1及三个API返回字段可见；27bc处长度初值不猜。同步提交callback=a011493e、user=C；payload/X按本地失败和提交路径归还。|
|同步serializer|a011383a直接调用a01109d6(C,Q)，Q+0写生成id，Q+0x1c/+0x20为容量/payload，method=_otc.info。0a14未知使JSON id参数来源不闭；params和C+0x2390通知止API，栈{writer,C}是否留存未知。返回仅0/−1；本函数不free借用Q/payload，不是异步reply callback。|
|周期请求|a01137f6的Q清40B、payload0x558，成功serializer后仅日志使用token/bindkey替换结果并在提交前归还。真正请求a011f9da(E,Q,a0112260,E,load32(E+0x1104),0)；随后payload归还/清槽。申请或serializer失败仍到a01137d6(C)；其返回0才schedule(a0110894,5000,C)。固定返回1800000不等成功调度/云接受。|
|pull请求|a0110aca从E−0x968取id，清Q中id之后36B，构造_otc.pull_ip_list、params空数组；序列化成功才以callback=a01102d8、user=E、timeout=E+0x1104提交。提交任意返回及序列化失败均归还payload，分配失败不提交；所有本地出口返回load32(E+0x110c)。|

必要旧证据只核主仓 `evidence/rea-0041-20261017/evidence/upper-miio-b.md` 的a01106f2、a0110788、a0111420三卡，Evidence IDs分别为 `ev_3b006d151d60a4c0666a982a7b583c03eb17cb2a375bf8bdedba72ac6bdc9884`、`ev_fed264e8febd84155f55a3ea96b02d2f198fbc22194ca0bf56d1850b312f38df`、`ev_715f044e905ca51fde778ab4788da1775244f18bf1a3c47f5513b8840ace9a25`。dyna_params只有变化才写ctx+0x110c并以ctx重排pull；此ctx对应E，乘1000和范围/溢出限制照旧继承。SDK沿F11/F12/Q24已验接口：正常正长度payload同步复制，callback/user仅浅复制；提交0不保证传输/消费，故临时payload可归还不等E/C/X寿命已闭。

## 显式断边

7个未知字原样保留（地址均0xa011前缀）：2e78=`0b475981`、3154=`0bc64c58`、322a=`0bc57c45`、2ad0=`7717c7c0`、2b0e=`7715e5c0`、27bc=`0b50ea4a`、0a14=`0b46e95a`。a01129be只29be..2b11与2b1e..2b5d计body；2b12..2b1d的12B `771925c31305803e33052503`只核原字，不解码、不补NOP、不计body。原字一致不等未知ISA已认证。

保留：事件生产者/数字意义、完整OTA时间表达式、syncfixedip字段来源、框架同步通知留存、owner/child全生命周期、SDK callback排队与取消并发、真实timer/溢出、云端接收/设备动作未知。a010d8ca等框架、JSON/分配器/格式化器、网络/OTA下层及SDK均止已验API。未执行固件/模型/SIM/QEMU/回放/构建/设备/外网，无安全异常实验，无模型/ROM/生产配置变更，无下级代理。

## 计时与交付

第一工具UTC：2026-10-24 18:27:51。技术完成UTC：2026-10-24 18:28:45，54秒墙钟；材料已定位且批量静态检查，早于预测4–6分钟即交付，不等待凑时。没有独立排队/中断/有效计算工时或token计量，不造数。提交完成和停止UTC由交付消息独立给出。

静态验证通过；提交前另核git diff --check及精确三文件范围。本轮不生成ignored中间产物；作者ignored原字仍由父窗按原清单转存。本树只提交本报告、verify.py、review.json，不推送。
