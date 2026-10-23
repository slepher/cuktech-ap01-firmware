"""Static candidate search only; no target execution or exhaustive alias claim."""
import hashlib
import json
from collections import Counter, deque
from pathlib import Path
from capstone import Cs, CS_ARCH_RISCV, CS_MODE_RISCV32, CS_MODE_RISCVC

ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / 'roms/0041/ap01-1.0.2_0041.bin'
raw = ROM.read_bytes()
BASE = 0x9ffff000
md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_RISCVC)
md.detail = True
cache = {}

def insn(pc):
    if pc not in cache:
        off = pc - BASE
        cache[pc] = next(md.disasm(raw[off:off+4], pc, count=1), None) if 0 <= off < len(raw)-3 else None
    return cache[pc]

def watched(v):
    return v is not None and (0x62fc9288 <= v < 0x62fc92b8 or 0x62fc94d8 <= v < 0x62fc94f0)

seeds = [BASE+i for i in range(0, len(raw)-3, 2)
         if (int.from_bytes(raw[i:i+4], 'little') & 0xfffff07f) == 0x62fc9037]
events = {}
stops = Counter()
caller_saved = [2, 6, 7, 8, *range(11, 19), *range(29, 33)]
for seed in seeds:
    regs = [None] * 128  # Capstone includes floating-point registers in the enum.
    regs[1] = 0
    queue = deque([(seed, tuple(regs))])
    seen = set()
    while queue and len(seen) < 10000:
        pc, state = queue.popleft()
        if (pc, state) in seen:
            continue
        seen.add((pc, state))
        if pc & 1 or not seed-4096 <= pc < seed+4096:
            stops['window_edge'] += 1
            continue
        i = insn(pc)
        if i is None:
            stops['undecoded'] += 1
            continue
        r = list(state)
        ops = i.operands
        m = i.mnemonic
        text = m + ' ' + i.op_str
        def event(kind, target, **extra):
            key = (pc, kind, target, tuple(sorted(extra.items())))
            if key not in events:
                events[key] = dict(address=hex(pc), kind=kind, target=hex(target), instruction=text,
                                   seed=hex(seed), **extra)
        for o in ops:
            if o.type == 3 and r[o.mem.base] is not None:
                addr = (r[o.mem.base] + o.mem.disp) & 0xffffffff
                if watched(addr):
                    store = m in ['sb','sh','sw','c.sw','c.swsp','sd']
                    event('store' if store else 'memory_read', addr,
                          value=r[ops[0].reg] if store and ops[0].type == 1 else None)
        nxt = pc + i.size
        call = m in ['jal','c.jal','jalr','c.jalr']
        if call:
            dest = None
            if m in ['jal','c.jal']:
                dest = (pc + ops[-1].imm) & 0xffffffff
            elif len(ops) == 3 and r[ops[1].reg] is not None:
                dest = (r[ops[1].reg] + ops[2].imm) & 0xfffffffe
            for reg in range(11,19):
                if watched(r[reg]):
                    event('call_argument', r[reg], register=md.reg_name(reg), callee=hex(dest) if dest is not None else 'unresolved')
            for reg in caller_saved:
                r[reg] = None
        elif m in ['ret','c.jr','jr']:
            stops['return_or_indirect_jump'] += 1
            continue
        elif m in ['j','c.j']:
            nxt = pc + ops[-1].imm
        elif m.startswith('b') or m in ['c.beqz','c.bnez']:
            queue.append((pc + ops[-1].imm, tuple(r)))
        elif m in ['lui','c.lui']:
            r[ops[0].reg] = (ops[1].imm << 12) & 0xffffffff
        elif m == 'auipc':
            r[ops[0].reg] = (pc + (ops[1].imm << 12)) & 0xffffffff
        elif m in ['li','c.li']:
            r[ops[0].reg] = ops[1].imm & 0xffffffff
        elif m in ['mv','c.mv']:
            r[ops[0].reg] = r[ops[1].reg]
        elif m == 'addi':
            v = r[ops[1].reg]
            r[ops[0].reg] = None if v is None else (v + ops[2].imm) & 0xffffffff
        elif m in ['c.addi','c.addi16sp']:
            v = r[ops[0].reg]
            r[ops[0].reg] = None if v is None else (v + ops[-1].imm) & 0xffffffff
        elif m in ['sb','sh','sw','c.sw','c.swsp','sd','fence','nop','c.nop']:
            pass
        elif ops and ops[0].type == 1:
            r[ops[0].reg] = None
        else:
            stops['unmodelled'] += 1
            continue
        r[1] = 0
        queue.append((nxt, tuple(r)))
    if queue:
        stops['state_cap'] += 1

out = dict(rom_sha256=hashlib.sha256(raw).hexdigest(), method='branch-following RV32C constant candidate search from all LUI 0x62fc9 seeds; +/-4096 B, 10000 states/seed; caller-saved constants discarded at calls',
           limitations=['Both branch outcomes explored without predicate feasibility; candidates require raw instruction review',
                        'Unknown/vendor instructions stop a path; no memory-loaded pointers, interprocedural aliasing or dynamic writes',
                        'All even ROM offsets include non-code seeds; no claim of whole-ROM absence or function coverage',
                        'Generic destination invalidation loses arithmetic values; no stack spill/reload propagation'],
           seed_count=len(seeds), stop_reasons=dict(stops), events=sorted(events.values(), key=lambda e:(e['address'],e['kind'],e['target'])))
Path(__file__).with_name('cfg-state-candidates.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(seeds=len(seeds), events=len(events), stops=dict(stops))))
