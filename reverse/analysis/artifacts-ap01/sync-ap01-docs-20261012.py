from pathlib import Path
import hashlib
import json
import sys

root = Path('D:/Documents/PlatformIO/Projects/codex_status')
ap = root.parent / 'cuktech-ap01-firmware-tools'
changes = {}
originals = {}

def edit(path, old, new):
    if path not in changes:
        originals[path] = path.read_bytes()
        changes[path] = originals[path].decode('utf-8').replace('\r\n', '\n')
    assert changes[path].count(old) == 1, (str(path), old[:100], changes[path].count(old))
    changes[path] = changes[path].replace(old, new)

def paragraph(path, starts, new):
    text = changes.get(path, path.read_text(encoding='utf-8'))
    old = next(p for p in (text.splitlines() if starts.startswith('2. ') else text.split('\n\n')) if p.startswith(starts))
    edit(path, old, new)

p = root / 'docs/cuktech-ap01-repository-value-analysis.md'
edit(p, '2026-10-11。结论：', '2026-10-12 文档复核。结论：')
edit(p, '| 当前 `codex_status` | `02f096506fe833187415b800192fcbe85d74c638`，工作区有未提交改动 | 多数据源、设备本地编译模板、完整 A/B Bundle、活动上下文、显式发布、设备认证及 PowerPlan |', '| 当前 `codex_status` | 2026-10-12 本地源码复核；候选与部署版本以 [PROGRESS](../PROGRESS.md) 为准 | 多数据源、设备本地编译模板、完整单份 Bundle、下载暂存、活动上下文、显式发布、设备认证及 PowerPlan |')
edit(p, '| 持久存储 | 0031 静态分区分析报告 `/data` 为 64 KiB；当前 Bundle 上限 256 KiB | 两份完整包、原厂数据共存、事务记录、掉电恢复；不能把内存图片文件当持久仓库 |', '| 持久存储 | 0031 静态配置 `/data` 为 64 KiB、`/resource` 为 1.25 MiB，实际空闲未知；Bundle 按设备报告动态准入 | 一份已安装内容加下载暂存、原厂数据共存、事务记录与内置恢复；下载前不能把旧内容算作可回收空间 |')
edit(p, '| 常驻与峰值内存 | ROM 预算建议新增常驻约 160–400 KiB、安装恢复峰值 384–768 KiB | 真机空闲堆、最大连续块、栈和网络/图形库峰值；预算是目标，不是运行测量 |', '| 常驻与峰值内存 | 早期 256 KiB 正文样例估算新增常驻约 160–400 KiB、安装恢复峰值 384–768 KiB | 按实际字体、编译缓存、解压器重算，并测空闲堆、最大连续块、栈和网络/图形库峰值；样例不是动态大包的保证 |')
paragraph(p, '320×240 单色画面', '320×240 单色画面每帧 9,600 字节，两帧 19,200 字节；完整 RGB565 彩色帧每帧 153,600 字节。初版沿用单色模板、分行转换到彩色屏有节省内存的依据，但最终显示接口是否支持这种提交方式仍需验证。显示帧缓冲和上游图片轮转用于绘制交接，与项目自管内容的持久更新策略分别核算。')
edit(p, '## 建议采用方式', '## 当前更新与协议要求\n\n更新顺序引用 [C9 单份更新设计](../project-workflow/single-copy-updates/design.md)：旧应用在下载及预检期间继续运行，完成后进入内置界面、停止并覆盖；覆盖失败通过稳定底座接受认证重传。原生固件 OTA 双槽保留。Note4 的单份存储、动态容量与 CSZ1 分块压缩已有 [部署记录](../project-workflow/single-copy-updates/status.md)，AP01 解压接口和独立应用加载仍待实现。\n\n接入时按 [当前协议](bridge-device-protocol.md) 核对认证状态、设备报告的数据合同和原事务回执。传输容量与解压后处理容量分别由设备报告；历史 256 KiB 是兼容上限或预算样例。当前源码已支持随 Bundle 下发的 CSFN v2 字体及 UTF-8 文本，候选与实机验证情况见 [字体专项](../project-workflow/bridge-macos/release-fonts-status.md)；AP01 须适配并声明能力，不能直接视为已支持。\n\n## 建议采用方式')

p = ap / 'reference/DESIGN/AP01-Bridge接入与资源预算.md'
paragraph(p, '> 2026-10-11', '> 2026-10-12 同步：平台更新规则唯一引用 [C9 单份更新设计](../../../codex_status/project-workflow/single-copy-updates/design.md)，实施与部署见 [C9 状态](../../../codex_status/project-workflow/single-copy-updates/status.md)，待办归主项目 C9。Note4 已实现单份 Bundle、下载暂存、动态容量与分块压缩；AP01 当前交付为设计和静态证据，独立应用加载、解压接口及实机尚未验证。原生固件 OTA 双槽保留。')
edit(p, '## 3. 已测量尺寸与估算方法', '## 3. 历史测量尺寸与估算方法')
edit(p, '这证明固定布局大小，不证明C++程序能链接、启动或正确运行。', '这证明报告所记源哈希下的固定布局大小，不证明C++程序能链接、启动或正确运行。以下结构尺寸、字体符号及预算均来自2026-10-11探针，移植当前源码前须重新生成；原始产物保留不改。')
edit(p, 'RV32试编译；64操作、32需求、16资源的当前固定格式', '历史RV32试编译；64操作、32需求、16资源')
edit(p, '| 当前持久槽头/元数据记录 | 130 / 138 | RV32试编译；只用于核算既有格式 |', '| 历史持久槽头/元数据记录 | 130 / 138 | 原探针尺寸；当前单份格式以C9实现为准，不套用此记录 |')
edit(p, '理论总量不超过min(384 KiB,3P/4)', '未压缩正文为P时，字体原始字节理论总量不超过min(384 KiB,3P/4)；若正文压缩，必须改用解压后长度核算')
paragraph(p, '更新期间切到稳定底座内置界面', '下载和预检期间旧应用继续运行，暂存占用与旧内容共同计入准入；校验完成、即将覆盖时才切到稳定底座内置界面，排空旧绘制、线程、回调和文件引用，释放旧模板/字体，再采用新内容。退出失败则拒绝覆盖。完整生命周期引用平台C9。')
paragraph(p, '当前生产Bundle解析保留全部模板源', '主项目生产Bundle安装已采用有界读取、字段过滤和逐项模板／字体解析，压缩正文按块读取；当前实现见 [bundle_store.cpp](../../../codex_status/src/bundle_store.cpp) 和 [bundle_payload.cpp](../../../codex_status/src/bundle_payload.cpp)。AP01仍须适配文件与内存接口，不能把Note4测试当作AP01峰值证明。按空、单、典型和实际上限记录解析、字体、解压器及网络的同时存活量，服务栈须有调用链和实测依据。')
edit(p, '读取当前Note4编译产物得到全部已选字体表34239字节', '历史Note4编译产物中的已选字体表为34239字节')
edit(p, '字体数据更接近跨平台固定成本。', '字体数值只代表该历史镜像。当前主项目已支持随Bundle发布的CSFN v2字体和UTF-8文本，相关候选与实机状态见 [字体专项](../../../codex_status/project-workflow/bridge-macos/release-fonts-status.md)。AP01须按实际字体资产预算并声明能力，不能把历史字体表作为当前ROM的固定成本。')
paragraph(p, '存储和准入规则引用', '存储和准入规则引用 [平台单份更新设计](../../../codex_status/project-workflow/single-copy-updates/design.md)。Bundle保持完整有序1–8项，按实际可用空间、模板数量、文件系统预留和运行成本准入。主项目已用bundle_storage_protocol=2报告动态max_bundle_bytes，压缩另报告max_bundle_decoded_bytes；旧设备保留256 KiB兼容上限。AP01应在实现并验证后声明相应能力。')
paragraph(p, '/resource名义1.25 MiB', '/resource名义1.25 MiB，实际空闲未知。下载准入必须容纳当前驻留内容、完整暂存包、缓存和预留；不能预先回收旧内容、删除原厂文件或格式化分区。覆盖阶段的空间和损坏恢复要求引用平台C9。上述680808字节是样例稳态占用，同大小未压缩包暂存时为942952字节，原厂占用另扣。压缩暂存与驻留方式的比较、原厂解压证据见 [C9 AP01评估](../../../codex_status/project-workflow/single-copy-updates/design.md#ap01-压缩暂存评估)；最终应用存储格式尚未定稿。')
edit(p, '  C --> V[内置更新界面：停止旧应用]\n  V --> U[独立更新任务：原厂客户端拉包]\n  U --> F[唯一应用文件：长度、摘要、兼容性、签名校验]\n  F --> P[持久记录候选版本]', '  C --> U[独立更新任务：暂存下载，旧应用继续运行]\n  U --> F[完整预检：长度、摘要、兼容性、签名]\n  F --> V[内置界面：停止旧应用并排空引用]\n  V --> W[覆盖唯一应用文件并读回校验]\n  W --> P[持久记录候选版本]')
edit(p, '首版采用“下载、验证、记录候选、重启、试运行、确认”的更新方式', '首版采用“暂存下载、预检、停止旧应用、覆盖并读回校验、记录候选、重启、试运行、确认”的更新方式')
edit(p, '允许更新期间失去旧应用；不完整或未通过验证的应用不得执行', '下载或预检失败保留旧应用；进入覆盖后允许失去旧应用，不完整或未通过验证的应用不得执行')
edit(p, '下载在独立任务中调用已核实的原厂webclient，逐块覆盖唯一应用文件，限制总长度、超时和连接数；不把文件收齐到第二份大内存。', '下载在独立任务中调用已核实的原厂webclient，逐块写暂存文件，限制总长度、超时和连接数；先完整预检，再停止应用并覆盖，不在内存中收齐整包。')
edit(p, '完整公式及边界以平台C9为准。', '以上均为稳态样例；暂存包必须另外计入，应用和Bundle更新串行准入。完整公式及限制以平台C9为准。')
paragraph(p, '稳定底座可以保留共用绘制和字体以缩小应用包', '稳定底座可以保留共用绘制和字体以缩小应用包，但相应部分更新仍需更新底座。单份应用的资源评估包括唯一已安装文件、暂存包、读回缓冲及运行内存，实际加载验证仍未完成。')
edit(p, '；不再以双应用文件占用作为单份方案的缺点。', '。')

p = ap / 'project-workflow/bridge-port-analysis/report.md'
edit(p, 'Bridge当前源码d02f096506fe833187415b800192fcbe85d74c638（检查时干净）。', 'Bridge早期源码对照及测量以raw中保存的源哈希为准；当前协议于2026-10-12按相邻主项目源码复核，部署与候选见 [PROGRESS](../../../codex_status/PROGRESS.md)。')
edit(p, '主项目256 KiB上限的单份Bundle', '256 KiB正文样例的单份Bundle（当前容量按设备动态报告）')
edit(p, '1–8模板、完整A/B Bundle、唯一active_context、原子安装/掉电恢复；不同于固件双槽', '1–8模板、完整单份Bundle、唯一active_context；暂存预检后停用旧内容并覆盖，提交记录读回校验，失败进入内置恢复；原生固件双槽保留')
edit(p, '保留PowerPlan控制权，按AP01实际硬件实现；不套用墨水屏断电保画面语义', '按设计声明常驻Wi-Fi，Bridge不生成休眠/开窗计划；保留数据更新、owner租约及请求期限，能力适配待实现')
edit(p, '3. 明确可写状态、RAM/栈和完整A/B Bundle预算。', '3. 明确可写状态、RAM/栈和单份Bundle加下载暂存的峰值预算。')
edit(p, '再接入渲染、Bundle、数据及PowerPlan。', '再接入渲染、Bundle、数据和常驻设备能力分派。')
paragraph(p, '用户确认的最新平台事项为', '当前规则、实施状态与AP01待验项以 [接入设计](../../reference/DESIGN/AP01-Bridge接入与资源预算.md) 和 [主项目C9状态](../../../codex_status/project-workflow/single-copy-updates/status.md) 为准。2026-10-12复核：Note4已实现并部署单份Bundle、动态容量及CSZ1分块压缩；AP01尚未实现独立应用加载或解压适配。存储试算产物按其记录的源哈希解读，原生固件双槽保留。')

p = ap / 'project-workflow/bridge-port-analysis/task.md'
edit(p, '/resource占用、原子写入及完整A/B Bundle布局。', '/resource占用、单份Bundle／应用加下载暂存、提交记录及恢复验证。')
edit(p, '完整A/B存储、内存生命期、代码注入空间预算及验收条件。', '单份存储与下载暂存、内存生命期、代码注入空间的设计预算及验收条件；实测另验。')
edit(p, '最小应用运行、更新/回退实机验证。', '最小应用运行、覆盖更新／底座恢复实机验证。')
paragraph(p, '当前方案与实施事项统一服从', '当前方案及实施状态引用 [主项目C9](../../../codex_status/project-workflow/single-copy-updates/status.md) 和 [AP01接入设计](../../reference/DESIGN/AP01-Bridge接入与资源预算.md)。Note4单份Bundle与压缩已部署；本表AP01实现和实机项仍未完成。2026-10-12已核对当前文档，历史测量产物保留原样。')

p = ap / 'project-workflow/bridge-port-analysis/status.md'
paragraph(p, '2026-10-11。', '2026-10-12。AP01当前完成静态逆向与接入设计，尚无本项目Bridge接入的可刷ROM或实机验收。全平台待办归主项目C9，规则见 [单份更新设计](../../../codex_status/project-workflow/single-copy-updates/design.md)，Note4已实现并部署的范围见 [C9状态](../../../codex_status/project-workflow/single-copy-updates/status.md)。')
paragraph(p, '最新单份预算：', '单份预算见 [接入设计第3节](../../reference/DESIGN/AP01-Bridge接入与资源预算.md#3-历史测量尺寸与估算方法)：历史8模板/256 KiB正文样例，应用与预留计入后稳态680808字节，同大小正文暂存峰值942952字节，原厂文件和额外开销另计。原始算式保存在raw/bridge-budget-20261011/single-copy-budget.json；动态准入仍受实测空闲量、解析/字体、解压和连续内存约束。')
paragraph(p, '将来实施依平台C9安排', 'AP01下一步按接入设计验证原厂接口、内置维护界面和认证更新入口，再选择动态应用或完整/差分镜像路径。统一压缩格式引用主项目CSZ1；0031解压代码已有静态证据，但可调用入口及应用加载未验证。本次只同步文档，不访问设备或账号，不构建、部署或提交。')

p = ap / 'project-workflow/bridge-port-analysis/plan.md'
paragraph(p, '2026-10-11用户确认全平台', '当前全平台规则与实施状态引用 [C9设计](../../../codex_status/project-workflow/single-copy-updates/design.md) 和 [C9交接](../../../codex_status/project-workflow/single-copy-updates/status.md)。2026-10-12文档复核同步单份存储、下载暂存、压缩与动态容量；Note4已实施，AP01继续按本设计待验项推进。原生固件双槽保留，本次不开展实现或设备操作。')

p = ap / 'project-workflow/bridge-port-analysis/review.md'
edit(p, '完整1–8模板、A/B包、身份/owner、真实回执和掉电恢复要求保留。', '当前验收要求为完整1–8模板、单份Bundle、身份/owner、真实回执和底座恢复；更新顺序与容量以接入设计为准。')
edit(p, '补充应用RAM代码和双文件成本：', '历史备选方案曾核算应用RAM代码和双文件成本（原始测量记录，当前设计见接入设计第6节）：')
edit(p, '## C9仅规划同步', '## 历史记录：2026-10-11 C9规划阶段')
changes[p] += '\n## 2026-10-12 文档一致性复核\n\n需求、规格、设计、报告及交接已按主项目C9实施同步；当前要求包含下载暂存、预检后停止并覆盖、内置恢复、动态容量及统一压缩格式。历史测量值按记录源哈希保留，当前字体、解析和容量实现另引用主项目。AP01仍无本次加载、刷写、USB或资源峰值实测，未修改代码及原始产物。验证记录见 [主项目文档复核](../../../codex_status/project-workflow/single-copy-updates/ap01-doc-sync-20261012.md)。\n'

p = ap / 'reference/brief.md'
paragraph(p, '2026-10-11用户确认：', '单份Bundle／应用更新的全平台要求引用 [C9设计](../../codex_status/project-workflow/single-copy-updates/design.md)，实施状态引用 [C9交接](../../codex_status/project-workflow/single-copy-updates/status.md)。Note4已实现；AP01按SPEC-RE-002/003交付设计，设备端移植和实机验证待完成。')
p = ap / 'reference/SPEC.md'
edit(p, '更新期间内置界面，失败可重发', '下载及预检期间旧内容继续运行，通过后进入内置界面、停止并覆盖；覆盖失败可认证重传')
paragraph(p, '上述单份策略的全平台范围', '上述单份策略的全平台范围和规则统一引用 [C9设计](../../codex_status/project-workflow/single-copy-updates/design.md)，实施与部署见 [C9交接](../../codex_status/project-workflow/single-copy-updates/status.md)。AP01实现及实机验证状态由本专项交接记录。')
p = ap / 'knowledge/AP01-官方固件分析/0031分区与启动入口复查.md'
paragraph(p, '2. 原厂/data总共64 KiB', '2. 原厂/data总共64 KiB，容不下256 KiB正文的单份Bundle样例。/resource为1.25 MiB只是名义容量；需先查占用、写入方式和恢复规则。当前存储与下载暂存需求见 [接入设计第3节](../../reference/DESIGN/AP01-Bridge接入与资源预算.md#3-历史测量尺寸与估算方法)，不能占用备用固件槽换空间。')

p = root / 'project-workflow/single-copy-updates/design.md'
edit(p, 'AP01规划容器仍按 S=64+P+11365N 估算（不是 ESP32 新格式的精确字节）', 'AP01历史尺寸探针的规划容器按 S=64+P+11365N 估算（不是当前ESP32格式的精确字节；移植时须按选定源码和字体格式重测）')
edit(p, '压缩暂存C时必须同时满足旧驻留+C及新驻留+C的峰值；', '以下按“压缩暂存、解压后驻留”的保守备选方式计算，不代表AP01已确定存储实现。若选用Note4的压缩正文驻留方式，须按压缩后的驻留长度和实际缓存重算。压缩暂存C时必须同时满足旧驻留+C及新驻留+C的峰值；')
edit(p, '先实现 Note4，AP01 仅遵守格式约定，入口/实机后续调查。本轮不部署。', 'Note4已实现且有[C9部署记录](status.md)，最新运行版本以[PROGRESS](../../PROGRESS.md)为准；AP01采用相同格式约定，可调用入口及实机后续调查。以下资源和测试数据为当时.80候选测量，后续源码版本须重测。')
edit(p, '最终候选独立打包，未触及诊断现场。', '当时候选独立打包，后续部署结果见[C9状态](status.md)。')
p = root / 'project-workflow/single-copy-updates/status.md'
paragraph(p, '待验仅在backlog C9管理：', '待验仅在backlog C9管理：真实掉电、堆峰值、功耗和显示矩阵仍未完成；后续运行版本与故障调查以[PROGRESS](../../PROGRESS.md)及对应专项为准，以上.80记录是历史部署证据。AP01按相同CSZ1约定设计，0031原厂DEFLATE已有表及代码引用，可调用接口和应用加载仍待实机；尚未构建AP01 Bridge接入ROM。2026-10-12文档同步见[复核记录](ap01-doc-sync-20261012.md)。')

manifest = []
for path, content in changes.items():
    assert path.read_bytes() == originals[path], f'Concurrent edit: {path}'
    assert content.count('```') % 2 == 0, path
    manifest.append({'path': str(path), 'before_sha256': hashlib.sha256(originals[path]).hexdigest(), 'after_sha256': hashlib.sha256(content.encode('utf-8')).hexdigest()})
if '--apply' in sys.argv:
    for path, content in changes.items():
        path.write_bytes(content.encode('utf-8'))
    (root / 'artifacts/ap01-doc-sync-20261012-files.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'mode': 'applied' if '--apply' in sys.argv else 'preview', 'files': len(changes), 'paths': [str(p) for p in changes]}, ensure_ascii=False))
