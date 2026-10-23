# A54：照片 reader 前缀与 lv_fs open/close 局部来源认证

2026-10-24；基线 `aabdfcd`，分支 `codex/re-0041-a54`。**A47/A49 的 H/D/C reader 前缀、mode byte、普通 open 的 `(D,path,2)` 和 close 的 `(D,H)`、条件缓存归还与清槽，均有本地 LVGL 9.2.1 候选的具体对应。** 只认证局部合同相符，不认证实际driver实例、ROM精确版本或完整库未改；新增ROM业务功能0、整库排除0。

重要载体限制：所读5个本地文件中，4个与现存本地zip对应成员全bytes相等，`gifdec.c`整文件不相等；本题选定的三个GIF file wrapper/open/close连续片段均在zip中原样存在。不能把“所选片段相同”写成“GIF源码全相同”，也不展开本题范围外的差异或read算法。

采用 reverse-engineer-anything 技能，先复用旧complete/最终ZIP与近期来源报告，再只读本地候选必要行。未打开/切换共享REA target，未读取或重导ROM，未执行候选/固件/SIM/模型/构建/回放/设备/外网。未修改主树、共享索引、生产ROM/配置/模型或候选；没有下级agent。A50的`a008b888`内部read消费未接管。

## 继承结论：已有出处 → 行为 → 局限 → 实际缺口

|已有出处|可靠合同与既有覆盖|局限及本轮处理|
|---|---|---|
|[A47](photo-reader-mode-a47-0041-20261024.md)、[A49独立复核](photo-reader-mode-review-a49-0041-20261024.md)|分类1→`a0107d8e`；W清零、+10 byte=1；`a019d6a4(W,source)`的普通driver open槽；`a01b2e3a(O)`以真实 `(D,H)`调用D+10，重读后条件归还缓存并清前三word|全部原字节/实参/顺序继承，不重导。诊断`lv_fs_open`与`/lvgl/src/misc/lv_fs.c`已有，不把候选签名覆盖实际ROM参数|
|A37/A39、A41/A42|成功constructor复制当时W到O，外层非零mode先内部归还后free(O)，清owner槽|输入源所有权与外层O不同，直接引用；不重做constructor、解码或最终页面DELETE|
|A33/A35、A47/A49已复用的`photo-evidence-round3.json`、system complete、最终`ap01-ui-0041-complete-source.zip`|正常五ROM照片mode0；旧业务及SIM替代已覆盖。A47按三个入口查询主rehost，仅page-logic有构造caller；weather-calendar complete已有非零reader分流|沿用既有完整复用边界，不再解包/复制SIM实现；旧业务不能证明五照片实际mode1，旧read分流不能当内部read已闭|
|F07/F08、D13/D14、A43/A44及近期来源结果|同一本地LVGL候选自报9.2.1；local zip不证明远端获取链；显示/event/list等已有真实差异；cache/图像部分合同已有局部对应|本题此前未认证lv_fs/GIF reader前缀；只补5个明确文件，不重复整库、显示/cache或版本历史认证|

实际缺口是A47/A49已可信的字段与生命周期到候选具体源码位置的映射。driver选择的具体注册项仍无实例种子；本题不为了给H命名而扩大到所有文件系统/driver或缓存算法。

## 本轮复核或纠正

`S`统一指 WSL `Ubuntu-24.04:/home/slepher/nuttx-ap01-sim/apps/graphics/lvgl/lvgl`。仅读`src/misc/lv_fs.c`、`lv_fs.h`、`lv_fs_private.h`以及`src/libs/gif/gifdec.h/.c`必要行，并与同父`v9.2.1.zip`的`lvgl-9.2.1/<相对路径>`成员在内存比较，不解包、不建哈希清单。F07/F08的ignored解包树无自身Git、apps commit不认证该树、zip不证明上游签名等限制全部继承。

本轮没有改写A47/A49原行为。需要收紧的是来源层次：前三word可对应`lv_fs_file_t`，但不等于标准`FILE*`；`mode=1`可对应GIF的`is_file`字节，不能与传给driver的`LV_FS_MODE_RD=2`混淆。候选`lv_fs_close`最终返回callback结果，而旧ROM合同未认证全部返回状态、实际caller又忽略它，所以不把候选返回值补进ROM伪代码。

## 真正新增：局部源行映射与来源裁定

|ROM可靠合同|候选精确位置（相对S）|对应与限制|
|---|---|---|
|W/O首三个word为H/D/C；+c输入data；+10 byte mode；+14另清零|`lv_fs.h:88–92`的file_d/driver/cache；`gifdec.h:28–33`的fd/data/is_file/f_rw_p|普通RV32下file结构12B，data在+c、uint8 is_file在+10，uint32位置在+14，和A47前缀相容。只恢复此嵌入前缀，不认证整个gd_GIF尺寸或把候选is_file声明当ROM byte事实的唯一依据|
|`a0107d8e`清零W、mode1、初始化成功才进入既有constructor|`gifdec.c:52–60`、`:773–788`|`gd_open_gif_file`清零局部、以true调用f_gif_open；后者清f_rw_p/data、设is_file、以`lv_fs_open(&fd,path,LV_FS_MODE_RD)`接入，成功再gif_open。候选bool adapter与ROM的初始化返回0门语义相容，不强行将每个源码helper逐一命名为ROM实体或证明未内联|
|D+4配置；可选ready；普通D+c以D/path/2调用；H写W首word|`lv_fs.h:53–56,69–75`；`lv_fs.c:85–118`|char letter后uint32 cache_size、ready/open/close指针；RV32普通对齐下+4/+8/+c/+10对应。候选ready(D)、open(D,real_path,mode)完整实参支持ROM接口；mode枚举RD=2。a019d6a4入口本轮仍只继承实际a0/a1，不能凭通用三参原型发明入口a2|
|source非空后缀为source+1，第二字节冒号则+2|`lv_fs.c:509–535`|默认盘符为0的lean规则先取path[0]作letter、跳首字节、可选跳冒号，和ROM所核普通后缀相容；非0默认盘符分支另有严格A..Z及X:选择规则，不能与前者混用。相容不是ROM的实际宏配置认证|
|非零D+4申请16B C；归还读取C+c；-1配置不归还该字段|`lv_fs_private.h:27–32`；`lv_fs.h:25`；`lv_fs.c:121–137,168–174`|候选C为start/end/file_position三个uint32加buffer指针，RV32共16B且buffer在+c。`LV_FS_CACHE_FROM_BUFFER=UINT32_MAX`解释-1 sentinel与借用buffer责任；普通非零配置buffer需要归还。其余C字段只作条件布局，不认证A50内部读写、首分配/填充或全部缓存策略|
|`a01b2e3a`入口D/close槽为空跳过；正常callback(D,H)；返回后重读config/C；条件buffer→C free；最后清前三word|`lv_fs.c:154–184`；`lv_fs.h:75`|候选先空门返回，再`close_cb(file_p->drv,file_p->file_d)`，之后条件free(buffer)/free(cache)、清file_d/driver/cache，顺序相容。callback不是callback(O)/free(H)，D未归还。源码成员表达不替换ROM已核的回调后重读或入口空门清槽限制|
|外层只在mode byte非零调用内部归还，另free O|`gifdec.c:816–821`|f_gif_close仅is_file为真时`lv_fs_close(&gif->fd)`，支持前缀与flag分层；外层O整体归还依A41/A42，候选片段不能补最终页面DELETE时序|
|driver槽与D的借用角色|`lv_fs.c:391–417`|候选drv_init清零caller的driver；register只新增链节点保存drv指针；get_drv按letter取该指针。支持可注册driver家族解释，但**没有与具体ROM注册函数/某个D实例绑定**，不认证注册算法、driver所有权全生命周期或某一底层文件系统|

本题生命周期表达仍采用ROM偏移视图：W/O保存H/D/C，D为借用；close回调以D/H接收driver自身与handle，由具体driver决定底层动作；通用层按config归还缓存并清前缀，外层另free O。H真实类型、具体callback地址及执行成功均不由候选证明。配置=-1的特殊自指分支只继承A47边界，本轮不新增mapped-buffer全部初始化或失败路径合同。

来源四类裁定：

|分类|本轮结果|
|---|---|
|确证ROM未改、可排除恢复|空；无精确构建输入/版本绑定，整库排除0|
|候选局部合同相符|H/D/C、GIF flag前缀、普通open/close实参、条件缓存归还及清槽，和所核lean后缀规则|
|家族可识别但实例/版本未知|lv_fs driver reader与GIF file adapter家族；候选注册角色不能绑定实际D或底层句柄|
|差异/未认证部分保留|本地gifdec.c整文件与zip不同，三个所选连续片段都相同；差异范围外不展开。候选close返回、默认drive配置、driver实例、完整失败/缓存算法未认证；F07/F08已有其他模块差异不能被本题匹配消除|

三个fs文件及gifdec.h全bytes与本地zip相等，gifdec.c只认证本题三个片段原样存在。事实是源行/载体比较及继承的ROM合同；具体符号映射与来源家族是推断。没有把5个成员比较写成整个包或ROM来源认证。

## 未闭精确边、验证与后继

新增ROM业务功能0、ISA规则0、完整库排除0。仍未知实际source类型1实例所选D、D+c/+10回调目标、H类型、实际driver注册调用与完整寿命、ROM精确版本/配置、完整返回ABI/全部失败臂及运行成功。默认五照片仍按A33/A35的mode0处理，不声称其实际走文件路径。

唯一后继闭包：先取得真实source类型1路径/注册项种子，再把该letter对应的D与open/close回调绑定；没有种子时无需扩全部文件系统。A50 read消费、缓存首次填充及后续独立复核不在本题接管。

[collect.py](../../analysis/photo-reader-source-a54-0041-20261024/collect.py)实际通过56项源锚与5个本地zip成员比较（4整文件相等、GIF三个所选片段相等），没有读ROM或执行候选。必要摘录和逐片段比较见[candidate-evidence.json](../../analysis/photo-reader-source-a54-0041-20261024/candidate-evidence.json)，条件布局/锚点/限制见[review-result.json](../../analysis/photo-reader-source-a54-0041-20261024/review-result.json)。布局为源声明的RV32条件推导，未编译。报告相对链接及`git diff --check`通过。本研究待独立技术复核，不冒称整reader或整个lv_fs完成。
