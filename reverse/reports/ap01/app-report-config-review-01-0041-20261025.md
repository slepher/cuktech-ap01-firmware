# Q25 report-config 非作者复核

复核者 app_report_config_review_01；作者提交 `1890c41d135ed66bf282d601645096c3e7d09a41`。结论：四 callback 的六组合同限定接受，行为纠正0、新增业务字节0；只闭合已交接请求的 ACK→结果适配阶段，真实配置应用及整个接口未闭。

## 身份与复核方法

启动基线 `7e4f4dca88af733319500704ddfeb2046ec2006b`，分支 `codex/app-report-config-review-01-20261025`，独占 report-config-review01 工作树。先读主仓 reverse-design §3.1/3.2/5.1/7、管理顶部/Q25补位行与预调研 S-P37；不改管理表或其他协作者文件。

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−0x9ffff000。独立脚本直接读 ROM，Capstone RV32/RVC 解码；没有执行作者 extract.py、目标、模型、SIM/QEMU、回放、构建、设备或网络。未更改ROM、生产配置、分析器或共享REA。

独立重读四窗：0xa00c6198..0xa00c6367 464B、0xa00c607e..0xa00c6197 282B、0xa00c0b82..0xa00c0b95 20B、0xa00c0b6e..0xa00c0b81 20B，共786B，逐窗原字/SHA与作者 static-windows.json一致，解码无缺口。六个字段key另核ROM零结尾原字，不计业务新量。作者 report/config analysis 读取自 report-config01 同相对路径；主窗转存后的主仓同路径为长期引用。

仅核 inherited-roots.json 两根 records[26]/[45]必要身份和安装，逐结构与主仓 upper-complete.evidence.json对应记录相等。profile digest `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；EIDs `ev_12f73038adef84341e7cb66ecab11785ac4dded7585b16b6bb9cfccf4bc09875`、`ev_20f6138d97a4e7749550583a9cfe9af14eb270f104fb15e4219dfce699d89a33`。get根0xa00c10d8..10ea安装ctx+6c=0xa00c6198/+70=0xa00c0b82；set根0xa00c1fba..1fcc安装0xa00c607e/0xa00c0b6e。根输入/序列化既有合同继承，不重做请求研究；不同profile不混证据。

## 六组接受结果

|组|独立原字复核结果|
|---|---|
|1 get门/字段|0xa00c61d4 n<=0到6364置−1并返回，无reply；token0转换得到32位status。61ee/61f4只有status==0且n>3到61f8；否则635a清临时槽后继续envelope。token1/2经a005fcba得word32，token3取指针和长度；不访问后续token，无本层配置范围/类型验证。|
|2 set门/差异|60a6默认status=0；60a8 n<=0直接60c0继续构造结果，n>0才解析token0。只输出code，不输出三个配置字段，不能套get空token失败门。|
|3 envelope/宽度|ctx+3c以lw/c.lw加载ID，未从ACK取IID或匹配IID；ctx+74 buffer、ctx+78 unsigned容量，小于等于0x557保留，否则0x558。JSON调用序列为外object/id/result子object/code；get满足门再附min/max/change；所有本层数值槽32位，code与min/max使用不同转换/写API。|
|4 raw借用|62c6..62d6以a2=token3指针、a3=长度调用a01b6866；无持久复制、加引号或本层free。借用至少覆盖同步raw调用；tokenizer可能改写输入，不能声称未改写传输原字。公共tokenizer、数字转换、JSON内部均止API。|
|5 finalize/reply/归还|62da..62f2和612c..6144先关闭JSON再finalize(builder,0,0)，非0返回−1不reply；成功才memset(D+4,0,0x24)、填D+0=ID、+1c=有界长度、+20=buffer。两D可见40B、未命名槽保持零。get D=frame-end−0x158，set=−0x148。ctx+64调用reply(D,ctx+68)，之后仅恢复寄存器/栈，原样返回reply a0。未清ctx+6c/+70，未free ACK/buffer/ctx。|
|6 error|0xa00c0b8a/0xa00c0b76直接调用0xa00bd7fa，调用前未改a0..a3，之后只恢复帧，返回helper a0。仅确认两个20B wrapper委托，未重读/重复裁决Q22共享body。|

原字中的相对分支按PC+位移解读，get status跳635a，空token跳6364；解码器显示位移不当绝对地址。必要返回路径与全部本层stores已检查，无未知word需补造。六key为id/result/code/minimum_report_interval/maximum_report_interval/reportable_change，原字比较通过。

## 断边、产物与计时

限定接受作者 ACK适配合同，不把code0等同设备接受、持久化、真实report调度、权限或并发正确。tokenizer/formatter/数字转换/JSON为公共API停止边；error共享0xa00bd7fa沿Q22合同。栈descriptor仅本次同步调用有效；reply是否持有descriptor或ctx文本、完整ctx寿命/并发取消/后台施加均未知。无新扩围种子。

同stem analysis：review.py为独立静态复验源码；independent-windows.json保留独立raw/SHA/全部指令；checks.json保留六key和两root身份比较；session.json记录计时。JSON导出依忽略规则留待父窗转存，未强制入库。检查包括ROM身份、四窗全覆盖/原字相等、六key、两root精确记录和安装、六组语义、git diff格式/范围；未运行项目构建或行为测试。

UTC首工具开始2026-10-24 17:58:51；技术核对结束18:00:21（90秒，含正常工具等待，无外部依赖等待或故意等待）；文档/提交/停止另列交付与session，不将技术时间称完整工时。token/cached input用量不可得，不估造。
