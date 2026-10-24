# F30：name首byte斜杠分支回到既验前缀

**a010e392→e43c这条正常分支只有4B：先将a3加1，再跳回旧e38e重新读取当前byte。匹配`0x2f`则重复，不匹配才落到旧e396；这段不改s3=同Q或s6=请求7，没有新callee/返回。** 若随后仍满足F27/F28的lookup/type/正常保存及clear调用条件，已验e3fc写点仍写7；并不是所有name或全部成功返回均保持7的证明。

2026-10-24；F11/11，任务F30，`/root/a56`；独占`re0041-f30` / `codex/re-0041-f30`，基线`bd457a6`。采用REA留存优先流程，先读取主仓既验参数/前缀/metadata，随后仅核准许范围内真实正常回边。无目标/固件/指令/模型执行、host字符串输入、旧脚本、SIM/QEMU、构建、回放、open/设备或外部服务；不切换共享REA、不读新FS/创建/allocator/driver正文、不改生产/主树/共享表，无下级agent、提交推送。

## 继承

|出处|既有合同与此次缺口|
|---|---|
|[F27](miio-queue-mode-init-gap-f27-0041-20261024.md)/[F28独立接受](miio-queue-mode-init-review-f28-0041-20261024.md)|同Q参数到lower `(Q,name,7,0,&包,0)`；s3=Q/s6=7；此前只取530B extent的前284B，明确e392→e43c未读。本题只补该目标的实际汇合|
|F28本地原路径`reverse/analysis/miio-queue-mode-init-review-f28-0041-20261024/review-evidence.json`|复用六个稀疏锚点：e344/e348保存同Q/请求，e38a常数47、e38e LBU、e392 BEQ、e3fc SW。没有重读前缀ROM或运行F27/F28脚本|
|F27/F28正常公共块|lookup非负及所选对象低4位=5后clear(Q,0,0x18)，e3fc完整SW请求；可选cleanup/别名与完整返回保持未知，全部继承，不新读helper|
|旧whole-ROM metadata|a010e320 extent530B、EID `ev_1ae31bd9673fe052005725f2f591e68ab775f2c90180395a1d2879b61bedc772`仅定位。本轮不将剩余窗口线性字节当全部name/创建路径或完整CFG|

0041原件沿主仓`roms/0041/ap01-1.0.2_0041.bin`，长度6,769,704B独立检查；SHA256继承`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，不重算摘要；映射offset=VA−0x9ffff000，不套其他ROM/SIM。新字段没有新REA生产ID/profile；旧参数和来源按F27/F28保留。

## 复核与纠正

F27/F28无语义纠正；它们当时明确保留未读目标，本次补上**极短的真实回边**，不反写冻结报告。首轮探查实际取`[e43c,e48c)`80B，Capstone5.0.7/RV32+RVC显示入口两条已在4B内回旧前缀。后续76B虽然已在获准范围内被读取，但不纳入本正常分支语义、未沿其中调用展开，也不继续取余窗口；本报告如实保留读取边界，不冒称实际仅读过4B。

[check.py](../../analysis/miio-queue-mode-name-branch-f30-0041-20261024/check.py)仅复核必要4B原件和六条旧稀疏行，以标准库独立拆C.ADDI、C.J及旧BEQ目标，**14项PASS**。没有从任意中间半word拼指令、没有NOP未知字或手填provider边界。新两指令均为16位、无厂商编码。生成`evidence.json`在本地原路径忽略保留，含实际首次80B读取/仅4B语义使用的区别。

## 真正新增

|原地址/LE原字|字段、控制及参数效果|
|---|---|
|a010e43c `8506`|C.ADDI rd=a3、signed立即数1；a3=low32(a3+1)，不是更改s3/s6或写Q|
|a010e43e `81bf`|C.J signed位移−0xb0，真实目标**a010e38e**。不是落入e440创建/失败代码，也不是函数返回|
|旧a010e38e `03c70600`|LBU a4,0(a3)，重新读移动后的cursor；该读取以及有效字节是既验前缀/本次组合的条件|
|旧a010e392 `6305f70a`|BEQ a4,a5到e43c，a5由旧e38a设0x2f；否则4B fallthrough为e396。因此可重复跳过当前连续斜杠byte，退出后进入旧前缀后续路线|
|同Q/请求连接|该局部环只定义a3/a4并分支，s3/s6不变，无call保存额外前提。离开环以后仍须继承opaque调用正常callee-saved约定、lookup/type门和有效Q等条件，才接e3fc写点|

局部表达（分析表达而非原源码/输入实验）：

```c
// 仅已从e392相等门进入的分支
a3 = low32(a3 + 1);          // e43c
goto old_e38e;              // e43e
// old_e38e: a4 = U8(*a3);
// old_e392: if (a4 == 0x2f) goto e43c; else goto old_e396;
```

新增精确范围是**这4B及到既验name门的回环/同Q请求连续性**；新业务功能0、库/ISA认证0。没有恢复创建成功臂、permission或失败处理，也没有从请求flags推动态mode。不能由cursor最终能到非斜杠byte推lookup成功、有效路径、实际选择该name或Q容量/生命周期。

在旧正常公共块的既有条件全部成立时，这一回环没有引入新s6定义，因此e3fc仍以7作SW源；只能据此说该写点word(Q)&0x40=0。若后续走其他门/返回，则不在这一组合合同内，结果不强制7。最小条件合同见[contract.json](../../analysis/miio-queue-mode-name-branch-f30-0041-20261024/contract.json)。

## 精确未闭与后继

本次遇到已验汇合即停。e440及后续创建/permission/失败臂的语义、所有成功返回保持、optional cleanup别名、后续writer/替换和F23实际运行mode仍未知。本轮不解释首探窗口后76B所见调用，未读新callee正文；它们不能由线性位置或callee名字补正常含义。

若以后要覆盖更多正常创建结果，精确种子仍是**旧lookup负门e3d6→e440**在同Q/请求7条件下的真实正常创建汇合或返回；需管理查重登记后仅取必要caller字段，不读下层FS/allocator/driver。当前任务不要求完整创建/成功返回闭包，不自行补题或重复同头扫描。

实际检查14项PASS、JSON解析、主仓后备引用解析、独占status/证据忽略与`git diff --check`通过。无原件执行或输入枚举；成果未提交推送，交付后停止供主窗整合/补位。
