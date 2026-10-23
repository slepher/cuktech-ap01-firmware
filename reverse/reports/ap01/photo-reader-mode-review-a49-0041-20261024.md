# A49：非零 reader mode 构造及归还独立技术复核

2026-10-24；基线 `df35f44`；独立树/分支 `re0041-a49` / `codex/re-0041-a49`。**限定接受 A47 分类1→mode1 W→既有 O 状态复制，以及 `a01b2e3a(O)` 的 callback(D,H)、条件缓存归还、前三 word 清零合同；无语义纠正，新增功能0。** 不能直接命名为标准 `fclose`；具体 D、open/close 回调实现及默认五照片实际 mode1 未证。采用 reverse-engineer-anything skill，复用证据并只读主仓 ROM，没有打开、共享或切换 REA target/database。

## 继承结论：已有出处→行为→局限→精确缺口

|已有出处|行为与本轮使用|局限与复核缺口|
|---|---|---|
|[A47](photo-reader-mode-a47-0041-20261024.md)及其[evidence.json](../../analysis/photo-reader-mode-a47-0041-20261024/evidence.json)|类型1 source 接入 mode1 工作区；driver reader 初始化及资源归还|独立核 mode 的 byte 宽度、W/O 对应、D/H实参、分支与清理原序，不重导函数|
|[A37](photo-decoder-owner-a37-0041-20261024.md)、[A39](photo-decoder-review-a39-0041-20261024.md)|constructor `a010a65a(W)` 正常分配 O，copy(O,W,0x664)，返回 O，owner+5c 持有，+74持内部派生区|可靠合同继承；本轮将 mode1 W 接到同一 constructor，并补 mode1 wrapper 返回锚点。复制当时状态，不保证入口 H/C 永远不变|
|[A41](photo-decoder-destroy-a41-0041-20261024.md)、[A42](photo-destroy-review-a42-0041-20261024.md)|旧O非空时先旧source失效；O+10整byte非零才以 O 调 a01b2e3a，随后 free(O)，清 owner+5c/+74|外层顺序与 mode0 全继承；A47补的内部合同不升级为页面最终 DELETE 已闭|
|A33/A35及上述报告引用旧 photo round3、system complete、最终ZIP/SIM|正常五ROM资源的 descriptor+10→data、mode0输入借用及照片业务已有|不以替代实现/照片业务证明 ROM mode1，不重复资源/PNG/全源码导出|
|A47 引用 page-logic `#/records/15`、whole-ROM 索引及 weather-calendar-complete `#/evidence/30`|清零 helper caller、函数范围/直接调用定位及旧 reader 的非零分流已有|caller/范围不等于内部行为；旧 stdout有截断。沿用 A47 有界复用记录，不将局部未命中说成历史从未恢复|

沿用 `a01b2e3a` extent Evidence `ev_ec1bdb465c5285588d9902692167d9cad1269b7a6dffaf198bf0a9682018058e`、direct-call Evidence `ev_d78eb655cefbb3b29310d1ac98b8d3519ba63de4f3bff158f7a0a334d6818af0`；本轮没有虚构新 REA ID。填充 `a0024906`、copy `a000589c`、归还封装 `a008ab8a` 沿用既有合同，不扩底层 heap。ROM 映射继承 `offset=VA-0x9ffff000`。

## 本轮复核或纠正：逐项接受/未核

|A47结论|判定|原指令/对象依据与范围|
|---|---|---|
|分类1以同一 source 进入构造|接受|ed876 的 C.LI a5,1；ed878 的 BNE a0,a5 精确到 ed842；相等路径 ed87c 把保存 source=s3 给a0，ed87e JAL a0107d8e。类别标签不证明实际五照片命中|
|mode1 W 初始化、实参与返回门|接受|7da2 保存 source=s1；7da4/7da6 给 zero/0x664，7daa 形成 W=s0−0x674并调用填充；7dba/7dbe 的 SW分别清 W+14/+c；7dc2为 **SB** W+10=1。7db4 给 a1=source，7db6 给 a0=W，7dc6 调 a019d6a4；7dca 非零到7de6返回0，零时7dcc/7dd0调用同 constructor。初始化结果不是H|
|W成功复制到O并返回持有|接受，复制内部继承|A37/A39已核 copy(O,W,0x664)，包括当时前三word/mode；本轮补7dd4..7de4的返回尾声，仅恢复保存寄存器/sp并返回，不覆写constructor返回a0。不是保存栈W地址；后续owner持有门沿A39继承|
|D/H/C字段与普通open ABI|接受，具体driver未核|d798 SW W+4=D；d80e取 D+c，d810置a2=2，d812给a0=D，d818间接调用，d828把正常接受的H写W+0，再回d7a8读取配置。source后缀规则沿A47；可选ready回调前d75c保存a1、d762恢复同a1，补核其跨调用持有，不展开注册链的厂商步进。特殊配置−1自指分支不当作普通回调H|
|配置非零的缓存结构|接受|d7a8/d7ac配置零返回；非零d7ae给16，d7b4实际目标 **a008e362**，d7bc将结果写W+8。该缓存分配与constructor的O分配a008aea0为不同边；A47未将两者混同。本轮不扩缓存填充或全部失败臂|
|归还回调为callback(D,H)|接受|2e44保存O=s1；2e46取 a0=word(O+4)=D，2e4a取 fn=word(D+10)，2e4e给a1=word(O)=H，2e50 C.JALR a5。D为空或fn为空分别跳2e84；不是callback(O)、free(source)或free(H)。返回值没有用于后继门|
|回调后重读与条件缓存归还|接受|2e52重读O+4，2e54读D+4；配置0或C=word(O+8)为空均到2e78。配置−1经2e5e跳2e6e，仅归还C；其他非零配置先条件归还C+c，再2e6e重读O+8归还C。2e66/2e70实际目标均a008ab8a；不能缓存回调前的D/config/C代替原重读|
|前三word清零及外层free(O)|接受，条件明确|2e78/7c/80分别 **SW zero** 到O+0/+4/+8，均32位；mode byte未在callee清零。清槽块只在D与回调均存在且回调已调用的路径执行，入口两个空门跳过；2e84..8c为尾声。随后外层free(O)、清owner+5c/+74沿A41/A42；内部C/其+c与O是不同分配根，D没有作为free实参|
|实际D/回调、mode1执行及库身份|未核|诊断串支持文件接口型driver解释，不认证标准FILE*、底层文件系统、准确版本或运行成功；默认五ROM照片仍沿mode0合同，不声称其实际走mode1|

没有语义纠正。必要对象关系与顺序如下，为分析视图而非原源码或完整结构体：W前缀的H/D/C位于+0/+4/+8，mode为+10的byte；constructor在正常成功路径复制当时W状态到O。正常替换非零mode时，callee先检查D及其+10回调，再调用 `(D,H)`，重读D/config，条件归还缓存，最后清O前三word；外层另归还O。不把内部清槽条件改成无条件，也不把同名路径串解释为未改源码认证。

## 真正新增

新增功能、算法、资源与来源认证均为 **0**。仅有独立接受记录及42B旧结论复核锚点：mode1 wrapper返回尾声/初始化失败零返回22B、可选ready回调前后a1保存恢复10B、归还函数尾声10B；未重导整函数。a1保存恢复检查只认证现有普通路径参数持有，不认证具体D选择算法或回调实现。

[review.py](../../analysis/photo-reader-mode-review-a49-0041-20261024/review.py) 只用Python标准库读取主仓ROM，对A47的 **83条** 留存raw逐条比对，并独立拆I/S/B/J、压缩访存/移动/立即数/零分支和AUIPC/JALR，共 **148项 PASS**。[review-result.json](../../analysis/photo-reader-mode-review-a49-0041-20261024/review-result.json) 保存检查索引及42B增补。未运行A47写文件脚本、未导入其解码器、未改模型；普通成功合同未依赖未认证厂商指令。JSON、报告本地链接及提交差异检查通过。无固件执行、SIM、构建、回放、设备、外网，未改生产ROM/代码/配置。

## 未闭精确边与后继筛选

- **事实**：分类门、byte mode、普通分支的寄存器实参/槽偏移、回调后重读、缓存归还和清槽条件/原序。**解释**：driver reader及缓存资源用途结合诊断串和字段操作；不是标准fclose或源码版本认证。
- **未核，继承**：真实source类型1实例所选D、D+c/+10实际目标、H具体类型与真实关闭成功、缓存+c首次分配/填充、全部失败臂、最终页面DELETE和底层heap复用。默认五照片实际mode1无证据，不扩全文件系统或所有driver。
- **后继有真实种子**：旧主仓 `reverse/rehost/weather-calendar-complete-0041.json#/evidence/30` 原stdout明确在a010a5e2读取mode byte、a010a5e6为零跳内存分支，非零时a010a5e8置a3=0、a010a5ea调用 **a008b888**。可只追同reader前缀到该目标的ABI、D读取/reader回调槽及缓存持有连接；具体D仍无实例种子，不能假定默认照片。

后继重叠筛选已做且范围有界：当前 `reverse/reports/ap01/*.md` 对a008b888仅A47提旧分流；主仓 `reverse/rehost/*.json` 精确文本检索仅weather complete两次。whole-ROM round1已有a008b888 extent `ev_0cf7b05aecf9153467edba3b567024c23acd5f53b2e1392c883286c7ca4197e6`（544B），historical_contracts/dossiers为空。这只说明这些已检边界；后继仍须先读旧complete相邻记录，不能据索引空项宣称内部从未恢复。本轮未展开a008b888，不自行承接。
