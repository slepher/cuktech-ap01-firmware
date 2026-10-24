# K06：slider 构造请求、返回门与初始位置独立复核

2026-10-24；基线 `7e633b1`；独占树/分支 `re0041-k06` / `codex/re-0041-k06`。**限定接受 K05，无实质语义纠正、新增功能0。** 循环控制的是8轮请求；child返回和20B wrapper返回各有独立门，正常返回配置路径汇回同一请求递增点。实际child count用于选择x=0或320，不是成功申请计数，也没有因此建立全程 `N>0 && idx<N` 不变量。

采用已读 [reverse-engineer-anything skill](C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md)。复核者未参与K05生产；没有运行或导入K05验证器，也没有把其JSON当作原件。只读主仓ROM与明确旧证据；未打开/切换共享REA target，不运行固件、SIM、模型、构建、历史回放、输入实验、设备或外部服务，不做异常输入/漏洞/缺陷验证。仅写本路独占报告/analysis，未改生产代码、ROM、配置、分析器模型或其他任务文件，无下级agent。

## 继承结论

|既有出处|可靠合同，直接继承|本轮边界|
|---|---|---|
|[K05](window-slider-construction-k05-0041-20261024.md)|已解释8d2a起请求计数、child/wrapper返回门、实际count决定位置|待审主张，不以作者自检替代独立原件；只核此构造问题|
|[K03](window-slider-contract-k03-0041-20261024.md)、[K04](window-slider-review-k04-0041-20261024.md)|class/global对象身份、constructor将+38/+3c置0、count wrapper为无符号16位、事件/导航前置边界|不重验class表或事件机制，不把构造零索引外推全程不变量|
|[E05](ctk-app-close-e05-0041-20261023.md)、[E06独立复核](ctk-app-close-review-e06-0041-20261023.md)|generic factory的class/parent保存和非空parent的u16 count增加、重分配及追加；厂商srw shift2已接受|直接继承parent挂接，不再导出factory或重核厂商字|
|[H04](weather-page-close-review-h04-0041-20261023.md)、E06|a00d7806是class析构walker；公共删除核心另负责父数组移除、count更新和对象本体free|wrapper空分支只按真实调用表达，不补完整删除/回滚|
|K05/K03/J04的旧complete、SIM与资源范围|旧SIM验收和日常窗口属于各自限定对象/来源|不重跑SIM，不套日常active=count−1，不提取颜色/文字/全资源或重建源码|

旧真实种子为主仓 `evidence/rea-0041-20261017/evidence/whole-rom-private-20261023-068.json`，Evidence `ev_70c4f2e4ab81d16f68ee9e092f50824c912cdae172d69b06e93511cdc1f54e18`。本轮只读其 `structuredContent.normalized_result.assembly` 中必要控制/寄存器行与精确直接调用查询，未复制整dispatcher或产生新REA Evidence ID。

## 本轮复核或纠正

独立 [review.py](../../analysis/window-slider-construction-review-k06-0041-20261024/review.py) 直接读取 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，映射 `offset=VA−0x9ffff000`。使用Capstone 5.0.7离线解码，并自行按bit位核JAL、B、C.B、C.J及word访存字段；结果见 [review-result.json](../../analysis/window-slider-construction-review-k06-0041-20261024/review-result.json)。没有执行目标指令、创建对象或触发分配结果。

|K05主张|独立原件锚点|裁定/限制|
|---|---|---|
|s2是请求编号，不再是较早的O|8d2a置s2=0；8d2c LW s5,0(s7)；8d30 BNE s5,0→8d68；8d66为自跳|接受。O每轮重读；未认证跨调用稳定或真实执行断言分支|
|child和wrapper为两次独立请求|8d68把O送a0，8d6a→a00d91c6，8d6e保存child至s1；8d72置14h，8d74→a008e362，8d78保存另一返回至s10|接受两层返回/身份。20B是申请实参，不等于额外child或成功数|
|child零与wrapper零各有原门|8d70 C.BEQZ a0→8d82；8d7a C.BNEZ a0→8dd0；零wrapper路径8d7c传child，8d7e真实JAL→a00d7806|接受caller的条件控制流。这不认证下层在真实正常运行会返回0，不宣称执行过失败路径|
|请求递增与成功结果分离|8d82 C.ADDI s2,1；8d84置8；8d86 BNE s2,a5→8d2c。零child与walker正常返回均到8d82|接受0..7请求编号；正常终止8轮不证明8个成功/可用/保留孩子|
|配置路径持有wrapper|8dd4/8ddc以s1作已有flag调用的对象；8de2 SW s10,10(s1)|接受child内保存wrapper指针；内容/资源/最终释放不展开|
|正常返回配置路径汇合到请求递增|8e7a/8e80分别选择request5/6分支，8e84非零的其他request直接回8d82；所选配置尾部8f86、904a、90fa的C.J目标均为8d82|接受必要控制边；仅核退出边，不重做中间文字/图像装配或callee效果。控制回边不是配置实际成功证明|
|实际count决定初始位置|8e5e以本轮parent s5为a0；8e60→a00a491c。8e64置1、8e66置y0、8e68置x320；8e6c为BLTU 1,N→8e72，否则8e70改x0；8e72以child作a0，8e74→a00d8d1e|接受unsigned谓词 `N>1 ? 320 : 0`，因此x0包含N≤1，不能写成request==0或仅N==1|
|普通child创建接入同generic factory|d91d0 parent→a1，d91d2/6构造class a0263ef4，d91da→a00d76ae；d91de非零去d9220保存对象，d9222初始化，d922a从s1恢复返回|接受非零对象正常路径的薄接入，generic append已由E06接受；不重新认证完整分配/初始化及其副作用|
|没有以loop次数验收最终N/索引|8d86退出后8d8a已读取其他byte；旧068中精确直接setter目标a00a4aa0查询为空，s2相关普通赋值仅8d2a置0、8d82加1|接受K05的有界结论：所列caller没有最终非零count/有效索引验收，也没有所查直接setter调用。不能排除被调初始化/尺寸/样式服务经间接callback改变状态|

实质语义纠正0。K05对wrapper空分支的收紧正确：调用class walker不等于公共删除/父count递减回滚。E06的parent挂接发生于普通child创建中，早于caller另申请wrapper，所以wrapper配置成功数也不能等同于parent结构count。

## 真正新增

**新增功能、ISA规则、准确来源认证和整函数导出均为0。** 本次只增加未参与生产的agent对K05构造条件合同的独立接受，以及必要原字/控制边索引。K03/K04事件与class、E05/E06通用挂接、H04析构层次和旧SIM验证不重计。

可保留的结论始终带条件：若相同O、索引仍为0，且至少一个成功挂接的child保留到观察点，则N≥1且索引0有效；若额外保证初始N=0、全部8次创建/挂接正常、无其他增删，才可推出N=8。循环本身没有证明这些额外保证；本轮没有以静态分支存在冒充申请失败/成功或运行期对象可用性的观察。

## 精确未闭与实际验证

未闭：各申请实际结果、所有孩子可用性；循环期间全局O稳定性与进入时N=0；初始化/配置callee及其间接事件对count/当前与先前索引的影响；观察点至少保留一个child和整个生命周期不变量；附属wrapper/资源最终归还。没有新writer/callback种子，不扩全GUI、根析构或颜色文字分支。

实际运行本路独立脚本：**47项稀疏原件检查PASS**，含必要返回门/递增汇合、直接目标、标准/压缩控制边、word存取与位置实参；另对一个旧body做精确setter/counter查询。JSON、报告相对链接及diff检查通过。未运行K05脚本、目标ROM、SIM、模型、构建或历史回放。

本构造问题达到有证据的条件答案及可定位断边；本轮不自行接下一题。没有支持遍历所有GUI以填满全程不变量的新连接，后续由管理者另按真实种子去重决定。
