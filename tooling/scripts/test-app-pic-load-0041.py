"""S1 offline experiment: normalize internal pointers and execute at two RV32 bases.

Requires pyelftools==0.32 and unicorn==2.1.4. Parses trusted compiler ELF on the
host only; no APX2 format, production loader, firmware addresses or device I/O.
"""
from collections import Counter
from pathlib import Path
import argparse
import copy
import hashlib
import json
import struct
import subprocess

SCRIPT = '''OUTPUT_ARCH(riscv)
ENTRY(probe_entry)
SECTIONS {
 . = probe_base;
 .text : { KEEP(*(.text.probe_entry)) *(.text .text.*) }
 . = ALIGN(16);
 .rodata : { *(.rodata .rodata.* .srodata .srodata.*) *(.data.rel.ro*) }
 . = ALIGN(16);
 .data : { *(.data .data.* .sdata .sdata.*) }
 .bss (NOLOAD) : { *(.bss .bss.* .sbss .sbss.* COMMON) }
 .forbidden : { *(.got*) *(.init_array*) *(.fini_array*) *(.tdata*) *(.tbss*) }
 ASSERT(SIZEOF(.forbidden)==0,"Unexpected GOT/implicit initializer/TLS in probe")
 /DISCARD/ : { *(.comment .note* .eh_frame* .riscv.attributes) }
}
'''


def extract(path, allow_differences=False):
    from elftools.elf.elffile import ELFFile
    from elftools.elf.relocation import RelocationSection
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        assert elf.elfclass == 32 and elf.little_endian and elf['e_machine'] == 'EM_RISCV'
        sections = [s for s in elf.iter_sections() if s['sh_flags'] & 2 and s['sh_size']]
        assert all(s.name in ('.text', '.rodata', '.data', '.bss') for s in sections)
        base = min(s['sh_addr'] for s in sections)
        memory = max(s['sh_addr'] + s['sh_size'] for s in sections) - base
        initialized = max(s['sh_addr'] + s['sh_size'] for s in sections if s['sh_type'] != 'SHT_NOBITS') - base
        image = bytearray(initialized)
        spans = {s.name: [s['sh_addr'] - base, s['sh_size']] for s in sections}
        for s in sections:
            if s['sh_type'] != 'SHT_NOBITS':
                at = s['sh_addr'] - base
                image[at:at + s['sh_size']] = s.data()
        fixes, counts = [], Counter()
        # Link-resolved, base-invariant relocations. This is only a fixture whitelist.
        # pyelftools 0.32 does not name RISC-V relocations. These IDs are also
        # checked against the saved GNU readelf output from the actual fixture.
        names = {1: 'R_RISCV_32', 16: 'R_RISCV_BRANCH', 17: 'R_RISCV_JAL', 19: 'R_RISCV_CALL_PLT', 23: 'R_RISCV_PCREL_HI20',
                 24: 'R_RISCV_PCREL_LO12_I', 25: 'R_RISCV_PCREL_LO12_S',
                 44: 'R_RISCV_RVC_BRANCH', 45: 'R_RISCV_RVC_JUMP'}
        if allow_differences:
            names.update({35: 'R_RISCV_ADD32', 39: 'R_RISCV_SUB32'})
        for rels in elf.iter_sections():
            if not isinstance(rels, RelocationSection):
                continue
            target = elf.get_section(rels['sh_info'])
            if not target['sh_flags'] & 2:
                continue
            symbols = elf.get_section(rels['sh_link'])
            previous = None
            difference = None
            for rel in rels.iter_relocations():
                if difference is not None and (rel['r_info_type'] != 39 or rel['r_offset'] != difference[0]):
                    raise ValueError('ADD32 must be immediately paired with SUB32 at the same word')
                # libgcc carries optional linker hints even under --no-relax.
                # They do not patch runtime bytes; require an adjacent instruction relocation.
                if rel['r_info_type'] == 51:
                    if (previous is None or previous['r_offset'] != rel['r_offset'] or
                            previous['r_info_type'] not in (19, 23, 24, 25) or
                            rel['r_info_sym'] != 0 or rel['r_addend'] != 0):
                        raise ValueError('Invalid RELAX hint in fixture')
                    counts['R_RISCV_RELAX'] += 1
                    previous = None
                    continue
                name = names.get(rel['r_info_type'])
                if name is None:
                    raise ValueError('Unsupported fixture relocation: ' + str(rel['r_info_type']))
                counts[name] += 1
                previous = rel
                symbol = symbols.get_symbol(rel['r_info_sym'])
                index = symbol['st_shndx']
                if not isinstance(index, int) or not elf.get_section(index)['sh_flags'] & 2:
                    raise ValueError('Non-local relocation: ' + name)
                if name in ('R_RISCV_ADD32', 'R_RISCV_SUB32'):
                    resolved = symbol['st_value'] + rel['r_addend']
                    defining = elf.get_section(index)
                    at = rel['r_offset'] - base
                    if (target.name not in ('.rodata', '.data') or at % 4 or
                            not target['sh_addr'] <= rel['r_offset'] <= target['sh_addr'] + target['sh_size'] - 4 or
                            not defining['sh_addr'] <= resolved < defining['sh_addr'] + defining['sh_size']):
                        raise ValueError('Invalid local difference relocation')
                    if name == 'R_RISCV_ADD32':
                        difference = (rel['r_offset'], resolved)
                    else:
                        if difference is None or struct.unpack_from('<I', image, at)[0] != (difference[1] - resolved) & 0xffffffff:
                            raise ValueError('Unpaired or incorrect SUB32 word')
                        difference = None
                    continue
                if name == 'R_RISCV_32':
                    offset = rel['r_offset'] - base
                    fixes.append(offset)
                    value = struct.unpack_from('<I', image, offset)[0]
                    if not base <= value < base + memory:
                        raise ValueError('External pointer in fixture')
                    struct.pack_into('<I', image, offset, value - base)
            if difference is not None:
                raise ValueError('Unpaired ADD32 at end of relocation section')
        return {'image': bytes(image), 'memory': memory, 'entry': elf['e_entry'] - base,
                'spans': spans, 'fixups': sorted(fixes), 'relocations': dict(counts)}


def load(probe, base):
    """Validate the entire tiny fixture before applying internal BASE32 fixups."""
    image, memory, spans = probe['image'], probe['memory'], probe['spans']
    if not 0 < len(image) <= memory <= 65536 or base < 0 or base % 16 or base + memory > 2**32:
        raise ValueError('image bounds')
    def inside(offset, count, names):
        return any(start <= offset and offset + count <= start + size
                   for name, (start, size) in spans.items() if name in names)
    if probe['entry'] % 2 or not inside(probe['entry'], 2, ('.text',)):
        raise ValueError('entry bounds')
    fixes = probe['fixups']
    if fixes != sorted(set(fixes)):
        raise ValueError('duplicate/unordered fixups')
    for offset in fixes:
        if offset < 0 or offset % 4 or offset + 4 > len(image) or not inside(offset, 4, ('.rodata', '.data')):
            raise ValueError('fixup destination')
        value = struct.unpack_from('<I', image, offset)[0]
        if not inside(value, 1, ('.text', '.rodata', '.data', '.bss')):
            raise ValueError('fixup pointer')
    result = bytearray(image) + bytearray(memory - len(image))
    for offset in fixes:
        struct.pack_into('<I', result, offset, base + struct.unpack_from('<I', image, offset)[0])
    return bytes(result)


def execute(probe, base):
    import unicorn as uc
    from unicorn.riscv_const import UC_RISCV_REG_A0, UC_RISCV_REG_A1, UC_RISCV_REG_PC, UC_RISCV_REG_RA, UC_RISCV_REG_SP
    machine = uc.Uc(uc.UC_ARCH_RISCV, uc.UC_MODE_RISCV32)
    machine.mem_map(base, (probe['memory'] + 4095) & ~4095)
    machine.mem_write(base, load(probe, base))
    # Synthetic host service and stack; none are AP01 memory-map claims.
    service, stop, stack = 0x800000, 0x800100, 0x900000
    machine.mem_map(service, 4096)
    machine.mem_write(service, struct.pack('<II', 0x00750513, 0x00008067))  # addi a0,a0,7; ret
    table = service + 512
    machine.mem_write(table, struct.pack('<III', 1, 12, service))
    machine.mem_map(stack, 16384)
    results = []
    for version in (1, 1, 2):
        machine.mem_write(table, struct.pack('<I', version))
        machine.reg_write(UC_RISCV_REG_SP, stack + 16384)
        machine.reg_write(UC_RISCV_REG_RA, stop)
        machine.reg_write(UC_RISCV_REG_A0, table)
        machine.reg_write(UC_RISCV_REG_A1, 10)
        machine.emu_start(base + probe['entry'], stop, count=10000)
        assert machine.reg_read(UC_RISCV_REG_PC) == stop, 'instruction budget exceeded'
        results.append(machine.reg_read(UC_RISCV_REG_A0))
    assert results == [35, 36, 0xffffffff], results
    return results


def main():
    import unicorn as uc
    import native_build_0041 as native
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--tool-prefix', required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_dir() or any(out.iterdir()):
        parser.error('--out must be an existing empty directory')
    tool = native.tools(args.tool_prefix)
    source = native.MODULES / 'probe_app_pic_0041.cpp'
    script = out / 'probe.ld'
    script.write_text(SCRIPT)
    flags = [f for f in native.FLAGS if f != '-fno-pic']
    flags += ['-fpie', '-fvisibility=hidden', '-mcmodel=medany', '-fno-devirtualize',
              '-fno-devirtualize-speculatively', '-fno-asynchronous-unwind-tables']
    obj = out / 'probe.o'
    subprocess.run([tool('g++'), *flags, '-c', str(source), '-o', str(obj)], check=True)
    probes = []
    for base in (0x10000, 0x30000):
        path = out / ('probe-%x.elf' % base)
        subprocess.run([tool('ld'), '-m', 'elf32lriscv', '--no-relax', '--emit-relocs',
                        '--gc-sections', '--defsym=probe_base=%d' % base,
                        '-T', str(script), str(obj), '-o', str(path)], check=True)
        assert not subprocess.check_output([tool('nm'), '-u', str(path)], text=True).strip()
        probes.append(extract(path))
        path.with_suffix('.dis').write_text(subprocess.check_output([tool('objdump'), '-dr', str(path)], text=True))
        path.with_suffix('.relocations.txt').write_text(subprocess.check_output([tool('readelf'), '-rW', str(path)], text=True))
    assert probes[0] == probes[1], 'Normalized images differ across independent link bases'
    probe = probes[0]
    assert len(probe['fixups']) >= 2 and '.bss' in probe['spans'], 'fixture lost pointer/BSS coverage'
    checks = {}
    for base in (0x200000, 0x400000):
        checks[hex(base)] = execute(probe, base)
    rejected = []
    for label, change in (
        ('entry-outside-text', {'entry': probe['memory']}),
        ('entry-odd', {'entry': 1}),
        ('fixup-out-of-bounds', {'fixups': [len(probe['image'])]}),
        ('fixup-into-code', {'fixups': [0]}),
        ('duplicate-fixup', {'fixups': [probe['fixups'][0]] * 2}),
        ('truncated-image', {'image': probe['image'][:1]}),
        ('memory-budget', {'memory': 65537}),
    ):
        corrupt = dict(probe, **change)
        try:
            load(corrupt, 0x200000)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('accepted: ' + label)
    corrupt = copy.deepcopy(probe)
    image = bytearray(corrupt['image'])
    struct.pack_into('<I', image, corrupt['fixups'][0], corrupt['memory'])
    corrupt['image'] = bytes(image)
    try:
        load(corrupt, 0x200000)
    except ValueError:
        rejected.append('pointer-out-of-bounds')
    else:
        raise AssertionError('accepted external pointer')
    try:
        load(probe, 0xfffffff0)
    except ValueError:
        rejected.append('base-overflow')
    else:
        raise AssertionError('accepted address overflow')
    (out / 'probe.bin').write_bytes(probe['image'])
    report = {key: value for key, value in probe.items() if key != 'image'}
    report.update({'passed': True, 'hardware_verified': False, 'product_abi_frozen': False,
                   'compiler': subprocess.check_output([tool('g++'), '--version'], text=True).splitlines()[0],
                   'flags': flags, 'unicorn': uc.__version__, 'source_sha256': native.sha(source),
                   'script_sha256': native.sha(Path(__file__)), 'image_sha256': hashlib.sha256(probe['image']).hexdigest(),
                   'execution_results': checks, 'negative_checks': rejected,
                   'limitations': ['Synthetic addresses; no 0041 RAM/cache/interrupt evidence',
                                   'Small fixture only; no real App lifecycle or peak RAM proof',
                                   'No APX2 wire format or untrusted ELF parsing on device']})
    native.write_json(out / 'load-report.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
