# A76：固定路径格式的引擎连接（0041）

认领 J08/12，作者 `/root/g23`，独占 `re0041-a76`／`codex/re-0041-a76`，固定基线 `bd457a6`。**已证字面 `/` 的真实callback调用、fmt续读、正常返回本地计数及固定s的部分分支；`%s`实际取参／输出未闭。** 最后已证分支为 `0xa01a3abe→0xa01a3ae0`，按用户最新收尾指令不读取尚未授权的后继。范围仅固定 ROM `/%s` 的必要控制流与间接调用端；三个callback本体由A78独占。本报告是静态推导，不是运行或输出实验。

## 1. 继承结论

继承 [A74](reader-driver-format-gap-a74-0041-20261024.md) 适配结果（本题开始时尚待复核，现已由 [A75](reader-driver-format-review-a75-0041-20261024.md) 限定接受）：原路径 mode2 caller 经 42B wrapper、`0xa0053252`、旧 `0xa002d770` 把 `S,0,0,fmt,va` 交给 `0xa01a37d2`。fmt 是已验 ROM `/%s\0`，va 首 word 是 suffix 指针；count256 时 S 的六个 word 为 `{0,0xa002b536,0xa002b4d8,0xa002af2e,buf,255}`。适配先 SB0 到 buf，正常返回透传引擎 a0。本题不重读适配层、literal、open/close 或三个函数指针目标。

继承的输出边界保持：初始清零不证明最终 NUL、`/%s` 家族意图不证明实际输出。候选正常域为有效、分离、NUL 终止 suffix 短路径/count256；不执行具体输入或指令模型，不根据标准 printf 名补字节。

## 2. 本轮复核或纠正

旧资料查重：主仓 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json` functions5997 的 `0xa01a37d2` 无 dossiers、historical_dossier 或 historical_contracts。extent EID `ev_2ef71c21882936bf466e0db84b206e01d8bbb3b3e0343c9e8fed1cac5674caca` 只给 `[0xa01a37d2,0xa01a40f6)` 和 `[0xa01a410c,0xa01a4430)`，总3144B；direct-call EID `ev_f187bdf2006f155ea0d84318bf9db0b86db2f47bb49daf66f0e0501025fcb75c` 仅13个目标。索引 profile 为 `b6368dd18431e8113aa5026c713d41e648ab0f6ddd9421ff6c4a49e23b3cd2f3`／`f71eaf7d63ce1b1fa1671fe1932e6a44e275d3716b51411a6bb6af26d7663a44`，不是引擎语义合同。

父级 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json` 精确 procedure 搜索没有该函数 record。主仓 reports 和 analysis 中 Markdown／contract.json 的 `a01a37d2`／入口邻接精确搜索只见 A74 及管理记录，无固定 format body 合同。此有限查重不证明其他载体、间接调用或未定义函数不存在。

原件只读主仓 `roms/0041/ap01-1.0.2_0041.bin`，继承长度6,769,704B及 SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`；file offset=VA−0x9ffff000，不重算hash、不混0031。新窗口使用 Capstone5.0.7 RV32/RVC静态解码，关键I/S/B/J和压缩字段另拆位核定；无新REA生产EID/profile，不更改或执行私有ISA模型，不开新数据库/切换共享REA。未见旧语义纠正；新增是有界原字段和真实控制/实参连接，非完整formatter或厂商来源认证。

## 3. 真正新增

主窗登记首窗 `[0xa01a37d2,0xa01a3852)` 128B 后，只读该原字段。入口保存 s0..s11/ra，帧160B；`37f4 3a8b` 将入 a4（va）存 s6，`37fe aa84` 将入 a0（S）存 s1，`3814 0149` 将 s2清零。a3 保持 fmt。三个固定地址的双 word 在入口搬到局部：`0xa01c11e8/+4`、`0xa0637698/+4`、`0xa0637690/+4`，仅记录搬运，不读其 ROM 数据或假设类型。

`3832 83c90600` 为 `LBU s3,0(a3)`；`3836 e38d093c` 以零相等跳到 `0xa01a4410`，`383a 93075002` 置 a5=0x25，`383e 638df900` 相等跳 `0xa01a3858`。因此继承的首字节0x2f走非百分号字面分支：`3842 93871600` 把 fmt+1 置 a5，`3846 232af4f8` 保存到 s0−0x6c，`384a 0509` 本地 s2加1；`384c dc40` 读 `word(S+4)` 到 a5，`384e ce85` 把 U8 字符置 a1，`3850 2685` 把 S 置 a0。首窗到此结束，尚未把紧接未知字称为已验 indirect call。

续窗 `[0xa01a3852,0xa01a38c0)` 110B 已登记：`3852 8297` 为 `C.JALR a5`，故真实间接实参为 `S+4(S,47)`；`3854 6f00503b` 无条件跳 `0xa01a4408`。这才把前窗的指针加载与调用连起来，尚不借此认证该目标写了字符。

字面分支先加 s2 再调用，调用后不测试回传 a0而直接续读fmt；不能把该引擎计数理解为按 callback 的实际选中n累加。

百分号入口 `3858 83c91600` 读 fmt 后一 U8 到 s3，`385c/3860` 保存 fmt+2 到 s0−0x6c，`3864 e383f9fe` 若该字节仍为0x25则跳 `384a` 重用字面调用。固定 `%s` 中 s3=0x73，不走该 equality；`3872/74/76` 把 s4/s5/s10 清零。`38b4 6367a719` 的 unsigned `0x3f<s10` 为假，`38b8 638ab916` 的 s3==0x2b 为假，`38bc 63e43503` 的 unsigned 0x2b<s3 为真，下一实际地址 `0xa01a38e4`。其它 flag/数字/宽度分支只记跳过，不恢复任意格式。

这是寄存器／原字段推导，固定字节由旧 literal 继承，不是运行输入；s2加1目前只称引擎本地计数，与 stream.word0 分离，不预设最终 return 或有效写出数。独立 I/S/B/J 与压缩字段检查当前37项通过。

随后登记的 `[0xa01a38e4,0xa01a3950)`／`[0xa01a4408,0xa01a4430)` 两窗，共148B，核得固定 s3=0x73 在 `38e4 6389c915` 不等 t3=0x2d，`38e8 e390d9ff` 不等 t4=0x30，实际跳 **`0xa01a38c8`**。本轮没有把先前静态跳过区域当可任意读；已另报该28B连接。Capstone 对获准窗在 `0xa01a38f4` 停解；它处于本次固定's'不走的旁支，记录停点，不填未知、不从中间半字继续或解释旁支。

续读点 `4408 832644f9` 把 s0−0x6c 保存的下一 fmt 指针重读到 a3，`440c 6ff06fc2` 跳 `3832`。零 fmt 的 `3836` 直接到 `4410` 恢复保存寄存器；`4428 4a85` 把 **s2复制到 a0**，再恢复原 s2／sp并 RET（`442e 8280`）。故正常终止返回的是引擎本地计数 word，结束段没有间接 callback、额外 NUL 写或 S.word0 读取；这不把 s2 与 S.word0 自动等同。

另条件继承 [A78](reader-driver-format-stream-a78-0041-20261024.md) 合同（现已由 [A79](reader-driver-format-stream-review-a79-0041-20261024.md) 限定接受）：S+4目标包装单byte，S+8目标在正常有效域按剩余容量夹取、正数时copy后重读count/buf、更新count再补NUL、返回所选n；S+c目标返回0且自身无stream写。未重读三个本体或运行作者脚本；A78/A79仍把任意所选n的copy效果与更深持有保持界面前提。不能据本题已验S+4调用把这些条件去掉。当前43项字段检查通过，新读累计386B，其中一窗旁支停解不声称全覆盖。

登记后续28B、96B及50B窗口后，固定s的剩余已证控制如下。它们属于本轮真实新增，不是运行路径观测：

| 地址／原字 | 固定s的实际门 |
| --- | --- |
| `38c8 938709fd`／`38cc 93f7f70f`／`38d0 63e4f31a` | `(s3−0x30)&255=0x43`；unsigned `9<0x43`→`0xa01a3a78` |
| `3a78 6398a902` | s3不等a0=0x2a→`0xa01a3aa8` |
| `3aa8 e39f19f9` | s3不等a7=0x2e→`0xa01a3a46` |
| `3a4a 638cf906`／`3a4e 638ab907` | 不等0x7a、不等s11=0x74 |
| `3a52 63949907` | 不等s9=0x6a→`0xa01a3aba` |
| `3aba 93f7f90d`／`3abe 63918703` | `s3&0xdf=0x53`，不等s8=0x4c→**`0xa01a3ae0`** |

va仅在入口保存到s6；在这些已选中片段中没有读取／推进va包或suffix，也未到字符串输出调用端。s4/s5/s10清零不靠标准格式器惯例重命名。正常结束返回a0=s2不证明固定`/%s`已能到达该结束段，callback回返与callee-saved/对象有效期条件不能略去。

全部获准半开窗口为 `[0xa01a37d2,0xa01a3852)`128B、`[0xa01a3852,0xa01a38c0)`110B、`[0xa01a38e4,0xa01a3950)`108B、`[0xa01a4408,0xa01a4430)`40B、`[0xa01a38c8,0xa01a38e4)`28B、`[0xa01a3a78,0xa01a3ad8)`96B、`[0xa01a3a46,0xa01a3a78)`50B，总560B。新增的旁支停解点 `0xa01a38dc`、`0xa01a3a80`、`0xa01a3ad2`、`0xa01a3a5e` 与此前 `0xa01a38f4` 均保留原4B前缀，不填NOP、不执行/修模型、不猜连续覆盖。`0xa01a3aa8` 是已核direct branch真目标，且在授权窗内，故从该目标解码，不是跳过未知字任意续接。

所有权：所选中引擎片段将S/va/fmt保存在本栈或callee-saved寄存器，以S和字符值调用callback；没有在这些片段见持久参数地址发布或分配/释放。不能外推未读case/copy全无更深持有或副作用；S/buf/va/suffix须在相应服务期间有效并无破坏性别名或不兼容变化，不由表达式不同证明分离。另只读[A80](reader-driver-format-copy-gap-a80-0041-20261024.md)作者有限n1合同，未重读copy body或扩到任意字符串长度。

最小机器合同见 [contract.json](../../analysis/reader-driver-format-engine-gap-a76-0041-20261024/contract.json)，静态检查源码 [check.py](../../analysis/reader-driver-format-engine-gap-a76-0041-20261024/check.py)，本地忽略 [evidence.json](../../analysis/reader-driver-format-engine-gap-a76-0041-20261024/evidence.json) 保留原字、分支字段、授权窗口及旁支停解前缀。最终59项静态字段检查通过；本题新业务／厂商来源认证0，新增仅上述有界真实连接。不是非作者验收。

## 4. 未闭精确边与停止

最后精确断边为 **`0xa01a3abe→0xa01a3ae0`**。此前申请的最小后继 `[0xa01a3ae0,0xa01a3b40)`96B尚未授权且没有读取；按用户“当前分发任务结束后不再派新任务”指令，本题不再扩展。若日后重新授权，有种子的后继应只核该固定s实际后继，定位va读取／推进与字符串callback实参，再按真实连接登记，不整switch/engine或新helper。

仍未知：suffix指针何时读出、va如何推进，字符串分支长度／精度／返回宽度，S+8/+c是否及何时以何参数调用，实际路径字节、最终NUL、截断与suffix借用结束。已证首literal调用和正常结束a0=s2不闭合整条`/%s`；没有“短有效输入已运行通过”的结论。copy有限n1合同不扩成任意length，正常返回word不补标准printf含义。

交付检查：59项字段检查、JSON解析、报告引用解析、`git diff --check`及生成物忽略保留通过。只写本报告及同名analysis，无共享表／生产修改、固件/指令/模型/host格式输入枚举/旧脚本执行、SIM/QEMU/构建/IO、下级agent、提交或推送。按最新要求保存成果并停止，不接新任务。
