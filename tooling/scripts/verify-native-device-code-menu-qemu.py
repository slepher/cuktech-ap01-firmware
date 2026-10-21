"""Exercise the original 0041 menu via its real LVGL focus group (WSL only).

This wraps the pinned native runner. It never calls the added menu handler
directly. All input enters original lv_group_send_data; storage uses guest VFS.
"""
from pathlib import Path
import hashlib
import sys

i = sys.argv.index('--runner')
runner = Path(sys.argv[i + 1]).resolve()
del sys.argv[i:i + 2]
restart = '--device-code-restart' in sys.argv
if restart:
    sys.argv.remove('--device-code-restart')
source = runner.read_text(encoding='utf-8')
assert '--lvgl-input-model' in sys.argv and '--safety-seconds' in sys.argv
assert '--native-loopback' not in sys.argv

def replace(old, new):
    global source
    assert source.count(old) == 1, 'native runner version mismatch: ' + old[:70]
    source = source.replace(old, new)

replace("                    if action.get('wall_time'):action['value']=regs[10]", """                    if action.get('wall_time'):action['value']=regs[10]
                    if action.get('menu_count'):action['value']=regs[10]
                    if action.get('menu_lookup'):
                        def word(address):
                            return int.from_bytes(bytes.fromhex(super(NativeRSP,self).request(f'm{address:x},4')),'little')
                        page=word(action['lookup_output']);data=word(action['lookup_output']+4)
                        window=action['lookup_window']
                        state=word(window+16)
                        action['value']={'found':regs[10], 'window':window,'page':page,'data':data,
                            'list':word(data+8) if data else 0,
                            'state':super().request(f'm{state:x},8') if state else ''}
""")
replace("                        elif action.get('native_page') is not None:", """                        elif action.get('group_key') is not None:
                            group=int.from_bytes(bytes.fromhex(super().request('m62fc95bc,4')),'little')
                            assert group,'native focus group missing'
                            changes={1:timer_va,2:temporary,10:group,11:action['group_key'],32:0xa01ad906}
                        elif action.get('menu_lookup'):
                            def word(address):
                                return int.from_bytes(bytes.fromhex(super(NativeRSP,self).request(f'm{address:x},4')),'little')
                            group=word(0x62fc95bc);node=word(group+12);window=word(node)
                            assert window!=native_ui_root,'Settings did not take native focus'
                            action['lookup_output']=param;action['lookup_window']=window
                            super().request(f'M{param:x},8:'+bytes(8).hex())
                            changes={1:timer_va,2:temporary,10:window,11:26,12:param,13:param+4,32:0xa00a72ae}
                        elif action.get('group_event'):
                            def word(address):
                                return int.from_bytes(bytes.fromhex(super(NativeRSP,self).request(f'm{address:x},4')),'little')
                            group=word(0x62fc95bc);node=word(group+12);focused=word(node)
                            changes={1:timer_va,2:temporary,10:focused,11:action['group_event'],12:0,32:send_event_va}
                        elif action.get('menu_count'):
                            changes={1:timer_va,2:temporary,10:action['menu_count'],32:0xa00dd144}
                        elif action.get('menu_refresh_default'):
                            # Original fbdev callback invokes this same native
                            # default-display refresh with a null timer. Only
                            # the virtual POLLOUT gate is bypassed, no pixels
                            # or LVGL objects are supplied by the host.
                            changes={1:timer_va,2:temporary,10:0,32:0xa00e0ac8}
                        elif action.get('native_page') is not None:""")
replace("                    elif action.get('observe'):", """                    elif action.get('menu_tick'):
                        action['value']=int.from_bytes(bytes.fromhex(super().request(f"m{profile['tick']:x},4")),'little');action['done'].set()
                    elif action.get('menu_focus'):
                        def word(address):
                            return int.from_bytes(bytes.fromhex(super(NativeRSP,self).request(f'm{address:x},4')),'little')
                        group=word(0x62fc95bc);node=word(group+12)
                        action['value']=word(node) if node else 0;action['done'].set()
                    elif action.get('observe'):""")
replace('    def diagnostic_probe(self,token,identity):', '''    def device_code_probe(self,token,identity):
        import zlib
        def stored(required=True):
            body=json.dumps(dict(device_mac=identity,path='/data/ap01_ui.device_code',offset=0,length=64)).encode()
            status,value=self.http(self.port,'POST','/api/diagnostic/file',body,token)
            if not required and status!=200:return None
            assert status==200,('device-code file',status,value.get('error'))
            raw=bytes.fromhex(value['data_hex'])
            assert len(raw)==16 and raw[:4]==b'DVC1' and raw[4:12].isdigit()
            assert zlib.crc32(raw[:12])==int.from_bytes(raw[12:],'little')
            return raw
        def settle():
            until=time.monotonic()+25
            while time.monotonic()<until:
                state=self.action(observe=True)
                if state['root_ready']:return state
                time.sleep(.1)
            raise TimeoutError('original menu animation')
        def key(value):
            self.report.setdefault('device_code_keys',[]).append(value)
            if value==10:self.action(group_event=1,event='native_group_press')
            self.action(group_key=value,event='native_group_key',key=value);time.sleep(.15)
            if value==10:self.action(group_event=0xb,event='native_group_release')
        def capture(name):
            start=self.action(menu_tick=True);deadline=time.monotonic()+20
            while ((self.action(menu_tick=True)-start)&0xffffffff)<500:
                if time.monotonic()>deadline:raise TimeoutError('menu animation/frame settle')
                time.sleep(.05)
            self.action(menu_refresh_default=True,event='native_refresh_default')
            self.snapshot(name)
        def lookup(count):
            self.report['device_code_lookup_expected']=count
            value=self.action(menu_lookup=True,event='native_menu_lookup')
            self.report.setdefault('device_code_menu_trace',[]).append(value)
            assert value['found']==1 and value['list'],value
            assert self.action(menu_count=value['list'],event='native_child_count')==count,value
            return value
        before=stored(False)
        if DEVICE_CODE_RESTART:
            previous=json.loads(resume_report.read_bytes())['native_device_code_menu']
            assert before is not None and hashlib.sha256(before).hexdigest()==previous['record_sha256'], 'restart lost saved code'
        self.action(onboarded=True)
        self.action(native_page=6,direction=0,event='native_page');settle()
        self.report['device_code_stage']='open_settings'
        key(10);time.sleep(.8)
        self.report['device_code_stage']='lookup_settings'
        lookup(8);capture('stock-settings')
        for _ in range(6):key(0x13)
        assert bytes.fromhex(lookup(8)['state'])[1]==0x36
        capture('device-code-entry')
        key(10);lookup(3)
        first=stored()
        if before is not None:assert first==before,'opening rotated persisted code'
        capture('device-code-submenu')
        key(10);assert stored()==first,'read-only row wrote a code'
        key(0x13)
        if not DEVICE_CODE_RESTART:
            key(10);second=stored();assert second!=first,'explicit regenerate did not rotate'
            capture('device-code-regenerated')
        else:second=first
        key(0x13);capture('device-code-return');key(10);lookup(8)
        assert bytes.fromhex(lookup(8)['state'])[1]==0x36
        key(10);lookup(3);assert stored()==second,'reopening rotated code'
        key(0x13);key(0x13);key(10);lookup(8)
        key(0x13);key(10);time.sleep(.8)
        assert self.action(menu_focus=True)==native_ui_root,'original Return did not restore home focus'
        assert stored()==second
        key(10);lookup(8)
        for _ in range(6):key(0x13)
        key(10);lookup(3);assert stored()==second,'recreated native page rotated code'
        key(0x13);key(0x13);key(10);lookup(8);key(0x13);key(10)
        assert self.action(menu_focus=True)==native_ui_root
        self.nor_snapshot('device-code-persisted')
        self.report['native_device_code_menu']={'passed':True,
            'restart_recovered':DEVICE_CODE_RESTART,'previous_file_present':before is not None,
            'record_sha256':hashlib.sha256(second).hexdigest(),
            'checks':['original_focus_group_input','eight_original_settings_rows',
                'three_native_submenu_rows','eight_decimal_digits','crc_valid',
                'opening_and_navigation_preserve_code','read_only_first_row',
                'explicit_regeneration' if not DEVICE_CODE_RESTART else 'restart_preserves_code',
                'return_to_parent','original_return_to_home','press_key_release_click',
                'delete_and_recreate_native_page'],
            'fixtures':['synthetic binding','virtual peripherals',
                'original default-display refresh callback bypasses virtual POLLOUT gate'],
            'physical_verified':False}

    def diagnostic_probe(self,token,identity):''')
replace('        if diagnostic_probe:self.diagnostic_probe(token,identity)',
        '        self.device_code_probe(token,identity)\n        return')
replace("functional=report.get('native_firmware_protocol_passed') if firmware_only else report['native_application_smoke_passed']",
        "functional=report.get('native_device_code_menu',{}).get('passed',False)")
replace("    report['native_runner_sha256']=NATIVE_RUNNER_SHA",
        "    report['device_code_verifier_sha256']=" + repr(hashlib.sha256(Path(__file__).read_bytes()).hexdigest()) +
        "\n    report['device_code_runner_variant_sha256']=" + repr(hashlib.sha256(source.encode()).hexdigest()) +
        "\n    report['native_runner_sha256']=NATIVE_RUNNER_SHA")
sys.argv[0] = str(runner)
exec(compile(source, str(runner), 'exec'),
     {'__name__':'__main__','__file__':str(runner),'DEVICE_CODE_RESTART':restart})
