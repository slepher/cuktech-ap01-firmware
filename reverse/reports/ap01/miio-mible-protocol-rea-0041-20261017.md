# 0041 miio_client / mible协议逆向：REA续作

2026-10-17。参考roth-m/miioclient-mqtt固定提交`063f5d121f8e5b0421ad256dc0b3c9d6934d3426`，由父代理独占本机REA6.5.0/Ghidra12.1.4会话，GPT-6.1 Sol子代理分别核对RPC表和蓝牙协议。仅离线分析，不运行下载程序、不访问设备或真实账号，不修改ROM/Bridge/SIM。

原件SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，base`0x9ffff000`、entry`0xa0000000`，REA profile `958b301907fe9bfcbbf58f56c40ca89e93ea3d974184b719c8b172f60709c6f3`。复用已正确绑定会话，没有重开原件或改用外部提供方。本轮归档含30项REA函数记录，其中2项为先前保留的UI记录、28项为本轮新记录。导出的unknowns数组为空仅表示工具账本未注册未知项，绝不表示协议已全解。

## 1. 原厂命令目录

原件`0xa066d808..0xa066df10`存在连续1800 B、90条、每条20 B的描述表，布局为短名称指针、完整名称指针、处理函数指针、辅助名称指针/零、原始flags。各指针和字符串由原件读回核对，REA注册函数的`index*0x14`提供独立步长证据。

| 前缀 | 条目数 | 已恢复程度 |
| --- | ---: | --- |
| cmd. | 49 | 名称、函数关联和静态记录；全部运行可达性未证明 |
| cmdrpc. | 13 | 含属性读取/写入、动作及版本变体；选定属性处理路径部分恢复 |
| miIO. | 25 | 有对应组注册证据；包含info、OTA等处理器 |
| ota. | 1 | downgrade记录；不代表允许绕过安装限制 |
| user. | 2 | 静态记录及对应组注册 |

`0xa01ab298`包装`0xa01202e4`进行注册。注册表使用锁，按组名和组类型低3位拒绝重复，再追加链表。组类型与每条描述的尾部flags是不同字段；flags观察值0/2/3的完整权限含义未恢复。**90条描述不是90个已经证明能从LAN调用的API**；cmd可能是内部命令层，不能把表名直接拼成网络请求就宣称可用。

## 2. localhost消息与真实回执

`0xa01b82e8`接收流并解析JSON边界，读取method后将local.消息交给`0xa01b6a84`，其他上报进入`0xa01b6146`。本轮确认10项本地分派名称，另有local.info回包名称：

| 分派名称 | 已观察的用途/边界 |
| --- | --- |
| local.prep_suspend | 进入专门处理器；完整休眠合同未核清 |
| local.query_status | 要求可提取的id，构造local.status并使用当前状态；不是固定在线 |
| local.query_time | 回包local.time、保留原请求id，时间数值来自原厂helper |
| local.ble.config_router | 解析配网输入并返回成功或错误；并非任意HTTP接口 |
| local.query_country | 地区查询分支 |
| local.query_did | 设备身份查询分支 |
| local.query_info | 构造local.info；涉及位置/型号等字段，未核定完整合同 |
| local.ble.scan_recovery_triggered | 蓝牙扫描恢复通知路径 |
| local.req_auto_add_confirm_message | 自动添加确认相关；含状态/参数检查及签名路径 |
| local.query_log_enc_key | 日志加密材料协商；random/derive_key相关路径，密钥协议未完整恢复 |

网络侧状态表示有6个值：0=device_init，1=wifi_ap_mode，2=sta_mode，3=cloud_trying，4/5=cloud_connected。`query_status`在额外条件满足时可回复bind_success。该6值表示与蓝牙接收的11值OT状态不能直接互换。

上报路径`0xa01b6146`要求状态helper返回值大于2才进入转发，因此cloud_trying也能进入，不等于云端已收到或执行成功。存在整数id时，每项待回执记录申请32 B，保存id、时间helper值、回调、原fd和next。`0xa01977cc`按id匹配、摘链、调用存储回调并释放记录；找不到返回-1。无可提取id的上报另走无待回执记录路径，不能把它与查询类必须带id混同。超时期限与完整过期回调链尚未恢复。

关键REA Evidence：上报`ev_6627acfe805089cd29c29531a68de77faf5428c5d675d4a2a4e7415a1126cc41`；id读取`ev_8ed313c8d7458ce47ed160bc7cae2a069e0828cf8f5eee84f408add3301160d4`；匹配/释放`ev_27416ce2005ee739c75846d55757bb0e72e7b969b2cd8911d502489b5ffdc574`。

`miIO.ota`处理器的来源位检查明确拒绝local-origin，另核params/忙态并输出结构化错误。保留localhost服务不能直接获得原厂OTA调用权限；本轮不修改这项检查，也不改先前用户要求的unsigned包分支离线候选。

## 3. 蓝牙命令包装与参数

命令分派器`0xa0129f0c`读取根对象中的params，再读取params.cmd进行匹配，调用已注册处理器；六个处理器进一步查找params.aug。因此已恢复的**内部包装形状**为：

```json
{"params":{"cmd":"ble_scan","aug":{"on":1}}}
```

这是解析层结构示意，不是经验证可发送的完整RPC请求。外层method、来源/权限、序号及帧封装仍需继续核实。

| 命令 | 参数/分支 | 处理器 |
| --- | --- | --- |
| ble_config | aug.pid、ver；ver10000表示沿用当前版本，超过9999拒绝；配置相同可直接返回 | 0xa012a44c |
| ble_restore | 蓝牙状态恢复，条件满足时删除event_rule/CRC、pair/unpair时间等键；不等同于AP01整机复位 | 0xa0125d66 |
| ble_deinit | 调用蓝牙相关清理接口；并未证明完整卸载所有后台任务 | 0xa0125d04 |
| ble_event | aug.act分支1清外设数据库、2按mac/objid移除、3用mac/objid/pid/beaconkey新增或更新 | 0xa012a6fe |
| ble_fastpair | aug.mac、objid、pid、permit；permit按非零转布尔；记录超过10项时有裁减路径 | 0xa012abfa |
| ble_scan | aug.on数值0/1控制扫描；其他值拒绝，后续投递事件并保存开关值 | 0xa012a29e |

六项均有本轮REA Evidence，详见蓝牙JSON。注意：参数读入到8/16位字段不代表原厂严格检查8/16位范围；MAC/beaconkey经过字符串提取及逐字节十六进制转换，不把它描述为已证明有完整长度/字符合法性检查。多个处理器找不到aug时返回0，也不能将其解释为实际完成配置。

## 4. FE95和OT通知状态

FE95服务下恢复出六项48 B特征记录。记录UUID为`0x0001/0x0002/0x0004/0x0005/0x0010/0x0019`；`+0x1c`原始字节依次`0x0c/0x02/0x10/0x14/0x04/0x2e`，`+0x14`原始字段为24/2/2/24/20/20。属性/长度的常规解释属于推断，完整结构尚未核定。特征句柄在运行时注册后产生，不能从静态表伪造；每项认证/配网载荷含义尚需继续核清。

`ot_state_callback`(`0xa012a036`)从params读取状态文本，写入另一套11值状态：

| 值 | 文本 |
| ---: | --- |
| 0 | device_init |
| 1 | didkey_req1 |
| 2 | didkey_req2 |
| 3 | didkey_done |
| 4 | token_done |
| 5 | wifi_ap_mode |
| 6 | sta_mode |
| 7 | cloud_trying |
| 8 | cloud_connected或bind_success |
| 9 | cloud_retry |
| 10 | prov_timeout |

这是文本到枚举的映射，不是证明所有状态必然按表顺序发生的完整状态转移图。无消息的计数分支也会写7，错误/未知params返回-1。认证/配网仍有协议opcode、计时器、断开清理等分支待恢复；此结果不证明标准蓝牙SMP/链路加密可用。

在worker的事件`0x100`路径进一步定位到以下opcode分支。值来自接收数据的低8位，不是GATT UUID或JSON方法编号；仅列已观察动作，不补猜完整认证协议：

| opcode | 分支地址 | 已观察动作 |
| --- | --- | --- |
| 0x15 | 0xa012d1b6 | 连接子状态符合条件时，将句柄/载荷/长度转交0xa012dc54 |
| 0xa2 | 0xa012d1f4 | 生成28 B设备信息应答；完整字段布局未恢复 |
| 0xa4 | 0xa012d2ee | 调用空载荷transfer operation3；reset/cancel语义仍为推断 |
| 0xa6 | 0xa012d32a | 日志加密密钥请求；失败路径发送0xe5 |
| 0xa7 | 0xa012d154 | 清25 B缓冲，安排operation2/type0x12及回调0xa012db24 |

## 5. 参考项目能帮助什么

RothM的socket/select与本地JSON分派适合解释兼容接口和构造离线测试输入。但它的固定id12345、固定cloud_connected及简化ok回复，不适合代替这里的实际状态、身份来源及请求回执。其ARM Linux可执行文件不能在AP01 RV32/NuttX直接运行；协议兼容也不证明官方源码血缘。

目前可以据此定义本地适配层和更真实的模拟输入，不能据此宣称已完整重建两套原厂SDK、已脱离米家或可安全停用原任务。本轮未增加App功能或重新构建SIM，之前的SIM回归报告不作为原厂私有协议运行验收。

## 6. 产物、限制与后续缺口

- [原厂90项命令表/注册与回执分析](../../artifacts/ap01-research/rehost-20261016/miio-rpc-rea-0041.json)
- [本地消息目录/6值状态](../../artifacts/ap01-research/rehost-20261016/local-rpc-rea-0041.json)
- [蓝牙包装/参数/特征/11值状态](../../artifacts/ap01-research/rehost-20261016/mible-protocol-rea-0041.json)
- [30项真实REA函数证据](../../artifacts/ap01-research/rehost-20261016/miio-mible-rea-0041.evidence.json)
- [输入/输出指纹清单](../../artifacts/ap01-research/rehost-20261016/miio-mible-rea-manifest-0041.json)

REA使用通用RV32/RVC模型，存在厂商扩展指令未解码、RAM初始化未建模及内存函数被误标no-return的限制。部分函数伪代码只剩清零调用，而Listing仍包含后续指令；本轮分别记录REA观察和原件字节/Capstone辅助证据，不把线性指令猜测当完整控制流证明。Ghidra字符串对象可能显示共享后缀的较长字符串；参数键按原件精确地址读回，而非照抄显示名称。

仍缺：完整认证/密钥交换及帧序列、每条GATT特征的数据合同、所有RPC来源/权限规则、待回执过期策略、属性/动作全部设备参数映射、断开/异常清理的完整生命周期。后续优先将蓝牙外层路由和认证/配网opcode与本轮表项逐条关联，再分析网络配网/重连和OTA服务可拆分边界。未执行这些路径或读取真实设备凭据。
