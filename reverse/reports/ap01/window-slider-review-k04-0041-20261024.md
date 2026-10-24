# K04：K01/K03 事件状态、class 安装及对象引用独立复核

2026-10-24；基线 `0d8027f`；独占树/分支 `re0041-k04` / `codex/re-0041-k04`。**限定接受 K03 的实际增量，无实质语义纠正，新增功能0。** 祖先 class 状态来自回调后重新读取的事件 flags bit0；class+c 确指向 K01，真实创建结果与全局槽的连接成立。count/索引不变量、唯一 owner 和实际事件时序没有因本次复核获得认证。

采用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。复核者未参与 K03 生产；直接只读主仓 ROM，未运行或导入 K03/K01 验证器，没有把其 evidence.json 当作原件。用户明确恢复覆盖历史停止条款，其他共同限制保留。未打开/切换共享 REA target/database，未运行固件、SIM、模型、构建、历史回放、输入实验、设备或外部服务；未修改生产代码、ROM、配置、分析器模型或他人文件，无下级 agent。

## 继承结论

|既有出处|继承内容|本轮界限|
|---|---|---|
|[K01](window-slider-entry-k01-0041-20261024.md)、[K03](window-slider-contract-k03-0041-20261024.md)|入口 a00a4cac、三 callee、事件/索引接入及待复核增量|以 K03 为待审主张，必要位置直接重新读取原件；旧地址/extent不计新增|
|[H03](weather-page-close-h03-0041-20261023.md)、[H04独立复核](weather-page-close-review-h04-0041-20261023.md)|事件 current@0、target@4、code@8、userdata@c、param@10、previous@14、flags8@18；class双参、descriptor单参；key getter要求原code恰11h和非空param；公共删除的分层责任|可靠旧合同直接继承，不重导事件库、getter或完整删除/析构链|
|[J04](factory-reuse-gap-j04-0041-20261024.md)、K01所引旧036/043/047|factory slider 与日常窗口组件不同；当前索引+38、count wrapper、既有setter内部行为及完整旧body已留存|不重做三callee，不把目录名与GPIO FactoryTestMode连接|
|旧 `whole-rom-private-20261023-068.json`，`ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`|dispatcher已含创建和全局保存种子|只查询 structuredContent.normalized_result.assembly 的必要寄存器/调用位置，原字另外读取；不复制/重导dispatcher|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、J04/K01的有界复用结论|SIM/照片/替代服务已有明确范围|passed-in-sim不证明ROM ABI/真实设备效果；不重复最终ZIP/全矩阵或据无标题判缺失|

旧忽略证据只读根为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/`。本轮不产生新 REA Evidence ID，也不认证精确 LVGL 来源版本。

## 本轮复核或纠正

独立 [review.py](../../analysis/window-slider-review-k04-0041-20261024/review.py) 直接读取 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−0x9ffff000`。采用 Capstone 5.0.7 的离线 RV32/RV32C 解码，并自行按 bit 位解算 JAL、B、C.B、C.J 和 I/S 访存字段；只保存必要锚点。结果见 [review-result.json](../../analysis/window-slider-review-k04-0041-20261024/review-result.json)。

|主张|独立原件依据|裁定|
|---|---|---|
|a00d81f8 在自身 class 入参非零时先查 base|81f8 C.BNEZ→822c；822c读class.word0，再822e C.J→81fe。81fa/fc只在最初class为0时取current对象/class|接受；K01显式传自身class，因此是祖先处理，不是类型检查|
|只调用首个非空祖先event槽|8200读class+c，8202空则回822c；非空分支820e清E+c，8212重读槽，8214保存E，8216以当前a0=class、a1=E间接调用|接受；helper不自行调用所有祖先。祖先回调内部的递归行为不在此接受范围|
|返回精确1来自flags，而非回调数值|8218 LBU a0,18(s1)覆盖回调返回；8220 `not a0,a0`，8226 `c.andi a0,1`；无class的8230置1|接受 `(~flags)&1`。H04所述bit0删除标记关联继承；不给该位另造正式枚举名|
|K01事件/键ABI与mask|4cc0保存incoming a1为E；4ccc LW E+8，4cda LW E+0；4cd0/2/4构造ffff8000−1并AND；4cde/4d00的独立B字段分别比较31h/11h|接受，只清bit15。没有将mask写回E.code；key getter仍受原code==11h的旧合同限制|
|精确返回门与左右索引门|4cc8 BNE a0,1→出口；4d16为BGE x0,a0，4d48为BLTU a1,a0；key常数13h/14h/0ah及分流目标独立核定|接受signed非正与unsigned `<count`的区别。getter/count/setter/删除的必要JAL真实目标与K03一致|
|class+c实际绑定到K01|a03725cc的四word确为a0263ef4/a00a4bdc/a00a4c54/a00a4cac|接受 event槽安装身份；不由地址表推出真实事件已发生|
|创建class与对象word0连接|8cbc/8cc0构造同C，8cc4→a00d76ae，8cc8将返回保存s2；generic factory的76c0保存class到s3，76e0零返回绕开，76e2 SW s3,0(a0)|接受成功创建路径的同class身份。分配算法、其他构造行为和实际成功不扩大认证|
|62fcb6b0保存对象而非+30 handle|8b90/8b9c得到s7=62fcb6b0；8d1e SW s1,30(s2)，8d22另SW s2,0(s7)，8d2c重读槽|接受全局对象引用。旧068所选寄存器序列支持s2来自创建返回；不能认证全局唯一owner或当前target必等于槽值|
|删除和清槽原序|4d58/5a查O+38；零分支4d62以O作a0，4d64→a00ded6c，4d6c SW zero到全局，再跳出口|接受调用后清引用；未比较O与槽值，也没有删除数值返回检查。清槽本身不是free|
|count宽度与已知前置门|495a→a00dd144后尾声不改a0；dd190读O.extra，空返回0，dd196为LHU extra+30；4c40/44初始化两索引0；4af4只有count零门，4af8只有与当前索引相等门|接受返回范围0..65535及既有门。没有证据把N≥1、idx<N提升为所有时刻成立的不变量|

语义纠正0。以上接受只针对正常下层调用返回的静态合同。事件机制沿H04：栈事件借用，class callback与descriptor callback ABI不同；清E.user_data不等于释放userdata。K01没有本轮新分配或显式free；对象资源责任仍交公共删除及既有对象树/class析构链，不把全局引用改称排他所有者。

## 真正新增

**新增功能、ISA规则、来源排除及完整函数导出均为0。** 本轮交付仅为未参与生产的agent对K03实际增量的限定独立接受，以及必要原件核验索引。K01索引算法、H04事件/key/delete、旧callee、最终SIM验收均不重新计成果。

在外部已有 `N≥1`、`0≤idx<N` 时，K03给出的左右环绕公式符合signed/unsigned原门；这只是条件代数。构造零索引、callee非零count门和class/global接线不能推出append必成功、所有事件期间count恒非零或此前索引仍有效。复核没有运行count0、非法索引、异常输入或缺陷实验。

## 精确未闭与实际验证

保留：正常调用全程的count/当前与先前索引不变量；全局所有writer、排他owner与target/槽值一致保证；31h正式枚举名、输入设备/真实页面可达性及实际产品效果；附属资源完整生命周期和精确源码版本。K03保留这些边界正确，不将部分局部接受写成完整slider、FactoryTestMode或原ROM完成。

独立脚本实际运行 **84项稀疏检查及4个class word PASS**；检查包含必要直接目标、标准和压缩条件/跳转字段、访存宽度/偏移、mask常量及关键ABI锚点，未执行目标指令。JSON解析、报告相对链接及diff检查通过。没有运行K03脚本或任何旧SIM/回放/构建。

K03所提旧068的8d2c后child构造循环、8d68创建/8d82递增/8d86回边是另一个可定位种子；本次未接管，也不对其构造count条件作技术裁决。是否继续由管理者按旧合同去重后另派；不能从构造时条件外推完整生命周期，更不扩GPIO或根析构。
