# AP01 官方固件获取：0041 流程恢复与新版下载

整理日期：2026-11-06。官方固件的查询、下载、校验与原件归档归 **cuktech-ap01-firmware 本仓库**；逆向仓库负责取得原件之后的分析。本文是本仓库的流程入口。

## 0041 当时是怎么取得的

2026-10-13，设备保留用户报告的 `1.02_0031`，用米家账号扫码登录小米云，查询型号 `njcuk.enstor.ap01` 的最新固件，下载了 `1.0.2_0041`。没有通过手机 ROM 解包、设备 Flash 导出或设备升级来取得文件。

实际链路：

1. 复用相邻 `cuktech-ap01-firmware-tools` 的 `XiaomiQrLogin` 和 `XiaomiCloudClient`，由本仓库的受限下载器执行流程。
2. 生成临时二维码，用户在官方米家 App 扫码确认。
3. 在下载之前，用 Windows 当前用户 DPAPI 加密保存可复用登录字段，并读回核验。
4. 登录后 POST `https://api.io.mi.com/app/home/latest_version`，请求数据为 `{"model":"njcuk.enstor.ap01"}`。请求签名、加密与响应解密由云客户端处理，不能直接用匿名 HTTP 请求代替。
5. 核对返回的型号、版本和 MD5，通过独立、不带账号 Cookie 的会话 GET 固件 URL。实际观察到的下载主机是 `iot-ota-cdn.io.mi.com`。
6. 流式下载，限制 16 MiB 和下载时间；计算 MD5、SHA256，与同次云查询的 MD5 比对，再保存文件并读回校验。
7. 保存不含凭据或完整下载 URL 的 JSON 元数据。退出时删除二维码，保留加密登录缓存。
8. 用独立新进程复用缓存查询成功，验证登录态确实可持久复用；没有发送设备 RPC 或 `miIO.ota`。

下载失败时，旧工具允许同一登录进程内输入 `retry`，五分钟内重试，最多三次；不需要每次失败都重新扫码。

### 已核实的 0041 原件

| 字段 | 值 |
| --- | --- |
| 型号 | `njcuk.enstor.ap01` |
| 版本 | `1.0.2_0041` |
| 规范原件 | `roms/0041/ap01-1.0.2_0041.bin` |
| 字节数 | `6769704` |
| MD5 | `3c2d962be82c73860daff903178d9b9e` |
| SHA256 | `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9` |
| 下载时设备更新 | 未发送 |
| 独立新进程复用登录 | 已成功 |

元数据在 [0041 JSON](../roms/0041/ap01-1.0.2_0041.json)，原件清单在 [ROM 清单](../roms/CATALOG.md)。JSON 中 `codex_status/artifacts/ap01-research/` 的绝对路径是当时的保存位置，不是当前运行入口。

这里取得的是米家应用 OTA 更新容器，不是整片 Flash 备份。下载校验通过不代表新版本已经适配本仓库的补丁、构建器或安装路径。

## 当前获取入口（本仓库）

[download_official.py](../tooling/scripts/download_official.py) 已支持新版。查询、下载、登录缓存和原件归档都在本仓库；仅扫码与云客户端模块仍从相邻 `cuktech-ap01-firmware-tools/features/official_firmware_source/` 只读导入。无需运行该仓库的命令，也不使用其 `env/mi-cloud.env`。

| 内容 | 本仓库位置 |
| --- | --- |
| 下载器 | `tooling/scripts/download_official.py` |
| Windows DPAPI 登录缓存 | `evidence/private/xiaomi-account.dpapi`，Git 忽略 |
| 临时二维码 | `evidence/private/xiaomi-login-qr.png`，退出时删除 |
| 下载原件与去敏记录 | `evidence/private/ap01-<version>.bin` / `.json` |
| 规范原件归档 | `roms/<版本后缀>/ap01-<version>.bin` / `.json` |

2026-11-06 已将拆分时留在相邻逆向仓库 `evidence/private/xiaomi-account.dpapi` 的加密缓存复制回本仓库，逐字节哈希比对通过；来源保留。实际查询和下载均成功复用缓存，没有再次扫码。DPAPI 缓存依赖原 Windows 用户环境，不可直接改名为 env 登录文件；不输出、提交凭据内容。

历史 0041 报告仍保存在相邻逆向仓库 `reverse/reports/ap01/firmware-download-20261013.md`，独立验证记录为 `reverse/analysis/0041-download-verification-20261013.json`。本文已恢复获取步骤与结果，后续获取流程在本仓库维护。

## 查询与下载最新版本

从本仓库根目录执行，使用已有 PlatformIO Python 和 requests 环境：

```powershell
$ap01Python = 'C:\Users\cogic\.platformio\penv\Scripts\python.exe'
$env:PYTHONIOENCODING = 'utf-8'

# 离线检查：不联网、不使用真实凭据。
& $ap01Python -B tooling/scripts/download_official.py --self-test

# 复用缓存，仅查询最新版本，不下载。
& $ap01Python -B tooling/scripts/download_official.py --latest --info

# 查询并下载执行时云端返回的最新版本。
& $ap01Python -B tooling/scripts/download_official.py --latest

# 或者只接受指定版本；如果云端返回其他版本则停止。
# & $ap01Python -B tooling/scripts/download_official.py --version 1.0.2_0055

# 缓存失效、确需重新扫码时使用。
# & $ap01Python -B tooling/scripts/download_official.py --latest --login
```

`--latest` 与 `--version` 互斥。不带两者时保留历史行为，只接受 `1.0.2_0041` / `1.02_0041`。`--version` 校验云端当前返回值，不能从云端按版本号检索历史包。`--info` 也执行所选版本检查。输出目录自动创建。

没有缓存时，命令生成二维码，需展示图片并保持进程运行，等待用户在官方米家 App 扫码确认。登录成功立即加密保存缓存；已有缓存的登录失败不会自动触发重复扫码，确认失效后用 `--login` 重登。

每次下载重新查询云端，以该次返回的版本、MD5 和 URL 为准。保留型号、版本文件名、MD5 格式、HTTPS 目的地、重定向、TLS、大小和时间限制；云端会话只能使用型号查询 API，禁止设备列表、RPC/OTA 路径。固件下载会话不带账号 Cookie。已有同名 BIN 或 JSON 时拒绝覆盖；重复执行的拒绝不表示已有原件损坏。

Windows 使用拒绝覆盖的原子 rename 提交下载文件；其他平台保留 link 的拒绝覆盖行为。保存后独立读回核对 SHA256；元数据不含账号凭据或完整下载 URL。

## 0055 本次实际获取记录

2026-11-06 21:55（Asia/Hong_Kong），使用原 DPAPI 缓存查询并下载成功：

| 字段 | 值 |
| --- | --- |
| 型号 | `njcuk.enstor.ap01` |
| 云端当前版本 | `1.0.2_0055` |
| 下载主机 | `iot-ota-cdn.io.mi.com` |
| 云端上传时间原值 | `1792751737` |
| 字节数 | `6389800` |
| MD5（同次云查询一致） | `16e38af473693064ddaca5f0ffe27ad7` |
| SHA256 | `0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7` |
| 本仓库原件 | `roms/0055/ap01-1.0.2_0055.bin`，已只读归档 |
| 去敏记录 | `roms/0055/ap01-1.0.2_0055.json` |
| 设备更新命令 | 未发送 |

云端更新说明：支持插件设置切换功率界面主题；支持屏幕显示 iPhone 18 系列及 iPhone Duo 型号；修复已知问题，优化用户体验。此处转录云端内容，不代表本项目对这些功能的验证。

下载副本与归档原件逐字节相等，独立读回大小、MD5、SHA256 均通过。下载和归档不改变 0041 默认构建目标；下载时 0055 尚未适配，后续补丁、构建与专项 QEMU 结果见 [0055 验证记录](0055-qemu-validation-20261106.md)。本次未刷入或控制设备。2026-11-07 按用户要求将 0055 原厂 BIN 与 0031/0041 一同纳入版本控制，下载元数据及登录缓存仍仅保存在本地。

## 后续版本归档

1. 保存下载命令的去敏 JSON，记录该次型号、版本、更新说明、云端 MD5、大小、SHA256 和获取时间。
2. 独立读回 BIN 核对大小、MD5 和 SHA256，将其与 JSON 及同次云端 MD5 比较。
3. 将原件与记录复制到本仓库新版本目录，设置原件只读；保留 0041 原件、候选和既有构建基线。
4. 更新 [ROM 清单](../roms/CATALOG.md)。新 BIN/JSON 目前默认被 Git 忽略，保存在本地；是否纳入版本控制另行决定，登录缓存不入库。
