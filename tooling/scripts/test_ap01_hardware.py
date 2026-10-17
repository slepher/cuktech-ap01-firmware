"""Semantic checks execute encoded instructions, separately from ROM replay."""
import argparse
from pathlib import Path
import sys
import unittest

sys.dont_write_bytecode = True
parser = argparse.ArgumentParser()
parser.add_argument('--deps', type=Path, required=True)
args, remaining = parser.parse_known_args()
sys.path.insert(0, str(args.deps.resolve()))
from emulate_ap01 import AP01, ENTRY


def machine(word):
    return AP01(bytes(0x1000) + word.to_bytes(4, 'little'))


class HardwareTests(unittest.TestCase):
    def test_csr_rmw_and_immediates(self):
        # Initial CSR=0x55, operand=3. All six Zicsr operations return old.
        for funct, expected in [(1, 3), (2, 0x57), (3, 0x54),
                                (5, 3), (6, 0x57), (7, 0x54)]:
            with self.subTest(funct=funct):
                m = machine((0x7c5 << 20) | (3 << 15) | (funct << 12) | (5 << 7) | 0x73)
                m.csrs[0x7c5] = 0x55
                m.setreg(3, 3)
                m.run(count=1)
                self.assertEqual(m.reg(5), 0x55)
                self.assertEqual(m.csrs[0x7c5], expected)

    def test_csr_zero_and_register_alias(self):
        for funct in (2, 3, 6, 7):
            m = machine((0x7c5 << 20) | (funct << 12) | 0x73)
            m.csrs[0x7c5] = 0xfedcba98
            m.run(count=1)
            self.assertEqual(m.csrs[0x7c5], 0xfedcba98)
            self.assertEqual(m.reg(0), 0)
            self.assertIsNone(m.events[0]['write'])
        m = machine((0x7c5 << 20) | (5 << 15) | (1 << 12) | (5 << 7) | 0x73)
        m.setreg(5, 0xffffffff)
        m.run(count=1)
        self.assertEqual(m.reg(5), 0)
        self.assertEqual(m.csrs[0x7c5], 0xffffffff)

    def test_addsl_operand_order_and_wrap(self):
        for shift in range(4):
            m = machine((shift << 25) | (14 << 20) | (10 << 15) | (1 << 12) | (12 << 7) | 0xb)
            m.setreg(10, 0xe0800000)
            m.setreg(14, 3)
            m.run(count=1)
            self.assertEqual(m.reg(12), 0xe0800000 + (3 << shift))
        m = machine(0x04e5160b)
        m.setreg(10, 0xffffffff)
        m.setreg(14, 1)
        m.run(count=1)
        self.assertEqual(m.reg(12), 3)

    def test_insb_preserves_other_bytes(self):
        for byte in range(4):
            m = machine(0xac000077 | (byte << 20) | (6 << 15) | (5 << 7))
            m.setreg(5, 0x12345678)
            m.setreg(6, 0xdeadbeef)
            m.run(count=1)
            expected = bytearray.fromhex('78563412')
            expected[byte] = 0xef
            self.assertEqual(m.reg(5), int.from_bytes(expected, 'little'))

    def test_ram_aliases_share_backing(self):
        m = machine(0x13)
        m.uc.mem_write(0x22fc0400, b'RAM!')
        for base in (0x20fc0000, 0x22fc0000, 0x60fc0000, 0x62fc0000):
            self.assertEqual(bytes(m.uc.mem_read(base + 0x400, 4)), b'RAM!')
        m.uc.mem_write(0xa8000040, b'PSRM')
        self.assertEqual(bytes(m.uc.mem_read(0x88000040, 4)), b'PSRM')

    def test_incrementing_memory_order_and_negative_offset(self):
        # Post-increment reads OLD base; pre-increment reads NEW base.
        for top, offset, expected_address, expected_base in [
            (11, 4, 0x62fc0800, 0x62fc0804),
            (9, 4, 0x62fc0804, 0x62fc0804),
            (9, 28, 0x62fc07fc, 0x62fc07fc),
        ]:
            word = (top << 27) | (offset << 20) | (14 << 15) | (4 << 12) | (12 << 7) | 0xb
            m = machine(word)
            m.setreg(14, 0x62fc0800)
            m.uc.mem_write(expected_address, bytes.fromhex('efcdab89'))
            m.run(count=1)
            self.assertEqual(m.reg(12), 0x89abcdef)
            self.assertEqual(m.reg(14), expected_base)

    def test_original_copy_instruction_pair(self):
        words = [0x5847460b, 0x5847d60b]  # th.lwia a2,(a4),4; th.swia a2,(a5),4
        m = AP01(bytes(0x1000) + b''.join(w.to_bytes(4, 'little') for w in words))
        m.setreg(14, 0x62fc0800)
        m.setreg(15, 0x62fc0900)
        m.uc.mem_write(0x62fc0800, b'COPY')
        m.run(count=2)
        self.assertEqual(bytes(m.uc.mem_read(0x22fc0900, 4)), b'COPY')
        self.assertEqual((m.reg(14), m.reg(15)), (0x62fc0804, 0x62fc0904))

    def test_extract_signed_and_unsigned(self):
        for funct, expected in [(2, 0xfffffff8), (3, 8)]:
            m = machine((7 << 26) | (4 << 20) | (6 << 15) | (funct << 12) | (5 << 7) | 0xb)
            m.setreg(6, 0x80)
            m.run(count=1)
            self.assertEqual(m.reg(5), expected)

    def test_custom_store_cannot_write_rom(self):
        word = (8 << 27) | (6 << 15) | (5 << 12) | (5 << 7) | 0xb
        m = machine(word)
        before = bytes(m.uc.mem_read(ENTRY, 4))
        m.setreg(6, ENTRY)
        m.setreg(5, 0)
        report = m.run(count=1)
        self.assertEqual(report['stop']['reason'], 'unsupported-custom-memory')
        self.assertEqual(bytes(m.uc.mem_read(ENTRY, 4)), before)

    def test_mmio_resets_masks_and_subwords(self):
        m = machine(0x13)
        self.assertEqual(m._mmio_read(m.uc, 0x968, 4, 0x20000000), 2)
        m._mmio_write(m.uc, 0x968, 4, 0xffffffff, 0x20000000)
        self.assertEqual(m._mmio_read(m.uc, 0x968, 4, 0x20000000), 0x3f)
        m._mmio_write(m.uc, 0x1001, 1, 1, 0xe0800000)
        self.assertEqual(m._mmio_read(m.uc, 0x1000, 4, 0xe0800000), 0x100)

    def test_unknown_mmio_and_csr_fail(self):
        m = machine(0x13)
        m._mmio_read(m.uc, 0x100, 4, 0x20000000)
        self.assertEqual(m.stop['reason'], 'unsupported-mmio-read')
        m = machine(0x13)
        m._mmio_write(m.uc, 4, 4, 0, 0xe0800000)
        self.assertEqual(m.stop['reason'], 'unsupported-mmio-write')
        m = machine((0x7ff << 20) | (2 << 12) | (5 << 7) | 0x73)
        self.assertEqual(m.run(count=2)['stop']['reason'], 'cpu-exception')


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]] + remaining)
