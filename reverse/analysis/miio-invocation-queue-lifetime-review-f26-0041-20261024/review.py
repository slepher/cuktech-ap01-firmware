"""F26 contract-composition audit only. No ROM, decoder or old-script execution."""
import json
from pathlib import Path

MAIN=Path('D:/Documents/PlatformIO/Projects/cuktech-ap01-firmware')
OUT=Path(__file__).resolve().parent
checks=[];inputs=[]
def read(rel):
    p=MAIN/rel
    inputs.append(rel)
    return p.read_text(encoding='utf8')
def load(task):return json.loads(read('reverse/analysis/'+task+'/contract.json'))
def check(label,value):
    assert value,label
    checks.append(label)

c=load('miio-invocation-queue-lifetime-f25-0041-20261024')
q=load('miio-queue-size-gap-f15-0041-20261024')
copy=load('miio-queue-copy4-review-f18-0041-20261024')
send=load('miio-native-queue-f13-0041-20261024')
recv=load('miio-queue-receive-gap-f19-0041-20261024')
msg=load('miio-queue-message-source-review-f22-0041-20261024')
state=load('miio-queue-send-wait-review-f24-0041-20261024')
reports={}
for task,name in {
 'F12':'miio-request-ownership-review-f12-0041-20261024.md',
 'F14':'miio-native-queue-review-f14-0041-20261024.md',
 'F16':'miio-queue-size-review-f16-0041-20261024.md',
 'F18':'miio-queue-copy4-review-f18-0041-20261024.md',
 'F20':'miio-queue-receive-review-f20-0041-20261024.md',
 'F22':'miio-queue-message-source-review-f22-0041-20261024.md',
 'F24':'miio-queue-send-wait-review-f24-0041-20261024.md',
}.items():
    reports[task]=read('reverse/reports/ap01/'+name)
    check(task+' independent limited-acceptance source','限定接受' in reports[task])
check('same claim and fixed baseline',c['claim']=='F11/9' and c['baseline']=='bd457a6')
check('composition uses six accepted interfaces',set(c['effective_dependencies'])=={'F12','F14','F16','F18','F20','F22'})
check('same-M setup identities',q['identity']['L']=='M+0x128' and
      q['identity']['ctx0']=='user+0x8c = M+0x174' and q['identity']['ctx1']=='user+0x880 = M+0x968')
check('queue output slot arithmetic',0x128+0x18==0x140 and 'L+0x18' in q['identity']['queue_output_slot'])
check('size4 is initializer conclusion with later-writer limit',
      'initialized word at +0x18 is 4' in q['conditional_conclusion'] and
      any('later writes' in t for t in q['unknowns']))
check('F16 accepts same-state scope not all queues','Q+0x18初值=4' in reports['F16'] and '后续' in reports['F16'])
check('actual send source and n from Q',send['objects']['S']=='address of caller-local I pointer' and
      'word(Q+0x18)' in send['objects']['n'])
check('send copy call and publication are ordered',
      any('copy' in t and 'prior' not in t and 'incremented' in t for t in send['observed_connections']))
check('n4 copy is bounded not atomic/object copy',
      'n=4' in copy['domain'] and 'word-aligned' in copy['domain'] and
      'three byte' in ' '.join(copy['route']) and 'final ordinary LBU/SB' in ' '.join(copy['route']) and
      'deep-copy' in copy['direct_ownership'])
check('receive derives actual header length independently',
      recv['objects']['actual_len']=='U16(Msg+0x0a), not automatically word(Q+0x18)' and
      's0-0x34' in recv['objects']['outI'] and 's0-0x24' in recv['objects']['outMsg'])
check('pool and K queue not merged','distinct' in msg['list_helper']['identity_limits'])
check('kind-based return not all heapfree','kind0/2' in c['effects']['Msg_return'] and
      'kind1' in c['effects']['Msg_return'] and 'Physical heap release is not certified' in c['effects']['Msg_return'])
check('objects/three local slots separated in contract',set(c['objects'])==
      {'Manager','R','I','send_slot','Msg','receive_slot','receive_msg_slot'})
check('pointer value transfer explicitly not deep copying I/R',
      'neither I nor R is deep-copied' in c['effects']['send_payload'])
check('four premise groups preserved',set(c['preconditions'])=={'send','relay','receive','dispatch'})
pre=c['preconditions']
check('actual n4 and post-init writers remain premises',
      any('actual n at copy is 4' in t and 'later writes' in t for t in pre['send']))
check('same runtime Msg and header/payload stability remain premises',
      any('same runtime' in t for t in pre['relay']) and
      any('payload bytes and length have not been changed' in t for t in pre['relay']))
check('validity/domain/capacity/separation not inferred from logical objects',
      any('word-aligned' in t and 'capacity' in t for t in pre['send']) and
      any('different expressions alone are not proof' in t for t in pre['relay']) and
      any('capacity' in t for t in pre['receive']))
check('I ctx R user lifetime and selected worker0 remain premises',
      any('ctx/R/user' in t and 'return0' in t for t in pre['dispatch']) and
      any('return1' in t for t in pre['dispatch']))
check('slot expiry scoped to direct borrow/no other borrower',
      'no other borrower/alias' in c['effects']['send_slot_expiry'] and
      'does not permit I, R, user or ctx to expire' in c['effects']['send_slot_expiry'])
check('Msg reuse cannot alias-damage I/receive slot premise',
      any('cannot invalidate or alter I or receive_slot through aliases' in t for t in pre['receive']))
check('normal intermediate return/dispatch condition explicit',
      any('opaque intermediate services return' in t for t in pre['receive']) and
      any('valid I' in t for t in pre['dispatch']))
check('R lifetime separate from Msg/I cleanup','Returning Msg or I does not itself return R' in c['effects']['R_lifetime'])
events=c['ordered_events']
expected=['send_copy_return','publish_Msg','receive_this_Msg','receive_copy_return',
          'Msg_return_interface_or_pool_writes','consumer_reload_I','type1_dispatch',
          'executor_normal_return0','I_return_interface']
check('conditional partial order preserves publication/Msg/I boundaries',events==expected)
check('F22 old global caller guard excluded',
      'caller_flag_condition' in c['pending_dependency']['excluded_from_accepted_premises'] and
      not any('flag' in t.lower() for group in pre.values() for t in group))
check('F24 accepted expanded caller coverage',state['review']=='F24' and
      all(t in state['prior_caller_scope_correction'] for t in ['7af0','7afc','Stable flag0']))
check('F24 state ordering correction remains external',
      '1972 loads T+c' in state['pseudocode_order_refinement'] and
      not any('T+' in t for group in pre.values() for t in group))
check('new actual delivery/storage proof not claimed',
      any('same runtime Msg' in t for t in c['not_established']) and
      any('valid storage' in t for t in c['not_established']))

decision=dict(schema='ap01.conditional-lifetime-review.v1',claim='F11/9',review='F26',baseline='bd457a6',
 decision='limited acceptance of F25 conditional composition',new_business=0,semantic_corrections=0,
 accepted_source='reverse/analysis/miio-invocation-queue-lifetime-f25-0041-20261024/contract.json',
 accepted_effects=['queue transfers four pointer-value bytes; no I/R deep copy',
  'direct native source-slot borrow ends at send copy return only under explicit no-other-borrow/domain assumptions',
  'receive uses actual Msg U16 length, with runtime-identity/length4/stability premises retained',
  'Msg kind-based return precedes consumer reload/dispatch and selected worker0 I interface',
  'R/request-message/session lifetimes remain their separate F11/F12 contracts'],
 actual_state_update=dict(F24='independently accepted core with caller-scope correction and pseudocode ordering refinement',
  source='reverse/analysis/miio-queue-send-wait-review-f24-0041-20261024/contract.json',
  handling='F25 pending-F24 is historical; old F22 caller_flag_condition excluded, no state-service execution premise added'),
 limits=c['not_established'],new_ROM_bytes=0,new_helper_bodies=0,new_execution=False)
(OUT/'contract.json').write_text(json.dumps(decision,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(OUT/'review-result.json').write_text(json.dumps(dict(status='PASS-contract-composition-only',
 review='F26',checks=checks,inputs=inputs,ordered_events=events,decision=decision,
 limits=['Text/contract consistency supports manual scope review, not new execution/ABI/storage proof',
         'No F25 check.py, old technical scripts, ROM/decoder/helper/model run']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(f'PASS {len(checks)} independent reference/contract invariants; no ROM or execution')
