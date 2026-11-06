"""Pinned ROM patch profiles; App package/ABI versions are independent."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
MENU_SYMBOLS = ('ap01MenuRegisterOne0041', 'ap01MenuRegisterTwo0041',
                'ap01MenuRegisterThree0041', 'ap01MenuList0041')
BASELINES = {
    '0041': (6769704, '972db4c136c7ed9e24a83c07c1a7fd62040ca018b08ca285216d26b1fee3c6b9'),
    '0055': (6389800, '0d4a2c10314e984e8425f77385f3be89ebe33937eaa711938fda8f318a909bb7'),
}


def _integer(value):
    if isinstance(value, bool):
        raise ValueError('Boolean is not a ROM address')
    result = int(value, 0) if isinstance(value, str) else value
    if not isinstance(result, int) or not 0 <= result <= 0xffffffff:
        raise ValueError('ROM address is not uint32')
    return result


def validate_profile(raw, target):
    """Validate a complete reviewed profile before any compilation or patching."""
    fields = {'format', 'target', 'status', 'original', 'mapping_base', 'payload_offset',
              'ui_hook', 'timer_delete', 'menu_hooks', 'unsigned_ota'}
    if target not in BASELINES or set(raw) != fields or raw['format'] != 1 or raw['target'] != target:
        raise ValueError('Unsupported or incomplete ROM profile')
    if raw['status'] != 'static_verified':
        raise ValueError('ROM addresses and replay contracts must be statically verified')
    original = raw['original']
    expected_path = f'roms/{target}/ap01-1.0.2_{target}.bin'
    if set(original) != {'path', 'bytes', 'sha256'} or original['path'] != expected_path:
        raise ValueError('Unexpected original ROM path')
    if (original['bytes'], original['sha256']) != BASELINES[target]:
        raise ValueError('Original ROM identity differs from pinned baseline')
    profile = dict(raw)
    profile['original'] = dict(original)
    profile['mapping_base'] = _integer(raw['mapping_base'])
    profile['payload_offset'] = _integer(raw['payload_offset'])
    # Both targets intentionally share the existing immutable-module linker script.
    if profile['mapping_base'] != 0x9ffff000 or profile['payload_offset'] != 0x675000:
        raise ValueError('Unsupported mapping or module link address')
    if original['bytes'] > profile['payload_offset']:
        raise ValueError('Payload would overlap the immutable original')
    ranges = []

    def patch(item, keys, lengths):
        if set(item) != keys:
            raise ValueError('Incomplete patch record')
        record = dict(item)
        record['offset'] = _integer(item['offset'])
        try:
            before = bytes.fromhex(item['original_hex'])
        except (ValueError, TypeError):
            raise ValueError('Invalid original patch bytes') from None
        if len(before) not in lengths or item['original_hex'] != before.hex():
            raise ValueError('Unexpected patch span or noncanonical original bytes')
        start, end = record['offset'], record['offset'] + len(before)
        if start < 0x1000 or start & 1 or end > original['bytes'] - 40:
            raise ValueError('Patch outside original instruction range')
        if any(start < b and a < end for a, b in ranges):
            raise ValueError('Overlapping ROM patches')
        ranges.append((start, end))
        return record

    profile['ui_hook'] = patch(raw['ui_hook'], {'offset', 'original_hex'}, (8,))
    profile['timer_delete'] = patch(raw['timer_delete'], {'offset', 'original_hex', 'nonnull_tail'}, (8,))
    tail = _integer(raw['timer_delete']['nonnull_tail'])
    if tail != profile['mapping_base'] + profile['timer_delete']['offset'] + 8:
        raise ValueError('Timer continuation must follow the replayed prologue')
    profile['timer_delete']['nonnull_tail'] = tail
    if not isinstance(raw['menu_hooks'], list) or len(raw['menu_hooks']) != 4:
        raise ValueError('Four reviewed settings hooks are required')
    profile['menu_hooks'] = []
    for index, item in enumerate(raw['menu_hooks']):
        record = patch(item, {'offset', 'original_hex', 'symbol'}, (10,) if index == 3 else (8,))
        if record['symbol'] != MENU_SYMBOLS[index]:
            raise ValueError('Settings replay symbol/order mismatch')
        profile['menu_hooks'].append(record)
    profile['unsigned_ota'] = patch(raw['unsigned_ota'],
        {'offset', 'original_hex', 'replacement_hex'}, (2,))
    replacement = bytes.fromhex(raw['unsigned_ota']['replacement_hex'])
    if len(replacement) != 2 or raw['unsigned_ota']['replacement_hex'] != replacement.hex():
        raise ValueError('Unsigned OTA replacement must be one compressed instruction')
    return profile


def load_target(target='0041'):
    if target == '0041':
        raw = {'format': 1, 'target': target, 'status': 'static_verified',
            'original': {'path': 'roms/0041/ap01-1.0.2_0041.bin', 'bytes': BASELINES[target][0], 'sha256': BASELINES[target][1]},
            'mapping_base': '0x9ffff000', 'payload_offset': '0x675000',
            'ui_hook': {'offset': '0x5e180', 'original_hex': '97001500e780404d'},
            'timer_delete': {'offset': '0x8be58', 'original_hex': '411106c622c426c2', 'nonnull_tail': '0xa008ae60'},
            'menu_hooks': [dict(offset=hex(offset), original_hex=before, symbol=symbol)
                for offset, before, symbol in zip((0xb262c, 0xb263a, 0xb2648, 0xb2754),
                ('efc08f0281460546', 'efc0af0181462d46', 'efc0cf00b7450fa0', 'ef10ef4a814523a4a900'), MENU_SYMBOLS)],
            'unsigned_ota': {'offset': '0x707fc', 'original_hex': 'dde7', 'replacement_hex': '7da0'}}
    elif target == '0055':
        raw = json.loads((ROOT / 'tooling/rom-targets/0055.json').read_text(encoding='utf-8'))
    else:
        raise ValueError('Unsupported ROM target')
    return validate_profile(raw, target)


def validate_original(profile, original):
    identity = profile['original']
    if len(original) != identity['bytes'] or hashlib.sha256(original).hexdigest() != identity['sha256']:
        raise ValueError(f"Exact original {profile['target']} required")
    records = [profile['ui_hook'], profile['timer_delete'], *profile['menu_hooks'], profile['unsigned_ota']]
    for record in records:
        before = bytes.fromhex(record['original_hex'])
        if original[record['offset']:record['offset'] + len(before)] != before:
            raise ValueError(f"Original patch bytes mismatch at {record['offset']:#x}")


def profile_identity(target):
    profile = load_target(target)
    return hashlib.sha256(json.dumps(profile, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
