# F07：显示闭包的本地 LVGL 来源识别与版本差异

2026-10-23；分支 `codex/re-0041-f07`，基线 `f22ec27834ce88b3a18d1417677ad79c78322c08`。本轮是来源比对，待新 agent 独立复核。

**本地候选确实自报 LVGL 9.2.1，所选 13 个源码文件与本地现存 v9.2.1.zip 对应成员逐字节相等；但 ROM 的显示事件闭包不是这个候选的未修改实现。** 最强不一致是 DELETE 枚举 `ROM 0x29` / `候选 0x26`、ROM 的 event-list 重入状态与 bit16 descriptor 门在候选中不存在、以及显示 layer 默认初始化行为不同。可识别显示删除、双阶段 sender、NuttX 后端 DELETE callback 的来源家族与具体候选函数；不能据此认证 ROM 为 9.2.1、把差异归因于厂商而非其他上游版本，或排除整个 LVGL 库。

F05/F06 的 ROM 合同继续有效，包括 F06 的 `filter & 0xffff7fff` 纠正。本报告不重做 `+2b8` 普通 SW 扫描，不建立新非 NULL 安装者，不恢复 MiIO loop 后继。

## 路径、包与只读访问边界

明确候选根为 WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim`，以下 `S` **仅作为本文路径缩写**，实际绝对根是 `/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`；证据 JSON 每项保存完整绝对路径。`S/src/display/lv_display.c`、`S/src/drivers/nuttx/lv_nuttx_entry.c` 真实存在。未到其他根搜索版本。地址、字段偏移和未另标十进制的机器常量均以十六进制书写；文件行号、条目数为十进制。

来源依据保存在 [source-evidence.json](../../analysis/display-source-auth-f07-0041-20261023/source-evidence.json)：

- apps HEAD 为 `8ff533beb37eeef1f288c467acd7c50b542464eb`；NuttX HEAD 为 `6fc5b3e9dc51dcda46d99519f72b7f2ec6db2e64`，与历史交接记录一致。NuttX 12.10 在本轮仍只是历史候选标签；没有由其反推 ROM 系统版本。
- `S/lv_version.h:8..11` 为 major 9、minor 2、patch 1、info 空串。`/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/Makefile:59..78` 的默认 URL 指向 GitHub tag archive，`LVGL_VERSION=9.2.1`、`LVGL_TARBALL=v9.2.1.zip`、解包目录 lvgl。只读取该文本，未访问 URL、执行 Makefile 或下载。
- LVGL 解包目录无 `.git`；apps 的 `graphics/lvgl/.gitignore:1` 忽略 `/lvgl`，`git ls-files graphics/lvgl` 只列包集成文件。因此 **apps commit 不能认证解包源码未修改**。选定 Makefile/.gitignore 无相对 HEAD 的工作区 diff；apps 工作区有其他 SIM demo 修改，未修改、恢复或复制它们。
- 本地包绝对路径 `/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/v9.2.1.zip` 已存在。只读打开其 `lvgl-9.2.1/<相对路径>` 成员，与实际候选文件 bytes 比较：13/13 相等。所选包括 version、display.c/private.h、ll.c/h、event.c/private.h/h、array.h、types.h、entry.c、fbdev.c、draw.h。未解包到参考树、未新建 hash 清单。包文件名/内容一致性不证明该 zip 从何获得、未被同时修改或经过上游签名认证；没有声称完成整包/整树认证。

默认 sandbox 下 `wsl.exe` 首次读取返回 `Wsl/E_ACCESSDENIED`；明确 UNC 根访问返回路径不存在。按已授权本地根以 `require_escalated` 重试只读命令成功；这是 host sandbox 访问边界，不是候选不存在或权限损坏的证明。没有修权限、安装软件或改参考树。未启动 SIM/QEMU/固件、服务或设备连接，没有构建、联网、历史回放或共享 REA target 切换。使用 REA 技能的事实/推断/未知与原字节核验方法；本轮复用保留 ROM 指令，不生成虚构 REA Evidence ID。

## 逐函数/必要片段映射

分类含义：**候选相符**仅指表内已比对的合同；**可识别但版本未知**指多项结构/顺序支持该来源身份，却不足以证明具体版本/原文件未改；**差异/封装保留**指候选不能直接替代 ROM。没有任何一行达到“确证 ROM 未改、可排除继续恢复”的等级。

| ROM 核心或片段 | 精确候选位置 | 调用、布局、返回、所有权比对 | 裁定 |
| --- | --- | --- | --- |
| `a005cc1e` 的 cc9c..ccc6 配置/caller | `S/src/drivers/nuttx/lv_nuttx_entry.c:96..110`，`lv_nuttx_dsc_init` / `lv_nuttx_init` | 清配置后默认 `/dev/fb0`、`/dev/input0`，再以 `(config,result*)` 初始化，result 第一个槽接显示。字符串、参数顺序与发布连接共同支持，不能仅凭字符串作认证；ROM caller 还含独立业务。 | 候选配置合同相符；caller 封装保留 |
| `a0084b96` 大容器的 4d9a..4e7e 创建片段 | `S/src/display/lv_display.c:62..89` `lv_display_create`，及 `S/src/drivers/nuttx/lv_nuttx_fbdev.c:75..90` | 候选 fbdev create 先分配 backend，调用 display_create(800,480)，失败释放 backend；display_create 插头、失败返回 NULL、清显示、填分辨率、分 layer、条件 layer_init。ROM 对象清0x324、分 layer0x58并写+2b0，条件+2b4 `(obj,layer)` 相符于这段关系；但 layer 初始化有下述实际差异。ROM大容器并非已证明与候选某一个源码函数边界相等，可能含内联/封装。 | 来源可识别，版本未知；初始化差异保留 |
| `a008aec0` list 分配插头 | `S/src/misc/lv_ll.c:16..18,57..78` `lv_ll_ins_head`；`lv_ll.h:31..35` | ROM alloc(size+8)，NULL直返；非NULL先 prev=NULL、next=旧head、更新旧head.prev，再 head，新list时 tail，返回新节点。候选相同；RV32两指针8B及 n_size/head/tail 三word布局相合。未展开每个 list helper 源-ROM逐指令认证。 | 候选相符；不能凭通用插链算法认证具体版本 |
| `a00873ea` out 发布必要片段（不是独立函数入口） | `S/src/drivers/nuttx/lv_nuttx_entry.c:134..159` `lv_nuttx_init` | 候选 fbdev_set_file 非零则 delete、disp=NULL，再可选 result->disp=disp；其后才 touchscreen/result->indev。ROM s7保存out、73ea `[s7]=s1`，之后输入初始化，支持发布来源；本轮未核大容器全部失败转移，不能认证候选的所有失败分支在ROM一模一样。 | 候选发布合同相符；失败全貌/容器封装未认证 |
| `a007ffa0` 注册适配 | `S/src/display/lv_display.c:734..739` `lv_display_add_event_cb` | `(disp,cb,filter,userdata)` 变为 `(&disp->event_list,cb,filter,userdata)`；ROM +2e8，直接到a01b93b4。候选 void 返回；ROM wrapper 的寄存器残留不升级为业务返回。字段绝对偏移仍由ROM合同决定。 | 可识别但版本未知 |
| `a01b93b4` descriptor 分配/追加 | `S/src/misc/lv_event.c:88..105` `lv_event_add`，`lv_event_private.h:27..31` | RV32 descriptor12B：cb@0、userdata@4、filter@8；保存顺序 cb/filter/userdata，零size时初始capacity1、element_size4，再push pointer、返回descriptor均相合。ROM array还写+10 byte，dispatcher另用list+14状态，候选四word array无这些成员。两边断言失败处理不被改写为“malloc失败正常NULL返回”。 | descriptor合同相符；list结构/事件维护差异保留 |
| `a00814f4` sender | `S/src/display/lv_display.c:780..797` `lv_display_send_event`；`lv_event_private.h:33..43`；`lv_types.h:55..57` | 清28B event；两target、code、userdata、param、prev、flags 的RV32布局相合。先true后false；只有返回 `LV_RESULT_OK=1` 才第二阶段；最终返回dispatcher结果。ROM DELETE code=29而候选DELETE=26，不能用候选枚举替换ROM常量。 | sender控制/ABI候选相符，枚举版本差异保留 |
| `a008acfa` dispatcher | `S/src/misc/lv_event.c:63..85` `lv_event_send` | bit15 phase、mask仅清bit15、ALL0/code比较、先写event.userdata再重读cb以 `(event*)` call、callback返回不用、flags bit1停止处理和bit0删除具有共同骨架；ROM额外entry/迭代deleted门、bit16跳过、list快照及重入维护，候选没有。不可静默省略这些分支。 | 明确不是未改本地9.2.1；实际来源版本/修改者未知 |
| `a007fe32` backend getter | `S/src/display/lv_display.c:927..933` `lv_display_get_driver_data` | NULL disp才取默认，仍NULL返回NULL，否则读driver_data；ROM读+2e0。调用者以此取得backend，支持字段语义。未证完整candidate私有结构偏移一致。 | 候选getter合同相符，可识别但版本未知 |
| `a00800b4` 已装DELETE callback | `S/src/drivers/nuttx/lv_nuttx_fbdev.c:383..405` `display_release_cb`；注册:75..90 | event.userdata→disp→driver_data；非NULL先清driver_data和另一显示hook；signed fd>=0 close并写-1；offscreen资源非NULL用系统free后清槽；再lv_free backend；日志Done。ROM严格相同资源顺序/双allocator分工，resource@34因此支持 **候选 offscreen buffer** 解释，不能硬称mmap framebuffer。具体显示hook偏移有下述不一致；底层close/free成功不由静态调用证明。 | 后端适配来源高度可识别；版本/字段差异未认证 |
| `a0081554` 删除闭包 | `S/src/display/lv_display.c:158..212` `lv_display_delete`；private.h:114..149 | 保存default/refr身份→DELETE→remove_all→detach indevs→sys/top/bottom、act清零、逐screen删除→sync list清理→显示list摘链→可选refr_timer删除→可选layer_deinit(disp,layer_head)→重读layer_head归还→free disp→更新default/refr。与F06原顺序逐项相合；候选使+2b0/+2b4/+2b8分别可解释为layer_head/layer_init/layer_deinit，但绝对结构和版本不一致，尚非精确字段源码认证。 | 删除顺序/所有权可识别，版本未知；callee及安装断边保留 |

表内多个候选函数对应一个ROM大容器片段时，不把“边界不同”单独当厂商修改证据；编译内联足以造成此现象。ROM底层allocator、fd层、全部显示资源callee与事件维护helper仍未恢复/未认证，不能借本表排除。

## 不能被编译优化消掉的差异与 ABI 限定

1. **事件编号不同。** 本轮从候选 `lv_event.h:35..112` 枚举起点ALL=0逐项计数，DELETE=38/0x26，REFR_REQUEST=53/0x35；ROM `a0081570 93059002` 装0x29，backend注册6cca亦0x29（F05/F06）。枚举取值本身不是RV32/64位、enum宽度或内联造成。这里仍称 ROM 的0x29为DELETE，依据是实际显示删除路径/注册业务，而非拿候选枚举反向标注。尤其不能顺手把ROM所有0x35/0x38按此9.2.1头文件定名。
2. **事件维护有额外状态。** 候选 `lv_event_list_t` 直接 typedef `lv_array_t`（event.h:116），array.h:35..40仅data/size/capacity/element_size，普通RV32为16字节且无条件字段。ROM ad26传0x14作快照长度、ad32/ad48读写list+14，a01b9456写list+10；这些超出候选的结构。ROM ad72/ad76以0x10000测试filter并跳过，候选event_send只有cbNULL、phase及code检查。ROM entry ad16..1e及每轮ad56..5c预先查deleted；候选仅callback后查。来源可能是其他上游版本或厂商改造，当前无法二选一，故标 **相对候选的实际差异**，不虚称厂商已改某行。
3. **layer构造默认不同。** 候选display.c:80只malloc_zeroed(sizeof(lv_layer_t))，成功后紧接条件layer_init；ROM分0x58、经a00819d0→a0081978，除清零外在条件+2b4之前写layer+38 word=ff、+3c byte=0。候选draw.h:70..108的layer定义和这段create没有对应额外默认调用。不能只用“也是分配layer”认证未修改；本轮不推算所有可配置结构的实际sizeof，也没有构建验证。
4. **早期显示hook布局未相同。** 候选private.h中七个32位resolution/dpi成员后依次buf_1、buf_2、buf_act、flush_cb、flush_wait_cb；普通RV32指针4B且此段无条件项，flush_cb为+28、flush_wait_cb为+2c。候选release_cb清的是flush_cb，ROM清的是+2c（00e2），不能直接把ROM+2c宣布为已认证候选flush_cb。后段偏移还受enum/bitfield packing、LV_INV_BUF_SIZE、draw buffer和其他条件字段影响；禁止拿本地x86-64 SIM sizeof去反证ROM配置。getter+2e0、event_list+2e8等仍以ROM为准。

F06已纠正的mask这里与候选表达完全相容：候选 `filter & ~LV_EVENT_PREPROCESS`，PREPROCESS=0x8000，uint32 filter结果为0xffff7fff；不是“低15位”。ROM `ad42 e17a`、`ad50 fd1a`、`ad80 b3f75701` 对应同一常量。此项匹配不能抹去额外bit16门与list维护差异。

## 生命周期与来源能解释到哪里

这是源-ROM映射说明，不是参考实现：`display_list → display → layer_head`；显示另持backend，event list持descriptor，descriptor.userdata借用display。sender的28B event在栈上同步传给callback；backend callback先解除显示关联，再请求fd、offscreen候选资源和backend归还；返回display_delete后才清其他显示资源，最终先可选layer_deinit，再重读layer_head归还，再归还display，最后更新保存的全局显示引用。所有顺序、原重读、word/byte宽度和close signed门沿用F06，不擅自重排。

由源码可提出更准确的 **候选语义**：F05/F06的payload/optional_delete_cb在这一有界删除序列中分别对应layer_head/layer_deinit；init_cb对应layer_init。它不是已装 `display_release_cb`：后者走event descriptor `(event*)`，layer_deinit走 `(disp,layer*)`。也不因此发现了ROM非NULL +2b8安装或MiIO loop连接。候选源码里存在同名槽不证明ROM运行时调用它，更不能证明其返回后字段未变；F06的返回后layer pointer重读必须保留。

backend+34的候选名mem_off_screen有具体free而非munmap的生命周期证据；本轮只提高来源解释，不证明ROM该指针的完整生产、分配长度、实际framebuffer映射或物理释放。源码set_file的其他生产和errout分支未在本轮逐指令复核，保留断边。

## 实际验证与可复用结论

[capture.py](../../analysis/display-source-auth-f07-0041-20261023/capture.py) 通过wsl.exe运行只读Python读取上述明确文件、Git元数据和本地zip成员，仅将有行号的选定片段及比较布尔值保存到本worktree。没有为交付复制整份大源码树，也没有包/ROM hash清单。[verify.py](../../analysis/display-source-auth-f07-0041-20261023/verify.py) 直接读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，按 `VA-0x9ffff000` 核F06全部选定指令raw与ROM一致，再核20个本轮来源比较锚点；不是重新反编译/执行F06脚本或固件。[validation.json](../../analysis/display-source-auth-f07-0041-20261023/validation.json) 保存小锚点和边界，不重复整套汇编。

实际结果：**PASS 694条复用F06指令raw匹配、20个源比对锚点、13/13本地包成员字节相等**。其“694”是按F06窗口遍历的条目数，不宣称694个互不重叠新指令。原始指令与厂商字语义认证仍引用F06及其只读本地模型边界；本轮不冒称独立重证全ISA。F05/F06入口保留Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3` 只作既存线索，本轮未增加REA Evidence。提交前检查差异、独占路径和 `git diff --check`。

**事实**：读取到的路径/Git/header/package元数据、13成员相等、ROM原bytes、候选源码分支与布局、枚举差异。**推断**：上述LVGL/NuttX来源家族与layer/offscreen等候选语义识别。**未知**：ROM精确版本/commit、相对另一上游版本是否仍有厂商修改、完整编译配置与结构布局、未展开callee、layer_deinit真实安装/运行值、backend+34生产、上层loop/9428连接。

可复用认证范围仅为“本地候选13文件与本地9.2.1包成员相同 + 表列合同匹配/不匹配”；**没有“确证ROM未改可排除”项**。不得据此整库排除图像、事件、显示或NuttX适配，更不能用候选源替换ROM差异和失败路径。

一个后继闭包：新agent独立复核本报告的包成员/版本证据、DELETE枚举、event-list结构及bit16/deleted门差异，再审layer_deinit候选命名是否只限定在本删除序列；不扩版本搜索、不编译、不重扫+2b8。管理者可据该独立复核决定今后哪些接口名可作来源别名，实际ROM事件维护与非NULL槽安装仍另列未恢复。
