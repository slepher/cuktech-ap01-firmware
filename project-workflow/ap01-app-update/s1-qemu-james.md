# S1：james.local Docker QEMU 验证

2026-11-02。用户指定：后续 QEMU 在 `james.local` 运行，依赖只安装到对应 Docker 环境，不直接安装到宿主机。本轮遵循此约束，未部署设备。

## 环境与输入

SSH 用户 slepher，Linux x86_64；Docker 26.1.5，使用已有免交互 `sudo -n docker` 权限，未修改用户组或系统配置。复用远端历史目录 `/home/slepher/ap01-review-20261022` 中的 QEMU 二进制和模型传输脚本，只读挂载，没有重建或覆盖该目录。

- QEMU 10.1.0：`build/qemu/qemu-system-riscv32`，SHA256 `25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11`。
- 既有 AP01 模型源码 `deps/qemu-10.1.0/hw/riscv/ap01.c`：SHA256 `a74574d45a8f7de30113998821d8670ce0fe6d97cd70679e064265d1d0bbc158`。本轮只记录其指纹，不声称重新验证了二进制与源代码的构建对应关系。
- 既有 `run-qemu-ap01.py`：SHA256 `28d04c47a497ba2c4caaf646ed651e01558545ba71f0345682e8f8972dc60a02`。
- 输入仍是上一轮 152 B 最小 C++ 映像，SHA256 `01e8528d08daae49cb0c05b100be39117e8a0ecaad44bb47d52222f5b0135d38`，不是原厂 ROM 或完整业务 App。
- 本轮独立目录：`/home/slepher/ap01-s1-20261102/{container,input,output}`。

容器定义为 `tooling/scripts/Dockerfile.ap01-qemu-runtime`。基础镜像固定为 `docker.1ms.run/library/debian@sha256:f6b08b09a05725f9431502d3b5714f5c4576e82c1a84fa1debe0c24a7e0c3ec4`；运行镜像 `ap01-s1-qemu:20261102`，镜像 ID `sha256:ec3b01f1af01da8fbf716ed589ecd41dd166048456a80068c395ff6f0d506bb8`。Python 3.13.5 及动态库仅装在镜像内，包版本清单已保存；宿主没有 apt/pip 安装。

首轮默认 Debian 源下载缓慢，安装阶段 exit 137，原因未确定。改用历史 Dockerfile 使用过的清华镜像源后，容器构建成功；不把首次失败计为通过。后续运行无网络、只读根文件系统，2 CPU / 512 MiB / 64 PID 限额，UID/GID 1000，临时目录为 tmpfs，结果写独立 output 目录。未重启或修改服务器既有服务；临时容器运行后自动删除。

## 执行结果

1. 既有 `test-qemu-ap01.py` 模型合成基线：55 项全部通过。
2. 新增 `test-app-pic-qemu-0041.py`：复用上一轮 BASE32 修正器，将同一映像加载到模型片内 RAM `0x62fc0000` 与 PSRAM `0xa8000000`，每个地址使用独立 QEMU 进程。
3. 两处均返回 `[35, 36, 0xffffffff]`：正常服务调用、BSS 累加及错误服务版本拒绝均与 Unicorn 一致。每次调用检查返回 PC、SP、s0、s1 正确。
4. 每个进程限定 20 秒的调试通信预算，结束后关闭连接并回收进程。容器通过 Unix socket 调试，不映射网络端口。

运行前遇到两处适配错误：加载器不应在纯运行模式导入本机构建目录；AP01 模型要求 raw BIN 大于 4 KiB。分别改为延迟导入构建依赖和 8 KiB 合成 `j .` 占位映像后通过；旧失败日志保留，最终通过记录是 `load-qemu-run03.json`。没有为模型失败放宽加载器修正校验。

本地证据：`build/s1/qemu-james/model-baseline.json`、`load-qemu-run03.json`、`runtime-versions.txt`、`docker-build-retry.log`。报告中的测试/加载脚本 SHA 已与本地最终文件核对一致。远端原始日志在独立 output 目录。镜像和输入保留以便复验，没有残留 `ap01-s1-*` 容器。

## 复现命令

将 Dockerfile、两个加载测试脚本、`probe.bin` 和 `load-report.json` 放入上述独立目录；输入摘要必须相同。以下命令在 james.local 执行；重新验收须使用新的输出文件名。

```sh
sudo -n docker build \
  --build-arg BASE_IMAGE=docker.1ms.run/library/debian@sha256:f6b08b09a05725f9431502d3b5714f5c4576e82c1a84fa1debe0c24a7e0c3ec4 \
  --build-arg DEBIAN_MIRROR=mirrors.tuna.tsinghua.edu.cn \
  -t ap01-s1-qemu:20261102 /home/slepher/ap01-s1-20261102/container

sudo -n docker run --rm --network none --cpus 2 --memory 512m --pids-limit 64 \
  --user 1000:1000 --read-only --tmpfs /tmp:rw,nosuid,nodev,size=64m \
  -v /home/slepher/ap01-review-20261022/build/qemu/qemu-system-riscv32:/engine/qemu:ro \
  -v /home/slepher/ap01-review-20261022/cuktech-ap01-firmware/tooling/scripts:/support:ro \
  -v /home/slepher/ap01-s1-20261102/input:/input:ro \
  -v /home/slepher/ap01-s1-20261102/output:/output \
  ap01-s1-qemu:20261102 python3 -B /input/test-app-pic-qemu-0041.py \
  --qemu /engine/qemu \
  --expected-engine-sha256 25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11 \
  --support-dir /support --fixture-dir /input --output /output/load-qemu-run03.json
```

模型基线使用相同容器/挂载，命令改为 `python3 -B /support/test-qemu-ap01.py --qemu /engine/qemu --output /output/model-baseline.json`。

包源未锁定 Debian snapshot，因此未来重建镜像可能得到不同包版本；本轮复验身份以镜像 ID 和保存的包清单为准，不能把 Dockerfile 等同于跨时间字节可复现承诺。

## S1 边界

模型允许从模拟片内 RAM/PSRAM 取指，不能据此证明真实 0041 的权限、缓存一致性、中断安全或可用容量。本轮没有启动原厂 ROM，没有运行完整业务 App，没有在设备上加载代码。最小样本的搬移执行现有 Unicorn 与 QEMU 两份相互独立的执行结果；完整 App 的 C 服务边界、最终受限修正、实机执行内存和存储掉电准入仍未完成。

## 2026-11-03：APX2 五入口与生产加载器执行

旧镜像已被清理，QEMU 二进制与历史传输脚本仍在且摘要未变化。按同一 Dockerfile 和固定基础镜像重新构建 `ap01-abi-qemu:20261103`，镜像 ID `sha256:0478bf66b12b274e5d365560dfbc0869897abc6dc80ef974066df04d98e69681`。Dockerfile SHA256 `01db3b83aecce473acd37119404e371f7ae9551bd1ee20609637b079d58ccb77` 与本地一致。依赖仍只安装在容器，未安装宿主包。独立输入/输出位于 `/home/slepher/ap01-abi-20261103/{input,output}`；验证容器已退出。

本次不再使用旧 ProbeServices ABI：`probe_app_abi_v2.cpp` 使用正式五入口签名，带 data 函数指针修正和 bss 状态，通过服务表 invoke 调用固件。两处独立链接（0x10000/0x30000）归一化结果一致；映像 356 字节、含 bss 372 字节、完整 APX2 包 620 字节，包 SHA256 `0505f3b8a54a185aa72a29e4e39f1259610e21eb13778d0e177e14ef58d1e5ef`。

`probe_app_image_guest_0041.cpp` 与生产 `apx2.cpp`、`app_image_0041.cpp`、`app_lifecycle_0041.cpp`、`native_sha256_0041.cpp` 一起编译为 6,744 字节 RV32 验证程序，SHA256 `265f16e4383f72756eedf062896b95549b1bf3711ea37dcee76ce12e18adc64b`。QEMU 内由这些生产代码校验 APX2、复制/修正/清零、经测试后端 fence.i 后进入样本，而不是由 Python 预先重定位后直接跳入样本。

同一包在 `0x62fca000` 和 `0xa8000000` 两处均完成：

- start 服务表回调、event 更新状态、health 确认入口状态。
- prepare_stop 首次 Pending，已有代际引用排空前不释放，stop 成功后释放。
- 同地址重新加载、第二代再次执行全部入口，旧代际拒绝。
- 错误期望摘要在分配前拒绝。
- 返回 PC、SP、全部整数被调用者保存寄存器保持。

最终报告 `build/app-install/qemu-james/abi-run02.json` 的脚本/程序/包/构建清单指纹均与本地核对一致。重建环境下模型基线 55 项也通过，报告 `build/app-install/qemu-james/model-baseline.json`。首个链接因验证程序缺少 strcmp 失败，补齐后构建成功；未修改生产校验器来迁就样本。

本机构建（空输出目录，使用既有 pyelftools 环境，不运行 Unicorn）：

```sh
mkdir -p build/app-install/abi-qemu-v2
build/s1/python/bin/python -B tooling/scripts/build-app-abi-probe-0041.py \
  --out build/app-install/abi-qemu-v2 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

将 `app.apx2`、`guest.bin`、`build-report.json` 及 `test-app-abi-qemu-0041.py` 上传独立 input；Docker 运行沿用本页隔离选项和只读 engine/support/input 挂载，镜像改为 `ap01-abi-qemu:20261103`，input/output 改为 `/home/slepher/ap01-abi-20261103`；容器命令为：

```sh
python3 -B /input/test-app-abi-qemu-0041.py --qemu /engine/qemu \
  --expected-engine-sha256 25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11 \
  --support-dir /support --fixture-dir /input --output /output/abi-run02.json
```

复验必须使用新输出文件名。固定地址预留和 fence.i 仅为模型测试后端，不加入生产平台构建清单；不能推导真实 AP01 的执行权限、缓存同步或中断安全。仍不是完整 ROM 启动、完整业务 App、实际堆容量或端到端安装服务在 QEMU 中运行的证据。

2026-11-03 核心服务追加验证：五入口样本改用正式 `AP01_CORE_RANDOM` C 助手；guest 使用生产 `app_core_0041` 的代际校验与分发，测试端随机源返回确定值。输入在 `input/core`，本机构建在 `build/app-install/abi-qemu-core`；guest 7,128 字节 SHA256 `acb73322b073bceb3b89c7954281f981d5cdea372ed8a222389a1e41c9a9037f`，包 SHA256 `9263e45a86de264c852989f9aa92ba94f4b17f139ad901d5430cf16cce2148dc`。同一镜像/引擎/脚本，两基址均通过，报告 `build/app-install/qemu-james/abi-core-run01.json`。本轮没有重新跑未变化的模型基线；该镜像 55 项基线结果仍为前节报告。此前 probe 中未规范的 service=1/op=1 回调由正式核心操作定义替代，旧样本/旧报告仅是历史证据。


## 2026-11-03 私有堆运行库小样本

复用已有 Docker `ap01-abi-qemu:20261103`，image id `sha256:0478bf66b12b274e5d365560dfbc0869897abc6dc80ef974066df04d98e69681`，未安装宿主依赖。输入目录 `/home/slepher/ap01-abi-20261103/input/heap-v2`；输出 `/home/slepher/ap01-abi-20261103/output/abi-heap-run01.json`，本地报告已取回并与 guest/package/build report SHA 核对。

使用原有引擎/runner 指纹，容器 --network none、只读根、2 CPU、512 MiB、64 pids；两基址 0x62fca000/0xa8000000 返回 0，全部整数保存寄存器和 SP 保持。生产堆服务、私有 malloc/nothrow new 等运行库实际执行；两代 reload、堆预算拒绝、stop 前数据存活、资源 drain 清零通过。guest SHA `c5c78102c164d7316e26c364e27239e49ab98520549180c41c99c0c63b695b98`，APX2 SHA `7264196d304bfb1341dce0a2f5d2375c69a21701e5806e619c9cb05b291838c2`。

构建入口 `build-app-abi-probe-0041.py`，本地输入 `build/app-install/abi-qemu-heap-v2`，报告 `build/app-install/qemu-james/abi-heap-run01.json`。依然是小样本与固定模型内存；不证明完整 ROM 启动、真实业务 App、物理 cache/MPU 或实际堆预算。


## 2026-11-03 私有 time() 服务调用

复用相同 `ap01-abi-qemu:20261103` Docker 镜像/引擎，输入 `/home/slepher/ap01-abi-20261103/input/time`，报告 `build/app-install/qemu-james/abi-time-run01.json`（已取回并核对三个输入 SHA）。两个基址及两代重载均返回 0，SP/整数保存寄存器保持；包内 time() 经实际 core UTC 服务读到模型提供的 1700000000 秒，原 heap/new/delete/calloc/realloc/排空验证同时通过。

guest 11992 字节，SHA `6c1e06cf13a57bc9101ad68f4f5b02620f658be536df9a7a908a4608c29cb622`；包 SHA `3361e9f052818d1efdde61938eb80a28d36dba2c64159131402339d51bccccd8`。无宿主安装、无实机/部署；不证明真实 RTC、完整业务 App 或物理执行内存准入。

### 2026-11-04 共享平台真实单包回归

远端旧运行镜像已不存在，按同一 Dockerfile、固定基础摘要和清华容器软件源重建 `ap01-abi-qemu:20261104`，镜像 ID `sha256:02aba83405eefd37e9c529a84ae0e26cf7d8e79a7749dc2d48e991fe8101c0cc`。依赖仅安装在容器内；未改动已有服务。引擎、support 和 runner 摘要与前次一致。首次命令误写引擎预期摘要，在执行前被身份检查拒绝；修正后通过。

输入 `build/app-install/d2-shared-guest-01`，远端同名目录位于既有 input 下；输出 `build/app-install/qemu-james/d2-shared-run01.json` 已取回。guest SHA256 `e63b5eff1ae0730ee60d4ef32e7de6b3dbfe4c98db8ce435f186eba351639871`；真实 App 包仍为 D1 的 `581eafe33e3e524a3aefdb32e30905be75be304cfa202f14efcdbda113de1dcc`。两个基址均返回 0，保存寄存器和栈保持，输入三项摘要与本地一致。这是共享所有者改造后的单包回归，未执行真实双包集合，也不是完整 ROM 或实机验证。

### 2026-11-04 真实双包集合执行

复用 `ap01-abi-qemu:20261104`，输入 `d2-set-guest-01`；runner 上传为 `test-app-set-qemu-0041.py`（本仓 `test-app-abi-qemu-0041.py`，SHA256 `25c94487e6fd3302df2f6d70b8c543189ba1bf843e3fb084ec472b60b5a47ef2`）。新增 `set.amf3` 输入地址 0xa81c0000、`peer.apx2` 地址 0xa81c1000；执行池按 16 B 对齐推进。基址 0xa8000000 和 0xa8040000 均返回 0，栈和保存寄存器保持。

报告 `build/app-install/qemu-james/d2-set-run01.json` 已取回；guest、主包、构建报告、Manifest、peer 五项输入摘要与本地一致。guest SHA256 `eee01f5cd36199d11952db42e0f7618dd4209c2aa9c86c17ea7d6ed255330b9a`，Manifest 文件 SHA256 `ec95e0a813a6a02a7feb16d502424a59f2f12e0c483625c32f5fb293510a7b33`，peer 文件 SHA256 `98966125e3c3ffb8a8e7dd7d993880da74ac268391aa5e6aabef9791f4473faa`。三条实际后台任务运行，peer 页面可进入，两个 App 的窗口重建不创建新线程或监听。底层仍为前述模型替身；生产文件入口、硬件缓存/权限不在此证据范围。

### 2026-11-04 文件暂存到真实双包

`d2-files-guest-02` 使用生产 `Ap01NativeAppFileBootV3` 与 `app_set_files_v3`。模型仅提供文件 I/O：按 `/resource/app-store/current.amf3` 及摘要包路径读取三个输入；stage 完成后禁用该 I/O，后续 UI 载入仍成功，证明没有在 UI 阶段重开文件。Manifest/主包/peer 与前次相同。

既有 Docker 镜像/runner 下两个基址通过。报告 `build/app-install/qemu-james/d2-files-run02.json` 已取回并核验五项输入；guest SHA256 `06b8de3cd93dbc1414808ad4ac53f136a62a8200644e5acdc19732783e7a73d2`。仍覆盖三任务、peer 页面和两包窗口重建。模拟 malloc 不回收，仅宿主 ASan 测试验证实际暂存对象释放；不声称模型验证了真实堆回收、VFS 持久性或完整原厂启动。

### 2026-11-04 健康观察回归

`d2-watch-guest-01` 继续执行相同真实双包，增加集合监督断言：两包 healthy、窗口删除后 window_absent、重建后 healthy、停止发布 UI 快照并推进 5001 ms 后 ui_stale。监督 tick 由 guest 显式调用，原生独立线程的创建在完整候选编译/链接中检查；不把该注入当作真实 RTOS 卡死或硬件看门狗测试。

报告 `build/app-install/qemu-james/d2-watch-run01.json` 两基址通过并核对五项输入。guest SHA256 `dc96687226a35876501e01b29964ad2da9841b24013a861b07b4d67654b1eeaa`。Docker 镜像/runner/引擎沿用前次，未安装宿主依赖或访问实机。

### 2026-11-04 分别冻结真实工作线程

`d2-beats-guest-02` 载入心跳版业务包及 peer，先完成既有双包启动/页面/窗口重建验证，然后逐个跳过业务、peer、发现线程调度；每次保持 UI 与其他线程推进 200 轮（每轮模型时间增加 100 ms），断言所属 App Failed、另一 App OK。恢复全部线程后 App health 回到 OK；最后一次故障被平台锁存，恢复后不清除。

`build/app-install/qemu-james/d2-beats-run02.json` 两基址通过，五项输入摘要与本地一致。guest SHA256 `a609247c4cd6fff250d78f5ab913df4462e48cc58e7c3996e5842c4a9ae816fb`；主包 SHA256 `7325faf42b12c57d892e76ca2517ae45393c77baf7dc00c2f81ff6dfdcdf1656`，peer SHA256 `93ebd331efc55e0f0adaabda2239ae81288367d72762ec33a1286b9a7dd56cad`。真实指令执行依然使用模型 ROM I/O 和协作调度；这不是硬件抢占/整机死锁恢复测试。

### 2026-11-04 实际 worker 许可恢复

`d2-resume-guest-01` 继续运行双包及线程停滞断言，末尾显式授予模型写许可。实际业务 worker 创建 Bundle 目录一次并恢复健康；持续许可不重复创建。撤权后再次开放并注入 mkdir 失败，health Failed，继续调度也不重复尝试。最后关闭集合门。模型未实现 Bundle 持久文件成功提交，此项由真实 Bundle 宿主测试补充。

`build/app-install/qemu-james/d2-resume-run01.json` 两基址通过，五项输入摘要核对一致；guest SHA256 `4ff31432cca7cbb2a1ecb55b90224e104618f997285621dadc077d246e909247`。新的业务包 SHA256 `c3bf0c7d4a01d6788532cf178c7f8e969862af5088c42062b522df5eec5e9913`，peer 不变。许可是测试注入，不是 D3 持久事务或实机结果。


## 2026-11-04：真实双包 AUT3 选择与健康提交

输入 `build/app-install/d3-journal-guest-01/`，报告 `build/app-install/qemu-james/d3-journal-run01.json`。james.local 既有 `ap01-abi-qemu:20261104` Docker，image `sha256:02aba83405eefd37e9c529a84ae0e26cf7d8e79a7749dc2d48e991fe8101c0cc`；同既有 QEMU/support 指纹，未安装宿主依赖。两个执行基址 `0xa8000000`、`0xa8040000` 均返回 0，栈哨兵/保留寄存器通过；取回报告后核对 guest、业务包、build-report、Manifest、peer 五份输入指纹一致。

- guest SHA256：`ddd5f5c1c2fe24c16125134b0c01886a86d0bd2a49372a6fca5aa1b3e30eb862`。
- 业务包：既有 `d2-business-resume-01/app.apx2`，SHA `c3bf0c7d4a01d6788532cf178c7f8e969862af5088c42062b522df5eec5e9913`；peer 和 Manifest 与 d2-resume 输入一致。
- 开机预置合法 SwitchPending 模型记录，实际 AUT3 load/select 消耗 trial，再通过 stageSelected 按摘要找到完整 AMF3/APX2。UI 执行两个真实 App，真实三 worker/页面切换/窗口重建继续通过。
- 用实际 supervisor/healthSelected 连续观察健康，观察前写门关闭；实际日志保存 Succeeded 后才开放写入，真实业务 worker 初始化一次。重新 load 双记录仍为 Succeeded。逐个冻结真实线程保留索引健康检查，最终平台故障锁存并撤销写许可。

边界：预置事务不是 HTTP 上传/commit；日志是 guest 中的 2×320 B 可写模型槽，VFS write 的同步由模型约定，不证明真实 Flash 耐久性。没有模拟整机复位或回退包实际重载；AUT3 掉电/回退决策另有宿主测试。ROM 网络/LVGL/维护、调度与时间仍为模型；未启动完整 ROM、未调用真实 reboot、未触碰实机。原有 `d2-resume-run01` 仍保留显式写许可与恢复失败测试，本次是新增持久批准路径。

## 2026-11-04：当前 AUT3 format 2 与运行集合快照

输入 `build/app-install/d3-journal2-guest-01/`，取回报告 `build/app-install/qemu-james/d3-journal2-run01.json`。沿用已核验的 james.local Docker 镜像 `sha256:02aba83405eefd37e9c529a84ae0e26cf7d8e79a7749dc2d48e991fe8101c0cc` 和前述引擎/support/runner；容器 network none、只读根和输入、512 MiB/2 CPU。未在远端宿主安装依赖。

guest 由当前生产源码重新构建，SHA256 `54312d89a28958980f55863833270f6bf8c7149a1f0ef41774be67dfc53ec26a`。新增 format=2、两包完整 received 偏移编码和 Succeeded 重载保留断言，以及 runtime() 的 started=2、complete、健康状态、Manifest 版本/摘要和各包运行摘要核对。既有真实两 App/三 worker/窗口重建/连续健康批准/写许可/逐线程停滞和栈哨兵检查保留。0xa8000000、0xa8040000 均返回 0，保存寄存器保持；五份输入摘要与本地一致。

构建命令：`python3 -B tooling/scripts/build-app-v3-guest-0041.py --out build/app-install/d3-journal2-guest-01 --package build/app-install/d2-business-resume-01/app.apx2 --manifest build/app-install/d2-resume-set/set.amf3 --peer build/app-install/d2-peer-beats-02/app.apx2 --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-`（输出目录须预建且为空）。执行复用上述 Docker 挂载，运行 `/input/test-app-set-qemu-0041.py --direct-v3`，fixture 指向新输入目录、output 指向新报告。

边界保持：仍预置 SwitchPending，内存双日志、模型 ROM I/O/时间/协作线程；尚未串起 HTTP 安装、CPU 重启、回退集合重载和垃圾清理。没有完整原厂 ROM 启动或实机操作。此前 format 1 的报告仅作历史证据，本报告覆盖当前 format 2 启动/健康路径。

## 2026-11-04：HTTP 提交文件驱动 RV32 启动

新增宿主测试 peer 的 `SNAPSHOT` 只读命令：在响应 commit 后、下一次推进模型重启时钟之前，导出模型文件的精确字节。`test-app-set-client-http-v3.py --snapshot-dir <预建空目录>` 保存原事务响应、文件映射及指纹；不修改服务或伪造 SwitchPending。四链 HTTP 回归通过，导出 `build/app-install/d4-http-snapshots-01/commit-{0..3}.json`，报告 `build/app-install/set-snapshot-tcp-v3-report.json`。新版 C++ 宿主 ASan/UBSan 102896 检查及相关 RV32 编译通过。

`build-app-v3-guest-0041.py --snapshot <commit.json> --out <预建空目录> --tool-prefix <既有工具前缀>` 从双 AUT3 format 2 日志选取最新记录，核对 CRC/事务 ID/阶段，再按持久摘要选 AMF3 与两包并做完整包校验。guest 直接载入这两份日志（0xa81ff000 的长度头+双槽），不再编码初始记录；实际生产 journal/selector 消耗试运行，真实两 App/三线程启动、全体健康后持久 Succeeded 并开放写入。暂存文件/包仍由模型 VFS 提供。

前三份（首装、A 单更、A+B 批更）已生成 `d4-http-guest-00/01/02`，沿用 james.local 的锁定 Docker 镜像、QEMU/support/runner 执行。`build/app-install/qemu-james/d4-http-run00/01/02.json` 各两个基址返回 0、栈/保存寄存器通过。六项输入（guest、主包、构建报告、Manifest、peer、双日志）及原始快照指纹均与本地一致；单更 B 包 SHA 与首装相同。共同 guest SHA256 `2f3b12847d817fad7fa8dabb1dd9aeff24944d22405978bb20209b1318e7cd79`。

准确边界：HTTP 服务在宿主运行，落盘为模型；QEMU 是独立全新 CPU 进程，尚不是同一 VM 内 HTTP→硬件 reboot 的连续执行。四次宿主事务的前置成功仍由宿主健康模型建立；QEMU 健康结果还没有反向交给客户端决定下一事务。第 4 份失败快照已捕获，但候选失败→CPU 再启动→旧集合重载尚未串联，不能宣称完整端到端或回退闭环完成。无实机访问、宿主依赖安装或生产 Bridge 启停。

## 2026-11-04：RV32 候选失败日志→旧集合实际重载

构建入口增加 `--boot-mode fail-trial` 和 `--boot-mode rollback --resume-journals <上次导出文件>`，均要求原始 `--snapshot`。失败模式先执行真实候选双 App/三线程，再跳过实际业务 worker 调度，保持 UI 与另外两线程推进；生产 supervisor 判定 AppFailed，healthSelected 写入 RollbackPending 并要求重启，写门保持关闭。guest 导出生产 VFS 模型实际写入的双 AUT3 槽，不由 Python 制造回退记录。

runner 新增按构建报告固定地址 0xa81ff000/648 B 导出双槽，每个基址独立保存并报告 SHA256；远端新文件为 `/input/test-app-set-resume-qemu-0041.py`，SHA `0320f1d83ca2bbd462f51c6e33cd73dee0c44e0adc3937fcba24f75d215cfa75`，原 runner 保留。james.local Docker 镜像/引擎/support 及资源隔离沿用已核验基线。

- 失败输入 `d4-http-fail-guest-01` 使用第 4 份 HTTP commit 快照；guest SHA `cf21c953dc436bdd61af5bb759459736956365760c2704cfba21a4372ac54f30`。`qemu-james/d4-http-fail-run01.json` 两基址均通过，输出日志 SHA 均为 `e3bab0c23de4a0ff615224640a6d6b9cbe9f73bba7a45abdb4da97311605e5fb`，phase=RollbackPending、trialStarts=1、rollbackStarts=0。
- 回退输入 `d4-http-rollback-guest-01` 使用上述原样日志以及同一 HTTP 快照中的 oldDigest/oldVersion 对应文件。guest SHA `87cb3a5f5734e0a98fde613b34e6b2c60f4b077d2379fb33e96b8fab212e9891`。`qemu-james/d4-http-rollback-run01.json` 两基址均实际运行旧双 App/三线程、页面/窗口重建和连续健康批准，持久 FailedRolledBack 后开放写许可。两基址日志 SHA 均为 `5570bb2c46dcd1861e3f434a3fd385ac8e12998fe8ace2541e14ee7f2fba82f5`，trialBoot=42/rollbackBoot=43，两个消耗计数均为 1，cleanupPending=1。
- 输入六项及输出日志指纹已核对；旧 Manifest、主包、peer 与第 3 次成功批更的三个文件逐一同 SHA，证明没有混合候选/旧包。

边界：这是两次独立 QEMU CPU 进程之间传递真实模型日志的回退加载，未调用同一 VM 的硬件复位，未接生产 Flash。终态日志导出时先保留健康批准结果，随后原有线程停滞回归仍运行；不能把导出结果当作退出时实时健康。客户端终态/清理还没有接收此次 RV32 结果，回退失败再进入维护、无旧集合首装失败等完整链路继续开放。未操作实机。

相同导出机制的正常批更回归 `d4-http-export-guest-01` / `qemu-james/d4-http-export-run01.json` 双基址通过；guest SHA `3b462de3c1ce7d17fcac25daea49471a136330ef740c26f8866d895a6c397fd0`，终态日志 SHA `1b4af2330064a0b873b59453daa1d554fd31d0ae8f07d256697460a7bc916110`。六项输入与日志校验通过，Succeeded/trialStarts=1/rollbackStarts=0/cleanupPending=1，未要求第二次正常启动。

## 2026-11-04：回退也失败→第三次启动维护

新增 `--boot-mode fail-rollback`：使用实际候选失败导出的 RollbackPending 日志，加载并执行旧双 App；真实旧 worker 停滞后，生产监督/selector 持久 RecoveryRequired，返回 Maintenance，写门保持关闭。`--boot-mode maintenance` 使用该日志启动 boot=44，stageSelected 不尝试任何 App，重复 poll/stage 5 次仍为 Maintenance，taskCount/mounts=0、可执行池 cursor 不动，模型维护监听仅启动一次；双槽内容、序号和消耗计数均不变。

james.local Docker 镜像/引擎/support 及隔离不变。新 runner `/input/test-app-set-maintenance-qemu-0041.py` SHA `929535b54cdbfbf809238dbbe35468d31432cdb6a504cf29231d04b495aaa004`，维护模式报告明确 `production_apx2_loader_executed=false`、`real_abi_v3_app_executed=false`、`no_app_maintenance_verified=true`，不把零 App 执行误报为真实集合启动。

- `d4-http-rollback-fail-guest-01` / `qemu-james/d4-http-rollback-fail-run01.json` 两基址通过；guest SHA `03b9a96341065929af5368a36e87d4282cd6e91ae1e13c462f71a7f84c37b58b`。
- `d4-http-maintenance-guest-01` / `qemu-james/d4-http-maintenance-run01.json` 两基址通过；guest SHA `10d41d3227a15f7c32166db566f2b75e048f9db5a1b229f888a234c07e041a5b`。
- 两阶段输入六项与输出日志 SHA 已核对；RecoveryRequired 日志 SHA `b421a3ea443be65d2ec966ed8e0b27f146c4e74d706f89b315763f376d8b159a`，trialBoot=42/rollbackBoot=43、计数均 1。第三次启动输入/输出双日志逐字节相同。

复现沿用 snapshot 构建命令；fail-rollback 的 resume-journals 指向 `d4-http-fail-run01.a8000000.journals.bin`，maintenance 指向 `d4-http-rollback-fail-run01.a8000000.journals.bin`。两个基址的上游日志一致，均已核验。

边界：维护监听仍为模型，不证明真实网络救援/完整原厂 UI；三次执行是独立 CPU 进程的文件传递，不是同 VM 硬件 reset。RV32 原生 HTTP 与客户端结果闭环、空集合首装失败后的再安装、设备资源预算/孤儿清理等继续开放。未安装远端宿主依赖、未部署或操作实机。

## 2026-11-04：同 VM QMP 复位链

runner 增加可重复的 `--next-fixture`（最多总共三阶段），复用既有 support.QMP 的有界命令，不启动新的模拟器来替代后续启动。每阶段执行实际 guest 后读出双日志，下一阶段必须与预期 journal 输入逐字节一致，否则在 reset 前拒绝；实际传入下一阶段的是刚读出的字节。随后取消断点、QMP `system_reset`、确认暂停和 PC 已回到 reset 地址，再装入下一阶段 guest/输入。构建报告增加 ELF `__guest_bss_start/end` 的 address/size；每次启动清零该 guest BSS，并恢复 .data 初值，避免把旧调度上下文带入新启动。

当前 runner `/input/test-app-set-reset-qemu-0041.py` SHA `25c6208aeea65f538f06622c5e1c323b8e0df80a84f6a95c18be50221b3d16ad`。所有运行仍在 james.local 同一锁定 Docker 镜像/引擎/support 与原有隔离限制内。输入 `d4-reset-{fail-trial,rollback,fail-rollback,maintenance}-01` 均重新构建带 BSS 元数据。

- `qemu-james/d4-reset-rollback-run01.json`：fail-trial → 一次 QMP reset → rollback；两个基址两阶段均返回 0，最终日志 FailedRolledBack 与此前一致。
- `qemu-james/d4-reset-maintenance-run01.json`：fail-trial → reset → fail-rollback → reset → maintenance；两个基址三阶段均返回 0，第三阶段无 App 启动，RecoveryRequired 双日志不变。各基址两次 reset 保持同一 QEMU PID（6 / 10），PC 都为 `0xa0000000`。
- `qemu-james/d4-reset-mismatch-run01.json`：故意将 fail-trial 输出接到 maintenance（需要 RecoveryRequired 而实际为 RollbackPending），按预期 `journal handoff mismatch`，无 reset/第二阶段执行；这是负向检查，不是成功运行报告。

三个报告及每阶段输出日志已取回；逐一核对每个构建报告及其所有输入摘要、全部阶段输出摘要、日志传递字节、reset 次数/同 PID/reset PC。正常回退最终 SHA `5570bb2c46dcd1861e3f434a3fd385ac8e12998fe8ace2541e14ee7f2fba82f5`；维护 SHA `b421a3ea443be65d2ec966ed8e0b27f146c4e74d706f89b315763f376d8b159a`。

复现：既有 Docker 命令的 runner 改为上述新文件，`--fixture-dir /input/d4-reset-fail-trial-01 --next-fixture /input/d4-reset-rollback-01`；维护链将 next 改为 `/input/d4-reset-fail-rollback-01` 再追加 `/input/d4-reset-maintenance-01`。每次输出用新名称。

准确边界：现已验证同一模型 VM 的 CPU reset，复位后按测试引导加载新 guest/BSS，持久存储由宿主保存的实际模型槽模拟；不是完整原厂 Boot ROM 的启动路径，也不是原厂 reboot 寄存器/Flash 行为。HTTP 仍在宿主，QMP reset 由测试协调器触发，RV32 结果尚未闭环给原客户端或完成清理。此前“独立 CPU 进程传递”的记录保留为历史，本节补充同 VM 证据；不声称完整端到端/实机已验。

## 2026-11-04：首次安装失败后的空集合与重装

HTTP 测试增加 `--fail-first`（当前限 Python CLI）：在原四链前插入一次失败首装，随后以新 operation_id 重装完全相同的候选 Manifest/版本。`build/app-install/set-empty-retry-tcp-v3-report.json` 五事务通过，boot_id 为 13/14/15/16/18；首次终态 FailedRolledBack、runtime 为完整健康空集合（零摘要/版本/运行列表），cleanup_pending=false。相同 Manifest 的新事务安装成功后，继续 A 单更、A+B 批更、失败整集回退，清理均完成。已核对首次失败与重装 operation_id 不同、候选摘要相同；掉回复仍走原事务恢复。快照存放 `d4-empty-snapshots-01/commit-{0..4}.json`。

RV32 构建新增 `--boot-mode empty-rollback`，要求上游真实失败日志且 oldVersion/digest 均为零。测试输入仍携带候选包以便统一 runner，但空回退不得读取/装载这些包或分配执行池。生产 stageSelected 跳过 Manifest 文件、保留维护监听，由监督器确认无 App 的健康集合，30 秒观察后持久 FailedRolledBack，trial/rollback 各一次、cleanupPending=1。runtime.started/count/version/digest 均为零，taskCount/mounts=0。

james.local Docker 新 runner `/input/test-app-set-empty-qemu-0041.py` SHA `63ddfaf974fd419089f7b936e54c006256340cfeca86a2f5b9a6c8e00ea21fd5`，同既有镜像/引擎/support/隔离。`d4-empty-fail-guest-01` 的 guest SHA `7e6f8dbec8034415b947821834df4bfc2b427a87b6e7a7178f40375f669ba0db`，`d4-empty-rollback-guest-01` 为 `46e380b87548cdd06176f850259221d165a5d65acaab40982f9f59bf105fe1fc`。`qemu-james/d4-empty-reset-run01.json` 两基址均在同 VM 完成 fail-trial→QMP reset→empty-rollback，PC 复位到 0xa0000000，各阶段返回 0。输入/输出指纹已核对；终态双日志 SHA `c5e2188077bafa13e9c379cd670a8f7aca433bdb0806d89b5839a75638d20e9f`，old 集合身份为零、计数均 1。

复现沿用现有命令：HTTP 四链命令加 `--fail-first --snapshot-dir build/app-install/d4-empty-snapshots-01`（须空目录）；RV32 fail-trial 输入用 commit-0，empty-rollback 的 resume-journals 用 `d4-empty-fail-run01.a8000000.journals.bin`；runner 用 `--fixture-dir /input/d4-empty-fail-guest-01 --next-fixture /input/d4-empty-rollback-guest-01`。

边界：宿主 HTTP 已证明清理后同包重装，RV32 已证明同 VM 的空集合健康回退；尚未将 RV32 输出终态送回 HTTP 服务/客户端驱动后续重装，不合并声称一个连续端到端证据。Flash/原厂引导/网络仍为模型，未操作实机。

## 2026-11-04：RV32 终态回到原 HTTP/CLI 事务

guest 新增与双日志同一时刻的测试用 `ARV3` 运行快照（0xa81ff300，912 B，显式 LE 编码），来自 `boot.runtime()`：实际 boot ID、集合版本/摘要、启动数量、complete、监督健康/采样时间、逐 App ID/版本/摘要/健康与执行顺序。正常/回退健康批准时先导出，再执行原有后续故障回归；失败路径导出当时实际故障快照。该格式仅为测试跨架构桥，不是新增设备协议或持久 ABI。构建可指定 `--boot-id`，按原 HTTP boot_id+1/+2 递增，不再假定所有事务都使用 42/43。

宿主 C++ 测试 peer 增加 `APPLY`：只接受当前 SwitchPending 原事务的 RV32 终态，核对 MAC/操作 ID/请求指纹、旧/新版本和摘要、接收偏移/掩码/总量、单次试运行及清理标记；再核对导出 runtime 的 boot ID、完整健康集合和持久 Manifest 各成员。该分支跳过宿主 selector/健康注入，以实际 runtime 提供生产 service.runtime()，随后由生产 service.tick()/cleanup/HTTP serializer 完成清理和结果报告。其他既有测试仍可使用宿主模型健康。

新增协调脚本 `tooling/scripts/run-app-set-rv32-result-0041.py`：仅使用 james.local 的固定镜像 ID 和引擎 SHA，独立 UUID 远端输入/输出目录、只读输入、network none 与既有资源限制；不安装依赖。每次 commit 后用实时快照构建/上传 guest，实际运行双基址，核对报告/输入/日志/runtime 指纹以及双基址输出一致。失败事务先预跑生成下一阶段 fixture，再以同一 VM QMP reset 正式串起候选失败/回退；正式链实际输出返回原 peer。预跑属于测试准备，不是产品额外重启。

`test-app-set-client-http-v3.py --rv32-results --fail-first` 连续五事务通过：首装失败回到空集合并清理、新 operation_id 重装相同 Manifest、A 单更且 B 不上传/身份不变、A+B 批更、候选失败整集回退。丢回复仍恢复原事务，每事务 commit 一次；客户端逐字段对照 RV32 runtime 的 boot ID、Manifest 版本/摘要、启动数量、每 App ID/版本/摘要/健康。最终 boot_id=13/14/15/16/18，全部 cleanup_pending=false，宿主不注入健康。

权威报告 `build/app-install/set-rv32-closure-v3-report-02.json`，SHA `157e8941c6d475415f87a2fcd8179960f5e7f1526bfaa705daf41cf7b61ff84e`；输入和各次详细报告/输出位于 `build/app-install/d4-rv32-closure-02/`。五组实际日志/runtime/报告摘要均已核验。首轮 `...report.json` 已运行通过，但旧汇总字段误留 `app_instructions_executed=false`；修正汇总并加入客户端逐字段对照后重新运行的 `-02` 为当前证据。宿主 C++ ASan/UBSan 102896 检查及相关 RV32 编译通过，Python 四入口语法检查和 diff check 通过。

复现（先创建新的空 snapshot-dir）：

```sh
python3 -B tooling/scripts/test-app-set-client-http-v3.py --rv32-results --fail-first \
  --binary build/app-install/test-set-journal-v3 \
  --manifest build/app-install/d2-resume-set/set.amf3 \
  --package build/app-install/d2-business-resume-01/app.apx2 \
  --package build/app-install/d2-peer-beats-02/app.apx2 \
  --snapshot-dir build/app-install/d4-rv32-closure-02 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf- \
  --report build/app-install/set-rv32-closure-v3-report-02.json
```

边界：这次是原客户端→生产 HTTP 字节处理/存储模型→真实 RV32 App/监督→原样终态及运行快照→生产清理/HTTP→原客户端的连续测试，不再是两段无反馈证据。HTTP 字节仍通过宿主管道，当前 `--rv32-results` 不支持 TCP 或 Bridge UI；App 的 ROM 网络/LVGL/时间/调度仍为模型，QMP reset/测试引导不等同原厂 Boot ROM/Flash。RV32 里未运行完整 HTTP 服务。真实网络断连、Bridge 原生 IPC、资源/写集/孤儿回收等目标继续开放；未部署或操作实机。

## 2026-11-05 回环 TCP 与实际 RV32 结果

2026-11-05 TCP/RV32 闭环：Python 原客户端经回环 TCP 完成五事务（首装失败空回退、同包重装、单更、批更、整集回退）；每事务一次 commit，重启执行期间 26 次查询原事务，实际 RV32 日志/运行快照导入后由生产服务清理并返回，boot=13/14/15/16/18，终态 cleanup_pending=false。报告 `build/app-install/set-rv32-tcp-v3-report-02.json`，SHA `436ca005efa953a19c51567a7caa759745fa1d47c750eba6471bd04cc4f9ebca`。实际 App 在 james.local Docker 双基址执行，宿主不注入健康。Bridge UI/Rust 与真实 RV32 的同次闭环、原生 HTTP/原厂启动仍待验证；未操作实机。

旧镜像 `ap01-abi-qemu:20261104` 已不存在，首次 TCP 尝试因此失败并人工中止，不能作为通过证据。复用 Dockerfile.ap01-qemu-runtime 在 Docker 内重建 `ap01-abi-qemu:20261105`，镜像 ID `sha256:f69f687096a1e3437c7225f8e004b7f45bce243c22670507c0aef7e41d540420`；未在 james.local 宿主安装依赖。运行脚本支持同时指定 `--qemu-image` 与 `--expected-image-id`，本轮使用上述值。QEMU 引擎 SHA 保持 `25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11`。

## 2026-11-05 Bridge 页面与 Rust worker 接实际 RV32

2026-11-05 Bridge UI/Rust/RV32 闭环：生产页面函数经测试 IPC、真实 Rust worker、回环 TCP 和生产 C++ HTTP 完成五事务（首装失败空回退→同包新 ID 重装→A 单更→A+B 批更→整集回退）。james.local Docker 中真实 App 双基址运行，导出日志/运行快照返回原客户端；每事务一次 commit，重启等待期间 20 次原事务查询，boot=13/14/15/16/18，终态 cleanup_pending=false。页面重开恢复、成功/回退标签、查询与归档均通过。报告 `build/app-install/set-rv32-ui-v3-report-01.json`，SHA `26d67fcd842758202b07668a861420a9a82314c2463c011649c2f5ffe9fe2982`；全部快照、子报告和终态二进制摘要复核一致。原生 Tauri IPC/文件对话框、网络变化自动发现、完整 RV32 HTTP/原厂启动仍未验证，未操作实机或生产 Bridge。

复现：先创建一个新的空 snapshot 目录，避免覆盖历史证据。使用固件提交 `7802d7b` 的脚本、Bridge 提交 `b16450e` 的缓存实现；测试上下文设备登记为空，自动重连在网络发现前返回，不扫描实机。Docker 镜像与上节 20261105 指纹相同。

```sh
PATH=/Users/slepher/.cargo/bin:$PATH CARGO_TARGET_DIR=/private/tmp/codex-ap01-bridge-v3-target \
python3 -B tooling/scripts/test-app-set-client-http-v3.py \
  --tcp --rv32-results --fail-first --rust-ui \
  --rust-bridge /Users/slepher/project/codex_status/bridge \
  --binary build/app-install/test-set-journal-v3 \
  --manifest build/app-install/d2-resume-set/set.amf3 \
  --package build/app-install/d2-business-resume-01/app.apx2 \
  --package build/app-install/d2-peer-beats-02/app.apx2 \
  --snapshot-dir build/app-install/d4-rv32-ui-01 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf- \
  --qemu-image ap01-abi-qemu:20261105 \
  --expected-image-id sha256:f69f687096a1e3437c7225f8e004b7f45bce243c22670507c0aef7e41d540420 \
  --report build/app-install/set-rv32-ui-v3-report-01.json
```

这里的 CPU 复位是 QMP 模型，文件系统为内存 VFS；真实执行指 App 指令/加载/健康监督，不包括原厂 ROM 服务实现。运行包身份逐字段与实际 912 B ARV3 快照核对，单更 B 身份不变，回退恢复完整旧集合。

## 2026-11-05 后续网络静态审计（非 QEMU）

2026-11-05 网络阻塞审计：固定 0041 ROM 的 TCP accept 在空队列/阻塞模式下传 -1 无限等待，并不使用监听器接收超时。共享 native listener 创建 socket 时新增 ROM 已支持的 type bit 11（0x800），同时覆盖维护和 App；接收/发送仍用非阻塞 flags 及既有 deadline。新增 audit-native-network-0041.py 固定 ROM SHA/关键指令与调用链，变更 ROM 拒绝。完整 ABI 3 平台构建及候选校验通过，`d3-platform-09.bin` 6932264 B，SHA `f84b41d9529b9ca9d262bdc9e7c63ad09b464aa97554c17120aac73fb02f528b`；反汇编确认 TCP/UDP type=0x801/0x802。证据 `build/app-install/d2-network-audit-01/report.json`。本轮是静态原厂指令审计/构建，不是实际网络时序验收；维护预留、内核锁等待和资源完整审计仍待完成，未操作实机、不可部署。

原厂路径：socket `0xa00268c4` → psock_socket `0xa00360e2`；IPv4 ops `0xa01be908` 的 +32 指向 accept `0xa00349d6`。空队列检查 conn+29 的 bit 3；未设置时 `0xa0034af6` 装入 -1，调用 `0xa003c08e`，再进入无限 semaphore wait `0xa002786c`。type bit 11 在 `0xa0036194` 映射到该 bit 3。没有假定 Linux fcntl/ioctl/setsockopt 常量，也没有改写原厂函数。复核命令：`python3 -B tooling/scripts/audit-native-network-0041.py --report build/app-install/d2-network-audit-01/rom-audit.json`；候选检查：`python3 -B tooling/scripts/test-firmware-0041.py --manifest build/app-install/d3-platform-09.manifest.json`。原厂指令审计不能替代后续运行测试。

## 2026-11-05 原厂 socket/accept 指令对照

2026-11-05 原厂网络指令执行：james.local Docker QEMU（rv32,xtheadbb=true）运行编译后的监听器前段及固定 ROM 的 psock_socket/TCP accept。TCP/UDP type=0x801/0x802；原厂将 bit 11 映射为 conn.flags bit 3；空队列下非阻塞返回 -11、不进入 wait。阻塞对照即使设置接收超时 20 deciseconds，仍到达 timeout=-1 的等待入口，测试在该处断点停止。五项检查通过，报告 `build/app-install/d2-network-qemu-01/network-20261105-03.json`，SHA `facfb56108c944973903f1043b17437aa42d599151bbe26b62cef6ae49800da0`；脚本、ROM、监听器片段及引擎/支持脚本摘要一致。分配/setup 和空连接为替身，未执行完整内核引导/真实网络，不能宣称内核锁耗时或维护预留已验；未操作实机。

本轮原测试镜像 20261105 已不存在；使用已有 Dockerfile、同一 Debian 基础摘要，在 Docker 内重建 `ap01-network-qemu:20261105-01`，ID `sha256:5eb73f3723ae561b43d9a416f1d29730fb5c945800fe5501b2e0ec6a8101365e`。不安装宿主依赖、不改动运行服务。第一次脚本导入因容器路径层级不同失败，已将审计模块的默认路径求值移至 CLI；第二次默认 rv32 在 T-Head 指令处超时，不作为通过证据；显式启用 xtheadbb 后第三次通过，固定 ROM 字节没有改写。

输入目录 `/home/slepher/ap01-abi-20261103/input/network-20261105-01`，包含原始 ROM、两份脚本和从 `d3-platform-09/native_io_0041.o` 的 listener section 用 objcopy 导出的 154 B `listener.bin`。测试只执行 listener 到 socket 调用入口，不执行其中后续外部重定位调用；psock_socket 的 setup 在 `0xa003401e` 拦截并提供零化 conn，其余标志传播及 accept 分支执行原厂指令。阻塞对照停在 `0xa003c08e`，不会实际等待。未启动完整 ROM，未初始化 RF，也未使用真实 socket。

运行沿用只读根、无网络、2 CPU/512 MiB/64 PID、UID 1000 及 /tmp tmpfs 的 Docker 限制；引擎和 support 只读挂载，output 独立可写。容器内命令：

```sh
python3 -B /input/test-native-network-qemu-0041.py \
  --qemu /engine/qemu \
  --expected-engine-sha256 25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11 \
  --support-dir /support --rom /input/ap01-1.0.2_0041.bin \
  --listener /input/listener.bin --output /output/network-20261105-03.json
```

复现须使用新的 output 名，脚本拒绝覆盖。镜像及全部本地输入摘要保存在 `d2-network-qemu-01/execution-identity.json`，超时尝试报告保留为 `network-20261105-02.json`。

## 2026-11-05 原生 I/O 截止回归（宿主）

2026-11-05 原生 I/O 截止修复：waitFd 原先两次读取单调时钟，100→102 ms/截止 101 ms 会导致无符号下溢并请求 poll 1000 ms；新增真实适配器宿主回归先复现失败，改为单次采样后通过。覆盖已截止、等待上限、EINTR、I/O 错误、就绪/挂断，以及 TCP/UDP 非阻塞参数和各初始化失败的关闭路径；已接 test-native-app-platform-v3.py，原有双 App/宿主回归与 ASan/UBSan 一并通过。报告 `build/app-install/d2-native-io-01/native-app-platform-v3-report.json`，SHA `912740522e5de52aae4f4061509a6f1f8e528760cc87969434fd5e44445286d4`。完整候选 `d3-platform-10.bin` 6932264 B，SHA `17ae3f3f7e43fc045a11a96f6b86d5c5127273693070922defb84b582de1ad54`，镜像校验通过；未操作实机，不可部署。ROM 时钟/poll 为测试替身，不证明实际时延、时钟失效恢复或维护资源预留。

回归直接包含生产 native_io_0041.cpp，仅 ROM_FN 由时钟/poll/socket 替身解析；RV32 PollFd 24 B 静态断言仍保留在交叉构建中。命令：

```sh
python3 -B tooling/scripts/test-native-app-platform-v3.py \
  --out build/app-install/d2-native-io-01 \
  --package build/app-install/d2-business-resume-01/app.apx2
python3 -B tooling/scripts/test-firmware-0041.py \
  --manifest build/app-install/d3-platform-10.manifest.json
```

首次回归的断言失败是刻意验证旧实现，退出 134；修复后通过，不涉及 Python 崩溃或真实设备。此前原厂 socket/accept QEMU 证据仍对应 d3-platform-09 的 listener 片段，本轮新增期限修正由宿主生产适配器测试和完整 RV32 编译验证，不扩大旧 QEMU 的验证范围。

## 2026-11-05 维护 HTTP 工作区（宿主及完整交叉构建）

2026-11-05 维护请求预留：Ap01NativeServices0041::State 在 App 启动前持有并复用 34817 B HTTP 工作区（2048 B 头+32768 B ROM 块+终止位），串行维护请求解析不再逐次申请 6145 B/大块缓冲区。生产 RV32 State=35536 B（已含工作区）、维护对象=200 B、维护线程栈=16384 B；构建报告明确嵌套计费，避免再叠加旧 HTTP 上限。注入解析器数组分配失败后，空/小/最大分块及复用通过，越界/截断拒绝；ASan/UBSan 原生平台、集合 102896 检查、独立维护 OTA/重放/重启回执/无稳定记录切槽、跨仓职责边界均通过。完整候选 d3-platform-12.bin 6932600 B，SHA `d063186246c5daa8e977abd2091928f38da6fdef47ea0c58a964b079284ecd53`，校验通过。证据在 `build/app-install/d2-maintenance-reserve-01/`；仍不保证响应/处理器及 ROM 分配或整机维护储备，未操作实机、不可部署。

报告摘要：

- `native-app-platform-v3-report.json`：`c9c319dd89bd152dfbf20f0005184afa0987ccab39e9887384441f58df7265aa`。
- `set-journal-v3-report.json`：`e9a7ddc7022e38aa864a2c9ee756541c26133ead809bc9872b70490cd8337375`。
- `maintenance-gate-report.json`：`bd5af9abc84885c2418a6aeed4b809ee67325422ac0dce0db3c2bc78bdcfd71d`。

分配失败测试只替换 nothrow 数组分配；真实解析器借用预留工作区，handler/响应分配不在本项无分配声明内。共享工作区复用后还检查长度边界和截断，原有动态分配 fallback 仍单独覆盖。集合生产 HTTP 路由和独立维护 32 KiB OTA 分块使用同一工作区入口。独立维护最初失败为长 checkout 临时路径触发既有 128 B VFS 限制，测试改用短临时根后通过，未放宽固件路径规则。无 App 绑定仍可维护和切槽。

复现（输出目录须预建）：

```sh
python3 -B tooling/scripts/test-native-app-platform-v3.py --out build/app-install/d2-maintenance-reserve-01 --package build/app-install/d2-business-resume-01/app.apx2
python3 -B tooling/scripts/test-app-maintenance-gate-0041.py --out build/app-install/d2-maintenance-reserve-01 --rom build/app-install/d3-platform-12.bin
python3 -B tooling/scripts/test-app-set-journal-v3.py --out build/app-install/d2-maintenance-reserve-01 --package build/app-install/d2-business-resume-01/app.apx2 --manifest build/app-install/d2-resume-set/set.amf3 --peer build/app-install/d2-peer-beats-02/app.apx2
python3 -B tooling/scripts/test-firmware-0041.py --manifest build/app-install/d3-platform-12.manifest.json
```

## 2026-11-05 响应内存失败（宿主及完整交叉构建）

2026-11-05 响应 OOM：故障注入复现 ArduinoJson String writer 在最终 flush 失败时仍返回非零计数，旧判断可留下空/不完整成功正文。统一 ap01EncodeJson0041 保留一次预分配，检查文档溢出、输出上限、序列化计数和实际长度；集合、维护/ROM 及保留的旧 App 更新回执复用。HTTP 对非 frame 空正文直接发送无需 String 分配的 503/unknown，指引查询原事务，避免将可能已提交的动作报为成功或拒绝。新回归、ASan/UBSan 原生平台、102896 集合检查、独立维护及旧 HTTP 均通过。完整候选 d3-platform-13.bin 6932440 B，SHA `f9690ed792daa30d30af512c7a3cb5c20ae8de98e3281cb4996cabcb7c081eaf`，镜像校验通过；证据 `build/app-install/d2-response-oom-01/`。不是全处理器 OOM 矩阵或整机资源保证，未操作实机、不可部署。

证据摘要：

- `native-app-platform-v3-report.json`：`097c5968d6a23e56026f6e4a67af8443176487f91d5767bd9fe79535de73b778`。
- `set-journal-v3-report.json`：`d4c1f26079330e222fe6b8f7e816e910fb425ace3b8fe34ca3a51e349f0e2a5e`。
- `maintenance-gate-report.json`：`9b57091b493207fbe5d874cd915c932b1b25922affa78fff30f82c7eb6abd08e`。
- `http-report.json`：`f5960c83824589482732561c5b9594d636d176e3d9af0d11c0c050937ab15a3b`。

测试直接注入 String realloc 失败，验证旧 writer 非零计数/空正文、新 helper 拒绝输出，以及正常序列化只发生一次 reserve；还覆盖长度上限和 JsonDocument 分配失败。HTTP 测试模拟已处理请求返回空成功正文，保持解析工作区可用并拒绝解析器数组分配，断言线上 503 Unknown 与查询原事务提示。处理器/响应 malloc 的全部调用链故障矩阵仍开放。

回归入口仍为 `test-native-app-platform-v3.py`、`test-app-set-journal-v3.py`、`test-app-maintenance-gate-0041.py`；保留路径通过 `test-app-http-0041.py --out build/app-install/d2-response-oom-01 --package build/app-install/golden.apx2` 验证。完整候选通过 `test-firmware-0041.py --manifest build/app-install/d3-platform-13.manifest.json`，未运行 QEMU或操作实机。
