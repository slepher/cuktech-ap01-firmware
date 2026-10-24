# A81：format copy的n1有限域非作者复核

**限定接受A80的n1合同，语义纠正0、新增业务0。** 给定正常有效、适当分离且无干扰的源1B/目的1B，实际分支只在原src读一个普通byte，再在原dst写该byte，返回原dst。该有限路径不经过alignment门，不要求word对齐或额外可读padding，没有callee/栈或直接参数地址持有。其余长度、完整格式输出和资源寿命继续未闭。

2026-10-24；J08/14，非作者`/root/a56`，A80作者`/root/f12`已停止；独占`review-close-a81` / `codex/re-0041-a81-review`，固定基线`bd457a6`。按主仓最新reverse-design、analysis README和管理顶部“限定复核并关闭”执行，采用REA留存优先流程。只完成此复核，不接后继、不补位/创建下级agent。不运行作者locate.py/verify_n1.py、旧脚本、模型、目标、host输入、固件、SIM/QEMU、构建、回放、IO/设备或外部服务；不切共享REA，不改生产/ROM/配置/主树/共享表，不提交推送。

## 继承

|出处|本次处理与界限|
|---|---|
|[A80报告](reader-driver-format-copy-gap-a80-0041-20261024.md)、locate/verify_n1源码、contract及两份JSON|全部只读审阅，没有运行或导入作者脚本。本复核仅其已交付n1差集，不验收报告中的其他长度种子|
|[F17](miio-queue-copy4-f17-0041-20261024.md)/[F18](miio-queue-copy4-review-f18-0041-20261024.md)|既验入口`[589c,58ae)`与末尾`[590e,5918)`的普通字段/原dst返回直接继承，只读主仓F18 evidence.json必要行。n4接受域本身不扩大|
|旧upper-complete record76|路径`evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/76`，EID `ev_32725e49dc86c4d072d48e396f5c14986a521284bea8c8ff59cd533fc995a848`，profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；仅读必要入口/末尾assembly，不导出1080B或读别的branch body|
|[A78/A79](reader-driver-format-stream-review-a79-0041-20261024.md)|b512实际copy实参和stream夹取/有效域沿已验调用端，不重验S/engine；n1 helper不能代证caller存储有效或整个输出|

原件主仓`roms/0041/ap01-1.0.2_0041.bin`实查长度6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算摘要；offset=VA−0x9ffff000。旧profile/language沿原记录，不新造REA生产ID或认证源版本。

## 复核与纠正

[review.py](../../analysis/reader-driver-format-copy-review-a81-0041-20261024/review.py)以标准库独立拆位，**24项PASS**。新原件读取仅`[a00058ae,a00058c6)`24B/8位置，另从F18/record76取必要旧端点行；不新读端点ROM，不调用Capstone或任何模型/作者解码器。四个B型的opcode/funct3/寄存器/目标、三个C.LI、一个C.MV独立核验，并从已接受F18 raw独立再核末LBU/SB的width/base/offset。没有未知指令/NOP替换或手填边界。

|锚点|接受内容|
|---|---|
|继承589c..58aa|a5=7，保存dst于a6；n=1不取unsigned 7<n；a4=4，n4相等门不取。计算寄存器不改a0|
|58ae|unsigned BLTU a4,a2→58c8；给定n1不取4<n|
|58b2/58b4|a5=2；BEQ a2,a5→5920不取|
|58b8/58ba/58bc|a4=3；**a5=原a0(dst)**；BEQ n,3→58fe不取。CMV写a5而非改a0|
|58c0/58c2|a4=1；BEQ n,1的独立signed目标解为**590e**，本域取此边|
|继承590e|原字03c70500，I-format LBU a4,0(a1)，只在原src读1B。所选路没有先移动或向下对齐src|
|继承5912|原字2380e700，S-format SB a4,0(a5)，只在原dst写低byte。不是word store，也不追加NUL|
|继承5916|原字8280，RET；所选入口/dispatcher/端点均不改a0，无调用、栈或指针持久发布，返回原dst|

未发现A80语义错误。此路径只需所述1B读写足迹，故“无需额外padding/word对齐”来自实际byte路径与未走alignment门，而不是把n4既验域概括成全部非对齐算法。参数地址无直接持有，是这条无callee有限路径的事实；复制的数据byte本身不转移任何被指对象所有权。即使helper返回后不再读源，也不能据此推整个formatter/engine不保留其他指针。

## 真正新增

复核新增业务0、新字节语义0、ISA/来源认证0；仅对A80 n1差集提供非作者独立检查及限定接受。最小合同见[contract.json](../../analysis/reader-driver-format-copy-review-a81-0041-20261024/contract.json)。生成`review-evidence.json`保留24B字段及旧端点引用，忽略留本地原analysis路径。

给定n1及有效分离/无干扰前提，数据合同是`U8(original_dst)=U8(original_src)`的先读后写、a0返回original_dst；不需要执行目标、host替代函数或枚举输入来建立这个静态有限路径。没有研究任意重叠、原子性、所有caller或完整1080B算法。

## 精确未闭及关闭范围

n2..7其他短路、n8..255对齐/word拼接/额外访问足迹仍未闭；本复核没有读取这些新body，也不认证A80种子中的厂商bulk语义。实际source/dst有效性/分离/容量不能由caller表达式不同推得；实际输出、engine调用/计数/终止/截断、全库生命周期仍按原断边保留。

本次可关闭的是**A80限定n1交付的待复核状态**，由管理窗口整合维护；不能关闭广copy域或格式输出功能边。本人完成后停止，不提出或承接新逆向任务，不接先前未闭种子。

实际检查24项PASS、JSON解析、报告本地/主仓后备引用、独占status、证据原路径忽略保留和`git diff --check`通过。无生产修改、提交或推送；供主窗整合清理并关闭本项待复核状态。
