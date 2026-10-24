# Q17：同 N 正常 ready 复位、probe 请求与重连许可

结论：恢复三 helper 与已验 monitor 的接合阶段，**作者交付待非作者复核**。ready helper 清计数并置标记；probe helper 解析目标并提交 `otn.ntp` 任务；许可 helper 读取独立全局状态，在15/20/30/50时返回1，阻止 state2 的重连请求。没有证明探测、重连、联网或云响应完成，完整应用接入接口仍有异步交接断边。

认领 Q-17，作者 `/root/app_network_research_03`；分支 `codex/app-network-research-03-20261025`，基线 `3d0d89d9d951aec94c5d5920e7002fbd039f2fb8`。仅本报告与同 stem analysis；主仓流程/认领表只读，不回退协作者，不推送。

## 输入、查重及证据

主仓 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/reverse/reports/ap01/reverse-design.md` §3.1/3.2/5.1/7、rolling-management 顶部及 Q17 为本轮流程。继承 [Q09](app-network-research-02-0041-20261025.md) 与 [独立复核03](app-network-review-03-0041-20261025.md) 的四计时门、caller 顺序和 state1 特例，不重做716 B计时门或5644 B monitor。

精确 caller 来源为主仓 `evidence/rea-0041-20261017/evidence/upper-complete.evidence.json#/records/89/normalized_result`，Evidence `ev_4150d456a78d9d2a6c00fda793101e8915ff107084a8356d31e91552e2b072de`，历史 profile `4825fb58a33a3e7d618557975b153b8318cf7e833d190ad16bcbf8bd441ae621`；`miio-recovered.md` §6/10 是旧合同背景。有限搜索 upper-miio-a/b、upper-routing 及较晚报告未找到三 helper 的已有 body 合同；旧 caller 中可见调用不算本轮新增。较晚 [OTA验证](qemu-ota-validation-20261017.md) 与 [RTC显示](qemu-rtc-display-20261017.md) 已确认 a0069356 安排4000ms reboot，本轮直接继承，不重读其26 B，不运行QEMU。

原件主仓 `roms/0041/ap01-1.0.2_0041.bin`，6769704 B；SHA256 沿既存 CATALOG `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，本轮只核长度，不冒称重算全 ROM 摘要。映射 offset=VA−`0x9ffff000`。新读范围仅 `a0067be6..a0067c1f` 58 B、`a0067c20..a0067c9f` 128 B、`a0195ce4..a0195e59` 374 B，共560 B，普通 RV32/RVC 指令完整解码。无新 REA Evidence ID、无共享 REA 切换，未读三 helper 的 callee body。

## 三 helper 合同

### ready 复位 a0067be6(N)

N=`0x62fca7f8`，M=`word(N)`。`bf2` 读 N+1e0 mutex，非空以 timeout=-1 调 a005f3d8；`bfe` 重读句柄，`c02` **32位写零 N+1d0**；重读句柄非空才调用 a01b3c8c 解锁。随后 `c10..c12` **16位写1 N+1d4，在解锁之后**，即使mutex为空也执行这两次字段写入。没有 free/转移 N，没有修改 M，没有显式建立返回值；caller 忽略 a0，不能把残留锁返回或句柄当布尔成功。

正常 state2+ready（M+1af0字节非零）下，caller 先给 N+1cc 加 elapsed，分别在N锁下清 N+1c0、N+184，经过旧一次性crash处理后 `e5a6/e5a8` 调本 helper，再 `e5b0` 调D。故复位发生在此轮D判断之前，并非D返回成功后才复位；也不能推成一次连接只写一次。N+1d4 的写宽度为16位，不能照后续caller读取方式臆改为32位清写。

### 独立状态许可 a0067c20()

此函数无业务参数，借用 **G=`0x62fcad78`**，它不是 N 或 M。读取 G+0 mutex，无空值分支地以-1调用锁API；在锁内读取 `u8(G+8)`。值<=30时按掩码 `0x40108000` 取该位，置位恰为15/20/30；值>30时只接受50。命中四值先调用 a0060810 取得日志参数、重读状态用于日志，然后设返回1；其余返回0。退出经 G+0 解锁，最后 `a0=s2`。函数不改 G+8、不复位N，不证明该外部状态来自哪个网络模块；日志 `miio_net_analyse`/offline reason 只是诊断文本，不能将这些值擅命名成联网状态枚举。

state2的C或D动作门触发后，`e768` 调许可函数，**返回0才**执行 `a01b3d12(N)`；1表示此处抑制请求。state1继承Q09例外：C=1直接请求，随后仍判断D，D=1可以再请求一次，两条路均不经本许可门。其它state继续沿已验Q09，不把本门推广成所有重连入口的统一前置条件。G对象/状态生产者属新owner，已回报主窗，未读其writer或私有实现。

### probe 请求 a0195ce4(M,N)

入口保留M/N，构造零初始化的3 B前缀区（fp−88）和16 B域名区（fp−84）。以 `(M,prefix)` 调 a01a4f5a，返回值不检查；随后以 `(prefix,3)` 调 a002de24，非零则调用格式API `(domain,16,"%s.%s",prefix,"ot.io.mi.com")`，零则复制默认域名最多15 B并在末字节补NUL。这里只认证调用形状与选择逻辑；前缀获取/格式函数均止API边，不认证其内部边界或数据来源所有权。

以 `(domain,&ip_word)` 调 a00b532c，返回非零走日志路径并返回-1；此路不提交任务。返回0才构造20 B局部描述 R（fp−74）：

| R偏移 | 宽度 | 输入来源 |
| --- | --- | --- |
| +0 | 4 B | 上述解析API输出的ip_word；字节序止API边 |
| +4 | 2 B | 8053 (`0x1f75`) |
| +6 | 2 B | 未显式初始化的padding，不赋业务含义 |
| +8 | 4 B | callback地址 `a0068a26` |
| +c | 4 B | 借用的原N |
| +10 | 4 B | 7000 (`0x1b58`)；单位未由本helper独立证明 |

另清零64 B局部区 fp−60，以 `(ip_word,buf64,64)` 调 a01adc6e，仅用于后续日志，返回不检查。最后 `e3c..e52` 调 **`a0119638(M+0x128,4,"otn.ntp",R,20,M+0xe8)`**，原样返回其a0。这里的4、20与M两个子区参数由寄存器确认；`M+128`沿旧初始化为mi_otn loop对象，不能将两个M子区当N资源。

正常返回/解析失败均经共同epilogue归还0x90 B栈帧，没有本helper可见的堆分配/free、socket句柄取得/close或N/M所有权转移。R、域名与日志buffer的本地寿命到返回结束；a0119638是否同步复制R、是否保存borrow、提交失败/正常完成如何销毁任务，以及callback实际行为均未在本题获证。7000是描述原值，不能仅凭数值宣称完整超时机制。caller在B=1时传 `(M,N)`，忽略本helper返回，因此DNS失败或提交错误也不直接改本轮monitor控制流；不能把B触发或0返回当探测完成。

## 检查、断边与交付

[verify.py](../../analysis/app-network-research-03-0041-20261025/verify.py) 仅读主仓ROM与record89，Capstone5.0.7静态解码560 B，20处原字断言及四许可值枚举通过，保留全部原字、逐指令、5条必要常量字符串和有限caller切片于 [verification.json](../../analysis/app-network-research-03-0041-20261025/verification.json)；[inspection.txt](../../analysis/app-network-research-03-0041-20261025/inspection.txt) 为静态输出。这是作者检查，不是独立验收。没有执行固件、模型、SIM/QEMU、回放、构建、设备或外网，没有改ROM/生产配置/分析器。

本阶段已回答ready复位时点/宽度、许可值及caller特例、probe输入/返回/局部栈回收和请求参数。完整probe生命周期仍止 `a0119638` 任务持有/回收及 `a0068a26` callback；G状态生产者、前缀获取实现、DNS/格式/socket内部、a01b3d12任务实际完成、N+18c全部writer均未展开。不要强认三API同owner，也不能将本阶段标完整联网接口闭合。若重建需证明异步R寿命，应先另行查旧合同并登记精确a0119638交接边。

首个可用UTC采样为2026-10-24T17:13:58.895Z，结束采样为2026-10-24T17:16:44.926Z（可见采样差166.031秒）；此前已有读取/建脚本，故采样差不冒充完整任务耗时。估计6–11分仅为派发预算，未作实测工时替身；工具等待/有效工时及token无可靠会话遥测，不编造。

tracked交付为本报告与verify.py。ignored清单恰为同stem analysis的verification.json、inspection.txt；父窗按同相对路径转存并逐字节或SHA256核对后再清理。作者本地commit交付后停止。
