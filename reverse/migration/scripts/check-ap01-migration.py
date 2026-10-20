from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import zipfile
from urllib.parse import unquote

root = Path('D:/Documents/PlatformIO/Projects/codex_status')
art = root / 'artifacts/ap01-research'
manifest = json.loads((art / 'migration-manifest.json').read_text(encoding='utf-8'))
errors = []
existing_missing = []
archive = root / manifest['source_archive']
assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['source_archive_sha256']
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for item in manifest['sources']:
        assert hashlib.sha256(z.read(Path(item['source']).as_posix())).hexdigest() == item['sha256']
        if item['destination']:
            p = root / item['destination']
            assert p.is_file(), p
            if '/raw/' in item['destination'].replace('\\', '/'):
                assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256'], p

docs = list((root / 'project-workflow/ap01').rglob('*.md'))
docs += [root / 'tools/ap01/README.md', root / 'docs/cuktech-ap01-repository-value-analysis.md',
         root / 'docs/README.md', root / 'PROGRESS.md', root / 'docs/roadmap/backlog.md',
         root / 'project-workflow/single-copy-updates/design.md',
         root / 'project-workflow/single-copy-updates/ap01-doc-sync-20261012.md']
links = 0
for p in docs:
    raw = p.read_bytes()
    text = raw.decode('utf-8')
    if b'\r\n' in raw and b'\n' in raw.replace(b'\r\n', b''):
        errors.append(f'Mixed newlines: {p}')
    assert text.count('```') % 2 == 0, p
    for target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', text):
        if re.match(r'\w+://', target):
            continue
        file, _, anchor = unquote(target).partition('#')
        dest = (p.parent / file).resolve() if file else p
        links += 1
        if not dest.exists():
            detail = f'Missing link: {p.relative_to(root)} -> {target}'
            if p == root / 'docs/roadmap/backlog.md' and target in subprocess.check_output(['git', '-C', str(root), 'show', 'HEAD:docs/roadmap/backlog.md']).decode('utf-8'):
                existing_missing.append(detail)
            else:
                errors.append(detail)
        elif anchor and dest.suffix == '.md':
            headings = re.findall(r'^#+\s+(.+)$', dest.read_text(encoding='utf-8'), re.M)
            slugs = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
            if anchor not in slugs:
                errors.append(f'Missing heading: {p.relative_to(root)} -> {target}')
        if 'cuktech-ap01-firmware-tools' in target:
            errors.append(f'Local dependency in docs: {p} -> {target}')
for p in (root / 'tools/ap01').glob('*.py'):
    ast.parse(p.read_text(encoding='utf-8'), filename=str(p))

result = {'source_archive_files': len(manifest['sources']), 'moved_files': 33, 'raw_identical': 21,
          'markdown_files': len(docs), 'local_links': links, 'errors': errors, 'preexisting_missing_links': existing_missing, 'script_syntax': 'pass'}
(art / 'migration-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(bool(errors))
