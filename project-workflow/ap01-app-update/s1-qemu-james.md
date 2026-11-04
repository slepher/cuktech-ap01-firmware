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
