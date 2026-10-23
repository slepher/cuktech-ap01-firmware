# F08：本地 LVGL 候选、包成员与源-ROM差异独立复核

2026-10-23；新 agent，分支 `codex/re-0041-f08`，基线 `a241a601057368db225c58df4ea65c9a36843aaf`。**有精度纠正后限定接受 F07 的来源映射和“不认证 ROM 为未改 9.2.1”结论；确证 ROM 未改、可排除继续恢复的项目数仍为 0。** 本地候选 13 文件与本地 zip 对应成员相等得到独立复核，DELETE 编号、事件维护和早期 hook 布局差异成立。来源家族识别与精确版本/未改认证严格分开。

精度纠正：不得把“候选 event-list 16 B 对 ROM 20 B”写成完整结构大小比较。ROM `ad26` 的 `0x14` 是**被拷贝的 array 前缀快照长度**，另有 `list+0x14` 状态读写；该字段已经位于此 20 B 前缀之后。F07 正文原已称快照长度，未明确宣称完整 sizeof=20；本报告将任务书/摘要中的尺寸简称收紧，并把 F07“array 还写+10、list另有+14”的关系显式化。ROM 整个 list 的精确 sizeof/填充仍未认证，不能由快照长度推出。候选版本行号也精确为 `lv_version.h:9..12`。

## 旧成果复用对照与本轮增量

任务进行中管理转达用户新增复用要求。本轮随即只读追溯指定旧报告及最终归档，保留已完成复核，不扩源码/版本或重复整份导出。[reuse_check.py](../../analysis/display-source-review-f08-0041-20261023/reuse_check.py) 与 [reuse-review.json](../../analysis/display-source-review-f08-0041-20261023/reuse-review.json) 只保存检索边界、少量来源标记及命中/未命中；zip没有执行或解包到文件系统。

| 已有出处 | 可复用行为或来源信息 | 局限与本题剩余增量 |
| --- | --- | --- |
| `reverse/reports/ap01/application-rehost-complete-0041-20261017.md:27,35,39,41` | 明确宿主SIM/服务替代、宿主ELF、LVGL9.2.1 GIF适配、固定NuttX/apps提交。 | 这是SIM实现/验收层，不能认证ROM显示enum/list/布局。F07已据本地候选做认证，本轮仅独立校核其结论。 |
| `reverse/reports/ap01/application-function-matrix-0041.json` | scope明确GUI/service在NuttX SIM，业务features与证据路径保留；旧 `artifacts/ap01-research/rehost-20261016/system-complete-0041.json` 已按basename定位主树 `reverse/rehost/system-complete-0041.json`。 | 在该矩阵全文未检到本题六个核心地址/三类源码basename，不把SIM业务throughput当ROM库版本认证。 |
| `reverse/reports/ap01/factory-reference-map-0041-20261020.md:5..20` 及 `reverse/analysis/factory-reference-map-0041.json` | 既有离线REA/Ghidra索引；明确SIM家族通过≠原函数完成、完整C文件认证数0。 | 索引/报告中本题精确项未检到，不能用负结果声称历史从未分析或函数不存在。 |
| 主树 `reverse/rehost/system-complete-0041.json` | source/base与旧缓存来源明确；cached_evidence键为 `main_a00afc88`、`settings_a00fd1ac`、`charge_a00f61ae`、`source_note`；另有local_disassembly。 | 属旧反编译/原字节业务证据混合及SIM替代边界，不是本题显示闭包原字节证据；递归全文未检到本题精确项，未重导出缓存反编译。 |
| 主树 `reverse/rehost/ap01-ui-0041-complete-source.zip` | 中央目录39成员；只读 `tools/ap01/README.md`、`nuttx-sim.sh`、`nuttx-sim.c`、`ap01-ui.h`。sh:22/23检查已知NuttX/apps提交，C/UI成员为SIM/重建代码。旧 `tools/ap01/<basename>` 可定位当前 `tooling/scripts/<basename>`。 | 中央目录未含lv_display/lv_event/lv_nuttx类成员；四个指定文本成员没有本题精确项。未认证所有zip成员内容，不复制整包、不跑SIM。不能用应用重建源码填ROM结构。 |

有界精确项为 `a0081554/a008acfa/a0084b96/a007ffa0/a00814f4/a00800b4` 与 `lv_display.c/lv_event.c/lv_nuttx_entry.c`。旧材料若以其它地址/匿名helper记录，仍可能存在；本次不是全历史不存在证明。F06保留Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3` 继续作为已有入口线索，不追加伪造Evidence或搬运完整记录。

**继承**：F06 ROM生命周期合同、F07候选13成员及源-ROM差异主体；**复核或纠正**：独立本地读取、定点ROM复核、array前缀/整个list尺寸区分、short-enum限定；**真正新增ROM功能恢复：0**，确证未改可排除仍0。本轮新增的是复核证据和认证边界精度，不重新登记已有功能完成量。旧材料未提供能闭合ROM准确源码/版本/配置认证的证据，无必要扩版本或重做整库。

## 实际只读证据和可信度分层

本轮应用 REA 技能的静态证据和事实/推断/未知规则，复用既存 F06 合同作边界；没有打开共享 REA target、创建数据库或声称新增 REA Evidence ID。独立脚本没有导入/执行 F06/F07 脚本，也不将其 JSON 当 ROM 解码输入。

- [read_candidate.py](../../analysis/display-source-review-f08-0041-20261023/read_candidate.py) 重新读取 `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`，逐文件 bytes 对比同父 `/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/v9.2.1.zip` 的 `lvgl-9.2.1/<相对路径>`。所选 13 项与 F07 精确相同：`lv_version.h`、`src/display/lv_display.c`、`lv_display_private.h`，`src/misc/lv_ll.c`、`lv_ll.h`、`lv_event.c`、`lv_event_private.h`、`lv_event.h`、`lv_array.h`、`lv_types.h`，`src/drivers/nuttx/lv_nuttx_entry.c`、`lv_nuttx_fbdev.c`，`src/draw/lv_draw.h`。未解包参考树或新建 hash 清单。
- [candidate-review.json](../../analysis/display-source-review-f08-0041-20261023/candidate-review.json) 保存每项完整绝对路径、成员名、相等布尔值、必要行号片段和枚举逐项结果；另只读补充 `src/stdlib/lv_mem.c`、`src/lv_conf_internal.h` 的小段，以检查配置影响。这两补充文件不冒充 13 成员认证项目。
- 候选自报 major/minor/patch=`9/2/1`、info 空串。父 apps HEAD 独立读为 `8ff533beb37eeef1f288c467acd7c50b542464eb`；`git ls-files graphics/lvgl` 只列五个集成文件，`.gitignore` 忽略 `/lvgl` 以及 `/*.zip`；候选没有 `.git`。故固定父 commit **同时不能认证解包树和 zip 的未改来源**。Makefile:59..78 的 tag URL/版本/解包规则只是文本，未运行。zip 时间戳也是包内元数据，不是可信签名或下载记录。
- 独立结果 **13/13 相等**，认证的是本次读取的两个本地载体在这 13 个文件上的一致性。没有官方签名/可信下载链、整包/整树比对，更没有 ROM 精确 commit、编译输入和构建可复现证据；本地文件和包可以一起被改。不能把这一层相等升级成上游认证或 ROM 认证。
- [verify_rom.py](../../analysis/display-source-review-f08-0041-20261023/verify_rom.py) 直接读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，以 `VA-0x9ffff000` 获取原 bytes 并独立解码 11 组共 **86 个有界锚点**，独立算 **4 条 JAL 目标**；[rom-review.json](../../analysis/display-source-review-f08-0041-20261023/rom-review.json) 保存小证据，不再复制全部函数指令。厂商 `ad78` 独立核 opcode/register/两个六位域均15，取位语义仍限定于 F06 已读本地模型，未虚称新手册认证。

本轮默认 sandbox 的实际 WSL 读取失败为 `Wsl/E_ACCESSDENIED`；按任务明确授权以 `require_escalated` 仅本地读取成功。没有修 ACL、改候选、运行其 Python/C 源码、SIM/QEMU/固件/设备、构建、联网或历史回放。分析脚本只在独占 analysis 中写本轮证据，未修改 ROM、生产配置或模型。

## 11 项映射的独立裁定

下表 `S` 的绝对根为 `/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。地址/偏移默认十六进制，B/条目数为十进制。表内“接受”只接受所列合同和来源候选身份，绝不表示源码逐指令未改认证；大容器中的片段不伪装成独立函数入口。

| ROM | 候选与独立重读位置 | 裁定及理由 |
| --- | --- | --- |
| `a005cc1e` 配置/caller 必要片段 | `S/src/drivers/nuttx/lv_nuttx_entry.c:96..110` | 接受候选关系：清配置、fb/input 默认路径与 `(config,result*)`。ROM ccba/ccbe/ccc6 的参数/调用连接复核；整个 caller 的页面业务未据此排除。 |
| `a0084b96` 内创建片段 | `S/src/display/lv_display.c:62..89`；`lv_nuttx_fbdev.c:75..90` | 接受 display/list/layer 的来源关系；ROM 0x324 清零、0x58 layer、+2b0/+2b4 ABI 复核。额外默认初始化差异保留；未认证整容器边界或全部失败路径。 |
| `a008aec0` | `S/src/misc/lv_ll.c:16..18,57..78`；`lv_ll.h:31..35` | 接受 n_size+8、NULL门、head/tail 更新候选合同。通用插链骨架不足以认证某版本未改。 |
| `a00873ea` 发布片段 | `S/src/drivers/nuttx/lv_nuttx_entry.c:134..169` | 接受保存 out→写显示槽→输入初始化的来源关系；源码 LCD/custom init/touchscreen 条件会选择编译分支。ROM `[s7]=s1` 复核，不将全部源码 errout 自动移植到 ROM。 |
| `a007ffa0` | `S/src/display/lv_display.c:734..739` | 接受 `(disp,cb,filter,userdata)`→`(&list,cb,filter,userdata)`；ROM +2e8/目标 a01b93b4 既有合同保持。void wrapper 的寄存器残留不命名业务返回。 |
| `a01b93b4` | `S/src/misc/lv_event.c:88..105`；private.h:27..31 | 接受 descriptor12B、cb/userdata/filter@0/4/8、追加指针的来源关系；ROM list+10 byte 表明 array 实际多状态，不能套候选16B。 |
| `a00814f4` | `S/src/display/lv_display.c:780..797`；event_private.h:33..43 | 接受28B event布局及 phase1 恰返回1才 phase0。enum 数值分歧保留；不能由28B单独推出 enum 存储宽度。 |
| `a008acfa` | `S/src/misc/lv_event.c:63..85` | 接受phase/ALL/code、userdata更新→重读cb→`cb(event*)`公共骨架。ROM额外deleted前门、bit16跳过、快照/状态清理确实存在，候选不能替换。 |
| `a007fe32` | `S/src/display/lv_display.c:927..933` | 接受NULL才用默认、仍NULL则NULL、否则driver_data的候选合同；ROM+2e0事实复核，完整私有布局不认证。 |
| `a00800b4` | `S/src/drivers/nuttx/lv_nuttx_fbdev.c:383..405` | 接受高度可识别的后端release候选：userdata→display→backend，清关联、signed fd门、offscreen候选free、lv_free backend；清+2c的字段原名不能认证。 |
| `a0081554` | `S/src/display/lv_display.c:158..212`；private.h:114..149 | 接受 DELETE/资源顺序及 layer_deinit 候选关系。ROM+2b8非NULL时 `(display,layer*)`、返回后重读+2b0再归还的关键ABI复核；真实安装、运行值及callee仍未知。 |

## 差异、配置与 ABI 能改变什么

**DELETE 数值差异是确定的。** 本轮不是仅数正则匹配名：从 `typedef enum` 的首项ALL=0到PREPROCESS，去注释后顺序解析全部65项及显式值，结果 DELETE=38/0x26、REFR_REQUEST=53/0x35、PREPROCESS=0x8000；枚举体内部无 `#if`。ROM `a0081570 93059002` 和后端注册 `a0086cca 13069002` 均直接装0x29。`-fshort-enums`、packing、RV32/64、优化和内联均不把枚举常量38变41。任意预处理重写/另一个头文件属于额外编译输入差异，当前无证据，不能当作本候选配置已解释。ROM0x29按真实删除路径命名DELETE，不反向套候选的同数值CHILD_DELETED；也不能用候选统一改名ROM0x35/0x38。

**array 前缀与重入状态差异是确定的，整个 ROM list 尺寸未知。** 候选 `event.h:116` 直接 `typedef lv_array_t lv_event_list_t`；`array.h:35..40` 只有pointer和三个uint32，无条件成员。普通RV32为16B，packing不增加成员或产生新状态。ROM `a01b9456 23882401` 是 `sb s2,0x10(s1)`；`a008ad26 5146` 把0x14作快照拷贝长度，`ad32 83474901` / `ad48 230af900` 分别 lbu/sb `list+0x14`，`ad36`还按word读取同地址再取bit0，`ade0/ade8`清该bit。因此可靠表达为“ROM有20B array前缀快照及其后+0x14状态访问”；至少这些访问覆盖了+0x14，不能说完整对象只有20B。自然RV32对齐常可导出24B容器候选，但没有结构定义/sizeof证据，不在此认证为24B。候选64位pointer可能让array sizeof变24，既不符合ROM32位访问/字段关系，也不生成额外状态字段。

**bit16与deleted提前门不是packing差异。** ROM ad4e使s8=0x10000，`ad72 b3f68701`测试filter，`ad76 fdfa`命中就跳过；入口ad16..1e和每轮ad56..5c在callback前先查deleted。候选send仅有cbNULL、phase、code匹配，callback后才查stop/deleted，无这三组操作，也没有list状态维护分支。候选descriptor.filter本来就是uint32，不受enum缩短而变短；但第74行临时 `lv_event_code_t filter` 在short-enum ABI下可能截去高位。因此 F07“源码表达与ROM只清bit15相容”仅在能保留比较高位的enum配置下成立，不能认证所有ABI的通用filter合同。这一限定**不会消除差异**：截断高位也不能生成ROM“bit16置位直接跳过”的显式分支，更不能新增list字段/提前deleted门。ROM全mask继续按F06为0xffff7fff，不能写低15位。

候选event.code即使采用16位enum，其后void*常会补齐到+c，flags仍可能@18且总28B。因此 F07 的28B布局相符是兼容性事实，不是枚举宽度/原ABI认证；descriptor.filter的uint32和实际ROMword访问分别独立有据。

**layer初始化差异在所选源码路径下成立。** 候选display.c:80分配清零，84才条件调用layer_init，85..89才设buf_area/color；本轮补读 `src/stdlib/lv_mem.c:92..117`，其lv_malloc_zeroed成功路径调用core分配再lv_memzero，没有写固定ff。ROM 4e6e→19d0，1a22→0d8e清0x58，1a28→1978，19c4/19c8明确写layer+38 word=ff，随后+3c byte=0，先于4e72..7e条件init。`LV_DRAW_TRANSFORM_USE_MATRIX` 会增删layer结构中的matrix及移动后续字段，enum packing也会移动布局，但都不会把纯零初始化改成该额外ff写。malloc core/custom、日志或assert任意外部实现未获完整认证，不能据此声称所有配置已穷尽；若另行提供重定义/外部副作用才需单独核它们，而非把本次额外写归于普通packing。具体字段名/ROM layer完整sizeof仍不从候选推定。

**早期hook相对布局确实不同。** 候选private.h:43..80的七个固定32位resolution/dpi后是buf_1/buf_2/buf_act三个pointer，然后flush_cb、flush_wait_cb。普通RV32逐项相加：buf_1@1c，buf_2@20，buf_act@24，flush_cb@28，flush_wait_cb@2c。此段无enum、bitfield或条件字段；pack1/2/4都不会多插一个word，后段LV_INV_BUF_SIZE或matrix也不影响前段。候选release第389行调用set_flush_cb，ROM `a00800e2 23260902` 清+2c。接受F07“不能直接把ROM+2c认证成候选flush_cb”的裁定，也不能转而把它认证成flush_wait_cb：相同偏移不等于同一版本语义。后段+2b0/+2e0/+2e8等仍可能受可配置结构影响，本轮不计算完整候选sizeof或借SIM x86-64 sizeof作反证。

这些差异足以拒绝“ROM该闭包是此本地候选未改编译结果”的认证；并不证明修改者是厂商，也不能排除ROM来自另一上游版本。一般优化/内联能改函数边界、消除已知空hook等，不能凭空生成固定非零默认写、额外动态状态和提前deleted/bit16门。

## 保留的行为、命名边界与结束边

所有源名在此是分析映射，非恢复出的原源码。display由list持有，layer/backend由display关联；descriptor保存借用display的userdata，sender的28B event栈借用同步交callback。phase1只有结果恰1才进入phase0；callback返回值不用。backend路径先清关联，再在signed fd>=0时close并置-1，再条件系统free resource并清槽，最后LVGL归还wrapper；静态调用不等于已观察实际释放成功。显示DELETE后继续清其他资源，末尾可选deinit，再**重读**layer pointer归还，随后display归还与全局引用更新，不能套候选名后重排这些步骤。

+2b0/+2b4/+2b8与候选连续layer_head/layer_init/layer_deinit、构造/析构位置和二参ABI共同支持候选命名；不是已装a00800b4的event回调槽。未找到也未重搜+2b8非NULL安装者；运行时值、实际callee和返回后指针是否变化未知。backend+34与候选mem_off_screen的free/清槽关系支持offscreen候选名，仍未认证其生产/长度/映射，不据此叫mmap framebuffer。+2c保留匿名字段，不认证flush原名。

**事实**：本轮本地路径/元数据/13成员相等、65枚举值及无内部条件、直接ROM bytes/86锚点/4直接边、已读候选分支和结构定义。**推断**：11组来源家族/函数候选身份与layer/offscreen命名。**未知**：ROM精确版本/commit与编译输入、上游vs厂商差异归因、整包来源、完整struct/维护callee、非NULLdeinit安装与运行值、backend+34生产和上层loop/9428连接。没有标准库/整LVGL项目被认证可排除。

实际验证完成：13/13本地包成员相等、65枚举项解析、86个独立ROM锚点和4条直接JAL边通过，提交前检查独占路径与 `git diff --check`。没有复跑694条旧指令、整库重扫/新版本搜索、+2b8 writer扫描或构建。

一个后继闭包：以 `a008acfa` 的20B array快照、list+14 bit0与其恢复/清理调用为入口，恢复事件列表追加/移除/重入维护的小闭包，明确descriptor持有、延迟删除及快照归还的正常顺序。不要用本地16B候选代替这些ROM路径，也不以此扩全GUI/全LVGL版本认证。本轮只建议，由管理分配，不自行接管。
