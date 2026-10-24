# 来源与许可声明

本仓库包含逆向研究笔记、脚本、清单，以及用于复现构建的原厂 `1.0.2_0041` 更新镜像。

## 本仓库内容

- 除下文标注的第三方内容外，本仓库自有代码与文档采用 [MIT License](LICENSE)，版权归 Codex Status contributors。

## 第三方与厂商材料

- **CUKTECH AP01 固件**（`1.0.2_0031` / `1.0.2_0041`）：版权归 CUKTECH / 小米生态链所有。
  本仓库收录未经修改的 `roms/0041/ap01-1.0.2_0041.bin`，文件名、字节数与 SHA256
  见 `roms/CATALOG.md`。该厂商镜像及其内含资源不适用本仓库自有代码的 MIT 许可；
  使用与分发须遵守厂商与分发渠道的条款。其余 ROM 镜像仍只记录清单，不纳入 Git。
- **`cuktech-ap01-firmware-tools`**（作者 andy-JustSayWhen，MIT，commit
  `3bd98a8ca4fb35a9f8869121b13961d405b16dff`）：作为只读上游参考。本仓库若引用其文档或源码，
  按要求保留作者与许可说明。
- **`cuktech-screen-controller`**（MIT）：仅作原厂接口与显示交接的对照参考。
- **Bouffalo SDK**（Apache-2.0）：`reverse/sdk/` 只保留少量寄存器/内存映射头文件摘录，用于交叉核对，
  不包含完整 SDK；原始项目见 <https://github.com/bouffalolabs/bouffalo_sdk>。
- **Ghidra 12.1.4**：`evidence/` 中的私有安装副本不入库；本仓库可能包含自定义处理器语言
  （SLEIGH `.sinc/.ldefs` 等）与修复脚本，均按 Apache-2.0 派生约定提供，不声称是 NSA 官方发布。
- **REA**：分析工具由使用者自行提供；本仓库只保存其证据导出格式说明与复现脚本，
  `evidence/` 与 `rea/node_modules` 均不入库。

## 隐私

本仓库不包含设备账号缓存、token、认证密钥或任何 `*.auth-key` / `*.dpapi` 文件。
历史 `checksums/SHA256SUMS.txt` 仅记录哈希，不包含文件内容；现存仓库外归档，不再纳入 Git。
