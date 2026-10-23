# G12：fallback ADD 与 ready materializer 的独立复核

2026-10-24；基线 `f312a1a`；独立树/分支 `re0041-g12` / `codex/re-0041-g12`。**限定接受 G11 的字段、对象身份、通知 flag、rearm 与输出连接；纠正一处示意伪代码的重读原序。新增 ROM 功能 0，来源认证 0。** a010d7da 是已通知节点的记录 materializer，不能命名为直接 epoll_wait；静态登记成功不证明设备已 ready。

## 继承结论：已有出处→行为→局限→实际缺口

|出处|已有行为|本轮实际缺口|
|---|---|---|
|[G11 报告](display-ready-producer-g11-0041-20261024.md)及其 [evidence.json](../../analysis/display-ready-producer-g11-0041-20261024/evidence.json)|fallback 首次 ADD 安装节点，通知置 flag，collect 写记录并归队；与旧消费者条件连接|只独立核必要别名、实参、原编码、重读和归队，不重导 producer 或 initializer|
|[G09](display-ready-dispatch-g09-0041-20261024.md)、[G10](display-ready-review-g10-0041-20261024.md)|stride16 消费视图、同 fd bucket→watcher−14、callback(loop,watcher,mask)|消费/公共 poll/start/stop 全继承；不再次分析间接调用或业务 callback|
|[G07](display-alternate-work-g07-0041-20261023.md)、[G08](display-alternate-review-g08-0041-20261023.md)|显示 watcher/adapter、events2→mask4、stop/刷新/清 pending|显示链的实际触发、默认 display 身份仍不由本题认证|
|factory-test [retained-initializer.json](../../analysis/factory-test-0041-20261023/retained-initializer.json)，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`，profile `bcefdee5092076e55636e077b45523e203f4b870ae7b7ab547945ed1b8162279`|已留存登记/解析 backend/rearm/等待/collect/释放 file 借用和消费 body|旧原字节直接比对；G11/G12 不能把旧 initializer 记为新恢复|
|G11 对较晚 round3 和 G09 complete/SIM/ZIP 的复用记录|producer body 的新增与旧 initializer 引用已分层；SIM不认证ROM ABI|直接继承有界检索，不重复 ZIP、完整 bundle 或全 ROM 搜索|

本轮按 REA skill 使用已有留存与只读 ROM，未打开或切换活动 target、数据库或全局会话；没有新增目标运行。原始 ROM 从主树绝对路径只读访问。以下名称和字段是分析视图，非原源码或完整系统结构体。

## 本轮复核或纠正

|核查项|结论|定位与依据|
|---|---|---|
|caller data 身份|接受|c0e0/c0ec 以 frame−d0、长度16、填充值0初始化输入；c22c 写 events，c254 写 fd 到 frame−c8，即 record+8；c248 在提交前写 installed。c244/c2c4 重载相同 backend_fd；c2d0 解析，c2d4 保存返回对象到 frame−128，c2e4/c334 从同槽供 rearm/collect。整数 descriptor 没有被直接解释成 backend 指针|
|fallback ABI|接受|e106 取 submit_ctx+3c；e10a 产生−1；e110 不等跳离 fallback。e114/e116/e118 将 record/fd/op 置 a3/a2/a1，a0 仍为 backend_fd，e11a 调 a010e722。完整 ring/MOD 不在复核范围|
|ADD 节点和 callback 安装|接受|e73a/e740/e742 保存 op/fd/record；e750 保存解析对象；op1 门 e76e 保留。e792 的 backend+3c 经 e7cc/e7ce 进入取节点 helper。e7d2 保存 backend 于 node+2c；e7d4/e7d8→e7e0/e7e2 复制输入 +8/+c；e7dc 清 flag；e7ea 写独立 fd 字段+14。e7e4/e7e8/e7ee/e7f0 安装 events\|0x10000。e7f2/e7f6 算得 a0109b8e；e7fa/e7fc 写 node 自身到+20及 callback 到+24，e7fe 清 revents+1c|
|底层登记参数和成功门|接受|e802 构造 node+14，e806 保存同 node；e808/e80a/e80c 为 `(fd,node+14,1)`。e812 signed >=0 才到 e87c 链接，e88c 写 backend+24。失败清理沿 G11 原合同继承；不把失败节点解释为已登记|
|通知对象别名|接受|callback 的参数为嵌入 node+14 视图，参数+0c 正好是 node+20，其中已存 node 本身。9b8e 以 word 取该指针，9b90/9b92 只认证 byte(node+10)=1；此操作没有写 node+1c|
|materializer ABI/count/容量|接受|d7fc/d800/d802 保存 backend/out/capacity，d80c 置 count0，d844 返回 count。d874 为 signed `bge s3,s8,d8b4`；caller c338 传8，c33a out=frame−c0，c33e 调 collect。容量满仍处理节点，不是立即退出循环|
|record 输出宽度与重读|接受|d878/d87a 取 node.data 的高/低word；d87c 是 count<<4，d880 得 slot；d884/d886 写 slot+8/+c。d888 再读 node+1c，d88a 增 count。d88c 原字 `8b57db40` 的字段 `(opcode,funct3,top5,rd,base,index,shift)=(0b,5,8,15,22,13,0)`；现存只读模型 th.srw 是32位 indexed store、无 base 写回，故写 `word(out+offset)=events`。此窗口不写 slot+4|
|首次 revents 读取时点|**纠正示意原序**|d85e..d866 先脱链，d868 取 node+1c 到 a5，**d86a/d86e 才清 node+4/+0**，d872 判先前读出的 a5。G11 示意 `unlink //再清零; if(word(node+1c)...` 把首次读取画在清零之后。原汇编/evidence 留存正确，报告文字亦已有 d868/d888 两次读；本纠正只禁止将伪代码的清零/读顺序当实际指令序|
|容量满节点归队|接受|d874 到 d8b4，d8b4/d8b8/d8bc/d8be/d8c2/d8c4 把**同一节点**挂 backend+2c；d8c8→d8ac，d8ac/d8ae 使用预存 previous 继续至 d822。成功输出的 bit0x40000000 分支挂+34，其余归+2c。没有节点所有权转移到输出 record|
|rearm 顺序与负返回|接受|d760 从 backend+30 取+2c链尾；d764/d768 构造+2c/+24哨兵。d794 先清 flag、d798 清 revents，d79e/d7a2 再用 node+14 登记；d7a8 负值跳 d774 解锁/返回，尚未脱链；成功才 d7ac..d7ce 从旧链移到+24。不能把容量满节点解释为下次必然交付同一旧事件：rearm 会先清它的 revents|
|接旧消费者|接受，继承|c342 保存返回 count；G09/G10 已认证取 slot+8、events+0、stride16。producer 的 slot+8 **本质是登记 data 低word，仅本显示登记路径恰好为fd**；不是所有 backend 记录的 fd 语义。+4 未写不认证完整C/system ABI|

保留原序的局部表示仅需修正为：脱链邻接更新 → `first_revents=word(node+1c)` → 清 node 链接 → 检查 first_revents/容量 → 写 data64 → `events=word(node+1c)` → count增量 → indexed写 events。两次 revents 读取不能合并；这里没有主张读取之间发生过并发改变。

## 真正新增

仅新增独立审查和可重跑的编码核验，**新增功能 0**。字段与 producer 连接归 G11；旧消费合同归 G09/G10；旧完整 initializer 归 ev_dc0e；本轮不新增业务恢复或整库来源排除。

[review.py](../../analysis/display-producer-review-g12-0041-20261024/review.py) 使用主仓只读 ROM，115条 G11 留存 raw 逐条相同；旧 initializer 四个必要窗口共150B与 retained raw 相同；100项独立编码/字段/调用/别名检查通过。[review-result.json](../../analysis/display-producer-review-g12-0041-20261024/review-result.json) 只留检查索引和结果，不复制完整函数/raw/源码。I/S/B/JAL/压缩访存/mov及厂商字按原编码拆字段，不仅比较旧 asm 文本。厂商意义限现存只读模型对应规则，未改模型或认证完整ISA。

## 未闭的精确边

- **未核，继承**：底层 `(fd,node+14,1)` 登记正常返回以后，具体设备方法何时非零写 node+1c、是否实际调用 a0109b8e、是否形成显示 mask4；flag写者已知不等于 revents写者已知。
- **未核，范围外**：完整 MOD/DELETE、非fallback ring后端、池分配/析构、并发/重入、fd复用、恰好一次callback及退出后drain；公共poll/start/stop与旧业务不重做。
- **未核，继承**：a009d382副作用、默认display运行时同一性、精确libuv/NuttX版本及整库来源。

一个后继闭包若继续研究真实 ready，只追已安装 node+14 到**一个目标设备 poll 方法**的 revents 写者/通知接入；不重做已接受 producer 或旧消费者。若没有可定位设备种子，应维持此精确断边。

静态核验之外未执行固件、SIM、构建、历史回放、设备或网络；未修改主树、共享索引、生产代码、ROM、配置或模型，只写本任务独占报告和analysis。
