# 0055 官方固件获取

0055／0.1.3 平台使用原厂 `1.0.2_0055` 更新镜像。原件已随仓库保存，普通构建无需联网下载；文件身份见 [ROM 清单](../roms/CATALOG.md)。

下载原件不会改变设备固件。不要先通过米家将原厂 0031 升级到官方 0041／0055 来准备安装自定义 ROM；具体限制与首刷条件见 [刷机说明](flashing.md)。

## 环境与文件

下载入口为 [download_official.py](../tooling/scripts/download_official.py)。在线登录使用 Windows DPAPI 保存凭据，需要 Windows Python、requests，以及相邻 `cuktech-ap01-firmware-tools/features/official_firmware_source/` 中的扫码与云客户端模块。

| 内容 | 位置 |
| --- | --- |
| 加密登录缓存 | `evidence/private/xiaomi-account.dpapi` |
| 临时二维码 | `evidence/private/xiaomi-login-qr.png` |
| 下载镜像与去敏元数据 | `evidence/private/ap01-<version>.bin` / `.json` |
| 构建原件 | `roms/0055/ap01-1.0.2_0055.bin` |

登录缓存依赖 Windows 用户环境，不得提交或输出凭据内容。退出时删除临时二维码。

## 查询与下载

在仓库根目录执行：

```powershell
# 离线自检，不登录或访问设备
python -B tooling/scripts/download_official.py --self-test
# 查询并要求云端返回 0055
python -B tooling/scripts/download_official.py --version 1.0.2_0055 --info
# 下载并要求云端返回 0055
python -B tooling/scripts/download_official.py --version 1.0.2_0055
# 登录缓存失效时重新扫码
python -B tooling/scripts/download_official.py --version 1.0.2_0055 --login
```

`--version` 校验云端返回值，不提供按版本检索功能。云端返回其他版本时命令停止；构建仍使用仓库中的 0055 原件。

没有缓存时，命令生成二维码并等待用户在米家 App 扫码确认。登录成功后加密保存缓存；缓存登录失败时可用 `--login` 重登。

下载器核对型号 `njcuk.enstor.ap01`、版本、MD5、HTTPS 目的地、TLS、大小与时间限制。固件下载会话不携带账号 Cookie，不发送设备 RPC 或 OTA 命令。同名 BIN 或 JSON 存在时拒绝覆盖。保存后独立读回核对 SHA256，元数据不包含账号凭据或完整下载 URL。

原件为米家应用 OTA 更新容器，不是整片 Flash 备份。下载校验通过不代表实机部署验收。来源与许可见 [NOTICE](../NOTICE.md)。
