# Q12 非作者复核：sysconfig 启动读取、默认与回写接合

2026-10-25；**限定接受作者 Q12，行为修正0、新增业务0。** 独立复核覆盖 reader `a00ab2e8..a00ab433`、默认 helper `a00a3a96..a00a3ab5`，必要继承 writer/算法/消费者接合；没有将底层文件持久性或完整启动接口标为已闭合。

分支 `codex/app-settings-review-01-20261025`，启动基线 `3a6602608e65ed7504bec657f829d463b504777d`。作者提交 `6abd0bbd749d8e34634bf819c294df50fb33b811`；先读作者 settings01 工作树的报告和同stem `verify.py`/`result.json`，**未执行作者脚本**。作者报告合并后入口：[研究报告](app-settings-research-01-0041-20261025.md)。主树统一流程3.1/3.2/5.1/7、rolling-management顶部与Q12认领行仅只读。

使用 [reverse-engineer-anything 技能](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。只做离线静态原字、已有真body与反汇编核对；未使用/切换共享REA目标，未执行固件、模型、SIM、QEMU、回放、构建、设备或网络，无异常绕过，无ROM/生产配置/分析器修改，无下级代理。仅写本报告及同stem analysis，不回退其他协作者。

## 独立来源与方法

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，映射 `offset=VA−0x9ffff000`。自写 [review.py](../../analysis/app-settings-review-01-0041-20261025/review.py) 从此原件完整解码 reader332B、默认32B、writer116B，不导入/运行作者代码；用已安装 Capstone5.0.7 RV32+RVC 独立离线解码，并核关键寄存器、store宽度、分支和调用目标及路径/mode原字符串。人工沿完整指令流核对日志前后的保存值与资源顺序。

既有 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-072.json` 与 `-071.json` 的 `structuredContent.normalized_result` 真body分别为332B/116B；保留 assembly 与原件解码地址边界逐条对应。Evidence ID分别为 `ev_85099f331255aab9e146bc35df48bcdbe3e38160b9802c06864c877f036f7d00`、`ev_cf4c97ae60f1edbe9156a19d0427799c7c068d79ed1d916e7d8cdc3dd61c3c58`。未新增REA Evidence ID。L03–06/M01–02作为已验前提继承，不重验算法、向量、FS实现或GUI消费者。

## 验收结果

|验收项|独立原字/控制流事实与结论|
|---|---|
|注册头与callback边|`ab2fa/302`构造`62fcb4ec`，`ab306/310/314/318`依次形成头`{8,0,0}`。callback参数为`a00a40c4`，a1=100，`ab31a/31e`目标`a01b2474`。只接受安装调用边，不认证成功、节点回收或100单位。|
|读取参数和返回|`ab332`open类调用后a0保存到s4；`ab348`零值走`ab418`诊断并汇入默认段。非零时`ab34c..356`传`(G,8,1,H)`；下一条`ab35a`直接call旧校验wrapper，无read返回判断、无读前清G。|
|校验位宽|`ab35e`为`LHU a6,6(s1)`；`ab364`为`BNE a0,a6`，比较完整32位返回a0和零扩展u16，而非先截低16位或比较read返回。wrapper结果范围沿M02继承，不重新求算法值。|
|非零H两分支归还顺序|匹配`ab382`设s5=1；不匹配`ab414`设s5=0并由`ab416`跳回`ab384`；共同`ab384/386`把s4传close。之后`ab38a`才按s5决定保留/默认。close返回不参与决策，静态调用不证明底层必然释放成功。|
|失败路径与默认宽度|open失败`ab432`跳`ab38e`；不匹配close后也到该段。`ab3a8`默认helper先`3aa0 SW zero,G`再`3aac SH 0x0164,G+4`，只写G+0..5；完整32B helper其余仅栈/恢复/ret，无G+6清零、无校验/通知/额外call。|
|独立writer与句柄|默认后`ab3ac`call旧writer；writer入口自身`ab28e`open同路径`wb`，新返回W非零才`ab2c2`算校验、`ab2ce SH`至G+6、`ab2dc`写8/1并`ab2e2`close。读H不传入，不复用；writer open失败时默认6B已写但G+6保留旧值。|
|启动发布与消费者|reader完整流没有setter或通知`a00a5bbe`；默认helper同样没有。writer/read/close结果都不构成init保存成功门。G+2/G+3默认0可接L03/L05既验byte消费者，沿用其与3比较的条件，不添加枚举/时长含义；匹配时保留read后live G。|

默认32B原字独立留存于结果的完整解码：`411122c60008b797fc6223ac070813074016938787092392e700324441018280`。特别保留一个细节：尾部诊断的G+4在`ab3be`是LBU，不据格式文字反推正式结构字段；本结论与作者“LBU/LHU取值”表述相容，无行为修正。

## 检查与断边

[result.json](../../analysis/app-settings-review-01-0041-20261025/result.json) 为独立检查PASS，含完整原字/解码、关键检查点、调用目标、旧assembly和Evidence ID。脚本验证原件身份、三个完整窗口无漏解码、关键指令与目标和路径原字符串；人工检查如上。源码及报告入本地commit；result.json为ignored中间产物，由父窗口停止后按同相对路径转存。JSON解析与`git diff --check`通过；没有用项目构建或执行目标代替静态复核。

断边沿作者保留：open/read/write/close实际返回、持久和释放保证；G完整字段及全体writer；subscriber所有权/注销/并发/旧节点回收；callback和安装内部及100单位；真实启动consumer执行和重启效果。算法/FS内部无必要新种子，不扩查。可独立使用的成果是启动调用层读/校验/默认/尝试回写合同，不能声称全系统持久化已认证。

工具UTC起点 `2026-10-24 17:02:47`；静态分析终点 `2026-10-24 17:04:33 UTC`，起点至此106秒；报告写入、格式及提交检查随后。无刻意等待；本地工具等待仅回包，无有效工时遥测。input/cached/output/reasoning token运行环境不可得，不估造。派发2–4分钟预测未作为延时或补量理由。
