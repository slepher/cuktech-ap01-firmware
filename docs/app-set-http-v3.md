# App 集合 HTTP v3 请求合同

2026-11-04：请求解析器 `app_set_http_v3.cpp` 已实现并测试；尚未绑定原生安装处理器，不能把本页当作已可用设备接口。响应/能力/实际运行列表与客户端仍待实现。旧 `/api/app/update/*` 不由新解析器自动解释为集合请求。

## 路由与身份

所有路径位于 `/api/app/v3/`，维护端口仍为 18080；先经现有设备码鉴权（Authorization Bearer），解析器本身不代替鉴权。沿用传输层查询参数 operation_id（或 request_id）、device_mac、offset、sha256，不新增请求头。除 status 外，事务 ID 必须为 32 位十六进制且非零，MAC 必须精确匹配设备规范字符串。principal 来自已鉴权维护入口，不能从客户端正文注入。

| 方法与路径 | 请求体 | 其他参数 |
| --- | --- | --- |
| GET `/api/app/v3/status` | 空 | 无事务要求，仍须设备码鉴权 |
| GET `/api/app/v3/update/result` | 空 | operation_id、device_mac |
| POST `/api/app/v3/update/begin` | ASB3 + 完整 AMF3 | operation_id、device_mac |
| PUT `/api/app/v3/package/0/chunk` | 1–1024 B 原始包字节 | operation_id、device_mac、offset、sha256 |
| POST `/api/app/v3/package/0/ready` | 空 | operation_id、device_mac |
| POST `/api/app/v3/update/commit` | 空 | operation_id、device_mac |
| POST `/api/app/v3/update/cancel` | 空 | operation_id、device_mac |

包索引只能是单字符 0–7，指候选 Manifest 按 ID 排序的条目；具体是否存在/属于 changes 由事务核心二次检查。offset 为无符号规范十进制（允许 0，拒绝前导零、符号、尾随字符及 uint32 溢出），offset+块长度也不能溢出。sha256 是本块字节 SHA256，须逐字节匹配。begin/chunk 的 Content-Type 必须为 application/octet-stream。

## begin 二进制头

恰为 64 B 头 + 原始 AMF3，不做 Base64/JSON 膨胀。总上限 3648 B，低于现有维护请求体上限 4096 B；保留传输层既有限额。

| 偏移 | 字节 | 含义 |
| --- | --- | --- |
| 0 | 4 | ASCII ASB3 |
| 4 | 2 | 小端头版本 1 |
| 6 | 2 | 小端头长度 64 |
| 8 | 32 | expected_current_manifest 内容摘要 |
| 40 | 8 | 小端 expected_current_manifest 集合版本 |
| 48 | 4 | 小端后续 AMF3 字节数，须恰等于正文长度减 64 |
| 52 | 12 | 全零保留 |
| 64 | 64–3584 | 完整 AMF3，由事务核心解析/验证摘要、资源、依赖 |

首次安装 expected 摘要全零、版本为 0；其他情况二者均非零。这里的版本是 Manifest 序号，不是上传进度频繁更新的日志序号。commit 绑定 begin 已冻结的事务身份与围栏，不允许临时改变候选集合。

解析只验证请求边界并返回借用的正文视图，不分配大缓冲、不修改文件或日志。调用者必须检查解析成功，且不能在 HTTP handle 返回后保留正文指针。语法/摘要错误 400，未知路径 404，错误方法 405，正文超限 413。事务级 Conflict/Unknown/Busy 等响应映射尚待处理器实现，不将这些状态混为解析错误。

验证包含合法 begin/chunk/ready，旧路径拒绝、字段保留位污染、MAC 不符、方法/索引错误、整数边界、零事务身份和块摘要不符；宿主 ASan/UBSan 与 RV32 编译通过。尚未进行客户端与真实 HTTP 服务器的完整 v3 往返验证。
