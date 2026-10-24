# F28：同Q首word初始化写点的非作者复核

**限定接受F27：在所取正常前缀到达0xa010e3fc且正常callee保存约定成立时，完整word请求7写入同Q+0，因此该写点`word(Q)&0x40=0`。** 不把这一写点结论升级为所有创建臂、完整成功返回或运行期发送中的mode不变式。语义纠正0、业务功能新增0；本次只增加独立核验。

2026-10-24；F11/10；复核者`/root/a56`，非F27作者；独占`re0041-f28` / `codex/re-0041-f28`，基线`bd457a6`。采用REA技能的留存优先流程，只读主仓作者报告/证据和已登记的必要原字段；未运行作者两脚本、未切换共享REA。仅写本报告及同名analysis，不提交/推送、不改共享表或主树，不执行固件、模型、指令、queue/FS接口、SIM/QEMU、构建、回放、设备或外部服务。

## 继承

- [F15](miio-queue-size-gap-f15-0041-20261024.md)及[F16独立复核](miio-queue-size-review-f16-0041-20261024.md)：creator的s1是同Q，正常setup/attach的对象桥与Q+0x18初值4直接继承，不重新取证。该size字段与本题Q+0首word不同。
- [F23](miio-queue-send-wait-gap-f23-0041-20261024.md)/[F24](miio-queue-send-wait-review-f24-0041-20261024.md)：状态使用端取`word(Q)&0x40`及caller范围纠正直接继承；global `0x62fc6034`是另一个对象字段，不能混为Q.mode。
- [F27](miio-queue-mode-init-gap-f27-0041-20261024.md)及其原路径analysis已在主仓整合。只复核同Q参数桥、所取前缀保存/门、公共写点及局部尾段边界。旧metadata只作定位：wrapper extent EID `ev_dc1299415c0f66d3c859a6e1a230a2d8a35db294e684cbeab5271de37edc8098`；lower extent EID `ev_1ae31bd9673fe052005725f2f591e68ab775f2c90180395a1d2879b61bedc772`，不以extent推整函数行为。

原件为主仓`roms/0041/ap01-1.0.2_0041.bin`，长度独立检查6,769,704B；继承SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算摘要。`file_offset=VA−0x9ffff000`，不套其他ROM或库版本。旧F15/F16对象桥profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`继承；本次无新REA生产ID。

## 复核与纠正

[review.py](../../analysis/miio-queue-mode-init-review-f28-0041-20261024/review.py)为独立检查源码，不导入作者脚本。Capstone 5.0.7/RV32+RVC逐指令校宽，另以独立S/B/J位域核SW及分支/调用目标。仅取creator16B、wrapper48B、lower前284B，共348B；57个稀疏锚点及65项检查PASS。不存在把下一条未知字节当NOP或把16/32位宽度混用的步骤。详细原字/偏移/宽度保留在本地忽略的`reverse/analysis/miio-queue-mode-init-review-f28-0041-20261024/review-evidence.json`。所有结论仍是静态字段与条件合同，并非服务执行或厂商库身份认证。

|独立锚点|接受内容及条件|
|---|---|
|a005f10a/f10e/f112/f114/f118|a4=s0−0x50(attrs)，a3=0x180，a2=7，a1=s0−0x40(name)，a0=s1=继承的Q。既有f122/f126实际调用目标及成功输出沿F15/F16，不重验|
|a01974e6/e8/ea/f6/fa|依次保存原a3/a4/a5/a6/a7于本地连续包；只给原a3=0x180、原a4=attrs赋已知值，后三者不补猜|
|a01974ec/f0/f2/f4..7502|a4=&原a3包，a5=0，a3=0，a2=7；wrapper在调用前未改a0/a1。独立JAL解算a0197502→a010e320，故实际下层实参为`(Q,name,7,0,&包,0)`|
|a0197506..750c|局部epilogue恢复frame并返回，不替换a0；不由此认证lower完整成功合同或包的正式variadic声明|
|a010e338/344/348|s5=a5=0；非空name门正常通过后，s3=Q、s6=7。所取前缀到写点没有显式重定义s3/s6；opaque调用正常保存这些callee-saved寄存器仍是前提|
|a010e35c、368..380|请求mask4参与attrs门；只保留所取正常前缀寄存器与数值条件，不把所有创建路线归入此路径。e392比较name首byte与0x2f，相等跳e43c，该目标未读|
|a010e3d2/d6、3da/de/e4/e8/ea|lookup-like opaque调用目标a01a3772；返回须非负。a4=5明确位于e3de，选中对象`LHU(+0xe)&0xf`须等于5才落入写块；负返回跳e440、类型不等跳e50a均不展开。类型/资源正式业务名不推断|
|a010e3ee/f0/f2/f4|以`(Q,0,0x18)`调用既有清零接口a0024906，不读body、不由24推Q完整容量或有效性|
|**a010e3fc：23a06901**|独立S-format`(opcode,f3,base,src,offset)=(0x23,2,19,22,0)`，即`SW s6,0(s3)`。在保存/正常返回前提下**word(Q)=7**，故此写点`7&0x40=0`；不是OR、byte写或Q+0x18写|
|a010e3f8/400/404|从本地−0x90重读所选对象，再写Q+0xc；s5=0跳e40e，跳过aux输出槽写。不同表达式不证明对象不别名|
|a010e40e/412/414/418/41c/420/434/43a|加载可选清理指针，非零调用a002e14e，清本地槽，恢复mstatus，置局部状态0返回。本地所取尾段未见直接重写Q首word，但opaque清理的别名副作用未知|

上述原字段与F27一致，**没有语义纠正**。本次对e3de常数5、调用/分支目标和显式寄存器连续性的独立检查加强可复核性，不算新业务结论。正常可达性、对象有效性以及callee保存约定不可删去；仅凭原件中存在写块不能证明实际执行到它。

## 真正新增

新业务恢复0、新字节语义0；限定接受F27的“真实参数桥→同Q正常公共SW初值7”合同。可复用最小结论是：继承同Q身份、name/attrs及所选lookup/type门成立、opaque调用正常保存s3/s6并返回、目的word可写时，到a010e3fc后该次完整word写的值为7。这里只数值命名，不命正式OS flag。

不以Q.size4推Q.mode，不把参数7本身当写入证明，不把不同指针来源当不别名证明；不增加全producer、实际调度/成功、存储容量或生命周期结论。

## 精确未闭与后继

未读a010e392→e43c的name/创建臂、e440及e50a等分支；530B extent中余246B仍未知。已读前284B不能覆盖全部name路径。完整成功返回时mode保持、optional cleanup对同Q的别名效果、后续writer/替换以及F23运行期实际mode均未证。所有lower helper/FS/allocator/driver body不在此次复核范围。

有种子后继仍是F27提出的**e392→e43c实际name臂到已定位公共写块的必要保存/汇合**，需管理窗口查重登记后开展；不得泛化为整FS恢复。若要跨到完整返回保持，应另限实际清理别名/写入边取证。

实际验证：独立65项PASS、JSON解析、引用主仓整合路径核对、独占改动/空白检查及`git diff --check`；生成JSON原路径忽略保留。未运行作者两脚本，无固件执行、提交或推送。交付后停止，供主窗口管理后继。
