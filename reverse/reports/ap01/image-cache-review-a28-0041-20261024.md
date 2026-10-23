# A28：A27 cache release / victim cleanup 独立复核

2026-10-24；基线 `6eec181`，独立分支 `codex/re-0041-a28`。**限定接受 A27 本题新增合同，未发现需要纠正的语义；新增功能恢复为0。** 本轮读原 ROM 的必要稀疏锚点属于旧结论独立复核，不另记一份 cache/PNG 恢复。使用 reverse-engineer-anything 的留存证据优先流程；未打开或改变共享 REA target。

## 继承的旧结论与实际复核缺口

|已有出处|已经解释的行为|证据局限|本轮处理|
|---|---|---|---|
|[A23](png-session-lifecycle-a23-0041-20261023.md)、[A24](png-session-review-a24-0041-20261023.md)|session close 到 release、cleanup callback 身份及其 Pixel/source 析构合同|并非每次 release 都立即 free|直接继承；只核接入的 payload 基址适配尾端，不重导内部析构/PNG|
|[A25](pixel-memory-contract-a25-0041-20261023.md)、[A26](pixel-memory-review-a26-0041-20261023.md)|默认 raw/free/align 表与 Pixel/raw 析构|不证明 cache 何时调用它们|原样继承，不重读这些完整实现|
|[A27](image-cache-cleanup-a27-0041-20261023.md)及其 analysis/evidence.json|正常引用/失效门、cache+18 连接、容量驱逐和分配基址 free|尚待独立核宽度、ABI、对象别名、返回和原顺序|本轮唯一技术复核对象；下表逐项给接受范围|
|A27 analysis/reuse.json 中的旧 complete、matrix/map、pass3 与35个 ZIP 文本成员有界查询；whole-ROM 的 `ev_db4d09f13700851ceab5594f52b0512798e338b1d87b9f6d68468adcd8bcf685` / `ev_437047f402084c5e91a9dcb9916360ccd1bfe62dc2d0ad9ed0e4ea9b5f9a43c5`|前者保留 SIM/旧材料复用边界，后者已有入口/extent/callee定位|SIM 不证明 ROM 后端；地址清单不是完整行为合同；token无命中不等于此前未分析|继承查询，不重扫ZIP或重新记账入口；不认证候选LVGL来源|

A27 已有原字节合同是第1类证据；whole-ROM 地址/source candidate 是第2类；旧 SIM 验收和替代配置是第3类；本轮实际缺口仅是 A27 新接入合同的独立技术认证。旧 round2/round4 的 remaining 或 complete 单份 pending 不用于重新开题。

## 本轮复核或纠正

|结论|处置|独立核对的原指令范围/边界|
|---|---|---|
|release 的 cache/entry 身份、计数减一和重读|接受|`a019da4c/4e/50` 保存 cache=s2、entry=s1；`da52` 调 `a008b604`，`da5a` LW entry+4；非零分支到 `dabe/dac0` 的 ADDI -1 / SW word，`dac2` BGEZ 到 `da84`。`da86` 第二次调用 getter，而非复用旧值。getter 非NULL分支 `a008b604→a008b650` 是 LW a0,+4。仅正常合法引用范围，不扩异常输入/诊断。|
|引用归零后读取失效门|接受|`da8e` 非零即返回；`da90` 是 LBU +c，`da94` 整字节零判断，没有 bit0 掩码。因而普通未标记归零不立即析构。|
|cleanup 间接 ABI 与基址 free 顺序|接受|`da96/98` 从 entry 取得 payload；`daa0/04/06` 为 LW cache+18、a1=0、JALR；`daa8/aa` 随后将原 entry 传 `a008b6a6`。后者非NULL分支 `b6b0→b6f2` 保留 a0，直接调用 `a008b654`，再 `b6f6→a008ab8a`。适配尾 `b6a0/a2` 为 `a0 -= LW(a0+8)`，释放的是共用分配基址，不能改成 free(entry)。|
|cache+18 callback 槽解释|接受（继承安装身份）|`a01985ce` 保存 backend；`85d6/d8/da/dc` 从原 callbacks 复制12B至 cache+10，因此第三 word 是+18。A23–A26 已核的 `a008abb0` 身份/内部语义不再导出。backend 表只核本题 +10/+14/+20/+24 四槽。|
|失效字节与两种清理接入的配对|接受|`a019d02a` 引用非零到 `d05e/d060` 的 LI1/SB+c，再 backend+14；引用零分支依次 backend+14→payload→cache+18(payload,0)→destroy_entry。只认证局部合同，不推出任何上层业务触发。|
|容量驱逐进入同 cleanup 的顺序与返回|接受|`a019d9c8` 真指向 `a019d898`；返回0终止，非零重问 backend+24，结果2回到驱逐。`d8a4..ae` 请求 backend+20(cache,0)，非NULL才进入 `d8e4`；随后 backend+14(cache,victim,0)→payload→cache+18(payload,0)→destroy_entry→返回1。无victim路径末端 `d8d6` 返回0。原 entry 保存在 s1，不将 backend 返回值当 entry。|
|victim 引用门与厂商 indexed load|接受|`a00ec236` 取 cache+38；节点payload转entry后加 cache+4；`ec266` 真调 getter，引用为0转返回保存entry，非零沿关系继续。`ec270` 原字 `0b49f940` 的 `[opcode,f3,top5,rd,rs1,rs2,shift]` 独立解出 `[11,4,8,18,18,15,0]`。继承只读模型 th.lrw 语义为 `rd=*(rs1+(rs2<<shift))`；rd 与 base 都是 s2，故 s2 被加载值替换，但没有额外基址自增写回。|
|backend 归还计量在 cleanup 前|接受（限定到局部尾端）|`a00ebf60/62/64` 用 payload 调 cache+3c；`bf66/68/6a` 从 cache+c 减返回值并写回。调用者在 backend+14 返回后才调 payload cleanup。索引删除 helper 的内部算法直接引用A27，并未独立展开。|
|容量全部算术分支、完整排序、来源认证|未另核|不属于本题接入复核；继承A27所列范围，不以本报告扩大接受到整个cache、heap或LVGL来源。|

本轮没有语义纠正。上述 `th.lrw` 的 rd/base 同名说明是对原序表达的精度说明，并非新增厂商指令发现，也不更改分析器。所有间接 callback 返回值均未被伪造为析构成功证明；当前合同只说明正常静态控制流及原参数。

## 本轮真正新增

无新增业务功能、资源恢复或来源排除。新增交付仅为 A27 的独立复核结论和可复用稀疏原字节检查。没有重新导出整函数、PNG、默认 handler 表、全 cache 分类或源码归档，也没有重新生成旧复用查询。

## 仍未闭合的精确边

- `a019cfbe` 的正常上层业务调用者/失效触发仍未认证；不得将某次页面退出直接套入本清理合同。
- cache+38/+30 的完整排序及 victim 优先级、树/链 helper 内部算法仍在既有范围之外。
- cache+3c 完整计量回调/单位、动态 callback 与容量替换、底层 heap/同步仍未知；本报告未重复展开这些内容。
- 不证明具体图片的运行时缓存命中、何次 session close 发生销毁或任何解码/设备执行成功；SIM passed 不外推 ROM 完成。

当前 A28 复核范围已得到限定答案，无必要继续扩扫。后继若管理者另行派发，应从上述精确断边中先检索旧成果再选题，不能将 A27/A28 重记为两次恢复。

## 实际静态验证

独占 [verify.py](../../analysis/image-cache-review-a28-0041-20261024/verify.py) 对主仓 ROM 只读，以 `offset=VA-0x9ffff000` 映射，独立解码标准指令与 AUIPC/JALR/JAL 目标，并单独核厂商字位域。113项检查通过，保留98个稀疏锚点，见 [review-evidence.json](../../analysis/image-cache-review-a28-0041-20261024/review-evidence.json)。这是旧结论复核，不计新增功能；没有共享可写REA目标、模型修改、SIM、构建、历史回放、固件/设备/网络执行。报告链接、JSON格式与git diff --check另作交付检查。
