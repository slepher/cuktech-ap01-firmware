#!/usr/bin/env python3
"""Verify guest-driven OTA Flash results; never claim physical boot or deployment readiness."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


def table(data, offset):
    block = data[offset:offset + 4096]
    if block[:4] != b'BFPT':
        raise ValueError('partition magic')
    count = struct.unpack_from('<H', block, 6)[0]
    if not 1 <= count <= 16:
        raise ValueError('partition count')
    if zlib.crc32(block[:12]) != struct.unpack_from('<I', block, 12)[0]:
        raise ValueError('partition header CRC')
    entries = block[16:16 + count * 36]
    if zlib.crc32(entries) != struct.unpack_from('<I', block, 16 + count * 36)[0]:
        raise ValueError('partition entries CRC')
    firmware = [entries[i:i + 36] for i in range(0, len(entries), 36)
                if entries[i] == 0 and entries[i + 3:i + 6] == b'FW\0']
    if len(firmware) != 1:
        raise ValueError('firmware partition entry')
    return struct.unpack_from('<I', block, 8)[0], firmware[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('report', 'image', 'fixture', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument("--uploaded-image",type=Path,help="Explicit target when the native probe uploads a separate production ROM")
    args = parser.parse_args()
    if args.output.exists():
        parser.error('new output required')
    report = json.loads(args.report.read_text())
    image, before = args.image.read_bytes(), args.fixture.read_bytes()
    after = Path(report['flash_snapshot']['path']).read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    target_image = args.uploaded_image.read_bytes() if args.uploaded_image else image
    checks = {
        'source_identity': digest == report['image_sha256'],
        'fixture_identity': hashlib.sha256(before).hexdigest() == report['flash_fixture_sha256'],
        'snapshot_identity': hashlib.sha256(after).hexdigest() == report['flash_snapshot']['sha256'],
        'native_tcp': report.get('native_loopback') is True and report.get('provider_calls') == {},
        'diagnostics': report.get('diagnostic_probe_verified') is True,
        'no_guest_exception': not report.get('first_guest_exception') and not report.get('error'),
        'commit_returned_zero': any(c['payload_caller'] and c.get('result') == 0
                                   for c in report['native_ff13_calls']),
        'reset_after_commit': report.get('reset_requested') is True and report.get('premature_reset') is False,
        'source_files_unchanged': report['source_unchanged'] and report['flash_fixture_unchanged'],
        'nor_size': len(before) == len(after) == 0x1000000,
    }
    old_age, old_fw = max(table(before, p) for p in (0xe000, 0xf000))
    new_age, new_fw = max(table(after, p) for p in (0xe000, 0xf000))
    bases = struct.unpack_from('<2I', old_fw, 12)
    capacities = struct.unpack_from('<2I', old_fw, 20)
    active = old_fw[2]
    if active not in (0, 1) or bases != (0x10000, 0x7b0000) or capacities != (0x700000, 0x700000):
        raise ValueError('unexpected fixture layout')
    target = 1 - active
    start, end = bases[target], bases[target] + capacities[target]
    checks.update(
        selected_inactive_slot=new_fw[2] == target and new_age > old_age,
        partition_layout_unchanged=new_fw[3:28] == old_fw[3:28],
        target_exact=after[start:start + len(target_image)] == target_image,
        target_padding_unchanged=after[start + len(target_image):end] == before[start + len(target_image):end],
        boot2_unchanged=after[:0xe000] == before[:0xe000],
        active_unchanged=after[0x10000:0x710000] == before[0x10000:0x710000],
        crash_and_ota_staging_unchanged=after[0x720000:0x7b0000] == before[0x720000:0x7b0000],
        reserve_unchanged=after[0xff0000:] == before[0xff0000:],
    )
    result = dict(passed=all(checks.values()), checks=checks, validated_images=[hashlib.sha256(target_image).hexdigest()], running_image_sha256=digest,
                  device_accessed=False, physical_boot_verified=False, flashable=False,
                  scope='native guest TCP, readback, slot commit and reset request; /data journal and native /resource initialization may change',
                  http_response_observed=False, source_report=str(args.report),
                  previous_age=old_age, committed_age=new_age, target_slot=target)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
