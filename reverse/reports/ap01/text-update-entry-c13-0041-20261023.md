# 0041 C13：文本格式化更新入口

结论：`a0091ee4` 可识别为 ROM 自报的 `lv_label_set_text_fmt`，直接依赖 `a008bbd8` 自报 `lv_text_set_text_vfmt`。入口把变参通用寄存器保存为连续区；对象 `+0x2c` 的旧文本非空且 `+0x5c` bit4 为零时交给既有释放接口，随后取得新文本指针、写回 `+0x2c`、清 bit4 并调用后续刷新入口。直接依赖先调用底层格式化入口取得数值，按该数值加1申请缓冲，再以相同格式串及变参起点调用底层并返回缓冲指针。两个函数的局部参数、调用和存储合同已恢复；printf 内部、完整 GUI、所有权全生命周期未恢复。

仅本地静态读取和解码。代码来源为 LVGL 路径候选，准确上游版本及厂商修改未知，**无新增开源排除**。报告伪代码和结构名称是分析表达，不是原始源码。

## 范围、基线与来源

固定基线 `8b82f93`，独立工作树 `re0041-c13`、分支 `codex/re-0041-c13`。遵守本树滚动管理 C13 任务书及共同规则，已读 `C:/Users/cogic/.agents/skills/reverse-engineer-anything/SKILL.md`。逐级检查本工作树至盘根以及主仓库根，未发现适用 AGENTS.md。仅写 C13 专属报告和分析目录，不改共享索引、主树或其他工作树。

查重依据：[C09](detail-summary-c09-0041-20261023.md)/[C10](detail-summary-review-c10-0041-20261023.md) 明确保留文本接口内部未知；[C12](detail-mode-update-review-c12-0041-20261023.md)建议本任务；[宿主报告](multi-screen-app-host-0041.md) 只有命名原型，未认证本次内部合同。本次只展开两个核心函数，不重新展开 C09/C10。

- [静态核验脚本](../../analysis/text-update-entry-c13-0041-20261023/verify.py)以主仓库绝对路径只读 `D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware/roms/0041/ap01-1.0.2_0041.bin`，按 `file_offset=address-0x9ffff000` 定位，输出限于本任务目录。
- [原始指令与验证证据](../../analysis/text-update-entry-c13-0041-20261023/instruction-evidence.json)保留完整两函数原字节、逐条解码、所有直接控制目标原编码解算、关键操作数、资源字符串及有界本地来源检索结果。
- [既有 REA inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json)给入口范围 `a0091ee4..a0091f89`（166B，extent Evidence `ev_9bebf4d87defa0d1c2a1cf83c013b26dbd39471d91a976b647a8536709e3b442`），依赖范围 `a008bbd8..a008bc63`（140B，`ev_88c00ee419366a48bd34b527f212e68bfde147e2cf7fd33216cbbee0edeb3306`）。两函数均沿连续指令边界走到各自末尾 ret，未只采用反编译。直接调用 provenance 分别为 `ev_8cb80268149667bc520907372670d32b2e912259897a9eefa88f347dbde5a4fb`、`ev_4a3a5ca0fc65f6d413a5f3e936e89d649bf616a474966461703bc3355c5c0e33`。没有打开共享可写 REA 会话或数据库。

先核来源：入口诊断传入 `lv_label_set_text_fmt`@`a02647f4` 和 `.../lvgl/lvgl/src/widgets/label/lv_label.c`@`a02641a0`；依赖传入 `lv_text_set_text_vfmt`@`a0263794` 和 `.../lvgl/lvgl/src/misc/lv_text.c`@`a0263224`。这些原厂字符串能支持函数命名/来源候选，不能认证源码等价。限定检索主仓库 `reverse/sdk`、`tooling` 的 `lv_label.c/lv_text.c/lv_version.h/lvgl.h/lv_mem.c`，无匹配文件；未外连或下载上游源码。准确版本和厂商修改保持未知，不能凭两遍格式化的库形状将其排除。

## 参数、返回与局部结构

| 入口 | 机器合同与恢复程度 |
| --- | --- |
| `a0091ee4` | a0=对象，a1=格式串，变参通用寄存器从a2开始。正常非空入口先将对象/格式串存s1/s2。没有在该局部读取格式串内容或直接检查格式串是否NULL。返回前最后调用 `a009166e(obj)`，随后只恢复寄存器和栈；本地不设置有业务含义的返回值，原始void typedef未认证。 |
| `a008bbd8` | a0=格式串，a1=变参起点指针。调用 `a0053252(0,0,fmt,va)`，机器返回值加1作为申请量；`a008aea0(size)` 返回非零时调用 `a0053252(buf,size,fmt,va)`，最终明确a0=原申请结果buf。第二遍格式化返回值被忽略。 |

局部结构可表达为 `word text_at_2c; byte flags_at_5c;`，两者偏移相对同一个对象基址；其余字段和完整大小未知。bit4 是本入口的“跳过旧文本释放”判据及随后清除的位。将其称为静态/借用文本标志只是与行为相符的推断，未证明原始位域名、完整所有权类型或对象身份。

变参栈布局由入口原指令直接给出：设入口sp为S，`a0091ee4`减64，`1eea`令s0=sp+32，即S-32；`1ef0..1efc`把a2/a3/a4/a5/a6/a7分别写到S-24/S-20/S-16/S-12/S-8/S-4；`1f5e`令va=s0+8=S-24。该保存区末端与调用者栈参数起点S相接。实际只证明这个 RV32 构造和指针传递；浮点、64位对齐、底层对所有格式类型的处理未认证。`1f64`另将va写本帧局部，但没有改变传给依赖的a1。

## 原指令控制流与所有权边界

| 位置 | 已核事实 |
| --- | --- |
| `a0091f00` | a0非零跳到`1f42`；零路径构造文件/函数/`obj != NULL`与`NULL pointer`诊断，`1f30`调用日志`a008b51a`，`1f3e`调用`a0019672`。未核诊断下层是否返回，不把NULL路径重写成安全返回。 |
| `a0091f42..1f46` | s1=obj，s2=fmt；以原a0=obj调用`a00dddf4`。此调用的内部副作用未展开；旧文本/标志在它之后才读取。 |
| `a0091f4a..1f5a` | 读word(obj+0x2c)，零直接到`1f5e`；非零才读U8(obj+0x5c)，AND0x10；bit4非零同样到`1f5e`。仅旧文本非零且bit4零路径以该指针调用`a008ab8a`，然后word(obj+0x2c)=0。 |
| `a0091f5e..1f68` | a1=va，a0=fmt，直接调`a008bbd8`。本函数没有把新指针作为临时文本交给另一复制setter。 |
| `a0091f6c..1f7a` | 重读flags byte；word(obj+0x2c)=依赖返回a0；a0=obj；flags按AND~0x10后以byte写回；直接调用`a009166e(obj)`。调用后没有第二次释放新指针。 |
| `a008bbe2..bbf2` | a2=fmt、a3=va，保存两者；a1=0、a0=0；JAL至`a0053252`。 |
| `a008bbf6..bc0c` | size=首遍a0+1（32位机器加法），保存size并以a0=size调`a008aea0`；然后重载size、fmt、va为a1/a2/a3，a0仍为申请返回。 |
| `a008bc10..bc54` | 申请返回非零跳`bc52`保存buf并进入第二遍`a0053252`；零路径诊断含`text != NULL`、`Out of memory`，经日志和`a0019672`后布局上也落到`bc52`。未认证诊断返回属性，正常合同仅描述非零申请分支。 |
| `a008bc58..bc62` | 恢复寄存器时明确a0=s1=buf；不返回第二遍格式化的长度。 |

释放接口沿用已验收[C03](pogo-close-callback-c03-0041-20261023.md)/[C04](pogo-close-review-c04-0041-20261023.md)及[生命周期报告](uiiface-lifecycle-0041-20261023.md)：`a008ab8a`对NULL及静态哨兵`62fc95e0`返回，其他指针交底层释放；本次不扩allocator。`a008aea0`是申请缓冲的接口候选，其完整实现未展开；本次可直接认证的事实为请求量、返回值被当指针使用、非零分支及后续存储。bit4非零路径只证明本函数不释放旧指针，不证明别处如何处理其生存期。

## 必要伪代码与直接依赖

以下只表正常非空对象、申请非零路径；诊断分支保留上表，不能由伪代码推断其异常返回行为。

```c
// 局部机器合同；不是原始C或可执行参考模型。
text_update_local(obj, fmt, va_from_saved_a2_to_a7) {
    opaque_a00dddf4(obj);
    old = WORD(obj + 0x2c);
    if (old != 0 && (U8(obj + 0x5c) & 0x10) == 0) {
        release_a008ab8a(old);
        WORD(obj + 0x2c) = 0;
    }
    new_text = text_vfmt_a008bbd8(fmt, va_from_saved_a2_to_a7);
    flags = U8(obj + 0x5c);
    WORD(obj + 0x2c) = new_text;
    U8(obj + 0x5c) = flags & ~0x10;
    opaque_refresh_a009166e(obj);
}

pointer text_vfmt_nonzero_allocation_local(fmt, va) {
    n = opaque_format_a0053252(0, 0, fmt, va);
    size = wrapping_add32(n, 1);
    buf = opaque_allocate_a008aea0(size); // 本表达只续写非零分支
    opaque_format_a0053252(buf, size, fmt, va);
    return buf;
}
```

两遍调用对同一个底层传递相同的fmt和va指针，第二遍多传buf和size。依赖本身不扫描字符、不实现格式分派，也不显式写NUL。“首遍求字符数，+1预留终止符，第二遍格式化到新缓冲”是函数自报名和此数据流支持的强推断；底层实际支持哪些格式、va读取/推进方式、是否终止及具体长度约定仍未认证。尤其“同va地址”不等同已经证明底层完全不修改其所指内容。

`a009166e`只认证入口参数obj及调用顺序，内部重排/事件/动画不在本次范围；也未将`a00dddf4`的前置调用直接等同某种视觉效果。入口先处理旧指针再获得新指针是原指令顺序事实，本任务不对失败/异常输入构造验证，不推断缺陷。

## 事实、推断、未知与验证

**事实**：两函数原字节、166/140B连续边界、变参寄存器保存、15个全部直接控制目标、参数宽度与对象偏移、释放分支极性、两遍调用实参、返回buf、资源函数名与源路径。**推断**：LVGL来源候选、bit4为静态/借用文本属性、首遍取长度和第二遍写文本的库语义、刷新/分配的业务命名。**未知**：准确版本/厂商修改、原始typedef、底层printf能力及长度/NUL约定、完整allocator、完整对象/文本生命周期和并发规则、诊断是否返回、完整GUI效果、运行时可达性。

实际运行 `python reverse/analysis/text-update-entry-c13-0041-20261023/verify.py` 成功：2窗口306B、101普通指令、0厂商word；15个全部直接控制目标从原编码独立解算，36个关键操作数核对，9条ROM字符串读取，边界与既有REA inventory一致。关键分支不依赖反编译；两窗口不存在未解码厂商槽。来源检索0匹配只适用于列明的两个目录/五个文件名，不扩大成全机无源码结论。未执行固件、业务模型、畸形输入或历史回放，未连接设备/外部服务，未改ROM/生产代码/安全检查/分析器模型，未新哈希或复制清单。

后继建议：C14独立复核本次两函数，重点检查va栈布局、旧文本bit4条件与两遍格式化调用/存储顺序；保持printf、allocator、完整GUI内部为边界。
