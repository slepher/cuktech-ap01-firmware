# K03：K01 事件、class 绑定及全局对象的局部合同

2026-10-24；基线 `565dc6e`；独占树/分支 `re0041-k03` / `codex/re-0041-k03`。用户明确恢复后，只补 K01 所列精确边。**已给出 class callback 的双参身份、祖先事件状态的精确返回来源、原 mask/分支字段，以及同 class 创建结果到 `62fcb6b0` 的保存连接。正常 count/索引成立条件只能写成外部前置，尚无证据保证所有调用时刻满足；全局槽不认证唯一所有者。作者静态检查完成，待新独立 agent 技术验收。**

使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读取主仓 ROM、既有报告/证据；未打开/切换共享 REA target，不运行固件、SIM、构建、模型、历史回放、设备或外部服务，不做异常输入/漏洞/缺陷验证。只写独占报告和 analysis，无生产代码/ROM/配置/分析器模型变更，无下级 agent。函数/字段名字为分析视图，伪代码不是原源码。

## 继承：按地址、字段和 callback 去重

|既有出处|可靠合同及本轮处理|局限|
|---|---|---|
|[K01](window-slider-entry-k01-0041-20261024.md)，[J04](factory-reuse-gap-j04-0041-20261024.md)|入口 `a00a4cac`、三个 callee 及 `factory_ui/lv_window_slider.c` 归属早已有；只补未验收的接入/原字段|不把旧 extent 或地址重新计作发现；不套日常 `a00b2ff4/a00b3106` 对象|
|[H03](weather-page-close-h03-0041-20261023.md)、[H04 独立复核](weather-page-close-review-h04-0041-20261023.md)|事件布局 `current_target@0,target@4,code@8,user_data@c,param@10,previous@14,flags8@18`；class callback 双参；descriptor callback 单参；`a00d8af6` 原 code 恰为11h 才从非空 param 读 word；`a00ded6c` 公共删除与下层责任|全部直接继承，不重做 dispatcher、getter、删除/析构全链；这些旧合同不是 K03 新恢复|
|旧 `whole-rom-private-20261023-036/043/047.json`，见 K01 evidence 的 Evidence ID|`a00a4116` 读对象+38；`a00a491c` 调 `a00dd144`；`a00a4aa0` 的旧索引、位置/动画与+38/+3c原序|043 的伪码 void 不能覆盖其 a0 返回；只核返回接线和必要门，不重新导出三个 body|
|[application complete](application-rehost-complete-0041-20261017.md)、J04 的最终 SIM/reference-map/rehost/ZIP 范围盘点|旧 SIM/照片/安全替代服务与原 ROM ABI 分开；沿用 J04/K01 有界检索，不重复整矩阵/源码/资源导出|passed-in-sim 不等于原 ROM 完整恢复；无文本命中不等于从未分析|
|旧 `whole-rom-private-20261023-068.json`，Evidence `ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`|原 dispatcher 旧完整 body 已含 `8cc4` 的 class 创建及 `8d22` 全局保存种子|旧伪码只定位，本轮稀疏读原字核对象连接；不接管 cmd50/51、GPIO、全部工厂功能|

旧 JSON 的主仓载体均位于 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/evidence/rea-0041-20261017/evidence/`。没有复制整 body 或生成新 REA Evidence ID；四分报告与范围规则继承 rolling-management/history，停止条款由本次明确恢复指令覆盖。

## 复核或纠正：入口原字及状态的精度

[verify.py](../../analysis/window-slider-contract-k03-0041-20261024/verify.py) 只读原件，映射 `offset=VA−0x9ffff000`。没有导入 K01 脚本，也不执行输入或原指令。必要锚点及字段检查见 [evidence.json](../../analysis/window-slider-contract-k03-0041-20261024/evidence.json)。

|K01 记录|原字复核与解释|裁定|
|---|---|---|
|incoming a1 为 E；先调 helper 且返回必须1|`4cb8/4cbc` 构造 `a03725cc`，`4cc0` 保存 a1，`4cc2` JAL 真实目标 `a00d81f8`；`4cc8` BNE a0,a5→4cf2，a5=1|接受；返回的意义在下节补齐|
|E+0 与 E+8|`4ccc` LW a5,8(s2)，`4cda` LW s1,0(s2)；对应 H03/H04 current_target 与 code|接受；O 是当前投递目标，不能改成 original target@4 或事件 userdata|
|mask 与事件分流|`4cd0:6177` C.LUI a4,ffff8；`4cd2:7d17` C.ADDI −1，得到 `ffff7fff`；`4cd4:f98f` AND。`4cde` BNE→4cfe，`4d00` BNE→4cf2|接受，确实只清 bit15，比较31h/11h；不凭候选枚举命名31h|
|key19 左侧环绕|`4d16:6356a000` 独立 B 字段为 BGE x0,a0→4d22，即 signed a0≤0；正数走 index−1，否则 count−1；方向2|接受原 signed 门，不能写 unsigned index>0|
|key20 右侧环绕|`4d36` word 加1，跨 count 调用后重读候选；`4d48:63e3a500` 为 BLTU a1,a0→4d4e，否则 index=0，方向1|接受 unsigned 门；不新增 count>0 检查|
|key10 删除/清槽|`4d58` 读 O+38，零分支至4d62；`4d64` JAL `a00ded6c(O)`；`4d6c` SW zero 到 `62fcb6b0`；原 C.J 回出口|接受局部原序，删除调用先于清槽；未比较 O 与全局当前值，也未检查删除结果|

H04 已证 key helper 比较的是**未被 K01 写回修改的原 E.code**。K01 只在寄存器里清 bit15，没有改 E.code。因此“mask 后等11h”只使控制流到 key getter；实际 key19/20/10 路径仍依赖 helper 接受原 code 恰为11h且 param 有效。此为旧合同与调用点连接的精度补充，没有输入实验或新安全门。

## 真正新增：三个必要连接

### 祖先 class 事件 helper 的返回来源

`a00d81f8(C,E)` 中，C 非零时 `81f8` 直接到 `822c`，先读 `C.base@0`。C=0 时才从 E.current_target→object.class 起查。空 class 在 `8230` 返回1；class+c 没有 callback 时继续沿 base 查找。找到首个非空 callback 后，`820e` 清 E.user_data word+c，`8212/8216` 以 `(祖先class,E)` 间接调用。`8218` 重新读取 E.flags byte+18，覆盖 callback 的 a0；`8220/8226` 返回 `(~flags)&1`。

因此 K01 传自身 class `a03725cc`，这里是先送给祖先 class 事件处理，再以返回值继续自身逻辑，**不是 class 类型校验、callback 自身布尔返回或对象非空测试**。返回1的可证位义为：没有找到祖先 callback，或被调用后 E.flags bit0=0；返回0来自该 bit0=1。H03/H04 将该位与对象删除期间标记联系起来，本轮保持位合同，不给它另造正式 enum 名称。这里只调用首个非空祖先 callback；其内部是否继续递归由该 callback 负责，不能补成 helper 自己遍历调用全部祖先。

### class 表、实际工厂创建及全局对象身份

只读 `a03725cc` 的前四 word，原值依次为 `{a0263ef4,a00a4bdc,a00a4c54,a00a4cac}`。按已核 class 布局，`+c` 的 event slot 确为 K01；这不是通过日志名猜 callback。旧 dispatcher 的真实创建种子 `a00a8cbc/8cc0` 形成同 C，`8cc4` 调 `a00d76ae(C,parent)`，`8cc8` 保存返回 O 到 s2。generic factory 的 `d76c0` 保存 incoming class 到 s3，成功分配路径 `d76e2` 将 s3 写进返回对象 word0（零返回在 `d76e0` 绕开该写入）。由此静态证明成功创建对象安装的 class 与 K01 callback slot 相同。

`8b90/8b9c` 将 s7 建为 `62fcb6b0`；`8d22` SW s2,0(s7)，`8d2c` 又从该槽重读，连接到同一创建结果。`8d1e` 存的是 O+30 的另一个 handle，不能把 global 当成该 handle。该槽是保存 slider 对象地址的全局引用；K01 的 index0/key10 路径删除当前 O 后清此槽。实际创建/调用成功、排他性、所有 writer 或 O 必然等于当时槽值仍未认证。

对象释放责任沿 H03/H04 公共删除合同：K01 交给 `a00ded6c(O)`，由其正常删除核心/对象树/class 析构路径承担；清全局 SW 不等于 free，也不证明所有附属 context 最终归还。没有把全局引用升级为唯一 owner，没有扩根析构、输入组完整寿命或工厂 GPIO 关联。

### count/索引前置条件与原门的边界

`a00a491c` 在 `495a` 调 `a00dd144(O)`，其尾声不覆盖 a0。后者有效对象路径 `dd190..dd19a`：extra=LW(O+8)，extra空返回0，否则 LHU(extra+30) 返回 child count N。因此 N 是无符号16位值，a0=0..65535，不是状态码或有符号 halfword。class constructor 的 `4c40/4c44` 初始化当前+38、先前+3c为0；这不保证稍后 N 非零。

沿旧047，setter 在 `4af4` 只要求 count非零，并在 `4af8` 跳过当前索引等于请求索引的情况；没有在这个门加入请求索引<N或当前索引有效检查。对于调用时已有的正常条件 `N≥1`、`0≤idx<N`，key19 给出 `idx>0 ? idx−1 : N−1`，key20 给出 `idx+1<N ? idx+1 : 0`；N≤65535使正常 idx 的 signed/unsigned解释一致。该代数只说明条件成立时的正常环绕，不证明调用者已经建立或持续保持这些条件。

现有已核连接只证明构造零索引、旧 count 读取及全局保存；未认证所有 append 成功/删除变化/事件时序/串行化如何保证 `N≥1` 和两个索引有效。必须分别保留：caller没有显式count前置门；callee的已知非零/不同索引门；外部不变量未证。没有运行 count0、非法索引、异常输入或缺陷验证。

## 精确未闭、验证与后继

本题新增仅是以上祖先状态、class→创建→全局身份及 count 返回/前置精度；K01已记录的索引算法、三callee、H03/H04事件/删除合同不重计新增。未认证精确 LVGL 版本/来源，未排除整库，未宣称整个 slider/工厂 UI/ROM完成。

尚未闭合：所有正常调用时刻的 count/当前与先前索引不变量；全局槽的所有 writer、排他 owner、当前 target 与槽必然相等的上层保证；31h 正式枚举名、真实输入设备/页面可达性及产品效果；附属资源完整寿命。已知 class/factory 和清槽连接不能证明上述事实。

实际执行 `python -X utf8 -B reverse/analysis/window-slider-contract-k03-0041-20261024/verify.py`：87项稀疏检查及4个class word通过，其中13个JAL、7个B型门、6个C.J、6个压缩条件门和8个访存字段独立按原编码解算；没有导出整198B入口、整factory/dispatcher/资源/源码。JSON解析、相对链接及 `git diff --check` 另行核验。作者检查不等于独立技术接受。

下一步优先由未参与本报告的 agent 独立核上述实际增量，不重做整event/delete或三callee。若继续补功能，唯一已留存的窄种子是旧068中 `8d2c` 后的 child-append循环到 `8d82` 回边及当轮初始索引的接入，用于研究正常构造建立的 count 条件；必须先核旧合同，只取必要控制点，不展开其颜色/文字/资源内容，不将构造时条件外推所有生命周期。主窗口决定是否派发，本路不自行接题。
