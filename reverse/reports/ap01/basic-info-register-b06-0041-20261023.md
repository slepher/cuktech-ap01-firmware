# B06：a01b28ce 的直接注册合同

2026-10-23；基线 `59b27d4`，分支 `codex/re-0041-b06`。直接合同已恢复，待独立技术复核。本文为静态分析伪代码，不是原始源码。

## 问题与结论

`a01b28ce(a0=callback_word,a1=userdata_word)` 使用 `62fcb530` 的链表头，逐节点比较 `node+0` 与原 a0。**只以 callback word 去重，不比较 userdata。** 命中即返回，不更新旧 userdata；未命中则调用 `a008af14(&header)` 追加节点，随后写 `node+0=callback_word`、`node+4=userdata_word`。本函数没有调用 callback。

返回寄存器的形状不同：命中路径直接 `ret`，a0 仍是传入 callback word；追加路径从 append 得到的节点地址一直保留在 a0 后返回。原 C 返回类型/typedef 未知，不能人为统一成成功布尔值、索引或稳定节点句柄。B04 所示调用点不消费返回值。

因此不能将 B04 的 `for(i) register(a00a3c8a,i)` 直接描述成“创建每个 i 的独立订阅”。在链表有效、相关调用返回且没有范围外改写的前提下，已经出现同一 callback 的后续调用不会更新其 userdata；首次未命中才存当次 i。这是由局部合同推得的条件结论，不是实际执行观察。

## 函数与结构

| 函数 / 范围 | 参数、返回及直接关系 |
| --- | --- |
| `a01b28ce..a01b2919`，核心 | a0 callback word，a1 userdata word；遍历或调用 `a008af14`，返回寄存器见上。边界与保留 inventory 的76字节 body一致，结尾 `a01b2918` 是压缩ret。 |
| `a008af14..a008af67`，核心 | a0=header；读取 header+0 的 payload_size，加8传 `a008aea0`；返回节点或零。非零路径把两个链字段写入新节点，旧尾非零时改旧尾next，更新tail，原head为空则更新head。 |
| `a0089cda..a0089ced`，短直接依赖 | a0 header、a1 node、a2 value；node非零时 `word[node+header.payload_size]=value`，用于新节点prev。无业务返回值认证。 |
| `a0089cee..a0089d01`，短直接依赖 | 同参数；node非零时 `word[node+header.payload_size+4]=value`，用于新节点next及旧尾next。无业务返回值认证。 |

`a008aea0` 只作为 append 的不透明分配依赖：调用点请求 `payload_size+8`，返回零/非零控制是否进入链接写入。本任务不展开其内部分配实现。没有额外恢复完整容器库。

```c
// 偏移为指令事实；名称是根据读写关系推断。所有字段为32位word。
struct HeaderPartial {
    uint32_t payload_size; // +0，运行时读取；本任务不认证初始值为8
    uint32_t head;         // +4
    uint32_t tail;         // +8
};
// node不是固定C结构：payload后两个word由header.payload_size定位。
// node+0 callback_word、node+4 userdata_word（本次注册函数固定写入）。
// node+payload_size prev、node+payload_size+4 next（链访问器决定）。
```

## 指令依据与伪代码

`a01b28ce/28d2` 构造 header=`62fcb530`；`28d6` 取 head=`word[header+4]`，`28d8/28da` 计算 next_offset=`word[header]+4`。`28dc` 节点非零才到 `290c`。`290c/290e` 仅比较 callback word，等于跳 `2918`；否则 `2912` 的 word `40d7470b` 是 `th.lrw a4,a4,a3,0`，按既有本地模型读取 `a4=word[a4+a3]`，`2916` 回节点非零测试。a0、a1在这一遍历过程中均未改写。

未命中落到 `28de` 才创建栈帧，`28ea/28f0` 保存两个原参数，`28ec` 重新传 header；`28f2/28f6` AUIPC/JALR精确目标为 `a008af14`。返回后 `28fa` 的压缩sw写 callback，`28fc` 的32位sw写 userdata，两者均以原 a0 为节点。`2900..290a` 恢复并ret，不重写a0。

append 的 `a008af22/24/26` 请求size+8；`af2c` 返回零则直接到返回尾部。非零路径依次为：`af2e..34` 新next=0；`af38..3e` 新prev=原tail；`af42..4a` 原tail非零则原tail.next=新节点；`af4e..50` 先读head、再写tail；`af54..56` 原head为空则写head。`af60` 明确a0=保存的新节点/零。没有认证所有被调函数的其他寄存器副作用或整个容器生命周期。

```c
// 分析投影：WORD/load/store表示原32位访问，不补造原typedef。
word append_a008af14(HeaderPartial *h) {
    word n = opaque_a008aea0(h->payload_size + 8);
    if (n != 0) {
        store_word(n + h->payload_size + 4, 0);       // next
        store_word(n + h->payload_size, h->tail);    // prev
        if (h->tail != 0)
            store_word(h->tail + h->payload_size + 4, n);
        word old_head = h->head;
        h->tail = n;
        if (old_head == 0) h->head = n;
    }
    return n;
}

word register_a01b28ce(word callback_word, word userdata_word) {
    HeaderPartial *h = (void *)0x62fcb530;
    word p = h->head;
    word next_offset = h->payload_size + 4; // 遍历前快照
    while (p != 0) {
        if (load_word(p) == callback_word)
            return callback_word; // 已证a0，不认证原源语言返回类型
        p = load_word(p + next_offset);
    }
    word n = append_a008af14(h);
    store_word(n, callback_word);
    store_word(n + 4, userdata_word);
    return n;
}
```

伪代码保持原指令控制流，不补检查、替换返回或修改存储次序；不进行失败条件测试或缺陷验证。append中size可由两访问器分别重读，以上字段表达式保留这一关系；注册遍历的next_offset则只在入口计算一次。

B04调用点的 `a00a8b50` 传a1=s1，`8b52` 传a0=s2-0x376=`a00a3c8a`，`8b56/5a` 调本函数，`8b5e` s1加1，`8b60` 回比较。未在这里调用或恢复 `a00a3c8a` 消费者，也不解释基础信息对象构造。

## 证据、验证与边界

- [instruction-evidence.json](../../analysis/basic-info-register-b06-0041-20261023/instruction-evidence.json)包含4个有界窗口、逐条原字节、ROM文件偏移及解码。范围是注册76字节、append84字节、两个短访问器共40字节、调用点18字节。边界沿用 [whole-rom inventory](../../analysis/whole-rom-coverage-0041-20261023-round1.json) 的extent记录；注册body Evidence `ev_53000907732796d3d150db318ecb9c97e70b0b537f0daa8916462daca7cf3264`，append body Evidence `ev_3c1e6adecc849a4b6df0d1bb0e524e6d49d9da9d9795d52f5f19dec85678c9cf`。本任务直接读原ROM并逐条解码，没有另建共享REA数据库。
- [verify.py](../../analysis/basic-info-register-b06-0041-20261023/verify.py)实际执行通过：4窗口、89普通指令、2厂商word、13直接分支/JAL目标、2 AUIPC/JALR目标。普通指令用Capstone RV32+C解码；关键存储、条件及ret核到编码。两个厂商word逐字段核op/funct/寄存器/shift：`a01b2912` indexed load与 `a0089ce4` indexed store。附既有 `ap01thead2.sinc` 的 `th.lrw/th.srw` 原文和行号；这沿用本地观察模型，不冒充新的上游ISA认证，不改模型。
- 命令：`python reverse/analysis/basic-info-register-b06-0041-20261023/verify.py D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware`。执行仅为静态读取与辅助解码，未执行ROM、设备、外部服务、运行时探测或生产构建；未新增哈希/基线复制清单。复核期间曾因辅助脚本一个断言误写访问器偏移0而失败，核原指令确认是+4后改正，最终上述验证通过。

**事实**：参数保存、比较键、固定payload写入、链字段偏移、寄存器返回、指令顺序和局部调用边。**推断**：callback/userdata、head/tail/prev/next为读写关系命名；“注册”沿用任务及调用点线索。**未知**：header初始化及实际payload_size、原类型/并发合同、callback签名和执行时序、清空/删除、其他消费者、原分配器内部行为。不能因字段命名断言开源容器来源；本次代码均保留厂商/来源未知状态，无来源版本认证、无新增开源排除，整个基础信息模块仍部分恢复。

下一小任务：独立复核本报告的callback唯一键、userdata不更新、两种a0返回形状、next_offset快照及两个厂商indexed访问，不展开callback消费者或header构造。
