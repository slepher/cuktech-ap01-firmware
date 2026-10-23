# A20：天气图标条件闭包独立复核

2026-10-23；研究基线 `f40ea13ef4dc5ec2466f2e66431c3b7c01b6d4e5`，独立分支 `codex/re-0041-a20`，复核者非 A19 作者。结论：**有一处实质纠正后限定接受 A19**。两个整数转换、ctx 图像控件生产、32 bit 图标传递、code/q 映射、ROM 描述符选择、category15 先 remove 再 add、class0 source 借用/旧源释放、info 成功后的字段/更新调用均成立。纠正为 add 内部 `a00d8ffe` 实际调用 `a00d7546(obj,2)`，测试 **obj+0x28 的 unsigned16 状态**，不能用 A19 所写 `a00d7446(obj,2)` 的 **obj+0x24 word flags** 替代。详见下文逐字节纠正和伪代码。

本验收不证明实际 decoder 已注册、PNG info 已成功、widget 已绘制，或整个天气 UI/ROM 已恢复。遵循 [共同规则及完整 A20 任务书](rolling-management-0041-20261023.md)，使用 `reverse-engineer-anything` skill；读取了 [A19](weather-icon-flow-a19-0041-20261023.md)、[weather-dataflow](weather-dataflow-0041-20261023.md)、[A15](weather-subscriber-a15-0041-20261023.md)、[A16](weather-subscriber-review-a16-0041-20261023.md)、[A18](weather-current-review-a18-0041-20261023.md)。旧分发/arc/getter 只针对核接口。逐级检查本 worktree 祖先、根及输出目录，未发现适用 AGENTS.md。

只新增本报告和独占 analysis 文件；未更改 A19、共享索引、主树、其他 worktree、ROM、生产/构建代码或分析器模型，未创建下级 agent。所有检查为离线字节读取、反汇编和编码/文档一致性核验；未打开或切换共享可写 REA 会话，未执行固件、仿真、输入/历史回放、设备/服务连接或缺陷验证。

## 独立证据与范围

原件只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，身份沿用 A19/既有 dossier 的 SHA-256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，本轮未重新散列或制作哈希/复制清单。映射为 `file_offset = VA - 0xa0000000 + 0x1000`。

- [verify.py](../../analysis/weather-icon-review-a20-0041-20261023/verify.py)由本复核独立编写，直接读取原件，未调用 A19 的验证器。普通指令由 Capstone 5.0.7 解码；另外独立按位提取 RV32 I/S/B/J/U/R 与 RVC memory/branch/jump/CR 编码，验证调用、参数、写宽、分支和厂商字。脚本不解释执行控制流或输入。
- [instruction-review.json](../../analysis/weather-icon-review-a20-0041-20261023/instruction-review.json)保存原字节、文件偏移、反汇编、各行 raw_fields、179 项命名编码断言、12 个可达资源、ROM 字符串、厂商模型原文；[instructions.txt](../../analysis/weather-icon-review-a20-0041-20261023/instructions.txt)供逐地址审阅。
- 独立重提取 A19 的11核心和2必要 flag 谓词，并为纠正新增88 B的 `a00d7546..759d` 状态谓词。核心全字节范围见本轮 `windows`；语义限本天气链正常分支，不能把文件/符号/缓存、诊断和所有 image 类型视作完整验收。
- 必要窗口为构造调用 `a00a7f7e..7f9d`、两次生产转换 `a00aa58a..a5e1`、完整 callback `a00ab6b0..b753`。完整 callback 保留为核对图标参数/返回覆盖的上下文，不重做 arc 内部。
- 新读出的原字节逐行与 A19 留存1011行全部相符。这只是数据一致性佐证；A19 文本解释与自己的断言仍须独立核对，正因此发现上述 callee 误记。
- 新增谓词的历史范围出处为 `whole-rom-coverage-0041-20261023-round1.json` 中 `a00d7546` extent Evidence `ev_5fa5a5a0ce059d71f6f18900741dc6cff519ad7588c32e2401ae224d4f186af4`；本轮没有借此冒称新 REA 观测。其正常末尾逐字节由原件重取。

## 逐项裁定

以下接受仅指可定位指令事实或明确保留的先前合同；业务名字及未展开依赖不因此认证。

| A19 主张/闭包位置 | 判定 | 独立依据与边界 |
| --- | --- | --- |
| `now.ico` 产生两个 word 槽 | 接受 | `a00aa5ce/5d8` 各 `C.MV a0,s3`；`5d0/5da` 两个 JAL rd=ra，均到 `a0053f46`，分别 SW 到 `s0-0xc0/-0xbc`。相对先前 weather 基址 `s0-0xdc` 为 +28/+32。不能合并转换。字符串转整数内部及156 B生产/分发合同沿用 weather-dataflow，本轮未重做。 |
| `ctx+0x20` 的图像控件生产 `a00a5d5c` | 接受 | `a00a7f7e` LW a1,24(s2)，`7f94` a0=a1；a2常量 `a0251da8`，a3=19/a4=40；`7f96` 调 glue，`7f9a` SW a0,32(s2)。glue 先创建 `a00ed0a8`，保存返回 word，调 image setter，再 `(widget,reference,1,x,y)` 调 `a00dbb68`，重载保存 word 返回。创建/布局内部分别保留边界。 |
| callback 参数为 `load32(ctx+0x20),icon` | 接受 | `a00ab6c0/6ca` 两次 C.LW 得到 wrapper/ctx；`6d0` LW s3,28(a0)；`710` 原字节 `8850` 解出 C.LW a0,32(s1)，`712` `ce85` 为 C.MV a1,s3，`714` 调 `a0198946`。不是 ctx+32 地址，不截断 icon；+32第二槽未读。 |
| `a00a6998` unsigned 分组及 q 不对称 | 接受 | 全函数所有 branch raw_fields留存，范围差值按RV32模运算、BLTU/BGEU；`69d0/6a0e/6a7e` 为 SLTU zero,q 即 SNEZ，`69fe/6a20/6a92` 为与1的 BNE。q仅在相应分支以 LBU 读取 `62fc405f`，无写。完整表见下一节。 |
| `a0198946` mapper→remove→selector | 接受 | `8956→a00a6998`，`8960→a00d9044` 在所有类别分支前；每个可达资源臂的 LUI/ADDI重构 a1并汇合 `8a1e/20→a00ed560`。`89ce` BEQ 到 `8a94`，`8a98→a00d8f7c`；category15不调用 image setter。 |
| `a00d9044` 清 word flags及请求顺序 | 接受，限 mask1 | `9098→a00d749e` any；无位早退。有位先 `90a0→a00d8f02`，`90ce` 重读+0x24，`90da` C.SW 写 AND NOT mask；随后 `dddf4(obj)`、`8f42(parent)`、`8f42(obj)`；末次 `8f02` 不等于先前结果才另调 parent。mask0x10分支不在本链。 |
| `a00d8f7c` add 初门是 all flag 谓词 | 接受 | `8fd2→a00d7446` 正确；已有 bit1(数值1)则返回，否则先 `8f02`，再 `dddf4(obj)`，`8fee` 重读+0x24、`8ff4` C.SW OR mask。 |
| add 写位后 `a00d7446(obj,2)` | **纠正** | `8ffe` 原字节 `efe08fd4` JAL目标是 `a00d7546`。其正常体 `7592` LHU +0x28，AND mask，SNEZ；不是 +0x24 的 all-flags。下文给完整替换合同。 |
| `a00d7446/a00d749e` 各自的非空谓词 | 接受 | `7492/74ea` 均 C.LW a0,36(a0)。前者 AND、SUB mask、SEQZ，后者 AND、SNEZ；即全含/任含。它们仍分别服务 add入口与remove入口，不能拿来替代状态谓词。 |
| `a00dd454` 将本源分类为0 | 接受 | LBU首 byte，`(byte-0x20)&0xff <=0x5f` 返回1，否则 `(byte>>7)<<1`；NULL为3。12个可达描述符首 byte都是0x19，故分类0。没有展开类别1/2/3的 setter合同。 |
| `a0082e32/a0082c8c` info ABI与成功 | 接受，条件性 | wrapper局部+0xc SW source、+0x10 SB分类，调用dispatcher后 SNEZ。dispatcher对class0验证 source+0x10非零，遍历registry节点+0/+4非零门，重载+0经 C.JALR 调 `(node,&local,out_header)`；结果须==1才接受。callback身份/注册未核。 |
| `a00ed560` class0指针和旧源释放 | 接受 | info成功、aux guard通过后才读旧类型。`6c0` extu→`6c4` BLTU限定旧类型1/2时 `6c8`取旧+0x2c、`6ca`调释放；`6ce` SW新ROM描述符。class0无新分配/复制；不释放旧类型0。 |
| image宽高/格式写和更新顺序 | 接受 | header+4/+6为 LHU，写obj+0x3c/+0x40是word；header byte1格式读为LBU，重读obj+0x58 byte，SB更新低byte。依次 `a01b1ee6`、`a00ed438`、变换字段门、可选 `a00d89c6`、`a00dddf4`。不等同物理显示。 |
| `a01b1ee6` sentinel请求 | 接受，getter内部未核 | 两个 AUIPC/JALR分别核到 `a00901cc/a00901e2`，a1各为0，第二调用保留obj。任一结果==0x3fffffff才调 `a00d8f42(obj)`。 |
| `a00ed438` 四种缩放模式 | 接受，依赖边界保留 | mask0xf00模式b/c/d/e；各先 `a00ed198(obj,0)`、`a019dd98(obj)`。b/d/e要求源宽高非零，经必要helper和getter，以重读的源宽高为除数做signed DIV；b双轴独立，d signed min，e signed max，c双轴256；共享 `a00ed314`调用。原字/重读详见后文。 |
| PNG格式等于decoder成功、所有image类型已恢复 | 未核且不接受此类外推 | A19正文未声称成立。本轮只检查12个可达描述符、signature/IHDR，不重新认证额外资源臂5/10/17/22/23，未跑decoder。|

## 实质纠正：状态门不是 flag 门

A19 **“flag 状态与更新副作用”** 中句子“随后若 `a00d7446(obj,2)` 非零……”须以本节为准；A19其它地方关于两个 flag 谓词的定义本身无需更改。其顶层 `icon_update` 伪代码只表达 remove/add 顺序，仍成立。本报告不改写 A19 原文。

```text
a00d8ffa 8945       c.li a1,2
a00d8ffc 2685       c.mv a0,s1
a00d8ffe efe08fd4   jal a00d7546
// word 0xd48fe0ef: opcode=0x6f, rd=1, signed J imm=-0x1ab8
// a00d8ffe - 0x1ab8 = a00d7546

a00d7592 03558502   lhu a0,0x28(a0)
a00d7596 6d8d       c.and a0,a1
a00d7598 3335a000   snez a0,a0
a00d759c 8280       c.jr ra
```

`a00d7592` word `0x02855503` 的 opcode=3、funct3=5、rd=rs1=10、imm=40，明确是 unsigned16读取。ROM诊断名 `a0569930` 为 `lv_obj_has_state`；该字符串支持“状态”的业务名，但该门的最强事实是 `((load_u16(obj+0x28) & 2)!=0)`。与之相反，`a00d7446` 从 +0x24读取word，并返回全包含。两个字段、位宽和谓词语义均不同；数值mask=2不能被解释成同一对象flag。

正常mask1 add 的必要可读合同如下。函数名/字段名为分析视图，返回寄存器值不自动等价原始C返回声明；不展开这些request/group候选helper内部。

```c
add_mask1(obj) {
    if (a00d7446(obj,1) != 0) return;       // all FLAGS predicate
    before = a00d8f02(obj);
    a00dddf4(obj);                         // 位更新前
    store32(obj+0x24, load32(obj+0x24) | 1);
    if (a00d7546(obj,2) != 0) {            // STATE: load_u16(obj+0x28)
        g = a00d759e(obj);
        if (g != 0) {
            a00d85ea(g);
            v = a00d73c6(g);
            if (v != 0) a00dddf4(v);       // 保留a0返回值作为实参
        }
    }
    after = a00d8f02(obj);
    if (after != before) {
        a00d8f42(load32(obj+4));
        a00d8f42(obj);
    }
}
```

影响范围：category15仍执行 `remove_flag(obj,1)` 再 `add_flag(obj,1)`，不替换/释放source；**加位后是否进入 `a00d759e→a00d85ea/a00d73c6` 的条件必须由状态+0x28决定**。不能据flag+0x24的bit2状态预测该支路。初始已有隐藏位时 remove会实际清位并发请求，随后add再写位；初始无该位时 remove内部早退，仍然保留顶层调用，再add。两种初态的最终bit均为1，调用/失效序列却不应合并。该纠正不改变mapper结果、资源地址、class0 info门、source所有权或宽高/格式写入的验收结论。新增短依赖只为闭合这一正常门，无全状态机扩扫。

## 图标生产、映射和资源串接

生产两个槽的真实顺序为同一s3字符串指针两次调用 `a0053f46`，各自保存word返回。输入天气对象是同步发布中的借用指针；本callback只预读标量到寄存器，不把输入指针交给图标mapper/selector，也不写天气对象。初始图像由 `a00a5d5c` 把创建返回的widget交给image setter，返回保存至ctx+0x20；以后回调从该槽加载指针。ctx/控件的最终销毁仍断开。

完整code表复核如下；所有区间是原始32bit值按unsigned比较，差值按RV32截断。q为路径内LBU `62fc405f`，没有提前无条件读、没有本函数内写。表是静态控制流归纳，不是执行样例或回放。

| code | category |
| --- | --- |
| 100；101..103 | `1+(q!=0)`；`3+(q!=0)` |
| 104 | 6 |
| 150；151..153 | q==1选2否则1；q==1选4否则3 |
| 300..301；350..351 | `8+(q!=0)`；q==1选9否则8 |
| 302..304 | 11 |
| 305..318、399 | 7 |
| 400..403、405、407..410、457、499 | 12 |
| 404、406、456 | 13 |
| 500..515 | 14 |
| 其余32bit code | 15 |

`a00a6ae4` 的 ANDI -3用于406与404归并；`6af2` 的 SLTU是与unsigned差值比较后再加14。没有把全部q非零视同q==1，也没有把q命名为已认证的昼夜模式。所有可能category为 `{1,2,3,4,6,7,8,9,11,12,13,14,15}`。

本轮独立资源检查只覆盖这12个非15结果：category→描述符依次为 `1:a0251da8, 2:a062ff20, 3:a062fb30, 4:a062fd24, 6:a062eee8, 7:a062f2bc, 8:a062f414, 9:a062f618, 11:a0630658, 12:a062f9a4, 13:a062f834, 14:a062f16c`。LUI+ADDI均按有符号12bit低立即数重构，不能从常量文本猜资源。16种setter资源与category17别名在A19有留存，本轮不要求全部额外臂资源格式通过才接受本链。

每个可达描述符实读28B为7word：`{0x119,0,0,size,payload,0,0}`，payload=descriptor+28。独立检查PNG signature/IHDR，宽高除category1为19×19、category3为20×16外均20×20。描述符中+4/+8为零，不能从这两个word直接赋控件宽高。PNG CRC/完整块链本轮未重新核，沿用A19留存且不影响本轮来源/条件性裁定；signature/IHDR不证明decoder返回1。

## info、source更新与所有权

最小RV32存储视图如下，不是完整C结构定义：

| 对象或局部偏移 | 宽度 | 正常链事实 |
| --- | --- | --- |
| weather+28/+32 | word | 两次转换结果；callback只读+28 |
| ctx+0x20 | word pointer | 创建返回保存/回调加载 |
| widget+0x24 | word | flags，包括本链数值1位 |
| widget+0x28 | unsigned16读取 | 新核状态谓词；仅mask2正常分支 |
| widget+0x2c | word pointer | source引用，class0直接保存ROM描述符 |
| widget+0x3c/+0x40 | word | zero-extended header u16宽高 |
| widget+0x44/+0x48/+0x4c | word | 后段变换比较门：0、256、256 |
| widget+0x58 | byte写/halfword读 | 低2位source类型、bit2..6格式、保留bit7；高byte通过SB保持 |
| wrapper info local+0xc/+0x10 | word/byte | source和分类；局部大小参数0x4c |
| out_header+1/+2/+4/+6/+8 | byte/u16/u16/u16/u16 | 格式、aux guard flags、宽、高、stride；总初始化大小参数12 |

`a0082e32` 调 `a0080d8e(local,0x4c)`，写source/type后调dispatcher；dispatcher也调该helper `(header,12)`。本轮只保留初始化helper合同边界，未独立认证其完整实现为memset。class0的source+0x10非零门由所有12个payload指针满足，但registry/cache对象的运行初始化未因此证明。

必须保留dispatcher共同前缀：`a0082cea` LW registry+0x120取得cache对象；`a0082cf4` **无条件先LW该对象+8**，随后才按type分流。class0跳过的是文件型缓存查找/打开等后续操作，不能据A19“跳过文件/缓存预备动作”的概括删除这次共同读取。registry基地址 `62fc957c`，链头+0x114；每节点+0和+4非零；辅助位置local+0x14准备后，重读node+0并以 `a0=node,a1=&local,a2=header` 间接调用。返回须严格等于1。失败从registry+0x110读步长，然后从node+step+4取下一个节点；无节点返回0，wrapper SNEZ为失败。

成功时若header stride为0，格式20写 width×2，其他格式调用 `a00897c2(format)` 取得因子，RV32乘/加7/右移3后以SH写回header+8。该格式因子helper、registry注册及真实info callback仍未核，不能推定输出是IHDR尺寸或默认flags。

image setter本链顺序为：

```c
a00dddf4(widget);                         // 分类/info以前已有请求
type = a00dd454(src);                     // 本源=0
ok = a0082e32(src, &header);
if (ok != 1) { failure_log(); return; }
// 实际读的是header+2的u16；两个aux指针来自src+0x14/+0x18。
if ((load_u16(header+2)&0x10) != 0 &&
    (load32(src+0x14)==0 || load32(src+0x18)==0)) {
    aux_failure_log(); return;
}
old_type = load_u16(widget+0x58)&3;
if ((uint16_t)(old_type-1) <= 1) a008ab8a(load32(widget+0x2c));
store32(widget+0x2c, src);
w = load_u16(header+4); format = load_u8(header+1);
store32(widget+0x3c, w);
h = load_u16(header+6);
store32(widget+0x40, h);
b = load_u8(widget+0x58);                  // 写宽高后重读
store_u8(widget+0x58, (b&0x80)|((format<<2)&0x7c)|(type&3));
a01b1ee6(widget);
a00ed438(widget);
if (load32(widget+0x44)!=0 || load32(widget+0x48)!=256 ||
    load32(widget+0x4c)!=256) a00d89c6(widget);
a00dddf4(widget);
```

12个ROM描述符的aux word均0，所以本链在info成功后还需header+2的0x10位为0才到覆盖source；这是静态条件归纳，不是decoder输出观测。失败不会到新source/宽高/格式写入，却已经发生selector remove及setter最初的失效请求，不能说失败时控件完全不变。

所有权接受：class0新source不分配、不复制，widget持有ROM描述符借用引用，header是临时局部且不被持久保存。旧source类型1/2才先free旧+0x2c，再覆盖；旧类型0不释放。allocator的free职责沿用既有合同，本轮仅核调用条件/参数。category15不触发source setter；同一有效资源在非15路径没有去重早退，仍重新info和提交请求。天气输入指针未交给这些图像callee；widget/context销毁、并发存活/订阅注销不在本闭包。

## 更新依赖与厂商编码

`a01b1ee6` 的两个PC相对调用按 AUIPC/JALR 原字求和分别得到 `a00901cc/a00901e2`，任何一个结果等于0x3fffffff才调尺寸/区域请求 `a00d8f42(widget)`。本轮不重新认证这些getter内部，也不把sentinel判断改成其他大小限制。

`a00ed438` 模式b/d/e先检查source宽高各非零，再调用 `a00d929a(widget)`，取W/H getter；计算比例的除数在helper之后从widget+0x3c/+0x40**重新加载**，不以先前非零检查的寄存器值代替。`(W<<8)`/`(H<<8)`是RV32值，指令为signed DIV。模式b传两轴独立比例；d/e经signed比较选择相同比例到a1/a2；模式c传256/256。`a00ed314`内部和最终rasterize/物理刷新未展开。

本轮四处未知于普通Capstone的厂商word逐一核原字和既有只读模型：

| 地址 | 原little-endian字节/word | 字段与裁定 |
| --- | --- | --- |
| `a00ed5f8/a00ed6c0/a00ed748` | `8bb7073c` / `0x3c07b78b` | opcode11/funct3=3、rd=rs1=15、msb15/lsb0；对应模型 `th.extu a5,a5,15,0`，保留低16bit。仅6c0属于本class0旧源释放门，另两处不扩展语义验收。 |
| `a00ed4f2` | `0b16f942` / `0x42f9160b` | opcode11/funct3=1/funct7=33、rd12/rs1=18/rs2=15；模型 `th.mvnez a2,s2,a5`，条件非零才移动。d用SLT s2,a2选min；e用SLT a2,s2并在 `a00ed540`跳回此字选max。 |

模型路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc`，相关原文/行号保存于本轮JSON。该相互核对不等于新增外部厂商ISA认证或芯片运行观察，未改模型、未用反编译补未知word语义。所有image/flag/selector返回均没有统一scalar成功合同；callback在 `a00ab718`开始准备日志并覆盖a0，不消费icon更新返回。

## 来源、未核项和实际验证

事实：图标双次转换/word槽、控件创建胶合与ctx指针、unsigned完整映射及两类q门、12个可达ROM描述符及PNG标识/IHDR、remove/add原序、纠正后的u16状态门、class0/decoder间接ABI/返回==1、旧类型决定free、header读写宽度/重读、更新调用和返回覆盖。业务推断：q的昼夜/模式意义，flags数值1的隐藏名，部分getter/缩放/helper业务名。未知：q写者、decoder注册和真实info节点、完整创建/布局/失败分支、精确资源符号/气象名称、UI/context销毁、最终物理显示和库版本/厂商修改。

来源依据：原ROM字符串 `lv_image_set_src`、LVGL `src/widgets/image/lv_image.c`路径及新增 `lv_obj_has_state` 等名称支持LVGL来源候选；不证明准确版本或原样实现。厂商glue角色由业务边支持，原函数名未知。新增已认证开源排除为0；初始化、allocator、GUI request依赖均保留明确边界，不因库候选就静默排除。

实际运行本轮 `verify.py` 通过：[review-index.json](../../analysis/weather-icon-review-a20-0041-20261023/review-index.json)记录 **11核心+3必要谓词，17窗口，3286 B，1083条指令，179项原编码断言，4个厂商word，A19原字节1011行匹配，12个可达资源，剩余未解码指令0**。首次断言在 `a00d8ffe` callee处失败，证实是上述A19误记后增加88B短依赖并按原件纠正本轮预期，复跑通过；没有把失败压制或修改ROM/分析器模型。另检查报告相对链接、独占文件范围和 `git diff --check`，均通过。这些是静态验证，不是固件/decoder执行成功或硬件显示测试。

恢复程度：A19本天气正常条件闭包有纠正后限定接受；必须沿用本报告的状态门，其余已验收合同边界保留。一个后继小闭包：仅从 `62fc957c+0x114` 的decoder注册生产者追至本PNG资源需要的info callback，核成功返回、header格式/flags/宽高写入；不扩全decoder库/最终绘制。本轮无工具阻塞，保留该断边，不自行领取后继。
