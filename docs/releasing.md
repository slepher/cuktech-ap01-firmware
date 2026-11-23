# 版本发布

当前修改版为 **0.1.3**，基础平台为 **1.0.2_0055**。版本源码入口是 [`native_version.h`](../tooling/firmware-modules/native_version.h) 中的 `AP01_MODIFIED_ROM_VERSION`，不带后缀。tag、Release 名称与修改版版本保持一致。

## 提交与 tag

更新版本源码、测试预期和使用文档，完成构建与检查后提交。首次创建版本 tag：

```sh
git tag -a 0.1.3 -m "AP01 0055 platform 0.1.3"
```

如果 tag 已存在，先核对它指向的提交：

```sh
git show --no-patch 0.1.3
```

发布到 GitHub：

```sh
git push origin master
git push origin 0.1.3
```

创建本地 tag 不触发 CI，推送 tag 才触发发布。tag 不改写源码版本，也不更新设备；设备升级按 [刷机说明](flashing.md) 执行。业务 App 包使用自己的版本和发布流程。

## Release CI

[Release 工作流](../.github/workflows/release.yml) 监听所有 tag 推送，使用 Python 3.12 和 xPack RISC-V GCC 12.5.0-1：

1. 校验原厂 0055 镜像和补丁边界。
2. 在独立构建目录分别生成 base 与 App 平台固件。
3. 运行固件校验、槽位检查、维护与恢复回归、ROM 分类检查。
4. 归档构建细节，生成两个完整 BIN 的 `SHA256SUMS`。
5. 创建与 tag 同名的 GitHub Release，并自动生成变更说明。

工作流使用内置 `GITHUB_TOKEN` 的 `contents: write` 权限，无需额外发布密钥。推送后在 GitHub Actions 中打开对应 tag 的 Release 运行，确认构建、归档和发布步骤完成，再核对同名 Release 的附件。

## 发布附件

Release 只提供以下三个文件：

| 文件 | 用途 |
| --- | --- |
| `ap01-0055-base-0.1.3.bin` | 无 App 基版，提供独立维护服务 |
| `ap01-0055-app-platform-0.1.3.bin` | ABI 3 App 集合加载平台 |
| `SHA256SUMS` | 上述两个完整 BIN 的 SHA256 |

下载到同一目录后校验：

```sh
sha256sum --check SHA256SUMS
# macOS
shasum -a 256 --check SHA256SUMS
```

刷机使用完整 `.bin`。payload、ELF、map、manifest、审计与链接报告存放在对应 Actions 运行的 `ap01-build-details-<tag>` 构建产物中，保留 90 天。这些文件用于构建检查与诊断，不是刷机附件。manifest 内的文件路径属于 CI 构建环境。

## 归档已有 Release 的构建细节

在 Actions 中手动运行 Release 工作流，填写已有的 `release_tag`。工作流下载并校验该 Release 的附件，将其中的调试文件归档为 `ap01-build-details-<tag>`。

该操作不重编固件、不创建 Release，也不删除附件。需要精简已有附件时，先确认归档中包含所需文件，再清理调试附件并更新只覆盖两个完整 BIN 的 `SHA256SUMS`。
