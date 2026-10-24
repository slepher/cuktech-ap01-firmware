# A56：reader 按 source 首字节选择 D 的定点原字段证据

2026-10-24；认领 **J08/1**；研究基线 `32f9c9e`，分支 `codex/re-0041-a56-resume`。主仓唯一[认领表](rolling-management-0041-20261023.md#链条认领表)本轮三席恢复已登记 `/root/a56`，只准 `0xa019d708..0xa019d796` 选择窗口；工作树旧停止记录不作为授权。已阅读主仓 [reverse-design](reverse-design.md)，采用 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md) 的留存优先、原字节和事实边界规则。

**选择器从 `word(0x62fc9744)` 取首节点，以每节点 `word(N)` 作为候选 D，将 `U8(D)` 与 source 首字节相比较；不匹配时按 `word(N + word(0x62fc9740) + 4)` 继续。首个匹配进入已留存的 D+8 可选回调门及 D+0x0c 非空门，通过后才到已验的 `W+4=D` 保存。** 这是注册容器到候选 D 的选择规则，仍没有取得真实容器内容、注册写入者、具体 D 或任何槽目标；不是 POSIX driver 实例认证。

本轮只读原厂0041的144B新窗口和必要旧留存，不打开或切换共享REA，不执行目标指令、固件、模型、构建、SIM/QEMU、历史回放、设备或外部服务。不展开新callee/注册链，不修改生产、ROM、配置、分析器或共享表，不提交/推送，无下级agent。作者检查不是独立验收；交付状态为待非作者复核。

## 继承结论

|已有出处|已解释行为|局限与本题真正差集|
|---|---|---|
|[最终应用验收](application-rehost-complete-0041-20261017.md)、[J08盘点](reader-driver-reuse-gap-j08-0041-20261024.md)引用的较晚complete/最终ZIP|照片业务、主旋钮轮转及SIM替代已有覆盖|继承既有覆盖与SIM限制，不重盘点或执行；SIM不能证明ROM具体D|
|A33/A35、A37/A39、A41/A42，均由J08核过与本问题的界面|默认五ROM照片mode0；类型1候选构造W，成功后复制当时W到O；O外层归还已有|不把通用选择分支升级为实际五照片mode1，不重做照片、资源、构造或析构|
|[A47](photo-reader-mode-a47-0041-20261024.md)/[A49](photo-reader-mode-review-a49-0041-20261024.md)，必要继承认领A47/1|`0xa019d6ec`以LBU将source首字节放a2；s2=W、a5=source；非空source后缀为source+1或冒号时+2。`0xa019d798`保存s1=D到W+4；普通open经D+0x0c以 `(D,pathSuffix,2)` 调，close经D+0x10以 `(D,H)` 调；缓存条件及清槽已验|直接引用上述两端；A47没有选择窗口rows，不能由两端补猜中间D来源。本轮只补中间选择和门/调用端|
|[A50](photo-reader-consumer-a50-0041-20261024.md)/[A52](photo-reader-consumer-review-a52-0041-20261024.md)|D+0x14 read、D+0x1c seek与缓存持有/消费合同已验|不重复缓存算法/回调ABI；slot偏移不能认证具体driver|
|[A54](photo-reader-source-a54-0041-20261024.md)/[A55](photo-reader-source-review-a55-0041-20261024.md)|本地LVGL9.2.1候选的reader前缀、普通open/close及注册角色局部相符|保留候选版本/载体差异；候选源码不是原ROM全局容器或实际D绑定证据，本轮不新查源码或认证整库|
|J08/2的ROM `lv_fs_posix.c` 源路径xref/owner metadata|实际路径端 `0xa056b8e0` 与7个owner有定位证据|与本轮global/head/stride尚无身份桥，继续未知；不沿owner、注册或slot本体取证|

查重界面：J08已明确 `functions/5912` 只有extent500B与直接边，`historical_dossier=null`、`dossiers=[]`。旧extent Evidence `ev_859d0259f168d800653161ec3bc5f2e30ad376724ac8554d42ab611f85726f07`，直接边 `ev_1280933dca27de196ea349bb7f242f9b891487c60bddd21c237f3f9f345aaf4c`，仅作定位。F11中的栈D/请求R与G19中的poll W/ctx均未与本reader D/W建立对象身份，不因名称或偏移相同合并。

## 本轮复核或纠正

没有纠正A47/A49已接受的接口、模式或缓存合同。需要区分：本轮候选D的 **首字段比较是 unsigned byte**；节点的后继偏移由 `word(0x62fc9740)+4` 运行期读取，不能写成固定 `N+4`，也不能把它解释为D内部next字段。读到的是head/stride **槽地址**，没有读取它们的运行值。

厂商指令 `0xa019d750` 原字节 `0b47d740`（LE word `0x40d7470b`）经独立位域拆得 `(op,rd,f3,rs1,rs2,shift,top5)=(0x0b,14,4,14,13,0,8)`。Capstone不解码该字，原始显示保留为 `UNDECODED`；依据既有只读 `ap01thead2.sinc` 中 `:th.lrw` 局部规则，解释为 **`a4=load32(a4+(a3<<0))`**，无额外base写回。因此在此处a3已等于动态偏移，a4由当前N变为next。没有修改/执行模型，没有把此匹配作为新增ISA认证或独立上游规范。规则原文、路径和字段记录于本题JSON。

新窗口分支仅解算出目标地址；`0xa019d864..0xa019d86c` 与 `0xa019d798` 的目标指令全部从A47旧JSON复用，未新读取这些目标的ROM字节。共同出口 `0xa019d6dc` 不在本轮新窗口或所复用行中；本题只认 `s3=3/1` 与跳转事实，不补猜出口如何形成a0或完整返回ABI。

## 真正新增

证据类型为原厂字节静态字段/控制流，容器/driver名称为分析解释，不是运行观察或原源码类型。对象名N、D、W、pathSuffix沿接口关系定义。

|地址/原字节锚点|正常选择、条件和顺序|
|---|---|
|`0xa019d708 b796fc62`、`0xa019d70c 9386c657`|LUI/ADDI构成 `G=0x62fc957c`，不是ROM内某个D本身|
|`0xa019d710 03a7861c`、`0xa019d714 83a6461c`、`0xa019d718 9106`|按原序读取a4=`word(G+0x1c8)`即head槽 `0x62fc9744`，读取a3=`word(G+0x1c4)`即stride槽 `0x62fc9740`，然后a3+=4。head和stride来自两个不同word槽|
|`0xa019d71a 15e7`|a4非零跳 `0xa019d746`，为空则进入已有诊断服务调用端；两次不匹配之间也重回此门|
|`0xa019d746 0443`、`0xa019d748 03c50400`、`0xa019d74c 630cc510`|s1=`word(N)`取得候选D；a0=`U8(D)`；与继承的a2=source首字节相等时跳 `0xa019d864`。它选择链顺序中首个匹配项，不证明letter唯一|
|`0xa019d750 0b47d740`、`0xa019d754 d9b7`|仅未匹配臂，以既有th.lrw规则读取 `N=word(N+stride+4)`，跳回 `0xa019d71a`。不读D+offset，也不在本窗口增删/持有节点|
|继承 `0xa019d864 9844`、`0xa019d866 e31807ee`|匹配D后读 `word(D+8)`，非零跳回本轮 `0xa019d756` 调该槽；为零直接落到继承的D+0x0c槽门。因此这是可选回调，不是必须存在的open槽|
|`0xa019d756 2685`、`0xa019d758 232cf4fc`、`0xa019d75c 232eb4fc`、`0xa019d760 0297`|明确设置a0=D，将a5/source与a1/pathSuffix存到s0−0x28/−0x24，然后经a4间接调用。这里证明D作为a0，不由此臆定函数声明只有一个参数；槽地址仍未知|
|`0xa019d762 8325c4fd`、`0xa019d766 832784fd`、`0xa019d76a 63100510`|回调后先恢复a1后缀，再恢复a5/source；a0非零才跳 `0xa019d86a` 继续检查open槽。零则走本地诊断、s3=1及共同出口；首个匹配回调返回零后没有回到搜索next的边|
|继承 `0xa019d86a d844`、`0xa019d86c 15f7`|读取 `word(D+0x0c)` 并在非零时跳 `0xa019d798`，随后已有 `sw s1,4(s2)` 才保存D到W。槽为零的fallthrough不在本轮授权窗口，不补语义|
|`0xa019d73a..0xa019d73e`、`0xa019d78c..0xa019d790`|两条AUIPC/JALR独立算得目标同为 `0xa008b51a`，只记录诊断调用端，不展开callee；无候选时随后 `s3=3`，回调零时 `s3=1`，两者均跳 `0xa019d6dc`。这些状态寄存器值不冒充已认证最终返回码|

局部伪代码，**非原源码**；外部落点使用明确的继承/未闭边界：

```c
// a2=U8(source), a1=pathSuffix, a5=source, s2=W：继承A47。
N = load32(0x62fc9744);
next_off = load32(0x62fc9740) + 4;
while (N != 0) {
    D = load32(N);
    if (load_u8(D) == a2) goto matched;
    N = load32(N + next_off);       // 此语义依既有th.lrw规则
}
diagnostic_boundary_a008b51a(/* 原调用端实参 */);
s3 = 3;
goto common_exit_a019d6dc;         // 不认证最终a0/返回ABI

matched:
ready_slot = load32(D + 8);         // A47旧行
if (ready_slot != 0) {
    save_source_and_suffix();
    a0 = D;
    result = indirect_call(ready_slot);
    restore_suffix_then_source();
    if (result == 0) {
        diagnostic_boundary_a008b51a(/* 原调用端实参 */);
        s3 = 1;
        goto common_exit_a019d6dc;
    }
}
open_slot = load32(D + 0x0c);       // A47旧行；回调后重新读取
if (open_slot != 0) {
    store32(W + 4, D);             // A47旧行，之后按旧合同继续
    goto inherited_cache_and_open;
}
goto outside_selection_window;    // 不发明该fallthrough的返回/清理
```

本窗口不申请、复制、归还D或节点；候选D只装入s1，在通过既有门后保存到W。结合A47/A49，后续W/O借用D以调用槽，缓存及H另有既验责任；本题没有证明registry节点/D的所有者、引用计数、注销或完整寿命。D+8回调可能读写哪些对象、可否改变配置及实际ready含义均不由调用端认证；这里只保留返回零/非零的消费方式。

## 未闭精确边、实际验证及后继

本轮补齐的是 **source首字节→全局head/动态next→首个候选D→可选槽调用端→open非空门→已验W+4保存** 的局部规则；没有证明任何实时时刻确有节点、确有某个letter或正常I/O发生。仍未闭：`0x62fc9740/0x62fc9744`的初始化/写入者及节点布局来源、真实source类型1路径实例、具体D及D+8/+0x0c/+0x10/+0x14/+0x1c目标、J08/2 POSIX源路径端与该D的身份桥、同letter唯一性、完整返回ABI和driver注册/注销寿命。默认五照片仍mode0；无新增整库排除、完整ROM或运行成功结论。

唯一有种子后继：以原认领J08/1为父，登记 **`word(0x62fc9744)` head、`word(0x62fc9740)` stride 的初始化/注册写入者→节点word(N)=D** 身份桥，先查旧留存/写入metadata，再由管理窗口限定新窗口。相交A47/1为已验接口、J08/2为尚未绑定的POSIX模块端；差集是实际全局容器写入及D实例，不重做本轮选择或扩全部fsdrv。已向管理窗口报告锚点，未沿writer展开。

[verify.py](../../analysis/reader-driver-selection-a56-0041-20261024/verify.py) 实际运行：**41项检查PASS，42条指令，144B新原件窗口**。原件使用[CATALOG](../../../roms/CATALOG.md)已有0041身份：`roms/0041/ap01-1.0.2_0041.bin`，长度6,769,704B，既有SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；本轮仅校长度，未重算摘要。映射 `file_offset=VA−0x9ffff000`，新读取精确 `[0xa019d708,0xa019d798)`，没有整500B函数导出。

[evidence.json](../../analysis/reader-driver-selection-a56-0041-20261024/evidence.json) 保存每条新原字/文件偏移、Capstone版本和模式、独立LUI/ADDI/LW/LBU/SW/普通与压缩分支/AUIPC-JALR字段、唯一厂商字段和既有模型原文、必要继承A47行。没有新REA会话/profile/Evidence ID；旧索引EID保持原来源，本题JSON是静态原字段证据而非REA调用记录。脚本未运行作者/历史验证器或目标指令。JSON解析、相对引用、独占范围及 `git diff --check` 已检查；作者交付后停止，待非作者限定复核。
