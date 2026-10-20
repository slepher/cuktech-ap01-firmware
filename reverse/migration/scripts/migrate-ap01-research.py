from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import zipfile
from urllib.parse import quote, unquote

ROOT = Path('D:/Documents/PlatformIO/Projects/codex_status')
UP = ROOT.parent / 'cuktech-ap01-firmware-tools'
DOC = ROOT / 'project-workflow/ap01'
ART = ROOT / 'artifacts/ap01-research'
SHA = '3bd98a8ca4fb35a9f8869121b13961d405b16dff'
mapping = {}
for p in (UP / 'project-workflow/bridge-port-analysis').glob('*.md'):
    mapping[p] = DOC / p.name
for p in (UP / 'project-workflow/bridge-port-analysis/raw').rglob('*'):
    if p.is_file():
        mapping[p] = ART / 'raw' / p.relative_to(UP / 'project-workflow/bridge-port-analysis/raw')
for old, new in [
    ('reference/DESIGN/AP01-Bridge接入与资源预算.md', 'design.md'),
    ('reference/DESIGN/AP01-Bridge静态逆向.md', 'reverse-design.md'),
    ('knowledge/AP01-官方固件分析/0031分区与启动入口复查.md', 'knowledge/0031分区与启动入口复查.md'),
    ('knowledge/AP01-官方固件分析/0031网络监听与HTTP复查.md', 'knowledge/0031网络监听与HTTP复查.md'),
]:
    mapping[UP / old] = DOC / new
for name in ['__main__.py', 'resource_budget.py']:
    mapping[UP / 'features/bridge_port_analysis' / name] = ROOT / 'tools/ap01' / name

tracked = ['reference/brief.md', 'reference/SPEC.md', 'reference/design.md', 'reference/requirements.md',
           'knowledge/AP01-官方固件分析/离线恢复与救砖证据.md',
           'knowledge/AP01-官方固件分析/通信、存储、更新与恢复.md']
original = {p: p.read_bytes() for p in mapping}
original.update({UP / p: (UP / p).read_bytes() for p in tracked})
for p in (UP / 'features/bridge_port_analysis/__pycache__').glob('*'):
    if p.is_file():
        original[p] = p.read_bytes()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(UP), *args])

assert git('rev-parse', 'HEAD').decode().strip() == SHA
# All tracked modifications must be exactly the research appendices inspected before migration.
bases = {}
for name in tracked:
    base = git('show', f'HEAD:{name}')
    current = original[UP / name].decode('utf-8').replace('\r\n', '\n')
    assert current.startswith(base.decode('utf-8').replace('\r\n', '\n').rstrip()), name
    bases[name] = digest(base)
assert set(git('diff', '--name-only', '-z').decode('utf-8').strip('\0').split('\0')) == set(tracked)

def rewrite_links(text, source, dest):
    def convert(match):
        label, target = match.groups()
        if re.match(r'[a-zA-Z]+://', target) or target.startswith('#'):
            return match[0]
        path, sep, anchor = unquote(target).partition('#')
        resolved = (source.parent / path).resolve()
        if resolved in mapping:
            target = os.path.relpath(mapping[resolved], dest.parent).replace('\\', '/')
        elif resolved.is_relative_to(UP):
            target = f'https://github.com/andy-JustSayWhen/cuktech-ap01-firmware-tools/blob/{SHA}/' + quote(resolved.relative_to(UP).as_posix())
        else:
            target = os.path.relpath(resolved, dest.parent).replace('\\', '/')
        return f'[{label}]({target}{sep}{anchor})'
    return re.sub(r'\[([^\]\n]*)\]\(([^)\n]+)\)', convert, text)

def relocate_prose(text):
    for old, new in [
        ('features/bridge_port_analysis', 'tools/ap01'),
        ('project-workflow/bridge-port-analysis', 'project-workflow/ap01'),
        ('reference/DESIGN/AP01-Bridge接入与资源预算.md', 'project-workflow/ap01/design.md'),
        ('knowledge/AP01-官方固件分析/0031分区与启动入口复查.md', 'project-workflow/ap01/knowledge/0031分区与启动入口复查.md'),
    ]:
        text = text.replace(old, new)
    return re.sub(r'(?<![/\w-])raw/', 'artifacts/ap01-research/raw/', text)

outputs = {}
for source, dest in mapping.items():
    assert dest.parent.is_dir() and not dest.exists(), dest
    data = original[source]
    if source.suffix == '.md':
        text = rewrite_links(data.decode('utf-8').replace('\r\n', '\n'), source, dest)
        text = relocate_prose(text)
        text = text.replace('独立应用槽的回退由新底座负责，原厂两个固件槽不会自动替它回退。', '单份独立应用覆盖失败后由稳定底座提供内置恢复与认证重传，原厂两个固件槽不会自动恢复应用文件。')
        outputs[dest] = (text.rstrip() + '\n').encode('utf-8')
    elif source.suffix == '.py':
        text = data.decode('utf-8').replace('\r\n', '\n')
        text = text.replace('ROOT = Path(__file__).resolve().parents[2]', 'PROJECT = Path(__file__).resolve().parents[2]\n# Read-only upstream inputs; research code and outputs belong to codex_status.\nROOT = PROJECT.parent / "cuktech-ap01-firmware-tools"')
        if source.name == 'resource_budget.py':
            text = text.replace('\nPROJECT = ROOT.parent / "codex_status"\n', '\n')
        outputs[dest] = text.encode('utf-8')
    else:
        outputs[dest] = data

parts = ['# AP01 研究需求、规格与依赖\n\n本文件迁自本次研究追加到第三方文档的段落；上游原有产品需求与安装流程仍归原项目，不复制为本项目要求。\n']
for name, marker, title in [
    ('reference/brief.md', '### BRIEF-RE-001', '需求'),
    ('reference/SPEC.md', '### SPEC-RE-001', '验收规格'),
    ('reference/requirements.md', '静态逆向工具额外使用', '研究工具依赖'),
]:
    source = UP / name
    text = original[source].decode('utf-8').replace('\r\n', '\n')
    text = text[text.index(marker):]
    parts.append('## ' + title + '\n\n' + relocate_prose(rewrite_links(text, source, DOC / 'requirements.md')).rstrip() + '\n')
parts.append('## 原厂编译配置补充\n\n原先追加到上游通信与恢复文档的说明统一引用 [0031分区与启动入口复查](knowledge/0031分区与启动入口复查.md)：编译配置不能代替设备实际分区、读回、切槽及独立恢复证据。\n')
outputs[DOC / 'requirements.md'] = '\n'.join(parts).encode('utf-8')

# Preserve every source byte before removal or restoration. The backup remains local/ignored.
archive = ART / 'source-before-move.zip'
assert not archive.exists()
with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
    for path, data in original.items():
        z.writestr(path.relative_to(UP).as_posix(), data)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for path, data in original.items():
        assert z.read(path.relative_to(UP).as_posix()) == data

for path, data in outputs.items():
    assert not path.exists(), path
    path.write_bytes(data)
    assert path.read_bytes() == data

# Repoint references in the owner repository. Upstream-source references become pinned URLs.
updated = []
for path in [ROOT / 'docs/cuktech-ap01-repository-value-analysis.md']:
    text = path.read_text(encoding='utf-8')
    text = rewrite_links(text, path, path)
    text = text.replace('应结合 `cuktech-ap01-firmware-tools` 的现有接入设计使用', '应结合本仓库的 AP01 接入设计使用')
    text = text.replace('，另有本地分析文件', '，仅作为只读上游参考')
    text = text.replace('原厂固件逆向、修改包制作与安装、四页看板，以及接入当前 Bridge 的设计和资源试算', '原厂固件修改包制作与安装、四页看板；本项目接入研究见下方本地文档')
    text = text.replace('ROM 仓库本地的', '本仓库的')
    text = text.replace('ROM 仓库现有设计选择', '本仓库接入设计选择')
    text = text.replace('ROM 预算建议', '本项目预算建议')
    text = text.replace('保持 ROM 仓库已有的完整接入方向', '保持本仓库 AP01 设计的完整接入方向')
    text = text.replace('沿用 ROM 仓库的接入设计', '沿用本仓库的接入设计')
    text = text.replace('以 ROM 专项后续证据为准', '以本仓库 AP01 专项后续证据为准')
    path.write_text(text, encoding='utf-8', newline='\n')
    updated.append(str(path.relative_to(ROOT)))

manifest = {
    'upstream_head': SHA, 'source_archive': str(archive.relative_to(ROOT)),
    'source_archive_sha256': digest(archive.read_bytes()),
    'sources': [{'source': str(p.relative_to(UP)), 'sha256': digest(data),
                 'destination': str(mapping[p].relative_to(ROOT)) if p in mapping else None}
                for p, data in original.items()],
    'destinations': [{'path': str(p.relative_to(ROOT)), 'sha256': digest(data)} for p, data in outputs.items()],
    'restore_tracked': bases, 'updated_local_docs': updated,
}
(ART / 'migration-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'copied': len(mapping), 'raw_files': sum('/raw/' in str(p).replace('\\','/') for p in mapping), 'archive_files': len(original), 'upstream_cleaned': False}))
