"""Test bridge: exact HTTP snapshot -> james.local Docker RV32 -> observed result.

Never installs host dependencies or accesses a device. The caller owns the live
HTTP peer; this script returns bytes, not a fabricated HTTP success response.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys
import uuid

SCRIPTS = Path(__file__).resolve().parent
ENGINE = '25a9c3620f83411672359412d6aca73c20f0e2eb94d6a8fbae5e4c39f3be3f11'
IMAGE = 'sha256:02aba83405eefd37e9c529a84ae0e26cf7d8e79a7749dc2d48e991fe8101c0cc'
REMOTE = '/home/slepher/ap01-abi-20261103'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(args):
    return subprocess.check_output(args, text=True, timeout=180)


def ssh(args):
    return call(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=8', 'james.local', shlex.join(args)])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--tool-prefix', required=True)
    p.add_argument('--qemu-image',default='ap01-abi-qemu:20261104')
    p.add_argument('--expected-image-id',default=IMAGE)
    p.add_argument('--failed', action='store_true')
    a = p.parse_args()
    assert a.out.is_dir() and not any(a.out.iterdir())
    a.out = a.out.resolve()
    snapshot = json.loads(a.snapshot.read_text())
    old_boot = snapshot['reply']['boot_id']
    prefix = 'rv32-result-' + uuid.uuid4().hex
    image_id=ssh(['sudo', '-n', 'docker', 'image', 'inspect', a.qemu_image, '--format', '{{.Id}}']).strip()
    assert image_id == a.expected_image_id
    runner = SCRIPTS / 'test-app-abi-qemu-0041.py'
    remote_runner = f'{REMOTE}/input/{prefix}.py'
    call(['scp', str(runner), 'james.local:' + remote_runner])
    reports = []

    def build(mode, boot, journals=None):
        folder = a.out / mode
        folder.mkdir()
        command = [sys.executable, '-B', str(SCRIPTS / 'build-app-v3-guest-0041.py'),
                   '--snapshot', str(a.snapshot.resolve()), '--out', str(folder),
                   '--boot-mode', mode, '--boot-id', str(boot), '--tool-prefix', a.tool_prefix]
        if journals:
            command += ['--resume-journals', str(journals)]
        call(command)
        remote = f'{REMOTE}/input/{prefix}-{mode}'
        ssh(['mkdir', remote])
        call(['scp', *[str(folder / name) for name in ('guest.bin', 'app.apx2', 'set.amf3', 'peer.apx2', 'journals.bin', 'build-report.json')], 'james.local:' + remote + '/'])
        return folder, remote

    def execute(stages, label):
        name = prefix + '-' + label
        command = ['sudo', '-n', 'docker', 'run', '--rm', '--network', 'none', '--cpus', '2', '--memory', '512m',
                   '--pids-limit', '64', '--user', '1000:1000', '--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=64m',
                   '-v', '/home/slepher/ap01-review-20261022/build/qemu/qemu-system-riscv32:/engine/qemu:ro',
                   '-v', '/home/slepher/ap01-review-20261022/cuktech-ap01-firmware/tooling/scripts:/support:ro',
                   '-v', REMOTE + '/input:/input:ro', '-v', REMOTE + '/output:/output',
                   a.qemu_image, 'python3', '-B', '/input/' + prefix + '.py', '--direct-v3',
                   '--qemu', '/engine/qemu', '--expected-engine-sha256', ENGINE, '--support-dir', '/support',
                   '--fixture-dir', '/input/' + Path(stages[0][1]).name, '--output', '/output/' + name + '.json']
        for _, remote in stages[1:]:
            command += ['--next-fixture', '/input/' + Path(remote).name]
        ssh(command)
        path = a.out / (label + '.json')
        call(['scp', f'james.local:{REMOTE}/output/{name}.json', str(path)])
        report = json.loads(path.read_text())
        assert report['passed'] and report['engine_sha256'] == ENGINE and report['script_sha256'] == sha(runner)
        for index, (folder, _) in enumerate(stages):
            assert report['boot_inputs'][index]['build_report_sha256'] == sha(folder / 'build-report.json')
        outputs = []
        for base, result in report['results'].items():
            steps = result['stages'] if len(stages) > 1 else [result]
            assert len(steps) == len(stages) and all(s['result'] == 0 and s['stack_and_saved_registers_preserved'] for s in steps)
            if len(stages) > 1:
                assert report['same_vm_reset_verified'] and len(result['resets']) == len(stages) - 1
            pair = []
            for kind in ('journals', 'runtime'):
                item = steps[-1][kind]
                assert Path(item['name']).name == item['name']
                target = a.out / f'{label}-{base}-{kind}.bin'
                call(['scp', f"james.local:{REMOTE}/output/{item['name']}", str(target)])
                assert sha(target) == item['sha256']
                pair.append(target)
            outputs.append(pair)
        assert len(outputs) == 2
        assert all(outputs[0][i].read_bytes() == outputs[1][i].read_bytes() for i in (0, 1))
        reports.append({'path': str(path), 'sha256': sha(path)})
        return outputs[0]

    first = build('fail-trial' if a.failed else 'trial', old_boot + 1)
    result = execute([first], 'trial')
    if a.failed:
        mode = 'empty-rollback' if snapshot['reply']['old_version'] == 0 else 'rollback'
        second = build(mode, old_boot + 2, result[0])
        result = execute([first, second], 'rollback')
    output = {'snapshot_sha256': sha(a.snapshot), 'reports': reports,
              'docker_image':a.qemu_image,'docker_image_id':image_id,
              'journals': {'path': str(result[0]), 'sha256': sha(result[0])},
              'runtime': {'path': str(result[1]), 'sha256': sha(result[1])},
              'device_accessed': False, 'host_health_injected': False}
    (a.out / 'result.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
