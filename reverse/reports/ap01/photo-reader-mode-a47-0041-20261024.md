# A47：非零 reader mode 的构造与资源归还

2026-10-24；基线 `e2991b9`，分支 `codex/re-0041-a47`。**setter 的分类结果1分支确实以同一 source 调 `a0107d8e`，建立 mode=1 的 driver reader；成功后由既有构造器复制到 O。`a01b2e3a(O)` 调 O 所持 driver 的 +0x10 回调，条件归还缓存，随后清 O 的前三个 word。** 不能直接把此函数命名为 `fclose`，也未证明默认五张 ROM 照片实际进入非零 mode。采用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，只读主仓 ROM/历史证据；没有打开共享 REA target。

## 继承结论：已有出处、行为与局限

|已有出处|直接继承的行为|证据局限与本题实际缺口|
|---|---|---|
|[A41](photo-decoder-destroy-a41-0041-20261024.md)、[A42](photo-destroy-review-a42-0041-20261024.md)|oldO=owner+0x5c；U8(oldO+0x10)非零才以 a0=oldO 调 `a01b2e3a`，之后整体 free(O)，清 owner+5c/+74|只认证目标、实参与外层顺序；本题补 callee 内部资源归还和对应非零构造|
|[A33](photo-source-abi-a33-0041-20261024.md)、[A35](photo-source-review-a35-0041-20261024.md)|正常五资源是 ROM descriptor+0x10 data → mode0，借用 ROM 输入|不能把 setter 具有文件型候选分支改写为实际五照片以文件打开；mode0析构全继承|
|[A37](photo-decoder-owner-a37-0041-20261024.md)、[A39](photo-decoder-review-a39-0041-20261024.md)|同一 `a010a65a(W)` 成功时分配单块 O，copy(O,W,0x664)，owner+5c=O、+74持内部派生区|直接复用复制/持有合同；本轮仅把 mode1 的 W 前缀接上，不重导构造器或算法|
|主仓 `photo-evidence-round3.json#/rea_records/3`，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`；main-knob round2/system complete；最终 ZIP/SIM 合同|照片轮转、caller及替代实现已有|不以业务 caller 或替代实现认证非零 reader 内部；未执行/解包资源|
|主仓 `weather-calendar-complete-0041.json#/evidence/30`，address=`A010A302`|较早 objdump 已留 reader `a010a5d6` 的 mode 门和非零调用 `a008b888`|旧 stdout 明示截断；本轮只引用该 reader 分流，不将其算新功能或扩 read/seek 算法|
|主仓 `page-logic-0041.json#/records/15`，`ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`|清零 helper dossier 的 incoming caller 已有 `a0107d8e`|是 caller 记录，非 `a0107d8e` 的完整构造合同|
|whole-ROM round1：`a01b2e3a` extent `ev_ec1bdb465c5285588d9902692167d9cad1269b7a6dffaf198bf0a9682018058e`、direct calls `ev_d78eb655cefbb3b29310d1ac98b8d3519ba63de4f3bff158f7a0a334d6818af0`|函数范围 `a01b2e3a..a01b2e8d` 与 free-wrapper依赖已有|清单不是函数内部恢复；不能当此前完全未知函数。直接调用者还含其他图像入口，本题不扩全部caller|

本轮对主仓 `reverse/rehost/*.json`（含 photo/较晚 round3/complete）按 `a0107d8e/a019d6a4/a01b2e3a` 有界检索，仅 page-logic 命中前一地址；未命中不证明历史上从未分析。原 ROM 身份与 VA 映射继承 A33/A37，不新增哈希清单。

## 本轮复核或纠正

不纠正 A41/A42 的模式门和实参。非零 mode 表示同一 reader 前缀走 driver 接口，不能因源字段看似指针就把 `a01b2e3a` 叫作输入 free。必要原字节及56项检查见 [evidence.json](../../analysis/photo-reader-mode-a47-0041-20261024/evidence.json)。

ROM `a02631a8` 的路径串以 `/lvgl/src/misc/lv_fs.c` 结束，`a063137c` 是 `lv_fs_open`；后者被 `a019d6a4` 的诊断引用。它们支持“文件接口型 driver reader”的解释，不能认证库版本、编译来源、标准 `FILE*` 或任何具体文件系统实现。本文继续用地址及 D/H/C 字段名。

## 真正新增：同一非零 reader 的正常构造与归还连接

`W=s0-0x674` 是 wrapper 栈工作区，O 是既有单块对象，D/H/C 是分析命名；不是原源码类型。以下只恢复普通 driver 回调成功路径，条件本身是静态事实，不表示观察到实际调用。

|原地址|参数、返回判断及持有|
|---|---|
|`a00ed876..882`|分类结果等于1才以 a0=s3=原 source 调 `a0107d8e`；返回到既有非零 O 判断/owner持有。其它分类不是这条构造路径|
|`a0107da2..7dc6`|保存 source；清零 W 的0x664字节；SW清 W+0x0c、W+0x14，**SB W+0x10=1**。随后 `a019d6a4(a0=W,a1=source)`；不是传 source 指向数据的首word或 source+0x10|
|`a0107dca..7dd0`|初始化返回 a0=0 才 `a010a65a(W)`；非零返回走原零结果分支。该0表示初始化结果，不是 handle；不能把成功零结果写入 O作为H|
|`a019d798..7bc`|初始化路径把选定 D 保存 W+4；D+4 控制缓存配置；非零配置申请0x10字节缓存结构并保存 W+8。此处不是为每个模式都申请输入缓冲|
|`a019d80e..828`|普通 D+4 != 0xffffffff 分支：取 `fn=word[D+0xc]`，以 a0=D、a1=此前由 source 得到的后缀、a2=2 间接调用；正常接受的返回值 H 保存 W+0。非空 source 的后缀在初始选择段是 source+1 或第二字节为冒号时 source+2。具体 D 注册和 fn 身份未闭|
|A37既有 `a010a7b8..7c2`|后续读取/构造成功后，copy(O,W,0x664) 持有 **当时** W 的前三word及 mode；故 O 的 reader 前缀不是指向 W 的栈地址。保持各下层调用可能更新缓存状态的原序，不发明入口H在所有阶段永远不变|
|`a01b2e44..e50`|保存 O=s1；a0=word[O+4]=D；D非零且 word[D+0x10]非零才继续，以 a1=word[O]=H 调该间接槽。**a0 是 D，a1 是 H**；并不是 `callback(O)` 或 `free(source)`|
|`a01b2e52..e74`|回调返回后重新读 D=word[O+4]、配置=word[D+4]。配置非零且 C=word[O+8]非零才归还缓存；配置 != 0xffffffff 且 word[C+0xc]非零时先 `a008ab8a(word[C+0xc])`，再重读 O+8 并 `a008ab8a(C)`；配置=-1跳过前者但仍归还C|
|`a01b2e78..e80`|回调已调用的路径随后依次 SW清 O+0、O+4、O+8，包含配置0或C为空的汇合。入口 D为空或回调槽为空则跳过整个清理/清槽块；不能改为无条件清槽|
|A41/A42外层|setter随后整体 `a008ab8a(O)`，再清owner+5c/+74。callee 内部的两个缓存归还与外层O归还是不同分配根；D没有作为free实参。mode字节没有在这个callee清零|

必要伪代码，非原源码；保留回调后的重读及缓存条件，不给未知返回类型命名：

```c
// a0107d8e：source类型1入口
zero(W, 0x664);
store_u8(W + 0x10, 1);
if (a019d6a4(W, source) != 0) return 0;
return a010a65a(W);                 // A37：复制当时状态到O，再返回持有

// a01b2e3a(O)：由A41非零mode正常替换调用
D = load32(O + 4);
if (D == 0) goto out;
fn = load32(D + 0x10);
if (fn == 0) goto out;
fn(D, load32(O));                   // 返回值不作条件判断
D = load32(O + 4);                 // 原程序重读
config = load32(D + 4);
if (config != 0) {
    C = load32(O + 8);
    if (C != 0) {
        if (config != 0xffffffff && load32(C + 0xc) != 0)
            a008ab8a(load32(C + 0xc));
        a008ab8a(load32(O + 8));
    }
}
store32(O + 0, 0);
store32(O + 4, 0);
store32(O + 8, 0);
out: /* 不认证返回状态；caller直接继续free(O) */;
```

资源解释：O 前缀持有 D/H/C；D的+0x10槽承担H对应资源的归还动作，通用层只负责调用并归还缓存。H是否真为某种文件句柄、该回调如何关底层资源，必须由具体D绑定/回调实现证明；这里没有 `free(H)`。缓存+0xc在配置=-1时不归还、其它非零配置时条件归还，说明该字段存在不同归还责任；其申请/填充及更深读取路径不在本题。初始化 `D+4=-1` 的特殊自指分支也不纳入上述普通open成功合同，不把它误写成回调H。

## 未闭精确边与必要静态验证

已闭问题是 setter 的非零构造种子、W/O前缀对应、`a01b2e3a` 的真实寄存器实参、缓存归还条件、重读及清槽顺序。事实为原字节调用/位宽/保存/分支；“driver reader/缓存资源”是结合诊断串及上述字段用途的解释。新增是这些连接，旧照片业务、mode0与A37复制算法的复核新增功能均为0。

未闭的是 **这条source类型1实例选择的具体D及 D+0xc/+0x10 回调地址**，因此不能认证底层文件系统、H具体类型、真实关闭成功与运行期资源复用；默认五ROM照片仍继承mode0，不声称实际非零调用。缓存+0xc首次分配/填充、全部失败臂、库精确版本均未展开。唯一后续闭包：若已有真实source类型1 caller/路径实例，再从其首字节与注册项绑定定位同一D的构造/归还回调；缺该种子时保留本报告的接口边界，不扩全文件系统。

[verify.py](../../analysis/photo-reader-mode-a47-0041-20261024/verify.py) 只读主仓ROM及历史JSON，保存7个必要短窗，56项检查通过；独立拆 JAL、AUIPC/JALR、压缩零分支、BEQ sentinel与SB位域，核a0/a1参数、byte mode、缓存分支及free原序。普通成功段没有用未认证厂商指令推合同；未解析注册链的厂商步进。JSON、报告本地链接、`git diff --check`通过。无固件执行、SIM、构建、历史回放、设备、外网或模型修改。本报告为研究交付，待独立技术复核。
