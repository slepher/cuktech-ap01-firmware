# I06：配置读取与初始化缓存合同独立复核

限定接受I05的机器合同：`a005a736` 内联片段调用 `a0060946("ck_config","wifi_configured",62fc919c,1)`，返回值精确等于1才走成功读取/日志臂，其余返回经原日志后SB清缓存整byte为0；两臂继续ad2c。成功臂没有直接把cache设1或作bit0归一化。a005acf0/ad28分别是传参/存储点，不是独立setter，此片段不调用持久写入接口。

语义纠正0，新增功能0。有一处统计精度纠正：I05的“18条旧原指令”应为18个旧raw条目，其中17条完整指令、最后1项为2B截断前缀；本轮仅补原件其后2B确认LUI边界，不改变上述合同。

基线 `14e7291a7ff4542d84f88c9a7286b4af06852f16`，独立树/分支 `re0041-i06` / `codex/re-0041-i06`，未参与I05生产。使用 reverse-engineer-anything 技能，只读主仓ROM、旧证据及I05/I01/I02报告；无共享REA target/数据库、固件/模型/SIM/构建/回放执行、设备/外网或下级agent。仅写本报告与独占analysis，不改共享/主树/生产ROM配置模型，不撤销他人改动。伪代码非原源码，不认证完整配置后端、硬件或网络状态。

## 继承结论：已有 → 行为 → 局限 → 精确缺口

|已有出处|已有行为与局限|本轮处理|
|---|---|---|
|[I05](wifi-config-cache-i05-0041-20261024.md)及verification.json|旧初始化的read参数/rc门/缓存宽度与I01关系已解释；主体已有，新功能0|仅独立核实内联callsite与证据强度，不运行I05采集器，不重导9448B初始化器|
|主仓 `evidence/wifi-psm-bounded-disassembly-20261021.json#/ranges/7`|64B旧原字节覆盖acd0..ad0f，末尾以.byte保留3737前缀；配置传参与比较主体已在|旧18条目逐byte比原件，统计按完整边界收紧，不将部分前缀算完整指令|
|主仓round3 initial `#/records/5`，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`|a005a736完整伪码/汇编及PARAM acf0、WRITE ad28、READ b7fa已有|继承其函数/引用定位，不把参数reference误作setter，也不重新复制大容器|
|[I01](boot-ready-increment-i01-0041-20261024.md)、[I02](boot-ready-review-i02-0041-20261024.md)|getter同键同地址1B、精确rc1、失败清0/LBU整byte返回及bypass非零跳过读已恢复并独立接受|直接继承getter/启动消费；本轮只确认初始化使用相同静态cache，不能升级cache为真实ready|
|I05所列PSM静态/flags、photo-round3旧writer|a0060946读家族与a0061848写家族、其他callback的0/1字节/持久写合同已有|不重新追writer、网络事件、NVS/文件/加密后端；不能用这些旧0/1写入规则担保初始化读入值必为bool|
|I05对system/guide/settings/page-logic及其他complete/SIM的复用边界|旧业务/替代服务不证明本callsite运行或硬件/network-ready；既有查询命中不等于新功能|继承有界复用结果，不再全ROM/所有JSON writer扫描或最终ZIP重复解包|

本轮精确缺口只是旧参数、byte宽度与两臂合流的独立技术接受。原字节合同、定位性refs、SIM替代和本轮稀疏核验分开记，不重复恢复已有PSM/启动主体。

## 本轮复核或纠正：逐项裁决

ROM只读路径为主仓 `roms/0041/ap01-1.0.2_0041.bin`，映射VA−9ffff000；核验索引见 [review-result.json](../../analysis/wifi-config-cache-review-i06-0041-20261024/review-result.json)。

|I05主张|独立原字段/目标依据|判定/限定|
|---|---|---|
|静态cache地址|acc8 `3796fc62`构造a2=62fc9000；acea保存s11=a2+19c；acf0给a2=a2+19c；其间旧指令无改写a2的调用|接受两寄存器同指62fc919c；acf0传输出指针，不是实际SB writer|
|namespace/key/长度|acda/acde构造a01c3000，acf4给a1+58，acf8给a0+68；ROM字符串分别wifi_configured/ck_config；acee C.LI a3=1；acfc JAL独立解出a0060946|接受 `(namespace,key,output_ptr,1)` 的1B输出范围，不把接口rc或指针当configured值|
|精确返回门|ad00 C.LI a5=1；ad0a BEQ字段rs1=a0/rs2=a5、目标b7fa|接受只有a0==1成功，不改非零/正值门|
|失败臂原序|ad24 JAL独立解出a008b51a；随后ad28 `23800d00` 是SB zero,0(s11)，顺序落至ad2c|接受caller清byte0，继续初始化；没有本site持久写回0或提前返回|
|成功臂原序|b7fa `83c70d00` 是LBU a5,0(s11)；b814调用日志a008b51a；b818 `6ff04fd1` 是rd=zero的JAL到ad2c|接受整U8读取并保留配置读入值的caller行为；没有直接写1、`&1`或bool归一化。日志及底层全局副作用不在此认证|
|同I01/I02 getter关系|既有getter以同字符串地址、同62fc919c、同长度1、同rc1门读取，LBU返回；bypass非零直接返回cache|接受继承的同键同址静态连接；不推断首次调用时刻、锁、跨调用串行化或所有writer|
|内联身份/持久方向|旧round3 procedure为a005a736；本块实际call只有配置read和日志，持久write入口a0061848属于旧其他writer|接受，acf0/ad28不可命名独立setter；不把RAM cache更新说成此块持久配置写入|
|资源责任|键串为ROM借用，输出为静态global byte；局部没有新heap申请、释放或指针所有权转移|接受本callsite范围；不推下层文件句柄/临时buffer/并发责任|

旧成功分支原汇编与I05描述一致：LBU后仅构造日志实参并调用日志，再回ad2c；“成功保持”指caller不另改该byte，不是保证未知callee绝无全局副作用。接口返回1与实际cache数值相互独立。

必要正常伪代码（不是原源码或新函数）：`rc=read("ck_config","wifi_configured",&cache_u8,1); if (rc==1) log_success(cache_u8); else { log_failure(); cache_u8=0; } /* continue ad2c */`。这里没有write持久接口，不将cache byte等同无线关联/IP/云绑定/硬件ready。

### 统计边界的精度纠正

旧range7最后一项为 `a005ad0e:3737`，原记录明确mnemonic=`.byte`，2B范围尚不足一条4B指令。I05按18条目逐byte比较是有效检查，但称“18条旧原指令”会夸大完整指令数。原件补其后 `a005ad10..ad11:1ca0`，完整字为 `37371ca0`，即LUI a4,a01c3；这只是失败日志实参构造的第一条。裁定：18个旧raw条目=17完整指令+1个2B前缀。新增2B边界核对为旧结论复核，不算功能或新ISA规则，不需要重导初始化器/失败业务。

## 真正新增

新增功能0、ISA规则0、完整函数导出0、来源认证/整库排除0。42项旧raw/实参/目标/字符串/稀疏检查、2B边界补全及一处计数措辞收紧都是独立复核；机器行为无纠正。初始化、getter、PSM及photo旧writer主体直接继承，未扩事件writer/网络/NVS。

## 未闭精确边、后继与验证

仍未知：实际初始化执行时刻、全部cache/bypass writer及政策、其他业务何时持久写入、配置后端完整I/O/锁/失败行为、实际联网或硬件状态。旧callback的0/1写入合同不被当作新缺口重开，也不据此认定所有读入byte均规范化。

单一后继闭包：只有出现62fc3fec的真实设置地址/调用种子时，再核bypass政策；当前范围无该种子，按已覆盖收缩，不扫全部writer、不扩初始化/网络/NVS。本轮不自行接题。

[review.py](../../analysis/wifi-config-cache-review-i06-0041-20261024/review.py)通过：18个旧raw条目与原件一致，I05的4个稀疏锚点一致；独立解码read/日志/合流JAL、rc BEQ、I/S/U/压缩实参字段、ROM键串及完整边界，共42项。没有执行旧验证器、目标、规则或输入回放。报告本地链接、JSON及 `git diff --cached --check`通过。结论仅独立接受I05内联配置缓存合同并收紧统计表述，未认证整个配置/网络系统。
