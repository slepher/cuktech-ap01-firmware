# J04：工厂正常UI/资源生命周期旧成果复用盘点

2026-10-24；基线 `09e11d0`，独立分支 `codex/re-0041-j04`。**工厂GPIO启动门、fd取得/失败清理、三轮后保持及独立长鸣已有合同；本轮新增功能0。只保留一个有既有extent/caller交叉证据的小候选：`a00a4cac`（198B）到工厂slider三个接口的正常UI动作接入。** 没有据此恢复其参数/事件码/索引门；成功后的stop/close、根对象析构与物理效果均不新派无种子扫描。

采用 reverse-engineer-anything 技能的既有证据优先与覆盖分层。仅检索旧报告、主仓ignored JSON的既存元数据与指定词项；没有读取ROM、新增原字节/反编译、重建分类/资源表、使用共享REA target、执行工厂命令/固件/SIM/模型/构建/回放/设备/外网或研究异常/缺陷。只写独占报告及analysis，未改主树、共享索引、生产ROM/配置/模型；无下级agent，未撤销他人修改。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

|已有出处与地址/字段|已覆盖行为|局限/精确缺口及处理|
|---|---|---|
|[reference-map](factory-reference-map-0041-20261020.md)及其analysis JSON；[application最终验收](application-rehost-complete-0041-20261017.md)、[matrix](application-function-matrix-0041.json)|33个可达构造器及服务SIM范围；两个factory路径旧账为不在matrix、完整C文件未认证|旧关联数0不是原件未分析。matrix里的`ap01_sim_factory_reset`是设置复位服务，不是量产工厂测试UI或硬件测试验收；不重建整表|
|[factory-test](factory-test-0041-20261023.md)，initializer `a005a736`内联块、callback `a009f178..f347`|GPIO3采样规则、GPIO12数字写入；输入fd=`62fc4004`、输出fd=`62fc4000`；成功active=`62fc92b8`、phase=`62fc9420`、count=`62fcb030`、timer=`62fc92c0`；失败分支已核fd释放；单次timer自重排、三轮后保持|直接继承，不再“发现”fd或三轮。成功后stop/close/fd释放、外部状态关系和物理极性未闭；本轮无真实新调用种子，不建议扫所有close/driver|
|[B16](factory-active-reader-b16-0041-20261023.md)、[B17独立复核](factory-active-review-b17-0041-20261023.md)|外部active reader一次有界定位只得到旧initializer写1、旧callback首门；B17已收紧区间/谓词/无代码数据过滤等边界|外部读者仍未知；不重跑字段/全ROM扫描，不把负结果升级为无消费者，也不把active=1解释为周期timer仍运行|
|[buzzer第一轮](buzzer-backlight-0041-20261023.md)B5，`a00a8582`内`a00a90fc..91a6`；第二/三轮及A01停机复核|独立10秒长鸣请求、busy/fd/running门、请求槽与worker/PWM局部责任已恢复|不能把长鸣与GPIO callback或工厂UI当作同一入口；蜂鸣正常线程退出未知继承，不重复停机负搜索|
|[multi-screen host](multi-screen-app-host-0041.md):79；host-slide/append及[H07](weather1-navigation-h07-0041-20261023.md)|已区分`factory_ui/lv_window_slider.c`命名组件与日常`lv_power_ui/lv_ui_window.c`；append实际procedure为`a00b3106/a00ab628`等，H07普通导航保留同一日常W子页；host-slider仅合成对象/LVGL leaves验证|三个callee与这组日常地址不同。日常索引/300ms/ready责任不能直接套到factory_ui组件；旧host文字的“供工厂测试界面”不认证与FactoryTestMode/GPIO业务连接|
|主仓system complete、settings round2至round2e及近期专项复核|日常设置/复位与服务边界已有；相关factory initializer也被MiIO/display等任务复用|6份system/settings文件按工厂路径、两slider地址、GPIO callback/active字段精确词项无命中；全rehost按本候选入口/slider词项无命中。负结果仅限文本与这些文件，不能否定历史或间接调用；近期display/MiIO复用同initializer不等于恢复工厂UI|

主仓绝对前缀统一为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。旧factory-test的保留initializer Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`、B16/B17的已审查询边界、buzzer的旧body及其局限直接引用，不重复校原字。资源“尚无关联”不表示未用、缺资源或需要全量提取。

## 本轮复核或纠正：旧关联空白不等于实现空白

旧 `factory-reference-map-0041.json` 对 `PogoPinMng/FactoryTestMode.c` 和 `factory_ui/lv_window_slider.c` 的函数关联均为空，明确不在UI matrix且完整文件未认证。后来的factory-test/B16/B17已经覆盖前一模块局部；whole-ROM round1既有source-xrefs已将后一路径 `a026872c` 关联多个slider函数。这里是旧证据范围交叉与关联精度收紧，不改共享旧表，不重建分类，不宣称这些函数本轮首次发现。

正常GPIO片段、独立蜂鸣、factory_ui命名slider、设置factory reset四者保留各自入口/证据层次，不能因“factory”名称相同而连接所有权或物理作用。路径xref只支持模块归属，不能自动当作FactoryTestMode界面或GPIO模式的入口。没有机器语义纠正，也没有执行证据。

## 真正新增：一个可供管理者选择的已有种子

|候选精确边|既有真实证据|允许的下一步与重叠边界|
|---|---|---|
|`a00a4cac → a00a4116 / a00a491c / a00a4aa0` 的UI动作接入|主仓`reverse/analysis/whole-rom-coverage-0041-20261023-round1.json`：入口extent=`a00a4cac..a00a4d71`，198B，Evidence `ev_a516b7ee45ef6385470a3f9afec6e7f7ae97bf725d4ac4ada41f51eac0352150`；direct-call Evidence `ev_bc62d24f75109fd94a41f3bebcf02277e33f5fa6c2ee47c2149d8f3cab8cdc2a`包含这三个callee。三个callee的旧dossier又分别把它列为caller，source-xrefs把callee归到factory slider路径|只建议核这一个入口的实际入参、正常事件/索引判断与同一slider对象的调用连接；getter/setter日志名只是定位语境，不先承诺返回ABI或正常触发。不是恢复整个工厂UI，不扩所有动画/资源/driver|

三个交叉dossier均在主仓 `evidence/rea-0041-20261017/evidence/`：`whole-rom-private-20261023-036.json`（`a00a4116`，`ev_a69ee943e45e52132c5985c140711e714400cc5b74cd44d0df9a506a1881f9f4`）、`-043.json`（`a00a491c`，`ev_c314a412c39242e310f9290afee3dcbb2ba583177cf87a56041dbf23d3bfaa17`）、`-047.json`（`a00a4aa0`，`ev_8b6ea19931eaa4dc2ffc322dddd2871cb71af6e21f226eed6ab8a32b2b46772c`）。这里只读取procedure/body/caller/source字符串元数据，没有复制或重导函数。所选source-xref Evidence为 `ev_6fe28ef7e060f411f20dd7f4928d0225ee14ae3a41ef0b49c0e93b89b863c853`。

重叠核查并非只看caller地址：按三个callee地址及其`get_active_win_idx/get_window_count/set_active_by_idx`日志名交叉检索。guide-complete/guide-round2命中的是日常`a00b2ff4/a00b3106`；guide实践/render/timer及三份page-logic没有该factory三callee/日志名命中。screen-host-append的实际procedure也属于上述日常对象；host-slider范围未执行完整UI/硬件，H07明确日常切出保留对象，均不是本候选同一动作的factory对象合同。结果见`cross_component_reuse`，不把同类操作名当同一对象。

当前reports对入口`a00a4cac`无命中；同组slider/path词项只命中旧inventory、reference-map、multi-screen host定位。主rehost全部JSON按入口/三个callee/日志名/路径的文本查询无命中。index里该入口自己的dossier与historical_contracts均为空，**这仅是此索引范围，不能宣称没有任何旧分析**。三个callee已有完整留存优先复用；后继若发现父级旧body覆盖，应立即收缩而不是重导。

该入口direct-call列表另有`a00ded6c`，但当前没有实际target/事件/所有权合同，不能凭“出现delete callee”派根析构任务。也没有它到GPIO timer/fd或active的已证连接，不能拿UI动作种子补工厂stop/close。

本轮新增的是这份复用裁定和有限后继定位，新增ROM功能0、原字节0、反编译0、开源/整库排除0。caller与extent是元数据事实；将其视为UI动作候选是有局限的推断，参数、返回、对象身份、事件语义和运行可达性均待后继核实。

## 未闭精确边、停止边界与验证

成功进入工厂模式后的stop/close/fd归还、工厂根对象及资源析构链、UI与GPIO测试的关系、active外部reader及所有writer、物理引脚/极性/实际灯或蜂鸣效果仍未知。本轮未取得这些边的新入口/对象种子，因此不建议相应全局搜索。B16的有界未知已经独立复核，重复同一谓词不会形成新闭包。

唯一建议是上述198B入口的正常slider接入；由管理者决定派发，本轮不自行接题。它与运行中的I05配置cache、B22 cmd51类型分类、J03设置持久化、T01 timer最终归还及I04 Time2责任范围不同；不扩`a00a8582`内已归B22/旧buzzer的分支，也不复制日常UI合同。

[inventory.py](../../analysis/factory-reuse-gap-j04-0041-20261024/inventory.py)实际只读旧JSON/报告：核198B extent与三个callee、三个独立旧caller表/source路径、matrix范围、旧map两项及精确词项检索，结果见[reuse-result.json](../../analysis/factory-reuse-gap-j04-0041-20261024/reuse-result.json)。未接触ROM或运行旧扫描器；JSON解析、报告链接与`git diff --check`通过。此为复用盘点而非新技术合同验收，不把物理效果或整个工厂模块标为完成。
