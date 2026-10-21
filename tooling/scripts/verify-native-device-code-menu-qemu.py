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
firmware_code = '--firmware-code' in sys.argv
if firmware_code: sys.argv.remove('--firmware-code')
auth = '--device-code-auth' in sys.argv
if auth: sys.argv.remove('--device-code-auth')
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
                    if action.get('menu_child'):action['value']=regs[10]
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
                        elif action.get('menu_child'):
                            changes={1:timer_va,2:temporary,10:action['menu_child'],11:action['key'],32:0xa00dcee4}
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
                    elif action.get('menu_read_code'):
                        owner=int.from_bytes(bytes.fromhex(super().request(f"m{action['menu_read_code']+0x10:x},4")),'little')
                        action['value']=bytes.fromhex(super().request(f'm{owner+17:x},9')).rstrip(b'\\0').decode('ascii');action['done'].set()
                    elif action.get('menu_context_state'):
                        owner=int.from_bytes(bytes.fromhex(super().request(f"m{action['menu_context_state']+0x10:x},4")),'little')
                        action['value']=int.from_bytes(bytes.fromhex(super().request(f"m{owner+12:x},4")),'little');action['done'].set()
                    elif action.get('menu_object_flags'):
                        action['value']=int.from_bytes(bytes.fromhex(super().request(f"m{action['menu_object_flags']+0x24:x},4")),'little');action['done'].set()
                    elif action.get('menu_focus'):
                        def word(address):
                            return int.from_bytes(bytes.fromhex(super(NativeRSP,self).request(f'm{address:x},4')),'little')
                        group=word(0x62fc95bc);node=word(group+12)
                        action['value']=word(node) if node else 0;action['done'].set()
                    elif action.get('observe'):""")
replace('    def diagnostic_probe(self,token,identity):', '''    def device_code_probe(self,token,identity):
        import zlib
        credential=token
        def current_code(layout):
            row=self.action(menu_child=layout['list'],key=0,event='auth_readout')
            code=self.action(menu_read_code=row,event='auth_menu_code')
            assert len(code)==8 and code.isdigit(),'invalid menu code'
            return code
        def stored(required=True):
            body=json.dumps(dict(device_mac=identity,path='/data/ap01_ui.device_code',offset=0,length=64)).encode()
            status,value=self.http(self.port,'POST','/api/diagnostic/file',body,credential)
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
        before=None if DEVICE_CODE_AUTH else stored(False)
        if DEVICE_CODE_RESTART and not DEVICE_CODE_AUTH:
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
        parent_trace=[6]
        for value,expected in ((0x13,7),(0x13,0),(0x14,7),(0x14,6)):
            key(value);observed=bytes.fromhex(lookup(8)['state'])[1]-0x30
            assert observed==expected,('parent wrap',observed,expected)
            parent_trace.append(observed)
        key(10);lookup(3)
        layout=lookup(3);arrows=[]
        for index in range(3):
            row=self.action(menu_child=layout['list'],key=index,event='native_style_child')
            arrow=self.action(menu_child=row,key=1,event='native_style_arrow')
            assert arrow,'stock row structure changed'
            arrows.append(bool(self.action(menu_object_flags=arrow)&1))
        assert arrows==[True,True,False],('code/action chevrons',arrows)
        self.report['native_device_code_style']={'passed':True,'arrows_hidden':arrows,
            'number_font':'complete original 0xa055fb7c for both states'}
        if DEVICE_CODE_AUTH:
            credential=current_code(layout)
            status,_=self.http(self.port,'GET','/api/diagnostic/status',b'',token)
            assert status==401,'binding token authorized manual diagnostics'
            status,_=self.http(self.port,'GET','/api/diagnostic/status',b'','')
            assert status==401,'missing menu code accepted'
            status,_=self.http(self.port,'GET','/api/diagnostic/status',b'',credential)
            assert status==200,'current menu code rejected'
            status,value=self.http(self.port,'GET','/api/wifi/profiles',b'',credential)
            assert status==200,('manual Wi-Fi auth',status,value.get('error'))
            # Menu code must not replace firmware/Bridge credentials.
            status,_=self.http(self.port,'GET','/api/firmware/slots',b'',credential)
            assert status==(200 if DEVICE_CODE_FIRMWARE else 401),'menu code firmware policy'
            status,_=self.http(self.port,'GET','/api/maintenance/status',b'',token)
            assert status==200,'original maintenance credential rejected'
        first=stored()
        if DEVICE_CODE_AUTH and DEVICE_CODE_RESTART:
            previous=json.loads(resume_report.read_bytes())['native_device_code_menu']
            assert hashlib.sha256(first).hexdigest()==previous['record_sha256'],'restart rotated code'
        if before is not None:assert first==before,'opening rotated persisted code'
        capture('device-code-submenu')
        readout=self.action(menu_child=layout['list'],key=0,event='numeric_readout')
        trace=[self.action(menu_context_state=readout)]
        assert trace[0]==1,'initial focus must be regeneration'
        for value,expected in ((0x14,2),(0x14,1),(0x13,2),(0x13,1)):
            key(value);selected=self.action(menu_context_state=readout)
            assert selected==expected and selected!=0,('submenu wrap',selected,expected)
            assert stored()==first,'navigation changed code'
            trace.append(selected)
        self.report['native_device_code_navigation']={'passed':True,'parent_trace':parent_trace,
            'submenu_trace':trace,'numeric_row_never_selected':True}
        if not DEVICE_CODE_RESTART:
            key(10)
            if DEVICE_CODE_AUTH:
                old=credential;credential=current_code(lookup(3))
                status,_=self.http(self.port,'GET','/api/diagnostic/status',b'',old)
                assert status==401,'old code survived regeneration'
                status,_=self.http(self.port,'GET','/api/diagnostic/status',b'',credential)
                assert status==200,'regenerated code rejected'
            second=stored();assert second!=first,'explicit regenerate did not rotate'
            capture('device-code-regenerated')
        else:second=first
        key(0x13);capture('device-code-return');key(10);lookup(8)
        assert bytes.fromhex(lookup(8)['state'])[1]==0x36
        key(10);lookup(3);assert stored()==second,'reopening rotated code'
        key(0x13);key(10);lookup(8)
        key(0x13);key(10);time.sleep(.8)
        assert self.action(menu_focus=True)==native_ui_root,'original Return did not restore home focus'
        assert stored()==second
        key(10);lookup(8)
        for _ in range(6):key(0x13)
        key(10);lookup(3);assert stored()==second,'recreated native page rotated code'
        key(0x13);key(10);lookup(8);key(0x13);key(10)
        assert self.action(menu_focus=True)==native_ui_root
        self.nor_snapshot('device-code-persisted')
        if DEVICE_CODE_AUTH:
            self.report['native_device_code_auth']={'passed':True,
                'checks':['missing_code_rejected','binding_token_no_manual_access','menu_code_accepted',
                    'manual_wifi_accepted','menu_code_firmware_access' if DEVICE_CODE_FIRMWARE else 'menu_code_no_firmware_access','original_maintenance_accepted',
                    'restart_preserves_code' if DEVICE_CODE_RESTART else 'rotation_invalidates_old_code'],
                'credential_logged':False,'physical_verified':False}
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
     {'__name__':'__main__','__file__':str(runner),'DEVICE_CODE_RESTART':restart,'DEVICE_CODE_AUTH':auth,'DEVICE_CODE_FIRMWARE':firmware_code})
