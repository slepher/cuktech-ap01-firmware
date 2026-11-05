"""Execute fixed-ROM directory read instructions in james.local Docker.

Mount/handle state and lock results are substituted. This does not mount flash,
walk LittleFS directory records, or prove the full enumeration lifecycle.
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
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.exists() and a.output.parent.is_dir()
    assert sha(a.qemu) == a.expected_engine_sha256
    audit = load('network_audit', Path(__file__).with_name('audit-native-directory-0041.py'))
    rom = a.rom.read_bytes(); audit.audit(rom)
    support_path = a.support_dir/'run-qemu-ap01.py'
    sys.path.insert(0, str(a.support_dir.resolve()))
    support = load('qemu_support', support_path)
    report = dict(passed=False, device_accessed=False, full_rom_boot=False,
                  cpu='rv32,xtheadbb=true,xtheadmempair=true,xtheadmemidx=true',
                  engine_sha256=sha(a.qemu), support_sha256=sha(support_path),
                  script_sha256=sha(Path(__file__)), rom_sha256=sha(a.rom),
                  cases=[],
                  substitutes=['mount and directory handle state', 'mount lock/unlock return values'],
                  scheduler_executed=False,
                  full_directory_enumeration_verified=False)
    try:
        with tempfile.TemporaryDirectory(prefix='ap01-net-') as folder:
            socket = Path(folder)/'gdb.sock'
            with a.output.with_suffix('.log').open('x') as log:
                process = subprocess.Popen([str(a.qemu), '-M', 'ap01', '-cpu', report['cpu'],
                    '-kernel', str(a.rom), '-S', '-display', 'none', '-serial', 'none',
                    '-monitor', 'none', '-d', 'guest_errors,int', '-gdb', f'unix:{socket},server=on,wait=off'],
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
                    # Execute ROM bytes unchanged; intercept only mount locks.
                    for address in (0xa00448c4, 0xa004493c, 0xa003f97c):
                        assert read(address, 16) == rom[address-0x9ffff000:address-0x9ffff000+16]
                    stop, sp = 0xa8101000, 0xa81fe000
                    inode, mount, handle, output = 0xa81d0000, 0xa81d1000, 0xa81d2000, 0xa81d3000
                    write(stop, struct.pack('<I', 0x6f))
                    for address in (0, stop, 0xa0027968, 0xa00274b2):ok(f'Z0,{address:x},4')
                    for position, lock_result in ((0,-16),(0,0),(1,0)):
                        write(inode,bytes(32));write(inode+24,struct.pack('<I',mount))
                        write(mount,bytes(300));write(handle,bytes(60))
                        write(handle+48,struct.pack('<I',position))
                        write(output-16,b'\xa5'*162)
                        regs=start(0xa00448c4,{10:inode,11:handle,12:output})
                        assert regs[32]==0xa0027968 and regs[10]==mount
                        reg(10,lock_result & 0xffffffff);regs=run(regs[1])
                        if lock_result==0:
                            assert regs[32]==0xa00274b2 and regs[10]==mount, f'unexpected PC {regs[32]:08x}; inspect exception log'
                            reg(10,0);regs=run(regs[1])
                        assert regs[32]==stop and regs[2]==sp
                        before=read(output-16,16);after=read(output+130,16)
                        assert before==after==b'\xa5'*16
                        data=read(output,130)
                        if lock_result:
                            assert regs[10]==lock_result & 0xffffffff
                            assert data==b'\xa5'*130
                        else:
                            assert regs[10]==0 or regs[10]==1, hex(regs[10])
                            expected=b'.' if position==0 else b'..'
                            assert data[0]==4 and data[1:2+len(expected)]==expected+b'\0',data.hex()
                        next_position=struct.unpack('<I',read(handle+48,4))[0]
                        assert next_position==position+(lock_result==0)
                        report['cases'].append(dict(position=position,lock_result=lock_result,
                            return_value=hex(regs[10]),output_hex=data.hex(),
                            guards_preserved=True,next_position=next_position))
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
