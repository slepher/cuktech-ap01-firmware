# D21：背光提交后动画的局部属性语义与来源

`a00f43bc→a018fb3c→a00df94c(target,0x3e,value,0x20000)` 与本地候选的 **indicator部分、默认状态、阴影透明度** 对应：`LV_STYLE_SHADOW_OPA=62`，`LV_PART_INDICATOR=0x020000`，`LV_STATE_DEFAULT=0`。结合D19/D20的三角path，支持此UI属性按0→约255→0无限往复变化，结束编辑将同一属性置0。实际可见阴影、target控件类型和渲染结果仍未知。这里是具体wrapper/属性定义的局部来源识别，不能由同号枚举认证ROM精确版本或所有属性编号。

动画字段与get/delete局部合同也有候选对应，但存在四项实际差异：ROM复制96B，普通RV32候选声明推得88B；early_apply尾部位置/声明bit不同；ROM start先调用path再exec，候选直接exec(start_value)；ROM重复时保留正的超期余时，候选直接重置为负repeat_delay。因此不能把本地9.2.1当作ROM未改源码。新增ROM功能0、整库排除0。

基线 `24c7b3d1d6e786c0e83aa986038462ab7de15f6e`，独立树 `re0041-d21`、分支 `codex/re-0041-d21`。采用 reverse-engineer-anything 技能的留存优先、事实/推断/未知规则。只读主仓ROM/留存和明确本地候选，不开共享REA target/数据库，不执行ROM、模型、SIM、构建、回放、设备或外网，不创建下级agent。只写本报告和独占analysis，不改共享/主树/生产ROM配置模型或候选，也不撤销其他agent改动。字段名与伪代码均非原源码认证。

## 继承结论：已有 → 行为 → 局限 → 实际缺口

|出处|已有行为与局限|本轮处理|
|---|---|---|
|[D19](backlight-animation-d19-0041-20261024.md)、[D20](backlight-animation-review-d20-0041-20261024.md)|96B descriptor、target/exec/path、2000单周期无限repeat、零完成/删除通知、正常结束编辑清理原序已恢复并独立接受；property/selector符号尚未认证|行为全继承，10个必要旧窗口只与原件比较，不新导出完整函数|
|D20指定 `settings-0041-round2b.json records[10]`，Evidence `ev_d2c060238142516e1df7a388e5984d96623578a75366a96c1472e9ed8c8df9fb`，及旧system/settings complete|已有timer处理→同target/exec查询删除→target值0；不是新清理功能|直接继承，不重新恢复页面/ctx生命周期|
|[F07](display-source-auth-f07-0041-20261023.md)、[F08](display-source-review-f08-0041-20261023.md)|本地候选自报9.2.1、zip成员比较与身份局限；显示/event结构/枚举有ROM差异；LL部分合同已比对|引用来源根及限界。二报告未覆盖本题属性或lv_anim结构/start/delete源行，不重复LL或显示认证|
|[A43](image-cache-source-a43-0041-20261024.md)、[D13](pixel-source-auth-d13-0041-20261024.md)|局部cache/pixel来源对应不能升级整LVGL身份|来源方法直接复用，不把无关合同当本题布局证明|
|[多屏宿主](multi-screen-app-host-0041.md)，`a00b3106`条目|此前已有a01b2eb4全匹配删除与a008bf6e动画启动业务命名|继承“已有动画家族识别”，本题不宣称首次识别动画，也不扩多屏切换|
|D20已筛complete/settings及本轮定向报告查询|同setter地址广泛出现在旧GUI业务，未提供本属性符号认证；旧服务/SIM不能认证ROM ABI|不重扫全部complete、最终ZIP/源码库；查询未命中不等于历史全无研究|

本题新增只限具体属性语义与未覆盖的动画局部来源比较，不是重新恢复GUI业务。

## 本轮复核或纠正：属性与局部来源

`S`仅作为 WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl` 缩写。F07/F08的apps commit不认证ignored解包树、local zip不证明远程签名/获取链、ROM精确来源未知等局限全部继承。仅读7个明确文件必要行，在内存与同父现存 `v9.2.1.zip` 的对应 `lvgl-9.2.1/<path>` 成员比较，7/7相等；不新增hash清单、不全解包、不修改候选。完整必要行与绝对路径见 [candidate-excerpts.json](../../analysis/backlight-animation-source-d21-0041-20261024/candidate-excerpts.json)。

|ROM合同/片段|候选相对S精确位置|局部裁定与限制|
|---|---|---|
|exec只传入byte值；wrapper固定property3e/selector20000|`src/core/lv_obj_style_gen.c:485–491` 的 `lv_obj_set_style_shadow_opa`，`src/misc/lv_style.h:257–260`|候选以数值union调用 `lv_obj_set_local_style_prop(obj,LV_STYLE_SHADOW_OPA,v,selector)`，SHADOW_OPA=62。与ROM目标/值/属性写入形状相符，支持阴影透明度命名。ROM薄wrapper固定selector，候选通用API接收selector参数，不能将ROM wrapper冒称该候选函数未改原体|
|selector固定00020000|`src/core/lv_obj.h:45–48,70–78`，`src/core/lv_obj_style.h:35,41–45`|selector为uint32、parts与state按OR组合；INDICATOR=20000，DEFAULT=0。支持本调用定位indicator默认状态，不是scrollbar(10000)或整个main(0)。没有核全部ROM selector解析/控件渲染|
|值0..255与结束值0|`src/misc/lv_color.h:39–54`|候选OPA_TRANSP=0、OPA_COVER=255；D19/D20已经证明byte截取和三角数值。由局部命名支持“阴影透明度往复”，不能保证阴影宽度/颜色已生效、控件当前可见或实际渲染外观|
|descriptor+00..+20指针槽|`src/misc/lv_anim.h:88–113,123–134`|普通RV32下九个4B槽依次var/exec/custom_exec/start/completed/deleted/get_value/user_data/path，与ROM真实调用槽对应；源prototype支持path返回int32、exec(var,int32)、通知(node)。本题+1c=0可与candidate user_data对应，但不认证ROM原typedef|
|+24..+44值/时间/repeat槽及init|`lv_anim.h:135–143`；`src/misc/lv_anim.c:75–83`，`lv_anim.h:26–27`|start/current/end/duration/act_time/playback_delay/playback_duration/repeat_delay/repeat_cnt顺序与ROM相符；init清零、500/0/100/repeat1/path_linear/early_apply默认相符。duration源码注释ms支持既有2000ms语境，不提供实际墙钟测量；INFINITE=ffffffff对应ROM哨兵|
|start节点复制与自指target修正|`lv_anim.c:90–99`|候选插链、失败返回NULL、按sizeof复制；仅var==输入descriptor时改为新节点，与旧ROM局部身份相符。原调用var为ctx+10对象，不能套用自指分支。本题不重新认证内存不足或所有start前后继|
|start的即时执行|`lv_anim.c:101–120` vs ROM `a008c044..54`|**不同**：候选early_apply执行 `exec(var,start_value)`；ROM从node+20取path，以node调用，得到返回后再exec(target,value)。这处控制/调用差异不由sizeof/enum packing消失。本例path(初始时间)数值可能同起值，但不能据此覆盖原调用顺序|
|get与delete身份及重扫|`lv_anim.c:145–165,174–183`|候选get精确var、exec可空通配；delete两项可空通配，删除后重头扫描；本实例两参数均非0，支持D19/D20同target/exec身份。ROM查询遍历厂商字a00891b2仍未知，不用candidate宏证明其ISA或完整列表算法|
|显式删除通知/释放顺序|`lv_anim.c:701–706`|remove_anim先ll_remove，再deleted_cb(anim)，然后lv_free(anim)，与ROM a008ac06局部合同相符；不调用completed，释放node而非var/ctx。本descriptor通知0，不能推出target最终销毁|
|无限repeat与有限完成|`lv_anim.c:570–595`|候选INFINITE不递减；有限完成摘链→mark change→completed→deleted→free，与ROM必要槽/原序相符。ROM重置活动时间保留已耗时差，候选这里直接设负repeat_delay；本轮不声称整个repeat调度算法一致|

原件仍为主仓 `roms/0041/ap01-1.0.2_0041.bin`，映射base `9ffff000`。关键稀疏原字：`a018fb46:b7060200` 构造selector20000，`fb4a:9305e003` 置property3e；`a008c044:9c50 / c046:2685 / c048:8297` 从+20取path并以node调用；`a008df72:93e70701` 设置early_apply实际mask10。其他必要字节/ABI沿D19/D20引用，未重新输出整窗口。

### 96B与候选尾部不能认证为同一结构

候选 `lv_anim.h:123–154` 无本段条件字段：在普通4B指针/4B对齐RV32前提下，九指针36B、九个32位值36B到+48，8B bezier参数到+50，last_timer_run在+50，flags从+54开始，尾部对齐得88B/+58。ROM按96B/+60复制且early_apply在+5c byte、mask10；candidate early_apply是第4个声明的单bit字段（在通常低bit起的布局为mask08）。因此只接受前+00..+44字段顺序相符，不能照搬候选sizeof、尾部或位域ABI。C位域最终分配依编译器，不把本轮手算当已构建的布局证明；即使保留该限制，ROM path即时调用与候选直接起值调用的差异仍独立成立。

差异来源可能为其他上游版本/本地或厂商修改，当前无法归因；不能将“相对本地9.2.1不同”写成已证明厂商改动。

## 真正新增与恢复程度

新增仅为property/selector局部语义、7文件必要源行定位及动画局部合同/差异对照；新增ROM业务功能0、ISA规则0、完整函数导出0、确证未改可排除项0。D19/D20字段、target身份、三角path、周期repeat与清理行为均继承，未改变既有原序。

事实：ROM数值/调用与旧窗口一致，明确本地候选定义及7个zip成员相等。推断：本调用可识别为indicator阴影透明度更新，动画属于相应LVGL来源家族。未知：精确ROM版本/编译输入、所有属性枚举一致性、实际控件类型/可见渲染、所有离页/ctx释放与厂商遍历字。局部来源识别不升级整库排除。

## 未闭精确边与验证

本题主问在局部来源强度内得到答案；具体UI可见效果仍需要target控件/样式渲染连接，当前不扩style引擎或页面生命周期。96B尾部的实际新增/改动字段和early_apply位布局来源未知；本轮不从候选猜字段，也不猜ctx最终释放。

单一后继建议：由新独立agent复核本题property/selector映射及96B/尾位域/即时path/重复余时四项来源差异，只核必要源行/原件锚点；不重做D19/D20业务，不扩通用style或完整动画。当前不自行接题。

[verify.py](../../analysis/backlight-animation-source-d21-0041-20261024/verify.py) 静态核验通过，[static-result.json](../../analysis/backlight-animation-source-d21-0041-20261024/static-result.json)记录10个旧窗口与原件相等、3个稀疏锚点、7个本地源码/zip成员相等及局部裁定。源行读取使用已授权本地WSL只读访问，未执行源码、固件或模型。报告相对链接、`git diff --cached --check`通过。本轮为研究者自核，技术接受待独立复核。
