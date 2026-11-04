# ABI 3 独立第二 App

`z_probe` 是多 App 集成验证用的独立可执行包：一个 `peer` 页面、一条后台任务，全部调用通过平台 C 表，无原厂地址依赖。health 在页面已附着、UI tick 与后台任务都运行后返回 OK；窗口删除后 Pending，event 3 重建页面。不是新业务功能，也不声明硬件容量。

复用正式打包器；输出目录须预建且为空：

```sh
build/s1/python/bin/python -B tooling/scripts/build-app-v3-0041.py \
  --out build/app-install/d2-peer-02 \
  --app-config tooling/app-examples/peer-v3/build.json \
  --app-id z_probe --version d2.0 --heap-bytes 4096 --stack-bytes 2048 --capabilities 57 \
  --tool-prefix build/s1/toolchains/xpack-riscv-none-elf-gcc-12.5.0-1/bin/riscv-none-elf-
```

Manifest 条目为 tasks=1、pages=1、TCP/UDP=0。依赖可固定真实 codex_status 包的内容摘要。`build-app-v3-guest-0041.py` 同时传入 `--manifest set.amf3 --peer app.apx2` 即编译集合 guest；未提供时仍构建单包 guest。沿用 `test-app-abi-qemu-0041.py --direct-v3`，运行仅允许 james.local Docker。guest 检查集合启动、三任务共存、peer 页面切换及两包窗口重建。底层 ROM I/O/LVGL/维护服务及调度仍为模型替身。
