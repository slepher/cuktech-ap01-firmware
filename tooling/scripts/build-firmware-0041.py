"""Firmware-owned offline AP01 0041 build, with an optional App source configuration."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
import native_build_0041 as native


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='New complete ROM filename (required for rom stage)')
    parser.add_argument('--build-dir', '--out', type=Path, default=native.ROOT / 'build/0041')
    parser.add_argument('--original', type=Path, default=native.ROOT / 'roms/0041/ap01-1.0.2_0041.bin')
    parser.add_argument('--tool-prefix')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--app-config', type=Path, help='App source/configuration JSON; firmware compiles and links it')
    group.add_argument('--app-source-dir', type=Path, help='Compatibility: package existing audited/linked build')
    parser.add_argument('--stage', choices=('audit', 'link', 'rom'), default='rom')
    parser.add_argument('--screen-host-probe', action='store_true')
    parser.add_argument('--json-header', type=Path, help='Explicit ArduinoJson src override')
    args = parser.parse_args()
    if args.stage == 'rom' and not args.output:
        parser.error('--output is required for ROM packaging')
    if args.app_source_dir and args.stage != 'rom':
        parser.error('--app-source-dir only packages existing artifacts')
    if args.screen_host_probe and (not args.app_config or args.stage == 'link'):
        parser.error('--screen-host-probe requires --app-config at audit/rom stage')
    try:
        tool = native.tool_prefix(args.tool_prefix)
        output = args.output.resolve() if args.output else None
        if output:
            destinations = [output] + [output.with_suffix(suffix) for suffix in
                ('.payload.bin', '.manifest.json', '.elf', '.audit.json', '.link.json', '.map')]
            if len(set(destinations)) != len(destinations) or any(p.exists() for p in destinations):
                parser.error('Use a new .bin output filename; candidate artifacts must not exist')
        out = (args.app_source_dir or args.build_dir).resolve()
        if not args.app_source_dir:
            if args.stage != 'link':
                audited = native.audit(out, tool, args.app_config, args.screen_host_probe, args.json_header)
                if args.stage == 'audit':
                    print(json.dumps({'passed': True, 'flashable': False,
                        'report': str(out / 'native-core-audit.json'), 'budget': audited['budget']}))
                    return
            linked = native.link(out, tool)
            if args.stage == 'link':
                print(json.dumps(linked['elf']))
                return
        output.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('build-native-app-rom-0041.py')),
            '--source-dir', str(out), '--output', str(output), '--original', str(args.original.resolve()),
            '--tool-prefix', tool], check=True)
    except (ValueError, FileNotFoundError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
