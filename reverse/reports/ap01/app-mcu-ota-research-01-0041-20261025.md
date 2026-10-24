# Q-27：MCU OTA 应用七槽生命周期适配

**应用侧准备、打开、写入、错误归还与已验完成槽的接合已恢复；作者静态结果，待非作者复核。完整 MCU OTA / 实际烧写未闭。** 与 ota_app 的 F=C+4 不是同一布局；本对象以下记 C，内嵌文件/校验接口地址 G=C+0x10。

认领 `/root/app_mcu_ota_research_01`；分支 `codex/app-mcu-ota-research-01-20261025`；启动基线 `7e4f4dca88af733319500704ddfeb2046ec2006b`。独占本报告及同stem analysis，不回退他人，不派下级。已读主仓 reverse-design 3.1/3.2/5.1/7、rolling-management 顶部及 Q-27。应用 REA 技能的事实/推断/未知分列原则，使用本地 Capstone 5.0.7 静态解码，不切换共享 REA。

原件 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset=VA−`0x9ffff000`；本轮实际核验。未执行目标、模型、SIM/QEMU、回放、构建、设备或外网，未改 ROM、生产配置或分析器。

首工具 UTC 2026-10-24 18:05:02；预测7–11分中低置信，依据六新槽1638 B与已验完成槽现成。实际技术/提交/停止时点在交付分列，提前完成立即交付。无外部等待；工具调用等待包含在墙钟中，不能独立量化有效工时；token遥测不可得，不造值。

## 证据与继承边界

[解码脚本](../../analysis/app-mcu-ota-research-01-0041-20261025/decode.py) 逐指令按低两位决定2/4 B宽度，保留 raw、offset、PC-relative目标与 AUIPC/JALR目标。1638 B六槽全部连续覆盖，无未知指令，无越界尾字。脚本只读指定六窗和28 B表，ROM全件只用于身份校验；字符串窗口另留存。

[raw.json](../../analysis/app-mcu-ota-research-01-0041-20261025/raw.json)、[disassembly.txt](../../analysis/app-mcu-ota-research-01-0041-20261025/disassembly.txt)、[boundary-evidence.json](../../analysis/app-mcu-ota-research-01-0041-20261025/boundary-evidence.json) 为 ignored 中间产物，主窗转存，不 force-add。后一文件保存六项 metadata（仅范围/调用，不冒充body）、注册必要原字和配置名原字。没有新 REA 导出。

继承 `evidence/rea-0041-20261017/evidence/miio-recovered.md` §3 MCU命令对象与七槽注册；upper-complete records248 EID `ev_c3dd842723b83165bc8e1a6b235f2005269080da4969520bd0c0f0e413db133a` 的既有初始化留存。本轮只抽取注册窗口和必要寄存器定义，不重做7982 B root。

完成槽 `a0074ea2` 的282 B合同直接继承 upper-miio-a.md §同地址，EID `ev_9da86361ce16fc84dba2cdf02382d0ad5f7241c94d366c9256e11464fa3bcb17`，未重读其body。MiIO offer/selector/start与HTTP adapter继承 Q13/Q16；UART/USB/P08和下游opaque固件流继承，未重读载荷或传输。文件write/close API继承 Q08（包括 fd>0 才关闭），本轮只证明传入同类 G 地址，不把 C 套成 ota_app。

## 表、对象与调度

ROM `a01bb0e8` 28 B，LE原字 `e8fb06a0224b07a09e0107a0a60207a0a24e07a0900307a0cafa06a0`：

|表偏移|目标 / body字节|本层实际合同|
|---|---|---|
|+0|a006fbe8 / 1230|prepare(T,C,type,params,len)|
|+4|a0074b22 / 114|只使用a3输出对象；配置版本输出尝试，恒回−9|
|+8|a007019e / 88|open(T,C,total)|
|+0xc|a00702a6 / 124|write(T,C,offset,buf,len)|
|+0x10|a0074ea2 / 282已验|complete(T,C)，旧验证/写头/trigger合同|
|+0x14|a0070390 / 62|error-close(T,C)，接口归还并signal|
|+0x18|a006faca / 20|透传既有a0/a1到a0060b16；返回其a0|

注册旧原字 `a00661f2..6218` 从 `s7+0xcc+0x1c` 复制28 B到栈表，a3传栈表，a4=s6。必要既有定义 `a006462e: lui s7,a01bb` 与 `a0065fe4: s6=s2+0x7c`，证明本表与该 C 实参接合；注册a2由 byte(s2+0x88)非零转4、零转0。**C是此处s2+0x7c的应用子区，不是0x38c命令对象的基址；本轮不重做s2构造与全析构。**

继承注册函数将表值复制到T+0x30、C指针保存到T+0x4c；offer同步借用params调用prepare，prepare回0才接受。HTTP open/write传入同一C；HTTP正常close调用+0x10完成，error调用+0x14归还，成功完成后的+0x18通知另经现成adapter门。不能将+4按表索引猜成start：T的start是既验公共函数，+4槽本轮实际只确认a3使用及恒−9，不补未知调用时点。

## prepare：输入借用、配置副本及状态

入口首先检查全局byte `0x62fc4a10`，零返回−7。调用 `a01b9588(*(C+0x178))`，非零返回−7；成功后锁内读取 byte(C+0xc)，随即 `a01b3226(*(C+0x178))`，该byte非零也回−7。这个短持有段结束后才解析参数；不声称整个prepare处于该signal对象的互斥区。

保存a0=T、a1=C、a2=type、a3=params、a4=len。清 byte(C+0x18)、word(C+0x1c)；清T+0xb0、T+0x70首字节、T+0x6e半字和三个64 B槽 T+0x1b0/+0x1f0/+0x230。type非零回−10；这些清理先于type门。栈解析描述符首两word是params/len，余word清零；`a0060cac(&descriptor)`非零回−5。原params指针不写入C/T。

通过已知JSON API查询与复制下列ROM key（准确名称在boundary证据）：

|key / 类型字|目标与行为|
|---|---|
|mcu_url / 3|`a0061f0c(&D,0,&query,1,T+0xb0,0x100)`；失败−10；成功还经`a002de24(url,0x100)`要求非空|
|mcu_hostip_list / 2|`a0061d20(&D,0,&query,1)`取得可选列表token；按token+0xc计数查询索引|
|列表元素 / 3|每次取到栈64 B，首字节仅'1'..'9'才复制63 B至T+0x1b0再每次+0x40，并显式写终止NUL；没有保存token/buffer指针|
|mcu_hostip / 3|复制至T+0x70，限64 B；失败清首字节|
|mcu_signed_file / 4|`a01976d4(&D,0,&query,C+0x18)`；事先该byte已清零|
|cert_verify / 3|取栈最多11 B；比较 verify(7)/optional(9)/none(5)，T+0x6e半字分别0/1/2；失败/其它文本回落0|
|mcu_original_length / 4|仅signed byte非零时查询至C+0x1c；缺失走−10；此word不是本层header total|
|partial_enable / 4|写T+0x6c（下游既验start读byte），本层API输出宽度仍按其边界，不扩大为已证完整word|
|mcu_force / 4|查询到先清零的栈byte；API回0则C+0x17c=1、C+0x17d=该值，否则半字(C+0x17c)=0；随后C+0x17e=0|

列表只观察到token声明计数门，没有在本槽看到将写入个数限定为3的额外条件；正常输入副本路径成立，不额外承诺任意列表长度的容量安全，也不进行异常输入实验。

已初始化解析器的出口汇合 `a006fd68` 调 `a01b38b6(&D)`；返回状态s3非零直接返回，零再调用 `a01b3f38`（a0沿前一API返回值，未显式重新设参），最终返回s3=0。不猜该尾API为free/通知，不展开body。解析器初始化失败直接回−5，不能把该分支补成已初始化对象析构。

本层没有普通heap分配；所有业务参数落入C/T值字段或字符串副本，未保存原JSON/栈query地址；公共JSON内部是否临时分配及清理范围止API。prepare未写ot_config持久项，读取配置版本也不在此槽。

## 版本输出槽：恒−9独立于格式输出

`a0074b22`保存a3为输出对象，栈8 B清零；调用 `a00616de("ot_config","mcu_ver",stack8,8)`，忽略其返回。`a002dcae(stack8)`非零才以 `a002de24(stack8,8)`长度调用 `a01b69d2(a3,"mcu_fw_ver",stack8,len)`。之后无条件返回−9。输入a0/a1/a2没有被使用，栈8 B无长期保存。格式/JSON服务的复制与终止语义止API，不能仅因可选输出发生把−9写成成功或start拒绝原因。

## open：G与8 B头的建立

`a007019e(T,C,total)`调用 `a01b9588(*(C+0x178))`，非零回−1；成功后调用 `a00700b6(C+0x10,total)`，非零回−1；后者严格止API，未读body。成功后 word(C+0x16c)=`0x584c4655`（LE字节`55 46 4c 58`），word(C+0x170)=total，然后 `a00b503e(C+0x10,total)`，a0原样返回。

本层没有在上述helper失败或最终file-open返回时signal；signal保持到旧complete或error-close出口，不虚构本地失败释放。API G是否分配内部校验对象仅作未知；本槽确认传入地址、total与头写入时点，不沿a00700b6内部证明。

## write：偏移加8、同步借用及长度返回

`a00702a6(T,C,offset,buf,len)`先 `a00701f6(G,offset,buf,len)`，**忽略其返回值**；随后 `a00b5122(G,offset+8,buf,len)`。后者返回0则本槽返回原len，非零则−1；只有失败日志路径可选，不改变返回。offset+8为32位运算，无本层溢出门，不在正常输入合同中假设更宽整数。

没有保存/复制/free buf，也不在本槽signal；输入buf同步借用到两个API返回。既验file-write在offset=0有首字节变换，但本层正常offset=0实际传8，不能把ota_app第一块变换机械套到MCU payload。G是地址C+0x10，确实与open/close/complete同一对象；未知校验helper只保留精确四实参，不展开算法。

## 完成、错误归还与最后通知

已验complete(T,C)：先 `a0070322(G)`，验证 `a00703ce(G,C+0x16c,1)`，可选verify(G,8)；验证零才写8 B头 `a00b5122(G,0,C+0x16c,8)` 并调 `a006fade(C)`。trigger回0且C+0x174计数正时才删除ot_config/mcu_ota_count并清计数；每个出口signal `a01b3226(*(C+0x178))`，返回首失败status或trigger结果。本轮头来源刚好是open的magic/total，不将C+0x1c original_length混作header total。此合同继承，不计新增282 B。

错误close `a0070390`：`a0070322(G)` → `a01addc6(G)` → `a01b3226(*(C+0x178))` → 返回0。三个callee返回均不传播。a01addc6沿Q08 fd>0才关闭并归还该G接口的已验API；本层原字a0070398/a00703a8确证给它的是与open/write同一G，未free C/T。complete有signal不代表已调用同一file-close；不能宣称正常成功与error释放完全对称，trigger之后实际文件/校验对象的寿命仍未闭。

最后通知 `a006faca`仅保存/恢复栈与ra，直接调用 `a0060b16`，未改传入a0/a1，也未覆盖返回a0。继承adapter时点只可说提交失败或成功安装后的相应门可能调用它；a0060b16角色、是否修改状态/释放对象严格止API，不因“通知”标签断言ctx清除或整条OTA完成。

## 限定验收与停止边

本轮能重建：同注册C/T的prepare接受与副本、版本输出尝试、G打开/头来源、payload偏移+8、长度返回、error归还/signal、与旧complete写头和trigger的接合。真实新增只六槽1638 B，表28 B另计；旧完成282 B、MiIO/UART/公共库新增业务覆盖0。

未闭且本轮严格停止：a006fade实际trigger266 B、a00703ce验证1886 B、a00700b6/a00701f6/a0070322 helper内部、a0060b16通知内部、完整C/T构造析构、并发取消、正常trigger后G释放保证、MCU传输/安装/内部固件/真实硬件效果。完整地址与实参足供后续已登记差集；不为闭合追新helper、不下探文件/hash/配置/sem/JSON/allocator库。应用完成及返回0不等价于MCU烧写成功。

作者检查：原件长度/SHA通过；表七word通过；六metadata extent匹配且总1638 B；逐指令连续覆盖与所有AUIPC/JALR静态目标核对；字段/返回与原字接合；JSON可解析；git diff --check；精确提交路径和ignored清单在交付回报。无独立非作者验收声明。

技术完成快照 UTC 2026-10-24 18:09:15：距首工具4分13秒（预测7–11分，已提前闭合限定差集）。这是墙钟包含读取/工具等待，非有效工时。提交与停止时点由交付消息另外报告。
