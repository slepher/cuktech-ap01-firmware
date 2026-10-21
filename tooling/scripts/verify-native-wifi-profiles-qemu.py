"""Run passive-profile checks in the native QEMU runner (WSL, no device).

Pass --runner PATH followed by the native runner's normal arguments, including
--lvgl-input-model. Only the original cache is seeded with synthetic credentials;
mutex, encrypted PSM, VFS and the HTTP application execute guest instructions.
"""
from pathlib import Path
import hashlib
import sys

i = sys.argv.index('--runner')
runner = Path(sys.argv[i + 1]).resolve()
del sys.argv[i:i + 2]
assert '--lvgl-input-model' in sys.argv, 'UI-thread gate required'
assert '--native-loopback' not in sys.argv, 'this probe requires the socket/MAC provider'
if '0xa005d180' not in sys.argv:
    sys.argv.extend(['--observe-pc','0xa005d180'])
source = runner.read_text(encoding='utf-8')

def replace(old, new):
    global source
    assert source.count(old) == 1, 'native runner version mismatch: ' + old[:60]
    source = source.replace(old, new)

replace("elif action.get('observe'):", """elif action.get('wifi_cache'):
                        mutex = super().request('m62fca9d8,4')
                        assert mutex != '00000000', 'original network mutex not initialized'
                        if action['wifi_cache'] == 'seed':
                            for address, data in ((0x62fca824,b'\\1'),
                                    (0x62fca831,b'QEMU-current'+bytes(21)),
                                    (0x62fca853,b'QEMU-original-pass'+bytes(47))):
                                super().request(f'M{address:x},{len(data):x}:'+data.hex())
                        action['value'] = [super().request(f'm{address:x},{length:x}')
                            for address,length in ((0x62fca824,1),(0x62fca831,33),(0x62fca853,65))]
                        action['done'].set()
                    elif action.get('observe'):""")
replace('    def diagnostic_probe(self,token,identity):', '''    def wifi_profiles_probe(self,token,identity):
        def call(method,body=None,status=200,credential=token,path='/api/wifi/profiles'):
            code,value=self.http(self.port,method,path,b'' if body is None else json.dumps(body).encode(),credential)
            assert code==status,(method,path,code,value)
            assert 'QEMU-original-pass' not in json.dumps(value)
            assert 'candidate-secret' not in json.dumps(value)
            return value
        def put(revision,rows,status=200):
            return call('PUT',dict(device_mac=identity,expected_revision=revision,profiles=rows),status)
        cache=self.action(wifi_cache='seed')
        call('GET',status=401,credential='!'*32)
        initial=call('GET');revision=initial['revision']
        assert initial['profiles']==[dict(ssid='QEMU-current',has_password=True,current=True,source='current')]
        saved=put(revision,[dict(ssid='QEMU-current'),dict(ssid='QEMU-current'),dict(ssid='QEMU-guest',password='')])
        assert saved['revision']==revision+1 and len(saved['profiles'])==2
        assert saved['profiles'][0]['source']=='saved' and saved['profiles'][0]['current']
        self.nor_snapshot('wifi-profiles-populated')
        put(revision,[],409)
        edited=put(revision+1,[dict(ssid='QEMU-current',password='candidate-secret')])
        assert len(edited['profiles'])==1 and edited['profiles'][0]['current']
        empty=put(revision+2,[])
        assert empty['profiles']==initial['profiles']
        assert call('GET')==empty
        call('POST',{},404,path='/api/wifi/activate')
        assert self.action(wifi_cache='read')==cache
        self.nor_snapshot('wifi-profiles-saved')
        self.report['native_wifi_profiles']={
            'passed':True,'initial_revision':revision,'final_revision':empty['revision'],
            'checks':['authenticated_route','original_mutex_snapshot','encrypted_PSM_save_readback',
                'current_uniq','duplicate_collapse','saved_password_edit_without_cache_change',
                'revision_conflict','empty_saved_list_keeps_current','no_activate_route'],
            'fixtures':['synthetic configured cache','loopback sockets and MAC','virtual peripherals'],
            'physical_network_verified':False}

    def diagnostic_probe(self,token,identity):''')
replace('        if diagnostic_probe:self.diagnostic_probe(token,identity)',
        "        self.wifi_profiles_probe(token,identity)\n        return")
replace("functional=report.get('native_firmware_protocol_passed') if firmware_only else report['native_application_smoke_passed']",
        "functional=report.get('native_wifi_profiles',{}).get('passed',False)")
replace("    report['native_runner_sha256']=NATIVE_RUNNER_SHA",
        "    report['wifi_verifier_sha256']=" + repr(hashlib.sha256(Path(__file__).read_bytes()).hexdigest()) +
        "\n    report['wifi_runner_variant_sha256']=" + repr(hashlib.sha256(source.encode()).hexdigest()) +
        "\n    report['native_runner_sha256']=NATIVE_RUNNER_SHA")
sys.argv[0] = str(runner)
exec(compile(source, str(runner), 'exec'), {'__name__':'__main__','__file__':str(runner)})
