"""Verify actual application OTA/switch with a persisted menu-generated code.

The synthetic NOR keeps stock UI/data but has a clean application filesystem.
No pairing, claim or business configuration is performed. Only the current
committed DVC1 record identified by a prior native-menu report is used.
"""
from pathlib import Path
import hashlib,json,struct,sys,zlib

def take(name):
    i=sys.argv.index(name);value=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2];return value
runner=take('--runner');record_report=take('--menu-record-report')
switch_only='--manual-switch-only' in sys.argv
if switch_only:sys.argv.remove('--manual-switch-only')
assert '--unconfigured-slots' in sys.argv
assert ('--slot-probe' in sys.argv) if switch_only else ('--firmware-probe' in sys.argv)
nor=Path(sys.argv[sys.argv.index('--flash-fixture')+1]).read_bytes()
expected=json.loads(record_report.read_bytes())['native_device_code_menu']['record_sha256']
records=set();at=0
while (at:=nor.find(b'DVC1',at))>=0:
    raw=nor[at:at+16];at+=4
    if len(raw)==16 and hashlib.sha256(raw).hexdigest()==expected and zlib.crc32(raw[:12])==int.from_bytes(raw[12:],'little'):
        records.add(raw)
assert len(records)==1,'one exact persisted native-menu record is required'
code=records.pop()[4:12].decode('ascii');assert len(code)==8 and code.isdigit()
source=runner.read_text(encoding='utf-8')
def replace(old,new):
    global source
    assert source.count(old)==1,old[:80]
    source=source.replace(old,new)
replace("        token=secrets.token_hex(16);identity=info['device_mac'];principal='native-qemu-bridge';pair_id='native-pair'", """        assert info['binding_count']==0,'fixture is not unbound'
        status,value=self.http(self.port,'GET','/health',token=LOCAL_MENU_CODE)
        assert status==200 and value['device_mac']==info['device_mac'],'current code rejected'
        self.report['native_unbound_before']=True
        return LOCAL_MENU_CODE,info['device_mac'],'ap01-menu-maintenance'
        token=secrets.token_hex(16);identity=info['device_mac'];principal='native-qemu-bridge';pair_id='native-pair'""")
action='self.slot_probe(token,identity)' if switch_only else 'self.firmware_probe(token,identity,unbound_frame)'
replace('        token,identity,principal=self.pair_binding(info)\n',f'''        token,identity,principal=self.pair_binding(info)
        def unbound_frame(op,path,payload,claim=False,expected_status=200):
            body=json.dumps(payload).encode()
            raw=struct.pack('>BBHHH',0xc2,0,op,0,len(body))+secrets.token_bytes(16)+struct.pack('>Q',1)+bytes(16)+body
            status,value=self.http(self.port+1,'POST',path,raw,'!'*32,True,claim)
            assert status==expected_status,('unbound business admission',status)
            return json.loads(value)
        {action}
        status,info=self.http(self.port,'GET','/api/pairing/info')
        assert status==200 and info['binding_count']==0,'maintenance created a binding'
        self.report['native_menu_maintenance']={{'passed':True,'operation':MENU_OPERATION,
            'binding_count_before':0,'binding_count_after':0,'credential_source':'persisted actual native-menu record',
            'record_sha256':MENU_RECORD_SHA,'physical_verified':False}}
        self.report['native_application_stage']='complete'
        return
''')
replace("functional=report.get('native_firmware_protocol_passed') if firmware_only else report['native_application_smoke_passed']",
        "functional=report.get("+repr("native_slot_switch_passed" if switch_only else "native_firmware_protocol_passed")+")")
replace("    report['native_runner_sha256']=NATIVE_RUNNER_SHA",
        "    report['menu_ota_verifier_sha256']="+repr(hashlib.sha256(Path(__file__).read_bytes()).hexdigest())+"\n    report['native_runner_sha256']=NATIVE_RUNNER_SHA")
sys.argv[0]=str(runner)
exec(compile(source,str(runner),'exec'),{'__name__':'__main__','__file__':str(runner),
    'LOCAL_MENU_CODE':code,'MENU_RECORD_SHA':expected,'MENU_OPERATION':'switch' if switch_only else 'ota'})
