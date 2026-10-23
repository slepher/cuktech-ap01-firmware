# F06：显示对象来源、DELETE 归还与可选 callback 独立复核

2026-10-23；新 agent，分支 `codex/re-0041-f06`，基线 `a1a40f5a3c6b6bd6b8a4542715e8ae9708868ca3`。**对 F05 显示对象→DELETE 后端归还→显示尾部释放闭包限定接受，纠正一处 dispatcher 通用掩码措辞；filter=0x29 的实际匹配结果不变。** `obj+0x2b8` 仅有初始 NULL 的证据，非 NULL 安装者、实际目标和返回时值继续未知。已注册 DELETE callback `a00800b4` 不是 `+2b8` 的目标证据。没有建立到 caller 栈 loop / `62fc9428` / timer.data 的连接，也不据此否定所有 opaque callee 的间接作用。

本轮只静态读取 ROM、既存证据与厂商指令模型。没有执行固件、连接设备或外部服务、编译、历史回放、异常输入、修改 ROM/生产代码/分析器模型、切换共享 REA target。使用 REA 技能的方法及证据边界；没有创建新原生数据库或虚构新 REA Evidence ID。所有修改限本报告及独占 analysis 目录。

## 独立取证与范围

新写 [review.py](../../analysis/display-exit-review-f06-0041-20261023/review.py)，直接读取主仓库 `roms/0041/ap01-1.0.2_0041.bin`，映射 `file_offset = VA - 0x9ffff000`。没有运行或导入 F05 的 verify.py，没有以 F05 JSON 为解码输入。[independent-evidence.json](../../analysis/display-exit-review-f06-0041-20261023/independent-evidence.json) 与 [instructions.txt](../../analysis/display-exit-review-f06-0041-20261023/instructions.txt) 保存本轮原字节、指令、直接目标位域核对、厂商位域/既有模型摘录、字符串和有界编码搜索。

本轮核心身份为 caller `a005cc1e` 必要片段、初始化容器 `a0084b96` 必要片段、`a008aec0` 分配/显示 list 链接、`a007ffa0` 注册适配、`a01b93b4` descriptor 安装、`a00814f4` sender、`a008acfa` dispatcher、`a00800b4` 后端 DELETE callback、`a007fe32` getter、`a0081554` 显示删除。短依赖只核 `a0080d8e` 清零 ABI、`a00819d0/a0081978` payload 初始化和 `a008ab8a` 归还 wrapper；一般 allocator/zero/free、事件数组扩容/维护、子对象删除和 fd 底层实现保留既有调用合同，没有冒称完整独立认证它们。

入口线索沿用保留 `factory-test-0041-20261023/retained-initializer.json`，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`；本轮重新逐字节核其全部 raw_ranges 与 ROM 一致。F04 栈 loop、type13 close/pending 合同仅接口针对核，不重复 timer/heap 恢复。

## 裁定及唯一语义纠正

| F05 项目 | 裁定 | 独立指令依据及限定 |
| --- | --- | --- |
| 配置与 out 身份 | 接受 | ccaa/ccb6 组合 `/dev/fb0`、`/dev/input0`；ccae/ccc2 写 config；ccba/ccbe 传 out/config；ccc6 目标 a0084b96。4bb4 保存 config，4bba 保存 out 至 s7；73ea word 写 s1 至 `[s7]`。不能证明整个容器期间无人改 out。 |
| 显示对象和 payload 初始状态 | 接受调用合同 | 4da2→a008aec0；成功分支 4de8/4dec 以对象及 0x324 调零 wrapper，后者将 `(dst,len)` 改为 `(dst,0,len)`→a0024906。+2b4/+2b8 在清零范围；4e26/2a 分配 0x58，4e2e 写 +2b0；1a22 清 0x58，19c8 word +38=ff，19ca byte +3c=0。大小均为十六进制：对象 804 B、payload 88 B。未扩展为 allocator/zero 算法全认证。 |
| list_allocate 所有权 | 接受 | aecE 读取 list+0，aed0 加8再分配；NULL直接返回；正常路径调用三个链接 helper、aefc 更新 list+4，新 list 首次 aF02 更新 list+8，aF0c 返回 s2。节点底层布局/helper不扩展；不凭名字认证来源。 |
| 构造 callback +2b4 | 接受区分 | 4e72 取 +2b4，非 NULL 时以 `(obj,word(obj+2b0))` 间接 call；不能与删除槽 +2b8 或 event callback 合并。 |
| backend 与 DELETE 真实安装 | 接受 | 6cc6 word 写 backend 至 obj+2e0；6cd4 的 a0=obj，a1=a00800b4，a2=29，a3=obj。ffec 加 2e8，fff0/fff4 真实目标 a01b93b4。 |
| 12 B descriptor / 追加 | 接受 | 93c2 请求0xc；9432 保存 cb@0，9438 filter@8，943a userdata@4；94f2 厂商乘加把数组地址推进 element_size×count；复制 descriptor 指针后 9502 更新 word count。扩容/重入维护保留 helper 边界。 |
| sender event ABI / phase | 接受 | 150e 清 0x1c 栈 event；1516/151a 写 obj@0/+4，152e code@8，1522 param@10；1532 先 phase1，1538 只有返回恰1才到1544 phase0。DELETE filter29属于 phase0，不因两阶段说调用两次。 |
| dispatcher filter 通用表达 | **纠正** | ad42 `c.lui s5,0xffff8`；ad50 `c.addi s5,-1` 得 **0xffff7fff**；ad80 是 `filter & 0xffff7fff`，只清 bit15，并非 F05 所写“低15位”。bit16 在 ad72/76 单独跳过；bit17..31仍保留在 code 比较值中。 |
| filter29 及 callback ABI | 接受具体合同 | th.extu 位域取 bit15与phase比较；filter=29 的 bit16/15均0、mask后仍29，匹配phase0/code29。ad8e 从descriptor+4取 userdata；ad92 写 event+c；ad96 **再读** cb@0；ad98 a0=event间接 call。 |
| backend 清关联和归还 | 接受 | 00c0 读取event+c；00c6 getter；正常backend非NULL先清 obj+2e0/+2c，signed fd>=0才调a0026888并写-1；再资源+34非NULL调用a002e14e且清槽；最后backend→a008ab8a。NULL obj 分支重新取默认显示，不能省略。 |
| 显示尾部与重读 | 接受 | 157e DELETE→1586 event list清理→显示资源调用→15da list移除→15e4条件调度对象删除→15e8可选+2b8→15f6重读payload→15fa归还payload→1600归还obj→1604后全局显示引用更新。 |
| +2b8 安装和 loop 断边 | 接受其未知限定 | 初值NULL不等于15f4时NULL；普通SW offset2b8检索非完整别名/厂商/批量写分析；a005cec2 的loop与ceca重读out是不同直接实参。没有可据以把此显示闭包命名为loop walker的已证边。 |

纠正只涉及通用 filter 表达，未改变实际 filter29 删除路径。本轮没有为了举例而执行任意 filter 或异常输入。F05 文本保留，由本报告提供正式纠正。

## 原字节、返回与所有权

决定本轮纠正的原字节：`a008ad42 e17a`、`a008ad50 fd1a`、`a008ad80 b3f75701`。`a008ad78 8bb6f73c` 独立拆得 opcode=0xb、rd=a3、rs1=a5、lsb=msb=15；既有只读 ap01thead2.sinc 的 `th.extu` 语义为取单 bit15。`a01b94f2 0b15f620` 拆得 rd=a0、rs1=a2、rs2=a5、op2531=16；本地 `th.mula` 模型为 `a0 += a2*a5`。没有据本地模型称厂商手册已认证。构造完整范围 `a0084b96..a00874af` 再次线性分长保留21个 Capstone 不认识的字，不把它们视为无写副作用。

dispatcher 的 callback 返回值被后续 flags byte 读取覆盖，不作为业务结果消费；event bit0 在入口及迭代前检查，callback 后先取 bit1，再查 bit0，不能把两 bit统一为一个任意布尔返回。sender 仅对 dispatcher 返回值作 `==1` 门。F05 泛称“保留原返回判断”在本闭包成立，本轮未展开重入/维护 helper 的全部效果。DELETE sender 返回到 a0081554 后没有阻止尾部清理的返回判断；不能把“注册存在”说成任意运行状态必执行后端 callback。

backend callback 的原序必须保留：`00de 2320092e` / `00e2 23260902` 清显示关联，之后 `00e6 8840` 取 signed word fd；`00e8 63460500` 的负值分支直接到00f4。非负分支 `00ec ef60caf9`→a0026888，调用返回后 `00f0 fd57` / `00f2 9cc0` 写-1，没有依据返回值重试或改变顺序。`00f4 c858` 取资源；`00f8 efe06a85`→a002e14e 后 `00fc 23aa0402` 清+34，再 `0102 efa09028`→a008ab8a归还backend。fd为负时不重新写-1；资源为NULL时不调用归还也不额外写槽。NULL backend走日志并返回。

`a008ab8a` 对 NULL 及固定哨兵 `62fc95e0` 直接返回，其他值转 a002e14e；本报告“归还”指调用该合同，不宣称已观测堆或硬件状态。后端fd局部产生点6d3c以 `(pathname,3)` 调a003f4f6，6d40将返回word写backend+0；底层file close与buffer+34生产/映射未知，不将其改名为已证 mmap。

| 实体 | 最小布局（偏移十六进制，word=32 bit） | 生命周期 |
| --- | --- | --- |
| caller out / loop | out@s0-314；loop@s0-240 | out被发布，返回时ceca重新读；不认证整个运行期别名写全集。 |
| 显示对象 | payload@2b0；init_cb@2b4；optional_delete_cb@2b8；backend@2e0；event list@2e8；调度对象@308 | 全局list持有；DELETE先于显示资源和最终payload/obj归还。 |
| descriptor，12 B | cb@0；userdata@4；filter@8 | event list保存其指针，注册userdata=obj；不位于+2b8。 |
| 栈event，28 B | obj@0/+4；code@8；userdata@c；param@10；flags byte@18 | sender栈借用，同步callback传 event*；param0与userdata分开。未据此穷尽排除callee保存栈指针。 |
| backend | signed fd@0；resource pointer@34 | 清obj关联后依次请求fd/资源/backend归还。 |
| payload，0x58 B | word@38=ff；byte@3c=0 | optional callback前作为a1读，返回后重新取值归还，继而归还obj。 |

```c
// 分析伪代码，不是原源码。未知callee效果不以省略证明不存在。
init_fragments(config, out) {
    obj = allocate_and_link(&display_list); // a008aec0
    zero_contract(obj, 0x324);
    obj->payload = allocate_contract(0x58);
    init_payload(obj->payload);             // zero 0x58; +38=ff; byte+3c=0
    if (obj->init_cb) obj->init_cb(obj, obj->payload);
    // 其他显示配置及后端生产未完整恢复。
    obj->backend = backend;
    register_event(obj+0x2e8, a00800b4, 0x29, obj);
    *out = obj;
}
match_descriptor(filter, phase, code) {
    if (filter & 0x10000) return false;
    if (((filter >> 15) & 1) != phase) return false;
    value = filter & 0xffff7fff;             // 正式纠正：非低15位
    return value == 0 || value == code;
}
dispatch_selected(descriptor, event) {
    event->userdata = descriptor->userdata; // event+c
    cb = descriptor->cb;                    // 写userdata之后重读
    cb(event);                              // 返回值不用，随后重读flags byte
}
backend_delete_event(event) {
    obj = event->userdata;
    backend = get_backend(obj);             // NULL obj才取默认显示
    if (backend) {
        if (!obj) obj = default_display;
        if (obj) { obj->backend = 0; obj->field_2c = 0; }
        fd = signed_word(backend+0);
        if (fd >= 0) { close_contract(fd); word(backend+0) = -1; }
        resource = word(backend+0x34);
        if (resource) { free_contract(resource); word(backend+0x34) = 0; }
        release_wrapper(backend);
    }
    log_contract();
}
delete_display(obj) {
    saved_global14 = global_display14;
    saved_global10 = global_display10;
    send_event(obj, 0x29, 0);               // phase1恰返回1后才phase0
    clear_event_list_contract(obj+0x2e8);
    // 原序：输入关联、+2c0/+2c4/+2cc、+2bc元素和+26c列表。
    cleanup_display_resources_contracts(obj);
    unlink_contract(&display_list, obj);
    if (word(obj+0x308)) delete_schedule_contract(word(obj+0x308));
    cb = word(obj+0x2b8);
    if (cb) cb(obj, word(obj+0x2b0));       // 身份/安装/运行值未知
    release_wrapper(word(obj+0x2b0));       // callback返回后重新读取
    release_wrapper(obj);
    if (saved_global14 == obj) global_display14 = display_list_head;
    if (saved_global10 == obj) global_display10 = 0;
}
```

## 有界负搜索、来源与结束边

独立重新扫描整ROM半字对齐位置，只匹配普通 RV32 SW 编码与 S立即数=0x2b8，仍仅三处：`a00efd3e 23acab2a`、`a00eff32 23ac0b2a`、`a014e264 232c812a`。本轮只将其作为编码命中，不从命中全集推导“没有其它 writer”。它不区分指令/数据、不覆盖先加基址后低偏移store、别名、批量复制、indexed厂商store或全部callee。没有建立非NULL目标候选集，更没有证明15f4实际跳过。构造厂商字库存正说明普通解码负结论的覆盖限制。

字段写入、调用ABI、宽度、返回门和重读是本轮直接字节事实；“显示对象/DELETE/后端”是由配置、注册及资源消费共同支持的业务恢复推断。F05所列 LVGL/NuttX 源码路径仅帮助识别子系统，未认证具体LVGL版本或未改源码；不据此排除厂商初始化/回调。通用内存与文件层维持明确合同及来源认证缺口。

实际静态验证：运行本轮脚本 **PASS 108 checks，19 windows，2092 bytes**，全部选定窗口可解码（两处厂商字按独立位域及只读本地模型处理）；直接边独立算 JAL/AUIPC-JALR；保留入口 raw_ranges 匹配；3个SW命中及21个构造未知字保留。脚本不执行目标代码。提交前检查独占路径、`git diff --check` 和git状态。没有进行固件/模型回放或项目构建。

未核清单：完整初始化正常成功条件、所有显示/输入资源callee、event数组维护/重入、backend+34生产和底层fd最终归还、out/obj全运行期别名写、非NULL+2b8安装/目标/返回时值、上层loop/9428连接。F04实际close(9428,cb)及退出后pending消费机会继续开放。本轮结束在这些精确边，不能将本显示删除闭包提升为 MiIO 退出完成。

一个实质后继闭包：围绕同一显示对象从发布out到返回前的保存引用，定向恢复可能写+2b8的别名/批量/厂商store及其正常调用；找到真实安装后再核 callback 是否接触本loop/9428。不要重复本轮普通SW扫描，也不要把DELETE callback当+2b8目标或扩为全部显示/全timer扫描；本轮不接管该后继。

管理提出F07可优先做本闭包本地LVGL来源/适配差异认证。本轮实际遇到的来源入口仅ROM中的 `src/drivers/nuttx/lv_nuttx_entry.c`、`src/display/lv_display.c` 字符串，以及本地指令模型；未遇可定位LVGL候选源码树，故无法据本轮证据认证9.2.1。若管理已有SIM报告提供只读本地候选路径，则适合以该路径为明确入口，对上述约十个核心身份逐项核源码和厂商差异，仍将候选版本标为未认证直至比对成立。本轮未为该建议扩扫、访问WSL、外连或下载。
