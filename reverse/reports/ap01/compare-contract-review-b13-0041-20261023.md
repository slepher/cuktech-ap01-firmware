# B13：比较合同独立复核

2026-10-23；分支 `codex/re-0041-b13`；固定基线 `123d476`。**限定接受[B12](compare-contract-b12-0041-20261023.md)，无需纠正。** 本次只核 `a00501be..a0050201` 完整68B的正常参数/返回合同，没有展开响应、历史回放或异常验证。结论为静态恢复，不是固件执行观察；厂商load的语义仍依赖既存本地模型。

## 逐项验收

| B12主张 | 裁定 | 本次独立原指令依据 |
| --- | --- | --- |
| a0=L、a1=R、a2=n；n按无符号word使用，a0返回 | 接受，参数业务名和常用RV32 ABI解释为推断 | `01c0` BGEU读a2；两个word load以a0/a1为地址；byte load读a0/a1加index；`01de`写a0=0；`01fc`写a0=左byte减右byte；`01e0/0200` C.JR ra。无需对象、全局或额外callee。 |
| n<=3或任一地址不4B对齐时走byte路径 | 接受 | `01be` a5=3；`01c0` BGEU a5,a2→01d6；`01c4` OR a5,a0,a1，`01c8` ANDI 3，`01ca`非零→01d6。 |
| word fast path只跳过相等4B，word不等回到首byte | 接受 | `01ce/01d0`为零偏移C.LW；`01d2` BEQ相等才→01e2，依次n-=4、L+=4、R+=4；`01e8` BLTU 3,n→01ce。不等从01d6设置index=0，无指针推进；剩余n<=3由01ec→01d6。word相等与字节次序无关，word大小未用于返回。 |
| 两条load是indexed unsigned-byte、无基址/index回写 | 接受原编码及与本地模型一致性；独立上游ISA认证未核 | `01ee=0x80e5478b`、`01f4=0x80e5c68b`：op=0xb、funct3=4、bits31:27=16、shift=0；rd/rs1/rs2分别15/10/14和13/11/14。既存 `th.lrbu` 构造器计算rs1+(rs2<<shift)，读1B零扩展，仅赋rd，无rs1/rs2赋值。 |
| 右基址减1和index先增抵消，两侧比较同一索引 | 接受 | `01d6` index(a4)=0；`01d8` a1-=1；`01ee`先读L[index]，`01f2` index+=1，`01f4`读(R-1)[index]。若循环开始index=i，两地址为L+i、R-1+(i+1)=R+i；`01f8`相等→01da，下一轮使用i+1。 |
| n=0不读buffer并返回0；相等返回0 | 接受，限正常合同 | `01da` BNE n,index→01ee；相等则01de置a0=0并返回。n=0时仍有a1算术减1，但不做内存读取。本次不推广异常地址合同。 |
| 首个不同unsigned byte左减右，范围-255..255；NUL不终止 | 接受，load零扩展语义依模型 | `01f8` BEQ相等→长度门控；不等直落 `01fc` SUB a0,a5,a3并返回。循环唯一继续条件为byte相等及index!=n，无NUL测试。两byte均零扩展，故补码返回解释为上述有符号差值。 |
| 无store、call、额外直接依赖 | 接受本68B窗口 | 25条原编码全部解码，只含load、寄存器算术、branch/jump和两处C.JR ra；无store/JAL/JALR调用。C.JR ra为返回，不当作callee。 |
| B10的20B调用在正常内存前提下，非零为内容不同 | 接受推论；沿用已验收调用点，未重核caller | B10/B11已核 `a00a86a8` 的a0=p、a1=payload+5、a2=0x14及86ac非零分支。本次只补helper含义；不认证p有效性、跨调用对象同一性、完整caller返回或响应。 |
| memcmp形状不等于开源来源/版本认证 | 接受；准确来源未核 | 本地完整函数证明比较算法形状；既有源码路径索引未绑定本函数到上游源码/版本。无唯一来源证据，不认证newlib/NuttX/厂商实现，不新增开源排除。 |

## 合同与控制流论证

正常前提为被读取的n字节可读、比较期间稳定，地址区间不绕回；参数按RV32 word传递。返回0当且仅当这n字节均相等。若最早不同索引为k，返回 `uint8(L[k])-uint8(R[k])` 的有符号32位结果。该合同不需要结构体、全局或直接callee。

word循环的不变量为已推进前缀的4B块全部相等；每次只在相等后同时推进两指针并扣除4。到byte路径时，未比较后缀的顺序未改变。byte循环开始index=i时，前i个byte已相等；两indexed load读同一i，返回前不再增加地址。由长度门控与首异即返回可得合同。此处是对已核指令的人工静态论证，没有执行模型或生成测试输入。

```c
// 语义投影，非原始源码；uint8读取语义依既存lrbu模型。
int32_t compare_501be(const uint8_t *L, const uint8_t *R, uint32_t n) {
    if ((((uintptr_t)L | (uintptr_t)R) & 3) == 0) {
        while (n > 3 && load_u32(L) == load_u32(R)) {
            L += 4; R += 4; n -= 4;
        }
    }
    for (uint32_t i = 0; i != n; ++i)
        if (L[i] != R[i]) return (int32_t)L[i] - (int32_t)R[i];
    return 0;
}
```

## 证据、实际验证与边界

[verify.py](../../analysis/compare-contract-review-b13-0041-20261023/verify.py) 是本次独立位域解码器，不调用B12 checker、反编译器或固件。只读主仓库ROM `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，按 `offset=VA-0x9ffff000` 读取offset 332222起68B。逐条解码标准/压缩opcode、寄存器、立即数和绝对分支目标，并与另列的25条操作数合同断言比较；核完整连续范围、既有dossier body与所有68B，另核B12保存字节序列及本地模型摘录一致。

[review-evidence.json](../../analysis/compare-contract-review-b13-0041-20261023/review-evidence.json) 保留25条VA/offset/原字节/独立解码与结果，关联既有dossier Evidence `ev_bcb6dbb168d8b5f6e23caa37ac3eb465a0ea1b6160de2e419ac51b904323a3ed`。本次运行 `python reverse/analysis/compare-contract-review-b13-0041-20261023/verify.py` 退出0：**passed，68B、25条原编码（23普通+2厂商），dossier/B12字节与既存模型一致**。脚本只写本任务证据，不是形式化证明或执行覆盖。报告逐项验收、循环不变量与来源边界经过人工核对。

事实为68B原编码、寄存器流、分支和返回；推断为ABI参数命名、memcmp形状名称及可读C投影。厂商load语义与无回写仅认证相对于既存 `ap01thead2.sinc` 模型的一致性，独立上游ISA认证未知。准确源码/版本/修改状态、实际内存/可达性、跨调用对象稳定性和完整响应仍未知。局部正常算法/参数/返回合同恢复完成，模块及全ROM目标仍部分恢复。

祖先及本树相关目录未发现适用AGENTS.md。已读REA skill；本次复用本地留存Evidence与原ROM，不开可写REA数据库/会话。没有执行固件、连接设备/外部服务、运行历史回放、缺陷/畸形输入验证、修改ROM/生产/安全检查/分析器模型；没有新增哈希或复制清单。差异检查后只暂存本任务独占报告和analysis文件并本地提交，禁止推送。

一个后继小任务建议：只恢复 [MiIO deferred settings](miio-deferred-settings-0041-20261023.md) 所称 `numeric_location_set_a009c5fc` 的正常参数/字段/返回合同，最多此函数及两个未解直接依赖。现有报告精确地址搜索仅命中该MiIO报告44/90行的调用说明和伪代码，未见函数体合同；这只证明报告检索边界，不代表全ROM无其他证据。主窗口指出kind=2直接提交点已经有界扫描过，因此不建议重复负扫描。这里未开展该函数的新逆向。
