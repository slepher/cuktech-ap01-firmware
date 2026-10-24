# Q10 天气启动位置差集非作者复核

结论：**本轮限定差集通过**，未发现需作者修正项；天气模块及整 ROM 仍为部分恢复。复核对象为作者提交 `baeee728` 的 [启动位置研究](app-weather-research-01-0041-20261025.md)，复核者 `/root/app_weather_review_01` 未参与作者取证。

独占分支 `codex/app-weather-review-01-20261025`，启动基线 `11c90bc45e5645d08cbb31c3b4ffd3d2da986e43`。主树最新流程 3.1/3.2/5.1/7 及管理记录 Q10 只读引用；只写本报告和同 stem analysis。未修改主树、ROM、配置、模型或共享 REA，未执行固件、SIM、QEMU、回放、构建、设备或外网，未扩展至 setter、天气 H 生命周期或公共库内部。

## 独立证据与方法

原件只读路径 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，长度 6769704 B，SHA256 `972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9`，offset = VA − `0x9ffff000`。

直接读取主树 `reverse/analysis/buzzer-backlight-0041-20261023.json#/functions/6` 的完整 body/assembly/raw_ranges，Evidence `ev_dc0e38b0f382799ea2a8e8ad7f21cefc5998b0767ecf38a58cfdebe8add167c3`。独立逐字比较三个基址建立窗口及 `0xa005ae7c..0xa005aec8`、`0xa005b8a4..0xa005b9ae`（均右端不含），总计 358 B；未以函数 extent 冒充 body。人工核汇编参数与控制流，另独立解码 7 个 JAL、2 个 BEQ 的目标及寄存器；没有执行或导入作者脚本。

必要继承只读主树 `reverse/analysis/weather-location-request-0041-20261023/retained-functions.json`：getter Evidence `ev_1fec2a04b869df31515a29b8ef1a531ed5b05dfc1f3fb10b10b53537c058dbf2`，URL Evidence `ev_c8cd305edf249153fdd712550910d2a60b3450092ab9dd7bbdca0aa4df2bca1b`。getter 全 body 原字及 URL 必要门窗口与原件一致；没有重新研究 setter、请求对象生命周期或 MD5/TLS。

[独立复验源码](../../analysis/app-weather-review-01-0041-20261025/verify.py) 使用 Python 标准库；[本地证据导出](../../analysis/app-weather-review-01-0041-20261025/evidence.json) 保存窗口摘要、汇编、直接边解码及 ROM 键。后者为 ignored 中间产物，须父窗口转存后才能清理任务树。

## 核对结果

| 项目 | 原字/源观察与结论 |
| --- | --- |
| 基址 | `s10=0x62fc9000`、`s4=s10+0xa0`、`s5=0xa01c3000`，namespace `s5+0x68` 为 `ck_config`。 |
| bind 返回门 | `0xa005ae90` 调读 `(ck_config,bind_flag,0x62fc916d,1)`；`0xa005ae96` 仅返回 1 转 `0xa005b8a4`。否则日志后 `0xa005aec4` 写同槽/长度，续 `0xa005aec8`；该路径没有先写零，也不到位置读或阶段标志。 |
| bind 字节门 | `0xa005b8a4` 的 LBU 后，`0xa005b8a8` 在字节为零时转 `0xa005b982`，跳过四键读取。 |
| 文本读 | `0xa005b8be/b8d6/b8ee` 依序读 `loc_province/loc_city/loc_district` 至 `0x62fc90a0/90e0/9120`，长度均 64；三个返回均未在本层判定。 |
| 数值读 | `0xa005b906` 读 `loc_id` 至 `0x62fc9160`，长度 4；`0xa005b90c` 仅返回 4 转 `0xa005b990`，读满路径只加载并日志，不加数值范围判断。 |
| 默认回写 | 不等于 4 时 `0xa005b92a/b92c` 建立 `0x186a0=100000`，`0xa005b930` 先 SW 至 RAM，随后 `0xa005b944` 写同键/槽/长度；写返回未用于本层判断。 |
| 阶段标志 | `0xa005b988` 为 SB 1 至 `0x62fc3fec`；bind 读成功且字节为零也可到达，不能称为定位、请求或绑定非零成功。 |
| 两个 ID 键 | 原 ROM `0xa01c327c` 为 `loc_id`；getter `0xa0265898` 为 `location_id`，不同键及不同输入槽，不能互换。 |
| getter 接合 | 空 cache 首字节直接返回 0；快路成功才复制 out。回退修 cache/写 `loc_province` 后返回 `n!=0`，本次回退不复制 out；不能将返回非零视为输出已填好。快路拒绝后的 a0 ABI 仍未知。 |
| URL 接合 | `0xa00aac68` 只测 getter 返回是否为零；返回零后 `0xa00aae16` 是 BGEU 拒绝 `100000>=legacy_id`，故接受条件为无符号 `legacy_id>100000`，且 `90e0/9120` 的首 byte OR 非零。默认值 100000 不过此门。 |

七个直接调用分别为读：`0xa005ae90/b8be/b8d6/b8ee/b906→0xa0060946`；写：`0xa005aec4/b944→0xa0061848`。两条 BEQ 为 `0xa005ae96→0xa005b8a4`、`0xa005b90c→0xa005b990`。上述为静态控制流与参数事实，不是运行观察；日志调用未充作配置保存结果。

## 断边与交付

继续保留未知：配置后端及读失败对目标槽的实际改写、写入持久化成功、文本终止与启动前 RAM 内容、getter 快路拒绝后的 a0 ABI、全系统首次天气任务的调度先后、真实定位/服务成功。对象/接口调用返回的后端语义没有因这次接线核对而闭合。窗口内未清零或补 NUL，仅是局部观察，不能升格为全系统否定；本轮不扩扫其他 writer、初始化或配置内部。

检查：独立 `verify.py` 通过（358 B、继承窗口、7 JAL、2 BEQ、7 键）；报告链接目标按主树依赖/本树新产物区分，JSON 可解析，`git diff --check` 通过。任务 commit 只包含报告及复验源码，不推送；ignored 清单仅 `reverse/analysis/app-weather-review-01-0041-20261025/evidence.json`，待父窗口转存。本树普通工作区检查须在提交后回传。

UTC 开始取首个可用时钟 `2026-10-24T16:55:25Z`（该读数仅显示到秒），主体复验完成 `2026-10-24T16:56:40.8441094Z`。最终交付检查 UTC 与可观测总墙钟随 commit 交付消息回传；未发生已知中断或异常等待，普通工具耗时包含在墙钟内，有效工作时长及 token 用量不可得，不编造。
