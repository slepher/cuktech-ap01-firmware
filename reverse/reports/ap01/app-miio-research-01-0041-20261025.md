# Q-04 普通 MiIO 策略 hook 来源：有限静态输入核查

状态：**部分恢复，作者交付待独立复核；接口未闭合**。本轮没有解析 hook 目标，不新增路由恢复合同。

认领 Q-04；作者 `/root/app_miio_research_01`。基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`。独占报告及同名 analysis 目录；未改管理表、旧报告、ROM、生产配置或分析器，未提交、构建、运行目标、模型、SIM、刷机或联网。

原件沿用 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算 hash。ROM 范围内文件偏移为 `VA - 0x9ffff000`，此公式**不适用于**低地址 RAM 对象 `0x62fc4944`。

## 继承结论

事实，来自已验 `evidence/rea-0041-20261017/evidence/upper-routing.md/.json` 六合同及 `upper-layer-0041-20261017.md`：

- `0xa0064368` 的 manager M 大小为 `0x23a0`；OTU context 为 `M+0x174`，其 `+0x28` 保存 `P=0x62fc4944`；OTS context 为 `M+0x968`，对应 `+0x28` 为 NULL。
- P 的 `+0/+4` 自链初始化；`+0x10/+0x14` 在未设置时装入 `0xa0121886/0xa011f186`。这两个是 add/delete 槽，不能充作 `+0xc` check 槽。
- 普通下行 `0xa01214f8` 从 context+0x28 得 P，非空时调用 P+0xc。已验调用点传入 `(P, descriptor, origin_u8, request+4, replycb, context)`；hook 返回 0/非 0 均最终由 dispatcher 返回 0。hook 自身是否调用 handler、如何回复及其实际成功语义仍未知。
- 查重依据为管理表 Q-04 当前行：同对象 hook 无其他认领；F11/F15 共用 manager 但研究请求/队列持有，不与本题差集重叠。

## 本轮核对或纠正

本轮仅在既存留存证据中定位必要窗口，不重做完整路由。

1. upper-complete record248 的 Evidence 为 `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`；它是留存的完整安装函数观察，与 upper-routing 安装合同所引 `ev_e4f23482ca65c754b823bd7a193f8268baa0ef139cccdd0227fe6c239488ec0c` 分开标识，不混用 ID。record272 为分派 Evidence `ev_d7381a8523524525f03bf4e08e0ea5380a9ff1fc4e0b4814db227954884a818c`。两条旧 profile 均保留 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`，未贴现代 profile。
2. 安装原指令 `a0064f12/1e` 构造 P，`a0064f2e/30` 为 32 位 self-link stores。`a00650b8` 将 P 存于 `(M+0x180)+0x1c=M+0x19c`，即 OTU context+0x28；`a00650ba/ca` 访问 P+0x10，`a00650cc/e2` 访问 P+0x14。这些已知 stores 不构成 P+0xc writer。
3. 分派反编译文本有额外第七个 `*(code **)(P+0xc)` 参数；实际 `a012171a: lw a6,0xc,s9`、`a012172e: c.jalr a6` 将 a6 用作目标寄存器。调用前 a0..a5 是既有六个业务实参，a2 在 `a0121722` 经 `lbu` 零扩展。不能仅因反编译额外表达式，认定第七个业务实参。这里纠正反编译表述，不把调用点六实参扩大为未解析 hook 本体的完整 ABI 合同。

稀疏指令见同名 analysis 的 `0xa0064368.selected.json` 与 `0xa01214f8.selected.json`；原件定点读取 5 窗口共 240 B，原字/VA/偏移在 `bounded-inputs-and-raw.json#/raw_windows`。仅核这些窗口，不代表函数全字节重验。

## 真正新增

**新增业务实现合同为 0**。新增的是可复用的有限输入检查记录：

| 留存源 | 检查范围 | 结果与限制 |
| --- | --- | --- |
| upper-complete.evidence.json | 317 records；精确匹配 parameters 中 a0064368/a01214f8/62fc4944/62fc4950；各记录现存 incoming_references/outgoing_references/referenced_names 字段中精确地址字符串 | 仅 record248 安装和 record272 消费匹配；P 精确引用来自安装函数，未得到 4950 独立 xref/writer/初始化实值 |
| whole-rom-private-20261023.evidence.json | 2873 records：162 analyze_function、407 xrefs、2300 inspect_native_instruction、2 search_strings、1 list_procedures、1 binary_overview；同样精确参数/现存引用字段选择 | 无匹配 P/4950 的记录/引用；不是覆盖整 ROM 的 writer 搜索，也未搜索全部 pcode/伪码值或邻近别名 |
| whole-ROM binary_overview record2282 | `ev_cc029be51b89ac74602096f9049dcd81f451978a45476bf6faa998aa2ecb8c4f` 的 segment 元数据 | `ram` 范围 9ffff000..a0673c28，另有 csreg；没有给出低 RAM P 的初始化载体映射。不能据此断言 P 为 BSS、恒零、不可写或没有 writer |

精确命中与原 profile 在 `metadata-selection.json`；各 bundle 的计数与 segment 原值在 `bounded-inputs-and-raw.json`。读取完整 JSON 只为元数据/精确记录筛选，不等于逐条审核其全部语义。没有打开共享 REA session、重跑 provider 分析、全 ROM 扫描、RAM 全值搜索或无种子导函数。

## 未闭精确边

断边为 `context+0x28 -> P=62fc4944 -> *(u32 *)(P+0xc=62fc4950) -> 未知目标`。已知安装函数没有在核对窗口给该槽赋实值；留存精确匹配未提供其 writer，不构成“全 ROM 无 writer”。因此不能恢复注册/覆盖时序、hook 正常函数返回、状态修改、callback/请求的持有关系、注销或必要寿命，也不能证明所有路径都不修改该槽。

所缺静态输入：① P/4950 的真实初始化载体及 ROM-to-RAM 拷贝/重定位映射，或② 可定位到该槽的 typed writer xref/存储实参及其函数体。得到任一项后才有必要追该对象的注册→调用→正常返回→关闭。不能把仅有 allocator、通用容器、队列或其他未知间接调用当作本题后继。

**真实后继种子：无新的 writer/实值种子。** 已知消费者 `0xa012172e` 与安装 P 的 `0xa00650b8` 仅为既存断边锚点，不登记为新研究任务。按父窗边界到此短项交付，不为填满预测时长扩展搜索。

## 时间与检查

预测 20–29 分钟，中低置信，假设既存索引能给出 writer；该假设在有限输入核查后不成立，实际按短项交付。UTC 开始 `2026-10-24T16:04:59Z`；UTC 结束 `2026-10-24T16:08:07.697545+00:00`；墙钟 `0:03:08.697545`。shell 工具等待合计约 30 秒，已包含在墙钟内；无 provider 等待或外部阻塞。首轮工具清单/单行 JSON 预览过大，后续改用本地 JSON 选择器，未把截断预览用作证据。token/cached 用量由父窗统一单列，本作者无独立计量。

实际检查：确认 HEAD、指定原件路径/大小继承身份、JSON 成功解析、精确记录筛选、必要指令与 240 B 定点原字保存、输出路径范围和 `git diff --check`。这是作者静态检查，不是独立技术验收。
