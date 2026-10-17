from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

root = Path('D:/Documents/PlatformIO/Projects/codex_status').resolve()
up = (root.parent / 'cuktech-ap01-firmware-tools').resolve()
art = root / 'artifacts/ap01-research'
manifest = json.loads((art / 'migration-manifest.json').read_text(encoding='utf-8'))
check = json.loads((art / 'migration-check.json').read_text(encoding='utf-8'))
assert not check['errors']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(up), *args])

assert git('rev-parse', 'HEAD').decode().strip() == manifest['upstream_head']
assert set(git('diff', '--name-only', '-z').decode('utf-8').strip('\0').split('\0')) == set(manifest['restore_tracked'])
archive = root / manifest['source_archive']
assert sha(archive.read_bytes()) == manifest['source_archive_sha256']
remove = []
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for item in manifest['sources']:
        source = (up / item['source']).resolve()
        assert source.is_relative_to(up) and source != up
        data = source.read_bytes()
        assert sha(data) == item['sha256'], f'Source changed: {source}'
        assert z.read(Path(item['source']).as_posix()) == data
        if item['destination']:
            dest = (root / item['destination']).resolve()
            assert dest.is_relative_to(root) and dest.is_file()
            if '/raw/' in dest.as_posix():
                assert dest.read_bytes() == data
            item['final_destination_sha256'] = sha(dest.read_bytes())
            remove.append(source)
        elif '__pycache__' in source.parts:
            remove.append(source)
assert not git('ls-files', '--', *[str(p.relative_to(up)) for p in remove]).strip(), 'Refuse to delete tracked files'
for name, expected in manifest['restore_tracked'].items():
    assert sha(git('show', f'HEAD:{name}')) == expected

# Individual allowlisted files only, after backup and target checks; no recursive deletion.
for source in remove:
    source.unlink()
git('restore', '--source=HEAD', '--worktree', '--', *manifest['restore_tracked'])
parents = {parent for p in remove for parent in p.parents if parent != up and parent.is_relative_to(up)}
for parent in sorted(parents, key=lambda p: len(p.parts), reverse=True):
    if parent.is_dir() and not any(parent.iterdir()):
        parent.rmdir()
assert not git('status', '--porcelain').strip(), 'Unexpected remaining changes; do not auto-clean'
manifest['cleanup'] = {'removed_files': len(remove), 'restored_tracked_documents': len(manifest['restore_tracked']), 'upstream_status': 'clean', 'head_unchanged': True}
(art / 'migration-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(manifest['cleanup']))
