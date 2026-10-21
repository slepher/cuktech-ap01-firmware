"""Run the original native firmware/slot probes without a Bundle fixture.

The menu-only bootstrap report contains binding state, not business receipts.
Recovery must remain independent of a configured or restorable business app.
"""
from pathlib import Path
import sys
i=sys.argv.index('--runner');runner=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
switch_only='--manual-switch-only' in sys.argv
if switch_only:
    sys.argv.remove('--manual-switch-only')
    assert '--slot-probe' in sys.argv
else:
    assert '--firmware-probe' in sys.argv and '--firmware-only' in sys.argv
assert '--unconfigured-slots' in sys.argv
source=runner.read_text(encoding='utf-8')
anchor="        frame(4,'/claim',{'bridge_id':principal,'device_mac':identity},True)\n"
assert source.count(anchor)==1
action='self.slot_probe(token,identity)' if switch_only else 'self.firmware_probe(token,identity,frame)'
source=source.replace(anchor,anchor+f'''        if True:
            {action}
            self.report['native_application_stage']='complete'
            return
''')
if switch_only:
    old="functional=report.get('native_firmware_protocol_passed') if firmware_only else report['native_application_smoke_passed']"
    assert source.count(old)==1
    source=source.replace(old,"functional=report.get('native_slot_switch_passed')")
sys.argv[0]=str(runner)
exec(compile(source,str(runner),'exec'),{'__name__':'__main__','__file__':str(runner)})
