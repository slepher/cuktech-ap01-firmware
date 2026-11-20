"""Execute reviewed 0055 native instructions and candidate trampolines in AP01 QEMU.

Run with an existing AP01 QEMU in Linux/WSL or an isolated container. Heavy
operating system and UI calls are intercepted; this is not a complete ROM boot.
The original/candidate ROM and optional matching ELF must be SHA-pinned by caller.
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

BASE = 0x9ffff000
OFFSET = 0x675000
ORIGINAL_SHA = '0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7'
CPU = 'rv32,xtheadbb=true,xtheadmempair=true,xtheadmemidx=true,xtheadcmo=true,xtheadmac=true'
PINNED_NATIVE = {
    0xa006bd58: '8347c900374afc62',  # signed_file load before unsigned rejection
    0xa006fce6: '8347ca00bdef',      # downstream signed_file conditional
    0xa006fd68: '81454a85eff0dfd4',  # signature verification call setup
    0xa00268e2: '8bb7b52c',
    0xa00360e2: 'b7f7f7ff9387077fed8ff1eb93f7f500',
    0xa0036194: '8b35b92cdc4099c503c7d70113678700a38ee700',
    0xa0034a4c: '03c7d901218b41cbd554cda8',
    0xa0034af6: 'fd55',
    0xa0034b1a: 'ef704057',
    0xa003c0ac: 'fd572a8926856384f502',
    0xa003c0da: 'efb02ef9',
    0xa0026724: 'b777fc6283a487c3',  # current TCB 62fc6c38
    0xa0026742: '0dc5',
    0xa002676c: '985f014598c1d85fd8c1bc439cc5',
    0xa0026784: '011122cc06ce0010930544fe0145eff09ff8814763440500832784fef24062443e8505618280',
    0xa00267c0: '411122c406c60008eff0dffb11c51105b2402244410182803765fc621305c506c5bf',
    0xa00448c4: '317122dd26db4ad94ed706df52d556d35ad15ecf',
    0xa004493c: '8b571518',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def symbols(path):
    """Read the admitted little-endian RV32 ELF symbol table without dependencies."""
    data = path.read_bytes()
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    assert header[0][:6] == b'\x7fELF\x01\x01' and header[2] == 243
    assert header[11] == 40
    sections = [struct.unpack_from('<10I', data, header[6] + i * 40) for i in range(header[12])]
    result = {}
    for section in sections:
        if section[1] != 2:
            continue
        assert section[9] == 16
        strings = sections[section[6]]
        names = data[strings[4]:strings[4] + strings[5]]
        for at in range(section[4], section[4] + section[5], 16):
            name, value, size, info, other, index = struct.unpack_from('<IIIBBH', data, at)
            if not index or not name:
                continue
            end = names.index(0, name)
            result[names[name:end].decode('ascii')] = value
    return result


def static_audit(rom, expected_sha, elf=None, expected_elf_sha=None):
    digest = hashlib.sha256(rom).hexdigest()
    assert digest == expected_sha, 'input ROM SHA mismatch'
    for address, expected in PINNED_NATIVE.items():
        data = bytes.fromhex(expected)
        assert rom[address - BASE:address - BASE + len(data)] == data, hex(address)
    if elf is None:
        assert digest == ORIGINAL_SHA, 'candidate ROM requires matching ELF'
        return None
    assert expected_elf_sha and sha(elf) == expected_elf_sha
    assert rom[OFFSET:OFFSET + 8] == b'AP01APP1'
    assert rom[OFFSET + 64:OFFSET + 64 + 17] == b'cuktech-ap01-0055'
    assert rom[OFFSET + 128:OFFSET + 160].hex() == ORIGINAL_SHA
    names = symbols(elf)
    required = ('ap01Register0041', 'ap01SettingsRegister0041', 'ap01SettingsList0041',
                 'ap01MenuRegisterOne0041', 'ap01MenuRegisterTwo0041',
                 'ap01MenuRegisterThree0041', 'ap01MenuList0041', 'ap01TimerDelete0041')
    for name in required:
        assert BASE + OFFSET + 256 <= names[name] < BASE + len(rom) - 40, name
    listener = [value for name, value in names.items() if name.endswith('8listenerEjb')]
    assert len(listener) == 1
    return {**{name:names[name] for name in required}, 'listener':listener[0]}


class Machine:
    def __init__(self, rsp):
        self.rsp = rsp
        self.breakpoints = set()
        self.stop = 0xa8101000
        self.sp = 0xa81fe000

    def ok(self, command):
        response = self.rsp.request(command)
        assert response == 'OK', (command[:80], response)

    def write(self, address, data):
        for at in range(0, len(data), 256):
            chunk = data[at:at + 256]
            self.ok(f'M{address + at:x},{len(chunk):x}:{chunk.hex()}')

    def read(self, address, size):
        result = bytes.fromhex(self.rsp.request(f'm{address:x},{size:x}'))
        assert len(result) == size
        return result

    def reg(self, n, value):
        self.ok(f'P{n:x}=' + struct.pack('<I', value & 0xffffffff).hex())

    def breaks(self, addresses):
        addresses = set(addresses)
        for address in sorted(self.breakpoints - addresses):
            self.ok(f'z0,{address:x},4')
        for address in sorted(addresses - self.breakpoints):
            self.ok(f'Z0,{address:x},4')
        self.breakpoints = addresses

    def run(self, pc=None):
        if pc is not None:
            self.reg(32, pc)
        self.rsp.deadline = time.monotonic() + 8
        response = self.rsp.request('c')
        assert response.startswith(('T05', 'S05')), response
        return struct.unpack('<33I', bytes.fromhex(self.rsp.request('g'))[:132])

    def start(self, pc, values=None):
        for n, value in {1:self.stop, 2:self.sp, **(values or {})}.items():
            self.reg(n, value)
        return self.run(pc)

    def returned(self, registers):
        assert registers[32] == self.stop and registers[2] == self.sp


def unsigned_ota_cases(machine, rom, cases):
    """Execute the original/patched gate and the unchanged signature selector."""
    gate = rom[0x6cd60:0x6cd62]
    assert gate in (bytes.fromhex('dde7'), bytes.fromhex('7da0'))
    patched = gate == bytes.fromhex('7da0')
    state = 0xa81c8000
    for flag in (0, 1):
        machine.write(state + 12, bytes([flag]))
        machine.breaks({0xa006bd62, 0xa006be0e})
        registers = machine.start(0xa006bd58, {18: state})
        expected = 0xa006be0e if patched or flag else 0xa006bd62
        assert registers[32] == expected and registers[15] == flag
        assert machine.read(state + 12, 1) == bytes([flag])
        cases.append(dict(kind='unsigned_ota_rejection_gate', patched=patched,
                          signed_file=flag, continued=bool(patched or flag),
                          flag_preserved=True, pc=hex(expected)))
    for flag in (0, 1):
        machine.write(state + 12, bytes([flag]))
        machine.breaks({0xa006fcec, 0xa006fd68})
        registers = machine.start(0xa006fce6, {20: state})
        expected = 0xa006fd68 if flag else 0xa006fcec
        assert registers[32] == expected and registers[15] == flag
        assert machine.read(state + 12, 1) == bytes([flag])
        cases.append(dict(kind='ota_signature_selector', signed_file=flag,
                          signature_validation_selected=bool(flag), pc=hex(expected)))


def native_cases(machine, cases):
    m = machine
    stop, sp = m.stop, m.sp
    m.write(stop, struct.pack('<I', 0x6f))
    m.breaks([stop])
    for tcb, tls in ((0xa81d0000, 0xa81d1000), (0xa81d0100, 0xa81d2000),
                     (0xa81d0000, 0xa81d1000), (0xa81d0100, 0)):
        m.write(tcb, bytes(80))
        m.write(tcb + 60, struct.pack('<I', tls))
        m.write(0x62fc6c38, struct.pack('<I', tcb))
        r = m.start(0xa0026784)
        m.returned(r)
        assert r[10] == tls
        r = m.start(0xa00267c0)
        m.returned(r)
        expected = tls + 4 if tls else 0x62fc606c
        assert r[10] == expected
        cases.append(dict(kind='native_tls_errno', tcb=hex(tcb), tls=hex(tls), errno=hex(expected)))

    sock, connection, accepted = 0xa81e0000, 0xa81e0100, 0xa81e0400
    m.breaks([stop, 0xa003401e, 0xa003c08e])
    for socket_type in (1, 0x801, 0x802):
        m.write(sock, bytes(0x500))
        r = m.start(0xa00360e2, {10:2, 11:socket_type, 12:0, 13:sock})
        assert r[32] == 0xa003401e
        m.write(sock + 4, struct.pack('<I', connection))
        m.reg(10, 0)
        r = m.run(r[1])
        m.returned(r)
        assert r[10] == 0
        flags = m.read(connection + 29, 1)[0]
        assert flags == (9 if socket_type & 0x800 else 1)
        result = dict(kind='native_socket_flags', socket_type=socket_type, connection_flags=flags)
        if socket_type & 15 == 1:
            m.write(connection + 24, struct.pack('<H', 20))
            r = m.start(0xa00349d6, {10:sock, 11:0, 12:0, 13:accepted, 14:0})
            if socket_type & 0x800:
                m.returned(r)
                assert r[10] == 0xfffffff5
                result['empty_accept'] = 'EAGAIN without wait'
            else:
                assert r[32] == 0xa003c08e and r[11] == 0xffffffff
                result['empty_accept'] = 'blocking path stopped before indefinite wait'
        cases.append(result)

    m.breaks([stop, 0, 0xa0027968, 0xa00274b2])
    inode, mount, handle, output = 0xa81d0000, 0xa81d1000, 0xa81d2000, 0xa81d3000
    for position, lock_result in ((0, -16), (0, 0), (1, 0)):
        m.write(inode, bytes(32))
        m.write(inode + 24, struct.pack('<I', mount))
        m.write(mount, bytes(300))
        m.write(handle, bytes(60))
        m.write(handle + 48, struct.pack('<I', position))
        m.write(output - 16, b'\xa5' * 162)
        r = m.start(0xa00448c4, {10:inode, 11:handle, 12:output})
        assert r[32] == 0xa0027968 and r[10] == mount
        m.reg(10, lock_result)
        r = m.run(r[1])
        if lock_result == 0:
            assert r[32] == 0xa00274b2 and r[10] == mount, (
                'directory unlock', hex(r[32]), hex(r[10]), hex(r[1]))
            m.reg(10, 0)
            r = m.run(r[1])
        m.returned(r)
        assert m.read(output - 16, 16) == m.read(output + 130, 16) == b'\xa5' * 16
        data = m.read(output, 130)
        if lock_result:
            assert r[10] == lock_result & 0xffffffff and data == b'\xa5' * 130
        else:
            expected = b'.' if position == 0 else b'..'
            assert r[10] in (0, 1) and data[0] == 4 and data[1:len(expected) + 2] == expected + b'\0'
        next_position = struct.unpack('<I', m.read(handle + 48, 4))[0]
        assert next_position == position + (lock_result == 0)
        cases.append(dict(kind='native_directory', position=position, lock_result=lock_result,
                          returned=r[10], next_position=next_position, output_guards_preserved=True))


def candidate_cases(machine, names, cases):
    m = machine
    m.breaks([m.stop, 0xa00268c4])
    for udp in (0, 1):
        r = m.start(names['listener'], {10:18081 if not udp else 8767, 11:udp})
        assert (r[32], r[10], r[11], r[12]) == (0xa00268c4, 2, 0x801 + udp, 0)
        cases.append(dict(kind='candidate_listener', udp=bool(udp), socket_type=r[11]))

    # Exercise the actual ROM-to-payload jump. An unrelated callback must call
    # native registration then return, without allocating or starting services.
    site, native_registration = BASE + 0x79bce, 0xa01b3e50
    m.breaks([site + 8, native_registration])
    arguments = {10:0xa81d0000, 11:0xa8001234, 12:0, 13:0xa81d1000}
    r = m.start(site, arguments)
    assert r[32] == native_registration
    assert all(r[n] == value for n, value in arguments.items())
    m.reg(10, 0)
    r = m.run(r[1])
    assert r[32] == site + 8 and r[2] == m.sp
    cases.append(dict(kind='candidate_ui_registration_hook', native_arguments_preserved=True,
                      unmatched_callback_returned=True, stack_preserved=True))

    # Intercept only the heavy C++ menu handlers, then execute their real stub
    # continuations back into the exact next original instruction.
    sites = [(0xc3cc4, 'ap01SettingsRegister0041', 1),
             (0xc3cd2, 'ap01SettingsRegister0041', 1),
             (0xc3ce0, 'ap01SettingsRegister0041', 11),
             (0xc3df4, 'ap01SettingsList0041', 0)]
    s1, s3, returned_list = 0xa81d4000, 0xa81d5000, 0xa81d6000
    for index, (offset, handler, event_filter) in enumerate(sites):
        site = BASE + offset
        m.breaks([site + (10 if index == 3 else 8), names[handler]])
        m.write(s3, bytes(32))
        values = {8:0xa81d7000, 9:s1, 19:s3, 10:0xa81d0000,
                  11:0xa8001234, 12:event_filter, 13:0}
        r = m.start(site, values)
        assert r[32] == names[handler] and r[10] == values[10]
        if index != 3:
            assert (r[11], r[12], r[13]) == (values[11], event_filter, 0)
        m.reg(10, returned_list)
        r = m.run(r[1])
        assert r[32] == site + (10 if index == 3 else 8)
        assert r[2] == m.sp and r[8] == values[8] and r[9] == s1 and r[19] == s3
        expected_a1 = s1 + 0x6be if index < 2 else 0xa00fd000 if index == 2 else 0
        assert r[11] == expected_a1
        if index == 3:
            assert struct.unpack('<I', m.read(s3 + 8, 4))[0] == returned_list
        cases.append(dict(kind='candidate_menu_continuation', index=index,
                          a1=hex(r[11]), return_pc=hex(r[32]), stack_and_saved_registers_preserved=True))

    # NULL must return. Non-NULL must replay the exact four stack instructions
    # and resume in the untouched original timer function before any dereference.
    timer, continuation = 0xa007deec, 0xa007def4
    m.breaks([m.stop, continuation])
    r = m.start(timer, {8:0x12345678, 9:0x3456789a, 10:0})
    m.returned(r)
    assert (r[8], r[9]) == (0x12345678, 0x3456789a)
    cases.append(dict(kind='candidate_timer_null', returned=True, stack_preserved=True))
    r = m.start(timer, {8:0x12345678, 9:0x3456789a, 10:0xa81d0000})
    assert r[32] == continuation and r[2] == m.sp - 16 and r[10] == 0xa81d0000
    assert struct.unpack('<III', m.read(m.sp - 12, 12)) == (0x3456789a, 0x12345678, m.stop)
    cases.append(dict(kind='candidate_timer_nonnull', original_prologue_replayed=True,
                      continuation=hex(continuation)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu', type=Path)
    parser.add_argument('--expected-engine-sha256')
    parser.add_argument('--support-dir', type=Path)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--expected-rom-sha256', required=True)
    parser.add_argument('--elf', type=Path)
    parser.add_argument('--expected-elf-sha256')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    rom = args.rom.read_bytes()
    names = static_audit(rom, args.expected_rom_sha256, args.elf, args.expected_elf_sha256)
    if args.check_only:
        print(json.dumps(dict(passed=True, static_only=True, rom_sha256=sha(args.rom),
                              native_anchors=len(PINNED_NATIVE), candidate_symbols=bool(names))))
        return
    assert all((args.qemu, args.expected_engine_sha256, args.support_dir, args.output))
    assert not args.output.exists() and args.output.parent.is_dir()
    assert sha(args.qemu) == args.expected_engine_sha256
    support_path = args.support_dir / 'run-qemu-ap01.py'
    sys.path.insert(0, str(args.support_dir.resolve()))
    support = load('qemu_support_0055', support_path)
    report = dict(passed=False, rom_sha256=sha(args.rom), elf_sha256=sha(args.elf) if args.elf else None,
                  engine_sha256=sha(args.qemu), support_sha256=sha(support_path),
                  script_sha256=sha(Path(__file__)), cpu=CPU, cases=[],
                  device_accessed=False, full_rom_boot=False, scheduler_executed=False,
                  original_lvgl_ui_executed=False, real_flash_or_network_verified=False,
                  substitutes=['kernel socket setup allocation', 'empty TCP accept backlog',
                               'synthetic TCB/TLS records', 'mount/directory state and lock outcomes',
                               'heavy menu C++ handlers and native object event registration'],
                  limitations=['No complete ROM boot or hardware acceptance.',
                               'Candidate cases execute real jumps/stubs but intercept heavy UI/kernel handlers.',
                               'No scheduler, radio, Flash writes, or physical LCD/rotary input.'])
    try:
        with tempfile.TemporaryDirectory(prefix='ap01-0055-native-') as folder:
            socket = Path(folder) / 'gdb.sock'
            with args.output.with_suffix('.log').open('x') as log:
                process = subprocess.Popen([str(args.qemu), '-M', 'ap01', '-cpu', CPU,
                    '-kernel', str(args.rom), '-S', '-display', 'none', '-serial', 'none',
                    '-monitor', 'none', '-d', 'guest_errors,int', '-gdb', f'unix:{socket},server=on,wait=off'],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=log, preexec_fn=support.child_limits)
                connection = None
                try:
                    deadline = time.monotonic() + 20
                    connection = support.connect(socket, process, deadline)
                    rsp = support.RSP(connection, deadline)
                    rsp.request('?')
                    machine = Machine(rsp)
                    for address, expected in PINNED_NATIVE.items():
                        assert machine.read(address, len(bytes.fromhex(expected))) == bytes.fromhex(expected)
                    if names:
                        for address in names.values():
                            if BASE + OFFSET <= address < BASE + len(rom):
                                assert machine.read(address, 16) == rom[address - BASE:address - BASE + 16]
                    unsigned_ota_cases(machine, rom, report['cases'])
                    native_cases(machine, report['cases'])
                    if names:
                        candidate_cases(machine, names, report['cases'])
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
        report['passed'] = True
    except Exception as error:
        report['error'] = f'{type(error).__name__}: {error}'
        raise
    finally:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))


if __name__ == '__main__':
    main()
