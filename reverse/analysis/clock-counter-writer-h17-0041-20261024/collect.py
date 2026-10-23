"""Bounded retained-reference survey; no ROM sweep or target execution."""
import json
import subprocess
from pathlib import Path

MAIN = Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
HERE = Path(__file__).resolve().parent
EVIDENCE = MAIN / 'evidence/rea-0041-20261017/evidence'
query = '62fc6c64|g_system_ticks|clock_timer|clock_systimer|clock_initialize'
surveys = []
for rel in ['evidence/rea-0041-20261017/evidence',
            'evidence/rea-0041-20261017/round3/evidence', 'reverse/rehost']:
    p = subprocess.run(['rg', '-l', '-i', query, str(MAIN/rel), '-g', '*.json',
                        '-g', '!*.evidence.json'], capture_output=True)
    assert p.returncode in [0, 1], p.stderr
    surveys.append({'root': str(MAIN/rel), 'query': query,
                    'excluded': '*.evidence.json (selected complete bundle checked separately)',
                    'matching_files': p.stdout.decode().splitlines(), 'exit_code': p.returncode})

# Named source-xref/global-ref artifacts are not supplied at these locations.
inventory_roots = [MAIN/'reverse', MAIN/'evidence/rea-0041-20261017/evidence',
                   MAIN/'evidence/rea-0041-20261017/round3/evidence']
p = subprocess.run(['rg', '--files', '--hidden', '--no-ignore',
                    *map(str, inventory_roots)], capture_output=True)
assert p.returncode == 0
named_refs = [s for s in p.stdout.decode().splitlines()
              if any(t in Path(s).name.lower().replace('_', '-').replace('.', '-')
                     for t in ['source-xref', 'global-ref', 'globalref'])]

bundle_path = EVIDENCE/'upper-complete.evidence.json'
bundle = json.loads(bundle_path.read_text(encoding='utf-8'))
hits = []
for index, record in enumerate(bundle['records']):
    z = record.get('normalized_result', {})
    text = json.dumps(z).lower()
    if not any(t in text for t in ['62fc6c64', 'g_system_ticks', 'clock_timer', 'clock_systimer', 'clock_initialize']):
        continue
    refs = [{'source_address': x.get('source_address'), 'target_address': x.get('target_address'),
             'kind': x.get('kind')} for x in z.get('outgoing_references', [])
            if x.get('target_address') == '0x62fc6c64']
    hits.append({'record_index': index, 'evidence_id': record['evidence_id'],
                 'operation': record['operation'], 'parameters': record.get('parameters'),
                 'references': refs,
                 'note': 'native_value_flow output.location is not a memory STORE/write reference'})
assert len(hits) == 1
assert hits[0]['parameters']['procedure'] == '0xa00992d2'
assert len(hits[0]['references']) == 4
assert all(x['kind']['read'] and not x['kind']['write'] for x in hits[0]['references'])

remote = '''import json
from pathlib import Path
root=Path('/home/slepher/nuttx-ap01-sim/nuttx')
out=[]
for rel in ['sched/clock/clock_timer.c','sched/clock/clock_systimer.c','sched/clock/clock_initialize.c']:
 p=root/rel
 if not p.exists():
  out.append({'path':str(p),'exists':False}); continue
 lines=p.read_text().splitlines()
 seeds=[i for i,line in enumerate(lines) if 'g_system_ticks' in line or 'clock_timer(' in line or 'clock_systimer(' in line]
 keep=set()
 for i in seeds: keep.update(range(max(0,i-5),min(len(lines),i+7)))
 out.append({'path':str(p),'exists':True,'seed_lines':[i+1 for i in seeds],
             'lines':[{'line':i+1,'text':lines[i]} for i in sorted(keep)]})
print(json.dumps(out))
'''
p = subprocess.run(['wsl.exe', '-d', 'Ubuntu-24.04', '--exec', 'python3', '-c', remote],
                   capture_output=True)
candidate = json.loads(p.stdout) if p.returncode == 0 else {
    'status':'local candidate read unavailable', 'returncode':p.returncode,
    'stdout_utf8':p.stdout.decode(errors='replace'),
    'stderr_utf8':p.stderr.decode(errors='replace'),
    'limitation':'No candidate content obtained; inherited H15 excerpts remain reference only'}
(HERE/'candidate-excerpts.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result = {'scope': 'H17 bounded counter writer discovery; offset address not queried',
          'surveys': surveys, 'named_ref_inventory': {'roots':list(map(str,inventory_roots)),
                                                      'matching_artifacts':named_refs},
          'selected_complete_bundle':{'path':str(bundle_path),'records':len(bundle['records']),
                                     'hits':hits},
          'writer_seed_found':False, 'new_business_functions':0,
          'limits':['text references do not cover computed addresses or unretained functions',
                    'candidate g_system_ticks has no ROM binding',
                    'no full-ROM byte/field scan, IRQ survey, disassembly export or shared target'],
          'checks':'4 retained references are READ=true, WRITE=false',
          'candidate_read_succeeded':p.returncode == 0}
(HERE/'review-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'retained_counter_records':len(hits),'counter_read_refs':4,
                  'writer_seed_found':False,'candidate_read_succeeded':p.returncode == 0}))
