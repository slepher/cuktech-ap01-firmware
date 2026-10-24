# Q14：正常 cmd59 状态生产到应用 refresh 可见性

**正常响应→缓存→item 两字段→同步通知的阶段已恢复，作者研究待独立复核。** 与 Q11 的连接是后续 refresh 从同一 item+0x14 读取状态；不是某次 cmd67 的因果确认，更不是协议物理生效证明。认领 Q-14，作者 `/root/app_protocol_research_02`，分支 `codex/app-protocol-research-02-20261025`，基线 `3a6602608e65ed7504bec657f829d463b504777d`。

采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存证据优先方法；全程静态读取，不开或切换共享 REA、不执行固件/模型/SIM/QEMU/回放/构建、不连设备或外网、不改 ROM/生产配置/分析器。布局名称和伪代码为分析命名。

## 查重与继承

只读主树 reverse-design 3.1/3.2/5.1/7、管理顶部/Q14。以 `a00a973e/cmd59/cmd0x59` 核主树报告的领域父级及较晚覆盖；[N02](telemetry-interface-n02-0041-20261024.md)的生产合同为51/52/56，[P17](port-response-p17-0041-20261024.md)为63/65；旧 uart-response 的14个用例没有59。P10含59但只覆盖查询时序，未覆盖这里两字段写入。未见可直接继承的完整 cmd59 writer 合同；这是有界覆盖检索，不声称全库不存在任何引用。

- [B19](uart-normal-parser-review-b19-0041-20261023.md)/[B21](queued-command-review-b21-0041-20261023.md)：正常 CRC、活动命令匹配及当前 handler 调用门；仅调用瞬间 handler 为 a00a8582 才适用本题。
- 固定 helper `a0191652` 沿 [UART response](uart-response-0041-20261023.md) 与 [P10](history-sampling-p10-0041-20261024.md)：按请求长度比较/同步复制 payload，变化时有 cmd+0x20 事件；不把描述符应答长度当成本片段的拷贝上限，不重做 copy 内部。
- [E01](uiiface-item-ownership-e01-0041-20261023.md)/[E02](uiiface-ownership-review-e02-0041-20261023.md)：T=`u32[62fcb2cc]`，T+0 为数组 A，T+6 为 u8 count，item stride 0x1a8；a00a389c 的同步借用通知、结束清 mask 合同。这里不重验容器创建或公共回调链。
- [Q11](app-protocol-research-01-0041-20261025.md)：a009c662 的两固定槽 refresh 与 item+14 读取、byte2 比较门及四协议反向映射。Q11 非作者复核另行进行；本题只接合 writer，不代替或重复转换器验收。

## 证据身份与原字检查

原件主树 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；offset=VA−0x9ffff000。来源主树 `reverse/analysis/uart-response-0041-20261023.json#/functions/0/normalized_result`，EID `ev_6f9f82e5daf0540a1c24a0b85daa2e394785391692765e5e3e100eb7b37ed94c`，完整 profile digest `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`（Ghidra 12.1.4、RISCV:LE:32:ap01thead3）。源 bundle 为 `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json`，其留存 source SHA `689b060f96eaba167291ecf78c8998e5aea590555e793cac735d448265d1d385`。

[verify.py](../../analysis/app-protocol-research-02-0041-20261025/verify.py)重新读 ROM 并核整件身份、留存 raw body 全字节及其 SHA；核本题74条原指令边界、3处 JAL、2处 SB 的源寄存器/byte宽度/偏移、3处厂商 indexed 编码字段。厂商 byte读和 word写语义参考主树只读 `evidence/rea-0041-20261017/processor/data/languages/ap01thead2.sinc:6410/6596`；源 profile 与局部语义参考分开记录，不把私有模型当独立上游 ISA 认证。ignored [instruction-evidence.json](../../analysis/app-protocol-research-02-0041-20261025/instruction-evidence.json)保存原字、文件偏移与字段，父窗需转存。

## 正常输入与生产合同

`a00a874e..8756` 比较完整入参 cmd 与0x59，命中跳 `a00a973e`。函数入口将 cmd/len 的低8位和 payload 指针存为栈 view（a00a85a0/85a4/85a8）；本题不赋予函数业务成功返回值。

| 阶段 | 原指令事实 | 可采用的接口约束 |
| --- | --- | --- |
| copy请求 | 9742 LBU count@62fcb01c；9752 左移3；9758 ANDI 0xf8；975c 调 helper | n=`(u8[62fcb01c]<<3)&0xf8`，等价 `(count&31)*8`，不是 T.count*8，也不是完整 count*8 |
| 目的/源缓存 | 974e 从62fcb6c4取 copy dst；976a 在 copy 后再次加载它 | 这是全局中的32位指针，不是把0x62fcb6c4本身当数据数组；copy后缓存 source 指针 S，S+1另存 |
| item循环 | 9764 先读T，非零才入；9786/978a 每轮重读全局T及其u8 count；97b8读当前T的A | i从0递增，以每轮 T.count 为实际 loop界限；copy请求数与 loop数是不同来源，不据此补一个 min/统一数量合同 |
| byte0 | 97bc `th.lrbu a6,s2,s7,3`，97c6 LBU item+14；97ce SB | unsigned `S[8*i]` 比较/写入 item+0x14，完整8位，无PD等映射或bit截取 |
| byte1 | 97f4 `th.lrbu a6,s9,s7,3`，97f8 LBU item+15；9800 SB | unsigned `S[8*i+1]` 比较/写入 item+0x15，其他6B在本循环不消费 |
| 变化发布 | a7每项先清零；byte0变置1000；byte1变 OR2000；9828 indexed word store | 两字节都不变不写mask/不通知；单变为1000或2000，两变3000；最终直接覆盖 item+0，**不是 OR 旧mask** |
| 同步通知 | 982c i&0xff→a0；9830调用a00a389c | 每个变化项一次通知，字段与mask已写好；index传低8位，原循环索引本身没有每轮截成u8 |

97bc和97f4的编码核得 rd=a6，base=s2/s9，index=s7，shift=3；9828核得 source=a7，base=s6，index=s5，shift=0。这排除把 indexed byte源误读成word源、把第二字段误当S+8或把mask写成RMW的解释。

```c
// 只作顺序说明，不执行；重读位置不可省略。
fixed_update(load32(0x62fcb6c4), (load8(0x62fcb01c)<<3)&0xf8, &view);
if (load32(0x62fcb2cc) != 0) {
    S = load32(0x62fcb6c4); // copy后缓存
    for (i=0; ; ++i) {
        T = load32(0x62fcb2cc);
        if (i >= load8(T+6)) break;
        A = load32(T); I = A+i*0x1a8; changes=0;
        if (load8(I+0x14) != load8(S+8*i)) {
            store8(I+0x14, load8(S+8*i)); changes=0x1000;
        }
        if (load8(I+0x15) != load8(S+8*i+1)) {
            store8(I+0x15, load8(S+8*i+1)); changes |= 0x2000;
        }
        if (changes) { store32(I,changes); notify(i&0xff); }
    }
}
advance_queries(); // a0191746，无需有字段变化
```

伪代码的load表达式是语义压缩，机器代码对每字段源只加载一次并用于比较/写入。首次T非零门不是每轮空检查；不从动态重读推导并发替换安全性。缓存 S 是在helper之后取得，循环/回调间不重载它；T/count/A则每轮重读。没有新增分配/释放或指针所有权转移，S与item沿已存对象借用；同步 callback不可凭此持有item用于异步访问。E02的walker在完整同步分发后清缓存数组中的mask，不能把mask当可持久查询的状态字段；+14/+15作为item状态继续存在，受原容器寿命约束。

## 相等路径、查询推进与 refresh 接合

helper是否发现raw变化不作为item循环门；即使raw相等，也会按正常控制流检查item。两字段相等只跳过本项通知，循环结束仍到9792调用 a0191746；初始T为空也走同一查询推进。selector返回非零转85e4，返回零后按62fcb508选择后续既有路径（0→9aac，非0→8824且cmd暂值5b），本题不展开尾部。继承P10：慢组包含50/51/57/59，period10，前有58组；这只是查询机会/推进合同，不承诺响应年龄或固定采样率。

接合Q11：端口0/1 getter成功时refresh读 `u8[item+0x14]`。本题byte0状态因此在**后续真正调用refresh**时可见；不是“9828写mask后必然即时执行refresh”的已证直接边。refresh比较整byte与槽byte2；不同则保存整byte并反解mask的0x08/10/20/80到槽byte0协议开关，只有四映射字段改变才使其bool返回true。只变其他mask位会更新byte2而bool仍false；同byte2则不重新计算，即使此前setter改过byte0。+15的0x2000通知不构成本题已证的Q11配置刷新输入。

Q11 setter先refresh再本地修改/普通提交；本题生产后再次refresh只能证明应用获得了peer普通查询所报告的状态。未建立 cmd67某请求→本次cmd59 的相关ID、成功码、持久化或物理协商链；既有协议配置即时通知低8位也不能替代这些证据。

## 验收与剩余边界

已完成静态检查：copy请求表达式与实际loop分离、两byte源/写宽、mask直接覆盖、相等不通知仍推进、缓存与回调借用、Q11条件refresh接合；没有重做转换器/submit或扩MCU、公共copy、queue、异常回放。脚本检查通过，合同JSON可解析，git diff --check通过。作者结果仍待非作者独立复核。

未闭：S与T生命周期/数量初始化跨阶段全局不变量，本轮不补异常路径；+15应用消费本题只记录writer不扩下游；没有从cmd59观测反推特定cmd67完成。已知后继若要证明请求相关确认，必须另给真实响应/关联种子，不能无种子搜索67凑量。

预计5–9分钟、中置信。首次可得UTC读数2026-10-24 17:01:23.838，之前规则/证据读取未计；检查完成17:03:58.217，实测时钟区间154.379秒，完整启动时间不可精确恢复。无排队/中断；工具同步等待未独立计量，token不可得，不造有效工时。提前闭合即交付。ignored原字产物11556 B，SHA256 `62ee62a106c95ce3c38b86197f77e4ab1c0bcc8d5bbd2e2535a8406e92d71c3b`，父窗逐字核对转存后再清理；本题不删除工作树。
