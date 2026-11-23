"""Exercise maintenance errors through the real transport and fenced client, offline."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import struct

spec = importlib.util.spec_from_file_location('client', Path(__file__).with_name('app-set-client-v3.py'))
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)
mac = 'AABBCCDDEEFF'


class Response(io.BytesIO):
    def __init__(self, status, value):
        super().__init__(json.dumps(value).encode())
        self.code = status


class Opener:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def open(self, request, **kwargs):
        self.calls.append((request.method, request.full_url))
        return Response(*next(self.replies))


def rejects(call, text):
    try:
        call()
    except ValueError as error:
        assert text in str(error), str(error)
    else:
        raise AssertionError('Expected rejection: ' + text)


busy = (409, dict(error='maintenance_busy', stage='platform_operation'))
oom = (503, dict(error='reply_oom', stage='response'))
missing = (404, dict(device_mac=mac, protocol=3, error_code='not_found'))
with tempfile.TemporaryDirectory() as folder:
    def installer(replies):
        transport = client.Transport('localhost:18080', '01234567', mac)
        transport.opener = Opener(replies)
        sleeps = []
        cli = client.Installer(transport, mac, 'localhost:18080', Path(folder)/'receipt.json',
                               sleep=sleeps.append)
        cli.record = dict(operation_id='1'*32, expected_manifest='0'*64, expected_version=0,
                          original_boot=1)
        cli.manifest = dict(digest='2'*64, version=1, apps=[])
        return cli, transport.opener, sleeps

    cli, wire, sleeps = installer([busy, oom, missing])
    original = dict(cli.record)
    assert cli.query() == missing and len(sleeps) == 2 and cli.record == original
    assert all('operation_id=' + '1'*32 in url for _, url in wire.calls)
    assert not cli.path.exists()

    cli, wire, sleeps = installer([busy, missing])
    assert cli.mutate('POST', 'update/begin') == missing
    assert [method for method, _ in wire.calls] == ['POST', 'GET'] and sleeps

    active = dict(device_mac=mac, protocol=3, operation_id='1'*32,
                  candidate_manifest='2'*64, candidate_version=1, old_manifest='0'*64,
                  old_version=0, received=[0]*8, changed_mask=0, ready_mask=0,
                  sequence=1, phase='receiving')
    done = dict(active, phase='cancelled', sequence=2)
    cli, wire, sleeps = installer([(200, active), busy, (200, active), (200, active), (200, done)])
    cli.load_receipt = lambda: None
    assert cli.cancel()['phase'] == 'cancelled' and sleeps
    assert [method for method, _ in wire.calls] == ['GET', 'POST', 'GET', 'GET', 'POST']

    for status, error in [(401, 'device_code'), (429, 'device_code_rate_limited'),
                          (503, 'device_code_unavailable'), (400, 'json'), (413, 'body_limit')]:
        value = dict(error=error, stage='manual_auth', action='read_device_status')
        cli, wire, sleeps = installer([(status, value)])
        assert cli.mutate('POST', 'update/cancel') == (status, value)
        assert not sleeps and len(wire.calls) == 1
        text = str(client.rejection(status, value))
        assert error in text and str(status) in text and 'manual_auth' in text and 'read_device_status' in text
        cli, _, _ = installer([(status, value)])
        cli.load_receipt = lambda: None
        rejects(cli.cancel, error)
        client.check_response(status, dict(value, device_mac=mac), mac)
        rejects(lambda: client.check_response(status, dict(value, device_mac='112233445566'), mac), 'identity mismatch')

    # Initial status backoff must happen before a receipt or begin request exists.
    empty = bytearray(64); empty[:4] = b'AMF3'
    struct.pack_into('<HHIHHQH', empty, 4, 1, 64, 64, 0, 160, 1, 0)
    empty[32:64] = hashlib.sha256(empty).digest()
    cli, wire, sleeps = installer([busy, (401, dict(error='device_code', stage='manual_auth'))])
    cli.path = Path(folder)/'initial-receipt.json'
    rejects(lambda: cli.install(bytes(empty), []), 'device_code')
    assert sleeps and not cli.path.exists() and all(method == 'GET' for method, _ in wire.calls)

    for status in (200, 202, 404, 409):
        for identity in ({}, dict(device_mac='112233445566')):
            rejects(lambda: client.check_response(status, dict(identity, protocol=3), mac), 'identity mismatch')
    rejects(lambda: client.check_response(400, dict(error_code='bad_package'), mac), 'identity mismatch')
    cli, _, _ = installer([(200, dict(done, device_mac='112233445566'))])
    rejects(cli.query, 'identity mismatch')
    cli, _, _ = installer([(200, dict(done, operation_id='3'*32))])
    rejects(cli.query, 'fence mismatch')
    # An explicit wrong identity fails immediately, including transient errors.
    cli, _, _ = installer([(409, dict(busy[1], device_mac='112233445566')), missing])
    original = dict(cli.record)
    rejects(cli.query, 'identity mismatch')
    assert cli.record == original

print('maintenance errors: transport, retries, cancellation, rejection details, identity and transaction fences passed')
