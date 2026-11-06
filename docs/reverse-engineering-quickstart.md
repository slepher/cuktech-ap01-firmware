# AP01 逆向接续入口

最后整理：2026-11-06。本页用于下一次版本对比先复用既有证据和工具，避免重新定位环境、下载编译器或重复分析已确认接口。

## 先读和先用

| 需要解决的问题 | 入口 |
| --- | --- |
| 当前已经核对过的原厂接口 | `tooling/firmware-modules/native_rom_addresses_0055.h`；135 个位置，134 个被生产源码使用 |
| 入口补丁与原始字节 | `tooling/rom-targets/0055.json`；七处补丁、精确 SHA 和续接位置 |
| 已消费结构字段 | `tooling/rom-targets/0055-abi-checks.json`；40 项带立即数的指令 |
| 本次迁移的语义与陷阱 | [0055 地址迁移](0055-address-migration.md) |
| 当前可用 WSL、工具链和模拟器 | [0055 WSL/QEMU 验证](0055-qemu-validation-20261106.md) |
| 最新候选与准确验收范围 | `build/0055-qemu-verified-20261106/release.json` |
| REA 证据与快照 | `evidence/0055-address-migration-20261106/rea-evidence.json`、`rea-0055-snapshot.json` |
| 本地可搬移检查点 | `evidence/0055-reuse-20261106-final/checkpoint.json` |

上面的源码、配置、指南和保存脚本由本仓库 Git 维护。`build/` 和 `evidence/` 仍按仓库规则忽略，检查点保留在本机，换机器需要另行拷贝。原厂 ROM 只在清单中记录路径和摘要，没有重复打包；0055 原件本身也需要保留。

## 保存与核验

```powershell
python -B tooling/scripts/save-research-checkpoint.py --out evidence/0055-reuse-20261106-final
python -B tooling/scripts/save-research-checkpoint.py --verify evidence/0055-reuse-20261106-final
```

保存拒绝覆盖已有目录；重存请换新目录名。文件按 `files/<原仓库相对路径>` 保留，清单记录每个文件的大小、SHA256 和源 HEAD。HEAD 不代表当前全部源码已提交；检查点也不是完整固件源码或整台机器备份。

检查点保存本轮的候选定位、全函数体比较、全局变量、字体/页面验证脚本及小型报告、REA 快照、已确认地址、QEMU 结果和 GCC 发布元数据。也保存三组 QEMU guest、App/peer、Manifest 和构建描述；将这些输入恢复到新的 fixture 目录后可复跑，无需先重编业务包。两个大型线性反汇编缓存不保存，可以重新生成。工具链归档优先用同卷硬链接保存，删除 `build` 中的名字后检查点仍保留数据；不要修改任一名字所指向的归档内容。

原研究脚本是 0041→0055 的历史参考，可能硬编码版本、`build` 路径和输出文件名。下次先复制到新的调查目录，再修改输入/输出，避免直接执行后覆盖旧候选。确认结果以生产地址头、`ui/final-mapping.json` 和 `services/mapping.json` 为准；`ui/mapping.json`、`prefix-mapping.json`、`candidates.json` 包含未审定候选，不能自动用于补丁。`compare_bodies.py` 等还使用相邻逆向仓库的 `reverse/analysis/whole-rom-coverage-0041-20261023-round1.json`；检查点在原文件存在时另存 `analysis/0041-function-boundaries.json`，保留绑定原件的函数边界及直接调用，读入路径可改用该精简副本。完整研究历史仍在逆向仓库，未整体备份；正式构建继续只依赖固件仓库。

## 下一个 ROM 的最短调查顺序

1. 固定新原件的大小、SHA256、版本、容器/VA 映射；旧版函数与全局地址作为搜索锚点，不能自动当作新版地址。
2. 先看 REA 已留存证据，再按原件 SHA、架构、基址、入口和分析 profile 重载匹配快照。快照不是完整持久 Ghidra 数据库，不保证免除新的自动分析；现有反编译记录可先直接查阅。
3. 复用函数边界和调用关系进行候选匹配，先查完整函数和局部调用，再查实际消费的立即数/字段、全局变量及原厂页面顺序。归一指令序列只用于定位候选，不作为签名兼容证明。
4. 候选身份确认后维护独立地址配置，要求原始字节与原件身份完全一致。保留旧目标和 App 合同，只有有证据的布局/续执行变化才写适配。
5. 先运行静态检查，再执行原厂/候选指令与真实 App 的专项 QEMU 验证，记录替身和未覆盖项。每次报告绑定 ROM、ELF、App、guest、模拟器和传输脚本的摘要。

可复用检查：`test-rom-target.py --target 0055`、`test-rom-migration-0055.py`、`test-stock-screen-count.py`、`test-native-0055-qemu.py`、`build-app-v3-guest-0041.py --target 0055` 和 `test-app-abi-qemu-0041.py --direct-v3`。具体命令及既有 fixture 在上面的 QEMU 报告中。

## 已经踩过的坑

- 当前 Windows 沙箱内访问 WSL 会被拒绝，沙箱外 `wsl -d Ubuntu-24.04 --exec ...` 可用。先查本机 WSL；不要因 `james.local` 无法解析就认定没有模拟环境。
- 已验收引擎在 `/home/slepher/qemu-ap01-boot-safety-20261019/build/qemu-system-riscv32`，SHA256 `b46de0508e0f4be6c4ef5ded168360c7bf4bc5e23bf43e44e9f244a79d33b0ce`。现有模型基线 55 项通过。
- 原厂 memset 会用 `th_mula`，实际指令测试要启用已支持的 `xtheadmac`，并保留报告中的完整 CPU 扩展配置。非法指令先核对 ISA/模拟器能力。
- GCC 8 的预编译 libm 含绝对指令重定位，适合固定链接的 ROM 并不意味着适合可搬移 App。已验收 xPack GCC 12.5.0-1 Linux x64，官方归档 SHA256 `624fae17fb5dfaa0d8a9f8b345c9831cca9e06322a34254342a19eea61915e82`；不能为换工具链而放宽 App 修正白名单。
- WSL 在 `/mnt/d` 解包大量工具链小文件很慢。在 WSL 独立临时目录解包本次约 11 秒；`wsl-toolchain-path.txt` 的临时路径重启后可能失效，先查可执行文件，再从检查点中的已校验归档重解。不要回退到旧 GCC 而不记录。
- 原厂页从 9 个增至 11 个，Settings/Pet 保持 6/7，新增页为 8/9，旧末页 8→10；peer 的物理页旧 17→19。指令或函数签名相似不证明页面数量相同。
- 菜单跳板必须重放新调用点覆盖的指令；0055 前两处是 `addi a1,s1,0x6be`。短序言匹配曾把图像构造误认成析构内部，必须核对调用及类元数据。
- Ghidra 有 memcpy/memset 被误标不返回、自定义指令和边界恢复限制。不能把截断的伪代码当作接口变化证据；结合原始指令和实际调用。
- 专项 QEMU 通过不代表完整 ROM 冷启动或真实 LCD/Wi-Fi/Flash 验收。当前不访问设备、不自动刷机，候选全局硬件标记保持 false。
