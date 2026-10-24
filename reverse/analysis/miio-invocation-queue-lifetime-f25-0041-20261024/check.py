"""F25 local contract/reference consistency only; no ROM or old scripts."""
from pathlib import Path
import json
MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
c=json.loads((OUT/'contract.json').read_text(encoding='utf8'))
checks=[]
def check(label,ok):
    assert ok,label
    checks.append(label)
reports={
 'F12':'miio-request-ownership-review-f12-0041-20261024.md',
 'F14':'miio-native-queue-review-f14-0041-20261024.md',
 'F16':'miio-queue-size-review-f16-0041-20261024.md',
 'F18':'miio-queue-copy4-review-f18-0041-20261024.md',
 'F20':'miio-queue-receive-review-f20-0041-20261024.md',
 'F22':'miio-queue-message-source-review-f22-0041-20261024.md'
}
sources={k:(MAIN/'reverse/reports/ap01'/p).read_text(encoding='utf8') for k,p in reports.items()}
check('every effective review has a source report',set(c['effective_dependencies'])==set(sources))
for k,t in sources.items():check(k+' source records limited acceptance','限定接受' in t)
check('copy domain source preserves byte order and finite domain',
      'word对齐' in sources['F18'] and '逐byte' in sources['F18'] and '并非一次LW/SW' in sources['F18'])
check('receive source preserves actual length distinction',
      'U16(Msg+0x0a)' in sources['F20'] and '不能替换为Q.size4' in sources['F20'])
check('receive source has kind-based return boundary',
      'kind0/2' in sources['F20'] and 'kind1' in sources['F20'])
check('setup source preserves initialization/normal conditions',
      '初值' in sources['F16'] and 'matching-thread' in sources['F16'])
check('F23/F24 is pending, not an accepted effective dependency',
      c['pending_dependency']['review']=='F24 pending at synthesis'
      and 'F23' not in c['effective_dependencies'] and 'F24' not in c['effective_dependencies'])
f22c=json.loads((MAIN/'reverse/analysis/miio-queue-message-source-review-f22-0041-20261024/contract.json').read_text(encoding='utf8'))
check('frozen F22 guard is explicitly excluded as global premise',
      'caller_flag_condition' in f22c and 'caller_flag_condition' in c['pending_dependency']['excluded_from_accepted_premises'])
f18c=json.loads((MAIN/'reverse/analysis/miio-queue-copy4-review-f18-0041-20261024/contract.json').read_text(encoding='utf8'))
f19c=json.loads((MAIN/'reverse/analysis/miio-queue-receive-gap-f19-0041-20261024/contract.json').read_text(encoding='utf8'))
check('selected domains are grounded in existing contracts',f18c['claim']=='F11/5' and f19c['claim']=='F11/6')
check('local slots and heap objects have separate identities',
      all(k in c['objects'] for k in ['R','I','Msg','send_slot','receive_slot','receive_msg_slot']))
e=c['ordered_events'];check('event ids unique',len(e)==len(set(e)))
check('source borrow ends after copy and before queue publication',e.index('send_copy_return')<e.index('publish_Msg'))
check('internal Msg returned after payload copy and before I dispatch',
      e.index('receive_copy_return')<e.index('Msg_return_interface_or_pool_writes')<e.index('type1_dispatch'))
check('selected heap I cleanup follows normal executor return0',
      e.index('type1_dispatch')<e.index('executor_normal_return0')<e.index('I_return_interface'))
check('all required condition groups are retained',
      set(c['preconditions'])=={'send','relay','receive','dispatch'} and all(c['preconditions'].values()))
result=dict(status='PASS-semantic-reference-consistency-only',claim='F11/9',task='F25',checks=checks,
            sources={k:'reverse/reports/ap01/'+p for k,p in reports.items()},new_rom_bytes=0,
            prior_scripts_run=False,limitations=['References and contract invariants only; no firmware/runtime/semantic proof by execution',
                                               'F26 independent review pending; premises are not established runtime facts'])
(OUT/'check-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(status=result['status'],checks=len(checks),new_rom_bytes=0)))
