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
                    if action.get('menu_font'):action['value']=regs[10]
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
                        elif action.get('menu_font'):
                            changes={1:timer_va,2:temporary,10:action['menu_font'],11:0,32:0xa0090560}
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
                    elif action.get('menu_label_mode'):
                        action['value']=int(super().request(f"m{action['menu_label_mode']+0x5c:x},1"),16)&15;action['done'].set()
                    elif action.get('menu_object_flags'):
                        action['value']=int.from_bytes(bytes.fromhex(super().request(f"m{action['menu_object_flags']+0x24:x},4")),'little');action['done'].set()
                    elif action.get('menu_focus'):
                        def word(address):
                            return int.from_bytes(bytes.fromhex(super(NativeRSP,self).request(f'm{address:x},4')),'little')
                        group=word(0x62fc95bc);node=word(group+12)
                        action['value']=word(node) if node else 0;action['done'].set()
                    elif action.get('observe'):""")

LOCAL_MENU_CODE=None
replace('    def application_probe(self,info):', '''    def device_code_probe(self,token,identity):
        global LOCAL_MENU_CODE
        def settle():
            until=time.monotonic()+25
            while time.monotonic()<until:
                if self.action(observe=True)['root_ready']:return
                time.sleep(.1)
            raise TimeoutError('native menu animation')
        def key(value):
            if value==10:self.action(group_event=1,event='wifi_press')
            self.action(group_key=value,event='wifi_key',key=value);time.sleep(.15)
            if value==10:self.action(group_event=0xb,event='wifi_release')
        def lookup(count):
            v=self.action(menu_lookup=True,event='wifi_lookup')
            self.report.setdefault('wifi_trace',[]).append(v)
            assert v['found']==1 and v['list'],('Settings not ready',v)
            actual=self.action(menu_count=v['list']);self.report.setdefault('wifi_counts',[]).append([count,actual])
            assert v['found']==1 and actual==count,('row count',count,actual,v)
            return v
        def capture(name):
            start=self.action(menu_tick=True);until=time.monotonic()+25
            while ((self.action(menu_tick=True)-start)&0xffffffff)<500:
                if time.monotonic()>until:raise TimeoutError('native frame settle')
                time.sleep(.05)
            self.action(menu_refresh_default=True,event='wifi_refresh');self.snapshot(name)
        def choose(index):
            for _ in range(9):
                if bytes.fromhex(lookup(9)['state'])[1]==0x30+index:return
                key(0x13)
            raise AssertionError('settings selection did not converge')
        def put(rows):
            status,v=self.http(self.port,'GET','/api/wifi/profiles',token=LOCAL_MENU_CODE);assert status==200
            body=json.dumps(dict(device_mac=identity,expected_revision=v['revision'],profiles=rows)).encode()
            status,v=self.http(self.port,'PUT','/api/wifi/profiles',body,LOCAL_MENU_CODE);assert status==200,(status,v)
            return v
        def fingerprints():
            result={}
            for path in ('/resource/codex-status/bindings.bin','/data/ap01_ui.device_code','/data/e#network.did','/data/e#network.uid','/data/e#network.token','/data/e#network.bind_key'):
                body=json.dumps(dict(device_mac=identity,path=path,offset=0,length=1024)).encode()
                status,value=self.http(self.port,'POST','/api/diagnostic/file',body,LOCAL_MENU_CODE)
                assert status in (200,404),('protected read',path,status,value.get('error'))
                if status==200:
                    assert value['eof'];result[path]=hashlib.sha256(bytes.fromhex(value['data_hex'])).hexdigest()
                else:result[path]=None
            return result
        def checks(count,expected):
            v=lookup(count+1);hidden=[];fonts=[]
            for i in range(count):
                row=self.action(menu_child=v['list'],key=i)
                label=self.action(menu_child=row,key=0)
                assert self.action(menu_label_mode=label)==4,'SSID must stay single-line'
                fonts.append(self.action(menu_font=label))
                mark=self.action(menu_child=row,key=1);assert mark
                hidden.append(bool(self.action(menu_object_flags=mark)&1))
            assert hidden==[i!=expected for i in range(count)],hidden
            assert len(set(fonts))<=1,('mixed SSID fonts',fonts)
            self.report.setdefault('wifi_fonts',[]).append(fonts)
        self.action(onboarded=True)
        self.action(native_page=6,direction=0,event='native_page');settle()
        key(10);lookup(9);capture('wifi-settings')
        choose(6)
        key(10);layout=lookup(3)
        row=self.action(menu_child=layout['list'],key=0)
        LOCAL_MENU_CODE=self.action(menu_read_code=row)
        assert len(LOCAL_MENU_CODE)==8 and LOCAL_MENU_CODE.isdigit()
        protected=fingerprints()
        key(0x13);key(10);lookup(9)
        choose(0)
        # Parent wrap with new Wi-Fi/device-code indices; real original input.
        key(0x14);assert bytes.fromhex(lookup(9)['state'])[1]==0x38
        key(0x13);assert bytes.fromhex(lookup(9)['state'])[1]==0x30
        self.action(wifi_cache='clear');put([])
        choose(7);key(10);lookup(1);capture('wifi-empty')
        key(0x14);lookup(1);key(10);assert bytes.fromhex(lookup(9)['state'])[1]==0x37,('expected Wi-Fi selection',lookup(9))
        self.action(wifi_cache='seed');put([])
        key(10);checks(1,0);capture('wifi-current-only')
        key(0x13);key(0x13);checks(1,0) # list wraps, mark stays independent.
        key(10);time.sleep(1);checks(1,0) # selecting current is a no-op.
        key(0x14);key(10);lookup(9)
        rows=[dict(ssid='QEMU-current'),dict(ssid='Lab-Guest',password='synthetic-test'),dict(ssid='0123456789ABCDEFGHIJKLMNOPQRSTUV',password='')]
        put(rows);key(10);checks(3,0);capture('wifi-saved-list')
        key(0x13);checks(3,0);capture('wifi-focus-other')
        for _ in range(2):key(0x13)
        key(10);lookup(9)
        put([dict(ssid=('设备-Y5' if i==3 else 'Saved-'+str(i)),password='synthetic-test') for i in range(8)])
        key(10);checks(9,8);capture('wifi-max-top')
        for _ in range(8):key(0x13)
        checks(9,8);capture('wifi-max-current')
        key(0x13);capture('wifi-max-return');key(0x13);checks(9,8)
        key(0x14);key(10);lookup(9)
        # Recovered stock states: brightness1d/3f -> right3d(Return),
        # Version1e starts43(Return) when original MCU updater returns0.
        choose(2);key(10);capture('wifi-stock-brightness')
        key(0x13);key(10);lookup(9)
        assert bytes.fromhex(lookup(9)['state'])[1]==0x32,'brightness return mapping'
        choose(3);key(10);capture('wifi-stock-version')
        key(10);lookup(9)
        assert bytes.fromhex(lookup(9)['state'])[1]==0x33,'version return mapping'
        # The adjacent stock screensaver still opens and returns correctly.
        choose(1);key(10);capture('wifi-stock-screensaver')
        # REA a00fd1ac: screensaver starts3b; right3c, right3a(Return).
        key(0x13);key(0x13);key(10);lookup(9)
        choose(6)
        key(10);lookup(3);capture('wifi-device-code-regression')
        key(0x13);key(10);assert bytes.fromhex(lookup(9)['state'])[1]==0x36
        choose(8);key(10);time.sleep(.7)
        assert self.action(menu_focus=True)==native_ui_root
        key(10);lookup(9)
        assert fingerprints()==protected,'identity/binding/menu-code changed'
        self.report['wifi_protected_files_sha256']=protected
        self.nor_snapshot('wifi-menu-verified')
        self.report['native_wifi_menu']={'passed':True,'checks':['stock_original_LVGL_input','nine_settings_rows','saved_SSID_names','empty_single_typical_max','current_stock_checkmark','focus_does_not_move_check','long_name_clipped','both_wrap_boundaries','paired_row_scroll','current_no_reconnect','stock_screensaver_return','stock_brightness_version_return','device_code_return','original_return_home','delete_recreate'],'preview_source':'original LVGL RGB565 buffers; virtual LCD screendump is not acceptance','radio_switch_verified':False,'physical_verified':False}
        self.report['native_device_code_menu']={'passed':True}

    def application_probe(self,info):''')
replace('        token,identity,principal=self.pair_binding(info)', '        token,identity,principal=self.pair_binding(info)\n        self.device_code_probe(token,identity)\n        return')
replace("functional=report.get('native_firmware_protocol_passed') if firmware_only else report['native_application_smoke_passed']","functional=report.get('native_wifi_menu',{}).get('passed',False)")
replace("elif action.get('observe'):","elif action.get('wifi_cache'):\n                        assert super().request('m62fca9d8,4')!='00000000'\n                        configured=action['wifi_cache']=='seed'\n                        for address,data in ((0x62fca824,bytes([int(configured)])),(0x62fca831,(b'QEMU-current'+bytes(21)) if configured else bytes(33)),(0x62fca853,(b'QEMU-original-pass'+bytes(47)) if configured else bytes(65))):\n                            super().request(f'M{address:x},{len(data):x}:'+data.hex())\n                        action['done'].set()\n                    elif action.get('observe'):")
source=source.replace("except Exception as error:self.report['native_application_error']=type(error).__name__+': '+str(error)","except Exception as error:\n                        import traceback;self.report['native_application_error']=traceback.format_exc()")

# Optional original-driver API fixture. Core, native adapter, encrypted PSM and
# VFS execute in the guest; this models radio replies only, never actual RF.
driver_model='--wifi-driver-model' in sys.argv
if driver_model:
    sys.argv.remove('--wifi-driver-model')
    replace("name in ('socket','wifi_mac','wall_epoch') or args6[0]",
            "name in ('socket','wifi_mac','wall_epoch','wifi_drv_stop','wifi_drv_cache','wifi_drv_start','wifi_drv_essid','wifi_drv_ip') or args6[0]")
    replace('base.builder_for=lambda path:', "profile['apis'].update({0xa00699c4:'wifi_drv_stop',0xa006bfdc:'wifi_drv_cache',0xa0068a7a:'wifi_drv_start',0xa00756c2:'wifi_drv_essid',0xa00c6ba0:'wifi_drv_ip'})\nbase.builder_for=lambda path:")
    replace('class NativeProvider(OriginalProvider):', "wifi_driver={'mode':'success','actual':b'QEMU-current','fail':False,'starts':0,'stops':0}\nclass NativeProvider(OriginalProvider):")
    replace("        if name=='wall_epoch':", """        if name.startswith('wifi_drv_'):
            if name=='wifi_drv_stop':wifi_driver['stops']+=1;return 0
            if name=='wifi_drv_cache':
                assert a2==1
                ssid=self.read(fd,33).split(bytes(1),1)[0];password=self.read(a1,65).split(bytes(1),1)[0]
                assert 1<=len(ssid)<=32 and len(password)<=64
                self.write(0x62fca824,bytes([1]));self.write(0x62fca831,ssid+bytes(33-len(ssid)));self.write(0x62fca853,password+bytes(65-len(password)));return 0
            if name=='wifi_drv_start':
                wifi_driver['starts']+=1
                if wifi_driver['fail']:wifi_driver['fail']=False;return -5
                wifi_driver['actual']=self.read(0x62fca831,33).split(bytes(1),1)[0];return 0
            assert fd in self.sockets and 0xa0000000<=a1<0xa0700000-6
            assert bytes.fromhex(self.rsp.request(f'm{a1:x},6'))==b'wlan0'+bytes(1)
            if name=='wifi_drv_essid':
                value=wifi_driver['actual'];self.write(a2,value+bytes(33-len(value)));self.write(a3,bytes([1]));return 0
            assert name=='wifi_drv_ip' and a2==0x701
            self.write(a3,struct.pack('<I',0 if wifi_driver['mode']=='hold' else 0x0100007f));return 0
        if name=='wall_epoch':""")
    replace("elif action.get('wifi_cache'):", """elif action.get('wifi_driver'):
                        command=action['wifi_driver']
                        if command in ('hold','success'):wifi_driver['mode']=command
                        elif command=='fail':wifi_driver['fail']=True
                        else:assert command=='status'
                        action['value']={k:v for k,v in wifi_driver.items() if k!='actual'};action['done'].set()
                    elif action.get('menu_phase'):
                        owner=int.from_bytes(bytes.fromhex(super().request(f"m{action['menu_phase']+16:x},4")),'little')
                        action['value']=int.from_bytes(bytes.fromhex(super().request(f'm{owner+40:x},4')),'little',signed=True);action['done'].set()
                    elif action.get('wifi_cache'):""")
    replace("        def put(rows):", """        def phase(expected):
            v=lookup(4);row=self.action(menu_child=v['list'],key=0);until=time.monotonic()+90
            while time.monotonic()<until:
                value=self.action(menu_phase=row)
                if value==expected:return
                time.sleep(.1)
            raise TimeoutError(('Wi-Fi state',expected,value))
        def put(rows):""")
    replace("        for _ in range(2):key(0x13)\n        key(10);lookup(9)", """        # Actual guest switch core/adapter and encrypted PSM, synthetic RF only.
        self.action(wifi_driver='hold');key(10);phase(2);checks(3,0);capture('wifi-connecting')
        key(10);phase(2) # duplicate request keeps original in flight.
        self.action(wifi_driver='success');phase(5);checks(3,1);capture('wifi-connected')
        status,saved=self.http(self.port,'GET','/api/wifi/profiles',token=LOCAL_MENU_CODE)
        assert status==200 and [x['ssid'] for x in saved['profiles'] if x['current']]==['Lab-Guest']
        key(0x14);self.action(wifi_driver='fail');key(10);phase(6);checks(3,1);capture('wifi-rollback')
        key(10);phase(5);checks(3,0)
        self.report['native_wifi_switch']={'passed':True,'success_after_actual_IP':True,'duplicate_kept_original':True,'driver_failure_restores_old':True,'real_guest_encrypted_PSM':True,'driver_fixture':True,'physical_RF':False,'calls':self.action(wifi_driver='status')}
        for _ in range(3):key(0x13)
        key(10);lookup(9)""")

# Restart uses the previous verified NOR, without reseeding network/cache/list.
if '--wifi-restart' in sys.argv:
    sys.argv.remove('--wifi-restart')
    replace("assert resume_report.parent.resolve()==(ROOT/'artifacts/ap01-platform-integration/device').resolve()",
            "assert resume_report.resolve().is_relative_to((ROOT/'artifacts').resolve())")
    # With saved credentials the original monitor retries empty scans. Model
    # a finite1s scan instead of20ms, keeping the original64-scan bound. This
    # is synthetic radio timing, not native association/timeout acceptance.
    replace('OriginalProvider=base.Provider', """OriginalScan=base.scan_mock.EmptyScan
class RestartScan(OriginalScan):
    def __init__(self,read,report):
        super().__init__(read,report);report['empty_scan']['latency_ms']=1000
    def handle(self,pc,args):
        current=self.transaction
        if pc==base.scan_mock.APIS[1] and current and current['fd']==args[0] and not current['consumed']:
            now=int.from_bytes(self.read(0x62fc6c64,4),'little')
            if ((now-current['started'])&0xffffffff)<1000:
                self.report['empty_scan']['pending']+=1;return 1
        return super().handle(pc,args)
base.scan_mock.EmptyScan=RestartScan
OriginalProvider=base.Provider""")
    replace("        key(10);lookup(9);capture('wifi-settings')", """        # Pairing on a fresh NOR had already allowed native UI startup to
        # settle. A resumed binding has no such delay: wait on guest ticks
        # before entering Settings so stock input's animation gate is open.
        started=self.action(menu_tick=True);until=time.monotonic()+60
        while ((self.action(menu_tick=True)-started)&0xffffffff)<2000:
            if time.monotonic()>until:raise TimeoutError('restart UI startup')
            time.sleep(.1)
        key(10);lookup(9);capture('wifi-settings')""")
    replace("        self.action(wifi_cache='clear');put([])", """        previous=json.loads(resume_report.read_bytes())
        assert fingerprints()==previous['wifi_protected_files_sha256'],'protected state changed across restart'
        # Maintenance may become ready before the stock network cache restores.
        until=time.monotonic()+30;polls=0
        while True:
            status,saved=self.http(self.port,'GET','/api/wifi/profiles',token=LOCAL_MENU_CODE);polls+=1
            assert status==200, ('restart profiles HTTP',status)
            if len(saved['profiles'])==9 and any(p['current'] and p['ssid']=='QEMU-current' for p in saved['profiles']):break
            if time.monotonic()>=until:raise TimeoutError(('restart profiles',[(p['ssid'],p['current']) for p in saved['profiles']]))
            time.sleep(.1)
        self.report['native_wifi_restart_ready_polls']=polls
        assert [p['ssid'] for p in saved['profiles'] if p['current']]==['QEMU-current']
        assert any(p['ssid']=='设备-Y5' for p in saved['profiles'])
        choose(7);key(10);checks(9,8);capture('wifi-restart-saved')
        for _ in range(3):key(0x13)
        capture('wifi-restart-utf8')
        key(0x14);key(0x14);key(0x14);key(0x14);key(10);lookup(9)
        self.report['wifi_protected_files_sha256']=fingerprints()
        self.report['native_wifi_restart']={'passed':True,'saved_names_UTF8':True,'current_checkmark':True,'binding_and_identity_unchanged':True,'menu_code_unchanged':True,'cache_not_seeded':True}
        self.report['native_wifi_menu']={'passed':True,'physical_verified':False}
        self.nor_snapshot('wifi-restart-verified')
        return
        self.action(wifi_cache='clear');put([])""")

if '--dump-variant' in sys.argv:
    Path(sys.argv[sys.argv.index('--output')+1]).with_suffix('.variant.py').write_text(source,encoding='utf-8');raise SystemExit(0)
sys.argv[0]=str(runner)
exec(compile(source,str(runner),'exec'),{'__name__':'__main__','__file__':str(runner),'LOCAL_MENU_CODE':LOCAL_MENU_CODE})
