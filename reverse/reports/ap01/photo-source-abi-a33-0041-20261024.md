# A33：照片主旋钮的新源实参 ABI

2026-10-24；基线 `b673714`，分支 `codex/re-0041-a33`。仅核已知照片正常分支到 `a00ed7f4` 的新源接入。**旧 `custom0.rd()` 在 `a00b180c` 实际是 `th.lrw a1,a5,a6,2`：按索引读取 ROM 表 `a055fe44` 中的描述符指针，作为 setter 第二参数。** 照片轮转、源表存在及调用地址均已有留存；新增的是该厂商字的可信 ABI 和对象身份连接，不是新增照片业务。

## 继承结论：已有出处→行为→局限→缺口

|既有出处|已解释行为|证据局限与本轮处理|
|---|---|---|
|主仓 `photo-evidence-round3.json#/rea_records/3`，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`|完整主旋钮 `a00afc88` 已有 type7 查找、五项轮转、setter、保存索引顺序|较晚 round3 仍明确 `uVar7=custom0.rd()`；不能仅凭完整 body 认证这条厂商字|
|`main-knob-0041-round2.json#/records/1`，`ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`|同一分支的汇编已留存 `a00b17ea..183a`，包括表基址和 `a00b1816` 调用|原汇编存在不是本轮发现；只对必要局部按 ROM 原字复核，不导出整主函数|
|`system-complete-0041.json#/cached_evidence/main_a00afc88`；detail-knob round2|父级 complete 同样留存该主分支，详情旋钮为旧导航合同|核最新材料后仍是同一 custom0 限制；详情分支无需重复恢复|
|最终 `ap01-ui-0041-complete-source.zip` 的 `tools/ap01/ap01-ui-pages.h`|SIM 以 `lv_gif_set_src(pet,&ap01_pets[g_ap01_ui_pet_index])` 重建照片/宠物页|这是替代实现，不能证明 ROM 的表地址、指针加载 ABI 或复制策略。只读成员，没有解包/执行|
|A29、A31|对象+5c 门、+2c 旧源 getter、`a00890e8` 到同 image-cache 的指定 key 失效已闭|全部继承；本轮不重做旧源、双 cache、cleanup|
|A23–A28|source 分类、PNG/session/Pixel/raw 所有权、失效和延后 cleanup 已恢复|直接引用；不把 PNG cache 合同套为 GIF 内部所有权，不重做资源/PNG/分类|

独占 `evidence.json` 的 reuse/late_round3_hits 留下本题的有界复用检查；未命中不是此前没有分析的证明。ROM 身份沿用原件 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9` 与原映射 `VA-9ffff000`，没有新建哈希清单。

## 本轮复核或纠正

不纠正旧五项轮转业务或原调用顺序；纠正的是把 `custom0.rd()` 当成无可认证输入的残余表示。原字 `8bc50745` 的字段为 opcode=0b、funct3=4、bits31:27=8、rd=11(a1)、rs1=15(a5)、rs2=16(a6)、shift=2。现存只读 `ap01thead2.sinc` 的 `th.lrw` 规则为 `rd=load32(rs1+(rs2<<shift))`，不更新 base/index。模型规则是局部语义依据，原字位域独立拆解；未修改分析器模型。

`a00b1804/1808` 的 LUI/ADDI 形成 `a055fe44`，所以该指令不是复制描述符，也不是把表项地址作为 source，而是把表项中的 **32-bit 指针值** 放入 a1。原字校核属于旧结论局部复核，不计重新发现完整 callback。

## 真正新增：身份、实参及借用边界

已知正常照片分支 `a00b17ea..1828` 的必要结构如下；这是分析伪代码，不是原源码：

```c
page = a00dcee4(current, 7);
ctx = load32(load32(page + 0x10) + 4);
uint32_t next = load32(ctx + 12) + 1; // 32-bit wrap，再 unsigned 比较
if (!(4u >= next)) next = 0;
source = load32(0xa055fe44 + (next << 2));
a00ed7f4(load32(ctx), source);
store32(ctx + 12, next);             // 返回之后，从栈保存槽重读 next
```

`a00b17fe` 是 BGEU，目标 `a00b1804`；不把旧 char/uint 局部类型当 ABI。`a00b1810` 以 ctx 首 word 为 a0，`1812` 将 next 保存到 `s0-144`，`1816` 的 JAL 链接 ra 且目标为 `a00ed7f4`；`181a/1824` 返回后重读并写回索引。setter 入口 `a00ed808` 保存 a1 至 s3，没有从新源参数推断调用返回值；caller 忽略返回 a0。

|索引|ROM 表槽|新 source 描述符|描述符+10 的数据地址|
|---|---|---|---|
|0|a055fe44|a01c4a50|a01c4a6c|
|1|a055fe48|a03f3b08|a03f3b24|
|2|a055fe4c|a046a894|a046a8b0|
|3|a055fe50|a04a09b8|a04a09d4|
|4|a055fe54|a037c064|a037c080|

这是表项/指针身份的最小读取，没有重新提取 GIF/PNG、解码、命名或分类资源。五项数据地址均为对应 ROM 描述符+28；它们不是临时栈对象。索引和对应表项的绑定是静态条件事实，不意味着观察到每一项实际显示。

新源的借用/复制只闭到必要接入边：`a00ed830` 用 s3 调既有分类 helper `a00dd454`；其返回0分支在 `d838` 读取 **source+10 的指针值** 作为 a0，`d83c` 调 `a0107dea`。内存输入入口在 `a0107dfe` 保存该 a0 到 s1，清零栈工作区后 `a0107e12` 将原指针写进工作区（base=`s0-674`，指针槽=base+c），`e16/e1a` 清零相邻位置/模式槽，再以工作区地址调用 `a010a65a`。因此这条边按值传递/保存了借用 ROM 数据指针，未复制整个描述符或 GIF 字节；并不转移 ROM 的所有权。这里说的借用仅限这些已核指令，不能外推构造器之后绝无内部复制。

setter 随后以 `a0107dea` 返回 a0 保存至 s2，并在 `a00ed842` 判断非零才继续成功路径；零分支进入旧日志/返回路径。未把静态 source 指针存在推成解码成功，也未把 PNG/cache 的 owned/free 合同套给此 GIF 工作对象。

## 未闭精确边与一个后续闭包

- 本题从主旋钮到 setter 的新 source 身份、厂商加载及两个寄存器实参已闭。实际执行命中、每次切页时序、对象+5c 是否非零、真实 cache 命中均未观察；A29/A31 的原边界保留。
- `a010a65a` 对传入工作区的持久化/内部数据复制、其返回对象的完整 GIF 生命周期不在已核窗口中；不能声称完成 GIF 解码器所有权恢复。若后续确有此需求，单独核该构造器中 base+c 输入指针到返回对象保存槽的连接即可，不重做照片或 PNG。
- 精确库版本、其余 setter caller 和页面退出连接未认证。A23–A28 中动态 handler 替换/heap 等未知不变。

## 必要静态验证

运行 `python -X utf8 -B reverse/analysis/photo-source-abi-a33-0041-20261024/verify.py` 通过：4个必要短窗、25项命名 ABI/调用断言，另核厂商位域及只读规则、BGEU 编码目标、5项表指针/数据槽、旧 round3/complete 与 ZIP 复用。输出只留最小接入窗口和身份值。无整函数导出，无固件执行、SIM、构建、回放、设备或外网访问；不改生产代码、ROM、配置、模型。本报告为研究交付，待独立技术复核。
