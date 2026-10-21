#!/usr/bin/env python3
"""Execute original 0041 slider bytes with synthetic window/LVGL leaves.

Requires the existing Linux AP01 QEMU engine. No device/network access beyond
private Unix debugger sockets. This does not execute LVGL allocation or boot UI.
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

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('ap01_probe', Path(__file__).with_name('run-qemu-ap01.py'))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
SHA = '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'
WIN, STOP, STACK, ANIM = 0x62fd0000, 0x62fd8000, 0x63030000, 0x62fd9000
SCREEN, OUT = 0x62fd2000, 0x62fd3000
SLIDER, LEFT, RIGHT, READY = 0xa00b3106, 0xa00b3080, 0xa00b30c0, 0xa00ab628


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qemu', type=Path, required=True)
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if a.output.exists() or not a.output.parent.is_dir():
        p.error('output must be new in an existing directory')
    image = a.image.read_bytes()
    assert hashlib.sha256(image).hexdigest() == SHA, 'original 0041 identity'
    report = dict(original_sha256=SHA, engine_sha256=hashlib.sha256(a.qemu.read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='original slider/move/ready bytes; synthetic objects and LVGL leaves',
                  allocation_executed=False, full_ui_executed=False, hardware_verified=False, cases=[])
    with tempfile.TemporaryDirectory(prefix='ap01-screen-') as tmp:
        socket_path = Path(tmp) / 'gdb'
        with (Path(tmp) / 'qemu.log').open('w') as log:
            command = [str(a.qemu.resolve()), '-M', 'ap01', '-cpu', 'rv32',
                       '-kernel', str(a.image.resolve()), '-S', '-display', 'none',
                       '-serial', 'none', '-monitor', 'none',
                       '-gdb', f'unix:{socket_path},server=on,wait=off']
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                                       preexec_fn=probe.child_limits)
            sock = None
            try:
                deadline = time.monotonic() + 40
                sock = probe.connect(socket_path, process, deadline)
                rsp = probe.RSP(sock, deadline)
                rsp.request('?')

                def put(address, data):
                    assert rsp.request(f'M{address:x},{len(data):x}:{data.hex()}') == 'OK'

                def read(address, size):
                    return bytes.fromhex(rsp.request(f'm{address:x},{size:x}'))

                def word(address, value=None):
                    if value is None:
                        return int.from_bytes(read(address, 4), 'little')
                    put(address, struct.pack('<I', value & 0xffffffff))

                def reg(index, value):
                    assert rsp.request(f'P{index:x}={struct.pack("<I", value & 0xffffffff).hex()}') == 'OK'

                leaves = [0xa00dd144, 0xa00dcee4, 0xa00d8c12, 0xa01b2eb4,
                          0xa008df3c, 0xa008bf6e, 0xa008b51a, 0xa008bd70, STOP, 0xa005d0ea]
                for address in leaves:
                    assert rsp.request(f'Z0,{address:x},2') == 'OK'
                count, animation, resumed = 9, None, []
                children = [0x62fe0000 + 0x100 * i for i in range(17)]

                def call(address, *args, expected_stop=STOP):
                    nonlocal animation
                    reg(1, STOP)
                    reg(2, STACK)
                    for i, value in enumerate(args):
                        reg(10 + i, value)
                    reg(32, address)
                    for _ in range(80):
                        stop = rsp.request('c')
                        assert stop.startswith(('T', 'S')), stop
                        registers = struct.unpack('<33I', bytes.fromhex(rsp.request('g'))[:132])
                        pc, arg0, arg1 = registers[32], registers[10], registers[11]
                        if pc == expected_stop:
                            assert registers[2] == STACK, 'stack not restored'
                            return
                        assert pc in leaves, hex(pc)
                        result = 0
                        if pc == 0xa00dd144:
                            assert arg0 in (WIN, SCREEN)
                            result = count if arg0 == WIN else 1
                        elif pc == 0xa00dcee4:
                            assert arg0 in (WIN, SCREEN)
                            assert arg1 < (count if arg0 == WIN else 1), (hex(arg0), arg1, count)
                            result = children[arg1] if arg0 == WIN else WIN
                        elif pc == 0xa00d8c12:
                            assert arg0 in children[:count]
                            word(arg0 + 0x20, arg1)
                        elif pc == 0xa008df3c:
                            put(arg0, bytes(96))
                        elif pc == 0xa008bf6e:
                            animation = read(arg0, 64)
                        elif pc == 0xa008bd70:
                            resumed.append(arg0)
                        reg(10, result)
                        reg(32, registers[1])
                    raise AssertionError('unexpected call loop')

                for extra in (0, 1, 8):
                    count = 9 + extra
                    put(WIN, bytes(128))
                    word(WIN + 0x3c, 1)
                    for i in range(count):
                        tag = 0x62fd4000 + i * 16
                        word(children[i] + 0x10, tag)
                        word(tag, i + 1 if i < 9 else 0x80 + i - 9)
                        word(tag + 4, 0x62fd6000 + i * 16)
                    # Screen-level window-kind search never traverses win pages.
                    call(0xa00a7334, SCREEN, 1, OUT)
                    assert word(OUT) == WIN
                    # Actual page-tag search safely skips registered external tags.
                    call(0xa00a72ae, WIN, 0xfe, OUT, OUT + 4)
                    if extra:
                        call(0xa00a72ae, WIN, 0x80 + extra - 1, OUT, OUT + 4)
                        assert word(OUT) == children[count - 1]
                        assert word(OUT + 4) == 0x62fd6000 + (count - 1) * 16
                    # Real ready callback dereferences Pet's tag -> state -> GIF.
                    word(children[7] + 0x10, 0x62fd1000)
                    word(0x62fd1004, 0x62fd1100)
                    word(0x62fd1100, 0x62fd1200)
                    word(0x62fd125c, 1)
                    word(0x62fd1260, 0x62fd1300)
                    word(WIN + 0x34, 7)
                    word(WIN + 0x38, 6)
                    put(WIN + 0x4c, b'\1')
                    order = [7] + list(range(9, count)) + [6]
                    for direction, targets in ((2, order[1:]), (1, list(reversed(order[:-1])))):
                        for target in targets:
                            old = word(WIN + 0x34)
                            animation = None
                            call(SLIDER, WIN, target, direction)
                            assert word(WIN + 0x34) == target and word(WIN + 0x38) == old
                            assert read(WIN + 0x4c, 1) == b'\0'
                            assert animation is not None
                            fields = struct.unpack('<16I', animation)
                            callback = LEFT if direction == 2 else RIGHT
                            assert (fields[0], fields[1], fields[4], fields[7], fields[12]) == (WIN, callback, READY, WIN, 300)
                            for value in (0, 160, 320):
                                call(callback, WIN, value)
                                expected = (value - 320, value) if direction == 2 else (320 - value, -value)
                                actual = tuple(struct.unpack('<i', read(children[i] + 0x20, 4))[0] for i in (target, old))
                                assert actual == expected, (actual, expected)
                            put(ANIM, animation)
                            call(READY, ANIM)
                            assert read(WIN + 0x4c, 1) == b'\1'
                            report['cases'].append(dict(children=count, source=old, target=target,
                                                        direction=direction, samples=[0, 160, 320]))
                    # Same-page request must not start another animation.
                    animation = None
                    call(SLIDER, WIN, word(WIN + 0x34), 2)
                    assert animation is None
                    # Instant switch and stale previous-page cleanup also accept appended index.
                    call(SLIDER, WIN, count - 1, 0)
                    assert word(WIN + 0x34) == count - 1
                    assert word(children[count - 1] + 0x20) == 0
                assert len(resumed) == 3 and set(resumed) == {0x62fd1300}
                # Early append before the stock child-count initialization alters
                # the seed active index. Prefer the existing later registration hook.
                reg(20, WIN)
                call(0xa005d0b4, expected_stop=0xa005d0ea)
                assert word(WIN + 0x34) == 16
                report.update(passed=True, pet_resume_calls=len(resumed), same_page_checked=True,
                              instant_switch_checked=True, screen_window_lookup_checked=True,
                              external_tag_lookup_checked=True, early_append_seed_active=16)
            finally:
                if sock:
                    sock.close()
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], transitions=len(report['cases']), output=str(a.output))))


if __name__ == '__main__':
    main()
