"""Index retained 0041 evidence; never execute or modify firmware.

This is a bounded evidence crosswalk, not a function-discovery/decompiler tool.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHA = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
BASE = 0x9ffff000
ADDRESS = re.compile(r'(?<![0-9a-z])(?:0x|ram[_:])([aA][0-9a-fA-F]{7})(?![0-9a-fA-F])')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    rom = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
    image = rom.read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA, 'Wrong ROM'
    inventory_path = ROOT / 'reverse/analysis/factory-code-resources-0041-inventory.json'
    inventory = read_json(inventory_path)
    assert inventory['rom_sha256'] == SHA
    matrix_path = ROOT / 'reverse/reports/ap01/application-function-matrix-0041.json'
    matrix = read_json(matrix_path)
    assert matrix['source_sha256'] == SHA
    inputs = {relative(rom): SHA, relative(inventory_path): digest(inventory_path),
              relative(matrix_path): digest(matrix_path)}
    script_path = pathlib.Path(__file__).resolve()
    inputs[relative(script_path)] = digest(script_path)
    files = {}
    path_addresses = {}
    for group, entries in inventory['c_groups'].items():
        for entry in entries:
            path = entry['path']
            # Verify a whole NUL-terminated string at its recorded ROM offset.
            offset = int(entry['rom_offset'], 16)
            assert image[offset:offset + len(path) + 1] == path.encode() + b'\0'
            path_addresses[BASE + offset] = path
            files[path] = dict(entry, group=group, functions=[], candidates=[],
                              full_file_reverse_complete=False)

    resources = {}
    address_resources = collections.defaultdict(list)
    for item in inventory['png'] + inventory['gif']:
        offset = int(item['rom_offset'], 16)
        resource_id = f"{item['kind']}@{item['rom_offset']}"
        assert hashlib.sha256(image[offset:offset + item['size']]).hexdigest() == item['sha256']
        resources[resource_id] = dict(item, id=resource_id, references=[],
                                     descriptors=[], semantic_review_complete=False)
        address_resources[BASE + offset].append((resource_id, 'payload-address'))
    for font in inventory['fonts']:
        resource_id = 'FONT@' + font['wrapper']
        resources[resource_id] = dict(font, id=resource_id, kind='FONT',
                                     references=[], semantic_review_complete=False)
        address_resources[int(font['wrapper'], 16)].append((resource_id, 'font-wrapper'))

    # Recover candidate LVGL descriptors by matching a real payload pointer at
    # descriptor+0x10. Header and size must also agree; otherwise retain a pointer
    # carrier candidate, never promote it to a descriptor.
    payloads = {BASE + int(v['rom_offset'], 16): v for v in resources.values()
                if v['kind'] in ('PNG', 'GIF')}
    for position in range(16, len(image) - 3, 4):
        pointer = struct.unpack_from('<I', image, position)[0]
        target = payloads.get(pointer)
        if target is None:
            continue
        start = position - 16
        magic = image[start]
        size = struct.unpack_from('<I', image, start + 12)[0]
        if magic != 0x19 or size != target['size']:
            continue
        address = BASE + start
        resources[target['id']]['descriptors'].append(hex(address))
        address_resources[address].append((target['id'], 'validated-image-descriptor'))

    functions = {}
    excluded = []
    observations = []

    def observe(address, text, source, locator, evidence_id=None, profile=None,
                limitations=None, refs=None, identity='retained-function-entry'):
        if not address or not re.fullmatch(r'0xa[0-9a-f]{7}', str(address).lower()):
            return
        address = str(address).lower()
        fn = functions.setdefault(address, dict(address=address, evidence=[], files={},
                                               resources={}, names=[], limitations=[],
                                               extent_complete=False))
        origin = dict(source=source, locator=locator, evidence_id=evidence_id,
                      profile_digest=profile, identity=identity)
        fn['evidence'].append(origin)
        for limit in limitations or []:
            if limit not in fn['limitations']:
                fn['limitations'].append(limit)
        # Only explicit address-bearing observations are used for automatic
        # ownership/resource links. Name similarity is never enough.
        addresses = {int(x, 16) for x in ADDRESS.findall(text)}
        for ref in refs or []:
            if isinstance(ref, dict):
                value = ref.get('target_address') or ref.get('address')
                if value:
                    try:
                        addresses.add(int(value, 16))
                    except (ValueError, TypeError):
                        pass
        referenced_text = []
        for target in sorted(addresses):
            offset = target - BASE
            if 0 <= offset < len(image):
                end = image.find(b'\0', offset, offset + 512)
                if end > offset and all(32 <= byte <= 126 for byte in image[offset:end]):
                    referenced_text.append(image[offset:end].decode('ascii'))
            if target in path_addresses:
                path = path_addresses[target]
                fn['files'].setdefault(path, []).append(dict(origin, string_address=hex(target),
                    relation='source-path-reference; may reflect inlining or merged function body'))
            for resource_id, relation in address_resources.get(target, []):
                fn['resources'].setdefault(resource_id, []).append(dict(origin,
                    target_address=hex(target), relation=relation,
                    confidence='retained-address-reference; runtime use not established'))
        name_pattern = r'\b(?:lv_page_ui_|lv_win_ui_|j_win_ui_|j_page_ui_|lv_window_)[A-Za-z0-9_]+'
        for name in re.findall(name_pattern, '\n'.join(referenced_text) + '\n' + text):
            # These are string/symbol mentions, not necessarily the function name.
            if name not in fn['names']:
                fn['names'].append(name)
        observations.append(origin)

    # Retained REA dossiers, including the flattened records from later audits.
    paths = sorted((ROOT / 'reverse/rehost').glob('*.json'))
    paths += sorted((ROOT / 'reverse/analysis').glob('*.json'))
    for path in paths:
        if path.name.startswith(('factory-code-resources', 'factory-reference-map')):
            continue
        try:
            bundle = read_json(path)
        except (ValueError, UnicodeError):
            continue
        if not isinstance(bundle, dict):
            continue
        records = bundle.get('records', [])
        usable = False
        for index, record in enumerate(records if isinstance(records, list) else []):
            if not isinstance(record, dict) or record.get('operation') != 'analyze_function':
                continue
            subject_sha = record.get('subject', {}).get('digest', {}).get('sha256')
            if subject_sha != SHA:
                excluded.append(dict(source=relative(path), locator=f'/records/{index}',
                                     reason='record subject is not exact 0041', subject_sha=subject_sha))
                continue
            result = record.get('normalized_result', record)
            if not isinstance(result, dict):
                continue
            procedure = result.get('procedure', {})
            address = procedure.get('address') or record.get('parameters', {}).get('procedure')
            if not address:
                continue
            # Pseudocode addresses and explicit data references; do not mine
            # arbitrary result metadata, caller addresses or neighboring functions.
            text = result.get('pseudocode') or ''
            refs = result.get('referenced_strings', []) + result.get('referenced_names', [])
            refs += [r for r in result.get('outgoing_references', [])
                     if r.get('kind', {}).get('data')]
            profile = record.get('analysis_profile') or {}
            observe(address, text, relative(path), f'/records/{index}', record.get('evidence_id'),
                    profile.get('digest'), record.get('limitations', []) + result.get('limitations', []), refs)
            usable = True
        # Selected screen-host records retain explicit per-function procedures.
        if bundle.get('original_sha256') == SHA:
            for index, item in enumerate(bundle.get('functions', [])):
                if isinstance(item, dict) and isinstance(item.get('pseudocode'), str):
                    observe(item.get('procedure'), item['pseudocode'], relative(path),
                            f'/functions/{index}', item.get('evidence_id'), item.get('profile_digest'),
                            ['Selected retained function; synthetic-object execution is a separate scope.'])
                    usable = True
        if usable:
            inputs[relative(path)] = digest(path)

    # Historical original-ROM Ghidra exports cover creator continuations missing
    # from false-noreturn dossiers. Keep seed boundaries instead of guessing
    # source functions inside a merged decompiler body.
    for path in sorted((ROOT / 'reverse/analysis/0041-20261013').glob('0041-ghidra-pass*.txt')):
        text = path.read_text(encoding='utf-8', errors='replace')
        if f'sha256={SHA}' not in text[:500]:
            continue
        inputs[relative(path)] = digest(path)
        starts = list(re.finditer(r'^=== seed ram:([a-f0-9]+) ===', text, re.M))
        for index, match in enumerate(starts):
            end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
            block = text[match.end():end]
            line = text.count('\n', 0, match.start()) + 1
            observe('0x' + match[1], block, relative(path), f'line:{line}',
                    limitations=['Historical generic RV32 seed body; source ownership, inlining, '
                                 'vendor instructions and function boundary remain subject to audit.'],
                    identity='historical-ghidra-seed')

    # Evidence-backed functions do not need a source-file guess to be useful:
    # keep unassigned functions as a first-class queue.
    for address, fn in functions.items():
        for path in fn['files']:
            files[path]['functions'].append(address)
        for resource_id, links in fn['resources'].items():
            resources[resource_id]['references'].append(dict(function=address, evidence=links))
        fn['file_attribution'] = ('multiple-source-paths; ownership unresolved' if len(fn['files']) > 1
                                  else 'single-source-path reference; not full ownership proof' if fn['files']
                                  else 'unassigned')
        fn['reverse_status'] = 'partial-retained-analysis; full body/branches/dependencies not certified'

    # Match creator *string mentions* to the existing tested family matrix.
    # This preserves successful SIM work without calling it native-function closure.
    features = []
    for feature in matrix['features']:
        name = feature['native_creator']
        hits = [address for address, fn in functions.items() if name in fn['names']]
        features.append(dict(id=feature['id'], creator=name, family=feature.get('family'),
                             sim_status=feature['status'], mention_functions=hits,
                             native_creator_entry_proven=False,
                             evidence=feature.get('evidence', []),
                             runtime_evidence=feature.get('runtime_evidence', [])))
    for path, entry in files.items():
        entry['functions'].sort()
        entry['status'] = 'partial: retained source-path/function links' if entry['functions'] else 'gap: no retained source-path/function link collected'
        entry['completed_scope'] = ('UI family SIM reconstruction and acceptance; not per-file branch closure'
                                    if entry.get('in_ui_matrix') else 'ROM filename string verified; consult module reports for semantic progress')
        entry['remaining'] = ['Reconcile all original functions and split inlined/merged bodies',
                              'Resolve indirect callbacks and transitive resources',
                              'Audit complete error, cleanup, persistence and hardware paths']
        if path.startswith('lv_power_ui/') or path == 'lvgl_ui_main.c':
            entry['progress_reference'] = 'reverse/reports/ap01/application-rehost-complete-0041-20261017.md'
            entry['semantic_progress'] = '已有UI家族重建/验收；不替代本文件全部函数归属与分支核账'
        elif path.startswith('PogoPinMng/'):
            entry['progress_reference'] = 'reverse/reports/ap01/mijia-task-dependencies-0041-20261017.md'
            entry['semantic_progress'] = '已有底座、天气、UART/USB依赖与服务合同线索；本文件完整覆盖未认证'
        elif path.startswith('miio_sdk/'):
            entry['progress_reference'] = 'reverse/reports/ap01/upper-layer-0041-20261017.md'
            entry['semantic_progress'] = 'MiIO 162根及90命令关联已有后续局部实现审阅；不能由单一路径代表全进程'
        elif path.startswith(('lv_lunar_calendar/', 'lv_comp_calendar/')):
            entry['progress_reference'] = 'reverse/reports/ap01/application-rehost-complete-0041-20261017.md'
            entry['semantic_progress'] = '已有农历、日期表及日历行为恢复/测试；函数到C路径归属仍须核对'
        elif path.startswith('SystemSettings/'):
            entry['progress_reference'] = 'reverse/reports/ap01/knowledge/0041-sim-wifi-selection-gaps.md'
            entry['semantic_progress'] = '已有SIM保存服务；原厂持久化与Wi-Fi格式兼容性仍开放'
        else:
            entry['progress_reference'] = 'reverse/reports/ap01/multi-screen-app-host-0041.md'
            entry['semantic_progress'] = '工厂滑动器已有定位；未见完整工厂测试流程验收'
        progress_path = ROOT / entry['progress_reference']
        inputs[entry['progress_reference']] = digest(progress_path)

    slider_path = ROOT / 'reverse/analysis/screen-host-slider-20261020.json'
    slider = read_json(slider_path)
    assert slider['original_sha256'] == SHA and slider['passed'] is True
    inputs[relative(slider_path)] = digest(slider_path)
    for address in ['0xa00b3106', '0xa00b3080', '0xa00b30c0', '0xa00ab628']:
        if address in functions:
            functions[address]['completed_validation'] = dict(
                source=relative(slider_path), scope='bounded original slider/move/ready execution',
                passed=True, allocation_executed=False, full_ui_executed=False,
                hardware_verified=False)

    total_links = sum(len(fn['resources']) for fn in functions.values())
    summary = dict(files=len(files), files_with_function_links=sum(bool(v['functions']) for v in files.values()),
                   files_without_function_links=sum(not v['functions'] for v in files.values()),
                   retained_functions=len(functions), functions_with_file_links=sum(bool(v['files']) for v in functions.values()),
                   functions_with_multiple_files=sum(len(v['files']) > 1 for v in functions.values()),
                   function_resource_pairs=total_links, resources=len(resources),
                   resources_with_function_links=sum(bool(v['references']) for v in resources.values()),
                   image_descriptors=sum(len(v.get('descriptors', [])) for v in resources.values()),
                   creators_with_sim_acceptance=len(features), full_files_certified=0)
    return dict(schema=1, rom_sha256=SHA, base=hex(BASE), input_sha256=inputs, summary=summary,
                methodology=['Exact-ROM retained evidence only; other versions excluded',
                             'Source file association requires an actual source-path address reference',
                             'Image descriptors require magic 0x19, data_size match and payload pointer at +0x10',
                             'Resource and name mentions do not prove execution, whole-function semantics or ownership',
                             'Missing collected reference means unknown, not unused or never previously analyzed'],
                files=files, functions=functions, resources=resources, sim_features=features,
                excluded_records=excluded,
                open_gaps=['No complete per-file/per-function/per-branch denominator',
                           'RAM-initialized pointer tables and dynamic resource selection not closed',
                           'Full /resource partition and Boot2 outside this XIP ROM',
                           'Wi-Fi persistence/binding compatibility remains open',
                           'MiIO/MiBLE subsequent upper-layer audit supersedes older seed counts'],
                coverage_reports=['reverse/reports/ap01/application-rehost-complete-0041-20261017.md',
                                  'reverse/reports/ap01/upper-layer-0041-20261017.md',
                                  'reverse/reports/ap01/knowledge/0041-sim-wifi-selection-gaps.md'])


def markdown(data):
    s = data['summary']
    lines = ['# 0041 原厂 C 文件 → 函数 → 资源引用与逆向缺口', '',
             f"ROM SHA256：`{data['rom_sha256']}`；映射基址 `{data['base']}`。", '',
             '本清单索引现有离线 REA/Ghidra 证据，不是新一轮全 ROM 反编译。当前 REA MCP 无活动目标，Windows 提供方声明的支持范围未包含 RV32，未重新打开原件。', '',
             '## 状态口径', '',
             '- **已完成的范围**：33 项构造器对应业务家族在既有 SIM 验收中通过；原件资源已提取/字体已恢复的范围另计。',
             '- **部分完成**：已有原件函数分析、文件路径引用或资源引用；不等于整个函数、C 文件或原厂硬件行为已完成。',
             '- **待补关联**：此次扫描的离线证据没有建立对应边，不能解释为从未分析、资源未使用或代码不存在。',
             '- 单个函数引用多个 C 路径时保留全部关联，不按邻近地址或名称强行归属。函数名列是日志中的名称提及，不保证就是当前函数名。',
             '- 资源边仅指直接数据地址/校验过的 LVGL 描述符/字体 wrapper；不把整个证据文件中共同出现的资源归给全部函数。', '',
             '## 数量', '',
             f"- 文件路径 {s['files']} 个；建立函数关联 {s['files_with_function_links']} 个，待补关联 {s['files_without_function_links']} 个。",
             f"- 收录函数/历史 seed {s['retained_functions']} 个；有文件路径关联 {s['functions_with_file_links']} 个，多文件关联 {s['functions_with_multiple_files']} 个。",
             f"- 图像及字体节点 {s['resources']} 个；有函数引用 {s['resources_with_function_links']} 个；函数—资源组合 {s['function_resource_pairs']} 对。",
             f"- 从原件校验得到图像描述符 {s['image_descriptors']} 个；完整 C 文件认证数为 0，不据此计算全 ROM 完成率。", '',
             '## 文件覆盖总表', '', '| 原厂/定制路径 | 函数关联数 | 已完成范围 | 仍缺 |', '| --- | ---: | --- | --- |']
    for path, entry in data['files'].items():
        done = entry['semantic_progress']
        missing = '全函数与分支、间接引用、硬件/持久化' if entry['functions'] else '先补路径→函数关联；并对照专项证据'
        lines.append(f"| `{path}` | {len(entry['functions'])} | {done} | {missing} |")
    for path, entry in data['files'].items():
        progress = entry['progress_reference']
        lines += ['', f'## {path}', '', f"已有进展：{entry['semantic_progress']}。[专项依据](../../../{progress})。", '', '| 函数/seed 地址 | 名称提及（非函数命名结论） | 图像/字体引用 | 状态与证据 |', '| --- | --- | --- | --- |']
        if not entry['functions']:
            lines.append('| 待补关联 | — | 未建立，不等于无资源 | 已确认 ROM 文件路径 |')
        for address in entry['functions']:
            fn = data['functions'][address]
            names = ', '.join(f'`{v}`' for v in fn['names'][:8]) or '匿名/未保留名称'
            if len(fn['names']) > 8:
                names += f"；另 {len(fn['names']) - 8} 项见 JSON"
            res = []
            for resource_id in fn['resources']:
                resource = data['resources'][resource_id]
                label = '/'.join(resource.get('rehost_names', [])) or resource.get('name') or '未命名'
                res.append(f'`{resource_id}` ({label})')
            sources = sorted({v['source'] for v in fn['files'][path]})
            status = '部分；多文件/内联归属待核' if len(fn['files']) > 1 else '部分；日志路径关联'
            if fn.get('completed_validation'):
                status += '；已完成原件滑动有界执行（合成对象，无完整UI/实机）'
            links = ', '.join(f'[{v.rsplit("/", 1)[-1]}](../../../{v})' for v in sources)
            lines.append(f"| `{address}` | {names} | {'<br>'.join(res) or '待补：此证据未建立直接资源边'} | {status}；{links} |")
    lines += ['', '## 33 项既有 SIM 验收对照', '',
              '以下保留既有通过结论；命中地址仅是构造器名字符串的引用，不直接当作构造器入口。', '',
              '| 构造器名称 | 家族 | 已完成范围 | 名称提及所在函数/seed |', '| --- | --- | --- | --- |']
    for feature in data['sim_features']:
        hits = ', '.join(f'`{v}`' for v in feature['mention_functions']) or '待补名称→入口对应'
        lines.append(f"| `{feature['creator']}` | {feature['family']} | {feature['sim_status']}（SIM 家族场景） | {hits} |")
    lines += ['', '## 已有函数证据、但 C 文件归属待补', '',
              '| 函数/seed | 资源引用 | 证据文件 |', '| --- | --- | --- |']
    for address, fn in sorted(data['functions'].items()):
        if fn['files']:
            continue
        sources = ', '.join(sorted({v['source'] for v in fn['evidence']}))
        lines.append(f"| `{address}` | {', '.join(fn['resources']) or '待补'} | {sources} |")
    lines += ['', '## 资源归属缺口', '',
              '下列项有已验证图像边界或既有字体清单，但本次证据未建立函数引用。已用于 SIM 也仍可能缺少原件归属边。', '',
              '| 资源 | 重建名称 | 提取/重建状态 | 下一步 |', '| --- | --- | --- | --- |']
    for resource_id, resource in data['resources'].items():
        if resource['references']:
            continue
        names = '/'.join(resource.get('rehost_names', [])) or resource.get('name') or '未命名'
        status = '原字体已恢复' if resource['kind'] == 'FONT' else '已入 SIM 清单' if resource.get('rehost_names') else '已识别边界，未入 SIM 清单'
        lines.append(f'| `{resource_id}` | {names} | {status} | 描述符/表/RAM 初始化/动态选择引用追踪 |')
    lines += ['', '## 优先补齐顺序', '',
              '1. 补齐无函数关联的应用文件，优先工厂测试、底座通信、USB 更新、设置持久化；先复核现有专项报告再做新采集。',
              '2. 拆解多文件/多页面 seed，核对真实函数边界和日志调用点，不沿用错误 no-return 截断。',
              '3. 补资源表、RAM 初始化和动态选择边；优先未纳入重建清单的 93 PNG 与 1 GIF。',
              '4. 逐项核对错误、取消、超时、释放、重入、掉电恢复及真实硬件，建立函数级验收。',
              '5. MiIO/MiBLE 采用 upper-layer 后续报告的 315 函数/537 未采集直接 callee/161 未定向调用历史快照，不能将旧 seed 数当作当前完成率。', '',
              '完整边、每条 Evidence ID、profile、JSON 指针/文本行号、限制、输入哈希及排除的其他版本记录均见 [机器清单](../../analysis/factory-reference-map-0041.json)。']
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Recompute and verify existing JSON/Markdown')
    parser.add_argument('--refresh', action='store_true', help='Regenerate this script-owned JSON/Markdown')
    args = parser.parse_args()
    data = build()
    json_path = ROOT / 'reverse/analysis/factory-reference-map-0041.json'
    md_path = ROOT / 'reverse/reports/ap01/factory-reference-map-0041-20261020.md'
    text = markdown(data)
    if args.check:
        assert read_json(json_path) == data, 'JSON differs from recomputed evidence'
        assert md_path.read_text(encoding='utf-8') == text, 'Markdown differs'
    else:
        for path in [json_path, md_path]:
            if path.exists() and not args.refresh:
                raise FileExistsError(path)
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        md_path.write_text(text, encoding='utf-8')
    print(json.dumps(data['summary'], ensure_ascii=True))
