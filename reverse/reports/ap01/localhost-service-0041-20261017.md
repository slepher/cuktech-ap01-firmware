# 0041 localhost监听服务核对

2026-10-17。用户要求确认ROM内localhost服务。仅离线读取0041原件及已留存Ghidra证据，不连接设备、不扫描端口、不发送ROM到分析提供方。原件SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。

## 结论

该监听是米家miio SDK的OT agent本地TCP通信入口，绑定 **127.0.0.1:54322**。监听创建、accept、poll和接收分派均有机器码/原件导出证据。接收链按JSON对象边界处理消息并提取`method`，再按`local.`前缀分派；因此应将其理解为米家内部RPC/消息通道，而非可直接挂接Bridge路由的HTTP服务器。未证明完整JSON-RPC 2.0标准兼容，也未证明所有连接都使用未加密消息。

## 证据链

- `0xa0066296`为miio_client初始化/事件循环入口；已留存Ghidra导出的日志关联`miio_sdk/miio_instance/client/miio_client.c`、`miio_client_func`及`OT agent listen fd`。
- `0xa0066558..655e`以`(2,1,0)`调用`0xa00268c4`创建IPv4流套接字。
- `0xa00666e6..6704`构造sockaddr字节`02 00 d4 32 7f 00 00 01`，调用bind入口`0xa003f446`。端口字节`d4 32`按网络字节序为54322；地址是设备自身loopback。
- `0xa0066748/674c`调用listen封装`0xa01a18ce`。留存事件循环导出显示监听FD接受连接后进入poll管理；已有客户端读事件分派至`0xa01b82e8`，不能只依据server字符串得出结论。
- `0xa01b82e8`接收处理器申请`0x800`即2048字节工作缓冲，在`0xa01b83aa`调用接收入口`0xa010d6f6`。这是单条缓冲申请，不能作为整个服务RAM成本。
- `0xa01b8644..86fa`出现引号`0x22`、反斜杠`0x5c`、左/右花括号`0x7b/0x7d`及嵌套计数/字符串转义分支，表明接收流中拆分JSON对象，而非HTTP请求行/头解析。
- `0xa01b8390`得到`method`键地址`0xa056c058`。`0xa01b878e`调用解析辅助`0xa0060cac`；`0xa01b87ba`调用字符串字段提取辅助`0xa0061f0c`，输出限制`0x40`。随后`0xa01b87c0..87e2`比较`local.`前缀并分流到`0xa01b6a84`或`0xa01b6146`；其他处理路径仍需逐项恢复。
- 相邻本地消息处理代码可见`local.status`、`local.prov_error`、`local.log_enc_key`及`OT_ONLINE`、`BIND_SUCCESS`等文本，支持配网/绑定/在线状态等米家内部协调用途。这里只给出身份和用途判断，不承诺这些方法均能从任意连接直接调用。
- 接收器另有加密标记分支及解密失败日志，不能把所有该端口流量统一描述为裸JSON。完整封装、密钥建立、权限和全部命令表尚未核定。

## 对独立App的意义

它证明原厂有内核TCP监听及内部消息循环可供研究，但不是已实现的局域网HTTP传输层。电脑不能直接通过设备LAN地址访问这个loopback绑定。修改为全网卡绑定也不会将其变成HTTP，更会改变米家内部接口的可达范围；本轮不修改任何绑定或鉴权。

独立App宜由底座增加自己的有界HTTP接口，再调用经过核实的公共服务；是否需要桥接个别米家内部操作，应先核清帧格式、身份检查、调用上下文及原厂并发关系。

## 复查材料与边界

- [0041既有完整网络函数导出](../../artifacts/ap01-research/0041-20261013/0041-ghidra-pass5.txt:43)
- [本次原件指令窗口](../../artifacts/ap01-research/rehost-20261016/localhost-0041-handler.txt)
- [本次字符串定位](../../artifacts/ap01-research/rehost-20261016/localhost-0041-strings.json)
- [先前0041绑定证据](knowledge/0041签名与Bridge接口分析.md:125)

Capstone 5.0.7按RV32/RVC线性解码选定窗口，未知T-Head指令按原始长度保留；不以线性寄存器猜测证明跨分支值流。Ghidra旧导出同样含custom0/unaff等限制。以上是静态实现证据，未观察实机当前监听状态，未验证任意RPC调用或真实云端/更新效果。原厂也可能存在本轮未覆盖的其他服务，不能据本入口断言全ROM不存在HTTP服务器。

## 独立性与公开源码核对

0041 ROMFS启动脚本分别后台启动`miio_client`、`mible_mesh_common_bt`和`lvgl_ui_main`。内置应用表中miio_client入口为`0xa0067296`、配置栈6144 B；界面入口为`0xa005cc1e`、配置栈65536 B。因此该监听运行在独立于原厂UI的后台应用任务内，不依赖某个页面处于前台。它们仍静态链接于同一ROM；独立地址空间、防止UI崩溃影响全系统及单独更新均未由此证明。

命名须区分：本报告“OT agent”来自miio_client内部接收/监听日志，不代表AP01另有一个独立的`miio_agent`可执行程序。小米公开的[Linux接口架构文档](https://cdn.cnbj0.fds.api.mi-img.com/miio.files/commonfile_pdf_de18fa5f5842fab918bc6d3d60093c28.pdf)明确区分直连miio_client的54322与经miio_agent转发的54320。这是公开Linux架构参照，不是AP01 NuttX构建一致性的证明。

2026-10-17联网检索未找到与AP01 0041对应、能直接重编的完整miio_client/OT实现源码。小米[发布文档](https://cdn.cnbj0.fds.api.mi-img.com/miio.files/commonfile_pdf_8912fc997966663192acb1106614994f.pdf)明确曾开源消息注册/分发中间层`miio_agent`，链接`MiEcosystem/miio_linux_open`；该GitHub地址本次访问返回404。官方[miio_open](https://github.com/MiEcosystem/miio_open)仍可访问，定位为接入文档，不能据此宣称原厂完整运行时开源。可参考协议和适配接口，不把Linux agent、社区控制客户端与AP01所用NuttX OT核心混同。

## 其他程序与动态任务

0041内置应用表共8项，除三个启动应用，还有`nsh`、`sh`、`renew`、`setlogmask`和`wapi`。表内存在表示可启动入口，不表示五项同时常驻；原件rcS的97字节正文明确最后打印`NSH auto exit.`并执行`exit`。`renew`的详细行为在本次未逆向，不仅凭名称认定其业务职责。

本次进一步找到0041自己的动态任务创建参数：`0xa0064fe8..0xa006500c`将a1设置为字符串`httpc_task`(`0xa025710c`)，a2设置为入口`0xa0123dca`，a3设置为`0x1400`，调用封装`0xa019750e`。支持HTTP客户端工作任务另行创建，而不是只看应用表就能数出所有运行任务；仍需复核创建封装完整ABI、启动条件与生命周期，不能断言此线程始终存在或把其参数当实测栈峰。未访问实机任务列表，全部NuttX/驱动/无线内部线程的名称、数量、状态与动态栈余量未知。
