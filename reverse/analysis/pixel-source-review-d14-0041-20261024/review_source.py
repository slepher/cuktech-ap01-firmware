"""Read only D13's selected source lines; no candidate execution or archive reread."""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'pixel-source-auth-d13-0041-20261024/candidate-evidence.json'

if __name__ == '__main__':
    prior = json.loads(OLD.read_text(encoding='utf-8'))
    request = []
    expected = []
    for member in prior['members']:
        request.append({'path': member['path'], 'ranges': [
            [part['start'], part['end']] for part in member['excerpts']]})
        expected.append({'path': member['path'], 'excerpts': member['excerpts']})
    program = '''import json
from pathlib import Path
request = json.loads(%r)
out = []
for member in request:
    with Path(member['path']).open() as stream:
        selected = {}
        last = max(b for a,b in member['ranges'])
        for number, line in enumerate(stream, 1):
            if number > last: break
            if any(a <= number <= b for a,b in member['ranges']):
                selected[number] = line.rstrip('\\n\\r')
    out.append({'path': member['path'], 'excerpts': [
        {'start':a,'end':b,'lines':[str(n)+': '+selected[n] for n in range(a,b+1)]}
        for a,b in member['ranges']]})
print(json.dumps(out, ensure_ascii=False))
''' % json.dumps(request)
    result = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec',
                             'python3', '-c', program], capture_output=True, check=True)
    current = json.loads(result.stdout.decode('utf-8'))
    assert len(current) == 10
    assert current == expected, 'Selected source lines differ from D13 retention'
    evidence = {'candidate_root': prior['root'], 'scope':
                'Independent current line reads only; archive equality inherited from D13; no ROM read',
                'selected_lines_equal_d13': True, 'source_text_retained_at': str(OLD),
                'members': [{'path': item['path'], 'selected_ranges': [
                    [part['start'], part['end']] for part in item['excerpts']],
                    'selected_lines_equal_d13': True} for item in current]}
    (HERE / 'review-evidence.json').write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('PASS: 10 members selected lines equal D13; no archive/ROM reread or target execution.')
