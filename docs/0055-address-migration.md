# 0055 地址迁移与兼容性核对

2026-11-06。目标是沿用 0041 的模块追加、入口跳板和原厂服务封装，生成不加载 App 的基版及支持独立 App 的应用版。只进行了本地分析、构建和离线验证，没有访问或写入设备。

后续已在本机 WSL 使用兼容工具链完成真实业务 App 重编和专项 QEMU 执行；最新候选、通过范围和完整启动限制见 [WSL/QEMU 验证](0055-qemu-validation-20261106.md)。下文首轮候选和本机 GCC 8 受阻记录保留作分析历史。

## 固定输入与实现

0055 原件为 `roms/0055/ap01-1.0.2_0055.bin`，6,389,800 B，SHA256 `0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7`。旧版对照 SHA256 为 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。

地址表在 `tooling/firmware-modules/native_rom_addresses_0055.h`，含 135 个对应位置，其中当前生产代码消费 134 个。`AP01_ROM_ADDR` 默认保留 0041 的地址，仅 `--target 0055` 选择新版。保留既有源文件/函数名，避免连带更改 App 的结构或 ABI。

`tooling/rom-targets/0055.json` 固定原件身份和七个补丁位置。编译审计、链接和打包绑定目标与配置摘要；原始字节不符、缺少地址、跨目标产物、审计过期均拒绝。模块继续位于文件偏移 `0x675000` / VA `0xa0674000`，容量上限仍为原有 `0x700000`。新版头部 CRC、40 B 恢复尾记录和恢复 CRC 与现有算法一致。这里的 VA/容器偏移不是实机烧录地址。

## 签名与实际差异

核对覆盖当前封装使用的参数寄存器、返回方式、所访问字段及关键调用链，未发现必须修改 App ABI 或原厂服务封装函数参数的变化。原始类型并无调试符号，恢复的 C 类型属于静态推断；不声称已证明全 ROM 的全部签名相同。

- 系统服务 40 项检查逐字节比较带立即数的指令，覆盖 PollFd 24 B、IPv4 Address 16 B、Clock 8 B、Lookup 实际字段、stat 60 B、statfs 24 B、inode flags/ops 和 Flash fd/flag。Lookup 28 B 由已访问字段和 ILP32 对齐推导，保留字节没有独立访问证据。
- LittleFS 24 项操作表的 96 B 在新位置逐字节一致。TLS 成功路径的 errno 偏移 `+4` 保留，全局兜底变量换址。重启 `ff04` 与切槽 `ff13` 的对应分支也单独核对。
- Wi-Fi 加密读写改用新的全局锁地址和寻址方式；线程创建末尾将 `memset(attr,0,12)` 提取为 helper。REA 确认 helper 的单指针清零行为，不需要改变外层五参数线程接口。
- 五组原厂字体的字符映射、字形指标、完整位图和 kerning 数据核对一致，Font36、Glyph8、Cmap20 及当前使用的图像/事件/定时器字段保持兼容。

有两处需要适配，不能机械替换地址：

1. **原厂根页面 9 → 11。** 旧索引 0–7 不变，旧 8 对应新 10；新增 8/9 调用 `lv_page_ui_cuk_con_info_ov_creat(parent,1/2)`，tag 为 `0x31/0x32`。设置仍是 6/tag9，宠物仍是 7/tag10。平台按目标保留所有原厂根页，App 从 11 之后挂载；App 页面 tag 的基数也相应调整。设置菜单仍为标题加六个原厂条目，设备码/Wi-Fi 插入位置保持。
2. **菜单跳板的被覆盖指令变化。** 新版前两处调用后是 `addi a1,s1,0x6be`，第三处是 `lui a1,0xa00fd`；0055 跳板补回这些新指令，0041 跳板保留旧续执行序列。定时器 NULL 保护的前 8 B 原序言未变，续接地址改为 `0xa007def4`。

| 用途 | 0041 文件偏移 | 0055 文件偏移 |
| --- | --- | --- |
| UI 挂接 | `0x5e180` | `0x79bce` |
| 定时器删除保护 | `0x8be58` | `0x7eeec` |
| 菜单调用一/二/三 | `0xb262c/0xb263a/0xb2648` | `0xc3cc4/0xc3cd2/0xc3ce0` |
| 菜单列表 | `0xb2754` | `0xc3df4` |
| 延用已有 unsigned OTA 分支修改 | `0x707fc` | `0x6cd60` |

## App 合同

APX2 仍为容器版本 2、256 B 头、ABI major 3；平台继续提供 3.1 函数表。AMF3、AUT3、集合事务、包摘要和 BASE32 修正记录不变。APX2 的既有 target 值 1 保留，用于经过本次适配的共同平台合同；`APX2_TARGET_0041` 历史名字没有成为新包格式。ROM 自身身份则明确为 `cuktech-ap01-0055` / `1.0.2_0055`。

格式验证使用现有 `peer-v3` 的真实 RV32 App：976 B，SHA256 `fb31b1f290baae3ff25585f924064f2f0e7941a1b31b95a0834e4cc7b8e0da89`，两次独立基址链接后归一映像相同，零未解析导入。这是离线包验证，没有在新版硬件执行 App。

验证同时发现本机 GCC 8 的两个既有构建兼容问题：`<cstdio>` 在宏安装后取消 `snprintf` 宏，以及合法本地 `R_RISCV_CALL(18)` 未被提取器接受。分别通过提前包含 `<cstdio>`、严格核对 AUIPC/JALR 与本地目标解决，不改变包或函数表。业务 App 虽可链接且零导入，但本机 GCC 8 libm 含 44 个绝对 HI20 和 84 个 LO12_I，仍被提取器拒绝。没有降低检查或生成不安全业务包；后续在当前 WSL 复用 GCC 12.5.0 工具链已解决这一构建限制，并运行真实业务包的双基址 QEMU 验证，详见上方后续报告。这不要求修改现有已发布 App 包。

## 构建与验证

```powershell
python -B tooling/scripts/build-firmware-0041.py --target 0055 --build-dir build/0055/base --output build/0055/ap01-0055-base.bin
python -B tooling/scripts/build-firmware-0041.py --target 0055 --boot-app-v3 --build-dir build/0055/app --output build/0055/ap01-0055-app.bin
python -B tooling/scripts/test-rom-target.py --target 0041
python -B tooling/scripts/test-rom-target.py --target 0055
python -B tooling/scripts/test-rom-migration-0055.py
python -B tooling/scripts/test-stock-screen-count.py --out build/0055/stock-count-tests
python -B tooling/scripts/test-firmware-0041.py --manifest build/0055/ap01-0055-app.manifest.json
```

未指定 `--target` 仍构建 0041。0055 应用版是独立 App 加载平台，不使用旧 `--app-config` 将业务静态链接进 ROM。完整发布产物和校验结果位于本地 `build/0055-migration-20261106/`。

最终两版 RV32 编译、零导入链接和镜像重建校验通过。旧版 0041 完整构建及无兄弟仓库的独立副本构建通过；隔离副本 OTA 检查 8 项中 7 通过、1 项按原有条件跳过。生产 `screen_host_0041.c` 使用 MSVC 严格编译并执行：0041 为 127 项，0055 为 139 项，覆盖原厂边界、两个 App 的页面冲突和 Pet→App→Settings 双向导航。MSVC 测试未启用 sanitizers，也未执行原厂 UI 或 RV32 指令。

生产 APX2 解析器与 SHA256 实现另经 MSVC 原生执行验证。原有损坏字段、截断、读取失败、预算和 BSS 测试通过；976 B peer 包在两个合成 RV32 基址加载成功，2 处修正及缓冲区保护通过，实际包截断和内容损坏均拒绝。这验证了生产加载器对既有格式的接受和加载，不是 App 指令执行或业务 App 的实机验收。

| 首轮历史候选（最新版本见后续 QEMU 报告） | 字节 | SHA256 |
| --- | --- | --- |
| `build/0055-migration-20261106/ap01-0055-base.bin` | 6,881,304 | `3d3ff23f864554d5b1897d04e1b0d66eb5fc71fa141563931e5a056e1a362db3` |
| `build/0055-migration-20261106/ap01-0055-app.bin` | 6,932,616 | `d853b44751f756e7416b4d1a334ea48e04cf88c850d1c05d81332d0a2c682b84` |

REA/Ghidra 12.1.4 的 35 条记录及可重载快照保存在本地 `evidence/0055-address-migration-20261106/`；同目录保留服务布局、字体、原厂页序和地址对应报告，`index.json` 记录摘要。关键 REA 证据：malloc `ev_b3fadb155bf831e9bf33fcaa4d5e620eed2a20d8a52454518f8e562987256977`，定时器 `ev_43e1ac2a4a70b68c9240a7fbe297f4b3b1ed47f52de6cf709a37eab7010ca057`，新原厂页构造器 `ev_b4e3192b3cb44a1fae0c98701bdd8e88bb7b8cacd7b91b11acbcfea512b50722`，11 页初始化字节 `ev_931c89db80787161947d6239784e585b622c4defa66c02a479c8470107d567e4`。

反编译器将部分 memcpy/memset 调用误标为不返回，并有自定义指令或函数边界限制；相关调用不能仅凭截断伪代码判断，已结合实际指令、原厂字节和历史 0041 证据核对。完整硬件启动、原厂页面/旋钮、Wi-Fi、OTA/切槽、旧业务 App 与数据恢复仍须实机验收；候选继续标记 `flashable=false`、`hardware_verified=false`。
