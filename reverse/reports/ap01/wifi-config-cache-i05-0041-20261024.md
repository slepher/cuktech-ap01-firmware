# I05：wifi_configured初始化读取与缓存接线

2026-10-24；基线 `10bc8b8`；独占树/分支 `re0041-i05` / `codex/re-0041-i05`。**主体已有覆盖，新增ROM功能0：a005acf0/a005ad28是a005a736内的传参/存储点，不是独立setter入口。该正常片段以a0060946读取 `ck_config/wifi_configured` 的1B到62fc919c；rc精确等于1时保留读入byte，其余返回在原日志后SB清0，再继续初始化。** 此处没有配置持久写入；它与I01 getter使用同键、同缓存及同rc==1门，不能称硬件ready或真实联网状态。

采用reverse-engineer-anything skill，只读主仓ROM与旧证据，不打开、共享或切换REA target/database。未执行固件、SIM、构建、模型、历史回放、设备、网络或外部服务；不创建下级agent，不改共享/主树、生产ROM、配置或模型。伪代码是旧机器合同的分析表达，不是原源码。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|已有行为与证据范围|本轮处理/缺口|
|---|---|---|
|[I01](boot-ready-increment-i01-0041-20261024.md)及其evidence.json|a009d7b4 getter的配置读ABI、非零bypass、rc==1门、失败清0及LBU返回已恢复；启动timer/完成动作主体早有|直接继承，不重跑getter/boot；本轮只接同地址初始化写入种子。独立复核由I02负责，不在此冒称其验收|
|主仓 `evidence/rea-0041-20261017/round3/evidence/whole-rom-round3-initial.evidence.json#/records/5`，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`|a005a736已有完整伪代码与汇编，明确read(...,&62fc919c,1)、rc==1日志、否则清0；PARAM/WRITE/READ分别定位acf0/ad28/b7fa|不因I01只引用references就把整片段认作全新功能；只补必要宽度、调用/分支及旧原字衔接，不重导9448B初始化器|
|主仓 `evidence/wifi-psm-bounded-disassembly-20261021.json#/ranges/7`|a005acd0..ad10的64B、18条旧原指令已保存，包含地址/键参数、长度1、配置调用、rc==1分支|旧byte逐条回源；仅补base LUI、失败SB、成功LBU/合流跳转16B，不另导整函数|
|主仓 `evidence/wifi-psm-static-20261021.evidence.json#/records/1`，batch Evidence `ev_6bccd23aa8e981b3cf815d9fc4f5e93202743fdf72948134929a9f956352b528`|a0060946与a0061848读/写家族已有静态记录；[Wi-Fi旧合同](knowledge/0041-sim-wifi-selection-gaps.md)已区分PSM格式与真实联网|接口家族与限界继承，旧反编译个别下层实参省略不能代替本callsite ABI。本轮不展开文件/加密后端、身份、网络配网或服务|
|主仓 `photo-evidence-round3.json#/rea_records/8`，Evidence `ev_29c85d896166eddfae866b5f53db4b21668d45d5e08f3d199d7cc8d948c8bd4c`；`wifi-psm-flags-20261021.evidence.json#/contract/wifi_configured`|另有网络状态callback的字节0/1与a0061848持久写入旧合同，setter记录已有|只作重叠盘点/继承边界，不扩这些事件writer，也不把其字面0/1规则搬成初始化读取值必为bool的保证|
|system/guide complete、settings/page-logic、近期MiIO/config及Wi-Fi/SIM报告|system旧getter和guide boot主体已解释；MiIO deferred设置/亮度位置等使用同配置接口但不是本键；SIM/列表/实机历史有各自边界|不把替代模型、列表部署或设备样本当此ROM调用的运行事实，不重复初始化、全配置或网络业务|

旧材料只读根为 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`。主仓顶层rehost JSON按acf0/ad28/919c/wifi_configured有界筛选命中asset-index、photo round3及system complete；page-logic/settings/guide未命中这些精确词不表示所有历史都未分析。本轮不重做最终ZIP/SIM或全ROMwriter搜索，主体由更早PSM原字与较晚round3直接覆盖。

## 本轮复核或纠正：正常缓存更新合同

|核查项|原指令/ABI与顺序|处置与限制|
|---|---|---|
|内联片段与缓存身份|acc8 LUI a2=62fc9000；acea ADDI s11,a2,19c保存同缓存地址；acf0 ADDI a2,a2,19c给输出指针。其间没有改写a2的调用|接受旧合同；参数地址reference不是实际写入，直接SB写者是后面的ad28|
|键/namespace/宽度|acda LUI a1=a01c3000、acf4 ADDI +58得key字符串；acde LUI s5=a01c3000、acf8 ADDI a0,s5,68得namespace；acee C.LI a3=1；acfc JAL目标a0060946|实参为 `(ck_config,wifi_configured,(void*)62fc919c,1)`，是1B输出范围，不是传缓存值、返回指针或4B布尔值。原ROM两字符串与I01一致|
|返回值判定|ad00 C.LI a5=1；ad0a BEQ a0,a5精确到b7fa|仅精确等于1走成功段，不改成正值/非零成功；返回值是配置接口状态/长度合同，不是configured本身|
|未返回1时的缓存写入|原失败日志ad24调用a008b51a，随后ad28为 **SB zero,0(s11)**；之后ad2c继续下一个初始化字段|清的是global cache整byte；没有本段“缓存失败就回写0到持久配置”的调用，也没有改成提前return。仅描述原正常控制流，不执行错误/异常输入|
|成功段与合流|b7fa **LBU a5,0(s11)**读取配置接口填入的完整byte用于既有日志；b814日志后b818的JAL rd=zero精确回ad2c|该段没有直接把cache设为1或`&1`归一化；状态rc=1与读入值相互独立。不证明配置文件/实际缓存只可能0或1|
|与getter衔接|I01已核a009d7b4同样以1B读取同键到同地址，rc!=1时SB清0，最终LBU返回；非零62fc3fec绕过读取直接返回cache|本初始化可产生getter所读的cache，但不能由此补全bypass标志设置时机、跨调用串行化、完整生命周期或所有writer|
|持久接口方向与资源|此site仅调用已有read入口a0060946；旧write入口a0061848属于其他已留存调用者。ROM键串借用、输出为静态global byte，当前内联块不分配/释放对象|不能将“RAM cache更新”称成“此site写入持久配置”。不展开下层buffer/文件句柄/锁/网络所有权，也不由静态指针推出运行同步保证|

没有机器行为纠正。必要旧行为可以表述为以下伪代码，非原源码或独立函数：

```c
// Inline within a005a736; unrelated initialization remains outside this view.
rc = a0060946("ck_config", "wifi_configured", (void*)0x62fc919c, 1);
if (rc == 1) {
    log_existing_success(load_u8(0x62fc919c));
} else {
    log_existing_read_failure();
    store_u8(0x62fc919c, 0);
}
// Both arms continue at a005ad2c, not a new early return.
```

I01的启动消费只按getter返回byte是否为0分流，并结合其他门；此配置值不认证无线关联、IP、云端绑定或硬件ready。旧物理/模型测试的结果也不能替代本块实际执行证据。

## 真正新增与实际验证

新增ROM功能、算法、ISA规则、完整函数导出及来源认证均为 **0**。新增仅既有初始化读/缓存门与I01的接线精度报告；16B补档是旧结论复核，不计功能增量，不重复读写后端或网络callback。

[verify.py](../../analysis/wifi-config-cache-i05-0041-20261024/verify.py) 只用Python标准库读取主仓ROM/旧JSON，映射VA−0x9ffff000。**18条旧原指令**逐byte一致，独立字段、JAL/BEQ目标、键串、旧reference类型及稀疏补档共 **45项PASS**。仅保存acc8 LUI、ad28 SB、b7fa LBU、b818合流跳转共16B，不导出初始化器或其他完整函数。[verification.json](../../analysis/wifi-config-cache-i05-0041-20261024/verification.json)留检查索引/原Evidence指针/局限，没有新REA ID。JSON、报告本地链接和提交差异检查通过。

## 未闭精确边与后继种子

本题的实际参数、1B写入范围、精确rc门、成功保留/其他清0及同getter关系已有定位答案。未核实际初始化何时执行、全部cache/bypass writer、持久配置何时被其他业务更新、后端完整I/O/锁/失败政策与运行同步；不能据此推出硬件或网络完成状态。

I01给出的本初始化种子已经由旧资料解释，本轮按覆盖收缩。其他字节0/1及a0061848 writer本身又有旧PSM flags/photo合同，不能当作新缺口继续重复。若后续确需补bypass政策，必须先给出62fc3fec的真实设置调用/字段写入种子；当前本范围未提供该种子，不扩全初始化、配网、云端或无界writer搜索，不自行承接。
