# 0041 六路滚动管理（2026-10-23恢复）

用户最新授权恢复持续六路推进，取代历史收尾暂停与三路上限。原管理交接已归档至 rolling-task-history-0041-20261023.md。主窗口只管理，不作函数逆向或技术语义判断。环境共7席，主窗口1席，研究/复核6席。最新批次六项均已整合；后继任务经过复用筛选后启动，真实状态见运行快照。

## 共同规则

只做0041静态功能恢复；禁止执行固件、连接设备/外部服务、漏洞/异常输入/缺陷验证、修改安全检查、ROM、生产代码、构建配置和分析器模型；不推送。只写独占reverse/analysis和reverse/reports/ap01文件。只用自己的独立worktree和分支，每次shell显式workdir并在PowerShell Set-Location。其他agent同时工作，不撤销他人修改、不改主树或共享索引，不创建下级agent、不自行接后继。忽略ROM/证据/工具从主仓库绝对路径只读访问；不复制工作区，不共享可写数据库或切换全局REA。优先留存证据；若工具不能隔离则报告管理者。临时状态/日志放各自独占analysis目录。只恢复正常原程序行为，不擅自修正。

交付列问题/范围/结论、业务行为、函数地址/参数/返回/调用、必要伪代码结构体状态转换、所有权生命周期、可定位证据与原指令、事实/推断/未知、来源与恢复程度、实际静态验证、断边和一个后续闭包。伪代码不是原源码；保留调用顺序、重读、宽度/符号、返回判断、失败/清理和间接ABI。边界/厂商指令须核原字节，不仅信反编译。标准库只有来源可核实才排除，适配/回调仍恢复；不新增哈希清单/复制清单/机械重复证据。不编译项目，不运行历史回放。完成标准为原问题闭包得到有证据答案或明确可定位断边，不能缩成短helper声称完成；不设函数数量或时长配额；主体已覆盖即收缩，已无必要增量即报告已覆盖并结束。

接近提交提前报告结论、剩余验证、阻塞和后继建议。检查差异、必要验证、明确路径git add、提交、报告commit/验证/未知/干净状态后结束。主窗口作范围验收，技术验收由新独立agent。恢复成果可先整合为待复核；不得自验冒称验收。每项完成即整合补位，从启动时最新管理提交创建新树；运行任务不移动基线。语义冲突交agent；回收仅限干净且已整合worktree，分支保留。用户要求收尾即停止派发。

主仓库：D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware。所有任务初始共同研究基线 ab9716e；实际启动基线为含本任务书的管理提交，在派发消息及运行表记录。

## 当前任务书



## 实际运行快照

以下六项真实运行，已结束任务即时补位，主窗口另计；不创建下级agent。

|任务|agent|基线|实际范围|
|---|---|---|---|
|A38|/root/a38_cache_key|beb2b7a|cache key匹配合同|
|A39|/root/a39_decoder_review|db28e99|decoder持有接入独立复核|
|D15|/root/d15_pwm_arithmetic|f312a1a|PWM厂商算术|
|E14|/root/e14_timer_deadline|beb2b7a|uv timer期限ABI|
|G13|/root/g13_device_poll|db28e99|具体设备poll/revents接入|
|H13|/root/h13_weather_clock|bdc139a|天气时钟返回ABI|

## 派发规则（本次用户调整优先）

先检索旧complete、最终验收、近期研究/独立复核，再按地址、调用点、callback、字段、资源和状态定位。旧路径先在当前reverse/rehost、reverse/reports/ap01、tooling和最终ZIP成员按basename/address/Evidence ID寻找。ZIP只读成员，不执行、不全解包/复制。旧round2/round4 remaining及单份pending须核父级complete；passed-in-sim仅SIM验收，不能外推ROM ABI/驱动/云端/来源。

每项先列既有出处→解释行为→证据局限→实际缺口，并区分原字节行为、旧反编译需局部核、SIM/照片/安全替代、未检到的精确边。可靠合同直接引用；仅补接入ABI/宽度符号/厂商字/对象身份/清理顺序。不可信custom0/unaff/extraout/no-return/边界具体定位，仅核必要窗口。重读原字节标旧结论复核，不算新增功能。禁止重复整函数导出、全资源提取、分类重建、PNG解码、全源码复制及机械哈希账。

报告必须分列继承结论、本轮复核或纠正、真正新增、未闭精确边。主体已有覆盖则收缩；无必要增量报已覆盖结束，由管理者决定换题。技术争议交研究/独立复核，不由管理者裁决。

## 本批已有成果→实际缺口

|任务/既有出处|已解释行为|局限与本轮真正增量|
|---|---|---|
|A25：A23/A24；pass3第1931/2048行；旧complete/ZIP复用对照|PNG session/pixel所有权及旧init调用已知|3ed71d2仅新增默认raw/free/align实际表绑定与实现；动态替换、heap/cache仍未知；A26只审新增|
|D08：D03–D07；charge/system complete服务替代|UART/DMA提交、持久描述符持有与归还合同|26f1f4f独立复核，新增功能0；channel分配到close及pool复用未闭|
|E07：charge-complete records[8]/[9]/[19]、round4、ZIP charge.h|a00f4610/a00f44e8/a00f5288旧原指令及SOC/时间/消费者已留存|bcfcb63仅为旧body边界信息；719b38d确认round3早已完整留存该函数与保存槽，E07/E08不可外推此前分析缺失；item+34/+38读者仍未知|
|F08：旧SIM最终验收、F07、ZIP来源|候选LVGL9.2.1匹配与差异已确认|3569ab7精度纠正：20B仅array前缀，另有list+14；enum packing不能覆盖ROM差异；新增功能/整库排除均0|
|G06：G05/G04/F06；system/settings round2b/c、page-logic[15]、ZIP timer|timer/create/resume和已恢复event主路径可继承|6c11f60/064320f仅3项尺寸/原序纠正；新增功能0；替代38 work生命周期未闭|
|H06：pass3第2653–2657行、weather-calendar-complete、H05|a00abed2/type4/ctx挂接/DELETE a00abb62早已有；文字/分类/arc/tiny消费者继承|7a8f3bc/52e61b9独立复核新增0；H05只增ABI/direct a019cbc0/显式free原序；正常离页连接仍缺|

H05/H06 type4 68B与H01/H03 type19 116B是不同对象；type19最终context释放另有断边，不套用。a019cbc0不得混同a0198946。旧SIM已覆盖weather分类/显示，不再重新恢复。

## 并发纠正（2026-10-24用户最新要求）

必须维持六个实际运行的独立worktree subagent；完成即补位。范围去重用于换题/收缩，不能作为长时间空席理由。主窗口维护准备队列；不为数量重复恢复已有成果。以下四项均以已定位断边或来源认证缺口为题。

## 提前准备的后继队列（未启动，不计并发）

- A31：A29交付后，独立复核其真正新增的调用/同cache身份与实参合同；旧照片Evidence全部继承。
- A32：A30交付后，独立复核计量callback/单位/预算数据合同，继承A27/A28 cleanup。
- D12：D11交付后，独立复核候选分层与来源认证范围，避免以候选低层deinit补ROM callback析构。
- E11：改为E09较晚round3覆盖纠正的独立技术复核，避免重复根退出搜索。
- G10：G09交付后，独立复核正常ready到watcher间接ABI，保留运行时触发未知。
- H09：H08交付后，独立复核旧type2未认证ABI/清理合同，分类/资源不重做。

以上需据正式报告收缩为完整独占任务书；若任务已覆盖且无必要技术增量，则从其他已定位缺口换题，不递归复核纯重复材料。主窗口在每项提交前准备具体任务，保持六路。

## 当前完整任务书 D15（已启动，基线f312a1a）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d15；分支codex/re-0041-d15；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/pwm-arithmetic-d15-0041-20261024.md及reverse/analysis/pwm-arithmetic-d15-0041-20261024/。

buzzer-backlight-round2明确lower ops+8=a0136762范围a0136762..a0136997中PWM分频/阈值厂商算术未恢复，round3/A02仍保留此边；本题只补正常PWM配置输入频率/duty到周期/分频/阈值与实际寄存器字段的算术合同。上层蜂鸣/背光映射、upper ioctl、stop/shutdown/轮询已留存，直接引用不重做。先查旧round2原窗口、完整system/guide设置与较晚round3，较新已有语义就引用；只补具体不可信厂商指令/宽度/符号/截断/寄存器ABI窗口，不改模型，不测异常输入，不把MMIO写当硬件运行证明。SDK候选若局部对应需明确来源/差异，不能代ROM。正常停机通知负搜索/计时单位/所有驱动不在本题。

先已有→行为→局限→实际缺口，四分类报告，只补必要原字节，不重复整函数/全资源/源码复制/机械哈希账；无增量及时覆盖交付由主窗口补位，不凑函数时长。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/网络。必要验证后独占提交，报告commit/验证/未知/clean结束。

## 当前完整任务书 A38（已启动，基线beb2b7a）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a38；分支codex/re-0041-a38；基线为本任务书提交。独占reverse/reports/ap01/image-cache-key-a38-0041-20261024.md及reverse/analysis/image-cache-key-a38-0041-20261024/。

A34/A36明确cache+10 comparator全部key等价语义尚未认证；lookup a00eb9c0头快路径用(payload,key)，后由a00ea832(cache+24,key)查树。本题仅恢复同image-cache比较器实际安装身份、source/class字段/宽度/返回、头快路径与树查询使用相同匹配合同，及已知PNG normal key协议。先查A23初始化/A27/A30/A34和旧complete/较晚round3，已留key布局/计量/排序/cleanup直接引用；只补未核比较接入，不扩平衡树全集，不凭名字假定字符串/指针比较，不研究任意重复insert或异常状态。

先已有→行为→局限→实际缺口，四分类报告，只补必要原字节，旧结论复核不算新增。若已覆盖及时引用结束由管理者补位，不凑时长/函数，不重复整函数/源码/资源/哈希机械账。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网。必要验证后独占提交，报告commit/验证/未知/clean结束。

## 当前完整任务书 E14（已启动，基线beb2b7a）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e14；分支codex/re-0041-e14；基线为本任务书提交。独占reverse/reports/ap01/uv-timer-deadline-e14-0041-20261024.md及reverse/analysis/uv-timer-deadline-e14-0041-20261024/。

F01/F02保留a009d146 start中a009d18c字节7715aac0与a009d1bc字节7716c5c0厂商64位算术UNKNOWN，未认证正常deadline/到期算术。本题先核较晚round3及ap01thead3现有条款/留存是否已解释，直接继承修复不重记；仅补这些不可信窗口的寄存器对/宽度/符号/回写及正常期限设置→a009d304到期消费的参数/比较合同。已有start flags/heap登记/repeat/活动计数、callback kind0..6与close walker全部继承，不再扫提交者/销毁，不恢复整个heap，不改/运行模型，不做异常/溢出输入测试。

先已有→行为→局限→实际缺口，四分类报告，只补必要原字节，旧结论复核不算新增。若已覆盖及时引用结束由管理者补位，不凑时长/函数，不重复整函数/源码/资源/哈希机械账。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网。必要验证后独占提交，报告commit/验证/未知/clean结束。

## 当前完整任务书 A39（已启动，基线db28e99）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a39；分支codex/re-0041-a39；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/photo-decoder-review-a39-0041-20261024.md及reverse/analysis/photo-decoder-review-a39-0041-20261024/。

新agent独立复核A37 a010a65a正常对象分配/0x664 W→O状态复制、O+c保留ROM输入指针、0x4664+5N分配与内嵌派生区、O经a0107dea返回到owner+5c与owner+74接入。A33/A35 source ABI及五资源/A29 cache失效合同全继承，不重导setter/整decoder。保持状态块复制与payload字节克隆不同；O最终析构/+74撤销、输入上界/格式版本/0x4000用途仍精确未知，不扩解码算法或执行资源。

先已有→行为→局限→精确缺口，四分类报告；独立复核新增功能0，可靠合同引用，只补必要原字节，不重复整函数/源码/资源导出或机械账。无增量及时交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 G13（已启动，基线db28e99）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g13；分支codex/re-0041-g13；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/display-device-poll-g13-0041-20261024.md及reverse/analysis/display-device-poll-g13-0041-20261024/。

G11/G12已闭a003e674(fd,node+14,1)→a003e344登记与a0109b8e通知flag，但设备实际写node+1c/revents未闭。只沿同一显示poll fd的构造/对象ops定位一个具体设备poll方法及其正常revents写入/已安装callback接入。先复用G07/G09/G11、F05/F07及旧initializer真实fd来源与retained ops，不能把backend_fd当目标设备fd或把返回>=0当ready。已闭注册/materializer/consumer直接引用不重导；若设备不能唯一静态定位给候选/精确间接边，不扩所有VFS/设备/IRQ/网络或运行时驱动实验。

先已有→行为→局限→精确缺口，四分类报告；独立复核新增功能0，可靠合同引用，只补必要原字节，不重复整函数/源码/资源导出或机械账。无增量及时交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 当前完整任务书 H13（已启动，基线bdc139a）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h13；分支codex/re-0041-h13；基线为启动时最新整合任务书提交。独占reverse/reports/ap01/weather-clock-abi-h13-0041-20261024.md及reverse/analysis/weather-clock-abi-h13-0041-20261024/。

weather-dataflow与后继weather-location-request均明确a00a9d1e时钟helper的厂商字0xa4e91577、参数0、两次除1000未认证，URL时间按a0/a1传%lld已有合同。本题只补时钟helper正常source调用→64位算术→返回对→已有签名/URL接入的宽度/符号/单位可证范围；先查较晚round3/原字节/现有thead3条款与旧完整阶段，不把旧UNKNOWN当较晚仍未知。E14只追uv timer deadline，不能将其时钟来源/epoch套用此helper；来源/epoch若无证保持未知，不重做URL/摘要/分类/天气显示，不执行网络或时间回放。

先已有→行为→局限→精确缺口，四分类报告；独立复核新增功能0，可靠合同引用，只补必要原字节，不重复整函数/源码/资源导出或机械账。无增量及时交付主窗口补位，不凑时长/函数。共同静态/安全/隔离规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证独占提交报告commit/验证/未知/clean。

## 预备完整任务书 A40（待A38正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a40；分支codex/re-0041-a40；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/image-cache-key-review-a40-0041-20261024.md及reverse/analysis/image-cache-key-review-a40-0041-20261024/。

独立复核默认cache+10/tree+4 comparator安装、source/class宽度与class0 unsigned地址/class1字节比较符号归一及头快路径(payload,key)/树(key,payload)的零等价合同；其他同类值原返回0须保持。A23/A27/A30/A34排序/计量/cleanup直接引用，不扩树算法/动态槽或重复insert。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 预备完整任务书 A41（待A39正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-a41；分支codex/re-0041-a41；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/photo-decoder-destroy-a41-0041-20261024.md及reverse/analysis/photo-decoder-destroy-a41-0041-20261024/。

A37/A39已闭O构造/原ROM输入持有→owner+5c/+74；本题只补已知setter a00ed7f4正常旧O替换/析构及派生+74撤销连接。先查旧photo/完整阶段/较晚round3和A33/A37 retained调用，沿真实owner+5c旧值的直接callee核对象/内部派生缓冲/原输入的归还原序，原ROM输入是借用不能编造free。无实际callee种子有界交付，不扩GIF/PNG算法/所有控件销毁。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 预备完整任务书 D16（待D15正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-d16；分支codex/re-0041-d16；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/pwm-arithmetic-review-d16-0041-20261024.md及reverse/analysis/pwm-arithmetic-review-d16-0041-20261024/。

独立复核D15真正新增freq/duty分频阈值、三个软浮点helper ABI、32位MULA/移位/PKBB16、80,000,000.0常量与正常寄存器/缓存写顺序。buzzer旧映射/upper/stop/shutdown合同继承，不做异常/波形/设备运行，不改模型；库来源与厂商硬件实测边保留。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 预备完整任务书 E15（待E14正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-e15；分支codex/re-0041-e15；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/uv-timer-review-e15-0041-20261024.md及reverse/analysis/uv-timer-review-e15-0041-20261024/。

独立复核E14正常deadline/到期比较的寄存器对、ADD64既有位域规则与回写/unsigned比较；旧模型规则不是本轮新增，F01/F02 callback/heap/flags/计数/销毁合同全继承，只核正式报告真正补充窗口，不运行或修改分析器模型/历史回放。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 预备完整任务书 G14（待G13正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-g14；分支codex/re-0041-g14；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/display-device-poll-review-g14-0041-20261024.md及reverse/analysis/display-device-poll-review-g14-0041-20261024/。

独立复核G13实际目标fd/设备ops身份、一个设备poll/revents写者到已安装通知callback的新增接入或精确间接断边。G07/G09/G11/G12 registration/materializer/consumer原序全继承；不能由登记成功/静态指针推实际ready，不扩其他设备/IRQ/全部VFS。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。

## 预备完整任务书 H14（待H13正式报告整合，不计运行）

树D:/CodexHome/visualizations/2026/10/23/01a1691a-e178-7710-86c0-84c2ff2d3dfb/re0041-h14；分支codex/re-0041-h14；基线为启动时最新整合任务书提交，届时记录SHA，不提前建旧基线树。独占reverse/reports/ap01/weather-clock-review-h14-0041-20261024.md及reverse/analysis/weather-clock-review-h14-0041-20261024/。

独立复核H13正常时钟helper调用/原厂商字、两次除1000与64位返回/URL%lld接入单位可证范围；旧条款/较晚反编译与URL摘要合同继承，不套用E14 uv deadline时钟源/epoch，不推实际外网请求或时间回放。

正式报告后据其继承/真正新增/未知清单收缩，先已有→精确缺口，四分类报告。独立复核新增功能0，仅必要旧字节/源行锚点，不重复整函数/资源源码复制/机械账；研究无增量及时覆盖交付主窗口换题补位，不凑时长函数。共同静态/安全/隔离/独占规则适用，不创建下级agent、不改主树共享/生产ROM配置模型，无SIM/构建/历史回放/设备/外网；必要验证后独占提交报告commit/验证/未知/clean。
