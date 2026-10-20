from pathlib import Path
import json
import re
from urllib.parse import unquote

root = Path('D:/Documents/PlatformIO/Projects/codex_status')
ap = root.parent / 'cuktech-ap01-firmware-tools'
manifest = json.loads((root / 'artifacts/ap01-doc-sync-20261012-files.json').read_text(encoding='utf-8'))
paths = [Path(item['path']) for item in manifest]
paths += [root / 'PROGRESS.md', root / 'project-workflow/single-copy-updates/ap01-doc-sync-20261012.md', ap / 'reference/DESIGN/AP01-Bridge静态逆向.md']
errors, links, anchors = [], 0, 0
for p in paths:
    raw = p.read_bytes()
    text = raw.decode('utf-8')
    if b'\r\n' in raw and b'\n' in raw.replace(b'\r\n', b''):
        errors.append(f'Mixed newlines: {p}')
    if text.count('```') % 2:
        errors.append(f'Unbalanced fence: {p}')
    for line in text.splitlines():
        if line != line.rstrip():
            errors.append(f'Trailing whitespace: {p}')
    for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
        if re.match(r'\w+://', target):
            continue
        file, _, anchor = unquote(target).partition('#')
        dest = (p.parent / file).resolve() if file else p
        links += 1
        if not dest.exists():
            errors.append(f'Missing link: {p} -> {target}')
        elif anchor and dest.suffix == '.md':
            anchors += 1
            headings = re.findall(r'^#+\s+(.+)$', dest.read_text(encoding='utf-8'), re.M)
            slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
            if anchor not in slugs:
                errors.append(f'Missing heading: {p} -> {target}')

design = (ap / 'reference/DESIGN/AP01-Bridge接入与资源预算.md').read_text(encoding='utf-8')
for required in ['暂存下载、预检、停止旧应用、覆盖并读回校验', '下载或预检失败保留旧应用', 'max_bundle_decoded_bytes', '原生固件 OTA 双槽保留', 'bundle_storage_protocol=2']:
    assert required in design, required
for stale in ['完整A/B Bundle', '再接收、逐项校验', '逐块覆盖唯一应用文件', '主项目当前全局512', '另一项改动进行中']:
    assert stale not in design, stale
assert 262144 + 64 + 262144 + 11365 * 8 + 65536 == 680808
assert 680808 + 262144 == 942952
assert 942952 + 524288 == 1467240
assert 942952 + 262144 == 1205096
assert 1310720 - 1205096 == 105624
result = {'files': len(paths), 'local_links': links, 'heading_links': anchors, 'errors': errors, 'budget_checks': 5, 'scope': 'documentation only; no firmware or device verification'}
(root / 'artifacts/ap01-doc-sync-20261012-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(bool(errors))
