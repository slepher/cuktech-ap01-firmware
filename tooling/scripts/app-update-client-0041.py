"""0041 App installation client. No ROM writes; credentials never enter receipts."""
import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import struct
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

TERMINAL = {'succeeded', 'failed_rolled_back', 'cancelled', 'recovery_required'}


class Uncertain(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Transport:
    def __init__(self, host, code, mac):
        parsed = urllib.parse.urlsplit('http://' + host)
        if not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
            raise ValueError('host must be hostname:port only')
        if not re.fullmatch(r'[0-9]{8}', code):
            raise ValueError('menu code must contain eight digits')
        self.base, self.code, self.mac = 'http://' + host, code, mac
        self.deadline, self.clock = None, time.monotonic
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def __call__(self, method, endpoint, params=None, body=None, binary=False):
        url = self.base + '/api/app/' + endpoint
        if params:
            url += '?' + urllib.parse.urlencode(dict(params, device_mac=self.mac))
        data = body if binary else None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(url, data=data, method=method, headers={
            'Authorization': 'Bearer ' + self.code,
            'Content-Type': 'application/octet-stream' if binary else 'application/json'})
        timeout = 15 if self.deadline is None else min(15, self.deadline - self.clock())
        if timeout <= 0:
            raise Uncertain('budget expired before request')
        try:
            response = self.opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            response = error
        except (OSError, urllib.error.URLError) as error:
            raise Uncertain('network outcome unknown; query the original operation') from error
        try:
            with response:
                raw = response.read(8193)
        except (OSError, http.client.HTTPException) as error:
            raise Uncertain('response interrupted; query original operation') from error
        try:
            if len(raw) > 8192:
                raise ValueError('response exceeds limit')
            value = json.loads(raw)
        except json.JSONDecodeError as error:
            raise Uncertain('incomplete response; query original operation') from error
        if not isinstance(value, dict) or value.get('device_mac') != self.mac:
            raise ValueError('response device identity mismatch')
        return response.code, value


def inspect_package(blob):
    if len(blob) < 256 or blob[:4] != b'APX2' or struct.unpack_from('<III', blob, 4) != (2, 256, len(blob)):
        raise ValueError('invalid APX2 header/length')
    digest = hashlib.sha256(blob[:192] + bytes(32) + blob[224:]).digest()
    if digest != blob[192:224]:
        raise ValueError('APX2 content SHA256 mismatch')
    for offset, label in ((128, 'App ID'), (160, 'App version')):
        raw = blob[offset:offset+32]
        text = raw.split(b'\0', 1)[0]
        if not re.fullmatch(rb'[A-Za-z0-9._+\-]{1,31}', text) or raw[len(text):] != bytes(32-len(text)):
            raise ValueError('invalid ' + label)
    return blob[128:160].split(b'\0', 1)[0].decode('ascii'), digest.hex()


def persist(path, value, create=False):
    payload = (json.dumps(value, indent=2) + '\n').encode()
    if create:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(payload); stream.flush(); os.fsync(stream.fileno())
    else:
        descriptor, name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(payload); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


class Installer:
    def __init__(self, request, mac, host, receipt, budget=180, clock=time.monotonic, sleep=time.sleep):
        self.request, self.mac, self.host, self.path = request, mac, host, receipt
        self.clock, self.sleep = clock, sleep
        self.deadline = clock() + budget
        if isinstance(request, Transport):
            request.deadline, request.clock = self.deadline, clock
        self.delay = 0.25
        self.record = None
        self.acknowledged = 0

    def pause(self):
        remaining = self.deadline - self.clock()
        if remaining <= 0:
            raise Uncertain('budget expired; resume using the same receipt')
        self.sleep(min(self.delay, remaining))
        self.delay = min(self.delay * 2, 2)

    def checked(self, status, value, operation=True):
        if value.get('device_mac') != self.mac:
            raise ValueError('wrong device')
        if status in (200, 202) and operation:
            if value.get('operation_id') != self.record['operation_id'] or value.get('target_sha256') != self.record['content_sha256']:
                raise ValueError('receipt operation/package mismatch')
            offset = value.get('received')
            if type(offset) is not int or not 0 <= offset <= self.record['length'] or value.get('length') != self.record['length']:
                raise ValueError('invalid acknowledged offset/length')
            if offset < self.acknowledged:
                raise ValueError('device acknowledged offset regressed')
            self.acknowledged = offset
            previous = self.record.get('result', {})
            if previous.get('phase') in TERMINAL and value.get('phase') != previous['phase']:
                raise ValueError('device terminal receipt regressed or changed')
        return status, value

    def query(self):
        while True:
            if self.clock() >= self.deadline:
                raise Uncertain('budget expired; query original operation')
            try:
                status, value = self.checked(*self.request('GET', 'update/result', {'operation_id': self.record['operation_id']}))
                if status != 503:
                    return status, value
            except Uncertain:
                pass
            self.pause()

    def mutate(self, method, endpoint, body=None, extra=None, binary=False):
        params = dict(extra or {}, operation_id=self.record['operation_id'])
        try:
            status, value = self.checked(*self.request(method, 'update/' + endpoint, params, body, binary))
            if status != 503:
                return status, value
        except Uncertain:
            pass
        # Never invent another operation or assume the request failed.
        return self.query()

    def load_receipt(self):
        self.record = json.loads(self.path.read_text())
        if (self.record.get('device_mac') != self.mac or self.record.get('host') != self.host
                or not re.fullmatch(r'[0-9a-f]{32}', self.record.get('operation_id', ''))
                or not re.fullmatch(r'[0-9a-f]{64}', self.record.get('content_sha256', ''))
                or type(self.record.get('length')) is not int or self.record['length'] < 256):
            raise ValueError('invalid receipt identity')

    def cancel(self):
        self.load_receipt()
        status, value = self.query()
        while status in (200, 202):
            if value.get('phase') in TERMINAL:
                self.record['result'] = value
                persist(self.path, self.record)
                return value
            if value.get('phase') in ('receiving', 'ready', 'switch_pending', 'trial_started'):
                status, value = self.mutate('POST', 'cancel')
            else:
                self.pause(); status, value = self.query()
            if value.get('phase') not in TERMINAL:
                self.pause()
        raise ValueError('cancel rejected: ' + value.get('error_code', str(status)))

    def install(self, blob):
        app, digest = inspect_package(blob)
        version = blob[160:192].split(b"\0", 1)[0].decode("ascii")
        identity = dict(device_mac=self.mac, host=self.host, file_sha256=hashlib.sha256(blob).hexdigest(),
                        content_sha256=digest, length=len(blob), app_id=app)
        if self.path.exists():
            self.load_receipt()
            if any(self.record.get(k) != v for k, v in identity.items()) or not re.fullmatch(r'[0-9a-f]{32}', self.record.get('operation_id', '')):
                raise ValueError('receipt does not match device, endpoint or package')
            status, value = self.query()
        else:
            status, value = self.checked(*self.request('GET', 'status'), operation=False)
            if status != 200 or value.get('cleanup_pending') or value.get('phase') not in TERMINAL | {'idle'}:
                raise ValueError('device is not ready for a new transaction')
            if value.get('runtime_reporting') is not True:
                raise ValueError('device cannot report the running App identity')
            if type(value.get('sequence')) is not int or value['sequence'] < 0 or len(blob) > value.get('package_max', 0):
                raise ValueError('invalid device limits or package too large')
            self.record = dict(identity, operation_id=uuid.uuid4().hex,
                               expected_sequence=value['sequence'], expected_current=value.get('current_sha256', '0'*64))
            persist(self.path, self.record, create=True)  # Durable ID before first mutation.
            status = 404  # No begin sent yet.
        if status == 404:
            # Explicit absence may mean the first begin was never sent. Replay
            # the SAME ID/identity and original sequence fence; never refresh it.
            body = dict(device_mac=self.mac, app_id=app, length=len(blob), sha256=digest,
                        expected_current=self.record['expected_current'], expected_sequence=self.record['expected_sequence'])
            status, value = self.mutate('POST', 'begin', body)
        while True:
            if self.clock() >= self.deadline:
                raise Uncertain('budget expired; resume using the same receipt')
            if status not in (200, 202):
                raise ValueError('operation rejected: ' + value.get('error_code', 'http_' + str(status)))
            phase = value.get('phase')
            if phase in TERMINAL:
                if phase == 'succeeded' and value.get('current_sha256') != digest:
                    raise ValueError('committed package identity mismatch')
                self.record['result'] = value
                persist(self.path, self.record)
                if phase == 'succeeded':
                    runtime = value.get('runtime')
                    if (not isinstance(runtime, dict) or runtime.get('state') != 'running'
                            or type(runtime.get('generation')) is not int
                            or not 1 <= runtime['generation'] <= 0xffffffff
                            or runtime.get('business_writes') is not True):
                        # A durable historical success is not evidence that its
                        # App is running after a restart/fault. Query only.
                        self.pause(); status, value = self.query(); continue
                    if runtime.get('sha256') != digest or runtime.get('version') != version:
                        raise ValueError('running App identity/version mismatch')
                return value
            if phase == 'receiving' and value['received'] < len(blob):
                offset = value['received']
                maximum = value.get('chunk_max')
                if type(maximum) is not int or not 1 <= maximum <= 1024:
                    raise ValueError('invalid chunk limit')
                part = blob[offset:offset+maximum]
                status, value = self.mutate('PUT', 'chunk', part,
                    dict(offset=offset, sha256=hashlib.sha256(part).hexdigest()), True)
                if status in (200, 202) and value.get('received') == offset:
                    self.pause()
            elif phase in ('receiving', 'ready'):
                status, value = self.mutate('POST', 'commit')
                if status in (200, 202) and value.get('phase') == 'ready':
                    self.pause()  # stop_pending: query then retry same idempotent commit.
            elif phase in ('switch_pending', 'trial_started', 'rollback_pending', 'rollback_started'):
                self.pause(); status, value = self.query()
            else:
                raise ValueError('unknown transaction phase')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True)
    parser.add_argument('--mac', required=True)
    parser.add_argument('--code-file', type=Path, required=True, help='file containing current eight-digit menu code')
    parser.add_argument('--action', choices=('install', 'status', 'result', 'cancel'), default='install')
    parser.add_argument('--receipt', type=Path, help='new receipt, or existing receipt to resume/query/cancel')
    parser.add_argument('--package', type=Path)
    parser.add_argument('--budget', type=float, default=180)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9A-Fa-f]{12}', args.mac) or not 1 <= args.budget <= 3600:
        parser.error('explicit 12-digit MAC and budget 1..3600 required')
    if args.action != 'status' and not args.receipt:
        parser.error('--receipt required for this action')
    if args.action == 'install' and not args.package:
        parser.error('--package required for install')
    try:
        transport = Transport(args.host, args.code_file.read_text().strip(), args.mac)
        if args.action == 'status':
            status, value = transport('GET', 'status')
            print(json.dumps(value))
            return 0 if status == 200 else 1
        installer = Installer(transport, args.mac, args.host, args.receipt, args.budget)
        if args.action == 'result':
            installer.load_receipt()
            status, value = installer.query()
            print(json.dumps(value))
            return 0 if status in (200, 202) else 1
        if args.action == 'cancel':
            value = installer.cancel()
            print(json.dumps(value))
            return 0 if value['phase'] in ('cancelled', 'failed_rolled_back') else 1
        result = installer.install(args.package.read_bytes())
        print(json.dumps(result))
        return 0 if result['phase'] == 'succeeded' else 1
    except Uncertain as error:
        print(json.dumps({'state': 'unknown', 'error': str(error), 'receipt': str(args.receipt)}))
        return 2
    except (ValueError, OSError) as error:
        print(json.dumps({'state': 'rejected', 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
