# A52：reader消费接口及缓存持有独立复核

限定接受A50，无语义纠正，新增功能0。非零mode reader按同一R前缀进入 `a008b888`，D+14回调实际为 `(D,H,dst,want,&count)`，D+1c定位回调实际为 `(D,H,position,0)`；普通小读按配置k懒申请B并保存在C+c，回调后重读C，随后借既有W→O复制持有，接A47/A49条件归还。计数、状态返回分别保留，跨缓存copy的低31位掩码不能省略。具体D、真实mode1照片及实际I/O成功仍未知。

基线 `ef05f6829664dd56c7224fd3f8dc0227bfb32501`，独立树/分支 `re0041-a52` / `codex/re-0041-a52`，未参与A50生产。使用 reverse-engineer-anything 技能，只读主仓ROM、已有证据与规则文本；没有打开共享REA target/数据库，没有执行固件、模型、SIM、构建、历史回放、设备或外网，没有下级agent。只写本报告和独占analysis，不改共享/主树/生产ROM配置模型，不撤销其他agent改动。R/D/H/C/B等为分析命名，不认证原typedef、FILE*或文件系统。

## 继承结论：已有 → 行为 → 局限 → 精确缺口

|已有出处|行为及局限|本轮处理|
|---|---|---|
|[A50](photo-reader-consumer-a50-0041-20261024.md)及evidence.json|read/seek实参、普通缓存字段、懒申请/重读、计数与既有归还连接已恢复；来源/实例未知|只复核该新增消费合同，不重导544B函数或展开所有失败分支|
|[A47](photo-reader-mode-a47-0041-20261024.md)、[A49](photo-reader-mode-review-a49-0041-20261024.md)|分类1→mode1 W；R前三word H/D/C；D+10回调(D,H)，回调后重读条件free(C+c)/free(C)，清前三word。特殊配置−1与普通B责任不同|直接继承构造/归还，保留实际D未证、清槽条件和回调后重读；本轮不重新命名fclose或重核driver选择|
|[A37](photo-decoder-owner-a37-0041-20261024.md)/[A39](photo-decoder-review-a39-0041-20261024.md)、[A41](photo-decoder-destroy-a41-0041-20261024.md)/[A42](photo-destroy-review-a42-0041-20261024.md)|copy(O,W,664)、owner持有与正常旧O替换最终归还已有|同一个C+c把B连接到已有复制/条件归还，不把浅复制误作B内容复制或新申请|
|A33/A35、照片round3、最终ZIP/SIM合同|默认五ROM照片mode0借用及上层轮转已有|继承，不凭通用非零mode臂认定真实五照片执行文件读取；不重做资源、PNG/压缩或解码|
|A50引用weather-calendar-complete `#/evidence/30`与`/1`，whole-ROM extent `ev_0cf7b05aecf9153467edba3b567024c23acd5f53b2e1392c883286c7ca4197e6`、direct-call `ev_86c95e3108349c7bdea188fd5ad92903355d6c757f0c400f887554f4a20abae3`|旧caller/边界仅定位；stdout截断不证明callee语义。A50已核complete内部并留搜索边界|继承复用记录，不重查整套complete/ZIP或全ROM。没有把旧负搜索等同历史从未恢复|

本轮精确缺口仅为这些消费/持有/宽度合同的独立技术接受。可靠旧行为直接引用；旧反编译/extent作定位；SIM/照片替代不作ROM ABI证据；只补必要原字节/字段检查。

## 本轮复核或纠正：逐项接受与未核

原件为主仓 `roms/0041/ap01-1.0.2_0041.bin`，定位 `offset=VA-0x9ffff000`。对A50的124条留存raw逐条比对原件，不运行旧验证器或重新输出整callee；独立拆压缩访存/移动、普通load/store/JAL和厂商字段。见 [review-result.json](../../analysis/photo-reader-consumer-review-a52-0041-20261024/review-result.json)。

|A50主张|本轮原字节/字段依据|判定|
|---|---|---|
|同R进入消费callee|`a010a5e2:03470501` 独立确认为LBU a4,10(a0)，不是单bit mode；a5e8令a3=0；a5ea直接JAL解出a008b888。b8a0..a6保存R/dst/want/out_count至s1/s6/s2/s5|接受正常非零mode接入；没有改为只传H，wrapper的NULL count不消除内部count|
|D+14五参read|b8ae取D=R+4；b8b8及ba5a等压缩LW独立确认fn=D+14；ba94..9e普通直读准备a0=D、a1=R+0、a2=dst、a3=want、a4=s0−38后间接call。填充路径ba52..64将a2=B、a3=k、a4=s0−34|接受read(D,H,dst,want,&count)，D是首参、H是次参；具体函数/结果协议未核|
|D+1c四参定位|b934/b936重取D/H，b93a从D+1c取fn，a2=旧cache_end+1、a3=0；b9d4..dc未命中同槽用saved logical_position|接受seek解释及原四参；没有把第4参数命名标准枚举。返回未用于这里后续read门，不补seek成功检查|
|普通C字段与命中|b8d4取C=R+8；独立LW字段确认C+8为位置、C+c为B；start/end与unsigned比较按A50原窗口。b8fe:de95把B加到已化简position−start的源偏移；命中copy后按实际量更新C+8|接受C+0/+4/+8/+c布局，范围尾端包含；32位加减/比较，不升为64位文件位置或承诺全部范围|
|B懒申请与复用|b9f6先检查保存B，非零到填充；b9fa取C，b9fe给a0=k，ba00直接JAL独立解出a008aea0，ba04 SW返回到C+c，ba08/ba0a重取C及B|接受普通k非零且非ffffffff的小读路径；want>k直读dst，不申请B。已有B复用，不另建所有权根|
|回调后C重读与缓存范围|ba66重新LW C；ba6c SW saved_position至C+0；ba70再取C；ba72读filled word，ba78..80更新end=start+filled−1；copy取min(filled,want)|接受原重读/写序。callback返回状态仍保存，不能以单个旧C快照替代原程序|
|count与status独立|b8cc先SW清局部word；对外count也SW。补核b960:2a8a为保存a0状态到s4；b996:5285为返回s4到a0。缓存命中b920置状态0，b978..980可选写实际count|接受返回status而非got；count/filled/out_count均32位独立通道，wrapper传NULL只省外部写入|
|正常游标更新|b974仅status==0回b91a重取C，读C+8并加局部实际消费量，再写C+8；状态非0不沿此成功汇合更新|接受这一正常成功原门，不宣称全部失败/短读协议或回调输入合同完整|
|厂商计数四字|b96c LE word42f9198b、b9c6 40fc160b、b9ca 3c06360b、ba86 40f9160b独立拆opcode/funct/rd/rs1/rs2，与既有规则逐段相等|接受mvnez总量夹取、mveqz取小值及extu低31位。不能把跨缓存copy的`&7fffffff`改写成纯min或计数高位始终无效|
|C/B到W/O持有及归还|A47/A49和A37/A39已核初读后copy(O,W,664)，含当时C指针；A47/A49普通配置归还同C+c再C，外层另free(O)|接受继承接线，浅复制不复制B数据，不保留栈W地址。read不自行free B/C，不转移D/H所有权；out-count局部不持久保存在R/C|
|具体D与真实mode1|只有通用静态分支及槽接口，没有实例/执行证据|未核，保持默认五照片mode0合同；不认证FILE*、具体driver或读取成功|

厂商规则来源为主仓 `evidence/rea-0041-20261017/ghidra/Ghidra/Processors/RISCV/data/languages/ap01thead2.sinc` 的mveqz/mvnez/extu短规则。本轮仅读文本逐段核对，不运行/修改模型，不提升为新厂商硬件规格。b9ca取bits30..0，copy长度与32位总量/position公式须分别保留。

正常必要表达（非原源码）：`R={H,D,C}; status=read(D,H,dst,want,&got)`；需缓存小读且B为空时 `B=allocate(k); C->B=B`，填充 `read(D,H,B,k,&filled)` 后重读C、保存范围、copy所需量；status为0才在原汇合路径更新逻辑position，按需输出got；最终返回status。构造后的W/O持有同C，归还合同由A47/A49决定。该表达不覆盖特殊配置ffffffff、全部I/O失败或新对象生命周期。

## 真正新增

新增功能0、ISA规则0、模型变更0、完整函数导出0、来源认证/整库排除0。124条旧raw与原件比较、166项字段/规则检查及6B稀疏锚点均为独立复核，不能重复记作新功能。三条新增锚点仅分别确认命中源加B、callback状态保存及返回状态；未新增解码/文件系统/全部失败恢复。

## 未闭精确边、后继与验证

仍未知：具体D及D+14/+1c目标、read/seek结果协议、H类型、真实类型1照片实例、特殊配置ffffffff、全部失败臂/heap复用/最终DELETE。来源映射由另一路A54处理，本轮不接管；静态对象字段接线不等于运行成功或实测缓存命中。

单一后继闭包：只有出现实际source类型1→具体D绑定的原始种子时，再核该实例D+14/+1c真实目标及正常结果协议；当前无实例种子，不扩大全driver/文件系统或与A54重复来源题，不自行接题。

[review.py](../../analysis/photo-reader-consumer-review-a52-0041-20261024/review.py)使用Python标准库静态核验通过：124条留存raw、13处压缩LW字段、10处普通访存字段、11处移动、4个JAL目标及4个厂商字字段，共166项；旧短规则文本一致，新增3个2B锚点。没有执行A50验证器、固件、规则模型或输入回放。报告相对链接、JSON及 `git diff --cached --check`通过。结论仅技术接受A50正常消费/持有范围，不声称全部reader/照片模块闭包。
