# 0031 本地维护凭据菜单（2026-10-31）

`access_menu_0031.c` 在原厂设置的“返回”前增加 `Access / 18080`。
首次进入生成并显示八位数字设备码。菜单为设备码、`Generate again`、`Back`；
旋钮在后两项间双向选择，按下 `Generate again` 重新生成，`Back` 返回原设置
并保持入口选中。设备码直接作为 HTTP Bearer 凭据，保留前导零。
原六项及原返回行为保留。
使用 0031 自带完整 ASCII 字体，不依赖 App、Bridge、稳定槽记录或额外字库。

`device_code_0031.c` 采用与 0041 相同的 DVC1 记录、无偏数字码生成与提交策略。
`device_code_native_0031.c` 使用 0031 原厂 `/dev/urandom` 和 LittleFS/VFS 接口。
正式记录为 `/data/ap01_0031.device_code`，临时记录加 `.new` 后缀；与 0041 文件
分开，防止在救援槽操作时轮换应用槽的设备码。重启和新版本 OTA 不自动轮换。
新 ROM 无构建密码、密钥文件或凭据哈希，原 manifest 凭据区域全零。

- 只有本地菜单生成/轮换；HTTP 不生成。初始未配置、损坏或读取失败返回 503。
- 记录包含 magic、八位码和 CRC。临时文件完整写入、同步、关闭并读回后原子重命名，
  再读取正式文件确认。重命名报错但新记录实际生效时仍认定成功。
- 首次写入断电：完整临时记录在下次打开菜单时恢复提交；不完整临时记录报错，
  可由本地 `Generate again` 明确重建。轮换断电且旧正式记录仍在时继续用旧码。
- 提交结果不明显示 `Check again`；当前页面只重读正式记录，恢复确认前不继续轮换。
  退出重建页面后，先读正式记录的同一规则仍适用。实体掉电耐久性尚待实机验证。
- 每个请求重新读取正式记录；旧 64hex 密钥没有兼容认证后门。四个工作任务共享
  五次失败/30 秒限流，正确认证清零计数；冷却期内正确码同样返回 429。
  限流状态随服务重启清空，与 0041 一致，菜单轮换不会清除冷却期。
- 轮换影响后续请求。已经读取旧记录的在途认证、已认证的 OTA 或诊断会话继续执行；若需使现有会话全部失效，
  应先结束会话或重启设备。未配置凭据仍可使用原厂紧急更新/恢复路径。

上传/诊断客户端的 `--auth-key-file` 现在读取菜单的八位数字码；仅为向尚未升级的
旧救援 ROM 发起迁移保留客户端 64hex 输入支持。该值不写入新 ROM，也不与目标
ROM 哈希绑定。升级后公开 `/health` 仅证明观察到版本，不能代替新码认证。

## 精确原件与补丁

原件 SHA256：`8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb`。
file offset 0 映射至 `0x9ffff000`。通过 REA 6.7.0 / Ghidra 12.1.4
对原件反编译、交叉引用和汇编复核，未把 0041 地址当作 0031 地址。

| 文件偏移 | 原指令字节 | hook 返回前重放 |
| --- | --- | --- |
| `0xbe8da` | `efc0ce7db7450fa0` | `lui a1,0xa00f4` |
| `0xbe9e6` | `efa0fd6e814523a4a900` | `li a1,0; sw a0,8(s3)` |

前者替换一次 Settings 事件注册，后者包装原设置列表创建。
0031 页面数据只有标题、时间、列表三个指针，不能访问 0041 的 `data[3]`。
菜单 context 由原页面 DELETE 回调释放；原列表在子菜单中隐藏，返回时恢复，
从而保留原条目对象及状态。其余事件、原子页面和原生唤醒逻辑继续走原件。

manifest 版本为 2，`[64:192]` 必须全零。`[192:228]` 使用 `AP31MNU1`、LE32 数量 2、两个
`offset/target/span` LE32 三元组。其余保留字节必须为零。
构建器及设备自检均校验数量、固定站点、覆盖长度、目标对齐和模块内范围；
manifest CRC 覆盖表。打包时核对被替换的原字节，并重建整包恢复 CRC。
设备拒绝旧版内置密钥 manifest；离线验证器仅为历史重建保留版本 1 读取。
release 必须链接菜单；RAM/probe 不链接菜单，需要先在模拟存储中预配置设备码。
构建器不再接受 `--auth-key-file`，也不生成 `.auth-key` 文件。

## 静态证据索引

完整证据保存在本地 `evidence/private/access-menu-0031-20261031/rea-evidence.json`。

| 结论 | REA Evidence ID |
| --- | --- |
| 两处 hook 的上下文及续指令、三指针页面布局 | `ev_5051132978367bd9b74e7c7795a5d7278f00922e55c490bcf6884734e19d1f4d` |
| 原 Settings 状态、原六项与返回 | `ev_3f017b8bcfeecd560b433e479c7f24185d21c009408959ca4af43ab819ab0194` |
| `0xa00b83d2` 页面查找 | `ev_b3463a749101943b64c0544ca5d789bc124bfe111d5511da861bc279fbd8a886` |
| `0xa00b85e6` 唤醒门 | `ev_45ba4aeb4b5e2833a420f107d1834bee8911a25034ba4b0aacaf7dc2018e34a7` |
| `0xa0192fb4` 原生行及子对象 | `ev_48f9627f41759c80ef668acf7638e98b5f8c490956426efdb611c4b4ad796c8d` |
| `0xa00c7466` 公共删除 | `ev_a42bfb11cb79e02820fba9fad3f94f208cdcb2162f34ea0318253de8b55cd312` |
| `0xa0086bcc` 标签复制文本 | `ev_74bb2a6fbccd78e14b41ad67d3a0d7aec083ef166ecd885b8c0722f612efdc52` |
| `0xa01e1d7c` 原厂字体 wrapper | `ev_8ff8eba10049fefb8ac52425d79b52639546cce48c842448d0e4c9e913cdf61b` |

Ghidra 对厂商 custom 指令和部分 no-return 边界存在限制，静态证据不等于执行证据。
字体 cmap 的 ASCII 32–126 覆盖另由 ROM 字节解析检查。

持久凭据适配的追加证据为本地 `rea-device-code-evidence.json`：

| 0031 接口 | REA Evidence ID |
| --- | --- |
| `0xa0052a7c` 原厂读取 `/dev/urandom` 的调用路径 | `ev_2e920d2003323ab636ede1a0f30aa03a660856698557fa4ff4d572776598006e` |
| `0xa019d862` inode 查找与引用、28 字节 lookup 布局 | `ev_16ba6e63f0c8c5166f91ed9de7c72a42895ebc6b08b0be9d9d2471f958b3dd70`、`ev_c6ccba2cbc8f03b16a106a01bd0d061ec338b1de6fa409fdacee80e4e56a2198` |
| `0xa00487de` LittleFS 重命名 | `ev_41c70f0c1795f83253f61ff9881872c6e6bf6086a9c78b7f81aeed0e80eb67f2` |
| `0xa01bb508` 精确 LittleFS ops 表 | `ev_56effbf89c7d68939b6a61b3d891b2c5a7a4f3a4051a4c921301a6e8801ff734` |
| file_get / sync / file_put | `ev_774ea7de3a344fc9069558cb28aeea3664154cbf6b8e3214f32d6dc1ec52dedc`、`ev_b61bd1c9ec943553f4ef0e0a6eb7998269e0bb1978fdca024ec6fd50288652bf`、`ev_0febce73684f205a8ecf1597a03055c6cf542fc6f7d82d0329ca5ec1a8ef6ebf` |

## 验证与边界

宿主菜单测试执行实际 C 实现，用模拟原厂对象/API 检查导航、隐藏/恢复、
生成/轮换、清理重建及分配失败；它不是原厂 LVGL 或物理旋钮模拟。
凭据核心与原生适配另检查掉电/损坏/随机源/读写/同步/重命名故障和限流。
既有 OTA 52 项、诊断 18 项、上传 5 场景回归通过。RISC-V `-Wall -Wextra -Werror`
交叉编译及禁止可写静态状态的链接约束通过。

可重复检查（Linux，输出目录须已存在）：

```sh
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-pie -no-pie \
  tooling/firmware-modules/test_access_menu_0031.c \
  tooling/firmware-modules/device_code_0031.c \
  tooling/firmware-modules/ota_channel.c -o /tmp/access-menu-check
/tmp/access-menu-check
cc -std=c11 -Wall -Wextra -Werror -fsanitize=undefined \
  tooling/firmware-modules/test_module_manifest_0031.c -o /tmp/access-manifest-check
/tmp/access-manifest-check
python3 tooling/scripts/test-access-menu-0031.py
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-pie -no-pie \
  tooling/firmware-modules/test_device_code_0031.c \
  tooling/firmware-modules/device_code_0031.c -o /tmp/device-code-check
/tmp/device-code-check
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-pie -no-pie \
  tooling/firmware-modules/test_device_code_native_0031.c -o /tmp/device-code-native-check
/tmp/device-code-native-check
```

manifest 宿主检查将匿名内存映射到实际 XIP 地址，执行设备端同一验证函数，
覆盖无密钥菜单表、旧内置密钥拒绝、畸形记录及 CRC；该地址落入 ASan shadow gap，
因此这一项使用 UBSan。菜单检查继续同时使用 ASan/UBSan。

无内置密钥 HTTP 整包候选已通过完整重建校验，保留原 GIF、启动头、传统 OTA
及恢复入口。RAM 位置无关实验亦通过链接及打包验证，但不是部署替代方案。
最终 HTTP 候选为 6,827,000 B，SHA256
`cd5ab02398214d186af064ac98ce4080b8d2cecb7f4b57d01a292d63dca6ccd5`。
模块为 19,408 B，超过历史 `bridge` 的 19,052 B 固定预算；使用 `http` 或
`gif-http` 布局，旧入口仍拒绝超预算，不静默扩大补丁范围。
`gif-http` 同长度候选也通过重建（6,804,520 B；SHA256
`b7207503b60dc62e56714242bc6b342360cc4772af790ba802b2ca5575c3df0e`），
该布局使用占位 GIF，不能宣称保留原猫 GIF；启动头、PEC 和传统 OTA 保留。
该产物只供离线验证，manifest 仍为 `flashable=false`、
`physical_device_verified=false`；未刷机、未访问设备。

待完成：同机熵源质量、持久化掉电、菜单/LCD/旋钮、OTA 非活动槽、回切/恢复
及保留槽不变的验收。外部 `codex_status` 主 release CI 的 0031 集成不在本次修改中。
