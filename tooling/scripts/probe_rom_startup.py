"""Bounded execution of original 0031 entry; no patches, MMIO stubs or devices."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--deps', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        parser.error('output must be a new file in an existing directory')
    image = args.image.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if len(image) != 6804520 or digest != '8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb':
        parser.error('only the exact original 0031 image is supported')
    sys.path.insert(0, str(args.deps.resolve()))
    import unicorn as u
    from unicorn.riscv_const import UC_RISCV_REG_PC, UC_RISCV_REG_SP

    uc = u.Uc(u.UC_ARCH_RISCV, u.UC_MODE_RISCV32)
    base, entry = 0x9ffff000, 0xa0000000
    uc.mem_map(base, (len(image) + 4095) & ~4095, u.UC_PROT_ALL)
    uc.mem_write(base, image)
    uc.mem_protect(base, (len(image) + 4095) & ~4095, u.UC_PROT_READ | u.UC_PROT_EXEC)
    # Candidate BL616-family RAM windows, zero-filled by the engine.
    # These are not a captured AP01 boot state or peripheral models.
    uc.mem_map(0x62fc0000, 0x78000, u.UC_PROT_READ | u.UC_PROT_WRITE)
    uc.mem_map(0xa8000000, 0x400000, u.UC_PROT_READ | u.UC_PROT_WRITE)
    trace = deque(maxlen=32)
    count = 0
    stop = {}

    def instruction(engine, address, size, unused):
        nonlocal count
        count += 1
        trace.append({'pc': hex(address), 'size': size,
                      'bytes': bytes(engine.mem_read(address, min(size, 4))).hex()})

    def memory_fault(engine, access, address, size, value, unused):
        stop.update(reason='unmapped-or-protected-memory', access=access,
                    address=hex(address), size=size, pc=hex(engine.reg_read(UC_RISCV_REG_PC)))
        return False

    def interrupt(engine, number, unused):
        stop.update(reason='cpu-exception', engine_interrupt_number=number,
                    pc=hex(engine.reg_read(UC_RISCV_REG_PC)))
        engine.emu_stop()

    uc.hook_add(u.UC_HOOK_CODE, instruction)
    uc.hook_add(u.UC_HOOK_MEM_INVALID, memory_fault)
    uc.hook_add(u.UC_HOOK_INTR, interrupt)
    try:
        uc.emu_start(entry, 0xffffffff, timeout=2_000_000, count=100_000)
    except u.UcError as exc:
        stop['engine_error'] = str(exc)
    if not stop:
        stop['reason'] = 'execution-budget-or-stop-address'
    assert hashlib.sha256(args.image.read_bytes()).hexdigest() == digest
    report = {
        'image_sha256': digest, 'engine': f'Unicorn {u.__version__}',
        'base': hex(base), 'entry': hex(entry), 'instructions_observed': count,
        'pc': hex(uc.reg_read(UC_RISCV_REG_PC)), 'sp': hex(uc.reg_read(UC_RISCV_REG_SP)),
        'stop': stop, 'last_instructions': list(trace), 'full_rom_boot_verified': False,
        'assumptions': ['generic RV32 engine CPU initial state', 'zero-filled candidate RAM windows',
                        'application entry, not chip reset/Boot2'],
        'not_modeled': ['vendor CSRs/extensions', 'BootROM services', 'timers/interrupt controller',
                        'clock/reset/flash controllers', 'display/DMA', 'radio', 'board peripherals'],
        'patches': [], 'mmio_stubs': [], 'source_unchanged': True,
    }
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
