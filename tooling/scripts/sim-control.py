#!/usr/bin/env python3
"""Send a bounded local request to the running AP01 NuttX SIM HOSTFS service.

Run inside WSL. Examples: sim-control.py wifi 1; bank 0 1; device 2 0 1;
fault 2; weather; check 0; package 0 42 0 0; saver 2; status.
The numeric bank namespaces are C1=0, C2=1, local charger=2.
"""
import argparse
import json
import os
from pathlib import Path
import time


def request(operation, values=(), root=Path('/home/slepher/nuttx-ap01-sim'), timeout=5):
    if not operation.replace('-', '').isalnum() or len(operation) > 31:
        raise ValueError('invalid operation')
    numbers = list(values)
    if len(numbers) > 4 or any(type(x) is not int or not 0 <= x <= 0xffffffff for x in numbers):
        raise ValueError('expected at most four unsigned integers')
    numbers += [0] * (4 - len(numbers))
    # Exclusive lock avoids overwriting a different client's outstanding request.
    lock = root / 'sim-control.lock'
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError('control-busy: inspect sim-control.lock owner')
            time.sleep(.05)
    try:
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        response = root / 'sim-response.json'
        previous = json.loads(response.read_text()) if response.exists() else {}
        session = previous.get('session')
        if not session:
            raise RuntimeError('SIM session unavailable; wait for startup before sending a command')
        floor = int(previous.get('request_high_water', 0))
        sequence = (floor if previous.get('request_retired') else max(int(previous.get('request', 0)), floor)) + 1
        if sequence > 0xffffffff:
            raise RuntimeError('request sequence exhausted; restart the SIM session before sending more commands')
        temp = root / 'sim-request.txt.new'
        temp.write_text(f'{session} {sequence} {operation} ' + ' '.join(map(str, numbers)) + '\n')
        temp.replace(root / 'sim-request.txt')
        while time.monotonic() < deadline:
            try:
                result = json.loads(response.read_text())
                if result['request'] == sequence and result.get('request_session') == session:
                    if result.get('request_retired') or result.get('session') != session:
                        raise TimeoutError(f'result-unknown-after-restart: request={sequence}; inspect current state before retry')
                    return result
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            time.sleep(.05)
        raise TimeoutError(f'result-unknown: request={sequence}; read sim-response.json before retry')
    finally:
        lock.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation')
    parser.add_argument('values', nargs='*', type=int)
    parser.add_argument('--root', type=Path, default=Path('/home/slepher/nuttx-ap01-sim'))
    args = parser.parse_args()
    result = request(args.operation, args.values, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['request_ok'] else 1)
