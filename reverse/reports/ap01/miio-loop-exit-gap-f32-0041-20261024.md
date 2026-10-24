# F32：同M的loop退出绑定与Q归还caller盘点

**旧留存足以连接同M配置的退出回调：worker经L.vtable+4调用a011e0ac(L,L)，它再从L+0x40取得a0110788，以(L,M+0xe8)调用，正常回来强制返回0。** L+0x44=a010f984是另一回调角色，不能按相邻偏移命名stop。另找到同L交generic归还接口a011fd3c的真实caller，但所见路径是线程创建返回非零后的分支，不是实际quit/线程结束的证明。

2026-10-24；F11/12，F32，`/root/a56`；独占`re0041-f32` / `codex/re-0041-f32`，基线`bd457a6`。采用REA留存优先流程，本阶段只读旧完整留存/机器合同/metadata及必要较晚报告，ROM新读取0B。没有新callback/close/调度body、原件/模型/target执行、构建、SIM/QEMU、回放、输入/设备/外部服务或旧脚本运行；不切换共享REA、不改生产/主树/共享表，无下级agent、提交推送。

## 继承与有限查重

|已有出处|已有行为与本次精确差集|
|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[upper-layer](upper-layer-0041-20261017.md)|旧upper各专项根与本地合同已存在；不把业务/SIM验收当native退出/队列排空证明|
|[F15](miio-queue-size-gap-f15-0041-20261024.md)/[F16](miio-queue-size-review-f16-0041-20261024.md)|同M，L=M+0x128、Q输出槽M+0x140=L+0x18、user=M+0xe8；16B配置至L+0x3c，thread/vtable/start与ctx身份桥直接继承，不重验start、size/mode或typed dispatch|
|旧`evidence/rea-0041-20261017/evidence/upper-miio-b.md/.json`|a011e3d6 generic worker退出、a011e0ac适配器、a0110788局部生命周期调用及a010f984另一角色已有合同。**generic退出行为直接引用，不重恢复**；本次只把同M实际配置/参数接入|
|旧`evidence/rea-0041-20261017/evidence/upper-routing.md/.json`|a011fd3c已有group-unregister-and-invocation-drain合同：条件等待/注销、queue归还和sync-list处理、caller-owned group不在本体free。该generic角色不是新发现；本次仅绑定同L caller与其Q实参|
|[F03/F04](miio-loop-close-review-f04-0041-20261023.md)|另一个栈loop及timer条件close/pending链已经解释。其+0x18和本native Q偏移相同也不合并对象，更不据其退出合同认本L实际关闭|

有限搜索查主仓reports近期精确a011e0ac/a0110788/a010f984/a011fd3c及F15引用，再查旧upper-miio-b与upper-routing。没有新同实例退出绑定报告命中只表示这些词项/载体的结果，不是全历史不存在；旧generic合同有命中后即复用，不重复恢复完整退出系统。

## 复核与纠正

本次无旧语义纠正。旧generic的“stop/queue destroy”是旧合同中的角色描述，下面以实际地址/字段说明同实例接线，不能从角色名推物理资源效果、queued I排空或最终free。

旧主来源`evidence/rea-0041-20261017/evidence/upper-complete.evidence.json`：

|record/EID|本题必要旧字段|
|---|---|
|248，`ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`|master配置表、vtable第二槽/user、thread参数与失败归还caller|
|195，`ev_9a7e0a186c4ed2b341b4d42187fcb73bebec13d401cd226033d30027d121387d`|worker持L于s1、finish处vtable+4的真实取槽/两参调用|
|309，`ev_f7edb78f19e658d59333a033352ac0d773b5a624c66ecd33e8c823a7d5278ccd`|a011e0ac从第二参读+40/+48，间接调用及强制返回0|
|77，`ev_339445ec35b31491f695197f3dd123d01e24a74489ccc10fde6b5e3f8e1a86c6`|a011fd3c入口L+18、保存L、归还界面前重读L+18和清槽；其generic合同已在upper-routing|

上述原assembly profile均为`4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，language沿旧`RISCV:LE:32:ap01thead2`，不是本轮新REA生产。upper-miio-b局部合同另有profile `04b34bbb41e8ff5d0cbbc2c7471d390693c40fe70f2e21519e2b21d268c9237d`，不混同：worker EID `ev_d6ca150724daa7644ed5506256c6a95b1a2139c22f4d49cf6923fd6bf288bbea`，adapter `ev_9a6f1939371027a133a36f527343d421d82247d825be42acd324c72a304de0f8`，a0110788 `ev_fed264e8febd84155f55a3ea96b02d2f198fbc22194ca0bf56d1850b312f38df`。本题不重新认证旧provider/模型或所有指令语义。

0041原件身份沿F15：6,769,704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射offset=VA−0x9ffff000；仅继承，不新读ROM/重算hash。[check.py](../../analysis/miio-loop-exit-gap-f32-0041-20261024/check.py)只读上述旧JSON和合同，**45项必要留存定位/对象换算PASS**；不是运行作者/历史技术脚本或新的原字节技术复核。结果`evidence.json`忽略留本地原路径，不复制大Evidence。

## 真正新增：同实例绑定及caller边界

|实际旧锚点|同M连接与限定|
|---|---|
|master a00653b8..53d8及F15已验copy|配置第二word=a0110788，第三word=a010f984，第四=user=M+e8。L+3c表起点使它们分别成为L+40/+44/+48；不是按offset猜stop|
|a00653ec/53f0/53f4/53fe|vtable位于M+158=L+30，第二槽M+15c保存a011e0ac、user槽M+160保存同L；L+10指该vtable的安装关系沿F15继承|
|worker a011e436..448|重新取vtable=word(L+10)、fn=word(vtable+4)，非零才以a0=L、a1=word(vtable+8)=L间接调用。这个时点是generic worker finish，不表示此前正常循环/业务quit必已发生|
|adapter a011e0ac/e0b8/e0ba/e0bc|第二参实际也是L；读取其+40回调和+48 user，再调用**a0110788(L,M+e8)**。这里两层间接调用不能压成未经证明的直接边，字段稳定及normal ABI前提保留|
|adapter e0c2/e0c8与worker e44a|有回调正常返回后a0置0；空回调同样返回0。worker再把该a0存s2。因此0来自适配器折叠，不能证明所有下层注销/停止成功|
|a0110788旧局部合同|复用已有服务调用序列，输入是parent=L、owner=user；owner+8c=M+174、owner+880=M+968恰为既验两个ctx。下层a01ab368/462/634等效果仍沿旧边界，不读正文、不把这些调用等同ctx/free完成|
|L+44=a010f984|旧合同为external RPC receive forwarding，使用user−e8定位M。所选worker退出读取的是vtable+4再L+40，并未以L+44取stop；不能因第三word挨着第二word就并入退出归还链|
|master a006556a/5578/557c|线程创建调用显式传同L=s7；返回**0跳55da**。所见非零返回走错误处理一侧，随后可达55b8；不恢复线程创建body或全部master分支|
|a00655b8/55ba|以a0=s7=同L调用a011fd3c，之后55be回旧4fa2。继承s7/正常callee保存前提；这是真实同L归还caller，但只认证**所见线程创建非零路径**，不是实际运行退出的接线|
|旧a011fd3c/fd52/fdc6/fdd0/fdd4|入口先检查word(L+18)，保存L后，旧归还点**重新读取**a0=word(L+18)交a01b3c64，正常返回后清L+18。Q身份依该槽仍持有本次Q；不能从初始Q指针推出后续槽无writer，也不把a01b3c64界面升级为已读close body|

新增范围仅为**已有generic角色与同M配置、两层退出callback实参、所见失败路径同L/Q归还caller的连接**；ROM/新body0、新业务功能0。没有重做正常start、dispatch、size/mode或generic drain算法。最小合同见[contract.json](../../analysis/miio-loop-exit-gap-f32-0041-20261024/contract.json)。

角色与生命周期分开：L是M内嵌对象，vtable也是M内字段，不因generic退出叫group而变成另一分配根；Q是L+18所持native queue，和F11栈descriptor别名Q无关。旧generic有条件循环/归还界面，不证明这次实际服务已完成、queued I对象或其深层资源已归还，更不证明M/L最终free。worker的finished flag与实际归还caller之间没有在本题获得“运行后必调用”的时序闭包。

## 精确未闭与后继

未知实际quit触发、正常运行后哪个caller在何种同步条件调用a011fd3c、stop下层完成、Q归还真实资源效果、queued I排空/深层资源责任、后续字段writer/并发、最终M/L存储归还。不能把线程创建失败清理路径当正常线程退出成功；不能以adapter0证明下层全部成功。

本阶段无需新ROM即可回答绑定与归还caller身份，故不请求新callee窗口。若以后要升级归还效果，精确边是**旧fdd0→a01b3c64(a0=重读L+18)**，应先查更晚合同/metadata并登记正常接口所需字段；若问真实quit，则要另有**正常运行后的具体caller→a011fd3c(sameL)**种子，当前所见失败caller不能替代。两者均不自动授权展开全调度/queue-close或推最终free。

实际检查45项PASS、JSON解析、主仓后备链接、独占status、证据忽略与`git diff --check`通过；仅本报告与同名analysis新文件，原件/共享表未改，未提交推送。交付后停止供主窗复核/补位。
