# 0041 F10：F09 容量 helper 独立复核

限定接受 F09 的 `a00ecc68` 正常合同，无语义纠正。owned 字节原值作为返回值，调用者只测非零；成功路径先发布 data，再发布 capacity，必要时才截断 count。**本轮新增业务/功能恢复为0**。这是旧结论独立复核，不是重新发现代码或新增事件库恢复。

基线 `f2d4bc9`；独立分支 `codex/re-0041-f10`。应用 REA shipped-artifact 证据分层，只读原 ROM 和既有材料，未打开共享可写分析目标。只写本报告及独占 analysis；未运行 SIM、构建、历史回放、固件或归档脚本，未改生产、ROM、配置和分析器模型。

## 已有成果→实际缺口

|既有出处|已解释行为及类别|局限；F10 实际处理|
|---|---|---|
|[F09](event-array-maintenance-f09-0041-20261023.md) 及其 evidence.json；原字节行为|容量 helper 的门、参数、乘积、发布顺序及返回；旧 caller 已知|仅需独立核正常合同；本轮只重读必要字节，标为旧结论复核|
|[G03](invalidation-submit-g03-0041-20261023.md)、[G04](invalidation-submit-review-g04-0041-20261023.md)、[G05](display-event-flow-g05-0041-20261023.md)、[G06](display-event-review-g06-0041-20261023.md)；已恢复/复核|descriptor 注册、容量满时 count+4、重入/删除/压紧、延后释放|全部继承，不重复导出、记账或认证完整事件库|
|主仓 reverse/analysis/0041-20261013/refined/0041-candidate-disassembly.txt，第56009行起；旧留存指令|a00ecc68 及续接字节早已存在|标题不认证边界；本轮仅拿必要原字节与正常控制流相互校核|
|[F07](display-source-auth-f07-0041-20261023.md)、[F08](display-source-review-f08-0041-20261023.md)；候选源码比较|ROM 与 LVGL9.2.1 的匹配和差异；20B 为前缀，另有 list+14 状态|继承，不用候选16B array覆盖ROM，不认证版本/整库排除|
|F09 的旧最终报告/矩阵/map/complete/ZIP 有界检索记录；SIM及检索范围证据|旧 SIM 行为与来源边界已区分；近期 G03–G06 比较早未知清单更新|直接引用 F09 检索范围，不再次遍历 ZIP、不重建旧检索账；地址未命中不等于未曾分析|

## 继承的旧结论

array 可见 data+0、count+4、capacity+8、element_size+c 是 word，owned+10 是 byte；owned 仅沿用既有字段角色名，不由名称证明来源。完整 list 大小未知。F09 已主动收缩早期 F06 未展开清单，G03–G06 的正常分派与删除维护均不属于本轮增量。

原注册器完整返回 ABI、所有动态订阅者与重入组合、底层 heap 合同不在本题。SIM passed-in-sim、ZIP 重建源码均不能证明上述 ROM 边界。

## 本轮复核或纠正

[review.py](../../analysis/event-array-review-f10-0041-20261023/review.py) 只读原 ROM，映射 `offset=VA-0x9ffff000`。独立使用 RV32/RVC 位域，而非运行 F09 验证器或复用其反汇编断言结果。23 项检查通过，结果见 [review.json](../../analysis/event-array-review-f10-0041-20261023/review.json)。只保留校核结果，不再次导出整函数或整份指令清单。

|原指令位置|独立校核结果及含义|
|---|---|
|a00ecc76 / ecc7a|opcode/funct3/寄存器/立即数为 LBU s3,[a0+10]；非零跳 eccb0。读取未做 bool 规范化|
|eccb0..eccbc|s2保存原a1，word读取element_size与data；标准RV32 MUL低32位乘积传a1，JAL a008c332；无厂商指令解释歧义|
|eccc0|仅非零返回跳 ecd02 正常尾；零分支不接成本轮正常合同|
|ecd02..ecd12|先读取旧count；data SW@0→capacity SW@8；BGEU s2,a5跳ecca0，否则count SW@4再跳同尾。unsigned比较与实际发布原序均成立|
|ecca8 / eccaa / eccae|先把s3移入a0，再从栈恢复调用前s3，最后经ra返回；返回原LBU数值，不是data或固定1|
|a01b9510..951a|a1加4，a0传s1，JAL ecc68；返回只做非零分支到94e8，零跳9504。追加路径合同继承G05/G06|

因此 F09 对正常非零分配返回的说明可限定接受：调用后非零 data 先发布，capacity随后发布，old_count较大才更新count，最终返回初始owned字节。零owned路径的日志及共用返回尾沿用既有合同；日志/分配器的跨调用保存寄存器依正常RISC-V ABI解释，不额外宣称底层实现已认证。

无语义纠正；补充报告精度仅为明确“正常尾”必须经 eccc0 非零分支进入，不能从未知断言返回边线性接入。该限制 F09 本身已正确保留。

## 本轮真正新增

独立复核结论与23项静态校核；新增功能0、新增业务恢复0、来源整库排除0。原字节重读统一计旧结论复核。未新增 callback、分类、资源或列表生命周期恢复，也没有重新登记 F09 局部合同。

## 仍未闭合的精确边

`a00eccfe→a0019672` 是否返回继续未知；零分配返回进入该诊断/断言块时，不能把线性后的 ecd02 解释为正常发布，也不能伪造安全失败返回。本轮未追断言、不开展异常输入或缺陷研究。

`a008c332` 的 realloc/heap 内部、零容量语义及真实回收仍为 opaque 调用边界。未认证完整 list sizeof、ROM精确LVGL版本或所有动态组合。

本题已得到所需独立复核，无必要再扩本题。后续若管理者另派任务，只能围绕另有证据不足的精确边继续，不能为本题凑函数或闭包。
