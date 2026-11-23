# 0055 ROM 与发布附件

当前基础平台为原厂 **1.0.2_0055**，修改版为 **0.1.3**。原件是米家 miIO.ota 应用更新容器，不是整片 Flash 备份；文件偏移不能直接作为实机烧录地址。

## 原厂镜像

| 字段 | 值 |
| --- | --- |
| 型号 | `njcuk.enstor.ap01` |
| 文件 | `0055/ap01-1.0.2_0055.bin` |
| 字节数 | 6,389,800 |
| SHA256 | `0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7` |

构建器根据 `tooling/rom-targets/current.json` 核对原件大小、SHA256 和补丁位置。查询与下载方法见 [官方固件获取](../docs/official-firmware-extraction.md)。原件已随仓库保存，构建不需要登录小米云。

安装条件、官方升级限制和首刷流程见 [刷机说明](../docs/flashing.md)。

## 固件类型

本项目提供两种完整固件：

| 固件 | 用途 |
| --- | --- |
| `ap01-0055-base-0.1.3.bin` | 无 App 基版，提供独立维护服务 |
| `ap01-0055-app-platform-0.1.3.bin` | ABI 3 App 集合加载平台 |

发布、下载附件和构建产物说明见 [版本发布](../docs/releasing.md)。厂商镜像及其内含资源的许可见 [NOTICE](../NOTICE.md)。
