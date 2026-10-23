# G15：fb0 file 私有 F 创建、登记与 close 归还

2026-10-24；基线 `82be763`；分支 `codex/re-0041-g15`。**同一 ops `a01c1368` 的 open 首槽真实目标是 `a012fabc`，close +4 槽是 `a012f3e0`。正常 open 产生零化的16B F，初始化选择字段−1、接入 D+c 链并写 file+10；正常 close 摘链、归还 F。close 本体没有遍历 F 的 poll 双槽或清除 P+14，不能把 G13 teardown 的清槽合同擅自移到 close。** 未观察实际 open/close、fd/inode 身份或 ready；未开展缺陷/异常输入验证。作者局部静态验证通过，待独立技术复核。

## 继承结论：已有出处→行为→局限→精确缺口

|已有出处|继承行为|局限与本题缺口|
|---|---|---|
|[G13](display-device-poll-g13-0041-20261024.md)、[G14](display-device-poll-review-g14-0041-20261024.md)|正常 fb0 注册把 ops=`a01c1368`、D 写入 inode+10/+18；poll +20=`a0132116`；F=file+10，F+8/+c 两个槽借用 P，P+14 回指槽地址；teardown 先清槽再清回指，不 free|本题只补同表实际 open/close 的 F 创建/归还，不重新导出 poll、revents 或通知|
|[F05](miio-exit-callback-f05-0041-20261023.md)/[F07](display-source-auth-f07-0041-20261023.md)、[G07](display-alternate-work-g07-0041-20261023.md)|`/dev/fb0`、flags3、backend 首 word 保存 fd、同 getter 到 watcher fd；正常显示退出 fd 非负调用 close wrapper，之后写−1|全部继承；不能凭这些推实际注册/open 成功或此刻 fd 仍指同 inode|
|[D03](uart-write-object-d03-0041-20261023.md)|File 的 inode+c/private+10、正常 file 安装、引用归还至最终 close 的已核合同|只补 ops 首槽与+4的实际间接 ABI；不展开通用路径解析、引用/文件表全生命周期|
|whole-rom-coverage-0041-20261023-round1.json|已有 a012fabc/a012f3e0/a0030eb8 extent 和 direct-call 定位|该索引三项无 dossier/historical_contract；旧定位不冒称新发现。较晚 round3 initial 只按两个实际目标精确检索，均未命中，不外推整个历史未恢复|
|[G03](invalidation-submit-g03-0041-20261023.md)/G04、[C03](pogo-close-callback-c03-0041-20261023.md)/C04|`a0024906(dst,value,len)` 填充接口；`a002e14e(ptr)` 既有归还接口|只核新包装器给零/长度16的调用，不重做 heap、整套填充算法或准确库来源认证|

旧 source-xref `a0055a14` 不是本表首槽，本轮没有将其命名为 open。复用 G13/G14 对旧 complete/ZIP/较晚阶段的筛选，不重复提取资源或机械账。

## 本轮复核或纠正

无 G13/G14 语义纠正。原字节读取 `word(a01c1368)=a012fabc`、`word(a01c136c)=a012f3e0`，与 poll 槽确属同表。正常设备 open 分派在 `a003ead8..eae4` 取 inode+10→ops 首 word，非空则以 file=s4 为 a0 调用，返回汇入原非负/负值判断。最终 close 的必要片段 `a0027d16..7d28` 取 inode=s5 的 ops+4，非空则传 file=s1 于 a0，保存返回并按 signed 非负判断。此前 D03 的引用/安装合同继承；这些局部指令不证明实际执行分派。

复用 extent Evidence：open `ev_5549cae82c755bfacd52dc83ec8484d45fd1966369b4236cddf09ac8eb4352bb`，close `ev_d02620377ad98867eab274a7d41801542f36a540969eaa8ec3e4a1a56100e1b5`，零化申请 wrapper `ev_7aeacb5fac6c61ac42c93ad78df4b7a5455cf96e1e8b4be61e4340701a88474f`。本轮必要原字节与旧边界一致；没有新开/共享/切换 REA target 或虚构新 Evidence ID。

## 真正新增：F 正常创建与发布

以下是偏移视图和分析伪代码，不是原源码或完整设备结构：

```c
// D = word(word(file+0xc)+0x18); F 总长16B
struct F_view {
    F_view *next;           // +0，D+c 的链
    int32_t selection;     // +4，初值 -1；后续何处改变不在本轮
    void *poll_slot[2];    // +8/+c，借用P；G13/G14合同
};
```

`a012face/fad0` 取 D，`fad4/fad8` 正常门要求 D 首 word 非空。违反前置条件转既有诊断 helper `a0019672`，本报告不改造成安全早退、不追诊断后的异常状态。`faf0` 保存原 file 为 s5，`faf2/faf4` 以16调用 `a0030eb8`，结果保存 s1=F；NULL 返回−12，未发布 F。

`a0030eb8` 的正常非空返回路径 `0ec6..0ede` 保存大小、以 `(word[62fc6aec],size)` 调 `a002ed8e`，非空时以 `(returned,0,saved_size)` 调已有填充 helper `a0024906`，最后恢复并返回保存的指针。故本调用的16B F 初始零化，两个 poll 槽均为0；不是仅凭 allocator 名称或候选源码断言 calloc。NULL 路径沿原 errno=12 返回，不展开底层 heap。

正常 open 顺序是：

```c
F = zero_alloc_a0030eb8(16);
if (!F) return -12;
saved_mstatus = clear_mstatus_bit8();
if (word(D+0xc)==0) {
    lower = word(D+0);
    cb = word(lower+8);
    if (cb) {
        r = cb(lower);              // 原a0来自fb0a；不是file/F
        if ((int32_t)r < 0) {
            restore_mstatus(saved_mstatus);
            a002e14e(F);
            return r;
        }
    }
}
word(F+4) = 0xffffffff;
word(F+0) = word(D+0xc);             // fb40重读，保留原序
word(D+0xc) = F;
word(file+0x10) = F;
restore_mstatus(saved_mstatus);
return 0;
```

`fb04/fb08` 只在当前 D+c 为0时考虑 lower+8；cb 为NULL直接发布。`fb3c..fb4a` 的写入均为32位，F+4=−1不是0；F+8/+c 保持零化结果。lower callback 的实际目标/内部副作用未在本题认证。初始化的 F+4 会由 G13 的 `a01320e0(D,word(F+4))` 消费；本题未恢复后续选择写者，不外推 plane 选择政策。

## 真正新增：close 摘链、归还与 poll 槽边界

`a012f3ee..f3fa` 读取同 D 与 F=file+10，正常前置要求 D 首 word和 F非空；`f41a` 要求链头非空。正常路径先保存/清 mstatus bit8。`f426` 读取**当前链头的 next**；仅该值为0时才取 `lower=word(D)` 的+0xc callback，存在则 `cb(lower)`，按 signed 非负继续，负值先恢复 mstatus 并直接返回该负值，未摘链/归还。本题不把这个判断换成引用计数，也不假设 F 一定是链头。

```c
// 正常有效链且F在链中；诊断路径仍是原程序合同，不伪造返回。
saved_mstatus = clear_mstatus_bit8();
if (word(word(D+0xc)+0)==0) {
    lower = word(D);
    cb = word(lower+0xc);
    if (cb && (int32_t)(r=cb(lower)) < 0) {
        restore_mstatus(saved_mstatus);
        return r;
    }
}
cur = word(D+0xc); prev = 0;         // f448重读链头
while (cur != F) { prev=cur; cur=word(cur+0); }
next = word(F+0);
if (prev==0) word(D+0xc)=next;
else word(prev+0)=next;
restore_mstatus(saved_mstatus);
a002e14e(F);
return 0;
```

`f44c` 的 NULL/未找到分支转原诊断，不是此伪代码声称 NULL可继续解引用。正常链头写在 `f458`，内部节点写在 `f462`；两条均汇入 `f464` 恢复 mstatus，再 `f468/f46a` 以原 F 调归还接口，`f472` 返回0。**close 本体正常路径没有读取 F+8/+c，没有调用 a003e2a0 或设备 poll teardown，也没有清 file+10、P+14。** 这是本体内的有界事实；lower callback及外层最终 close 其他工作不在该否定范围，不能推出全系统遗漏清理、异常行为或缺陷。

所有权：正常申请得到 F，由 D 的链与 file+10 持有同一地址；lower 指针为借用。poll setup 借用 P 写 F 的两槽，P又借用 F内部槽地址。已证解除双向槽借用的动作仍是 G13/G14 `setup=0`：清 `*P.private` 后清 `P.private`，它不释放 F/P。close成功摘链并把F交归还接口；不释放 P。**“已登记 P 在 close 前由谁确保 teardown”仍是精确未知边**，不能从本体没有槽清理就编造顺序保证，也不运行已登记close的验证。

## 未闭精确边与验证

- **事实**：表值、open/close 间接 file ABI、16B申请/零化调用、F字段写序、D链发布/摘除、lower callback门与参数、signed错误返回、mstatus恢复及F归还调用。来源仅支持既有 `video/fb.c` 路径/NuttX framebuffer 家族；准确版本、是否未改及完整库认证0。
- **推断**：所选显示 fd 的私有对象可沿这条正常 fb0 注册/open 路径取得 F，条件是注册成功、open命中同inode及身份未换；没有运行事实证明。
- **未知/断边**：实际运行fd/inode、open/close成功、F+4后续选择写者、lower callbacks的实际目标与内部工作、已登记P到最终close前的teardown调用顺序；异步ready/硬件通知继续继承G13/G14未知。未搜索完整VFS/所有设备/IRQ，未修改生产行为。
- [verify.py](../../analysis/fb-file-lifecycle-g15-0041-20261024/verify.py) 实际通过50项局部原字节/表值/调用检查；[evidence.json](../../analysis/fb-file-lifecycle-g15-0041-20261024/evidence.json) 留存268B必要窗口、旧extent/direct-call索引和较晚round3精确复用结果。VA映射 `VA−0x9ffff000`，只读主仓ROM；无新厂商指令语义。源码/固件/SIM/构建/历史回放/设备/网络均未执行或改动，未认证heap实际复用。

本题完成正常F创建/初始化/链持有与close本体归还合同，实际前置teardown顺序明确停边。一个必要后继是独立复核本报告 open/close表身份、F零化与错误/清理顺序，尤其“close本体不清poll槽”与“系统是否先teardown未知”的范围区分。提交前差异及 `git diff --check` 通过；本报告不冒称独立验收。
