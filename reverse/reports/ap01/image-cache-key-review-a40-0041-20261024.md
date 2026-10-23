# A40：默认 image-cache key 比较合同独立复核

2026-10-24；基线 `2844cc4`；分支 `codex/re-0041-a40`。结论：**接受 A38 本题合同；需纠正项0；新增功能0。** 默认初始化时 `cache+0x10` 与 `(cache+0x24)+4` 安装同一 comparator `0xa0087bc6`。source 为 `word+4`，class 为 `U8+8`；class0 比较 unsigned RV32 source 地址值，class1 按零结尾 unsigned byte 内容比较后把 signed 结果归一；同一非0/1 class 原样返回0。头调用 `(payload,key)`、树调用 `(key,payload)`，两条路径的返回0关系相同。此为静态条件，未观察任何实际命中。

应用已读 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。复用既有证据并只读主仓 ROM 稀疏核字节；未打开或切换 REA target/database，无共享可写 target。无执行固件、SIM、构建、回放、设备、网络或分析器修改。只写本任务独占报告及 analysis；不改变生产代码、ROM、配置或他人文件。

## 继承结论：已有出处→局限→本题缺口

|已有出处|继承行为|证据局限及本轮处理|
|---|---|---|
|[A38](image-cache-key-a38-0041-20261024.md) 及其 [evidence.json](../../analysis/image-cache-key-a38-0041-20261024/evidence.json)|默认安装、字段、class比较、两个入口与零等价的完整本题说明|作者自检；本轮独立阅读控制流、直接核 ROM 并按字段解 branch/JAL/LBU/厂商字，不重复整函数|
|A38 [reuse.json](../../analysis/image-cache-key-a38-0041-20261024/reuse.json)|complete/round4/pass3/round3/ZIP 的既有有界复用检索|未命中只代表该精确检索边界；不重做搜索，不宣称历史不存在分析|
|[A23](png-session-lifecycle-a23-0041-20261023.md)/A24|默认初始化 callback 表身份，PNG key source/class、payload、Pixel/source owner|直接继承 source 表和正常 PNG 输入身份；本轮仅复核首 callback 常量与安装连接|
|[A27](image-cache-cleanup-a27-0041-20261023.md)/A28|release/失效/cleanup/free 原序与所有权|直接继承，不新增分配、释放或生命周期动作|
|[A30](image-cache-accounting-a30-0041-20261024.md)/A32|首 word 为 data_size 及成功计量|直接继承；本 comparator 读取 +4/+8，不把 +0 当匹配字段|
|[A34](image-cache-order-a34-0041-20261024.md)/[A36](image-cache-order-review-a36-0041-20261024.md)|头快路径、fallback、排序/提升/victim 与返回重读|直接继承；只复核两条比较接入及0门，不扩平衡树或插入|

旧反编译只定位；本题裁决依赖已留原字节与独立字段复核。SIM/照片替代不支持 ROM ABI，本轮不据此立论。没有来源版本认证或整库排除。

## 本轮复核或纠正：逐项裁决

独立原字节断言见 [review-evidence.json](../../analysis/image-cache-key-review-a40-0041-20261024/review-evidence.json)，生成器为 [verify.py](../../analysis/image-cache-key-review-a40-0041-20261024/verify.py)。原 ROM 映射沿用 `file_offset=VA-0x9ffff000`；原始载体身份继承 A23。以下地址均为该 0041 image 的 VA。

|待核项|裁决|定位与理由|
|---|---|---|
|默认 `cache+10=a0087bc6`|接受|`a008e642..e64a` LUI/ADDI 产生该地址写首槽；表身份继承 A23。`a01985cc..85e0` 保存 cache，a2=12、a1=原 callbacks、a0=cache+10 送已有 copy adapter。不是新的 initializer 恢复|
|默认 `tree+4` 同函数安装|接受|`a00f0d26` 取 cache+10→a1；正常非零链 `d28→d6a`、`d6e→daa`、`dac→de0` 不改 a1；`de2` 设 a0=cache+24，`de6` 直达 a00f0b80。`c02` 保存 a1 到 s2，`c18` 写 tree+4=s2。是默认初始化等式，不证明动态永久相等|
|source word+4 / class U8+8|接受|`a0087bce/bd4` 位域解为 LBU，分别从 right/left+8 零扩展读 class；`bd2/bd8` C.LW 取 source+4；`bda` 直接调用 a0087b5c。`bde..be4` 尾声不改 a0，原样返回比较结果|
|不同 class 的 unsigned 排序|接受|`a0087b5c` BNE→7b9c；`7b9e` BLTU a3,a1→7b98 的 +1 门，否则保留 -1。class 已经 U8 零扩展；不混用 signed byte|
|同 class0 的 unsigned 地址比较|接受|`7b8e` source 相等→7ba2 返回0；否则 -1 为候选，`7b94` BGEU right,left 保留 -1，否则写 +1。只比较32位 source 值，不读取 descriptor 内容|
|同 class1 内容与 signed 归一|接受|`7b70` 直调 a002db16。A38 的 `db1a..db38` 对齐门与 `db58..db6e` 相等 word 零检测控制流可复用；常量组合为 `(word+0xfefefeff)&~word&0x80808080`，检出零则0，否则地址各加4。独核 `db3e/db42` 厂商字是 shift0 的 th.lrbu，rd=a5/a3，base=a0/a1，index=a4，按已留规则零扩展 byte。`db46` 左零结束；`db4a` 相等则继续；`db4e` SUB 返回两 U8 差−255..255。`7b74..7b7e` 零→0，signed BGE zero,result 的非正门→-1，其余+1|
|同非0/1 class 原返回0|接受|`7b62` 排除 class1 后，`7b8a` a5=0；`7b8c` class非零直接跳7ba2，未读取 source 内容。保留原行为，不补其他class比较|
|头/树实参方向及返回0|接受|头 `a00eba8c..ba94` 取 cache+10，a0=payload，a1=key 继承 A34，非零 fallback；树 `ea842/844` 保存 descriptor/key，`ea858..862` 取 tree+4、a1=payload、a0=key，0返回候选。方向确实相反|
|两入口零等价|接受|同class0：source值相等；同class1：零结尾 unsigned byte 内容相同；同其他class：恒0；不同class：均非0。各项零条件交换左右保持不变。只据静态分支作推断，不做输入/重复insert实验|

上述表中没有需纠正项。压缩 branch 的目标按原编码及 A38 留存反汇编交叉阅读；标准32位 branch/JAL/LBU 与两个厂商 word 另按位域核，不仅凭反编译输出。厂商规则只读 `ap01thead2.sinc` 的既有 th.lrbu 规则；这是静态模型一致性，不能当设备执行证明。

业务上，默认 cache 用 key 的 source/class 匹配，计量首 word 与 payload 中其他 owner 不参与本比较。PNG class0 descriptor 的借用地址及 class 必须匹配；class1 的既有字符串副本仍按内容匹配。后者复制/释放所有权直接继承 A23/A27，本轮不重新恢复。排序、计量、cleanup 与异常路径均未扩展。

## 真正新增

**新增功能0。** 本轮是 A38 的独立技术复核；有效初始化分支链、适配器原样返回和必要字段断言是对旧结论的复核证据，不计作新增功能。没有新生产实现、源代码恢复或模型改动。

## 未闭精确边、验证与后续闭包

本任务所列默认安装、字段宽度、signed/unsigned、同其他class返回0及两入口零等价均接受。下列未核且不影响该有限结论：动态 `cache+10`/`tree+4` 修改者与同步、同非0/1 class 的正常构造协议、重复insert前提、完整平衡树、实际图片命中/驱逐、字符串helper精确来源版本。初始化一致不能外推运行时不可修改；静态判定不能外推已观察实际命中。

实际静态验证：独占 verify.py 只读主仓 ROM，33项稀疏原编码/寄存器与 branch/JAL/LBU/厂商字段断言通过；另解析本轮 JSON、核报告相对链接、`git diff --check`。未重导整函数、未复制旧源码/资源、未运行旧脚本（避免覆盖旧任务证据）。本轮报告本身为独立复核结果，没有自封其他题目的验收。

一个后续闭包：若后续确需动态重配合同，应仅从 `cache+10` 与该实例 `tree+4` 的实际写者/调用点起查同步连接；当前没有这条证据，不扩为本轮必需工作。本题复核已完成，可结束并由管理者决定后继。
