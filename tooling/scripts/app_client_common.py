"""Shared App-set transport, durable receipts and bounded retry budget."""
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
        if not isinstance(value, dict):
            raise ValueError('response must be a JSON object')
        return response.code, value


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
