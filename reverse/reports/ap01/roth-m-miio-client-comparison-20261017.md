# roth-m/miioclient-mqtt 与AP01 0041 miio_client对照

结论：该项目提供的是兼容小米本地消息接口的社区开源替代程序，不能认定为AP01原厂miio_client的早期官方版本或完整源码。它可作为协议参考，但不是可以直接替换AP01的同一平台运行时。

2026-10-17只读访问用户指定仓库并下载指定公开文件，未执行二进制、构建脚本或安装脚本，未访问设备。固定仓库提交`063f5d121f8e5b0421ad256dc0b3c9d6934d3426`，该提交时间为2020-02-15T18:15:59Z；README/源码作者标记2019。提交时间不等于原厂SDK版本号。

## 一手来源

- [仓库README](https://github.com/roth-m/miioclient-mqtt/blob/063f5d121f8e5b0421ad256dc0b3c9d6934d3426/README.md)自称MI miio_client replacement，目标Xiaomi Aqara Lumi Gateway(mieu01)。MQTT处理在单独Python程序中。
- [miio_client说明](https://github.com/roth-m/miioclient-mqtt/blob/063f5d121f8e5b0421ad256dc0b3c9d6934d3426/miio_client/README.md)写明无加密、提供ARM二进制，并明确原厂程序仍用于Wi-Fi连接。
- [C源码](https://github.com/roth-m/miioclient-mqtt/blob/063f5d121f8e5b0421ad256dc0b3c9d6934d3426/miio_client/miio_client.c)头部称开源实现，含RothM修改标记；采用socket/select/cJSON，提供localhost TCP54322与对外UDP54321之间的消息传递。
- [编译脚本](https://github.com/roth-m/miioclient-mqtt/blob/063f5d121f8e5b0421ad256dc0b3c9d6934d3426/miio_client/compile.sh)使用arm-linux-gnueabihf GCC，将该源码及cJSON链接为miio_client。

## 对照

| 项目 | 仓库实现 | AP01 0041原厂组件 |
| --- | --- | --- |
| 文件/平台 | 32位小端ARM ELF，Linux目标 | RV32/RVC，NuttX内置应用，静态链接于ROM |
| 来源性质 | 社区兼容替代实现，无加密版本 | 小米SDK集成及AP01厂商适配；未找到匹配完整源码 |
| 本地接口 | 127.0.0.1:54322，JSON method/id/params | 相同端口及多项消息名，原件中另有完整解析/分派及加密路径 |
| 网络管理 | README要求保留原厂Wi-Fi连接能力 | 初始化原厂扫描/连接/断开回调、DHCP与网络监视任务 |
| 云/状态 | 对local.query_status直接返回cloud_connected，local.query_time使用宿主time(NULL) | 原厂云通信、绑定、OTA及相应工作任务 |
| 身份/结果 | 源码有固定设备ID/默认token、部分直接ok回执 | 原厂自己的认证/密钥/事务逻辑，不能以社区模拟回执替代 |

相同端口与方法证明针对同一协议家族兼容，并不能证明官方源码沿袭或AP01来自该项目。没有识别出能据此确认AP01原厂miio_client发布版本号的证据。

本次下载二进制50924 B，ELF32/LSB/e_machine=40(ARM)，SHA256 `df9087f2a47ca3e87ee0fcd3464578bdabf7724b2b07304f9e13ee7b02b8cef6`。文件身份、URL及源码/脚本哈希见本地清单（材料未随仓库收录：`../../reverse/rehost/roth-m-miio-client-inventory.json`）。二进制含local.query_status/local.query_time等实现文本；这不代替可重现构建或源到二进制逐指令一致证明。

AP01对照依据[任务功能调查](mijia-task-dependencies-0041-20261017.md)和[localhost接收器原件分析](localhost-service-0041-20261017.md)。如果借鉴该代码移植，必须重新编译并适配NuttX，逐项补原厂依赖、认证/错误/超时/帧边界；不得直接运行ARM ELF或将固定cloud_connected/ok当成真实业务成功。GPL许可标记不证明整个原厂SDK开源。
