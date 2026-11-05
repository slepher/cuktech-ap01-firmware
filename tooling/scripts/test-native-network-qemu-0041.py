"""Run the native listener prefix, socket/accept and thread TLS instructions.

Run only in james.local Docker. Socket allocation/setup is substituted by a
zeroed connection, with an empty accept backlog. No kernel boot, radio, real
socket, semaphore wait, or wall-clock latency is claimed.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qemu', type=Path, required=True)
    p.add_argument('--expected-engine-sha256', required=True)
    p.add_argument('--support-dir', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--listener', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.is_dir()
    assert sha(a.qemu) == a.expected_engine_sha256
    audit = load('network_audit', Path(__file__).with_name('audit-native-network-0041.py'))
    rom = a.rom.read_bytes(); audit.audit(rom)
    thread_audit = load('thread_audit', Path(__file__).with_name('audit-native-thread-0041.py'))
    thread_audit.audit(rom)
    support_path = a.support_dir/'run-qemu-ap01.py'
    sys.path.insert(0, str(a.support_dir.resolve()))
    support = load('qemu_support', support_path)
    report = dict(passed=False, device_accessed=False, full_rom_boot=False,
                  cpu='rv32,xtheadbb=true',
                  engine_sha256=sha(a.qemu), support_sha256=sha(support_path),
                  script_sha256=sha(Path(__file__)), rom_sha256=sha(a.rom),
                  listener_sha256=sha(a.listener), cases=[],
                  substitutes=['socket setup/allocation', 'empty connection/backlog', 'current TCB and TLS fields'],
                  scheduler_executed=False,
                  real_network_or_latency_verified=False)
    try:
        with tempfile.TemporaryDirectory(prefix='ap01-net-') as folder:
            socket = Path(folder)/'gdb.sock'
            with a.output.with_suffix('.log').open('x') as log:
                process = subprocess.Popen([str(a.qemu), '-M', 'ap01', '-cpu', report['cpu'],
                    '-kernel', str(a.rom), '-S', '-display', 'none', '-serial', 'none',
                    '-monitor', 'none', '-gdb', f'unix:{socket},server=on,wait=off'],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, preexec_fn=support.child_limits)
                conn = None
                try:
                    deadline = time.monotonic()+20
                    conn = support.connect(socket, process, deadline)
                    rsp = support.RSP(conn, deadline); rsp.request('?')
                    def ok(command):
                        assert rsp.request(command) == 'OK', command[:60]
                    def write(address, data):
                        for at in range(0, len(data), 256):
                            chunk = data[at:at+256]
                            ok(f'M{address+at:x},{len(chunk):x}:{chunk.hex()}')
                    def read(address, size):
                        data = bytes.fromhex(rsp.request(f'm{address:x},{size:x}'))
                        assert len(data) == size
                        return data
                    def reg(n, value):
                        ok(f'P{n:x}='+struct.pack('<I', value).hex())
                    def run(pc=None):
                        if pc is not None: reg(32, pc)
                        rsp.deadline = time.monotonic()+5
                        reply = rsp.request('c'); assert reply.startswith(('T05', 'S05')), reply
                        return struct.unpack('<33I', bytes.fromhex(rsp.request('g'))[:132])
                    def start(pc, values):
                        for n, value in {1:stop, 2:sp, **values}.items(): reg(n, value)
                        return run(pc)
                    # Confirm QEMU maps the unmodified image at its actual ROM addresses.
                    for addr in (0xa00360e2, 0xa0036194, 0xa00349d6, 0xa01be928):
                        assert read(addr, 16) == rom[addr-audit.BASE:addr-audit.BASE+16]
                    code, stop, sp = 0xa8100000, 0xa8101000, 0xa81fe000
                    sock, connection, accepted = 0xa81e0000, 0xa81e0100, 0xa81e0400
                    write(code, a.listener.read_bytes()); write(stop, struct.pack('<I', 0x6f))
                    ok(f'Z0,{stop:x},4'); ok('Z0,a00268c4,4')
                    for udp in (0, 1):
                        regs = start(code, {10:18081 if not udp else 8767, 11:udp})
                        assert (regs[32], regs[10], regs[11], regs[12]) == (0xa00268c4, 2, 0x801+udp, 0)
                        report['cases'].append(dict(listener='udp' if udp else 'tcp', socket_type=regs[11]))
                    ok('z0,a00268c4,4'); ok('Z0,a003401e,4'); ok('Z0,a003c08e,4')
                    for socket_type in (1, 0x801, 0x802):
                        write(sock, bytes(0x500))
                        regs = start(0xa00360e2, {10:2, 11:socket_type, 12:0, 13:sock})
                        assert regs[32] == 0xa003401e, hex(regs[32])
                        # Substitute only setup: install its normally allocated connection.
                        write(sock+4, struct.pack('<I', connection)); reg(10, 0)
                        regs = run(regs[1])
                        assert regs[32] == stop and regs[10] == 0 and regs[2] == sp
                        flags = read(connection+29, 1)[0]
                        assert flags == (9 if socket_type & 0x800 else 1)
                        case = dict(socket_type=socket_type, connection_flags=flags)
                        if socket_type & 15 == 1:
                            # Match the configured 2-second receive timeout (20 deciseconds).
                            write(connection+24, struct.pack('<H', 20))
                            case['receive_timeout_deciseconds'] = 20
                            regs = start(0xa00349d6, {10:sock, 11:0, 12:0, 13:accepted, 14:0})
                            if socket_type & 0x800:
                                assert regs[32] == stop and regs[10] == 0xfffffff5 and regs[2] == sp
                                case['empty_accept'] = 'EAGAIN without entering wait'
                            else:
                                assert regs[32] == 0xa003c08e and regs[11] == 0xffffffff
                                case['empty_accept'] = 'reaches wait with timeout -1 (stopped before wait)'
                        report['cases'].append(case)
                    # Execute the real lookup and errno paths with distinct
                    # task records; do not pretend this runs the scheduler.
                    for addr in (0xa002671a, 0xa0026784, 0xa00267c0):
                        assert read(addr, 16) == rom[addr-audit.BASE:addr-audit.BASE+16]
                    for tcb, tls in ((0xa81d0000,0xa81d1000),(0xa81d0100,0xa81d2000),
                                     (0xa81d0000,0xa81d1000),(0xa81d0100,0)):
                        write(tcb,bytes(80));write(tcb+60,struct.pack('<I',tls))
                        write(0x62fc6c18,struct.pack('<I',tcb))
                        regs=start(0xa0026784,{})
                        assert regs[32]==stop and regs[10]==tls and regs[2]==sp
                        regs=start(0xa00267c0,{})
                        expected=tls+4 if tls else 0x62fc604c
                        assert regs[32]==stop and regs[10]==expected and regs[2]==sp
                        report['cases'].append(dict(current_tcb=hex(tcb),thread_identity=hex(tls),
                                                    errno_slot=hex(expected)))
                finally:
                    if conn: conn.close()
                    if process.poll() is None:
                        process.terminate()
                        try: process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            process.kill(); process.wait(timeout=2)
        report['passed'] = True
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        a.output.write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(report))


if __name__ == '__main__':
    main()
