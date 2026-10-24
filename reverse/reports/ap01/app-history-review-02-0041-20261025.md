# Q-03 非作者复核：历史详情关闭对象与同 P 候选

**可独立使用阶段已闭合但接口未闭；限定接受。** 非作者 `app_history_review_02` 接受 research-02 新增 class、original target、GUI helper 差集及失败 callee 精度提示。P 最终归还仍未闭。新增业务0；纠正旧 P19 顶层失败措辞1项，research-02 无需行为修改。

基线 `5bbc331ab429fb76e956e50b8081c56f8d278b11`，唯一认领为 [管理表 Q-03 当前行](rolling-management-0041-20261023.md)。按父窗授权仅写本报告及同名 analysis，主树独占输出、不建 worktree。读 [reverse-design](reverse-design.md) 3.1/3.2/5.1/7及 [REA skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)，采用留存优先、必要原字与事实/推断/未知分账。未打开共享 REA、执行目标/模型/SIM/构建/刷机/网络、改 ROM/生产/配置/分析器、派下级或提交推送/reset/clean。

## 继承结论

直接继承 [P19 非作者复核](app-history-review-01-0041-20261024.md)、PR12、E06、H04 已验 creator、ring、公共删除、class walker/base dtor；不重验。W=s2、R=s7、P=s1，P 为独立零化0x6c分配，R.id=0x13、R.payload=P、W+0x10=R。Return 使用 Wlast，只有正常最后子对象布局才衔接此详情 DELETE；不扩成任意排列结论。

原件身份继承 CATALOG/P19：`roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，RV32 LE，`offset=VA-0x9ffff000`。本次核长度和必要原字，不重复hash。旧 `charge-0041-round4.json#/records/2` Evidence `ev_e30acc99f01e5e79a06965e472ec0c1aee39a56a7c3e8ae8ad7fdef09673d74e` 与 `charge-complete-0041.json#/creator_continuations/2` 的 Capstone5.0.7续体来源沿用。旧 profile 缺失及 custom/no-return 局限保留，不附现代profile。

## 本轮复核或纠正

| 差集 | 独立判定与证据 |
| --- | --- |
| W factory及class | 接受。ROM `0xa01afda6:ef9002c2` 独立J位域到 `0xa00d91c6`；`afdac:2a89` 保存W。`d91d2:374526a0`/`d91d6:130545ef` 独立LUI/I位域构造 `0xa0263ef4`，`d91da:efe04fcd` 到 `0xa00d76ae`。class原16B=`00000000c4540da0d0870da07ab00da0`，base=0、dtor=`0xa00d87d0`。不得套主window timer/G析构身份。 |
| DELETE对象 | 接受。`0xa00f1bac:83294500` 独立I位域为 `lw s3,4(a0)`，因此W取E+4 original target，非E+0 current target；事件字段语义沿E06/H04。`1bb0:03a90901` 取R=W+10；`1bb8:83244900` 取P=R+4。 |
| DELETE原序及所有权 | 接受。`1bbc:a84c` 独立C.LW位域先取P+58 timer；若干GUI字段清零后 `1bea→a008ae58`；`1bee:4a85` 令a0=R，继续清P字段，`1c10→a008ab8a(R)`，`1c14` 清W+10。完整callback原字只有这两处直接调用；无free(P)，P+58、P+60亦无store。清引用不等于delete控件。 |
| 同P外观helper | 接受有界收缩。`060c:2685` 传s1=P到a0，`060e:ef4054ab` 独立J位域到 `a00f50c2`。完整两支 `50c2..51f3` 保存P到s1，以a1零/非零分支；13处直接调用的a0均从P的0/10/14/18/1c/20字段取得，GUI callee边界沿既有合同。所有普通store目标为栈帧，compressed store也只栈保存；没有把P传下游或持久存出。两支在515c合流并返回，不形成新的同P归还/移交种子。未深入库内、不证明所有别名穷尽。 |
| 顶层失败精度 | **接受research-02提示，并纠正旧P19表措辞。** ROM `afdbe:ef7092a4` 独立J位域到 `a00d7806`，前置 `afdbc:4a85` 传W。E06/H04已验其是class walker，自身不摘数组或free(obj)。旧P19“R零删除W/P零删除W”只能解释为该walker调用，不能作为完整公共删除成功或W已free的证据。本轮未重验失败链其余分支；不扩大失败清理恢复。 |

以上对照 [作者报告](app-history-research-02-0041-20261024.md) 与其 `static-evidence.json`，该JSON仅作原字待核载体，没有导入/执行作者验证器。[独立源码](../../analysis/app-history-review-02-0041-20261025/verify_independent.py) 只用Python标准库读取ROM，核174条边界/字节、6个关键JAL、LUI/I位域、E/R/P load、timer C.LW、helper栈store/字段load，结果见 [independent-checks.json](../../analysis/app-history-review-02-0041-20261025/independent-checks.json)。机械核查数不计恢复量。公共析构不复跑，作者69处旧载体对照不冒称本轮独立重做。

## 真正新增

新增业务0。新增独立证据是已登记差集的原字核验，以及 `afdbe` 调用目标的独立位域确认。失败措辞纠正已经通知父窗，供其保留旧历史并增加限定；research-02已准确限定，无需作者回改。

重建可采用的静态合同仍是：正常Return恢复列表后删除Wlast；详情DELETE按E.original_target取得W→R→P，先捕获timer、按原序清GUI引用并删timer，再free(R)、清W+10。W公共删除沿条件合同处理GUI对象；它不能代填独立P的归还。此为分析合同，非原源码，也非运行观察。

## 未闭精确边与交付

`alloc_zero(0x6c)→P→R+4` 到以**同一个P**为实参的归还或明确所有权移交仍无定位。已知W→R→P挂接在free(R)/清W+10时断开；不据此判P常驻、泄漏或无别名。helper两支未增加真实归还种子，因此不建议无种子全ROM free/P reader搜索。未来只有其他已登记证据提供保存同P或归还实参的具体地址时，再按连接查重登记。任意子对象排列、间接关闭/resume、代际一致性等继承未知不关闭。

预计3–5分钟（定位<1、原字/对象1–2、交付1–2），材料充分定位后提前收敛。首个可得UTC时间记录 `2026-10-24 16:01:10 UTC`（此前读取启动未单独取时）；最终准确UTC及从首个可得时间起的墙钟见 delivery-checks.json。无主动等待、排队或中断；正常工具时间计入墙钟，有效工时未独立测量。token由父窗统一实际统计，cached单列；本子窗不可用，不估算。交付后停止。
