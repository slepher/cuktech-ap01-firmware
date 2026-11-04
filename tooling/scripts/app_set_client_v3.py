"""Client-side AMF3/package and post-reboot identity checks; no device access."""
import hashlib
import importlib.util
from pathlib import Path
import re
import struct

_spec = importlib.util.spec_from_file_location('amf3_builder', Path(__file__).with_name('app-manifest-v3.py'))
_builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_builder)


def _text(raw):
    text = raw.split(b'\0', 1)[0]
    if not re.fullmatch(rb'[A-Za-z0-9._+\-]{1,31}', text) or raw[len(text):] != bytes(32-len(text)):
        raise ValueError('invalid manifest text')
    return text.decode('ascii')


def inspect_manifest(blob):
    if len(blob) < 64 or len(blob) > 3584 or blob[:4] != b'AMF3':
        raise ValueError('invalid AMF3 header')
    version, header, size, count, entry_bytes, sequence, deps = struct.unpack_from('<HHIHHQH', blob, 4)
    if (version != 1 or header != 64 or size != len(blob) or count > 8 or entry_bytes != 160
            or not sequence or deps > 56 or blob[26:32] != bytes(6)
            or size != 64 + 160*count + 40*deps):
        raise ValueError('invalid AMF3 bounds/version')
    digest = hashlib.sha256(blob[:32] + bytes(32) + blob[64:]).digest()
    if digest != blob[32:64]:
        raise ValueError('AMF3 content digest mismatch')
    apps = []
    for index in range(count):
        raw = blob[64+160*index:64+160*(index+1)]
        app_id, app_version = _text(raw[:32]), _text(raw[32:64])
        values = struct.unpack_from('<7IQ5HHI', raw, 96)
        package_bytes, image_bytes, heap, stack, data_min, data_max, data_write, capabilities, tcp, udp, order, tasks, pages, reserved, abi = values
        if (app_id in ('.', '..') or reserved or abi != 3 or order >= count or tasks > 4 or pages > 32
                or package_bytes < 256 or not image_bytes or stack < 256 or stack & 15
                or raw[148:] != bytes(12) or data_min > data_max
                or not data_min <= data_write <= data_max or tasks*256 > stack
                or 18080 in (tcp, udp) or raw[64:96] == bytes(32)):
            raise ValueError('invalid App entry')
        apps.append(dict(index=index, app_id=app_id, version=app_version, digest=raw[64:96].hex(),
                         package_bytes=package_bytes, order=order, raw=raw))
    ids = [a['app_id'] for a in apps]
    if ids != sorted(set(ids)) or sorted(a['order'] for a in apps) != list(range(count)):
        raise ValueError('duplicate/unsorted IDs or startup order')
    for offset in (132, 134):
        ports = [struct.unpack_from('<H', a['raw'], offset)[0] for a in apps]
        ports = [p for p in ports if p]
        if len(set(ports)) != len(ports):
            raise ValueError('duplicate App port')
    previous = None
    for index in range(deps):
        raw = blob[64+160*count+40*index:64+160*count+40*(index+1)]
        source, target, reserved = struct.unpack_from('<HHI', raw)
        if (reserved or source >= count or target >= count or source == target
                or (previous is not None and (source, target) <= previous)
                or apps[target]['order'] >= apps[source]['order'] or raw[8:].hex() != apps[target]['digest']):
            raise ValueError('invalid dependency identity/order')
        previous = source, target
    return dict(digest=digest.hex(), version=sequence, apps=apps)


def inspect_packages(manifest, blobs):
    """Validate supplied packages. Unchanged entries may be omitted for single updates."""
    found = {}
    entries = {a['app_id']: a for a in manifest['apps']}
    for blob in blobs:
        info = _builder.package_info(blob)
        entry = entries.get(info['app_id'])
        if entry is None or entry['index'] in found:
            raise ValueError('unexpected or duplicate package')
        expected = struct.pack('<7IQ', len(blob), len(blob)-256-len(info['fixups'])*8+info['bss_bytes'],
                               info['heap_bytes'], info['stack_bytes'], info['data_read_min'],
                               info['data_read_max'], info['data_write_version'], info['required_services'])
        if entry['raw'][:96] != blob[128:224] or entry['raw'][96:132] != expected:
            raise ValueError('package does not match manifest metadata')
        found[entry['index']] = blob
    return found


def changed_packages(manifest, packages, mask):
    if type(mask) is not int or mask < 0 or mask >> len(manifest['apps']):
        raise ValueError('invalid changed mask')
    indices = [i for i in range(len(manifest['apps'])) if mask & (1 << i)]
    if any(i not in packages for i in indices):
        raise ValueError('missing changed package; retain the same receipt when resuming')
    return {i: packages[i] for i in indices}


def verify_running(value, manifest, original_boot):
    """False means keep querying; mismatched identity is an error, never success."""
    if value.get('phase') != 'succeeded':
        return False
    if value.get('candidate_manifest') != manifest['digest'] or value.get('candidate_version') != manifest['version']:
        raise ValueError('committed manifest identity mismatch')
    if type(original_boot) is not int or not 0 < original_boot < 2**64:
        raise ValueError('invalid original boot identity')
    boot = value.get('boot_id')
    if type(boot) is not int or not 0 < boot < 2**64:
        raise ValueError('invalid current boot identity')
    runtime = value.get('runtime')
    if (value.get('runtime_reporting') is not True or not isinstance(runtime, dict)
            or runtime.get('complete') is not True or runtime.get('boot_state') != 'started'
            or runtime.get('health_state') != 'healthy' or value.get('cleanup_pending') is not False
            or boot == original_boot):
        return False
    if runtime.get('manifest') != manifest['digest'] or runtime.get('version') != manifest['version']:
        raise ValueError('running manifest identity mismatch')
    running = runtime.get('running')
    if not isinstance(running, list) or len(running) != len(manifest['apps']):
        raise ValueError('running collection size mismatch')
    expected = sorted(manifest['apps'], key=lambda a: a['order'])
    for actual, app in zip(running, expected):
        if not isinstance(actual, dict) or any(actual.get(k) != app[k] for k in ('index', 'app_id', 'version', 'digest')):
            raise ValueError('running App identity/order mismatch')
        if type(actual.get('health')) is not int or actual['health'] != 0:
            return False
    return True


def check_capabilities(manifest, value):
    """Whole-set checks use the same aligned-image sum and resident charge as firmware."""
    limits=value.get('limits')
    if value.get('protocol')!=3 or not isinstance(limits,dict):
        raise ValueError('collection resource limits unavailable')
    def number(mapping,key):
        n=mapping.get(key)
        if type(n) is not int or not 0<=n<2**64:
            raise ValueError('invalid capability: '+key)
        return n
    if len(manifest['apps'])>number(value,'app_max'):
        raise ValueError('collection exceeds app limit')
    totals=dict(package_bytes=0,image_bytes=0,heap_bytes=0,stack_bytes=0,tasks=0,pages=0,capabilities=0)
    for app in manifest['apps']:
        raw=app['raw'];package,image,heap,stack=struct.unpack_from('<4I',raw,96)
        totals['package_bytes']+=package;totals['image_bytes']+=(image+15)&~15
        totals['heap_bytes']+=heap;totals['stack_bytes']+=stack
        tasks,pages=struct.unpack_from('<HH',raw,138);totals['tasks']+=tasks;totals['pages']+=pages
        totals['capabilities']|=struct.unpack_from('<Q',raw,124)[0]
    for key,n in totals.items():
        cap=number(limits,key)
        if (n&~cap if key=='capabilities' else n>cap):
            raise ValueError('collection exceeds '+key)
    ram,resident=number(limits,'ram_bytes'),number(limits,'resident_bytes')
    if resident>ram or totals['image_bytes']+totals['heap_bytes']+totals['stack_bytes']>ram-resident:
        raise ValueError('collection exceeds RAM after resident reserve')
    return totals
