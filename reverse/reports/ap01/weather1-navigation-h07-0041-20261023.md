# H07：weather1 正常切出复用核对与 DELETE 触发断边

2026-10-23；基线 `fca1d5e`；分支 `codex/re-0041-h07`。使用 reverse-engineer-anything 技能，只做静态分析与已有成果复用。**普通主浏览切出已被旧导航成果覆盖，本轮新增业务恢复为0。没有找到应补造的“转走即删除 weather1”连接；真实主窗口 teardown→type4 页面 DELETE 仍未闭合，且与 E05 的同一主窗口正常删除触发断边重叠。** 不继续为闭包扩扫整个 UI。

## 继承的旧结论：已有成果→实际缺口

旧文件只读根为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/`。表中路径均在当前仓库真实存在；没有因旧 tools/ap01 或 artifacts 链接失效而判为缺失。独占输出仅本报告及同名 analysis 目录；没有改共享记录、他人分支或生产文件。

| 既有出处 | 已解释行为、证据类型 | 局限 | 本轮处理 |
| --- | --- | --- | --- |
| `reverse/analysis/0041-20261013/0041-ghidra-pass3.txt:2653–2657`；H05/H06 | 旧反编译已有 `(a00abed2,page)`、type4、ctx/page挂接、安装 `a00abb62`；近期独立原字复核已有68 B ctx及显式free原序 | 安装 DELETE 不证明上层正常动作实际送达 | 全部继承，不计首次身份发现，不重新导出 callback/DELETE |
| `weather-calendar-complete-0041.json`，H06复用附记所列 evidence[10/11/12/14/15/17] | 当前/预报分类、文字、详情、arc、`a0198946`消费者旧原指令；H05直接 `a019cbc0` 另有原字合同 | 分类显示及SIM验收不能证明正常删除触发；两个setter不同 | 本题不重做分类、资源、控件、PNG或释放 |
| `main-knob-0041-round2.json#/records/1`，`ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7` | 已留 `a00afc88` 主导航反编译及指令；主浏览左右键汇入 `a00afd2a→a00b3106` | 旧default模型含厂商指令/no-return限制；不能把整个大函数都当可信新恢复 | 只核本题极短标准指令分支/调用锚点；不重导整函数 |
| `reverse/analysis/screen-host-append-20261020.json#/functions`；[旧滑动报告](screen-host-append-validation-20261020.md)；[主窗口报告§3](multi-screen-app-host-0041.md) | `a00b3106`、`a00b3080/a00b30c0`、`a00ab628`已有静态汇编：保留同一子页、更新active/prev及x坐标；weather为child5/type4；ready只改busy标志并条件恢复Pet | 旧历史执行仅为其原范围，本轮不重放；设计草案不是ROM原源码认证；旧API表将a00d7806称obj_del的条目不能覆盖H03/H04的class walker纠正 | 可靠导航合同直接引用；只核状态写锚点。普通切出不能用作DELETE交付证据 |
| `system-complete-0041.json#/native_semantics/overview_order`、`overview_gates`；`guide-complete-0041.json#/guide`、`#/hooks` | 已有主环 `[0,1,2,3,4,5,7,6,8]`、Time/Date/Weather切换及引导旋钮文案；重建的reset/back/parentclean接口 | native语义与SIM集成字段须分开；引导“切换界面”文案未证明释放对象 | 不以SIM导航或reset推ROM DELETE |
| `detail-knob-0041-round2.json#/result/weather`；[H03](weather-page-close-h03-0041-20261023.md)；[H04](weather-page-close-review-h04-0041-20261023.md) | 旧详情滚页和确认键离页；H03/H04原字证实另建type19详情父W→公共删除→子DELETE | 对象是type19/116 B ctx，不是主浏览type4/68 B ctx；详情返回还会查找type4刷新 | 全部继承；不借详情窗口的删除伪造weather1删除 |
| [E05 app生命周期](ctk-app-close-e05-0041-20261023.md)；H05构造参数 | `a005cd80`的s4为主window；`a005cfda`传s4给weather1对象创建；主window DELETE是a00ab8ec；通用递归删除合同已有 | E05已明确实际正常root删除incoming尚未找到。条件递归合同不是实际teardown触发来源 | 把剩余缺口合并到此对象身份明确的旧断边，不新记一份根删除恢复 |
| ZIP成员 `tools/ap01/ap01-ui.h:259–290,403–406,682–715`；`ap01-ui-pages.h:673–724` | SIM根clean/延迟redraw、weather1重建显示已经留存 | `lv_obj_clean(g_ap01_ui_root)`是重建策略，不能替代ROM“滑出”或主window teardown证据 | 只读成员，不解包、不执行、不复制源码 |

同时按basename检查了page-logic-0041及page-logic-evidence/evidence2。前者 records[2] 为包含creator的旧证据 `ev_29c3e3a3ec43f12e0a1d9c5db26f6b39875288fb82b8c2126a9974ddfe734175`；后两份相关设置页/资源证据没有给出本type4的正常teardown调用。此为上述材料的定位结果，不是全ROM不存在证据的证明。最终SIM报告和matrix的passed-in-sim口径沿用H06已核限制，不另跑验收；旧remaining/pending不升格为现存缺口。

## 本轮复核或纠正

[recheck.py](../../analysis/weather1-navigation-h07-0041-20261023/recheck.py) 从唯一原件 `roms/0041/ap01-1.0.2_0041.bin`只读取必要窗口；映射 `VA-0x9ffff000`，沿用共同原件身份，不生成新哈希。Capstone仅解标准RV32/RVC；另用独立位域计算核JAL、分支、C.J、SW/SB，局部原字见 [navigation-recheck.json](../../analysis/weather1-navigation-h07-0041-20261023/navigation-recheck.json)。这些为旧结论复核，既不是新REA Evidence ID，也不计新增业务。

- `a00aff60/62`：active索引5的右向分支到 `a00affc8`，置 `a2=2,a1=7`，`a00affcc` 跳共享尾 `a00afd2a`；该尾以 `a0=s1` 调 `a00b3106`。
- `a00b0288/8a`：active索引5左向分支到 `a00b0354` 的旧Date准备片段；`a00b03be` 置 `a2=1`，`03c0` 汇入 `a00b0088` 的 `a1=4`，再到同一slider尾。准备片段内部沿用旧证据，没有本轮重新恢复。
- `a00b3192/94/98`：读原active `win+0x34`，写目标到 `+0x34`、原active到 `+0x38`。`a00b31c8` 写byte `win+0x4c=0`；ready中的 `a00ab638` 写同一byte为1。它们是原有切页/动画状态，不能解释为页面被释放。

这几处局部窗口无厂商opcode，没有用custom0/unaff/extraout或错误no-return补猜导航。未重复读取完整slider、主输入大函数、天气callback或删除核心。原来的完整滑动/动画调用语义来自上述旧合同，62 B抽样本身不证明所有callee没有额外副作用。

本轮没有推翻H05/H06局部生命周期结论；只收紧“正常离页”的提问方式：**普通主浏览切出与对象销毁是不同状态转换。** 已知主环通过坐标滑动保留对象，并未提供送达本type4的0x29事件链。不能要求每次旋钮切出都拼出一条DELETE链，也不能据此推定本页永不销毁。

## 本轮真正新增

**新增业务恢复0；新认证开源排除0；新导航/删除闭包0。** 本轮产出是旧导航证据与H05/H06对象身份的复用对照、12项局部原编码复核，以及将剩余问题准确收缩到已有主window teardown断边。它不是第二次天气恢复，也不是第二份E05根删除发现。a019cbc0与a0198946仍分开；type4与type19的ctx释放结论仍分开。

## 仍未闭合的精确边

现有条件链可继承为：若真实主window W进入 `a00ded6c(W)` 公共删除，则通用删除核心按既有合同递归其子对象；type4子页P已安装的DELETE可以在其被正常删除时进入 `a00abb62`，执行H05/H06已核ctx/wrapper清理。但**哪个正常上层操作/teardown调用真正把同一个主W或P传入公共删除、以及该调用的实参与对象身份**仍无本题可引用的闭合证据。只证明P是W之子或handler已安装，不足以填此边。

普通左右旋钮切出本题范围已覆盖；type19详情确认键删除的是另一个临时W。没有把这些动作、SIM根clean、构造失败class walker或E05条件root删除连成实际weather1 DELETE。剩余工作应与E05同一正常主窗口teardown问题统一派发；本轮不转追其他订阅者、全ROM free或全UI删除incoming。

## 实际验证与边界

运行 `python -B reverse/analysis/weather1-navigation-h07-0041-20261023/recheck.py`：**passed，9个短窗、62 B、24条连续指令、12项编码检查**。有一次临时屏幕查看误从slider指令中间 `a00b3160` 起解，结果0条，未据此判函数无代码；正式窗口只从旧完整汇编已知边界取值，全部连续解码。JSON可解析，报告本地链接与diff检查通过。未启动SIM、构建、历史回放、设备、外网或目标执行；未改ROM、配置、生产代码和分析器模型，未打开共享可写REA会话，未创建下级agent。

恢复程度：普通主浏览切出继承已有覆盖；实际正常teardown→type4 DELETE仍是明确断边。本题到此收缩结束，交管理者决定是否将该共享断边作为后续任务，不能把本报告当作天气生命周期完整闭合。
