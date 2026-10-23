# A27：image cache release 到既有 payload cleanup

2026-10-23；独立基线 `f2d4bc9`，分支 `codex/re-0041-a27`。只恢复 A23/A24 明示的 cache 后端连接；**release 不等于立即 free**。正常有效 entry 的 word+4 减一后，重读引用数；只有数值为零且 byte+c 非零，release 才调用 cache+18 的既有清理 callback，再释放 payload/entry 共用分配基址。未标记条目归零后仍留存。插入容量不足时另有选零引用 victim、移出索引、清理、释放的路径。

## 继承的旧结论与实际缺口

|既有出处|已经解释的行为|证据局限|本轮补什么|
|---|---|---|---|
|A23 `png-session-lifecycle-a23-0041-20261023.md`，A24 独立复核|session close 在已知门控下调用 `a019d9f6(cache,entry)`；`a008abb0` 安装为三 word callback 表第三槽；cleanup 先处理 owned pixel，再按 class1 处理 source 副本；payload 本身不由 callback 释放|明确未恢复后端何次 release 调用 cleanup|引用原合同，仅补引用/标记判断、callback 实际槽连接和分配基址释放|
|A25 `pixel-memory-contract-a25-0041-20261023.md`，A26 独立复核|默认 handler 表绑定；Pixel/raw 分配、对齐、直接销毁先 raw 后 Pixel|并未证明每次 cache release 触发析构|原样继承，不重做 PNG、默认表或析构|
|`whole-rom-coverage-0041-20261023-round1.json`：`a019d9f6` 的 `ev_db4d09f13700851ceab5594f52b0512798e338b1d87b9f6d68468adcd8bcf685`，extent `ev_437047f402084c5e91a9dcb9916360ccd1bfe62dc2d0ad9ed0e4ea9b5f9a43c5`|有入口范围、source candidate 路径与直接 callee 清单|不是 ref、标记、ABI 或 cleanup 时序的行为证据；并未认证 LVGL 来源|只按留存入口定位短窗口，不把已有地址清单重计为新发现|
|旧最终 SIM 报告、matrix、factory map；四个 complete；page-logic、details/charge round4；pass3；最终源码 ZIP 的 35 个文本成员|本批有界 token 查询未命中本题 cache 地址、callback/字段名称，见 `reuse.json`|无命中只说明这组文件/词项，不能推出从未分析；SIM 验收和替代服务也不能证明 ROM 后端|不重新跑 SIM、不复制源码，不把旧 remaining/pending 当当前缺口|

查询包括 `a019d9f6`、`a008abb0`、`a019d914`、`cache_entry`、`lv_cache`、`cache_release`、`cache release`、`cache+`/`cache +`。近期 A23–A26 本来就覆盖安装/析构，检索命中直接继承。证据分类：A23–A26 是带原字节且已复核的行为合同；whole-ROM 清单是地址/来源候选；SIM/ZIP 是重建材料；实际尚缺的是 cache release/失效/容量驱逐到已知 callback 的连接。

## 本轮复核或纠正

只对 A23 的 callback 安装原字节和 entry-to-payload 适配末端作**旧结论复核**，不是新增业务恢复。`a008e64e/e652` 形成 `a008abb0`，`e660` 放第三槽；`a008e67c` 的 AUIPC/JALR 实际指向 `a019855e`。新核该创建器正常片段：以 backend 首槽调用取得对象，保存 backend 到 cache+0、容量到+8，三 word callbacks 复制到 cache+10..1b，因此原第三槽的身份实际是 **cache+18**。

`a008b654` 的 `b6a0/b6a2` 是 `payload = entry - load32(entry+8)`，不是 `entry+固定常数`。A23 已保存此适配器；本轮只复核两条。创建器的 +4=0x18 不能据此宣称完整 entry/header 恒长24字节；适配器使用 entry 自身 +8 的运行期偏移。

旧报告没有被改写，也没有把来源候选当开源排除。原反编译模型未用于推导以下厂商指令或 ABI。

## 本轮真正新增

### 正常 release 的引用与失效门

`a019d9f6(cache,entry)` 的正常路径 `da4c..da5e` 保存 cache 到 s2，entry 到 s1。`a008b604(entry)` 正常尾部返回 word+4；`da5a` 又从 entry+4 取值。若旧引用非零，`dabe/dac0` 减一并写回 **32位 word**，`dac2` 使用有符号 `bgez`。本题只解释正常合法引用范围；未展开负数诊断、NULL/assertion 或异常输入研究。

回到 `da84` 再调用 `a008b604(entry)`：

```c
// 仅正常有效参数/引用范围的结构化伪代码，不是原源码。
void release(Cache *cache, Entry *e) {
    if (entry_ref(e) != 0)
        e->ref_word = e->ref_word - 1; // RV32 word；原实现保留 signed 检查
    if (entry_ref(e) != 0) return;     // callback 后没有复用旧计数
    if (load_u8(e + 0x0c) == 0) return;
    void *payload = entry_payload(e);
    load_fn(cache + 0x18)(payload, NULL);
    destroy_entry(e);                 // 重新算 payload 基址，然后 free
}
```

`da90` 是 **LBU byte+c 整字节非零判断**，不是 bit0 掩码；不能自行把其余 bit 定义为 flags。`daa0/daa4/daa6` 以 `a0=payload,a1=0` 调 cache+18；没有传 cache 作第一个参数，也没有把 session 传进去。`daa8..dab2` 随后 `a008b6a6(entry)`；其正常末端 `b6f2→a008b654`、`b6f6→a008ab8a` 先重新取得 payload 基址再 free。该 helper 没有另行 free entry 指针；entry 是这块分配中的内部位置。

因此：未标记且降至0的 entry 仍可缓存；被标记 entry 在最后引用 release 时才销毁；已有0且标记非零时也走 cleanup。原实现不把 decrement 的返回值当最终引用数，也不在普通 release 中作 backend 索引移除。

### 谁设置失效字节

`a019cfbe` 的正常片段 `d014..d070` 先通过 backend+0c 得到一个 entry，再读取引用数。引用为0：backend+14 `(cache,entry,0)` → `entry_payload(entry)` → cache+18 `(payload,0)` → `a008b6a6(entry)`。引用非零：`d05e/d060` 用 SB 将1写 byte+c，然后 backend+14 `(cache,entry,0)`；此分支不在当前调用中清理 payload。之后该 entry 在原持有者 release 时由上面的零引用+标记门清理。

这里只恢复该正常 API 的局部行为。谁在上层调用这个指定-entry失效 API、何种业务动作导致失效，未作新断言。byte+c 的“待销毁/失效”语义来自这两条实际分支配对，不来自 LVGL 候选源码。

### 插入容量门到真实驱逐清理

`a008e67c` 创建器接收 backend 常量表 `a0263afc`。表中与本题有关的原 word：+10=`a00ebb90`（插入接入）、+14=`a00ebe98`（移出接入）、+20=`a00ec1e6`（victim选择）、+24=`a00ea78c`（容量门）。完整十 word 仅作为这一对象身份的表证据留存，没有重建全库分类表。

`a019d914` 的容量检查由 backend+24 `(cache,key,0,0)` 完成。结果2时，`d9c6/d9c8` 调 `a019d898(cache)`；返回非零后重新检查容量，仍为2则循环；helper 返回0则本次插入返回NULL。容量结果1也返回NULL；其余正常结果转 backend+10 插入，非NULL才调用 `a01b2fbe`。本轮仅核引用 helper 的 `b3012..b3018`：word+4 加一；原先已知 session/entry 发布不重做。

容量门 `a00ea78c` 正常片段：可从 key 经 cache+3c 回调计算申请量（key 为NULL则申请量0）；以无符号容量比较，并比较 `cache_used(+c) + 第三参 + 申请量`。所核调用点第三参为0。大于容量返回2，可满足返回0；申请量本身大于容量走返回1。加法是 RV32 加法，没有提升为64位。计量单位没有来源认证，本报告不把 `0xe1000` 推为某种像素数或完整缓存大小规则。

`a019d898` 的正常链：

```text
backend+20(cache,0) → victim
  NULL: 返回0，未调用payload cleanup
  非NULL: backend+14(cache,victim,0)
          → a008b654(victim)
          → cache+18(payload,0) [原安装目标 a008abb0]
          → a008b6a6(victim)
          → 返回1
```

实际 backend+20 为 `a00ec1e6`：从 cache+38 的节点起，节点关联 word+10 转 entry，并加 cache+4 取得引用 header；`ec266→a008b604`，引用数0才返回该 entry。非零则沿节点关系继续；到NULL返回NULL。因此有引用的候选被跳过，不先强行清理再检查引用。`ec270` 原字 `0b49f940` 是 `th.lrw s2,s2,a5,0`：字段 `[opcode,f3,top5,rd,rs1,rs2,shift]=[11,4,8,18,18,15,0]`，其索引是 `a5=load32(cache+30)`；**只加载 `*(s2+a5)`，不作基址自增写回**。只引用既有只读 `ap01thead2.sinc` 的 lrw 语义，未改分析器。

backend+14 的目标 `a00ebe98` 所核正常尾段 `bf26..bf6a` 先由 entry 算 payload，移除相关索引/链节点，随后通过 cache+3c 重新取用量，从 cache+c 扣除。其索引树内部算法、排序/LRU策略不在本题，未全函数恢复，也不以名称推定。调用返回后才由 `a019d898` 调 payload cleanup；**驱逐清理和 release 清理是两个有不同前置条件的接入点**。

### 所有权结论

沿 A23 已有 image cache 实例，cache+18 的身份已闭合为 `a008abb0`；由既有合同，callback 可按 owned 位销毁 Pixel/raw，并按 class1 释放 source 副本。callback 返回后后端才释放 payload 基址。release最后引用不一定触发此链，容量驱逐选中的零引用 entry 才走另一路完整链。ROM class0 source仍是借用；本轮没有新增原PNG解码、raw释放或每张图片执行成功的结论。

## 仍未闭合的精确边

- `a019cfbe` 的实际上层失效调用者和触发业务动作仍未知；不能据静态局部分支声称某次照片退出/页面切换必然标记 entry。
- cache+38/+30 的全链排序、victim优先级及索引helper算法未认证；仅证所核选择循环跳过非零引用。底层heap策略、复用、动态callback/容量重配及并发同步未展开。
- cache+3c 的完整计量回调及单位未恢复；本题只保留容量门调用ABI/返回与清理连接。没有整库LVGL来源认证或开源排除。
- 不证明运行时真实缓存命中率、何次具体session close发生驱逐或解码成功；未执行固件/SIM、构建、历史回放或设备/外部服务。

本题原断边已在正常引用/标记/容量驱逐范围内补上；余下是上述明确边，不扩到全cache或heap。后继如需技术验收，只独立复核新增的计数宽度、byte+c、cache+18间接ABI、lrw无写回及清理原序，继承A23–A26，不重导PNG/析构。

## 静态验证与可复用证据

运行独占 `reverse/analysis/image-cache-cleanup-a27-0041-20261023/verify.py`：16个必要正常短窗口，572 B、228条指令、54项原编码/调用目标/访存字段/表身份断言，1条厂商指令，全部通过。窗口不包含NULL/assert诊断、负数诊断或完整PNG/heap/整cache导出。`evidence.json` 保存这些窗口及相应原字节；`reuse.json` 保存有界复用查询。原ROM只读，映射 `file_offset=VA-0x9ffff000`。继承复核锚点单独标识，不计新增业务。
