# A29：旧源更新到同一 image-cache 失效接入

2026-10-24；独立基线 `ecfe6dd`，分支 `codex/re-0041-a29`。本轮只补接入连接，不重做 A27 失效、release 或 cleanup 内部。**正常 `a00ed7f4` 调用在对象 word+5c 非零时，读取对象 word+2c 作为旧源，调用 `a00890e8`；旧源非 NULL 时，后者确实向 A23 已确认的 image cache 全局槽 `62fc9698` 发起指定 key 失效。** 这不是证明每次照片切换/退出都会失效，也不是新增照片业务恢复。

## 继承的旧结论与实际缺口

|既有出处|已解释行为|局限|本轮实际补充|
|---|---|---|---|
|A23、A24；A25、A26|session cache 身份为 G+11c=`62fc9698`；查询 key 的 source word+4、class byte+8；payload cleanup 和 Pixel/raw 归还合同|没有正常上层失效接入|直接继承身份与 key 布局，不重导 session/PNG/析构|
|A27 `image-cache-cleanup-a27-0041-20261023.md`|`a019cfbe(cache,key)` 查到 entry 后，无引用立即移出/cleanup/free；有引用先 byte+c=1，再移出，最后 release 才清理|上层调用者、实际 cache 实例未闭|只补正常 caller 的参数、对象和 key；A28 独立复核 A27，不与之重复|
|`whole-rom-coverage-0041-20261023-round1.json` 的 `a00890e8` direct_calls，Evidence `ev_aa9eff0143bddc43c0c1b0b05731f7a92d3bdbb24e2bf4b70b362f5bbc331697`；extent `ev_44fc0b37046e3a6b7342f3943233f4174dc3f8286fd3ec79965478a81a216216`|旧清单早已有 `a00890e8→a019cfbe` 关系|地址关系并未解释 ABI 和两个 cache 身份|复用种子，仅核接入窗口，不全 ROM incoming 扫描|
|同清单 `a00ed7f4` direct_calls，`ev_1980883cc9366d20118371e1856a8a9a575f620da7729d9e874e6a8c2312e1ba`；extent `ev_c74f66dc31276048f57322477a4b334b0f97717cd3d9ee5c93095866c072e21b`|旧清单已记 `a00ed7f4→a00890e8`|没有旧源门、getter/参数身份|只核 +5c 门、+2c getter 与紧邻直接调用|
|`photo-evidence-round3.json` rea_records[3]，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`；`system-complete-0041.json` cached_evidence/main_a00afc88；main-knob round2|照片主旋钮分支旧反编译已写五项索引轮转及 `a00ed7f4(*puVar17,uVar7)`|新 source 实参由 `custom0.rd()` 表示，不能据此认证来源/ABI|明确继承，不把照片调用称首次发现；本轮不扩大该厂商字窗口|
|`page-logic-0041.json` records[15] `ev_794a176f91454b7304c06fbfaff53024aa96bf8a3a51698dbb831f8b9359f9ef`|memset dossier 中早已有 `a00890e8` caller 线索|不是其失效业务合同|只引用，不将 dossier 命中当全函数恢复|
|最终 SIM 报告、matrix、factory map、四个 complete、较晚 round3 与最终 ZIP|SIM/照片重建及父级验收已有；旧 pending 不作为缺失证据|不能证明 ROM 全部生命周期/来源；本批其余词项无命中仅是有界查询|不启动 SIM/构建/回放；不解包/复制或执行 ZIP 成员|

`reuse.json` 保存当前 rehost 全部 JSON、优先报告、pass3 与 ZIP 35 个文本成员的有界词项查询。ZIP 无本题地址词项命中不表示此前从未分析。没有重建全资源、PNG 或分类表。

## 本轮复核或纠正

A27 的失效实现可靠合同直接引用，没有重新读出或导出 `a019cfbe`。本轮没有发现应改写 A23–A27 的语义。尤其不能把以下两个 cache 混为同一对象：

- `a00890fe` 读取 G+120=`62fc969c`，第一个失效 call 使用它；其 key 的 source 在+0、class byte 在+4。
- `a0089172` 读取 G+11c=`62fc9698`，第二个失效 call 才使用 A23 image cache；key 的 source 在+4、class byte 在+8。

照片 round3/system complete 的 `custom0.rd()` 是旧模型具体不可信位置；本题无需靠它推导后面的旧源接入，故保留该实参断边，不把来源字符串或候选 LVGL 实现当修复。

## 本轮真正新增

### 正常旧源门和直接调用

`a00ed802` 把对象 word+5c 保存到 s2，并保持原对象到 s1；`a00ed80a` 若其为零跳到 `a00ed830`，跳过本轮接入。非零路径 `a00ed80e` 调 `a00eaa50(obj)`；其正常非 NULL 尾部 `a00eaa9c` 是 `LW a0,+2c(a0); RET`。紧接着 `a00ed812` JAL 到 `a00890e8`，其间没有重新装 a0。因此失效实参是当前对象 +2c 的旧 source，不是新传入 a1，也不是对象 +5c 指针。

旧 whole-ROM source-path 指针 `a037a528` 的原字符串是 `.../src/libs/gif/lv_gif.c`，`a00eaf4a` 路径 `a056b0ec` 是 `.../gif/gifdec.c`。它们辅助定位 GIF 来源候选，不认证准确版本或整库来源。上述结论依赖字段/实参指令，不依赖候选函数名。没有展开 GIF 解码或照片绘制。

### 相同 image cache 与相容 key

`a00890e8` 的源参数保存到 s2。以下仅概括**非 NULL 旧源**接入，不表示全部函数原源码：

```c
source = a0;
// G = 0x62fc957c；第一个 cache 身份不同，不套用 image payload 合同。
key0.word[0] = source;
key0.byte[4] = a00dd454(source);  // class helper 沿用 A23，不重做分类
key0.word[1..5] 的其余字节来自此前 word 清零;
a019cfbe(load32(G + 0x120), &key0);

memset(&key, 0, 24);
key.word[1] = source;
key.byte[8] = a00dd454(source);
a019cfbe(load32(G + 0x11c), &key);
```

第一次 key 由 `a008912a..913a` 清零五个 word，`913e` 写首 word、`9146` 写 byte+4；第二次 `9158..9160` 明确以 a2=24、a1=0 清零同栈区，`9166` 写 word+4、`916e` 写 byte+8。`a0089150` 与 `917a` 的 AUIPC/JALR 目标均核为 `a019cfbe`。第二个 key 的布局和全局 cache 槽与 A23 session 查询一致，闭合的是**同一 image-cache 实例与相容查找 key**。

调用 `a019cfbe` 不等于必找到 entry 或必设置标记：backend 查询是否命中及该 entry 是否仍被持有决定其分支。只有查到同 key 的有引用 entry 时，才能继承 A27 的 byte+c=1→移出→后续最后 release 清理合同；零引用分支继承立即清理合同。没有声称无命中创建 entry、清理所有图片或运行时命中成功。

## 仍未闭合的精确边

- 本轮闭合到 `a00ed7f4` 的正常旧源分支；没有认证主旋钮照片分支 `custom0.rd()` 所产生的新 source，也不证明每次切换都满足对象+5c 非零。
- 旧源为 NULL 时 `a00890e8` 另走清空 API `a019cf58`，本题不展开；不得把非 NULL 指定 key 合同套给该分支。
- 第一 cache G+120 的 payload、匹配比较器/副本 key 身份未恢复；与 G+11c 严格分开。G+11c 查找的实际 runtime 命中/引用数/是否触发延后 cleanup 未执行观察。
- 未追 `a00eadf6`/`a00eaf4a` 其他 retained caller 的完整生命周期，未恢复正常页面退出/切页一定触发失效的连接，不扩大成所有 cache invalidation。A27 的计量/排序/heap 未知原样继承。

本轮新增只是 1 条正常 API 到既有 image-cache 合同的接入连接；照片旋钮行为、API caller 地址清单、失效与清理内部均继承，不重复记新增业务。后继如需复核，仅审本报告 +5c/+2c 旧源门、双 cache/key 身份与直接调用 ABI，不再重扫 incoming 或展开 GIF/PNG。

## 必要静态验证

独占 `reverse/analysis/image-cache-invalidation-a29-0041-20261024/verify.py` 只读原 ROM，以 `file_offset=VA-0x9ffff000` 验证 6 个必要窗口，共128 B、37条指令、21项原编码/调用目标检查，全部通过。`evidence.json` 仅存上述接入窗口；没有重新导出 A27 失效内部或整函数。没有厂商指令参与所核接入窗口。无固件执行、SIM、构建、历史回放、设备/网络；不改生产代码、ROM、配置、分析器模型。本报告待独立技术复核。
