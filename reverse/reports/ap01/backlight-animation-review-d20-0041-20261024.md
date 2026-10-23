# D20：亮度提交动画合同独立复核

接受 D19：正常提交启动96B descriptor 描述的 UI 数值动画，单周期2000、无限 repeat；target 为 `*(ctx+0x10)`，exec=`a00f43bc`、path=`a00f4378`，completed/deleted 槽均0。正常结束编辑的原序是处理 timer 槽、按同一 target/exec 查询并删除动画、最后对同一 target 写0。没有技术纠正，新增功能0。周期沿既有 UI 毫秒语境表述为2000ms，不以静态分析宣称测得真实墙钟时长。

基线 `df35f44f0292b3bfafdfe8f12f0bb77d80926a0e`，独立树 `re0041-d20`、分支 `codex/re-0041-d20`。使用 reverse-engineer-anything 技能，未参与D19生产。只读主仓ROM与留存证据，没有新开或切换共享REA target、执行固件/模型/SIM/构建/历史回放、连接设备或外网，没有创建下级agent。仅写本报告及独占analysis，不改主树共享文件、生产ROM、配置或模型，不撤销他人修改。伪代码/字段名为恢复表达，不认证上游typedef。

## 继承结论：已有 → 行为 → 局限 → 精确缺口

|既有出处|行为与证据局限|本轮处理|
|---|---|---|
|[D19](backlight-animation-d19-0041-20261024.md)及其 instruction-windows.json、review-result.json|已解释descriptor、target、回调、无限repeat与局部清理；全页析构未闭|19个已有小窗口只与原件比较，不另存重复窗口、不重新导函数|
|[背光第二轮](buzzer-backlight-round2-0041-20261023.md)、[第三轮](buzzer-backlight-round3-0041-20261023.md)|timer+0xc取ctx、ctx+8c提交亮度；首次操作创建2000 timer、repeat=1且已有timer不重启；背光/PWM已有|直接继承。提交timer的一次repeat与动画无限repeat不得混用|
|主仓 `reverse/rehost/settings-0041-round2b.json records[10]`，Evidence `ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb`；round2c/system-complete复用链|正常结束编辑状态与动画清理接线早已保存，不能列为D19/D20新功能|本轮只查指定record及两条原调用，继承页面context连接，不重导大函数|
|主仓 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-125.json structuredContent`，Evidence `ev_65a0d85b67cba9945c5911cf445f9f17d9f0ca6f766b502580109ef15b078c4a`|已有 `a00f43d4` 原序，入参timer、s1=timer+0xc、复制后初始化再start|继承已有反编译，必要字段/调用以原件独立复核；不把初始复制内容当保留userdata|
|D19所列complete、page-logic、设置页与旧服务/SIM复用结果|旧业务主体已覆盖；宿主服务不能认证ROM节点/ctx所有权|继承限界，不重新解包最终ZIP或复扫完整页面|

实际缺口只为D19局部ABI/寿命主张的独立接受与证据强度，不扩成完整动画引擎或完整离页析构恢复。

## 本轮复核或纠正

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，VA映射 `VA-0x9ffff000`。下表原字节均来自D19可定位小窗口，本轮逐byte比较原件，并另行解码store位域/调用立即数；不重复输出全窗口。结果见 [static-review.json](../../analysis/backlight-animation-review-d20-0041-20261024/static-review.json)。

|主张|独立复核依据|结论|
|---|---|---|
|96B descriptor，初始化覆盖初始复制|`441e:13060006` 的长度96；`4432` JAL→`a008df3c`，`df4c`→`a0080d8e`，`0d9a`→`a0024906`。旧窗口确认a2=96、a1=0。初始化默认值随后覆盖，最后才写本入口字段|接受；初始ctx+24复制不能用于证明有效ctx userdata|
|target、exec、path真实槽|`4426:03a90401` 读 `s1+10` 至s2；descriptor基址 `s0-70`，独立S型立即数确认 `445a:232824f9`→+00、`4452:232af4f8`→+04、`4446:2328f4fa`→+20；前置常数分别构造a00f43bc/a00f4378|接受target是对象指针，不是ctx；path不是ready/completed|
|2000、起终值与repeat|`4436:9307007d`=2000写+30；+24=0、+28=80000000、+2c=510；`4462:7d59`令s2=-1，`4474:232a24fd`独立确认写+44|接受2000单周期、-1无限repeat；与timer repeat=1独立|
|完成/删除回调0|96B清零后，init默认及本入口所有覆写均未写+10/+14；完成路径 `c1f4/c1fc` 分别读取这两槽，显式删除只在 `ac20` 取+14|接受两个通知均不调用；不能据此推导ctx/target已被释放|
|节点副本与即时调用|start `bfe6` 长度96，从栈descriptor复制入节点；early apply按旧窗口+5c bit4；`c044..54` 先 `path(node)`，再 `exec(node->target,value)`，tick `c194..1b2` 同ABI|接受独立节点持有副本，栈descriptor退出即结束；start返回node在此未保存，无调用者指针持久保留|
|path和exec数值|path经 `4390`→`a008a73a` 的signed整数map；乘法、算术右移10、有符号>255后510-value。`43c4:93f5f50f` 保留低byte；`43c8`→`a018fb3c`，再以property3e/selector20000调用通用setter|接受量化三角形0→约255→0；不替换正弦，不认证具体控件属性或PWM|
|repeat消费|`c0a2:fd59`令s3=-1；`c232:63063701`相等跳过递减；随后重新读+44，非0重置+34活动时间。+3c/+40本实例均0|接受正常重复没有2000后有限完成；通用completed分支存在不代表本实例执行它|
|正常结束编辑原序|旧settings record确认；`feb8c` unsigned比较1999与tick差，大于时跳过timer删除，`feb98`清ctx+84；`feb9c`取ctx+10；`febaa`查询，非空 `febb6`删除，`febc0`值0调用|接受条件取消→清槽→查询/条件删除→target写0，不能改为无条件删除timer|
|显式删除对象身份与清理|查询比较节点+00 target、+04 exec；delete同一pair。`a01b2ef8/fc` AUIPC/JALR独立解出 `a008ac06`；该callee先摘链，+14可选通知，再 `ac2a`→`a008ab8a(node)`，不调用+10|接受释放动画节点；本例+14=0，不释放UI target/ctx、不调用业务ready|
|厂商字限界|查询遍历 `a00891b2:8bc7e740` 与原件一致，仍未知；普通比较和真实删除匹配提供局部身份交叉证据|接受D19局限，不将这次稀疏核验宣称完整链表算法/厂商ISA认证|

正常必要伪代码（非原源码）：初始化96B局部descriptor；写 `target=*(ctx+10), exec=a00f43bc, path=a00f4378, start=0, end=510, duration=2000, repeat=-1`；start复制为节点。到期经path计算数值、exec更新target，再按无限repeat重置活动时间。结束编辑时先按既有条件取消timer并清槽；若查询到 `(target,exec)` 节点则删除；最后设置该target值0。调用顺序、条件及节点/target/ctx身份保持分开。

## 真正新增

新增功能0、ISA规则0、完整函数导出0、整库来源排除0。19个旧窗口对原件、8个descriptor store偏移、12个直接/成对调用目标、17条稀疏指令的复核都是既有结论验证。没有新恢复timer/背光驱动、设置页业务或完整动画引擎；无技术纠正。

## 精确未闭与一个后继闭包

仍未知：所有正常离页/页面DELETE是否经过该结束编辑分支，target与ctx完整创建/销毁所有者，timer到期后其他槽管理路径；本轮没有无种子扫描这些范围。`a00891b2`厂商遍历字、动画userdata +1c原typedef、property3e/selector20000确切上游符号名均未认证。静态原序不证明运行时帧率或真实墙钟时长。

一个有正常路径种子的后继建议：仅沿已定位 `a00f43bc→a018fb3c→a00df94c(target,0x3e,value,0x20000)` 认证具体property/selector含义，回答动画实际UI效果。已筛当前reports，只有D19保留这项命名断边；charge/guide/system/settings2b/weather complete中的同地址命中是通用setter调用及既有清理，不提供本属性符号认证。建议精确比对已有本地LVGL候选定义，不扩通用style算法、所有页面或ctx free。本轮不自行接题。

实际运行 [verify.py](../../analysis/backlight-animation-review-d20-0041-20261024/verify.py) 通过；上述19窗口、8字段偏移、12调用目标、17稀疏指令及旧settings record校验通过。没有调用固件、分析器模型或历史输入。报告相对链接与 `git diff --cached --check` 通过；结论仅接受D19局部正常合同，完整页面/ctx寿命保持未闭。
