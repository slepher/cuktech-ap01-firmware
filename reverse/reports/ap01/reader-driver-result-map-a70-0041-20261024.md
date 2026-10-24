# A70：J08/9 reader错误word到数值status的静态映射

2026-10-24；固定基线 `bd457a6`，分支 `codex/re-0041-a70`，认领 **J08/9**，作者 `/root/g23`。**0xa00ea524是一个无callee、无外部数据读写的数值映射：输入a0的word经signed阈值门/相等比较，返回a0中的常数0..12。12个明确输入值分别映到0..11，其余输入word返回12。** 本函数只在自身16B栈帧保存/恢复s0，不读getter、IO状态或driver对象。

恢复使用原分支/常量字段，没有执行目标、模拟指令、运行模型、host输入枚举或异常输入试验。所有名字保持数字事实，不用标准errno/LVGL enum或未认证版本给常数补含义。接到A66/A68时，被映射的是**日志后第二次getter实际读到的word**，不是第一次值或底层IO原负返回；映射本身不证明这些值相同或错误槽必非零。

权限取自主仓 [唯一认领表](rolling-management-0041-20261023.md#链条认领表) J08/9；沿本批已读 [流程](reverse-design.md)、[保留规则](../../analysis/README.md)和 [REA技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读本函数必要原字段/旧定位，未读getter、IO、其他driver/helper；不运行旧技术脚本、固件、SIM/QEMU、构建、回放、设备或外部服务，不切换共享REA/模型，不改生产ROM配置、主树/共享表，无下级agent、提交推送。作者自检待非作者复核。

## 继承结论

|旧出处|已有连接与局限|本轮差集|
|---|---|---|
|[A66](reader-driver-open-close-a66-0041-20261024.md)|close失败路径日志后重新getter/LW，再把所得word交0xa00ea524；转换body此前opaque|只继承实际输入/输出使用，不重验open/close、格式化或fd接口|
|[A68](reader-driver-read-seek-a68-0041-20261024.md)|read/seek负返回分支同样以第二次getter值调用转换服务，尾声保留其a0|只补数值返回协议，不重读callback、底层IO或off_t边界|
|旧whole-ROM索引functions3328|0xa00ea524..0xa00ea5af，140B；extent EID `ev_c45212c04d6f0d4df9dca25e571b40d05e3508d5ddc8867f30925bac3eda87c2`；directcall EID `ev_5007020263124b8311e3c1adbf8333401dcf5802fde5a39c2afccb94b3e5c2e7`列空；无dossier/历史body合同|旧metadata只定位，未提供映射值/比较signedness；本轮仅该函数原字段，未扩其他库|

查重以主仓A66/A68的opaque边界及旧functions3328为依据；近期AP01精确地址报告只有调用端，没有此函数已验body数值合同。有限出处盘点不写成全历史从未分析。本题与J08/7–8共享转换callsite，但参数/返回映射是独立问题，不重计上层driver功能。

原件沿 [CATALOG](../../../roms/CATALOG.md)：AP01 `1.0.2_0041`，主仓`roms/0041/ap01-1.0.2_0041.bin`，6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射`file_offset=VA−0x9ffff000`；只核长度、继承摘要，不重算hash，不套0031/SIM。新字段证据无新REA生产ID/profile，旧EID各自来源保持。

## 本轮复核或纠正

旧A66/A68语义纠正0，映射是此前保留的精确断边。输入按RV32寄存器a0取值，不当作指针解引用；分支树的三个大小排序门都是**signed BLT**，不是unsigned门：

- `0xa00ea52c`先BEQ输入16→a5置7的0xa00ea5ac；否则`0xa00ea530`以signed `16<input`分到高侧。
- 低侧先等值比较12；`0xa00ea53c`用signed `12<input`分开13/14与2/5/0处理。
- 高侧先等值比较38；`0xa00ea57c`用signed `38<input`分开110/114与22/28处理。

等值门分别为BEQ或BNE，零分支在`0xa00ea552`用C.BNEZ；不能把BNE的默认返回路径误认成该常量成功分支。保留原指令分流次序，即使最终表可简写成相等映射，也不把原signed门改写为另一个ABI。

本题没有构造可调用host替代函数、遍历输入求结果或对目标做试验。下表来自静态分支目标和常量定义的手工路径重建；检查器只核编码/地址/内存效果、保存该表，不执行这个映射。

## 真正新增

### 完整数值合同

|输入a0的32位word数值（十进制）|返回a0（十进制）|判定/结果常量地址|
|---|---:|---|
|0|0|a552零fallthrough→a554置0|
|2|3|a544等值→共同返回；a542置3|
|5|1|a54c等值→共同返回；a54a置1|
|12|10|a538等值→共同返回；a536置10|
|13|6|a562等值→共同返回；a560置6|
|14|2|a56a不跳默认返回，a56e置2|
|16|7|a52c等值→a5ac置7|
|22|11|a584等值→共同返回；a582置11|
|28|4|a58c不跳默认返回，a590置4|
|38|9|a578等值→共同返回；a576置9|
|110|8|a59a等值→共同返回；a598置8|
|114|5|a5a4不跳默认返回，a5a8置5|
|其余32位输入word|12|各未匹配臂保留/重置a5=12后汇共同返回|

其中返回路径均为`0xa00ea556`恢复s0、`0xa00ea558 C.MV a0,a5`、`0xa00ea55a`恢复sp、`0xa00ea55c RET`。显式输出在a0这个**32位寄存器**，所有结果都是非负小常数；本题不据此认证C enum的名字、源级声明/packing或精确library版本。

### 副作用与原字锚点

`0xa00ea524`建立16B本地帧，`0xa00ea526 C.SWSP s0,0xc(sp)`是唯一存储，`0xa00ea556 C.LWSP`恢复它；没有global/heap/输入指针读写，未保存或发布参数地址，没有JAL/JALR/call。局部栈有效和正常返回ABI是前提，不把这句话说成函数完全没有内存操作。

独立字段证据包括：

- `0xa00ea52c 6300f508`的BEQ输入/常量16与目标a5ac；`0xa00ea530 63c1a704`的funct3=4确认signed BLT。
- `0xa00ea53c 6341a702`、`0xa00ea57c 634ca700`同为signed BLT，分别比较12/38。
- `0xa00ea552 11e1`是C.BNEZ a0→0xa00ea556；输入为零才继续`0xa00ea554 8147`置结果0。
- 27条C.LI/ADDI常量独立拆rd/imm，14条B型门、4条C.J与零门独立拆目标；共同返回原字/栈读写与无callee按完整140B静态解码核对。

这补出的是数值映射，不是新的错误状态观测。若A66/A68第二次getter读到0，本函数就返回0；它不依据先前IO负返回另行强制结果非零。哪个错误word在实际服务中出现、两次getter是否同值及错误状态语义仍依上层/底层各自合同，不能把表中的数字直接命名为标准errno或具体LVGL状态枚举。

最小机器合同见 [contract.json](../../analysis/reader-driver-result-map-a70-0041-20261024/contract.json)：明确输入word、十二个特例、默认12、signed排序门、32位返回和局部栈效果。没有把源码family候选当精确未改来源或整库排除。

## 未闭精确边、实际检查与后继

本函数的所有已观测分支与默认数值返回已给出静态答案，没有新callee断边。仍未知调用端第二次错误槽的真实值/稳定性、各数字的正式source enum/版本及实际FS/设备结果；这些不是mapper内缺失分支，不能借它扩大getter/IO/其他driver。

[verify.py](../../analysis/reader-driver-result-map-a70-0041-20261024/verify.py) 实际 **55项静态常量/控制/效果检查PASS**。仅三段48B/48B/44B、合140B原字段，Capstone 5.0.7离线RV32/RVC及独立编码字段，无厂商未知字、输入枚举、调用/模拟或模型执行；不运行作者/旧脚本。[evidence.json](../../analysis/reader-driver-result-map-a70-0041-20261024/evidence.json) 本地原路径忽略保留必要常量/分支字段与路径出处，不保存整函数源码或完整通用关系账本。JSON、相对引用、Git忽略、独占文件及diff检查通过；报告/源码/机器合同未提交推送。作者自检待非作者复核。

有种子后继仅在同 **J08/9** 安排非作者A71核静态映射表、三signed门/默认12、公共返回及栈效果；不重读callback或扩其他错误体系。进一步把映射接到真实IO错误状态，应先有相应getter/底层调用的精确正常证据并另登记，不能从此表反向猜运行输入。
