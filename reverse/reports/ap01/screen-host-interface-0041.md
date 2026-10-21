# 0041 屏幕宿主接口收敛稿

日期：2026-10-20；状态：已有共享核心、0041适配和codex_status接入；公共C结构见 `tooling/firmware-modules/screen_host_0041.h` / `screen_port_0041.h`。ABI v1仍为未部署的实验接口。依据：[追加验证](screen-host-append-validation-20261020.md)、[codex_status基线](codex-status-host-baseline-20261020.md)。本文件的动态屏幕集与调度语义取代最初架构文档中的静态注册草案；C头文件及错误值已经实现。

## 1. 所有权与容量

- 宿主拥有win挂钩、原厂条件门控、root/tag、动画、输入焦点及UI节拍；应用拥有业务状态、模板、数据合同与渲染。ROM地址仅在0041适配层出现。
- 静态应用清单声明唯一 `app_id` 与 `screen_capacity`。codex_status容量8，对应最多8模板；另一个应用的容量单独声明。宿主预算是这些容量之和，不再将“全部应用最多8屏”和“单应用8模板”混为一谈。配置须在链接/内存预算验收中有明确上限，容量不足在安装前拒绝，不裁剪页面。
- UI初始化为清单分配有界root池；不预分配逐屏完整帧。同一窗口代次内每个已分配root始终留在win内，退出/隐藏/替换屏幕集均不删除、不重排root。整窗口销毁会解除绑定；新代次从已确认Bundle重新建立root映射，不复用旧窗口裸指针。slot是应用池内句柄，不是原厂child索引；适配层维护实际映射。
- 原厂0..8及其对象指针保持不变。root固定320×240、x由宿主控制、初始x=320；消除布局/滚动干扰，并使用有效、清零的20字节兼容tag块。应用只操作root内部对象。
- 注册描述符被宿主复制，`screen_id`为稳定标识，非模板下标；app上下文和API必须长期有效。通过C不透明句柄传递对象，不将SIM的LVGL类型布局直接当作原厂ABI。

## 2. 最小接口及调用上下文

以下为操作合同；实际导出名与字段以C头文件为准。首个实现将 `on_create/on_will_enter` 收敛为可返回READY/PENDING/FAILED的 `prepare`，按需创建应用控件；解除绑定用 `unbind`。每应用 `poll` 按50ms消费关键队列；可选慢tick由应用在poll内按时间与活动状态分频，不另增加一套定时器。不新增插件加载协议。

| 接口/回调 | 合同 |
| --- | --- |
| 应用初始化 `(app_api, app_ctx)` | 清单驱动、挂钩线程执行，给出绑定本应用身份的API/context；不能只靠外部传入app_id冒充归属 |
| `replace_screen_set(expected_revision, screens, count)` | UI线程执行；一次替换本应用逻辑屏幕集，count可为0..capacity；返回OK并递增应用revision，或返回明确错误。校验重复ID、结构/ABI版本、visible、必需回调和容量；忙时返回BUSY，调用方保留待提交数据 |
| `find_screen()` / 应用revision | UI线程查询当前ID映射与revision；不重放Bundle安装。当前为进程内可信C接口，不提供隔离沙箱 |
| `prepare` / `unbind` | prepare按需创建应用控件；屏幕退役、删除、上下文更换或宿主销毁时unbind解除资源引用。root/tag由0041适配层持有；整窗口销毁/重建已由[原厂构造重放](screen-host-lifecycle-20261020.md)验证，跨窗口需重新绑定root |
| `prepare(ctx, slot, transition_id)` | 在UI线程请求目标准备，返回READY/PENDING/FAILED；准备完成前不启动动画、不释放源帧。PENDING后业务线程准备帧，UI通过50ms轮询消费，用原transition_id报告完成；过期结果丢弃。当前准备期限10秒，包含队列前方最长5秒HTTP处理 |
| `enter_ready(transition_id, result)` | UI线程回报准备结果，宿主核对目标ID、set revision与可见性；FAILED保留原显示，恢复应用激活状态按既有业务失败语义处理 |
| `entered` / `left` | 动画实际完成且目标仍匹配时派发，每次事务至多一次；不作为业务displayed确认。源屏直到完成前仍有可绘制内容 |
| `input(ctx, slot, event)` | 只对当前屏派发；浏览态短按可请求焦点锁；锁定态旋钮/短按由应用处理并可解锁。未知返回值保持已有安全状态 |
| `poll(app_ctx, now_ms)` | 每应用一次，沿用50ms UI节拍，即使页面隐藏/动画中也消费present/retire和准备结果；不等待业务锁。一个应用有8屏也不重复消费8次队列 |
| 应用业务执行器 | codex_status沿用现有业务线程处理激活、重绘与业务刷新；UI只发送有界请求、消费已准备帧，不同步执行模板激活/HTTP |
| `request_switch_to(screen_id)` | 应用专属API校验本应用归属，UI线程、顶层浏览态、动画/准备空闲；方向1=PREV、2=NEXT，不暴露原厂key值。后台仅更新应用队列 |

不保留 `priority` 或通用flags扩展行为：顺序固定为清单应用顺序、各自screen-set顺序。struct_bytes/ABI版本用于兼容检查，当前没有扩展保留字段。初期不提供热卸载、运行时下载或任意应用可切他人页面。

## 3. screen-set替换与Bundle提交

静态 `register_screen()` 不足以接纳现有Bundle运行时增删/重排，采用一个有界的应用级替换操作：

1. 复用现有Bundle预检、事务ID、单份安装与UI `retire` 屏障；提前验证新模板数/ID可放入本应用池。用户原厂页/应用页、稳定模板ID和输入修订号在退役前记录。
2. UI收到退役请求即解除旧图像引用并确认，之后业务才释放旧Bundle/字体。该确认即使隐藏也必须进行；`on_ui_poll`不能等待持有Bundle安装锁的业务线程。
3. 安装结果明确后，UI空闲时验证并提交新set；同ID保留root，新ID复用空root，删除项解除绑定。逻辑顺序独立于物理child顺序。校验失败不改旧set；若旧Bundle已被替换或退役，则旧set仅保留身份信息，禁止调用旧上下文，保持内置恢复页并报告失败。
4. Bundle提交结果未知先查询原事务。不得把未确定的Bundle暴露成新screen-set，也不新增第二套持久提交记录；set从已确认Bundle重建。重启/损坏继续沿现有恢复逻辑。
5. 只有原来在模板页、原ID仍有效或已按原规则回退新initial ID、期间无显式输入且无维护/配对抢占时才自动返回。原厂页发布不抢焦点。真实输入增加修订号并取消恢复意图。

初期准备/动画期间返回BUSY，不排队多次切换；准备必须有限期限，超时释放目标临时资源并保持源页。系统主动进入屏保/维护或UI销毁时取消transition，旧完成通知不得重新抢焦点。

## 4. 图像与渲染

保留 `Ap01Business`、`Ap01Application`、CompiledTemplate/Bundle和共享I4渲染引擎。迁移重点是 `Runtime` 的ROM挂钩/导航/图像适配，不能把既有模板改写成一套label布局。

受限LVGL表从实际需求起步：普通对象/标签、样式，加上**I4图像sink**（创建、提交不可变descriptor与像素、实际draw通知、解除引用/退役）。ROM端复用 `native_0041.cpp` 的image cache失效及I4描述符适配，SIM端复用 `src/ap01_template_lvgl.h`。准确C签名仍须逐一核对原件，尤其草案字体/样式包装函数的selector参数不能凭LVGL上游名称补齐。

每个模板最终有自己的root；完整帧按需保留。普通稳定显示沿用单帧，动画期间源/目标需各自有效的不可变帧和独立descriptor，完成后才退役源帧。两帧相对单帧至少增加38400B像素+64B调色板，另计descriptor、解码、渲染工作区和队列峰值；不得将该下界当完整RAM预算。8个root不表示8份常驻全帧，也不能复用同一可变descriptor让旧页在动画中变成新页。

目标模板激活继续使用既有单active context语义；源仅保存已绘制快照，不创建第二套活跃业务context。准备失败、安装并发和异步帧generation不匹配需要定向测试，不能只检查目标已选中。

`displayed`仍来自实际图像draw，核对当前generation、当前模板、可见性及系统优先级。`on_did_enter`、成功提交图像和数据ACK均不能替代。保留 `waiting_for_template_page` / `waiting_for_draw` / `screen_not_visible` / `pairing_dialog` / `maintenance_active`。

## 5. 输入和服务

主浏览环明确为 Pet ↔ 各应用逻辑屏幕 ↔ Settings。宿主接管这两条边及外部页；其余页面仍走原厂有条件的有向边，沿用33修复，不用数字递减判断环回。进入Settings复用原厂日期/设置刷新准备；离开Pet暂停GIF，进入Pet完成后保留原厂resume。

区分三种状态：宿主当前screen、应用模板active context、FOCUS_LOCKED。不能直接把旧 `Runtime::focused` 当输入锁。锁定3秒先解锁、后通知应用，一次按住只触发一次，释放不补短按；仅在UI线程可运行时成立。

维护、配对、唤醒/原厂弹窗优先于屏幕输入。UI仲裁属于宿主，绑定/owner/token/C2业务语义继续由原服务处理。保留现有18080维护、18081业务、8767发现及“先维护/发现、后恢复业务Bundle”的次序；同一阶段只有一个维护监听器和一个Flash执行器。将实现归属迁到本仓库时逐项提取，不另启动一套同端口服务。坏Bundle、0屏或screen创建失败不能关闭维护。

## 6. 分批落地界限

可先以单宿主screen承载既有8模板验证接口提取；这只是过渡，不算独占root目标完成。最终验收必须覆盖8模板各自root、另一应用共存、逻辑重排与稳定ID映射、两帧真实滑动、发布/删除/恢复、真实draw回执和系统抢占。

当前C实现已经定义结构尺寸检查与错误码。root创建使用可检查失败的class-create/init叶调用，失败逆序撤销追加，并检查原厂0..8指针不变；准备超时前先废弃旧token。UI销毁后拒收新帧并保留独立维护执行器。顺序销毁/重建、原执行器复用、旧epoch帧与旧revision拒绝已有[离线证据](screen-host-lifecycle-20261020.md)；实机峰值与LCD/SPI完成仍未证明；不将实验ABI标为已部署稳定接口。
