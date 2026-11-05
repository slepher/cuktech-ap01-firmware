# 生产执行内存后端与重启加载

2026-11-05：生产 `native_platform_v3_0041.cpp` 不再传空执行后端。平台对象持有 `Ap01NativeExecMemoryV3`，启动列表仍由 AUT3/AMF3 决定，APX2 校验、重定位、BSS 初始化和三个入口调用复用已有实现。

## 分配与发布

- 每个映像按 image+BSS 大小从现有平台 malloc 分配，额外预留 15 B 对齐空间，不预先占满 4 MiB。分配器自身元数据仍由原分配器负责。
- 只接受整个返回缓冲区位于 `0xa8000000..0xa8400000`；ROM 堆还包含较小 SRAM，不能把任意 malloc 返回值当可执行地址。范围是固定 ROM 静态映射和 QEMU 执行证据，不是物理容量验收。
- 16 B 对齐、总分配预算及最多 8 个映像；分配失败/越界拒绝，拒绝的原始分配释放。成功保留的映像（含启动失败）直到重启不释放，无热卸载 API。
- 发布检查保留区域身份、大小、text 内入口偏移和两字节对齐；同映像只发布一次。发布之前 APX2 已完成加载与摘要校验。
- 缓存顺序复用固定 ROM `0xa0029db2..0xa0029dce` 的原始编码：fence、D-cache clean-all、fence、fence、fence.i、I-cache invalidate-all、fence、fence.i。不能将 D-cache invalidate 替代 clean。

固定原 ROM SHA256：`972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`。32 B 序列为 `0f00f00f0b0010000f00f00f0f00f00f0f1000000b0000010f00f00f0f100000`。编码名称亦由 [binutils T-Head CMO 原始补丁](https://sourceware.org/pipermail/binutils/2022-September/122738.html) 交叉核对；这不证明设备实际 cache 效果。

## 本轮证据

| 项目 | 结果 / 本机产物 |
|---|---|
| 宿主 ASan/UBSan、RV32 编译 | `build/exec-backend/host/native-app-set-report.json`；地址范围、对齐、溢出、分配失败、预算/数量、保留所有权及既有集合回归通过 |
| 完整平台候选 | `build/exec-backend/platform-01.bin`，6933864 B，SHA256 `90da79aab5809f2d01dc75c01bf3f032472700ed0391fd7d6af35cc601dff17b` |
| 实际 App | `build/app-install/d2-business-pair-worker-01/app.apx2`，205360 B，SHA256 `27bb07332aff6eef0726f48ea09c3638eadee8df2be23b652324f6fed0e0b2cb`；本轮未修改业务源码 |
| 双地址加载/完整 Bundle 安装 | `build/exec-backend/install-qemu.json`，SHA256 `bde96c6824cb0abefc4fde67b634114e8eaca8a49fcba565ff2dfe85b296a5c5` |
| 同 VM reset、绑定与 Bundle 恢复 | `build/exec-backend/reset-qemu.json`，SHA256 `ddd844e02f130806300960a152e70ebde7c7bd2a8c97568f898e2ee164c4ed24` |
| firmware CLI 五事务→实际 RV32 结果 | `build/exec-backend/client-rv32.json`，SHA256 `4013fa5abe44401dae6355c97c132e40241d74c1202bc6e91e6e0d2a5d49c060` |

所有 QEMU 均在 james.local 既有 Docker 镜像执行，CPU `rv32,xtheadcmo=true`；没有设备访问、主机安装或部署。执行地址为 `0xa8000000`、`0xa8040000`。两个 App 均经生产 reserve/publish，包括实际缓存指令，随后进入真实入口；不再使用测试专用 reserveSet/publish。

同 VM reset 后 PC 为 `0xa0000000`；精确业务文件交接，绑定与 Bundle 内容不变，可写恢复更新状态。CLI 五事务依次为 failed_rolled_back、succeeded、succeeded（单更）、succeeded（批更）、failed_rolled_back；boot_id 为 13/14/15/16/18。运行结果由 RV32 导出后应用到原 HTTP 事务，非宿主健康成功注入；失败路径执行同 VM reset 后回退。

## 可复跑入口

`test-native-app-set-v3.py` 验证后端策略；`build-firmware-0041.py --boot-app-v3` 构建已接线平台；`build-app-v3-guest-0041.py --manifest ... --peer ...` 自动链接相同生产后端并记录 CPU 扩展。`test-app-abi-qemu-0041.py --next-fixture ...` 验证同 VM reset。`test-app-set-client-http-v3.py --tcp --fail-first --rv32-results --snapshot-dir ... --tool-prefix ... --qemu-image ... --expected-image-id ...` 复用原事务五链（snapshot-dir 必须新建且为空）。所有构建使用新输出目录，不覆盖证据；QEMU 执行遵守 james.local Docker 约束。

## 证据边界

执行后端生产接线和非实机重启加载链已补齐；不能据此称为完整原厂 ROM 启动或已可部署。QEMU 分配地址来自显式模型分配器，未执行原 ROM malloc/堆初始化；VFS、网络、LVGL 和调度仍是模型。CPU 确实 reset，但运行器会重新注入 guest/持久文件。业务恢复与 OTA 更新/回退分别有链路证据，尚未把真实 Flash、原厂复位入口和全部业务状态放在同一完整 ROM 环境中执行。物理执行权限、cache、RTOS 中断/并发及真实容量按约定留待实机授权，不扩展为本轮外围功能。
