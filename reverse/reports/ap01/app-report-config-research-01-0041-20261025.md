# Q-25 / S-P33：v3 property report-config 请求到结果适配

作者 app_report_config_research_01；静态作者交付，待非作者复核。只恢复有效请求已交接后的四个 callback（786B），并接合既有两 root；不能据此标记真实配置施加或整个接口闭合。

## 身份、范围及继承

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；file offset = VA − 0x9ffff000。本轮只以 Capstone 5.0.7 RV32/RVC 逐原字解码，无目标运行、模型/SIM/QEMU/回放/构建/设备/外网，也未更改共享 REA、ROM、生产代码或分析器。四窗全部可解，无未知 word；原字仍逐条保存，未知语义不补造。

主仓最新 reverse-design §3.1/3.2/5.1/7 和 rolling-management-0041-20261023 顶部/Q-25 为派发规则。独占 worktree `D:/CodexHome/visualizations/2026/10/24/01a16ec4-7aa8-7b43-a0e8-609e1021781b/ap01-s/report-config01`，分支 `codex/app-report-config-research-01-20261025`，启动基线 `9100a552b6862e9a3f884182b9da4f45eeac68ee`。父窗已创建工作树；本轮重试创建收到同名分支已存在，随后确认该树基线和干净状态后使用；未重置其他工作树。

继承主仓 `evidence/rea-0041-20261017/evidence/upper-miio-b.md` 两根 §0xa00c0ec2 / §0xa00c1c88（EID `ev_14adfa074a1d9499eebc51b4935ce6904d0d69e74bc576ca5c3977b93ecfb211` / `ev_4c25cb0c4b403592189b2e7f9b2e452af7b437b262aee735a65463f933ff54a0`）。另存 upper-complete.evidence.json records[26]/[45]，EID `ev_12f73038adef84341e7cb66ecab11785ac4dded7585b16b6bb9cfccf4bc09875` / `ev_20f6138d97a4e7749550583a9cfe9af14eb270f104fb15e4219dfce699d89a33`，原 profile digest `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621` 原封留在导出，不混同其他 profile。

根已接受 optional DID / IID3；get 发 IID 三数，set 再发 min/max32 和 change raw slice；doc释放、串行 writer、0/−1 根返回均继承。get 根 local DID 未显式 append；本轮结果也未发现 DID/IID输出，不能从同 ctx 的其他命令字段补入。根成功装 ctx+6c：get a00c6198 / set a00c607e；ctx+70：get a00c0b82 / set a00c0b6e。

## 可独立实现的 ACK 适配阶段

callback 入参 a0=ctx、a1=可写 ACK 字符串。两者均 `tokenize(ACK, stack pointer[64])` 调 a0191d52。继承 upper-miio-b supplemental §a0191d52（EID `ev_a81349569cb931f335ad69d594b206a00853f48a9fbdb7b851eeea61695106cf`，upper-helpers-second-005.json，前述 profile）：至多64 token，原地改写/去转义、引号/对象/数组跨度处理，不是通用 JSON 验证。这里不重验 tokenizer，也不将已分词文本当未改写原始传输字节。

|阶段|原字观察及合同|
|---|---|
|get 门 a00c61d0..61f4|n<=0 直接返回−1，不调 reply。n>0 时 token0 经 a002dcae 长度 API、a005fdfa(ptr,len) 转换为32位 status。status!=0 或 n<=3，min/max/change 临时槽置0且省略配置输出。|
|get 配置 a00c61f8..622a|仅 status==0 且 n>3：token1/2 以长度和 a005fcba(ptr,len) 得32位 word，分别 min/max；token3 的指针直接保存在 s3，长度经 a002dcae 保存在 s5。n>4 的其余 token 不访问。没有区间/类型/配置合法性验证。|
|set 门 a00c60a2..60be|status 初始0。n>0 才转换 token0；n<=0 保持0继续写结果。token1及以后不访问。不能把 set 的门替换成 get 的 n<=0 失败门。|
|公共 envelope|ctx+3c 以 lw 取32位请求 ID；输出 buffer=ctx+74，capacity 由 unsigned ctx+78 决定：<=0x557原值，否则0x558，即 min(size,0x558)。ID不是从 ACK 中解析，也没有 ACK IID匹配。|
|JSON形状|有序 API 调用生成顶层 object，`id`，`result` 子object，`code`。get 的零状态且 n>3 再写 `minimum_report_interval`、`maximum_report_interval`、`reportable_change`；set 只写 code。非零 get status 仍为 result.code，不在本函数转 error。|
|完成|关闭 result/外层 object 后调 a00602e6(builder,0,0)。非0返回−1、不调 reply；0则构造 descriptor，调用 ctx+64 并原样返回该 reply 的 a0。没有把 reply 返回强制改成0。|

正常语义输出示意（writer 内部 JSON/数字格式为公开 API 断边，不重验）：

```text
get n>=4,status=0: {id: ctx.id, result:{code:0, minimum_report_interval:word32(token1), maximum_report_interval:word32(token2), reportable_change:RAW(token3,len)}}
get n=1..3,status=0 或 status!=0: {id:ctx.id,result:{code:status}}
set: {id:ctx.id,result:{code: n>0 ? word32(token0) : 0}}
```

status 使用 a005fdfa、code 写入 a01b35d0；min/max 使用 a005fcba、与 ID 相同的 a01b3574 写入。寄存器/槽宽都是32位，没有64位拼接。正常适配保留这些 API 的区别；无符号范围、非法数字、溢出及格式化策略委托转换/JSON API，不从函数名发明输入验证。`code`、min/max/change key的原件字符串地址分别 a056bd3c、a0565a9c、a0565ae4、a0565b2c；id=a01c3280，result=a06124b8，逐字节附在 static-windows.json。

get raw 写点 a00c62c6..62d6：a0=builder，a1=change key，a2=token3 pointer，a3=token3 length，调用 a01b6866。没有复制到持久字段，没有本层加引号或独立 free。借用至少覆盖同步 raw API 调用；API 是否内部复制属于其合同。本轮未声称 token3 原始 JSON 仍未被 tokenizer 处理。

## reply ABI、本层归还与 error 委托

get frame=0x170，builder=frame-end−0x164，D=frame-end−0x158；set frame=0x160，builder=frame-end−0x154，D=frame-end−0x148。builder是三个32位字：buffer、capacity、初始0。

|reply descriptor D 偏移|两函数相同的原字写入|
|---|---|
|+0|ctx+3c 的32位 ID|
|+4..+27|先 memset(D+4,0,0x24)，其中下列两槽再覆盖|
|+1c|a002de24(buffer,capacity) 返回的有界长度 word32|
|+20|ctx+74 输出缓冲区指针|

因此 D 的本层可见范围为40B，+4..+18 和+24保留零；未命名槽保留 offset/raw，不推断协议意义。get a00c6306..6328、set a00c6158..617a：`reply(D, *(ctx+68))`，函数指针取 ctx+64。descriptor 位于栈上，只在同步调用时有效；输出文本仍在 ctx scratch buffer。reply若异步保留 descriptor/text 必须复制或满足外层生命周期，实际持有行为本轮未知。

reply返回后只恢复寄存器/栈并返回；四窗没有写零 ctx+6c/+70，没有 free ACK、scratch buffer、ctx或堆对象，也没有另建 retained property list。token表、builder、descriptor的本层存储随栈归还；不能把未显式清理推为 ctx 全生命周期结论。

两个20B error wrapper各仅 prologue → a00bd7fa → epilogue/ret，调用前没有更改 a0..a3，返回保持 helper a0（a00c0b8a/a00c0b76）。本包仅恢复 API委托，Q22 shared helper 本体、归一化与输出细节不在本轮重判/认证。没有据尚待主窗整合的 Q22 技术复核提前标整个 report-config error 接口闭合。

## 证据、检查及停止边界

同 stem analysis 的 extract.py 为本轮复验源码，仅从显式主仓原件取四窗；static-windows.json 完整保留786B/每窗SHA/指令/raw/直接call绝对目标，另有六个常量字符串；inherited-roots.json 为原 profile 两根完整记录。Capstone 的 branch/c.j 显示相对位移，直接 jal目标另列绝对VA；阅读分支时按 pc+位移计算，不能把显示的位移当绝对地址。

本轮已核：原件全长/SHA、四窗口464+282+20+20=786B覆盖、逐原字解码覆盖无缺口、get/set gate与全部return、所有 direct call、六 key bytes、reply栈offset、scope/diff。未进行独立非作者验收。无新增真实配置施加证据；输出 code0只说明本层构造/交接，不等于设备接受配置、持久化、报告调度、权限或并发正确。断边为 tokenizer/数字转换/JSON builder/finalizer公共API、Q22 shared error API、reply持有/真实后台效果。无额外业务种子扩展。

UTC起点 2026-10-24 17:49:21；技术结束、提交及停止时间见同 stem session.json 和父窗交付。技术与提交分列；工具正常读取包含技术墙钟，不提供虚构有效工时。token用量不可得，不估造。
