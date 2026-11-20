"""Build the AP01 platform base or ABI 3 App-loading firmware."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import native_build as native
from rom_target import load_target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New complete ROM filename (required for rom stage)')
    parser.add_argument('--target', choices=('0055',), default='0055')
    parser.add_argument('--build-dir', '--out', type=Path)
    parser.add_argument('--original', type=Path)
    parser.add_argument('--tool-prefix')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--app-source-dir', type=Path, help='Compatibility: package existing audited/linked build')
    group.add_argument('--boot-app-v3', action='store_true', help='Build resident ABI 3 journal-selected boot platform (retained RAM execution backend; hardware acceptance pending)')
    parser.add_argument('--stage', choices=('audit', 'link', 'rom'), default='rom')
    parser.add_argument('--json-header', type=Path, help='Explicit ArduinoJson src override')
    args = parser.parse_args()
    if args.stage == 'rom' and not args.output:
        parser.error('--output is required for ROM packaging')
    if args.app_source_dir and args.stage != 'rom':
        parser.error('--app-source-dir only packages existing artifacts')
    try:
        profile = load_target(args.target)
        tool = native.tool_prefix(args.tool_prefix)
        output = args.output.resolve() if args.output else None
        if output:
            destinations = [output] + [output.with_suffix(suffix) for suffix in
                ('.payload.bin', '.manifest.json', '.elf', '.audit.json', '.link.json', '.map')]
            if len(set(destinations)) != len(destinations) or any(p.exists() for p in destinations):
                parser.error('Use a new .bin output filename; candidate artifacts must not exist')
        out = (args.app_source_dir or args.build_dir or native.ROOT / ('build/' + args.target)).resolve()
        if not args.app_source_dir:
            if args.stage != 'link':
                audited = native.audit(out, tool, json_header=args.json_header, boot_app_v3=args.boot_app_v3, rom_target=args.target)
                if args.stage == 'audit':
                    print(json.dumps({'passed': True, 'flashable': False,
                        'report': str(out / 'native-core-audit.json'), 'budget': audited['budget']}))
                    return
            if native.validate_audit(out).get('rom_target') != args.target:
                raise ValueError('Compiled objects target differs from requested target')
            linked = native.link(out, tool)
            if args.stage == 'link':
                print(json.dumps(linked['elf']))
                return
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('build-native-app-rom.py')),
            '--source-dir', str(out), '--output', str(output), '--original', str((args.original or native.ROOT / profile['original']['path']).resolve()),
            '--tool-prefix', tool, '--target', args.target], check=True)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
