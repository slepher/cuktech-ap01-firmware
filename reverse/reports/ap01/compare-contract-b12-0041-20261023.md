# B12：a00501be 正常比较合同

2026-10-23；分支 `codex/re-0041-b12`；固定基线 `5cabca7`。仅静态恢复 `a00501be..a0050201`（68B），无直接callee，因此不另展开依赖。**正常内存前提下，返回0表示给定长度的字节全部相同，非零是首个不同的无符号字节“左减右”。B10的20B调用非零表示内容不同。** 本文不是运行观察或原始源码，待独立复核。

## 先查已有成果

本树报告中精确地址搜索命中 [B10](basic-info-dispatch-caller-b10-0041-20261023.md)、[B11](basic-info-dispatch-review-b11-0041-20261023.md)、[miio deferred settings](miio-deferred-settings-0041-20261023.md) 和管理任务书。B10/B11明确保留opaque返回语义；miio报告仅用 `compare_bytes_a00501be` 名称，且来源段明确libc形状不等于版本认证。

[既有USB机器dossier](../../analysis/usb-interface-ota-0041-20261023.json) 已完整保存本函数反编译、汇编和原字节，Evidence `ev_bcb6dbb168d8b5f6e23caa37ac3eb465a0ea1b6160de2e419ac51b904323a3ed`，body范围为上述68B。但其 `supporting-static-dossier` 状态不是本次参数/返回/来源的原指令验收；对应USB报告没有给本函数合同。故本次补核缺口，继续原任务；不把历史异常回放当新证据，也不续作其材料。没有另选或扩展响应依赖。

## 参数、返回与控制流

| 位置 | 已恢复合同和指令依据 |
| --- | --- |
| 入口 `a00501be` | a0=左缓冲区地址L，a1=右缓冲区地址R，a2=无符号32位字节数n；地址/长度按RV32 word传递。正常前提：被读取的n字节可读且本次比较期间稳定；不讨论异常地址、并发改写或绕回区间。无对象字段、全局变量或结构体依赖。 |
| `01be..01cc` | `a5=3`；`bgeu a5,a2,01d6` 表示n<=3直接走byte路径。否则OR两地址并AND 3；任一未4字节对齐也走byte路径。 |
| `01ce..01d2`、`01e2..01ec` | 对齐且n>=4时以两个C.LW比较word；仅相等时n-=4，L+=4，R+=4，n>3无符号条件继续。word不同时不推进指针或减少长度，从该word首字节进入byte路径，不能按word数值的大小直接返回。 |
| `01d6..01e0` | index=a4=0；机器先把a1减1，`bne a2,a4,01ee` 在有剩余时读取，否则a0=0后返回。n=0是正常空区间返回0，不读取buffer；不由此推广其他异常实参合同。 |
| `01ee..01f8` | `th.lrbu a5,a0,a4,0` 读L[index]并零扩展；index+=1；`th.lrbu a3,a1,a4,0` 读(R-1)[index]，即同一原索引的R字节。相等跳01da，重复剩余范围。两条厂商指令是indexed load，不是带指针更新的load。 |
| `01fc..0200` | 第一次byte不等时 `sub a0,a5,a3`、返回。范围为-255..255（负数在a0中为RV32补码）；a5/a3来自零扩展byte。两处返回均为C.JR ra。 |

返回合同因此为：n字节相等返回0；若最早不等索引为k，返回 `unsigned_byte(L[k])-unsigned_byte(R[k])`。返回符号对应无符号字节的字典序；不是只返回布尔值1，也不是字符串比较，NUL不终止。word fast path只跳过已证明相等的4B，不改变首异byte的次序。整个68B窗口没有store、call或间接调用，读取buffer后仅改变caller-saved寄存器；无额外直接依赖需要恢复。

```c
// 静态语义投影；正常可读内存，地址运算依RV32。不是原始源码。
int32_t compare_501be(const uint8_t *L, const uint8_t *R, uint32_t n) {
    if (n > 3 && (((uintptr_t)L | (uintptr_t)R) & 3) == 0) {
        while (n > 3) {
            if (load_u32(L) != load_u32(R)) break;
            L += 4;
            R += 4;
            n -= 4;
        }
    }
    // 机器实现中R先减1，右侧load在index加1后，抵消偏移。
    for (uint32_t i = 0; i != n; ++i) {
        uint32_t l = L[i], r = R[i];
        if (l != r) return (int32_t)l - (int32_t)r;
    }
    return 0;
}
```

B10/B11已核 `a00a86a8` 调用 `a00501be(p,payload+5,0x14)`，`86ac` 非零才进入 `86b2` 的p检查。因此在本helper正常合同的前提下，后继路径要求20B内容不同。这里沿用B11调用点，不再展开完整caller、后续复制/通知；保留原检查次序，不声称任意p均满足正常内存前提，也不认证此前lookup对象与后续重读对象跨调用相同。

## 来源、事实与未知

事实是原字节、RV32+C编码、比较/递增/返回寄存器、无callee及无store。`th.lrbu`两条原word分别为 `80e5478b`、`80e5c68b`：opcode=0xb、funct3=4、bits31:27=16、shift bits26:25=0；rd/rs1/rs2分别为15/10/14和13/11/14。它们匹配本地主仓库既有 `ap01thead2.sinc` 构造器：`ea=rs1+(rs2<<shift)`，读1B，零扩展给rd。核了位域与已有模型文本，未修改模型；厂商指令语义仍依赖这个既有模型，未新增独立上游ISA证明。

推断为“memcmp形状”的算法名、通常RV32 ABI的参数/返回解释及上文可读C投影。本地来源识别依据限于完整函数控制流和既有源码路径索引 [open-source-c-paths-0041.txt](../../analysis/open-source-c-paths-0041.txt)；该索引没有把这个函数绑定到某一libc源码/版本，普通memcmp控制流也不具有唯一来源性。仅能确定镜像为仓库0041（1.0.2_0041标签）；**不能确认newlib、NuttX libc、其他libc或厂商自写，不能确认准确上游版本或是否修改，因此不新增开源排除。** 本次不联网获取源码，不把算法名当来源认证。

未知仍为来源版本、独立厂商ISA认证、运行时可达性/实际内存状态、跨调用对象稳定性、caller完整返回合同和整个响应状态机。正常参数下本helper的局部算法/参数/返回已恢复；模块整体仍部分恢复。

## 证据与实际验证

- [verify.py](../../analysis/compare-contract-b12-0041-20261023/verify.py) 只读主仓库 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA-0x9ffff000`，起始offset=332222；与既有dossier全部68B逐字节及body范围比对。未新建哈希或复制清单。
- [instruction-evidence.json](../../analysis/compare-contract-b12-0041-20261023/instruction-evidence.json) 记录VA、文件偏移、原字节、重新解码、25项原编码检查和既有模型摘录。Capstone重解23条普通指令；独立位域解析5条普通branch、C.BNEZ、C.J、C.LI/ADDI、C.LW、OR/ANDI/SUB、两个return及2条厂商word。Capstone branch操作数字串为相对位移时，实际绝对目标以独立原编码检查为准。
- 工作树运行 `python reverse/analysis/compare-contract-b12-0041-20261023/verify.py`：退出0，**passed：68B、23普通指令、2厂商word、25项检查**。人工依完整25条序列核了word/byte路径、a1减1与index加1的抵消、返回顺序及无store/callee。自动检查不是形式化证明或执行覆盖。
- 祖先目录与本树相关路径未发现适用AGENTS.md。仅写B12独占报告/analysis；未建立可写REA会话/数据库，未执行固件、连接设备/服务、运行历史回放、异常输入/缺陷验证、生产构建或修改ROM/生产/安全检查/分析模型。差异检查通过后本地提交。

后继建议B13：只独立复核本68B正常合同，重点核两条indexed unsigned-byte load、R减1与index先增的抵消、首异byte差值及来源未识别边界；不扩响应或历史回放。
