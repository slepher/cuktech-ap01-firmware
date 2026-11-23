# 来源与许可声明

本仓库包含固件平台模块、构建和诊断脚本，以及用于复现构建的原厂更新镜像。

## 本仓库内容

- 除下文标注的第三方内容外，本仓库自有代码与文档采用 [MIT License](LICENSE)，版权归 Codex Status contributors。

## 第三方与厂商材料

- **ArduinoJson 7.4.3**（Benoit BLANCHON，MIT）：独立构建所需头文件保存在 `tooling/vendor/ArduinoJson/src/`，原始许可见 [LICENSE.txt](tooling/vendor/ArduinoJson/LICENSE.txt)。版本固定，不在构建期间下载依赖。
- `native_sha256.cpp` 复用 Codex Status contributors 的既有 MIT 字节工具实现，独立构建不需要读取外部 App 源码。

- **CUKTECH AP01 固件**（`1.0.2_0031` / `1.0.2_0041` / `1.0.2_0055`）：版权归 CUKTECH / 小米生态链所有。
  本仓库收录未经修改的 `roms/0031/ap01-1.0.2_0031.bin`、`roms/0041/ap01-1.0.2_0041.bin` 和 `roms/0055/ap01-1.0.2_0055.bin`，文件名、字节数与 SHA256
  见 `roms/CATALOG.md`。该厂商镜像及其内含资源不适用本仓库自有代码的 MIT 许可；
  使用与分发须遵守厂商与分发渠道的条款。当前平台构建使用 0055；修改后的 ROM 通过 GitHub Release 分发，不纳入 Git，内含厂商材料仍适用上述许可边界。
- **`cuktech-ap01-firmware-tools`**（作者 andy-JustSayWhen，MIT，commit
  `3bd98a8ca4fb35a9f8869121b13961d405b16dff`）：作为只读上游参考。本仓库若引用其文档或源码，
  按要求保留作者与许可说明。
- **`cuktech-screen-controller`**（MIT）：仅作原厂接口与显示交接的对照参考。

## 隐私

本仓库不包含设备账号缓存、token、认证密钥或任何 `*.auth-key` / `*.dpapi` 文件。
每次 Release 附带 `SHA256SUMS`，用于核对该次发布附件的完整性。
