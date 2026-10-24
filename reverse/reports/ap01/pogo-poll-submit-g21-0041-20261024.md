# G21：认领 G19/3 的实际 op2 非 fallback ring 输入

2026-10-24；管理/研究基线 `cb4abfd`；独占树/分支 `re0041-g21` / `codex/re-0041-g21`。只挂认领 **G19/3**。**实际六参op2路径先把调用者16 B记录交给逐槽复制，再构造64 B条目；条目保存的是第三参scratch中的槽地址，未直接保存调用者的栈记录指针。tail增量发生在复制/条目写入之前。末尾按head/tail掩码比较决定是否调用已定位的下层服务，没有统一成功返回检查。** 该服务正文未展开时只保存锚点，未把软件填槽/调用解释成OS已接受。

已先全文读取**主仓最新** [reverse-design](reverse-design.md) 及 [管理记录唯一认领表](rolling-management-0041-20261023.md)，旧worktree表不授权认领。原G19作者已提交 `bedf291` 并停止；G19/1–2由非作者G20复核，本报告不重开。当前原件为CATALOG所列AP01 `1.0.2_0041`，`roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射 `file_offset=VA−0x9ffff000`；本轮核长度但不重算摘要，不套0031/SIM候选。

采用已读 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。仅主仓原件/旧证据只读与独占产物写入，无共享REA target/database、生产/ROM/配置/模型变更，不运行固件、SIM、QEMU、模型、构建、历史回放、输入实验、设备或外部服务，不做漏洞/异常输入/缺陷验证，无下级agent、不改共享认领表、不推送。下列字段名/伪代码为分析视图，不是原源码。

## 继承结论与认领差集

|相交认领/旧出处|已经解释的连接|G21差集与界限|
|---|---|---|
|G19/2，[G19](pogo-poll-cancel-backend-g19-0041-20261024.md)，G20限定接受|`0xa009e320→0xa009e0e6(word(L+0x20),B+0x84,word(R),2,fd,&stack16)`，R非零记录扫描完成后stack16清零；调用端未检查返回|只取其实际输入前提，不重读软件取消、R扫描、ready、同fd或调用端窗口。主仓管理更新已记G20整合91ce915，G21不替其作技术验收|
|G11/1，[G11](display-ready-producer-g11-0041-20261024.md)/[G12](display-producer-review-g12-0041-20261024.md)|六参ABI `(backend_fd,submit_ctx,scratch,op,fd,record)`；`submit_ctx+0x3c==−1` fallback到四参 `0xa010e722`，正常返回门及原有失败分支已验|本轮只核非−1分支，实际op=2；不重验fallback、首次ADD、完整MOD、producer或OS backend。G12 revents首读/清链顺序纠正沿原报告保留|
|[G03](invalidation-submit-g03-0041-20261023.md)/[G04](invalidation-submit-review-g04-0041-20261023.md)|`0xa000589c(dst,src,n)` 的16/20 B**对齐路径**复制值而不持有源地址；`0xa0024906` 的64 B对齐零填充已有原字验收|直接引用限定正常copy/zero合同，不重导1080 B复制算法。源栈对齐已知，scratch/entry有效性、对齐及容量须由ring初始化保证，本轮未新追初始化|
|J05、G11/G12的父级complete/最终SIM/旧ZIP与较晚留存盘点|`0xa009e0e6`旧300 B extent/directcall已有；旧initializer有引用，不等于nonfallback body已恢复；SIM替代不认证ROM ABI|继承有界复用结论，不重新导出整个函数、initializer、源码、资源或机械哈希清单|

独占范围仅本报告与 `reverse/analysis/pogo-poll-submit-g21-0041-20261024/`。原件与ignored证据根为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。旧索引extent Evidence `ev_5ecc1c04fd168340d2026dfe5ab76a4c73eb4b3fecea6f6f091e514dab87aa7f`、directcall Evidence `ev_054cff139263352630c77f72f9497086efffddf7ec56802fc1fa4b985e332e9d`只作选址，不冒充新REA执行或完整body语义。

## 本轮复核或纠正

旧语义纠正0。必要入口锚点 `0xa009e104..0xa009e110` 仅核本差集的寄存器生存期和分流：fd→s4、record→s2、backend_fd→s5、op→s6；`0xa009e106`读取submit_ctx+0x3c，`0xa009e110` BNE −1到 `0xa009e168`。旧fallback正文不重新取证。

本实际输入为 `submit_ctx=B+0x84`、`scratch=word(R)`、op=2、record=&调用者stack16。scratch是第三个实参，不是record别名推定；源和目的从不同实参形成。R正式类型和scratch分配/生命周期未被G19/2证明，本轮不得因其用途猜成某native库对象。

## 真正新增：ring 分支的字段、复制与发布原序

以下偏移均为十六进制，word为RV32的32位访问：

|原字位置|行为/字段|所有权或状态意义|
|---|---|---|
|`0xa009e168/0xa009e170`|取tail_ptr=word(submit_ctx+0x04)，读取old_tail=word(tail_ptr)|+0x04保存的是指针，不能把该字段本身当tail值|
|`0xa009e16a/0xa009e17a`|mask=word(submit_ctx+0x0c)，i=old_tail & mask|名称index mask来自实际AND；没有认证容量、初始化或mask=2^n−1不变量|
|`0xa009e172..0xa009e188`|保存original_scratch；copy_dst=scratch+(i<<4)；word(tail_ptr)=old_tail+1；给copy接口 `(copy_dst,record,16)`|**先tail写回，再复制。** 不补fence、锁或“写完条目才发布”。地址/增量运算均按RV32低word|
|`0xa009e18a`|JAL目标 `0xa000589c`|沿G04已验正常对齐16 B值复制；不会把源栈地址当复制值写进条目。scratch基址对齐/有效性未从第三参类型自动得到|
|`0xa009e18e..0xa009e1a2`|复制返回后才读entries=word(submit_ctx+0x28)；E=entries+(i<<6)；以 `(E,0,64)` 调 `0xa0024906`|复制记录槽stride16，提交条目stride64；不可把两个对象/步长合并。清64服务仍以有效对齐entry为条件|
|`0xa009e1a6..0xa009e1d2`|按下表写E字段，含1次byte store与多次word store|条目指向scratch副本，不是caller's stack16。后续scratch/条目可复用时间仍是下层消费边界|
|`0xa009e1d6..0xa009e1e8`|重读ctx+0x00/+0x04两个指针，再分别读head/tail值；用最初保存的mask计算 `(head ^ tail) & mask`|值重读在条目填完之后，mask没有同步重读；不凭常见ring形状认证full/empty或原子协议|
|`0xa009e1ea..0xa009e1f0`|上述结果为0才调用 `0xa009dfcc(backend_fd,submit_ctx,original_scratch)`；非0直接到尾声|调用第三参是原scratch基址，不是copy_dst/record/E；下层新连接先报认领锚点，未获更新前不展开正文|

条目E的原写入顺序如下；字段名不认证正式SQE/OS ABI：

|顺序/地址|写入|
|---|---|
|`0xa009e1aa`|word(E+0x0c)=signed fd >>31，形成fd高word|
|`0xa009e1ae/0xa009e1b2`|word(E+0x10)=copy_dst；word(E+0x14)=0，形成零扩展的地址pair|
|`0xa009e1b6`|word(E+0x04)=backend_fd|
|`0xa009e1ba`|word(E+0x18)=op，本实际值2|
|`0xa009e1be`|word(E+0x08)=fd，与+0x0c组成sign-extended pair|
|`0xa009e1c6`|byte(E+0)=0x1d；不是word覆盖或正式opcode名认证|
|`0xa009e1ca/0xa009e1ce`|word(E+0x20)=(i<<2) OR op；本输入为(i<<2) OR2，不用加法代替通用OR|
|`0xa009e1d2`|word(E+0x24)=fd；与+0x08是两个实际保存点，不省略|

对本次输入及有效正常ring存储，G19/2已准备的全零stack16在copy调用中变为scratch+i*16的16 B值副本。条目仅保存该副本地址；callee本体没有把record参数指针存到submit_ctx/scratch条目。基于G04的对齐copy无源地址持有合同，原调用栈可在复制返回后失效，而副本及E需由后续提交/完成协议维持。若scratch/entry的有效性或对齐尚未认证，应保留该前提，不把局部copy合同升级为所有地址的算法认证。

局部伪代码（非原源码）可写为：

```c
// G19/3：只给submit_ctx+0x3c != -1 且 op==2 的本体。
tailp = word(ctx+4);
mask = word(ctx+0xc);
old_tail = word(tailp);
i = old_tail & mask;
copy_dst = scratch + (i << 4);
word(tailp) = old_tail + 1;            // 先于copy和条目清零
known_aligned_copy16(copy_dst, record);
E = word(ctx+0x28) + (i << 6);         // copy后才读entries
known_aligned_zero64(E);
write_entry_fields_in_table_order(E); // 表内byte/word与先后顺序保留
hp = word(ctx); tp = word(ctx+4);
head = word(hp); tail = word(tp);
if (((head ^ tail) & mask) == 0)
    opaque_a009dfcc(backend_fd, ctx, scratch);
restore_and_return();                 // 不形成统一成功码
```

调用后tail/条目没有本体回滚或状态码判断。`0xa009e1f4..0xa009e210`只恢复寄存器并返回，不比较/替换a0；无下层调用时a0可能是前序服务遗留，有调用时a0沿服务返回，因此不能统一命名为成功/失败。该事实不说明下层服务成功或失败，也没有异常输入/缺陷试验。

## 精确未闭、扩范围锚点及验证

认领G19/3当前本体差集已回答到“16 B副本→64 B条目→条件下层调用”的静态边界；没有重做G19/1–2、G11/1 fallback或ADD/ready/MOD。未认证：ctx/scratch/entries的初始化、容量/对齐/跨线程发布、条目与副本何时可复用、正式字段/opcode名称、实际OS提交/完成及返回成功。没有OS close、callback drain、timer停止或context释放结论。

按主仓扩范围规则已向管理者提交：原认领G19/3；新连接 `0xa009e1f0→0xa009dfcc(backend_fd,ctx,original_scratch)`；问题是该条件服务如何消费本环/副本、向下提交与返回；相交G11/1只为已验fallback，不重复。旧索引 `#/functions/2356/extent` 有范围 `0xa009dfcc..0xa009e0e5`、282 B，Evidence `ev_3389f9eb111676b5aa1d29ed405d754612ba2d22d0899a45d361148734f89779`；`#/functions/2356/direct_calls` Evidence `ev_6e8ac40e4549bbf220c9a7869277a91b8ca2984a1a2baa6431d765f3bab83edd`，无dossier/已验本体合同。管理窗口608da2b已将其登记为 **G19/4：未闭、仅锚点、未派**，没有扩大G19/3。这里只保存旧metadata及调用端锚点，没有读取该callee正文或沿其native service库追踪。日后须先登记负责人/范围并明确派发才可展开，任务名/报告不作扩范围授权。

[verify.py](../../analysis/pogo-poll-submit-g21-0041-20261024/verify.py) 只读原件进行 **28项稀疏检查及1条厂商byte-store字段实例PASS**，含3个JAL、入口BNE、末端C.BNEZ及10个word访存字段独立解算；结果见 [evidence.json](../../analysis/pogo-poll-submit-g21-0041-20261024/evidence.json)。`0xa009e1c6`原字 `0x01add78b` 的字段为 `(opcode,f3,top5,rd,base,index,shift)=(0x0b,5,0,15,27,26,0)`，按既有本地 `th.srb` 规则写byte到entries+i*64；规则来自只读profile，不是新增ISA/开源来源认证。未导出整300 B函数/源码/资源，未运行旧作者/复核脚本、目标或模型。JSON解析、相对链接及diff检查通过；作者自检仍待非作者独立复核。
