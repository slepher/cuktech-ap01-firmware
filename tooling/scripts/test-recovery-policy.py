#!/usr/bin/env python3
"""Executable policy prototype + NOR cut model. Not an integrated rescue ROM."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
import uuid
import zlib

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(file))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


probe = module('recovery_probe', 'run-qemu-ap01.py')
fixture = module('recovery_fixture', 'build-qemu-flash-fixture.py')


class Policy(ctypes.Structure):
    _fields_ = [(k, ctypes.c_uint32) for k in ('phase', 'armed_ms', 'healthy_since', 'tracking_health')]


def table(slot, age, entry_age=0):
    b = bytearray(fixture.partition_table(age))
    b[18] = slot
    struct.pack_into('<I', b, 48, entry_age)
    struct.pack_into('<I', b, 52, zlib.crc32(b[16:52]))
    return bytes(b)


def select(tables):
    valid = []
    for index, b in enumerate(tables):
        try:
            info = fixture.validate_table(b)
        except ValueError:
            continue
        valid.append((info['age'], -index, b[18]))
    if not valid:
        raise ValueError('both partition tables invalid; no recovered Boot2 policy')
    age, index, slot = max(valid)
    return -index, slot, age


def persist(tables, slot):
    index, _, age = select(tables)
    if age == 0xffffffff:
        raise ValueError('unsigned partition age wrap is not safe')
    tables[1-index] = table(slot, age+1)


def cuts(old, new):
    # Each erase byte prefix and each programmed byte prefix, plus bit-torn
    # last bytes. Synthetic cut granularity; not a silicon power-loss model.
    for n in range(4097):
        yield 'erase', n, b'\xff'*n + old[n:]
    erased = b'\xff'*4096
    for n in range(57):
        yield 'program', n, new[:n] + erased[n:]
        if n < 56:
            for bits in (1, 3, 7, 15, 31, 63, 127):
                torn = new[n] | bits
                yield 'torn-program', n, new[:n] + bytes([torn]) + erased[n+1:]


def run_model(lib):
    lib.recovery_step.argtypes = [ctypes.POINTER(Policy)] + [ctypes.c_uint32]*6
    lib.recovery_step.restype = ctypes.c_uint32
    cases = []
    def record(name, passed, safe, detail):
        if not passed:
            raise AssertionError(name)
        cases.append(dict(name=name, test_passed=True, recovery_guaranteed_in_model=safe, detail=detail))
    def step(s, tables, now, button=0, healthy=0, failed=0):
        return lib.recovery_step(ctypes.byref(s), 1, select(tables)[1], now, button, healthy, failed)
    tables = [table(0,19), table(1,20)]
    record('crash before guard, repeated power cycle', select(tables)[1] == 1,
           False, 'guard never runs; durable table keeps selecting broken slot1')
    record('button held but crash before guard', select(tables)[1] == 1,
           False, 'application-side GPIO detection cannot run before the guard')
    s = Policy()
    assert step(s,tables,1000) == 1
    persist(tables,0)
    assert step(s,tables,1001) == 2
    record('crash after arm readback, before confirmation', select(tables)[1] == 0,
           True, 'next modeled reset selects slot0')
    assert step(s,tables,2000,healthy=1) == 2
    assert step(s,tables,11999,healthy=1) == 2
    assert step(s,tables,12000,healthy=1) == 3
    persist(tables,1)
    assert step(s,tables,12001,healthy=1) == 2
    record('late crash after healthy confirmation', select(tables)[1] == 1,
           False, 'confirmation intentionally reselects slot1; one reboot still enters slot1')
    again = Policy()
    assert step(again,tables,1000) == 1
    persist(tables,0)
    assert step(again,tables,1001,healthy=1) == 2
    assert step(again,tables,11001,healthy=1) == 3
    persist(tables,1)
    record('single ordinary reboot followed by another healthy window', select(tables)[1] == 1,
           False, 'does not permanently return to fallback; needs button or a second timed power cycle')
    again = Policy()
    assert step(again,tables,1000) == 1
    persist(tables,0)
    record('second power cycle after durable arm and before confirmation', select(tables)[1] == 0,
           True, 'conditional escape window starts after persisted arm, not at power-on')
    persist(tables,1)
    button = Policy()
    assert step(button,tables,1000,button=1) == 1
    persist(tables,0)
    assert step(button,tables,1001,button=0) == 4
    record('held startup button with reachable guard', select(tables)[1] == 0,
           True, 'latched request survives button release and requests reset after readback')
    bad = [table(0,0xfffffffe),table(1,0xffffffff)]
    try:
        persist(bad,0)
    except ValueError:
        pass
    else:
        raise AssertionError('age overflow accepted')
    record('partition age exhausted', select(bad)[1] == 1,
           False, 'reject write; application cannot promise fallback without additional boot metadata policy')
    cut_results = []
    for target in (0,1):
        start = [table(0,19),table(1,20)] if target==0 else [table(0,21),table(1,20)]
        active, _, age = select(start)
        totals = {0:0,1:0}
        for phase, position, damaged in cuts(start[1-active],table(target,age+1)):
            trial = start.copy();trial[1-active] = damaged
            _, selected, _ = select(trial)
            totals[selected] += 1
            assert trial[active] == start[active]
        assert totals[0] and totals[1]
        cut_results.append(dict(operation='arm' if target==0 else 'confirm',
            modeled_cut_states=sum(totals.values()), next_boot_slot_counts=totals,
            original_selected_table_preserved=True,
            guaranteed_base_before_arm_commit=False if target==0 else None))
    return cases, cut_results


def native(qemu, image, output):
    name = 'recovery-' + uuid.uuid4().hex
    gdb, qmp_path = (Path('/tmp')/(name+s) for s in ('.gdb','.qmp'))
    deadline = time.monotonic()+20
    command = [str(qemu),'-M','ap01,boot-mmio=on,boot2-mock=on','-cpu','rv32',
        '-kernel',str(image),'-S','-display','none','-serial','none','-monitor','none',
        '-gdb',f'unix:{gdb},server=on,wait=off','-qmp',f'unix:{qmp_path},server=on,wait=off']
    process=gs=qs=qm=None
    try:
        with output.with_suffix('.qemu.log').open('x') as log:
            process=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=log,stderr=log,preexec_fn=probe.child_limits)
            engine=hashlib.sha256(Path(f'/proc/{process.pid}/exe').read_bytes()).hexdigest()
            gs=probe.connect(gdb,process,deadline);qs=probe.connect(qmp_path,process,deadline)
            rsp=probe.RSP(gs,deadline);qm=probe.QMP(qs,deadline)
            for index,value in ((2,0x20fcf000),(1,0x20fc0100),(32,0xa0000000)):
                assert rsp.request(f'P{index:x}='+value.to_bytes(4,'little').hex())=='OK'
            assert rsp.request('Z0,20fc0100,2')=='OK'
            assert rsp.request('Z0,0,2')=='OK'
            rsp.request('c')
            regs=struct.unpack('<33I',bytes.fromhex(rsp.request('g'))[:132])
            values=struct.unpack('<3I',bytes.fromhex(rsp.request('m20fd0000,c')))
            assert regs[32]==0x20fc0100 and values[0] and values[1]==0 and values[2]==0x52475031
            return dict(checks=values[0],failures=values[1],qemu_sha256=engine,command=command)
    finally:
        if qm:qm.file.close()
        for sock in (gs,qs):
            if sock:sock.close()
        if process:
            process.terminate()
            try:process.wait(timeout=2)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=2)
        for path in (gdb,qmp_path):path.unlink(missing_ok=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qemu',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve()
    paths=[out.with_suffix(s) for s in ('.host','.so','.elf','.payload.bin','.rom.bin','.qemu.log')]+[out]
    if not out.parent.is_dir() or any(x.exists() for x in paths):p.error('new files in existing directory required')
    src=ROOT/'tooling/firmware-modules'
    sources=[src/'recovery_policy.c',src/'test_recovery_policy.c']
    report=dict(simulation_only=True,integrated_rom_tested=False,physical_boot2_tested=False,
        universal_recovery_claim_supported=False,source_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sources+[src/'recovery_policy.h']})
    try:
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',*map(str,sources),'-o',str(paths[0])],check=True,capture_output=True,timeout=30)
        checked=subprocess.run([str(paths[0])],check=True,capture_output=True,text=True,timeout=10,env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1:detect_leaks=1',UBSAN_OPTIONS='halt_on_error=1'))
        assert not checked.stderr
        report['host']=json.loads(checked.stdout)
        subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-O2','-shared','-fPIC',str(sources[0]),'-o',str(paths[1])],check=True,capture_output=True,timeout=30)
        report['scenarios'],report['nor_cuts']=run_model(ctypes.CDLL(str(paths[1])))
        tool=ROOT.parent/'cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf'
        subprocess.run([str(tool)+'-gcc','-B'+str(tool.parent)+'/', '-march=rv32imac','-mabi=ilp32','-Os','-ffreestanding','-fno-builtin','-msmall-data-limit=0','-mno-relax','-nostdlib','-nostartfiles','-Wl,-Ttext=0xa0000000,-e,recovery_run_tests,--no-relax',*map(str,sources),'-o',str(paths[2])],check=True,capture_output=True,timeout=30)
        subprocess.run([str(tool)+'-objcopy','-O','binary',str(paths[2]),str(paths[3])],check=True,capture_output=True,timeout=10)
        paths[4].write_bytes(bytes(4096)+paths[3].read_bytes())
        report['rv32']=native(a.qemu.resolve(),paths[4],out)
        assert report['host']['checks']==report['rv32']['checks']
        report['experiment_passed']=True
    except Exception as exc:
        report.update(experiment_passed=False,error=f'{type(exc).__name__}: {exc}')
        if isinstance(exc,subprocess.CalledProcessError):report['tool_stderr']=exc.stderr.decode('utf-8','replace') if isinstance(exc.stderr,bytes) else exc.stderr
    with out.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(experiment_passed=report['experiment_passed'],universal_recovery_claim_supported=False,output=str(out),error=report.get('error'))))
    return 0 if report['experiment_passed'] else 1


if __name__=='__main__':sys.exit(main())
