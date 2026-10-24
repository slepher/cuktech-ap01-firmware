# A57：reader driver 选择窗口的非作者复核

**限定接受 A56 在 J08/1 的选择窗口差集；语义纠正0、新增业务功能0。** 原厂代码按 source 首byte搜索容器节点，节点word0是候选D，后继位于动态 `N+word(0x62fc9740)+4`。首个匹配才进入可选D+8回调门和D+0x0c非空门，随后沿已验边保存 `W+4=D`。这仍未认证真实注册内容、具体D/槽目标或POSIX driver实例。

2026-10-24；非作者复核者 `/root/f12`，任务A57挂原认领 **J08/1**，固定基线 `32f9c9e`，沿用独占 `re0041-f12` 工作树和 `codex/re-0041-f12-resume` 分支，没有新增agent。授权取自主仓[唯一管理记录](rolling-management-0041-20261023.md)当前J08/1的“待复核（A57本轮进行）”及管理者派发；作者 `/root/a56` 已交付停止。不以工作树旧认领表授权，不改主树/共享表，原F12文件保持不变。

遵循主仓 [reverse-design](reverse-design.md) 和 `reverse-engineer-anything` 技能。只读原件、旧A47证据及既有局部指令规则，不运行A56作者脚本，不切换共享REA，不执行固件/指令/模型/输入、构建、SIM/QEMU、历史回放、设备或外部服务，不改生产/ROM/配置/模型，不提交或推送，无下级agent。新writer/callee只保留锚点，没有展开。

## 继承结论

|已有出处|已解释行为及证据局限|本轮处理|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[J08盘点](reader-driver-reuse-gap-j08-0041-20261024.md)|照片业务/SIM已有覆盖；旧选择函数只有500B extent，不能推具体D|不重做业务/资源/SIM；extent不作body语义|
|[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)|source首字节进a2、s2=W、a5=source；后缀已算于a1；D+8可选门、D+0x0c门、W+4保存及后续open/close接口已验|直接读取主仓A47 JSON八条必要行，不新读窗口外ROM；这两端继承，不算A56首次发现|
|[A50](photo-reader-consumer-a50-0041-20261024.md)/[A52](photo-reader-consumer-review-a52-0041-20261024.md)、[A54](photo-reader-source-a54-0041-20261024.md)/[A55](photo-reader-source-review-a55-0041-20261024.md)|read/seek/cache及候选LVGL局部来源已有合同；候选注册角色不能绑定ROM具体实例|全部继承，不重做缓存、候选源码或开源归属|
|A56作者报告 `reader-driver-selection-a56-0041-20261024.md`|只补 `[0xa019d708,0xa019d798)` 的head/stride、候选比较、动态next及回调返回门；writer/具体D未闭|只复核这份差集，不读注册writer或新callee，不重开整个fsdrv|

作者交付在本轮独占 `re0041-a56/reverse/reports/ap01/reader-driver-selection-a56-0041-20261024.md` 与同名analysis目录，管理整合后保持相同仓库相对路径。既有extent Evidence `ev_859d0259f168d800653161ec3bc5f2e30ad376724ac8554d42ab611f85726f07`、直接边 `ev_1280933dca27de196ea349bb7f242f9b891487c60bddd21c237f3f9f345aaf4c`仅继承定位，不当作完整语义证据。

原件按 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查长度6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，没有重新生成哈希账。映射 `file_offset=VA−0x9ffff000`。不套0031/unsigned/SIM地址。

## 本轮复核或纠正

[独立检查器](../../analysis/reader-driver-selection-review-a57-0041-20261024/review.py) 仅新读原件 **144B** `[0xa019d708,0xa019d798)`，没有读取任何窗口外ROM目标。使用 **Capstone 5.0.7、RV32+RVC** 解码41条普通指令，1处厂商word保留 `UNDECODED`，共42个位置。**36项检查PASS**，包含独立LUI/I-format地址、B/CB/CJ目标、AUIPC/JALR两调用目标、厂商位域和八条A47继承行。原字、VA/文件偏移、检查结果、继承行与规则出处见 [evidence.json](../../analysis/reader-driver-selection-review-a57-0041-20261024/evidence.json)。没有运行、导入或重用A56作者检查器。

|复核锚点|原字/指令与推导|裁定|
|---|---|---|
|`0xa019d708..0xa019d718`|`b796fc62`/`9386c657`构成G=0x62fc957c。先LW head=`G+0x1c8=0x62fc9744`，再LW stride=`G+0x1c4=0x62fc9740`，a3加4|接受两个运行期槽地址；不是槽值，也不是D实例|
|`0xa019d71a`、`0xa019d746..0xa019d74c`|非零head到0xa019d746；`0443`取 `s1=word(N)`，`03c50400`取 `U8(D)`，B-format比较a0/a2相等到0xa019d864|接受按首byte比较的首匹配；不认证同letter唯一或source路径实际存在|
|`0xa019d750`、`0xa019d754`|原字 `0b47d740`，独立字段opcode=0x0b/rd=14/f3=4/base=14/index=13/shift=0/top5=8；CJ回0xa019d71a|既有 `th.lrw` 规则解释为a4=word(a4+a3)，即 `N=word(N+stride+4)`；不是固定N+4，也不是D.next|
|继承 `0xa019d864/0xa019d866`|A47的D+8 load与B-format非零分支目标独立解为0xa019d756|接受可选回调：空槽直接继续D+0x0c门；非空才调用|
|`0xa019d756..0xa019d76a`|先a0=D；源a5、后缀a1分别存s0−0x28/−0x24，再间接调用a4。返回后先恢复a1再a5；a0非零到0xa019d86a|接受真实调用端/保存恢复顺序；a0=D不证明只有一个形式参数。首匹配callback零后不搜索后续节点|
|继承 `0xa019d86a/0xa019d86c/0xa019d798`|D+0x0c读取，压缩非零分支独立解到0xa019d798，旧SW s1,4(s2)|接受通过门后W+4=D；open空槽的窗口外fallthrough不补语义|
|`0xa019d73a..0xa019d744`、`0xa019d78c..0xa019d796`|两组AUIPC/JALR独立算得0xa008b51a；其后s3分别3/1，两个CJ均到0xa019d6dc|接受调用端/状态寄存器值及出口地址，不将s3冒充最终a0返回码|

厂商语义仅继承主仓 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的 `:th.lrw` 局部规则；直接读该构造器必要片段并核 `delta=rs2<<shift`、`updated=rs1+delta`、4B load、`rd=value`。没有执行或修复模型，没有把本地规则相符升级为独立厂商ISA/来源认证。普通分支和关键宽度按原字段/Capstone双查，未NOP化未知编码。

复核未发现A56语义错误。局部伪代码（分析表达，非原源码）仍是：

```c
N = word(0x62fc9744);
next_off = word(0x62fc9740) + 4;
while (N != 0) {
    D = word(N);
    if (u8(D) == source_first_byte) goto first_match;
    N = word(N + next_off);  // 依既有th.lrw规则
}
diagnostic_boundary(); s3 = 3; goto exit_a019d6dc;
first_match:
if (word(D + 8) != 0) {
    save_source_and_suffix();
    a0 = D; result = indirect_call(word(D + 8));
    restore_suffix_then_source();
    if (result == 0) {
        diagnostic_boundary(); s3 = 1; goto exit_a019d6dc;
    }
}
if (word(D + 0x0c) != 0) {
    word(W + 4) = D;  // 继承A47；其后open/cache直接引用已验合同
}
// 空open槽fallthrough和共同出口最终返回均保留未知。
```

本窗口没有申请/复制/归还节点或D。D保存在寄存器后沿已验边交W借用，不能由此推registry所有者、引用计数、注销或完整生命周期。

## 真正新增

新增业务功能0、ROM功能恢复0、库排除0、ISA规则0；语义纠正0。本轮只为A56已交付差集提供非作者独立检查与限定接受意见。同字节重读不计新功能，旧A47两端不重记新增。

与F11/1–2的栈descriptor D、MiIO R/P/S/I以及G19/4的提交环对象无身份/地址/问题重叠；只因变量名D或相似偏移不合并对象。与J08/1的重叠正是已登记复核，J08/2仍未绑定。

## 未闭精确边

仍未知真实 `0x62fc9740/0x62fc9744` 的运行值与初始化/注册writer；N/D实例和D+8/+0x0c/+0x10/+0x14/+0x1c目标；source类型1的实际路径；POSIX源路径端到本容器的身份桥；注册/注销/所有权寿命；同letter唯一性；共同出口最终返回ABI；回调内部行为与实际I/O成功。默认五ROM照片mode0的旧结论不改变。

唯一有种子的后继沿作者建议：由管理者先对 **head槽0x62fc9744/stride槽0x62fc9740的writer→节点word0=D** 查重登记，再限定旧证据或新窗口；本轮没有读writer或新callee。独立接受的边界止于选择/门/调用端和继承W+4保存，不代表具体driver绑定闭包。

实际检查为36项定点静态检查、JSON可解析、相对引用存在、`git diff --check`与独占文件检查。交付时只有A57报告及同名analysis的 `review.py/evidence.json` 新增，F12原成果未改；全部未提交，复核者交付后停止。
