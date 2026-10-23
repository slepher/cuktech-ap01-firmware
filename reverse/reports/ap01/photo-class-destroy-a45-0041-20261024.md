# A45：照片具体 class 析构的有界接入断边

2026-10-24；基线 `82be763`，分支 `codex/re-0041-a45`。使用 reverse-engineer-anything 技能，仅静态只读0041原件和已有材料。**本轮没有获得把照片 ctx[0] 绑定到实际 installed class 的可信 creator/callee 种子，因此未闭合具体 class 析构到 owner+0x5c 的 O 及+0x74派生槽的 DELETE 清理。新增功能为0；按任务书无种子即有界交付。** 不把旧 setter 的释放路径外推成最终对象析构。

## 继承结论：已有出处→行为→局限→实际缺口

|已有出处|解释行为|证据局限与实际缺口|
|---|---|---|
|[A33](photo-source-abi-a33-0041-20261024.md)、[A35](photo-source-review-a35-0041-20261024.md)；主仓 `photo-evidence-round3.json#/rea_records/3`，`ev_e3db1fb1f6b8b75d3ba7fbf202ad701f4cd3b8eb42987c05789f1e2626527941`|type7子页wrapper+4取得ctx，ctx[0]是照片轮转setter `a00ed7f4` 的owner；五项源轮转已恢复|这是使用者到owner的身份，未提供owner由哪个creator分配、class字段写入的定义链；不能由setter位置命名class|
|主仓 `main-knob-0041-round2.json#/records/1`，`ev_daf583e6c481f2d7f53eb8443cd04003d53c22365147ac088957c1415a947da7`；`system-complete-0041.json#/cached_evidence/main_a00afc88`|同一consumer原汇编及完整主旋钮body已有|完整的是caller，不能因此称照片具体析构已有完整合同；较晚round3也不消除这个定义链缺口|
|[A37](photo-decoder-owner-a37-0041-20261024.md)、[A39](photo-decoder-review-a39-0041-20261024.md)|O单块分配`0x4664+5N`，借用ROM data；owner+0x5c持O、+0x74持O内部输出区|所有权布局继承；没有class身份，不据布局挑选一个邻近析构函数|
|[A41](photo-decoder-destroy-a41-0041-20261024.md)、[A42](photo-destroy-review-a42-0041-20261024.md)|旧O非空setter替换：cache失效→读U8(O+0x10)→mode0直接free(O)→清+0x5c→清+0x74→新source分类|已闭的是setter正常替换，DELETE是否调用同样流程仍未知；不重导setter、cache或allocator|
|[H03](weather-page-close-h03-0041-20261023.md)|通用删除核心`a00dcf52`在事件交付/子项递归后调`a00d7806(obj)`；walker按class+8调用`dtor(class,obj)`并进入base|可靠公共合同直接引用；该双参ABI不能改成descriptor的单参`callback(event)`。天气/窗口类身份不适用于照片owner|
|最终ZIP `tools/ap01/ap01-ui-pages.h`；旧SIM/最终验收|替代页面用`lv_gif_create(g_ap01_ui_root)`，随后`lv_gif_set_src(pet,...)`|只读成员。SIM名称及行为不是ROM creator、class常量、析构ABI或退出时序认证；没有执行资源或脚本|

## 本轮复核或纠正

没有纠正A33–A42或H03。只核consumer的必要原字节身份窗口，见 [evidence.json](../../analysis/photo-class-destroy-a45-0041-20261024/evidence.json)。原件、SHA身份和`offset=VA-0x9ffff000`沿用A33/A35，未新建哈希账。

`a00b17ec`置a1=7；`17ee`直接调`a00dcee4`；`17f2`读返回子页+0x10为wrapper，`17f4`读wrapper+4为s1=ctx；`a00b1810`从ctx+0加载a0，`1816`直接调`a00ed7f4`。这些窄窗只复核已有owner身份，不提供class写入或最终删除调用。其伪代码为分析重建，非原源码：

```c
page = a00dcee4(parent, 7);       // consumer查询，不是creator
wrapper = load32(page + 0x10);
ctx = load32(wrapper + 4);
owner = load32(ctx + 0);
a00ed7f4(owner, selected_source); // source/厂商加载ABI继承A33/A35
```

复用范围：旧photo/knob/system complete指定记录，最终ZIP指定成员，主仓`reverse/rehost/*round3*.json`按`a00ed7f4/a00b1816/a055fe44`查较晚材料，以及已有whole-ROM retained bundle按精确`a00ed7f4`文本查记录。本轮未重新导出整函数。retained命中四项：procedure inventory、`a00ed85e`单指令、`a00f4d92` dossier、`a00afc88` dossier；详见JSON中的Evidence IDs及参数。`a00ed85e`属于setter中资源实参，两个dossier的setter引用不能单独建立creator；inventory是地址目录。该边界下没有可引用的照片class完整合同，不能将未命中说成历史从未分析。

探索中还读过邻近`a00ed0a8` factory前缀及少量`a00ed000..a00eda40`局部指令用于排除“setter邻近即照片creator”的命名捷径；未得到其返回值写入照片ctx[0]的连接，因此不将那个class常量作为照片证据，不保留无关完整body、不继续沿它扩GUI。没有全ROM字段扫描、root退出负搜索、全class搜索或动画/算法/资源解码。

## 真正新增

新增功能、具体析构合同、资源恢复、来源认证及标准库排除均为 **0**。新增内容仅是有界复用结果和上述owner身份短窗的复核记录。没有基于`lv_gif_create`名字或LVGL候选源码推测ROM地址；也没有将释放O内部派生区描述为另一次free。

## 未闭精确边、验证与一个后续闭包

已知链为：type7 page→page+0x10 wrapper→wrapper+4 ctx→ctx[0] owner→owner+0x5c O、owner+0x74内部输出指针。未知边为：**实际构造中返回对象写入ctx[0]的调用点→该对象installed class常量→class+8具体析构入口→在DELETE调用条件下对同一个O和派生槽的清理。** 公共walker只能提供条件调用ABI，不能补上这个对象定义链。析构是否清+0x74、是否先free后清槽，均不能套用setter答案。

事实：稀疏原字节load/call及既有记录内容；推断：当ctx[0]与setter owner保持同一身份时适用已有O布局；未知：该对象构造/class身份、具体最终析构、主app正常退出触发、动态实际安装及执行。旧反编译中的custom0限制按A33保留，SIM/照片替代与ROM原字节分列；此结果不是运行验证或缺陷判断。

[verify.py](../../analysis/photo-class-destroy-a45-0041-20261024/verify.py)只读ROM与已有JSON/ZIP，6项必要owner身份/直接调用检查PASS；JSON解析、报告相对链接及`git diff --check`通过。未开REA target或共享可写数据库；无固件执行、SIM、构建、回放、设备、外网、模型/生产代码/ROM/配置修改。本报告为有界研究交付，待独立技术复核，不能冒称照片最终析构已完成。

唯一后续闭包：仅在已有页面构造留存中取得“实际call返回值→照片ctx[0] store”的定位证据后，再沿那个creator所用class核class+8及同owner的O清理；没有这个种子则本题保持断边，不从主app退出或所有GUI对象重新搜索。
