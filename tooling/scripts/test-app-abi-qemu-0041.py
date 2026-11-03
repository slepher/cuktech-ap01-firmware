"""Execute APX2 loading and five-entry lifecycle in james.local Docker QEMU.

Uses the historical runner's bounded GDB transport, not a new board model.
No real ROM boot, cache coherence, MPU, device access or App capacity claim.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import time


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--direct-v3', action='store_true', help='Execute real ABI 3 App model guest')
    p.add_argument('--qemu', type=Path, required=True)
    p.add_argument('--expected-engine-sha256', required=True)
    p.add_argument('--support-dir', type=Path, required=True)
    p.add_argument('--fixture-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        p.error('output must be new, with an existing parent')
    assert sha(args.qemu) == args.expected_engine_sha256, 'QEMU identity changed'
    sys.path.insert(0, str(args.support_dir.resolve()))
    support_path = args.support_dir / 'run-qemu-ap01.py'
    support = module('ap01_qemu_transport', support_path)
    probe = json.loads((args.fixture_dir / 'build-report.json').read_text())
    image = args.fixture_dir / 'guest.bin'
    package = args.fixture_dir / 'app.apx2'
    assert probe['built'] and sha(image) == probe['guest_sha256']
    assert sha(package) == probe['package_sha256']
    results = {}
    report = {'passed': False, 'engine_sha256': sha(args.qemu),
              'support_sha256': sha(support_path), 'script_sha256': sha(Path(__file__)),
              'guest_sha256': sha(image), 'package_sha256': sha(package),
              'build_report_sha256': sha(args.fixture_dir/'build-report.json'),
              'production_apx2_loader_executed': False, 'abi_v2_entries_executed': False,
              'synthetic_fixture': not args.direct_v3, 'substitutes': probe.get('substitutes', []), 'hardware_verified': False, 'full_rom_boot_verified': False,
              'results': results}
    try:
        with tempfile.TemporaryDirectory(prefix='ap01-s1-') as directory:
            root = Path(directory)
            kernel = root / 'idle.bin'
            # AP01's raw-image reader requires >4 KiB. Only the first word runs.
            kernel.write_bytes(struct.pack('<I', 0x0000006f) + bytes(8188))  # j .; no original ROM
            for base in (probe['bases'] if args.direct_v3 else (0x62fca000, 0xa8000000)):
                socket_path = root / 'gdb.sock'
                command = [str(args.qemu), '-M', 'ap01', '-cpu', 'rv32', '-kernel', str(kernel),
                           '-S', '-display', 'none', '-serial', 'none', '-monitor', 'none',
                           '-gdb', f'unix:{socket_path},server=on,wait=off']
                log_path = args.output.with_suffix(f'.{base:x}.log')
                with log_path.open('x') as log:
                    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                               preexec_fn=support.child_limits)
                    connection = None
                    try:
                        deadline = time.monotonic() + 20
                        connection = support.connect(socket_path, process, deadline)
                        rsp = support.RSP(connection, deadline)
                        rsp.request('?')
                        def expect_ok(request):
                            assert rsp.request(request) == 'OK', request[:40]
                        def write(address, data):
                            for at in range(0, len(data), 256):
                                chunk = data[at:at + 256]
                                expect_ok(f'M{address+at:x},{len(chunk):x}:{chunk.hex()}')
                        def register(number, value):
                            expect_ok(f'P{number:x}=' + struct.pack('<I', value).hex())
                        write(probe['guest_base'],image.read_bytes())
                        package_address,stop,sp=(probe['package_address'],probe['stop'],probe['sp']) if args.direct_v3 else (0x62fce000,0x62fc8000,0x62fd4000)
                        write(package_address,package.read_bytes())
                        write(stop,struct.pack('<I',0x0000006f))
                        expect_ok(f'Z0,{stop:x},4')
                        saved={reg:0x55000000+reg for reg in range(18,28)}
                        for reg,value in saved.items():register(reg,value)
                        for reg,value in ((1,stop),(2,sp),(8,0x12345678),(9,0x76543210),
                                          (10,base),(11,package_address),(12,package.stat().st_size),
                                          (32,probe['guest_base'])):
                            register(reg,value)
                        response=rsp.request('c')
                        assert response.startswith(('T05','S05')),response
                        registers=bytes.fromhex(rsp.request('g'))
                        get=lambda n:struct.unpack_from('<I',registers,n*4)[0]
                        assert (get(32),get(2),get(8),get(9))==(stop,sp,0x12345678,0x76543210)
                        assert all(get(reg)==value for reg,value in saved.items())
                        result=get(10)
                        results[hex(base)]={'result':result,'stack_and_saved_registers_preserved':True}
                        assert result==0,f'guest assertion failed at source line {result}'
                    finally:
                        if connection:
                            connection.close()
                        if process.poll() is None:
                            process.terminate()
                            try:
                                process.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                process.kill()
                                process.wait(timeout=2)
                        socket_path.unlink(missing_ok=True)
        report.update(passed=True,production_apx2_loader_executed=True,abi_v2_entries_executed=not args.direct_v3,real_abi_v3_app_executed=args.direct_v3)
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))


if __name__ == '__main__':
    main()
