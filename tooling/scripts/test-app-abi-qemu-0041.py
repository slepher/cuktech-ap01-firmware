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
    p.add_argument('--guest-diagnostics',action='store_true',help='Enable bounded QEMU guest error/interrupt logging')
    p.add_argument('--direct-v3', action='store_true', help='Execute real ABI 3 App model guest')
    p.add_argument('--qemu', type=Path, required=True)
    p.add_argument('--expected-engine-sha256', required=True)
    p.add_argument('--support-dir', type=Path, required=True)
    p.add_argument('--fixture-dir', type=Path, required=True)
    p.add_argument('--next-fixture',type=Path,action='append',default=[],help='Next boot in the same VM after QMP system_reset; exact journal or business-file handoff required')
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        p.error('output must be new, with an existing parent')
    assert sha(args.qemu) == args.expected_engine_sha256, 'QEMU identity changed'
    sys.path.insert(0, str(args.support_dir.resolve()))
    support_path = args.support_dir / 'run-qemu-ap01.py'
    support = module('ap01_qemu_transport', support_path)
    fixtures=[]
    for directory in [args.fixture_dir,*args.next_fixture]:
        probe=json.loads((directory/'build-report.json').read_text())
        assert probe['built'] and sha(directory/'guest.bin')==probe['guest_sha256']
        assert sha(directory/'app.apx2')==probe['package_sha256']
        for item in probe.get('extra_inputs',[]):
            assert Path(item['name']).name==item['name']
            assert sha(directory/item['name'])==item['sha256']
        fixtures.append((directory,probe))
    if args.next_fixture:
        assert args.direct_v3 and len(fixtures)<=3
        assert all(probe.get('guest_bss') for _,probe in fixtures)
        assert all(probe.get('journal_export') for _,probe in fixtures) or all(probe.get('business_export') for _,probe in fixtures)
        assert all(probe['bases']==fixtures[0][1]['bases'] for _,probe in fixtures)
        assert all(probe.get('cpu','rv32')==fixtures[0][1].get('cpu','rv32') for _,probe in fixtures)
    probe=fixtures[0][1];image=args.fixture_dir/'guest.bin';package=args.fixture_dir/'app.apx2'
    extras=probe.get('extra_inputs',[])
    results = {}
    report = {'passed': False, 'engine_sha256': sha(args.qemu),
              'support_sha256': sha(support_path), 'script_sha256': sha(Path(__file__)),
              'guest_sha256': sha(image), 'package_sha256': sha(package),
              'build_report_sha256': sha(args.fixture_dir/'build-report.json'),
              'production_apx2_loader_executed': False, 'abi_v2_entries_executed': False,
              'synthetic_fixture': not args.direct_v3, 'substitutes': probe.get('substitutes', []), 'hardware_verified': False, 'full_rom_boot_verified': False,
              'collection': probe.get('collection', False), 'extra_inputs': extras, 'results': results,
              'same_vm_reset_requested':bool(args.next_fixture),
              'boot_inputs':[{'mode':p.get('boot_mode'),'build_report_sha256':sha(d/'build-report.json')} for d,p in fixtures]}
    try:
        with tempfile.TemporaryDirectory(prefix='ap01-s1-') as directory:
            root = Path(directory)
            kernel = root / 'idle.bin'
            # AP01's raw-image reader requires >4 KiB. Only the first word runs.
            kernel.write_bytes(struct.pack('<I', 0x0000006f) + bytes(8188))  # j .; no original ROM
            for base in (probe['bases'] if args.direct_v3 else (0x62fca000, 0xa8000000)):
                socket_path = root / 'gdb.sock';qmp_path=root/'qmp.sock'
                command = [str(args.qemu), '-M', 'ap01', '-cpu', probe.get('cpu','rv32'), '-kernel', str(kernel),
                           '-S', '-display', 'none', '-serial', 'none', '-monitor', 'none',
                           '-gdb', f'unix:{socket_path},server=on,wait=off',
                           '-qmp',f'unix:{qmp_path},server=on,wait=off']
                if args.guest_diagnostics:command += ['-d','guest_errors,int']
                log_path = args.output.with_suffix(f'.{base:x}.log')
                with log_path.open('x') as log:
                    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                               preexec_fn=support.child_limits)
                    connection = None;qmp_socket=None;qmp=None
                    try:
                        deadline = time.monotonic() + 20
                        connection = support.connect(socket_path, process, deadline)
                        rsp = support.RSP(connection, deadline)
                        rsp.request('?')
                        if args.next_fixture:
                            qmp_socket=support.connect(qmp_path,process,deadline)
                            qmp=support.QMP(qmp_socket,deadline)
                        def expect_ok(request):
                            assert rsp.request(request) == 'OK', request[:40]
                        def write(address, data):
                            for at in range(0, len(data), 256):
                                chunk = data[at:at + 256]
                                expect_ok(f'M{address+at:x},{len(chunk):x}:{chunk.hex()}')
                        def register(number, value):
                            expect_ok(f'P{number:x}=' + struct.pack('<I', value).hex())
                        previous_journals=None;previous_business=None
                        if args.next_fixture:results[hex(base)]={'stages':[],'resets':[]}
                        for stage,(fixture,probe) in enumerate(fixtures):
                            rsp.deadline=time.monotonic()+20
                            if stage:
                                handoff={}
                                if probe.get('journal_export'):
                                    assert previous_journals==(fixture/'journals.bin').read_bytes(), 'journal handoff mismatch'
                                    handoff['journal_handoff_identical']=True
                                if probe.get('business_export'):
                                    assert previous_business==(fixture/'business-files.bin').read_bytes(), 'business-file handoff mismatch'
                                    handoff['business_handoff_identical']=True
                                assert handoff
                                qmp.deadline=time.monotonic()+5
                                expect_ok(f'z0,{stop:x},4')
                                qmp.command('system_reset')
                                assert not qmp.command('query-status')['running']
                                reset_regs=bytes.fromhex(rsp.request('g'))
                                reset_pc=struct.unpack_from('<I',reset_regs,32*4)[0]
                                assert reset_pc!=stop and process.poll() is None
                                results[hex(base)]['resets'].append({'pid':process.pid,'pc_after_reset':hex(reset_pc),**handoff})
                            image=fixture/'guest.bin';package=fixture/'app.apx2';extras=probe.get('extra_inputs',[])
                            write(probe['guest_base'],image.read_bytes())
                            if probe.get('guest_bss'):
                                bss=probe['guest_bss'];assert 0xa8100000<=bss['address']<=bss['address']+bss['size']<=0xa8180000
                                write(bss['address'],bytes(bss['size']))
                            package_address,stop,sp=(probe['package_address'],probe['stop'],probe['sp']) if args.direct_v3 else (0x62fce000,0x62fc8000,0x62fd4000)
                            write(package_address,package.read_bytes())
                            for item in extras:
                                data=(previous_journals if stage and item['name']=='journals.bin' else
                                      previous_business if stage and item['name']=='business-files.bin' else (fixture/item['name']).read_bytes())
                                write(item['address'],data)
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
                            stage_result={'result':result,'stack_and_saved_registers_preserved':True,'boot_mode':probe.get('boot_mode')}
                            if args.next_fixture:results[hex(base)]['stages'].append(stage_result)
                            else:results[hex(base)]=stage_result
                            assert result==0,f'guest assertion failed at source line {result}'
                            if probe.get('business_export'):
                                export=probe['business_export'];assert export=={'address':0xa81d0000,'limit':0x1f000}
                                header=bytes.fromhex(rsp.request('ma81d0000,20'));assert header[:4]==b'BFV1'
                                total=struct.unpack_from('<I',header,4)[0];assert 32<=total<=export['limit']
                                data=bytearray(header)
                                for offset in range(32,total,256):
                                    count=min(256,total-offset);chunk=bytes.fromhex(rsp.request(f'm{export["address"]+offset:x},{count:x}'))
                                    assert len(chunk)==count;data.extend(chunk)
                                lengths=struct.unpack_from('<6I',header,8)
                                assert 32+sum(n for n in lengths if n!=0xffffffff)==total
                                suffix=f'.stage{stage}' if args.next_fixture else ''
                                path=args.output.with_suffix(f'.{base:x}{suffix}.business-files.bin');assert not path.exists();path.write_bytes(data)
                                previous_business=bytes(data)
                                stage_result['business_files']={'name':path.name,'sha256':sha(path),'lengths':list(lengths)}
                            if probe.get('journal_export'):
                                export=probe['journal_export'];assert export=={'address':0xa81ff000,'size':648}
                                data=bytearray()
                                for offset in range(0,648,128):
                                    count=min(128,648-offset)
                                    chunk=bytes.fromhex(rsp.request(f'm{export["address"]+offset:x},{count:x}'))
                                    assert len(chunk)==count;data.extend(chunk)
                                suffix=f'.stage{stage}' if args.next_fixture else ''
                                path=args.output.with_suffix(f'.{base:x}{suffix}.journals.bin');assert not path.exists()
                                path.write_bytes(data);previous_journals=bytes(data)
                                stage_result['journals']={'name':path.name,'sha256':sha(path)}
                            if probe.get('runtime_export'):
                                export=probe['runtime_export'];assert export=={'address':0xa81ff300,'size':912}
                                data=bytearray()
                                for offset in range(0,912,128):
                                    count=min(128,912-offset);chunk=bytes.fromhex(rsp.request(f'm{export["address"]+offset:x},{count:x}'))
                                    assert len(chunk)==count;data.extend(chunk)
                                assert data[:8]==b'ARV3\x01\0\0\0'
                                suffix=f'.stage{stage}' if args.next_fixture else ''
                                path=args.output.with_suffix(f'.{base:x}{suffix}.runtime.bin');assert not path.exists();path.write_bytes(data)
                                stage_result['runtime']={'name':path.name,'sha256':sha(path)}
                    finally:
                        report.setdefault('qemu_exit_before_cleanup',{})[hex(base)]=process.poll()
                        if qmp:qmp.file.close()
                        if qmp_socket:qmp_socket.close()
                        if connection:
                            connection.close()
                        if process.poll() is None:
                            process.terminate()
                            try:
                                process.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                process.kill()
                                process.wait(timeout=2)
                        socket_path.unlink(missing_ok=True);qmp_path.unlink(missing_ok=True)
        maintenance_only=args.direct_v3 and all(p.get('boot_mode') in ('maintenance','empty-rollback') for _,p in fixtures)
        maintenance_verified=args.direct_v3 and any(p.get('boot_mode')=='maintenance' for _,p in fixtures)
        report.update(passed=True,production_apx2_loader_executed=not maintenance_only,
                      abi_v2_entries_executed=not args.direct_v3,
                      real_abi_v3_app_executed=args.direct_v3 and not maintenance_only,
                      real_abi_v3_collection_executed=args.direct_v3 and probe.get('collection',False) and not maintenance_only,
                      no_app_maintenance_verified=maintenance_verified,
                      same_vm_reset_verified=bool(args.next_fixture),
                      empty_collection_rollback_verified=any(p.get('boot_mode')=='empty-rollback' for _,p in fixtures))
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))


if __name__ == '__main__':
    main()
