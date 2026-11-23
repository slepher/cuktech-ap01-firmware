# 0055／0.1.2 独立 App 构建与接入

平台使用 App ABI 3 和平台函数表 3.1。业务 App 单独构建为 APX2 包，由 `ap01-0055-app-platform-0.1.2.bin` 加载；无 App 基版不加载业务包。

## 构建环境

需要 Python 3、pyelftools 和 xPack RISC-V GCC 12.5.0-1。App 的 `build.json` 声明源码根目录、include 路径、宏定义、源码列表和版本；路径必须位于该 App 源码目录中。输出目录须预先创建且为空。

使用仓库中的 `z_probe` 示例：

```sh
mkdir -p build/peer-app
python3 -B tooling/scripts/build-app-v3.py --out build/peer-app --app-config tooling/app-examples/peer-v3/build.json --app-id z_probe --version 0.1.2 --heap-bytes 4096 --stack-bytes 2048 --capabilities 57 --tool-prefix /path/to/riscv-none-elf-
```

示例显式指定 App 版本；业务 App 版本独立于 ROM 修改版管理。主要产物为 `app.apx2`、`app-manifest.json`、`build-report.json` 和链接 ELF。

## 接入要求

App 通过版本化 C 表调用平台服务，不直接绑定原厂地址。入口为 start、event、health；UI 回调不阻塞 I/O，文件与网络操作在 worker 执行。已发布代码和回调保留至重启，不支持在线卸载。

集合清单声明 App 身份、包摘要、能力、端口、线程和页面预算。启动平台根据 journal 选择 `/resource/app-store/manifests/<content-digest>.amf3`，核对清单与包后执行；仅复制 APX2 文件不足以构成有效集合更新。集合客户端入口为 `tooling/scripts/app-set-client-v3.py`，操作参数以 `--help` 为准。

## 校验

```sh
mkdir -p build/apx2-check
python3 -B tooling/scripts/test-apx2.py --out build/apx2-check
```

该命令验证 APX2 格式与加载器边界。`test-native-app-platform-v3.py` 是针对 `codex_status` 包及其资源预算的宿主回归，不能直接用 `z_probe` 包替代其输入。完整 ROM 和模型检查见 [平台离线验证](../../docs/0055-qemu-validation-20261106.md)。

接口定义见 [平台 C ABI](../../docs/app-platform-api-v3.md)，二进制格式见 [APX2 格式](../../docs/apx2-package-format.md)。离线验证不代表实机验收。
