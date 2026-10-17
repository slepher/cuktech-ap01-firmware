# 0041 miio/mible REA协议逆向

## Plan

用户要求参考roth-m/miioclient-mqtt，使用REA继续逆向0041的miio_client与mible_mesh_common_bt。本轮限定离线协议/状态机/接口分析，不运行第三方二进制、不连接设备、不停任务、不修改ROM或Bridge。保留SIM及既有归档。

## Task

1. 复用REA已绑定的0041 SHA与profile，保存真实函数Evidence及限制，不重开目标或向其他提供方发送原件。
2. 父代理独占REA，追踪本地接收/分派、RPC注册、BLE配网入口；GPT-6.1 Sol子代理分别核对native RPC表及蓝牙参数/状态机，原件指令作辅助证据。
3. 与已固定提交的roth-m源码比较接口与语义，区分兼容名称、完整实现、固定模拟回执与未证明行为。
4. 交付命令/接口清单、状态转移、依赖与未决项，Evidence/原件/报告哈希绑定。反编译伪代码不标为原始源码或可编译实现。

## Status

本轮限定协议调查完成：90项真实描述记录、10项本地分派名称与1项回包名称、6个蓝牙命令参数、FE95六项构造记录、两套状态表示及5个配网opcode分支已整理。REA6.5.0/Ghidra12.1.4归档30项记录（本轮新增28项），原件SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，base `0x9ffff000`，entry `0xa0000000`，profile `958b301907fe9bfcbbf58f56c40ca89e93ea3d974184b719c8b172f60709c6f3`。详见[结果、产物及未决项](miio-mible-protocol-rea-0041-20261017.md)。这不是两套SDK的完整源码重建；未执行硬件调用或改固件。

## Review

逐项保留已观察/推断/未知。厂商指令、RAM初始化映射及Ghidra错误no-return会截断函数，未覆盖路径不作否定结论；只在原始指令支持时补充局部结论。不得将localhost入口等同授权OTA，不使用RothM固定cloud_connected/ok替代真实服务结果。无需硬件验收的本轮调查不宣称实机行为已通过。
