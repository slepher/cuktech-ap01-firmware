# F24：send计数分支、状态服务及getter重试的非作者复核

**限定接受F23核心合同；确认旧caller覆盖范围纠正1项，并对F23末伪码作原序精确化1项。新增业务0。** `0xa0197af0`确为signed BLT到快速getter `0xa0197acc`，所以flag0且signed count<limit也能进入getter；`0xa0131920`的返回0只触发重试getter，非零原值返回，没有直接作为M交copy的边。

服务正常路径依次重读K的signed halfword计数/限值、按mode位选择0/−11或K/T状态更新与三opaque调用，再读signed T+0x22：零重试，非零返回32位相反数。三下层服务/诊断body均未读，不由局部状态称实际线程身份、阻塞/调度成功或交付完成。

2026-10-24；非作者 `/root/f12`，任务F24挂原认领 **F11/8**；固定基线 `bd457a6`，独占 `re0041-f24` / `codex/re-0041-f24`。作者F23 `/root/a56` 已交付停止，主仓[唯一管理记录](rolling-management-0041-20261023.md)已登记本轮复核。遵循最新 [reverse-design](reverse-design.md)、[材料规则](../../analysis/README.md)及REA技能；只独立核所派caller/服务必要字段。

不运行F23或历史技术脚本、目标/指令/模型、固件、SIM/QEMU、构建、回放、设备或外部服务；不读三个opaque服务/heap/调度body，不切换共享REA，不改生产/ROM/配置/模型/主树/共享表，不提交或推送，无下级agent。只写本报告、[独立源码](../../analysis/miio-queue-send-wait-review-f24-0041-20261024/review.py)、[必要合同](../../analysis/miio-queue-send-wait-review-f24-0041-20261024/contract.json)；[生成JSON](../../analysis/miio-queue-send-wait-review-f24-0041-20261024/evidence.json)本地原路径忽略保留。

## 继承结论

|来源|继承行为/局限|本轮界面|
|---|---|---|
|[F11](miio-request-ownership-f11-0041-20261024.md)/F12、[F13](miio-native-queue-f13-0041-20261024.md)/[F14](miio-native-queue-review-f14-0041-20261024.md)|type1 send来源、Q/F/K/source/n、mstatus原序及M→copy发布接线；此另一状态服务先前opaque|不重验I业务/allocator/copy/队列发布，只补caller进入/返回范围和服务局部状态|
|[F21](miio-queue-message-source-f21-0041-20261024.md)/[F22](miio-queue-message-source-review-f22-0041-20261024.md)|快速getter两gp链/条件332请求和正常链helper已限定接受|getter三臂本体不重验；其caller前驱的整体覆盖强度按本报告纠正，不能把“直接落入边”当唯一入口|
|[F23作者交付](miio-queue-send-wait-gap-f23-0041-20261024.md)|旧caller另两getter回边、新22B诊断及0xa0131920的状态/返回/opaque接口|只非作者核该差集，作者中途速报的服务目标次序不作证据，以最终原字段为准|

原件沿 [CATALOG](../../../roms/CATALOG.md)：主仓 `roms/0041/ap01-1.0.2_0041.bin`，实查6,769,704B，继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算机械摘要；`file_offset=VA−0x9ffff000`，不套0031/unsigned/SIM。

旧caller出处为F13本地忽略 `reverse/analysis/miio-native-queue-f13-0041-20261024/evidence.json#/rows`；F23首阶段/增量输出分别记录旧定位与后续补证，不能只读初始pending JSON就判断最终缺失。0xa0131920旧metadata范围200B、extent EID `ev_1bec9a08b90ab3a5a5e5df3aebd762aca00d8189db3a3050492eb9af24e4d5d3`、directcall EID `ev_3c7ff280f2e61f99733408917fc04191f5ab1220ee3137e9dbaa342361b3419c`只定位。新复核由原字/Capstone/位域取得，没有新造REA ID或改标profile。

## 本轮复核或纠正

独立检查器直接读3个必要区间：`[0xa0197ab8,0xa0197b1e)`、`[0xa0131920,0xa013197c)`、`[0xa013198a,0xa01319e8)`，合 **288B，65项PASS**；没有读取服务诊断参数中段0xa013197c..198a或任何新callee正文。普通指令由 **Capstone 5.0.7 / RV32+RVC** 解码，另独立核JAL、AUIPC/JALR、signed B-format、C.BEQZ和LUI/I-format地址；无UNKNOWN/厂商规则或模型执行。

### 旧caller覆盖纠正：直接边不是全部前驱

`0xa0197af0`原字 **`e34ef7fc`** 独立字段 `(opcode,f3,rs1,rs2)=(0x63,4,a4,a5)`，**signed BLT**，目标独立解为 **0xa0197acc**。不是unsigned比较、不是跳另一个等待入口。

实际至少有三条本题已证getter进入边：

- `0xa0197aca`：flag非零，直接落入7acc。
- flag零跳到7ae8；`LH(K+0x22)<LH(K+0x20)` 时由 **7af0** 回7acc。
- 状态服务返回0由 **7afc** 回7acc。

因此F21/F22冻结报告中“caller第一次flag非零才调用getter”的整体表述，须收窄为**7aca直接fallthrough这一条边**。flag稳定为0、count<limit且第一gp链为空时，可正常到getter自身flag零的332B请求分支，**不需要flag变化**。本纠正增加的是已定位caller前驱的覆盖，getter两链/重读/条件申请/容量边界本体不变。按管理要求原冻结文件不改，在本报告保留纠正依据；未做运行/输入实验或推缺陷。

### F23伪码原序精确化：先读判定值，再清另一槽

实际 `0xa0131972` **先LW T+0x0c到a5**，`0xa0131974` 才SH0到T+0x22，`0xa0131978` 比较**先前读入的a5**。F23地址表正确，但其末伪码把clear列在重新load/if之前。精确表达应为：

```c
status_value = load32(T + 0x0c);
store16(T + 0x22, 0);
if (!(signed32(status_value) > 0)) diagnostic_boundary();
```

本报告不将这次读移动到clear之后或插入额外重读。这是1处伪码原序精确化；F23核心状态/目标事实没有新的语义争议，原件/模型均未修改。

### 独立裁定的参数、状态与返回

|复核点/地址|接受的精确合同与边界|
|---|---|
|source/n保存：7ab8/7aba与service prologue/epilogue|外层s4=n、s3=source地址；service先存原s3到sp+0x1c、原s4到sp+0x18，正常尾声从同槽恢复。callee及其下层正常遵守ABI时跨服务保存的是数值，不是源区域寿命或无副作用证明|
|直接flag零call：7af4/7af6/7af8|a1=word(Q)，a0=K，JAL到0xa0131920；没有构造&outM。a2=n是遗留寄存器值，不据此添加形式参数；word(Q)正式类型也未知。该Q保持分析只限未穿越getter零诊断的正常直接边|
|7afc与7afe..7b10|C.BEQZ a0→7acc；非零恢复mstatus/寄存器，原a0返回。此服务返回值没有直接作为M进copy；只有快速getter非零才到7b12..7b1a|
|getter零诊断：7ad2..7ae8|LUI/ADDI构造a0=0xa062c874、a1=0x79、a2=0；AUIPC/JALR独立解到0xa0019672。不能从它线性拼到7ae8并假定诊断返回、a0仍Q或其余寄存器稳定|
|service保存/loop：1938/193a/1944/1948..1958|s2=K，s3=word(Q)&0x40，s7=K+8；每轮重新signed LH(K+0x22)和LH(K+0x20)。小于则返回0；未小于且mode非零返回常量−11。不命名正式mode位/错误枚举，不把计数门擅称调度成功|
|T/global：195c..1978|global地址=0x62fc6c18，读T后word(T+0x44)=K；U16 K+0x10读出+1，SH回同槽；然后按上节先读T+0x0c、清T+0x22并比较保存值。没有T非零门，正常有效T为前提，不套其他报告某次运行线程身份|
|第一opaque：1992..199e|a0=保存T、a1=1，目标独立算 **0xa002772e**，返回保存s8。其余正式参数/副作用不补猜|
|第二opaque：19a0..19ac|先SB8到T+0x1c，再a0=T、a1=K+8，目标独立算 **0xa00272d4**。不反转两个服务、不把它们命名为已证阻塞/调度动作|
|第三opaque：19b0..19be|只有第一返回s8非零才重读word(0x62fc6c18)作a0，以原保存T作a1，目标 **0xa001ad30**；不假定新读值仍等于T。三个body均未读|
|结果重读/返回：19c2..19e6|signed LH(T+0x22)为0则C.BEQZ到1948重新读K计数；非零NEG32返回相反数。原halfword为负时结果可正，不能统一写“负错误”。另有返回0与mode分支−11。循环是否进展未知|

本服务没有本体直接构造M或&outM并返回的连接；它可能经K/T/opaque服务改变状态，但不能据名称把a0当消息指针。caller零返回→getter重试之后，getter的候选M才交继承copy接口。仍不排除不透明服务经对象副作用写出其他内容，不能将“本层未见outM”说成整个下层无输出。

局部表达（非原源码，原序与opaque边界保留）：

```c
saved_source = source; saved_n = n;
// flag非零直接getter；flag0还必须保留count<limit这条getter进入边。
if (flag == 0 && signed16(K+0x22) >= signed16(K+0x20)) {
    r = service(K, word(Q));
    if (r != 0) goto restore_and_return_r;
}
M = quick_getter();
if (M == 0) goto diagnostic_boundary;
copy_and_publish_interface(K, M, saved_source, saved_n);

// service正常有效对象路径，mode只在入口取一次；K计数每轮重新读。
mode = word(Q) & 0x40;
for (;;) {
    if (signed16(K+0x22) < signed16(K+0x20)) return 0;
    if (mode != 0) return -11;
    T = word(0x62fc6c18);
    word(T+0x44) = K;
    halfword(K+0x10) = u16(K+0x10) + 1;
    v = word(T+0x0c);
    halfword(T+0x22) = 0;
    if (!(signed32(v) > 0)) diagnostic_boundary();
    r = opaque_a002772e(T, 1);
    byte(T+0x1c) = 8;
    opaque_a00272d4(T, K+8);
    if (r != 0) opaque_a001ad30(word(0x62fc6c18), T);
    h = signed16(T+0x22);
    if (h != 0) return -h;
}
```

diagnostic边界没有已证普通继续；上式不填诊断返回，也不将字面函数参数数量等同完整实际ABI。T/global和K字段的正式结构/枚举名字仍未知。

## 真正新增

**复核新增业务0、ISA/来源认证0、整库排除0。** F23核心字段/调用/返回合同获得限定接受；确认其对旧F21/F22 caller前驱覆盖的纠正，另明确1处伪码load/clear原序。没有重验getter三臂、heap/池、copy4、定时send或三下层服务。

F21/F22的helper本体依旧成立，只有“直接边”与“全部caller进入条件”的范围必须分开；不能因本轮确认回边再改写已验申请接口或把M有效性外推。A/J其他题与本K/T/source没有已证对象合并关系。

## 未闭精确边

仍未知三个服务的对象持有/副作用/真实返回意义、T/global writer和寿命、真实mode/flag/counter、循环进展与并发保证、源内存实际寿命、诊断是否返回及其寄存器合同、实际getter取得/copy/consumer成功。数值保存不保证source区域在任何等待状态都有效；局部服务返回也不认证投递。

一个有种子的后继为 **0xa01319a8/19ac→0xa00272d4(T,K+8)** 对已保存T及K+8的状态接入/返回到T+0x22重读的必要合同；管理窗口须先查重登记，只核对应正常连接，不扩全调度。当前只保存该锚点，未取新body或启动后继。

实际检查为65项原字段/目标/ABI栈槽核对、JSON解析、报告引用在本树或整合主树可定位、空白/独占文件及`git diff --check`。源码/合同/报告未提交，生成JSON受忽略留原路径，复核者完成后停止。
