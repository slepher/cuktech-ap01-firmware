# K05：slider 八轮构造请求与初始索引条件

2026-10-24；基线 `1dcbfe6`；独占树/分支 `re0041-k05` / `codex/re-0041-k05`。**正常返回循环请求创建8个直接子对象；请求计数独立于创建返回值和20 B wrapper申请结果。配置成功路径读取实际 parent child_count 决定新子对象的初始横坐标，没有最终 `N>0` 验收或显式选择初始索引的调用。** 因而8轮不能证明N=8，更不能单凭循环证明整个构造完成后 `N>0 && idx<N`。给出下述条件正常合同并保留精确断边，待独立技术复核。

采用已读 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读主仓原件与既有证据，不打开/切换共享REA target，不运行固件、SIM、模型、构建、历史回放、输入实验、设备或外部服务，不做异常输入/漏洞/缺陷验证。仅写本路独占报告/analysis，无生产代码、ROM、配置或分析器模型变更，无下级agent。伪代码为分析重建，不是原源码。

## 继承结论：已有→行为→局限

|已有出处|可靠合同，直接继承|本轮实际缺口|
|---|---|---|
|[K03](window-slider-contract-k03-0041-20261024.md)、[K04独立复核](window-slider-review-k04-0041-20261024.md)|class+c绑定K01；工厂创建结果保存至 `62fcb6b0`；constructor将当前+38与先前+3c置0；count wrapper返回 `LHU(extra+30)`；K01事件/祖先状态/导航/删除原序|仅8d2c后构造请求及实际count的连接；不重复验K03|
|[E05](ctk-app-close-e05-0041-20261023.md)、[E06独立复核](ctk-app-close-review-e06-0041-20261023.md)|`a00d76ae(class,parent)` 成功对象写class/parent；非空parent路径读/加/写u16 child_count，再按count*4重分配并追加对象；d7800的srw原字/shift2早已接受|复用通用挂接合同，不再导出factory、重做厂商字或整个对象树|
|[H03](weather-page-close-h03-0041-20261023.md)、[H04](weather-page-close-review-h04-0041-20261023.md)，E06|`a00d7806(obj)` 是class析构walker；对象数组移除、count变动和对象本体free属于公共删除核心的后段|caller的wrapper空分支须按实际callee表达，不能自动补成完整删除/append回滚|
|[J04](factory-reuse-gap-j04-0041-20261024.md)、K01，最终application complete/SIM与旧source ZIP盘点|factory slider与日常窗口为不同对象/地址家族；旧SIM/照片/替代服务范围明确|不套用日常a005d0b6的 `active=count−1` 种子；passed-in-sim不认证本ROM构造不变量|
|旧 `whole-rom-private-20261023-068.json`，Evidence `ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`|完整dispatcher原字/伪码早已留存；K03/K04明确定位8d2c、8d68、8d82、8d86但未解释本题条件|只取真实循环/返回门/初始位置控制点，不导出整dispatcher/颜色文字内容|

按精确循环地址、全局槽、`add_window`、constructor交叉查询现有报告，相关命中为K03/K04/K01，通用parent挂接则由E05/E06已有覆盖；该有界查询不代表此前所有历史都未分析。早期日常screen-host报告的追加试验只作旧范围说明，本轮不执行其脚本。忽略JSON/原件均从主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/` 只读访问。

## 本轮复核或纠正

已有语义纠正0。旧068伪码中的 `uVar24` 只用于定位；本轮按原字确认其寄存器为s2，已经在 `8d2a` 被置0，和K03里较早保存创建O的s2不是同一活跃值。此时O早已由 `8d22` 发布到全局；每轮 `8d2c` 再读全局到s5。不能把后续s2当对象指针，也不能把它当已成功创建的孩子数。

独占 [verify.py](../../analysis/window-slider-construction-k05-0041-20261024/verify.py) 直接读取原ROM，映射 `offset=VA−0x9ffff000`。35项稀疏检查含10个JAL、3个B型门、3个压缩条件门和2个访存字段独立位解算，结果见 [evidence.json](../../analysis/window-slider-construction-k05-0041-20261024/evidence.json)。旧068只查询必要汇编及是否有直接setter调用，不导入/运行K03/K04或历史验证器，不生成新REA Evidence ID。

## 真正新增：请求、挂接与位置的条件合同

### 请求数与两层返回值

|原指令位置|正常静态行为|数量/所有权含义|
|---|---|---|
|8d2a；8d2c/8d30|s2=request=0；每轮重读全局O到s5，非零才进入8d68；零对象分支记录断言并自环8d66|正常终止循环以非空O为条件；不证明全局跨调用稳定，也不把断言自环当执行结果|
|8d68/8d6a/8d6e|`child=a00d91c6(O)`；返回保存s1|这是直接child创建请求，非wrapper申请；O通过a0传入|
|8d70→8d82|child返回0直接跳请求递增|本轮计数仍增加；未因失败停止或重试本次编号|
|8d72/8d74/8d78|child非零时以a0=14h申请20 B，返回保存s10|这是另一次独立申请，不能与child合并成一个“成功计数”|
|8d7a；8d7c/8d7e|wrapper非零进入8dd0；零时 `a00d7806(child)`，随后落8d82|只证明调用class walker；本caller未调用公共删除/显式递减parent count，不认证完整回滚或该child最终可用性|
|8de2|成功配置路径SW wrapper到child+10|wrapper成为child保存的指针；其完整内容/资源/释放不在本题|
|8d82/8d84/8d86|request+=1；与常数8作BNE，不等则回8d2c|无论child0、wrapper0或正常配置返回，均由同request递增控制；正常终止时请求编号为0..7，不是8次已成功配置承诺|

`a00d91c6` 的必要薄接入：`d91d0` 将parent移到a1，`d91d2/6` 形成普通class `a0263ef4`，`d91da` 调同 `a00d76ae`。非零返回保存在s1，`d9222` 调初始化 `a00d9110`，`d922a` 将保存对象作为a0返回。因此其parent挂接使用E06已有合同；这里没有用目录名或API外观代替对象地址。wrapper/子控件进一步装配不展开。

### 使用实际count安放子对象，没有选初始索引

成功配置路径在 `8e5e` 以s5=本轮O调用 `a00a491c`，而非使用request或child作为实参。`8e64` 置a5=1，`8e66/68` 先给y=0、x=320；`8e6c` 的BLTU a5,a0在 `1<count` 时直接到8e72保留x=320；否则 `8e70` 改x=0。`8e72/74` 将本轮child与这组坐标交给 `a00d8d1e`。

所以正常“第一个保留孩子放在0、后来孩子放在320”的描述必须以当时实际count为准：谓词是 **N≤1**，不是 `request==0`、不是精确N==1，也不是根据申请次序推成功次数。该调用不写O+38/+3c；K03/K04已证它们在class constructor末端为0。本轮在旧068留存dispatcher汇编中未见直接JAL `a00a4aa0`，该有界结果不能排除初始化/尺寸/样式callee触发的间接callback或其他状态变化。

正常条件下，若同一O在构造进入时已有索引0，并且随后索引仍为0、至少一个成功挂接的直接child被保留到所选观察点，则该点N≥1，索引0有效。若另外已知进入时N=0、8次创建及parent挂接均正常完成、全局始终同一O且没有其他增删，那么可得到N=8；**这些额外条件不是request循环本身的验收结果**。wrapper申请成功数与parent的结构count也不能直接相等，因为parent挂接位于普通child创建服务内，先于caller的20 B申请。

原callee中的实际分配、重分配与初始化回调均按已有限定合同引用；不把“调用已返回”补成完整服务成功、不变式保持或资源全部可用。这里没有输入枚举、失败触发或缺陷试验，仅描述原有返回判断。

## 精确未闭与交付检查

继承：K03/K04的class/global、零索引、count读取、事件/删除；E05/E06的通用parent挂接；H03/H04的class析构层次。真正新增：8次请求与两层成功条件分离、原失败分支和递增原序、实际count决定初始位置的连接。未新恢复通用factory/厂商规则、颜色文字/资源、全部工厂命令或原ROM来源版本。

仍未认证：各申请实际成功、所有8个可用child、同一O在循环期间全局稳定、进入时N=0及所有初始化/尺寸事件对索引与count的副作用、构造结束后的动态增删和全生命周期不变量。当前准确断边为普通创建返回和配置callee内部可能发生的状态变化到“循环结束时至少保留一个child且idx仍0”的保证；caller没有最终非零count/有效索引检查来替代这些保证。无证据时保留条件结论，不声称N=8或整个初始化闭包完成。

实际运行独占静态脚本：**35项PASS**；JSON解析、相对链接和 `git diff --check` 通过。没有执行对象创建、分配、配置、目标ROM或历史回放，没有导出整函数/资源/源码或机械哈希清单。作者检查仍需独立技术接受。

本题已把有真实种子的循环控制与可证明范围说明清楚。没有取得建立全程索引不变量的新writer/callback连接，不建议为补不变量遍历所有GUI/根析构或顺颜色文字分支扩大范围。后续先独立复核本轮实际增量；其他研究由管理者另按真实种子去重派发，本路不自行接题。
