"""Bounded reuse check: no SIM execution, extraction, copies or hashes."""
from pathlib import Path
import json,zipfile
ROOT=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
ps=[ROOT/'reverse/reports/ap01/application-rehost-complete-0041-20261017.md',ROOT/'reverse/reports/ap01/application-function-matrix-0041.json',ROOT/'reverse/reports/ap01/factory-reference-map-0041-20261020.md',ROOT/'reverse/analysis/0041-20261013/0041-ghidra-pass3.txt']
ps+=list((ROOT/'reverse/rehost').glob('*complete-0041.json'))
for pattern in ['page-logic*.json','details-0041-round4.json','charge-0041-round4.json','*knob-0041-round2.json','photo-evidence-round3.json','settings-0041-round2*.json']:
 ps+=list((ROOT/'reverse/rehost').glob(pattern))
terms=['a001a8ee','a00288de','a00198bc','a01b5c48','a002c678','62fc6048','62fc603c','62fc5c4c','dma0_ch','dma_channel','DMA channel','UartComm','bflb_dma_channel_release','bflb_dma_channel_request']
def hits(text):
 return [{'line':i+1,'terms':[t for t in terms if t.lower() in line.lower()]} for i,line in enumerate(text.splitlines()) if any(t.lower() in line.lower() for t in terms)]
old={str(p.relative_to(ROOT)):hits(p.read_text(encoding='utf-8',errors='replace')) for p in ps}
recent={str(p.relative_to(ROOT)):hits(p.read_text(encoding='utf-8',errors='replace')) for p in (ROOT/'reverse/reports/ap01').glob('uart*.md')}
z=zipfile.ZipFile(ROOT/'reverse/rehost/ap01-ui-0041-complete-source.zip')
archive={n:hits(z.read(n).decode('utf-8',errors='replace')) for n in z.namelist() if not n.endswith('/')}
r={'limitation':'These literal/field alias searches are bounded discovery checks, not proof of never analyzed or missing implementation. Old pending/remaining does not override final SIM acceptance; SIM completion does not certify ROM DMA ABI.','terms':terms,'old_files':old,'recent_uart_reports':recent,'archive_members':archive}
(OUT/'reuse-check.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print('old files',len(old),'recent UART reports',len(recent),'ZIP text/members read',len(archive),'old hit files',sum(bool(v) for v in old.values()))
