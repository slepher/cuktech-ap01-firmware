# A07：线程注册入口与 userdata 的直接透传

2026-10-23；基线 `b2b262f`，分支 `codex/re-0041-a07`。**已闭合 A05 注册实参到一个直接创建包装的透传合同；尚未闭合线程最终以何值作为 consumer 的 a0。** `a0197f02` 将原 a2 不变放到 `a0052fee` 的 a2、原 a4 不变放到其 a3。A05 的 `a0126946` 与 consumer 因而分别成为这两个参数。下层局部可见入口转交与 userdata 保存，但启动适配器及三个厂商指令仍未恢复，不能称已证明 consumer 实际启动或已收到该对象。

已读 REA 技能/native guide、管理任务书、A05/A06及A03证据脚本；检查本树、主仓库和相关祖先未发现适用 AGENTS.md。只读取原 ROM 和既有证据，没有打开共享 REA 会话或数据库、执行固件、外连、连接实机、验证缺陷或修改分析器模型。下述为分析伪代码，不是原始源码。

## 范围与证据

两个核心函数：`a0197f02..a0197fa7`（166 B）及其直接 callee `a0052fee..a0053251`（612 B）。后者仅恢复与本任务相关的入口参数和保存/转交局部，不认证其整个线程系统行为。边界由主仓库 `evidence/rea-0041-20261017/evidence/final-seeded-roots-205.json` 的 `ghidra-function-manager` body ranges 定位，再核原 ROM 的前奏、返回、局部跳转；连续地址范围本身不等同完整语义认证。定位时读取另外两个 roots 文件的对应 inventory 项，没有据其其他 caller 扩展范围。

[collect-static.py](../../analysis/thread-userdata-a07-0041-20261023/collect-static.py) 只读主仓库绝对路径 `roms/0041/ap01-1.0.2_0041.bin`，沿用基址 `9ffff000`；只写本任务 [instruction-evidence.json](../../analysis/thread-userdata-a07-0041-20261023/instruction-evidence.json)。JSON保存两范围原字节和逐指令地址、44项独立字段/直接目标/分支核验。没有新增哈希或复制清单。

## a0197f02：直接调用合同（指令事实）

分析签名为 `int register_partial(void **out, void *name, void *entry, uint32_t stack_value, void *userdata)`，五参数分别为 a0..a4；类型名仅用于表达实参，不认证原始 typedef。

| 地址 | 原指令事实 |
| --- | --- |
| `a0197f12/18/1a` | `s3=a1`、`s4=a0`、`s2=a2`，分别保存 name、out、entry。 |
| `a0197f22..32` | a0=s0-44、a1=`a01bdc9c`、a2=12，调用 `a000589c`；原a3/a4分别由word store存s0-56/-52。这里仅认证调用参数，未展开该callee的复制语义。 |
| `a0197f36..42` | 重载原a3，word写s0-36，即候选12 B属性区+8；在s0-41即区+3写byte 1。 |
| `a0197f46..4e` | 调 `a002fcc8(4)`；返回零跳 `a0197fa4`，设置返回寄存器保存值s2=-1，再去属性区清理局部。 |
| `a0197f50..62` | 重载原a4至a4；a2=s2=原entry，a1=s0-44，a3=a4=原userdata，s1=4 B申请返回，a0保持此返回；AUIPC/JALR独立重组为调用 `a0052fee`。 |
| `a0197f66..70` | 保存创建包装返回到s2；零跳 `a0197f96`。非零以s1为参数调用 `a002e14e`，随后走共同返回段。 |
| `a0197f96..a2` | 读word(s1)到a0，word写s1到out；a1=name，直接调 `a01a9038`，然后到共同返回段。该callee返回没有作为本包装返回使用。 |
| `a0197f74..94` | 调 `a0024906(s0-44,0,12)`，随后返回s2。只认证参数与返回来源，不给该callee副作用补定义。 |

调用关系：A05 `a0063342/3346 → a0197f02 → a0052fee`。到第二条边时，参数精确为 `(new4, attribute_area, a0126946, consumer)`。直接传入不是把 entry 放入 userdata，也不是传 consumer+4；consumer+4 是上层保存4 B句柄指针的输出槽地址。

```c
// 分析表达；调用者/ABI规定的保存寄存器合同用于跨call追值。
int register_partial(out, name, entry, stack_value, userdata) {
    byte attributes[12];
    call_a000589c(attributes, ptr_a01bdc9c, 12);
    store32(attributes + 8, stack_value);
    store8(attributes + 3, 1);
    p = call_a002fcc8(4);
    if (p == 0) {
        result = -1;
    } else {
        result = call_a0052fee(p, attributes, entry, userdata);
        if (result != 0) {
            call_a002e14e(p);
        } else {
            object_word = load32(p);
            store32(out, p);
            call_a01a9038(object_word, name); // 此返回未替代result
        }
    }
    call_a0024906(attributes, 0, 12);
    return result;
}
```

属性区不是已认证的原始结构体。只确认本包装写偏移+3的byte及+8的word；复制callee内部、模板完整含义、name调用的具体命名语义、下层输出word所代表的真实句柄类型均待核。

## a0052fee：入口和直接保存局部（事实与边界）

入口 `a005300a/3010/3012/3022` 分别保存 a1→s2、a0→s6、a2→s9、a3→s7。因此本调用上下文的入口值是 s9=`a0126946`、s7=consumer。`a005305e/3062` 以 `0x140` 为参数直接调 `a0030eb8`，返回保存s1，零分支去 `a005324e`（设置s4=12并返回）。不把这个大小参数直接升级为已认证对象类型。

下表列局部指令，不为到达每个局部的整个前置条件赋义。

| 地址 | 已核局部 |
| --- | --- |
| `a0053100..310e` | a2=`a012f946`，a3=s9（入口保存值），a0=s1，a4=1；a1来自前面的分支/指令。直接调用 `a0030ef8`。a3在此是传给下层的值，不能自行解释成下层最终调用的a0。 |
| `a0053112/3114` | 保存返回到s4，非零跳 `a005324a`，在那里s4=16再去外部清理调用局部。 |
| `a0053126..3136` | 组合常量a5=`a0051dac`；word写该值到s1+`0x130`，word写s7到s1+`0x134`。这是候选userdata保存位置，不能只凭邻接认证这两个字段将由同一个callback消费。 |
| `a0053206/320a` | s6非零时word写s2到*s6；此处s2刚在`a00531f4`从s1+12读取。没有把它误认作直接写s1到out。 |
| `a005322c..3232` | 返回s4；其他分支、错误清理和临界区不在本任务语义恢复范围。 |

三个原word保留为未知：`a00530fa:8bba5a18`、`a00531c0:8bdbe744`、`a00531e8:8bb7073c`。普通 Capstone 不解码，脚本按原指令长度保留4 B，没有用反编译猜厂商语义。故这里只报告入口保存关系、明确的普通指令转交/存储局部；不凭省略这些word构造完整可达性或寄存器不变量证明，不认证下层全部参数状态。特别不证明 `a012f946`、`a0051dac` 的作用，也不推断最终 callback/线程 a0。

```c
// 分析字段，仅描述局部出现的两次word写；不是完整对象结构。
struct CreatedObjectPartial {
    byte unknown_000[0x130];
    uint32_t observed_code_130;   // 局部被写 a0051dac
    uint32_t observed_value_134;  // 局部被写 s7，入口保存原a3
};
// 已核局部：
call_a0030ef8(s1, local_a1, ptr_a012f946, s9, 1);
if (returned_value == 0) {
    // intervening call a002dc72 is not expanded here
    store32(s1 + 0x130, ptr_a0051dac);
    store32(s1 + 0x134, s7);
}
```

上述伪代码只表达该控制流局部；不把跨越未知厂商word和未展开callee的值关系提升为完整线程启动证明。

## 结论、来源和实际验证

事实：a0197f02直接传给a0052fee的entry与userdata分别是A05的a0126946和consumer；包装零返回后将4 B申请指针发布到consumer+4，再调用name相关callee。a0052fee入口保存二者，下层创建局部出现适配入口a012f946、原entry的转交，以及+130/+134两次word写。

推断：这是线程创建封装、12 B区域是线程属性，+134是后续携带用户对象的候选字段；依据是注册调用形态、stack参数、rpc_consume字符串及下层入口转交/保存局部。未知：`a012f946`如何进入原entry、`a0051dac`是否消费+134、最终consumer的a0、实际启动/调度时机、下层所有成功路径、对象完整结构及销毁。没有新增蜂鸣exited_sem或正常停机关联。

来源状态：两核心函数及未展开callee均未获得可核实的开源版本/出处；形似库API不足以排除，不新增开源排除。恢复程度：直接注册透传合同已恢复；下层持有/适配只局部恢复；到实际consumer调用的边仍断开。

实际验证：宿主Python脚本成功，Capstone 5.0.7；2窗口778 B，256个指令槽（253普通指令、3未知厂商word），44项独立检查通过，包括C.MV寄存器、word/byte存取字段、ADDI常量、5组AUIPC/JALR与2条JAL目标、两个压缩零分支目标。JSON解析、报告本地链接和 `git diff --check` 通过。不编译生产项目、不运行ROM或参考模型。PowerShell持续提示InitializeDefaultDrives失败，显式Set-Location后本树操作正常；第一次技能路径选错已改为技能目录真实路径，未修改环境。

下一小任务：只核 `a012f946` 是否以及如何将线程创建参数转为原entry的a0，最多该适配入口及一个直接依赖；若与+130/+134无直接关系则保持断边，不扩展调度器或RPC业务。可先独立复核本任务直接包装合同。

验证辅助的一次Python读取因宿主默认GBK不能解码UTF-8中文报告退出；显式UTF-8后重检。普通Git暂存被沙箱以主仓库 `.git/worktrees/re0041-a07/index.lock: Permission denied` 拒绝；依用户明确本地提交授权请求工具升级，不修改权限、不绕过限制。
