# A31：A29 旧源到 image-cache 失效接入独立复核

2026-10-24；独立基线 `9ea568ff30ee46271cb3dab26dff24cd9f5f8d35`，分支 `codex/re-0041-a31`。**限定接受 A29 新增的正常旧源接入连接；没有发现需纠正的语义，新增功能恢复为 0。** 原 ROM 必要锚点的重读是旧结论独立复核，不再记作功能恢复。使用 reverse-engineer-anything 技能；未打开共享可写 REA target/数据库。

## 继承结论：已有出处到实际复核缺口

|已有出处|已经解释的行为|证据局限|A31 实际缺口|
|---|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)、A24|image-cache 全局槽 `G+11c=62fc9698`；session 查询 key 的 source word+4、class byte+8；class helper `a00dd454`|不是上层失效触发证明|直接继承这些身份与布局，核 A29 第二次调用是否真正使用它们|
|[A27](image-cache-cleanup-a27-0041-20261023.md)、[A28](image-cache-review-a28-0041-20261024.md)|`a019cfbe(cache,key)` 命中后，零引用立即移出/清理；有引用标 byte+c、移出，最后 release 才清理|失效 API 被调用不等于命中，release 不等于立即 free|内部可靠合同直接继承，不重导失效/release/cleanup|
|[A29](image-cache-invalidation-a29-0041-20261024.md)及其 `analysis/evidence.json`、`verify.py`|+5c 门、getter 的 +2c 旧源、双 cache/key 与两次失效调用|尚需独立核控制流、宽度、实参和同 cache 身份|本轮唯一接受对象，见下表|
|A29 引用 whole-ROM `ev_1980883cc9366d20118371e1856a8a9a575f620da7729d9e874e6a8c2312e1ba` / `ev_aa9eff0143bddc43c0c1b0b05731f7a92d3bdbb24e2bf4b70b362f5bbc331697`|早已有 `a00ed7f4→a00890e8→a019cfbe` 地址关系|地址清单不是字段/实参合同|继承种子，不重扫 incoming、整函数或全 ROM|
|A29 引用照片 round3 `ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`、system complete、旧 SIM/最终验收/ZIP 与 `reuse.json`|照片旋钮轮转、旧 `a00ed7f4(*puVar17,uVar7)` 和 SIM 复用范围已有|新 source 仍由不可信 `custom0.rd()` 表示；SIM/照片重建不认证 ROM ABI|全部继承，未将该业务或旧地址关系称为首次发现，不重新查询 ZIP/资源|

证据类型保持分开：A23/A27/A28 及本题字节锚点是原字节行为；照片 `custom0.rd()` 是待局部核的旧反编译；SIM/照片重建是替代实现与验收；本题未闭边见末节。旧 pending 或词项无命中不证明此前未恢复。

## 本轮复核或纠正：逐项处置

|A29 结论|处置|独立原字节核对与接受边界|
|---|---|---|
|`a00ed7f4` 仅在对象 word+5c 非零时进入本连接|接受|`a00ed802` 是 LW s2,+5c(a0)，`d806/d808` 保存对象与新 a1；`d80a` BEQ s2,zero 精确到 `a00ed830`，跳过 `d80e/d812`。门读取 word，不是 byte/bit。未扩大为每次切页都满足该门。|
|getter 返回该对象 word+2c，紧接着作为失效 source|接受|`d80e` JAL 目标 `a00eaa50`；getter 入口 `a00eaa50` C.BNEZ a0 直接到 `a00eaa9c`，该尾端是 C.LW a0,+2c(a0)、RET。`d812` 紧接 JAL `a00890e8`，没有改写 a0。因此正常有效对象路径传旧 source，非保存的新 a1、非+5c 指针。这里只认证正常路径，不展开 getter NULL 诊断。|
|`a00890e8` 的非 NULL 参数进入指定 key 失效|接受|`a0089102` C.BNEZ a0 到 `a0089128`，后者 C.MV s2,a0。source 为 NULL 走另一分支，不套用此 key 合同。s2 保持原 source 供第二次 classifier/key 使用；未推断 API 返回值含义。|
|第一次调用属于另一 cache G+120|接受|`a00890f6/fa` 解出 G=`62fc957c`；`90fe` LW s3,+120(s1)。栈 key 基址 s0-38，`913e` SW source 到+0，`9146` SB classifier 返回低 byte 到+4，`914a/914e` 传 a1=key、a0=s3。`9150` AUIPC/JALR 精确落 `a019cfbe`。不得套 A23 image payload/比较器合同。|
|第二次调用是 A23 同一 image-cache 与相容 key|接受|`9158/915a/915c` 传 a2=24、a1=0、a0=s0-38；`9160` JAL 到既有清零 helper `a0024906`。`9164/9166` 恢复 source 到 a0 并 SW s2 到 key+4；`916a` JAL `a00dd454`，`916e` SB a0 到 key+8。`9172` LW a0,+11c(s1)，即 `62fc9698`；`9176` a1 同 key 基址；`917a` AUIPC/JALR 同样落 `a019cfbe`。与 A23 字段身份一致，不宣称全部 key 比较器内部已复核。|
|第一次 key 的其余部分清零、第二次 key 重清零|接受|`a008912a/2e/32/36/3a` 是五次 SW zero 到 key+4/+8/+c/+10/+14；source 写+0、class 随后覆盖 byte+4。第二次调用前重新清 24B；不将两个布局混用。清零 helper 语义直接继承既有合同，不重导其内部。|
|命中后的有引用失效与最后 release 清理|继承，不另核|A27/A28 已核；本题只补接入。调用本身不证明找到 entry、byte+c 被设置或发生实际析构。|
|照片新 source `custom0.rd()`、GIF 路径字符串及准确来源版本、其他 caller|未另核|不依赖它们接受旧源链；候选文件路径不作为整库来源认证。照片 source ABI、其余 caller 生命周期不在本次接受范围。|

没有语义纠正。必要数据流可简写为以下伪代码，它仅表达本次接受的分支，不是原源码或完整 API：

```c
if (load32(obj + 0x5c) != 0) {
    old_source = a00eaa50(obj);  // 正常有效对象分支：load32(obj+0x2c)
    a00890e8(old_source);
}
// a00890e8 的 source != NULL 分支：
// G+120, key0(source@0,class@4) → a019cfbe；
// 清零24B，G+11c, key(source@4,class@8) → a019cfbe。
```

source 是失效查找输入；本段没有新取得其所有权，也没有把 obj、新 a1、栈 key 或第一 cache 的 payload 当 image-cache 所有物。栈 key 只用于同步调用；entry/Pixel/source 副本的生命周期继续按 A23/A27/A28 已有合同解释。正常 API 未在这里恢复成有成功/失败意义的返回值。

## 真正新增

新增功能、资源恢复、业务恢复和来源排除均为 **0**。交付仅新增 A29 的独立接受结论与 [34 项稀疏检查](../../analysis/image-cache-invalidation-review-a31-0041-20261024/review-evidence.json)。没有重复导出完整 getter/失效函数、旧照片 callback、PNG/GIF 解码、cleanup 或旧复用账。

## 未闭的精确边与验证

- 照片旋钮 callback 的新 source `custom0.rd()` 实参来源/厂商 ABI 仍未知；没有证明每次照片切换/页面退出调用此 API 或满足 +5c 门。
- source==NULL 的清空 API 分支不在本次接受范围；G+120 的 payload、比较器和 key 副本身份仍未认证。
- G+11c 具体运行时命中、引用数、立即或延后清理没有执行观察；静态接入不等于失效一定发生。A27/A28 其他排序/计量/heap 未知不由本题补齐。

如需后续闭包，只能另立任务认证照片 callback 的新 source 实参窗口及真实业务触发；先复用完整旧照片证据，不据本报告重复恢复 cache 内部。

[verify.py](../../analysis/image-cache-invalidation-review-a31-0041-20261024/verify.py) 使用 Python 标准库，只读主仓原 ROM，以 `offset=VA-0x9ffff000` 独立解码标准 LW/SW/SB/ADDI、压缩分支/加载、BEQ、JAL、AUIPC/JALR 目标，34 项检查全部通过。没有厂商指令参与这条必要接入链；没有修改分析器模型。检查结果是旧结论复核，不是运行观察。未执行固件、SIM、构建、历史回放、设备/外网，未改生产代码/ROM/config/共享索引；仅独占 report/analysis 交付。JSON 格式、报告本地链接与 `git diff --check` 另行通过。
