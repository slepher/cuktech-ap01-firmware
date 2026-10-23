"""Read selected A43 source lines independently; never execute candidate code."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
prior = json.loads((HERE.parent / 'image-cache-source-a43-0041-20261024/candidate-evidence.json').read_text(encoding='utf-8'))
requests = [{'path': item['path'], 'ranges': [[s['start'], s['end']] for s in item['snippets']]} for item in prior['files']]
remote = '''import json
requests=%r
results=[]
for item in requests:
 wanted={n for a,b in item['ranges'] for n in range(a,b+1)}
 selected={}
 with open(item['path'], encoding='utf-8') as source:
  for number,line in enumerate(source,1):
   if number in wanted: selected[str(number)]=line.rstrip('\\r\\n')
   if number >= max(wanted): break
 results.append({'path':item['path'],'lines':selected})
print(json.dumps(results))
''' % requests
result = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--', 'python3', '-c', remote], check=True, capture_output=True)
actual = json.loads(result.stdout.decode('utf-8'))
review = []
for old, current, request in zip(prior['files'], actual, requests, strict=True):
    expected = {str(line['line']): line['text'] for snippet in old['snippets'] for line in snippet['lines']}
    assert old['path'] == current['path']
    assert current['lines'] == expected, old['path']
    review.append({'path': old['path'], 'ranges': request['ranges'], 'selected_line_count': len(expected), 'all_selected_lines_equal_a43': True})
evidence = {'scope': 'Independent selected-source-line reread only; A43 package equality and ROM contracts inherited, not rerun', 'files': review, 'file_count': len(review), 'line_count': sum(f['selected_line_count'] for f in review), 'source_copies_retained': False}
(HERE / 'review-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('PASS:', evidence['file_count'], 'files;', evidence['line_count'], 'selected lines equal A43 retention')
