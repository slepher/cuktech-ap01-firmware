# P01：activity byte 与两个 idle counter 的局部原字段精度

2026-10-24；基线 `327d557`；独占树/分支 `re0041-p01` / `codex/re-0041-p01`。**旧主输入在 `62fc403a` 存 byte1；旧周期callback尾段两次 LBU 读同byte。首次非零臂先SW清 `62fcbcc4`，经一个既有诊断调用后再读；第二读非零才SW清 `62fcbcc8`，随后SB清activity。两次读各有独立零分支，不合并成无条件双重reset。** 这是旧合同原字段精度复核，新增功能0；作者静态验证通过，尚待非作者P02独立接受。

使用 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只读主仓ROM/旧证据，写独占报告与analysis；不打开或切换共享REA target/database，不执行ROM、SIM、构建、历史回放、输入实验、设备、外部服务或模型，不研究异常/并发/漏洞/缺陷，不改生产代码、ROM、配置、分析器模型或他人文件，无下级agent。以下伪码仅表达既有正常静态路径，不是原源码。

## 继承结论

|已有出处|继承范围|本题仅补|
|---|---|---|
|[J07盘点](input-idle-reuse-gap-j07-0041-20261024.md)|已按早期/complete/较晚报告去重，定位真实producer、consumer与完整旧留存，纠正s2与app混同|必要原字宽度、基址、直接控制门与重读/写入顺序；不重新盘点所有输入writer|
|旧`main-knob-0041-round2.json#/records/1/normalized_result/assembly`，Evidence `ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`；system cached main|afd52..afd60的activity/唤醒接入早有|只核当前SB同字段身份和直接目标，不重做主键大handler或醒门|
|旧`reverse/analysis/screen-host-append-20261020.json#/functions/4`，procedure a00af262，Evidence `ev_4cd9ffcadd54fe381d075066b194c8af6fb2cd7098d35012c9c14281446c9463`|完整callback汇编/伪码早已保存，activity与两个计时器行为已经解释；伪码含unreachable/extraout限制|只核选定普通指令，旧完整body不重新导出、不认证其所有分支|
|guide-complete `#/saver/idle`及`#/bounded_local_disassembly/saver_idle_gates_asm`/`saver_idle_branch_asm`；[最终complete](application-rehost-complete-0041-20261017.md)|ScreenOff/ScreenSave时长、长按与首唤醒事件消费及SIM验证已有|直接继承，不重做算法、阈值或运行验收；passed-in-sim不等于原ROM/设备完整恢复|
|[E05](ctk-app-close-e05-0041-20261023.md)/[E06](ctk-app-close-review-e06-0041-20261023.md)|1000ms T1注册a00af262、borrowed app userdata及DELETE关联已独立接受|不复验timer注册或app生命周期；s2是全局基址，不是app|
|I03/I04、L/K/D/G已验报告|各自Time2对象、setter、factory slider、动画/显示合同已有|不接相邻主题、所有writer或GPIO，也不研究callback相邻OTA/安全分支|

## 本轮复核或纠正

原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−0x9ffff000`。独占 [verify.py](../../analysis/input-idle-activity-p01-0041-20261024/verify.py) 使用Python标准库直接读取20个稀疏原指令，解算RV32 I/S/B/J及C.LI/C.BEQZ字段；不导入J07或其他作者的检查器，不执行目标/输入。必要结果见 [evidence.json](../../analysis/input-idle-activity-p01-0041-20261024/evidence.json)，没有新REA Evidence ID、完整handler/callback复制或模型规则。

|原指令/字段|独立静态核验与限定|
|---|---|
|afd52 LUI s6，afd56 ADDI s11|s6=62fc4000；s11=s6+2c=62fc402c。afd5a的`8547`独立为C.LI a5,1；afd5c S字段opcode23/f3=0/rs2=15/rs1=27/imm14，即 **SB1@62fc403a**；afd60 JAL ra实际目标a00a769a|
|af78a/af79a|LUI rd18/upper62fc4000；ADDI rd18/rs1=18/imm2c，得s2=62fc402c。沿J07已定位旧正常尾段，此为全局base，与timer+0c借用的app对象区分，不给s2套app成员含义|
|afa78|opcode03/f3=4/rd15/rs1=18/imm14，**LBU**第一读activity。不是signed byte、halfword或原cached a5复用|
|afa7c/afa80，afa8c|LUI s1=62fcc000；ADDI−33c，精确地址 **62fcbcc4**。`ddcb`独立拆C.BEQZ：rs1'=a5，目标 **a00afb42**。第一读为零走既有ScreenOff分支，当前直落clear臂不执行|
|afaa8/afaac|`23a00400`是SW x0,0(s1)，32位清62fcbcc4；随后JAL ra独立目标 **a008b51a**。保留此旧诊断调用，不省略成连续两次counter写|
|afab0/afab4/afab8|重新执行与首次同字段的 **LBU@62fc403a**；随后LUI s1=62fcc000、ADDI−338得 **62fcbcc8**，不是复用第一个counter地址|
|afabc|B字段opcode63/f3=0/rs1=15/rs2=0，精确目标 **a00afbec**。第二读为零跳既有ScreenSave分支；不执行紧随的counter/byte清理|
|afac0/afac4/afac8|第二读非零的直落臂：先SW x0,0(s1)清32位62fcbcc8，再SB x0,14(s2)清8位62fc403a，最后JAL x0直接到 **a00af2a8** 共同尾声目标；没有交换两个写入或改成一起清零|

旧语义纠正0。对J07的精度收紧是：其“两个counter再消费byte”定位必须保留两个门和中间调用。仅从首次非零，不能把第二次值当作同一缓存读或宣布跨调用稳定；本题不研究该诊断内部/真实修改可能性，不作并发或缺陷判断。

## 真正新增：功能0，旧合同局部表达

```c
// 仅必要局部路径；旧阈值/其他分支直接引用，不表示原源码。
main_input_fragment:
    store_u8(0x62fc403a, 1);
    known_wake_wrapper();                 // a00a769a

periodic_activity_fragment:
    first = load_u8(0x62fc403a);
    if (first == 0) goto old_screen_off;   // a00afb42，旧算法不展开
    store_u32(0x62fcbcc4, 0);
    existing_diagnostic_call();           // a008b51a
second_activity_test:                     // a00afab0
    second = load_u8(0x62fc403a);          // 必须重读
    if (second == 0) goto old_screen_save; // a00afbec，旧算法不展开
    store_u32(0x62fcbcc8, 0);
    store_u8(0x62fc403a, 0);
    goto common_tail;                    // a00af2a8
```

`old_screen_off`内如何重入后段、各threshold和刷新门沿guide/旧body继承，本题不重建其完整CFG。这里仅表达选定直接门，不把first==0分支简化成函数return，也不把第二读为零改成无条件消费flag。main生产者与周期消费者是同全局byte身份，不因此声称它们在实际运行中已经先后执行、所有事件均进入该路径或1000ms实际等于无延迟的一秒。

这些是全局标志/计数的按值访存，没有本片段新分配、free、指针保留或所有权转移；既有app/timer生命周期沿E05/E06。只确认两counter是32位清零，不在本题给全局计数器加原子性、互斥、物理时间单位或完整结构名称。旧功能、body留存、SIM通过不重计；无新增来源认证、算法、ISA规则或完整函数导出。

## 精确未闭与实际验证

J07指定生产者→同activity字段→两个counter门/重读/消费顺序现已由必要原字段支持，尚待P02非作者复核。完整callback的其他刷新/阈值/对象分支、全部activity生产者、输入设备/真实节拍、跨调用或并发保证均不在此局部接受范围；未以本题证明这些未知已经恢复或不存在。

唯一必要后继是P02独立检查上述20条字段和直接目标，参考旧载体核范围，不重验整个timer、唤醒或threshold。没有新的必要功能种子，不自动扩全输入/全GUI/全ROM。

实际验证：独占脚本 **PASS：20条稀疏原指令、76B，独立确认3个JAL目标（含JAL x0）、1个BEQ与1个C.BEQZ**；另核旧assembly对应记录原序。JSON解析、报告相对链接及diff检查通过。作者自检不是独立验收，也不是目标执行/真实输入时序验证。
