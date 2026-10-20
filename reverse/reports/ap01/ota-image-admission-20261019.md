# 独立OTA镜像准入收敛

2026-10-19，用户明确要求删除请求、真实容量、完整性和实际写入成功之外的镜像内容限制。`ota_image.c/.h`不再读取型号固定偏移或参考板型头，不检查固定magic/Flash配置/安全模式/入口/代码跨度；只保留296 B至7 MiB边界、头CRC及40 B恢复尾标记/声明长度/全文件CRC。请求鉴权、传输CRC、超时、并发围栏和原厂写入读回不变。0041设备接入仓库使用完全相同的校验器；自有App manifest也不再是上传要求。

旧设备tail2仍含旧限制，因此先用其可接受的0031过渡包更新独立OTA自身，不能把源码已改当作设备已更新。过渡版tail3-minimal已实机单次成功，认证build ef8319734dcaa8e63d5151bfd512a69a、实际槽2、物理表age9。镜像6822072 B，SHA256 e34c7b3a4bbc6f582d31a56ae2b2d587748779868ff7df171d4f89bd9e3a634f，原启动/GIF/PEC/传统入口保持。后续完整0041刷写状态由同父目录codex_status/PROGRESS.md与project-workflow/ap01-template-integration/flash-0041-20261019.md记录。

两端各29项镜像正反向ASan/UBSan、52项请求故障、15项维护诊断通过；旧验证器接受过渡0031已离线核验。原生guest socket启动观察与实机认证健康分开记账，host代理失败报告保留。私有原始证据在codex_status/artifacts/ap01-platform-integration/ota-minimal-20261019和physical-0041-20261019。未修改冻结ROM或旧证据，未提交凭据。
