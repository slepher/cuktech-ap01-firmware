"""Incremental AP01 0031 functional hardware model; unknown hardware stops."""
import argparse
from collections import Counter, deque
import ctypes
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
SHA256 = '8a721fc8ef25458d415b2460e4a251e0503a82f7743fdff85b12612190e5c1cb'
BASE, ENTRY = 0x9ffff000, 0xa0000000
MASK32 = 0xffffffff


def memory_instruction(word):
    """Decode RV32 XTheadMemIdx byte/halfword/word operations only."""
    top, funct = word >> 27, (word >> 12) & 7
    width = (top >> 2) & 3
    if word & 0x7f != 0xb or funct not in (4, 5) or width == 3:
        return None
    if funct == 5 and top & 16:
        return None
    if top not in (0, 4, 8, 16, 20, 1, 3, 5, 7, 9, 11, 17, 19, 21, 23):
        return None  # Do not accept RV64-only unsigned-index/LWU encodings.
    rd, rs1, rs2, shift = (word >> 7) & 31, (word >> 15) & 31, (word >> 20) & 31, (word >> 25) & 3
    inc = bool(top & 1)
    if inc and funct == 4 and rd == rs1:
        return None  # Reserved destination/base alias for incrementing loads.
    return dict(rd=rd, base=rs1, index=rs2, shift=shift, size=1 << width,
                load=funct == 4, signed=not bool(top & 16),
                update=('post' if top & 2 else 'pre') if inc else None)


def csr_operation(word, old, source):
    """Zicsr RMW; None means no write (CSRRS/CSRRC with rs1/uimm=0)."""
    funct = (word >> 12) & 7
    rs1 = (word >> 15) & 31
    operand = rs1 if funct & 4 else source
    if funct in (1, 5):
        new = operand
    elif funct in (2, 6):
        new = old | operand if rs1 else None
    elif funct in (3, 7):
        new = old & ~operand if rs1 else None
    else:
        raise ValueError('not a Zicsr instruction')
    return old, None if new is None else new & MASK32


class AP01:
    def __init__(self, image, mhint_reset=0):
        import unicorn as u
        from unicorn import riscv_const as r
        self.u, self.r = u, r
        self.uc = u.Uc(u.UC_ARCH_RISCV, u.UC_MODE_RISCV32)
        self.image = image
        self.ram = ctypes.create_string_buffer(0x78000)
        self.psram = ctypes.create_string_buffer(0x400000)
        self.ram_ranges = []
        for address in (0x20fc0000, 0x22fc0000, 0x60fc0000, 0x62fc0000):
            self.uc.mem_map_ptr(address, len(self.ram), u.UC_PROT_ALL,
                                ctypes.addressof(self.ram))
            self.ram_ranges.append((address, address + len(self.ram)))
        for address in (0x88000000, 0xa8000000, 0xd8000000):
            self.uc.mem_map_ptr(address, len(self.psram), u.UC_PROT_ALL,
                                ctypes.addressof(self.psram))
            self.ram_ranges.append((address, address + len(self.psram)))
        size = (len(image) + 4095) & ~4095
        self.uc.mem_map(BASE, size, u.UC_PROT_ALL)
        self.uc.mem_write(BASE, image)
        self.uc.mem_protect(BASE, size, u.UC_PROT_READ | u.UC_PROT_EXEC)
        # SDK identifies MHINT as cache preload/AMR hints. Coherent functional
        # memory has no modeled cache latency. Initial value is explicit input,
        # not a claim about the physical Boot2 handoff/reset value.
        self.csrs = {0x7c5: mhint_reset & MASK32, 0x305: 0, 0x307: 0,
                     0x7c0: 0, 0x7c1: 0, 0x7e1: 0}
        # SDK reset values; these model configuration latches, not a boot dump.
        self.mmio = {0x2000e500: 0x21, 0x2000e504: 0,
                     0x200053a0: 0xffff, 0x200053a8: 0xffff,
                     0x20005040: 0xffff, 0x2000504c: 0x3ff,
                     0x2000b070: 0}
        self.mmio_masks = {0x2000e500: 0x3f, 0x2000e504: 0x7f,
                           0x200053a0: 0x0f0fffff, 0x20005040: 0xffcfffff,
                           0x2000504c: 0x03ff03ff, 0x2000b070: 0xfe0000fb}
        # GPIO41..52 reset: Schmitt enabled, input disabled (SDK glb_reg.h).
        self.mmio.update({0x20000968 + 4 * i: 2 for i in range(12)})
        self.mmio.update({0x20000154: 0x98543210, 0x20000158: 0xba76})
        self.mmio_masks[0x20000158] = 0xffff
        self.mmio[0x2000060c] = 3
        self.mmio_masks[0x2000060c] = 0xf
        self.mmio[0x20000090] = 0xf
        self.mmio_masks[0x20000090] = 0x00ffff0f
        self.mmio[0x2000f014] = 0x03010005
        self.mmio_masks[0x2000f014] = 0x0ff500ff
        self.mmio[0x2000f02c] = 0xa
        self.mmio_masks[0x2000f02c] = 0x1f
        self.mmio[0x2000f030] = 0xaa0a0020
        self.mmio_masks[0x2000f030] = 0xff0f803f
        # EF_IF_CTRL_0 reset: both autoload-done bits, auto-read enable,
        # interrupt-clear bit. OTP contents/programming remain unsupported.
        self.mmio[0x20056800] = 0x240003
        self.mmio_masks[0x20056800] = 0xff6fff78
        self.uc.mmio_map(0x20056000, 0x1000, self._mmio_read, 0x20056000,
                         self._mmio_write, 0x20056000)
        self.uc.mmio_map(0x2000f000, 0x1000, self._mmio_read, 0x2000f000,
                         self._mmio_write, 0x2000f000)
        self.uc.mmio_map(0x20000000, 0x1000, self._mmio_read, 0x20000000,
                         self._mmio_write, 0x20000000)
        self.mmio_masks.update({0x20000968 + 4 * i: 0x3f for i in range(12)})
        for base in (0x20005000, 0x2000b000):
            self.uc.mmio_map(base, 0x1000, self._mmio_read, base,
                             self._mmio_write, base)
        # CLICINFO: 80 IRQ slots from BL616 IRQn_LAST; 4 implemented control
        # bits is an explicit integration choice, not measured silicon state.
        self.mmio.update({0xe0800000: 0, 0xe0800004: (4 << 21) | 80})
        self.mmio.update({0xe0801000 + 4 * i: 0 for i in range(80)})
        self.uc.mmio_map(0xe0800000, 0x2000, self._mmio_read, 0xe0800000,
                         self._mmio_write, 0xe0800000)
        # Eight SYSMAP address/attribute pairs; memory is functionally coherent.
        self.mmio.update({0xeffff000 + 4 * i: 0 for i in range(16)})
        self.uc.mmio_map(0xeffff000, 0x1000, self._mmio_read, 0xeffff000,
                         self._mmio_write, 0xeffff000)
        self.uc.mmio_map(0x2000e000, 0x1000, self._mmio_read, 0x2000e000,
                         self._mmio_write, 0x2000e000)
        self.trace = deque(maxlen=64)
        self.events = []
        self.event_counts = Counter()
        self.count = 0
        self.pending = None
        self.stop = None
        self.uc.hook_add(u.UC_HOOK_CODE, self._instruction)
        self.uc.hook_add(u.UC_HOOK_MEM_INVALID, self._memory_fault)
        self.uc.hook_add(u.UC_HOOK_INTR, self._exception)

    def reg(self, index):
        return self.uc.reg_read(self.r.UC_RISCV_REG_X0 + index)

    def setreg(self, index, value):
        if index:
            self.uc.reg_write(self.r.UC_RISCV_REG_X0 + index, value & MASK32)

    def event(self, kind, **data):
        self.event_counts[kind] += 1
        if len(self.events) < 512:
            self.events.append(dict(kind=kind, **data))

    def _instruction(self, uc, address, size, unused):
        self.count += 1
        raw = bytes(uc.mem_read(address, min(size, 4)))
        self.trace.append(dict(pc=hex(address), size=size, bytes=raw.hex()))
        word = int.from_bytes(raw, 'little')
        if size == 4 and word & 0x7f == 0x73 and ((word >> 12) & 7) in (1, 2, 3, 5, 6, 7):
            csr = word >> 20
            if csr in self.csrs:
                self.pending = ('csr', address, word)
        elif size == 4 and word & 0xffc0707f == 0xac000077:
            self.pending = ('insb', address, word)
        elif size == 4 and word & 0xf800707f == 0x0000100b:
            self.pending = ('addsl', address, word)
        elif (size == 4 and word & 0x707f in (0x200b, 0x300b) and
              (word >> 26) < 32 and ((word >> 20) & 63) <= (word >> 26)):
            self.pending = ('extract', address, word)
        elif size == 4 and memory_instruction(word) is not None:
            self.pending = ('memory', address, word)
        elif size == 4 and word in (0x0010000b, 0x0020000b, 0x0030000b,
                                    0x0100000b, 0x0110000b,
                                    0x0180000b, 0x0190000b, 0x01a0000b, 0x01b0000b):
            self.pending = ('cache-sync', address, word)
            uc.emu_stop()
            return
        if self.pending:
            self._complete()
            if self.stop:
                uc.emu_stop()

    def memory(self, address, size, value=None):
        # Host uc.mem_write bypasses guest protections. Check explicitly before
        # using it to implement an instruction; never write the read-only XIP.
        address &= MASK32
        register = address & ~3
        if register in self.mmio:
            if value is None:
                return self._mmio_read(self.uc, address, size, 0).to_bytes(size, 'little')
            self._mmio_write(self.uc, address, size, value, 0)
            return
        ram = any(start <= address and address + size <= end for start, end in self.ram_ranges)
        rom = BASE <= address and address + size <= BASE + len(self.image)
        if not ram and not (rom and value is None):
            raise ValueError(f'unsupported instruction memory access at {address:#x}')
        if value is None:
            return bytes(self.uc.mem_read(address, size))
        self.uc.mem_write(address, (value & ((1 << (size * 8)) - 1)).to_bytes(size, 'little'))

    def _memory_fault(self, uc, access, address, size, value, unused):
        self.stop = dict(reason='unsupported-memory', access=access,
                         address=hex(address), size=size,
                         pc=hex(uc.reg_read(self.r.UC_RISCV_REG_PC)))
        return False

    def _mmio_read(self, uc, offset, size, base):
        address = base + offset
        register, shift = address & ~3, (address & 3) * 8
        if size not in (1, 2, 4) or (address & 3) + size > 4 or register not in self.mmio:
            self.stop = dict(reason='unsupported-mmio-read', address=hex(address), size=size,
                             pc=hex(uc.reg_read(self.r.UC_RISCV_REG_PC)))
            uc.emu_stop()
            return 0  # Required callback value; run is failed, not successful.
        full_value = self.mmio[register]
        if register == 0x20000090:
            full_value = (full_value & ~0xc0) | ((self.mmio[0x2000f030] & 3) << 6)
        value = (full_value >> shift) & ((1 << (size * 8)) - 1)
        self.event('mmio-read', address=hex(address), value=hex(value))
        return value

    def _mmio_write(self, uc, offset, size, value, base):
        address = base + offset
        register, shift = address & ~3, (address & 3) * 8
        if register == 0x20056800 and value << shift & 0x10:
            self.stop = dict(reason='otp-transfer-not-modeled', address=hex(address),
                             value=hex(value), pc=hex(uc.reg_read(self.r.UC_RISCV_REG_PC)))
            uc.emu_stop()
            return
        if (size not in (1, 2, 4) or (address & 3) + size > 4 or
                register not in self.mmio or register == 0xe0800004):
            self.stop = dict(reason='unsupported-mmio-write', address=hex(address), size=size,
                             value=hex(value), pc=hex(uc.reg_read(self.r.UC_RISCV_REG_PC)))
            uc.emu_stop()
            return
        mask = (((1 << (size * 8)) - 1) << shift) & self.mmio_masks.get(register, MASK32)
        self.mmio[register] = (self.mmio[register] & ~mask) | ((value << shift) & mask)
        self.event('mmio-write', address=hex(address), value=hex(value))

    def _exception(self, uc, number, unused):
        self.stop = dict(reason='cpu-exception', engine_interrupt_number=number,
                         pc=hex(uc.reg_read(self.r.UC_RISCV_REG_PC)))
        uc.emu_stop()

    def _complete(self):
        kind, address, word = self.pending
        self.pending = None
        if kind == 'csr':
            csr, rd, rs1 = word >> 20, (word >> 7) & 31, (word >> 15) & 31
            old, new = csr_operation(word, self.csrs[csr], self.reg(rs1))
            if new is not None:
                self.csrs[csr] = new
            self.setreg(rd, old)
            self.event('csr', pc=hex(address), csr=hex(csr), old=hex(old),
                       write=None if new is None else hex(new))
        elif kind == 'insb':
            rd, rs1, byte = (word >> 7) & 31, (word >> 15) & 31, (word >> 20) & 3
            shift = byte * 8
            self.setreg(rd, (self.reg(rd) & ~(0xff << shift)) |
                        ((self.reg(rs1) & 0xff) << shift))
            self.event('insb', pc=hex(address), byte=byte)
        elif kind == 'addsl':
            rd, rs1, rs2 = (word >> 7) & 31, (word >> 15) & 31, (word >> 20) & 31
            shift = (word >> 25) & 3
            self.setreg(rd, self.reg(rs1) + (self.reg(rs2) << shift))
            self.event('addsl', pc=hex(address), shift=shift)
        elif kind == 'extract':
            msb, lsb = word >> 26, (word >> 20) & 63
            width = msb - lsb + 1
            value = (self.reg((word >> 15) & 31) >> lsb) & ((1 << width) - 1)
            if (word >> 12) & 7 == 2 and value & (1 << (width - 1)):
                value -= 1 << width
            self.setreg((word >> 7) & 31, value)
            self.event('extract', pc=hex(address), msb=msb, lsb=lsb)
        elif kind == 'memory':
            insn = memory_instruction(word)
            base = self.reg(insn['base'])
            index = insn['index']
            if insn['update']:
                offset = (index if index < 16 else index - 32) << insn['shift']
            else:
                offset = self.reg(index) << insn['shift']
            effective = base if insn['update'] == 'post' else (base + offset) & MASK32
            try:
                if insn['load']:
                    raw = self.memory(effective, insn['size'])
                    if self.stop:
                        return
                    self.setreg(insn['rd'], int.from_bytes(raw, 'little', signed=insn['signed']))
                else:
                    self.memory(effective, insn['size'], self.reg(insn['rd']))
                    if self.stop:
                        return
            except (ValueError, self.u.UcError) as exc:
                self.stop = dict(reason='unsupported-custom-memory', pc=hex(address),
                                 address=hex(effective), size=insn['size'], detail=str(exc))
                return
            if insn['update']:
                self.setreg(insn['base'], base + offset)
            self.event('memory', pc=hex(address), address=hex(effective),
                       size=insn['size'], load=insn['load'], update=insn['update'])
        elif kind == 'cache-sync':
            # RAM/XIP are coherent in this functional model; no dirty cache
            # lines exist. Invalidate translated code on I-cache maintenance.
            if word in (0x0100000b, 0x0110000b):
                self.uc.ctl_flush_tb()
            self.event('cache-sync', pc=hex(address), instruction=hex(word))
        self.uc.reg_write(self.r.UC_RISCV_REG_PC, address + 4)

    def run(self, count=1_000_000, seconds=10, entry=ENTRY):
        deadline = time.monotonic() + seconds
        self.uc.reg_write(self.r.UC_RISCV_REG_PC, entry)
        while self.count < count and time.monotonic() < deadline and not self.stop:
            pc = self.uc.reg_read(self.r.UC_RISCV_REG_PC)
            try:
                self.uc.emu_start(pc, 0xffffffff, count=count - self.count,
                                  timeout=max(1, int((deadline - time.monotonic()) * 1_000_000)))
            except self.u.UcError as exc:
                if not self.stop:
                    self.stop = dict(reason='engine-error')
                self.stop['engine_error'] = str(exc)
            if self.pending:
                self._complete()
            elif not self.stop:
                self.stop = dict(reason='execution-budget-or-stop-address')
        if not self.stop:
            self.stop = dict(reason='execution-budget')
        copied = []
        for address, offset, size in ((0x62fc1100, 0x1c14, 0x1bc0),
                                      (0x62fc2cc0, 0x37d4, 0x2928)):
            if offset + size <= len(self.image):
                observed = bytes(self.uc.mem_read(address, size))
                copied.append(dict(address=hex(address), image_offset=hex(offset), size=size,
                                   matches_image=observed == self.image[offset:offset + size],
                                   sha256=hashlib.sha256(observed).hexdigest()))
        return dict(instructions_observed=self.count,
                    pc=hex(self.uc.reg_read(self.r.UC_RISCV_REG_PC)),
                    sp=hex(self.reg(2)), stop=self.stop,
                    last_instructions=list(self.trace), events=self.events,
                    event_counts=dict(self.event_counts),
                    csrs={hex(k): hex(v) for k, v in self.csrs.items()},
                    ram_copy_observations=copied,
                    full_rom_boot_verified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--deps', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mhint-reset', type=lambda s: int(s, 0), default=0)
    parser.add_argument('--count', type=int, default=1_000_000)
    parser.add_argument('--seconds', type=float, default=10)
    args = parser.parse_args()
    if args.output.exists() or not args.output.parent.is_dir():
        parser.error('output must be a new file in an existing directory')
    if not 0 < args.count <= 100_000_000 or not 0 < args.seconds <= 60:
        parser.error('count must be 1..100000000 and seconds 0..60')
    image = args.image.read_bytes()
    if len(image) != 6804520 or hashlib.sha256(image).hexdigest() != SHA256:
        parser.error('only the exact original 0031 image is supported')
    sys.path.insert(0, str(args.deps.resolve()))
    model = AP01(image, args.mhint_reset)
    report = model.run(args.count, args.seconds)
    report.update(image_sha256=SHA256, engine=f'Unicorn {model.u.__version__}',
                  mhint_initial=args.mhint_reset, source_unchanged=True,
                  assumptions=['functional coherent memory, no cache timing',
                               'zero-filled RAM; no captured Boot2 state'],
                  patches=[], function_stubs=[])
    assert hashlib.sha256(args.image.read_bytes()).hexdigest() == SHA256
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({key: report[key] for key in
                      ('instructions_observed', 'pc', 'stop', 'event_counts', 'csrs',
                       'full_rom_boot_verified')}, indent=2))


if __name__ == '__main__':
    main()
