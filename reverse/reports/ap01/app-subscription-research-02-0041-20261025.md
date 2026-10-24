# Q23：有效订阅身份、owned构造与正常重用门（0041）

作者静态恢复，待非作者复核。正常有效descriptor、有效reciprocal图前提下，本阶段可作为重建合同；不是完整manager生命周期闭合，也没有执行观察。

## 任务与证据

分支 `codex/app-subscription-research-02-20261025`；基线 `a4979f031d0799f97913c9496213394ab02abb58`。只写本报告及同stem analysis。主树reverse-design 3.1/3.2/5.1/7、rolling顶部/Q23只读；使用reverse-engineer-anything技能，无下级、外网、共享REA变更、固件/模型/SIM/QEMU/回放/设备/构建执行。没有改ROM、生产配置或分析器。

主仓原件 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，6,769,704 B；SHA256沿CATALOG `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，本轮核长度，offset=VA−`0x9ffff000`。新增七原窗62+74+200+76+74+38+80=604 B，均Capstone 5.0.7 RV32+C完整解码，无未知字。原字、偏移、窗口摘要和逐指令见[static-windows.json](../../analysis/app-subscription-research-02-0041-20261025/static-windows.json)，可由[extract.py](../../analysis/app-subscription-research-02-0041-20261025/extract.py)静态复取。该JSON是本地导出，不伪造新REA Evidence ID。

旧证据统一位于主仓 `evidence/rea-0041-20261017/evidence/`：

|继承位置|继承合同|
|---|---|
|`upper-miio-b.md` supplemental / `upper-helpers-second-002.json` / `ev_d1e4f42de34b3fc8ff67a2423a4be7cd2727d4e7d19df4a5ddfd5c09cf12d3c8`|version改串与正式版本选择，不重计|
|同文件 / `upper-helpers-second-003.json` / `ev_b62850fb9162668ae6954b55ed52b3dde46af021b1f8a3bb8ad0fe14b1210c23`|九type与88B descriptor布局，不重计旧746B|
|`upper-complete.evidence.json#/records/245` / `ev_c22e8476e961b1745b154b77d021ebafc0cedf6d943f1eb10ef9c9b712f6e21b`|sub root调用实参、锁、正常成功拼接/计数接口|
|同JSON `/records/48` / `ev_221426fb577a1866be99a4825a47510530b45aec1e8d468aed90c0e391e9f036`|unsub根接口|
|`upper-miio-b.md` final / `ev_2d96f116544452cd74f7c729d9949dc4f2217491b7c30215f93840b2e76deb21`|`a018eddc`双wrapper分配/失败仅归还wrapper，不重做|
|[Q20](app-subscription-research-01-0041-20261025.md)|图布局、peer matcher `a0118b08`已验、删除/stale/count阶段；七body和76B matcher均未重读|

这些REA来源profile为 `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`。限reports地址查重仅见Q20、预调研的API定位，未见本七body合同；这是有限查重而非全历史负证明。

## 比较层：返回0的含义必须随调用点区分

以下D为descriptor基址，type是D+0的byte；数字字段是RV32整word。不依据type名字发明权限或运行语义。字符串使用既有 `a002db16` strcmp API，内部不展开。

`a01189b8(A,B)` 顺序比较word +0、+4。首次不同返回RV32模2^32的减法差；两word相同才strcmp(A+8,B+8)，字符串相同返回0，不同规范成-1。因此只可靠使用0/非0，不把它当有序比较器。`a01189f6` 同理依次比较word +0/+4/+8，字符串从+0xc。数字没有截成16bit，也没有因classifier边界而改变宽度。

`a0118a40(A,B)` **不是对称descriptor相等**。首参type决定覆盖规则，两个参数的位置不可交换；全部下面的字符串相同比较返回0，不同为-1。

|首参type|第二参可接受type及比较|
|---|---|
|9|B=5/6直接0，不读target；B=3/4比较A+0xc与B+0x10；其它有效type比较A+0xc与B+0xc|
|7|B=5直接0；B=1/7比较双方+0xc；B=3比较A+0xc与B+0x10；其它有效type不匹配|
|8|B=6直接0；B=2/8比较双方+0xc；B=4比较A+0xc与B+0x10；其它有效type不匹配|
|1/2|先要求同type，再调用`89b8(A+4,B+4)`：D+4/+8两word及D+0xc字符串|
|3/4|先要求同type，再调用`89f6(A+4,B+4)`：D+4/+8/+0xc三word及D+0x10字符串|
|5/6|先要求同type，再strcmp(A+4,B+4)，符号字符串，无target比较|

7/8不支持的第二type走type减法；普通不同type也返回非0 type差。9的入口并不另设type有效性校验，本合同仅覆盖classifier已接受的1..9；不能外推任意非法输入。原字锚点：`8a54`首参9门、`8a64`第二参5/6直零门、`8a8c/8ab6`首参7/8门、`8ad0/8ad4`type差及相等门、`8aec/8b02`两数字比较callee。

旧classifier的5/6不copy target保持成立；本次matcher确实不使用该target。构造完整复制88B不代表5/6取得新的target语义。root先零填D，故全局7/8/9比较所读D+4/+8是初始化零，而非新增数字组件。

## 身份查询与owned构造

`a0118c46(key8)` 从全局peer哨兵 `0x62fcab94` 遍历，调用 `a00501be(P+8,key8,8)` memcmp API，0返回首个P；无匹配返回NULL。是8个原始字节的身份，非十进制文本，也不比较sender或target。helper没有本地lock。

`a0118c20(H,target_ptr)` 遍历循环edge链，比较word(E+8)==target_ptr，有返回1，无返回0；不调用descriptor比较、不比较DID，也不添加/删除或计数。它提前读取next，假定有效循环链；本题不实验损坏图。两个helper都只是借用输入，未保存key/H参数。

|构造callee|成功对象与初始化|输入借用终点/返回|
|---|---|---|
|`a0118b8a(D)`|`a002fcc8(0x6c)`分配108B T；`a0024906(T,0,0x6c)`全零；`a000589c(T+8,D,0x58)`复制88B；T+0x64/+0x68均指T+0x64，T+0x60计数0|D仅copy时借用，不保存D指针；返回owned T。NULL直接返回NULL|
|`a0118bd6(key8)`|分配0x30=48B P并全零；复制8B至P+8；P+0x24/+0x28均指P+0x24，P+0x20计数0|key8仅copy时借用，不保存key8指针；返回owned P。NULL返回NULL|

两构造器没有插入全局链；+0/+4仍零。peer sender8、update_ts、lastseen在构造时仍零，成功root另写。topic descriptor是内嵌owned副本，非borrowed JSON/栈D；字节复制没有认证对象最终销毁时刻。malloc/zero/copy/memcmp/strcmp均止公开API。

## root成功路径的接口实例化（继承root，不新增root字节）

root持mutex `0x62fcaba8`。`6320`先DID8查P；已有P的edge扫描 `644a..6456` 取T，**a0=T+8、a1=输入D**调用`8a40`，0且T非空即跳`6468`刷新sender8/update_ts/lastseen，status0，不新增边。因此是“已存topic覆盖此次请求”，不是描述符严格相等。Q20已验matcher记为`8a40(输入D,T+8)`，本次只实例化其callee，不能把sub方向套入删除方向。

未命中后沿既有aggregate/重新lookup阶段；删除body不重读。全局topic搜索 `64e2..651a` **先要求T.type==D.type**；1/2/7/8/9调`89b8(T+0xc,D+4)`，3/4调`89f6(T+0xc,D+4)`，5/6调strcmp(T+0xc,D+4)。该搜索是同type identity，不用宽覆盖谓词；不能把peer覆盖命中与全局重用混称相等。

|正常图条件|成功root行为|
|---|---|
|P无、T无|peer数<4才构造T与P；双wrapper成功后分别挂边，计数各+1，P/T插入各全局链并增加全局计数；新T按type计数+1|
|P有、T无|P edge_count按有符号门<=9才构造T；双wrapper成功后挂边并各+1；T插全局链、topic/type计数+1；P沿用|
|P无、T有|peer数<4才构造P；双wrapper成功后挂边并各+1；仅P插全局链、peer数+1；T沿用|
|P有、T有|`6756`查T+0x64是否含P，`6764/677c`查P+0x24是否含T；双方已有则刷新成功，不重复加边；双方都无且P count<=9才分配双wrapper、各挂边计数+1，两个对象不重造|

指针门两侧不同一边为-1（仅继承已有错误接口，不实验异常图）。peer数门是unsigned count<=3可进入构造；每peer edge门是signed count<=9，这些位宽/比较区别只在正常小计数域用于配额，不外推溢出或损坏状态。旧pair allocator已给wrapper中保存对侧指针的owner合同；这里没有重做或重计allocator body。root全部锁内退出仍有Q20清理/dump前置副作用，不能把“重复命中不加边”外推为全局无变更。

## 断边、验证与停止

独立可使用的是有效输入的身份/覆盖、查找、owned节点构造和正常成功重用阶段；正式版本权限、完整manager最终寿命、root以外同步、投递/fanout、取消/异常图、旧allocation-failure缺陷均未展开。helper没有本地锁不能证明调用者无并发。使用标准容器/owned值即可重建本接口；不需要复制厂商allocator/strcmp/memcmp内部。

检查：七窗解码字节总和604且各窗无漏字；ROM长度；旧root必要实参/分支对接；报告相对引用与JSON结构；提交只含两个独占目录。作者检查不是独立验收。UTC开始 `2026-10-24 17:39:24`；结束/耗时与提交交付见同stem `session.json`，token不可得，不估造；没有已知排队/中断，工具读取含在墙钟内。未按名义4–7分故意等待。
