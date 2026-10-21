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

LOCAL_MENU_CODE=None
replace('    def diagnostic_probe(self,token,identity):',"    def device_code_probe(self,token,identity):\n        global LOCAL_MENU_CODE\n        def settle():\n            until=time.monotonic()+25\n            while time.monotonic()<until:\n                if self.action(observe=True)['root_ready']:return\n                time.sleep(.1)\n            raise TimeoutError('native menu animation')\n        def key(value):\n            if value==10:self.action(group_event=1,event='wifi_press')\n            self.action(group_key=value,event='wifi_key',key=value);time.sleep(.15)\n            if value==10:self.action(group_event=0xb,event='wifi_release')\n        def lookup(count):\n            v=self.action(menu_lookup=True,event='wifi_lookup')\n            self.report.setdefault('wifi_trace',[]).append(v)\n            actual=self.action(menu_count=v['list']);self.report.setdefault('wifi_counts',[]).append([count,actual])\n            assert v['found']==1 and actual==count,('row count',count,actual,v)\n            return v\n        def capture(name):\n            start=self.action(menu_tick=True);until=time.monotonic()+25\n            while ((self.action(menu_tick=True)-start)&0xffffffff)<500:\n                if time.monotonic()>until:raise TimeoutError('native frame settle')\n                time.sleep(.05)\n            self.action(menu_refresh_default=True,event='wifi_refresh');self.snapshot(name)\n        def put(rows):\n            status,v=self.http(self.port,'GET','/api/wifi/profiles',token=LOCAL_MENU_CODE);assert status==200\n            body=json.dumps(dict(device_mac=identity,expected_revision=v['revision'],profiles=rows)).encode()\n            status,v=self.http(self.port,'PUT','/api/wifi/profiles',body,LOCAL_MENU_CODE);assert status==200,(status,v)\n            return v\n        def checks(count,expected):\n            v=lookup(count+1);hidden=[]\n            for i in range(count):\n                row=self.action(menu_child=v['list'],key=i)\n                mark=self.action(menu_child=row,key=1);assert mark\n                hidden.append(bool(self.action(menu_object_flags=mark)&1))\n            assert hidden==[i!=expected for i in range(count)],hidden\n        self.action(onboarded=True)\n        self.action(native_page=6,direction=0,event='native_page');settle()\n        key(10);lookup(9);capture('wifi-settings')\n        for _ in range(7):key(0x13)\n        key(10);layout=lookup(3)\n        row=self.action(menu_child=layout['list'],key=0)\n        LOCAL_MENU_CODE=self.action(menu_read_code=row)\n        assert len(LOCAL_MENU_CODE)==8 and LOCAL_MENU_CODE.isdigit()\n        key(0x13);key(10);lookup(9)\n        key(0x13);key(0x13)\n        # Parent wrap with new Wi-Fi/device-code indices; real original input.\n        key(0x14);assert bytes.fromhex(lookup(9)['state'])[1]==0x38\n        key(0x13);assert bytes.fromhex(lookup(9)['state'])[1]==0x30\n        self.action(wifi_cache='clear');put([])\n        key(0x13);key(0x13);key(10);lookup(1);capture('wifi-empty')\n        key(0x14);lookup(1);key(10);assert bytes.fromhex(lookup(9)['state'])[1]==0x32\n        self.action(wifi_cache='seed');put([])\n        key(10);checks(1,0);capture('wifi-current-only')\n        key(0x13);key(0x13);checks(1,0) # list wraps, mark stays independent.\n        key(10);time.sleep(1);checks(1,0) # selecting current is a no-op.\n        key(0x14);key(10);lookup(9)\n        rows=[dict(ssid='QEMU-current'),dict(ssid='Lab-Guest',password='synthetic-test'),dict(ssid='0123456789ABCDEFGHIJKLMNOPQRSTUV',password='')]\n        put(rows);key(10);checks(3,0);capture('wifi-saved-list')\n        key(0x13);checks(3,0);capture('wifi-focus-other')\n        for _ in range(2):key(0x13)\n        key(10);lookup(9)\n        put([dict(ssid='Saved-'+str(i),password='synthetic-test') for i in range(8)])\n        key(10);checks(9,8);capture('wifi-max-top')\n        for _ in range(8):key(0x13)\n        checks(9,8);capture('wifi-max-current')\n        key(0x13);capture('wifi-max-return');key(0x13);checks(9,8)\n        key(0x14);key(10);lookup(9)\n        # The adjacent stock screensaver still opens and returns correctly.\n        key(0x14);key(10);capture('wifi-stock-screensaver')\n        key(0x14);key(10);lookup(9)\n        key(0x13);assert bytes.fromhex(lookup(9)['state'])[1]==0x32\n        for _ in range(5):key(0x13)\n        key(10);lookup(3);capture('wifi-device-code-regression')\n        key(0x13);key(10);assert bytes.fromhex(lookup(9)['state'])[1]==0x37\n        key(0x13);key(10);time.sleep(.7)\n        assert self.action(menu_focus=True)==native_ui_root\n        key(10);lookup(9)\n        self.nor_snapshot('wifi-menu-verified')\n        self.report['native_wifi_menu']={'passed':True,'checks':['stock_original_LVGL_input','nine_settings_rows','saved_SSID_names','empty_single_typical_max','current_stock_checkmark','focus_does_not_move_check','long_name_clipped','both_wrap_boundaries','paired_row_scroll','current_no_reconnect','stock_screensaver_return','device_code_return','original_return_home','delete_recreate'],'radio_switch_verified':False,'physical_verified':False}\n        self.report['native_device_code_menu']={'passed':True}\n\n    def diagnostic_probe(self,token,identity):")
replace('        if diagnostic_probe:self.diagnostic_probe(token,identity)','        self.device_code_probe(token,identity)\n        return')
replace("functional=report.get('native_firmware_protocol_passed') if firmware_only else report['native_application_smoke_passed']","functional=report.get('native_wifi_menu',{}).get('passed',False)")
replace("elif action.get('observe'):","elif action.get('wifi_cache'):\n                        assert super().request('m62fca9d8,4')!='00000000'\n                        configured=action['wifi_cache']=='seed'\n                        for address,data in ((0x62fca824,bytes([int(configured)])),(0x62fca831,(b'QEMU-current'+bytes(21)) if configured else bytes(33)),(0x62fca853,(b'QEMU-original-pass'+bytes(47)) if configured else bytes(65))):\n                            super().request(f'M{address:x},{len(data):x}:'+data.hex())\n                        action['done'].set()\n                    elif action.get('observe'):")
source=source.replace("except Exception as error:self.report['native_application_error']=type(error).__name__+': '+str(error)","except Exception as error:\n                        import traceback;self.report['native_application_error']=traceback.format_exc()")
if '--dump-variant' in sys.argv:
    Path(sys.argv[sys.argv.index('--output')+1]).with_suffix('.variant.py').write_text(source,encoding='utf-8');raise SystemExit(0)
sys.argv[0]=str(runner)
exec(compile(source,str(runner),'exec'),{'__name__':'__main__','__file__':str(runner),'LOCAL_MENU_CODE':LOCAL_MENU_CODE})
