# Q-27 / S42 MCU OTA 应用七槽非作者复核

**可独立使用阶段已闭合但接口未闭。接受作者六新槽1638 B及28 B表的限定应用合同；语义纠正0，新增业务覆盖0。** 完整MCU OTA、验证、trigger和实际烧写仍未闭。复核者 `/root/app_mcu_ota_review_01` 未参与作者取证。

启动基线 `5f50102e56012e2e1e0fa8f9d8010d3c8e8214fd`；分支 `codex/app-mcu-ota-review-01-20261025`。作者提交 `342abd2b092ed1bb12d8ace1991f3e83f0dc972e` 已停止，检查时主树尚无作者报告，按派发使用父窗指定 `ap01-s/mcu-ota01` 作者树只读报告、decode.py和三份原字产物。没有执行作者脚本。已读主树reverse-design 3.1/3.2/5.1/7、rolling-management顶部和Q-27精确补位行；准备包只读S42初包/成熟动态。

首工具UTC `2026-10-24 18:21:11`。预测3–5分钟，中置信，依据作者完整281秒；提前完成即交付。技术、提交、停止分列于末节。token遥测不可得，等待不能从墙钟分离；无外部等待或中断，不填有效工时。

## 继承结论

继承作者报告所指既验MiIO注册/HTTP adapter、Q08文件API、UART/USB/P08接口和完成槽 `a0074ea2` 282 B。完成槽EID `ev_9da86361ce16fc84dba2cdf02382d0ad5f7241c94d366c9256e11464fa3bcb17`，注册EID `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a`。旧body未重验、未计本轮新增。特别是正常complete返回验证/trigger状态，不能套错误close的恒0；signal API返回也不等OTA结果。

本报告相对作者报告路径待主窗合并后可用：[作者报告](app-mcu-ota-research-01-0041-20261025.md)。当前只读来源绝对树由父窗提供，不自行猜测已合并。

## 本轮独立复核

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射offset=VA−`0x9ffff000`，独立核验通过。[verify.py](../../analysis/app-mcu-ota-review-01-0041-20261025/verify.py) 是独立只读静态程序，使用本地Capstone 5.0.7 RISC-V32/RVC顺序解码，未运行目标或指令模型。514条指令连续覆盖六窗，无未知或尾缺口；原字逐条对照作者raw，六窗摘要一致。14处配置字符串原字与ROM一致。独立输出 [review-checks.json](../../analysis/app-mcu-ota-review-01-0041-20261025/review-checks.json) 和 [review-disassembly.txt](../../analysis/app-mcu-ota-review-01-0041-20261025/review-disassembly.txt) 为ignored待转存证据。

|复核项与原字锚点|接受的事实/限定|
|---|---|
|`a01bb0e8` 28 B，`e8fb06a0224b07a09e0107a0a60207a0a24e07a0900307a0cafa06a0`|七槽依次prepare/version/open/write/旧complete/error/末通知。不能按槽位置推start原型。|
|`a006462e b7bb1ba0`、`a0065fe4 130bc907`、`a00661f2..621b`|表基址a01bb0e8，28 B栈副本；注册a4=s2+0x7c=C，a2由byte(s2+0x88)转0/4。不是命令0x38c对象同基址证明。|
|`a006fc5a..fc66`|prepare保存T=a0、C=a1、type=a2、params=a3、len=a4；全局byte门及短signal持有后的C+c busy门失败−7。|
|`a006fcac..fd16`|C+18 byte、C+1c word、T字符串/证书半字和三64 B槽先清，后type非0回−10；params/len仅存栈descriptor，初始化失败−5。|
|`a006fd26..fd46`、`a006fd82..fd8c`|mcu_url复制至T+b0、容量256并要求非空。失败走−10及已初始化解析器清理。|
|`a006fdee..fdf2`、`a006ff28..ff76`|hostip_list按token+c计数；首byte减'1'后unsigned<=8才复制63 B到T+1b0再每轮+40，写NUL。无额外3项上限；不承诺异常列表容量安全。|
|`a006fe26..fe4a`、`a006fea0..feca`|signed字段API输出至C+18；非零才读original_length至C+1c，缺失−10。该word不是header total。|
|`a006fe88..ffa8`|cert_verify取栈11 B；verify/optional/none比较长度7/9/5，写T+6e半字0/1/2，其它回落0。|
|`a0070000..005c`、`a00700b0`|partial API输出T+6c；force成功写C+17c=1、C+17d=value byte，失败清C+17c半字，随后C+17e byte=0；不扩API输出宽度。|
|`a006fd68..fd80`|初始化后的解析器出口调a01b38b6；status0才续a01b3f38，未显式重设a0，不猜尾API用途。原JSON/栈地址无本层长期存储。|
|`a0074b34`、`a0074b58..4b8e`，`5d55`|只使用a3输出对象，栈8 B配置读取及可选mcu_fw_ver输出；末端恒−9，不能视为成功/start语义。|
|`a00701ce 93890401`、`a00701dc..01e8`|G=C+10；helper0后写word(C+16c)=584c4655及word(C+170)=total，继而file-open(G,total)。失败−1，file-open返回原样；本层不补signal。|
|`a00702b4..02da`，`93058900`|write先helper(G,offset,buf,len)，忽略其返回；随后file-write(G,offset+8,buf,len)，0回len、否则−1。buf本层借用至两API返回，无存指针/复制/free。|
|`a0070398..03c8`，`0145`|error调用a0070322(G)、a01addc6(G)、signal(*(C+178))，忽略三者返回并恒0；不free C/T。|
|`a006fad2 ef104f84`|末槽透传a0/a1到a0060b16并返回其a0；不证明下游清ctx或完成烧写。|

阶段接合静态推断（不是原源码）：prepare复制应用参数 → open同G并写magic/total → write同G且payload偏移+8 → 正常路径继承complete写8 B头/验证/trigger及signal，错误路径本轮证实关闭接口后signal恒0。正常complete不等同error-close全部资源释放；继承API仅说明本层实参与返回边界。

## 真正新增

新增业务恢复0 B；这是非作者复核，六窗1638 B+表28 B均为作者差集重验。必要旧注册锚点50 B单列，不重算新增，也未重做旧7982 B root。新增的是独立复验源码和原字对照产物。检查全部接受，无需作者修正。

## 未闭精确边

严格止 `a006fade(C)` trigger、`a00703ce(G,C+16c,1)` 验证、三个tag helper `a00700b6/a00701f6/a0070322`、`a0060b16`、公共JSON/文件/信号/配置等API；本轮未读其body。完整C/T构造析构、并发取消、open失败后的最终归还保证、正常trigger后的G寿命、MCU内部/传输/真实烧写仍未闭。没有执行固件、模型、SIM/QEMU、回放、构建、设备或外网；未改ROM/生产配置/分析器或共享REA。没有下级代理。

有种子的后继仅是已登记边界上的 `a006fade(C)`，需管理窗口查重授权后才能研究；本任务已停止，不沿该种子展开。应用返回0或signal调用不能外推硬件安装成功。

## 技术、提交、停止

技术完成UTC `2026-10-24 18:23:37`，首工具起146秒，包含读取与工具等待，实际早于3–5分钟预测。静态程序断言通过；原件身份、七word、514条原字、14字符串及范围覆盖检查通过。提交前另做diff/JSON/精确文件范围检查。

提交与停止时点、实际commit和ignored清单由最终交付回报，避免将提交时间写成有效取证。只提交本报告与verify.py，不推送；ignored两文件由父窗转存到主树同相对路径。
