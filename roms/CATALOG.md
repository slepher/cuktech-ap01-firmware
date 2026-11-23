# 0055 ROM 与发布附件

当前基础平台为原厂 **1.0.2_0055**，修改版为 **0.1.2**。原件是米家 miIO.ota 应用更新容器，不是整片 Flash 备份；文件偏移不能直接作为实机烧录地址。

## 原厂镜像

| 字段 | 值 |
| --- | --- |
| 型号 | `njcuk.enstor.ap01` |
| 文件 | `0055/ap01-1.0.2_0055.bin` |
| 字节数 | 6,389,800 |
| SHA256 | `0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7` |

构建器根据 `tooling/rom-targets/current.json` 核对原件大小、SHA256 和补丁位置。查询与下载方法见 [官方固件获取](../docs/official-firmware-extraction.md)。原件已随仓库保存，构建不需要登录小米云。

安装条件、官方升级限制和首刷流程见 [刷机说明](../docs/flashing.md)。

## 发布附件

[Release CI](../.github/workflows/release.yml) 在 tag 推送后构建、校验并发布附件：

| 固件 | 用途 |
| --- | --- |
| `ap01-0055-base-0.1.2.bin` | 无 App 基版，提供独立维护服务 |
| `ap01-0055-app-platform-0.1.2.bin` | ABI 3 App 集合加载平台 |

每种固件附带 payload、ELF、map、manifest、审计与链接报告。附件版本取自 `native_version.h`；文件大小和 SHA256 以对应 Release 的附件与 `SHA256SUMS` 为准。

构建与发布命令见 [README](../README.md)。候选标记 `flashable=false`、`hardware_verified=false`；离线校验通过不代表实机验收。厂商镜像及其内含资源的许可见 [NOTICE](../NOTICE.md)。
