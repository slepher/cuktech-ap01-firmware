#!/usr/bin/env python3
"""Authenticated AP01 native NSH client. Does not install firmware or retry commands."""
import argparse
import json
from pathlib import Path
import socket
import sys
import threading
import zlib


def line(connection,limit=128):
    data=bytearray()
    while len(data)<limit:
        byte=connection.recv(1)
        if not byte:raise ConnectionError('console closed before greeting')
        data+=byte
        if byte==b'\n':return bytes(data)
    raise ValueError('oversized console greeting')


def connect(args,key):
    connection=socket.create_connection((args.host,args.port),timeout=10)
    try:
        request=('GET /diagnostic HTTP/1.1\r\nHost: '+args.host+'\r\n'
                 'Authorization: Bearer '+key+'\r\nConnection: Upgrade\r\n'
                 'Upgrade: ap01-diag/1\r\n\r\n')
        connection.sendall(request.encode('ascii'))
        if line(connection)!=b'HTTP/1.1 101 Switching Protocols\r\n':
            raise ConnectionError('diagnostic upgrade rejected')
        headers={};size=0
        while True:
            header=line(connection,256);size+=len(header)
            if size>1024:raise ValueError('oversized upgrade response')
            if header==b'\r\n':break
            name,value=header.rstrip(b'\r\n').split(b':',1)
            name=name.lower()
            if name in headers:raise ValueError('duplicate upgrade header')
            headers[name]=value.strip().lower()
        if headers.get(b'upgrade')!=b'ap01-diag/1' or headers.get(b'connection')!=b'upgrade':
            raise ValueError('invalid upgrade response')
        connection.settimeout(args.timeout)
        return connection
    except Exception:
        connection.close();raise


def flash_dump(args,key,output):
    address=args.address;remaining=args.length
    while remaining:
        count=min(args.chunk_bytes,remaining)
        with connect(args,key) as connection:
            connection.sendall(f'FLASH\n{address:08x} {count:08x}\n'.encode('ascii'))
            fields=line(connection).split()
            if len(fields)!=4 or fields[:2]!=[b'OK',b'FLASH'] or int(fields[2])!=count:
                raise ValueError('physical Flash read rejected')
            expected=int(fields[3],16);data=bytearray()
            while len(data)<count:
                block=connection.recv(min(4096,count-len(data)))
                if not block:raise ConnectionError('truncated Flash response')
                data.extend(block)
            if zlib.crc32(data)!=expected:raise ValueError('Flash transfer CRC mismatch')
            output.write(data);output.flush()
        address+=count;remaining-=count


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',required=True)
    parser.add_argument('--port',type=int,default=18080)
    parser.add_argument('--auth-key-file',type=Path,required=True,
                        help='current device menu code (8 digits); historical rescue 64hex keys also accepted')
    parser.add_argument('--command',action='append',default=[],help='explicit native NSH command; sent once')
    parser.add_argument('--operation',choices=('shell','status','logs','flash','interrupt','close'),default='shell')
    parser.add_argument('--address',type=lambda v:int(v,0),default=0,help='physical NOR offset for flash reads')
    parser.add_argument('--length',type=lambda v:int(v,0),default=65536,help='flash bytes, split into checked 64 KiB chunks')
    parser.add_argument('--chunk-bytes',type=lambda v:int(v,0),default=65536,help='physical read bytes per connection, 1..65536')
    parser.add_argument('--output',type=Path,help='new binary transcript, never overwritten')
    parser.add_argument('--timeout',type=float,default=120)
    args=parser.parse_args()
    key=args.auth_key_file.read_text(encoding='ascii').strip()
    if not ((len(key)==8 and all(c in '0123456789' for c in key)) or
            (len(key)==64 and all(c in '0123456789abcdefABCDEF' for c in key))):
        parser.error('8 digit device menu code or historical 64 hex key required')
    if not 1<=args.port<=65535 or not 1<=args.timeout<=3600:parser.error('invalid port/timeout')
    if any('\n' in c or '\r' in c or '\0' in c for c in args.command):parser.error('one command per --command')
    if args.command and args.operation!='shell':parser.error('commands require shell operation')
    if args.operation=='flash' and (not args.output or not 1<=args.length<=0x1000000 or not 0<=args.address<=0x1000000-args.length or not 1<=args.chunk_bytes<=65536):
        parser.error('flash requires --output and a valid range inside 16 MiB NOR')
    output=args.output.open('xb') if args.output else sys.stdout.buffer
    try:
        if args.operation=='flash':flash_dump(args,key,output);return
        with connect(args,key) as connection:
            connection.sendall(args.operation.upper().encode('ascii')+b'\n')
            admission=line(connection,2048 if args.operation=='status' else 128)
            if args.operation!='shell':
                if admission.startswith(b'ERR '):raise ConnectionError('control operation rejected')
                if args.operation=='logs':
                    fields=admission.split()
                    if fields[:2]!=[b'OK',b'LOGS'] or len(fields)!=3:raise ValueError('invalid log framing')
                    remaining=int(fields[2])
                    if not 0<=remaining<=8192:raise ValueError('invalid log size')
                    while remaining:
                        data=connection.recv(min(4096,remaining))
                        if not data:raise ConnectionError('truncated log snapshot')
                        output.write(data);remaining-=len(data)
                    output.flush();return
                if args.operation=='status':
                    status=json.loads(admission)
                    if status.get('protocol')!='AP01-DIAG/1':raise ValueError('invalid status protocol')
                elif admission!=b'OK SIGNAL\n':raise ValueError('invalid signal response')
                output.write(admission);output.flush();return
            if admission!=b'OK SHELL\n':raise ConnectionError('shell admission rejected')
            connection.settimeout(args.timeout)
            if args.command:
                connection.sendall(('\n'.join(args.command)+'\nexit\n').encode('utf-8'))
            else:
                def input_loop():
                    try:
                        for command in sys.stdin:
                            connection.sendall(command.rstrip('\r\n').encode('utf-8')+b'\n')
                        connection.shutdown(socket.SHUT_WR)
                    except OSError:pass
                threading.Thread(target=input_loop,daemon=True).start()
            received=0;prefix=bytearray()
            while True:
                try:
                    data=connection.recv(4096)
                except KeyboardInterrupt:
                    # Raw TCP has no terminal driver to translate ETX into a
                    # signal. Use a separate authenticated control connection.
                    with connect(args,key) as controller:
                        controller.sendall(b'INTERRUPT\n')
                        if line(controller)!=b'OK SIGNAL\n':
                            raise ConnectionError('native interrupt rejected')
                    continue
                if not data:break
                received+=len(data)
                if len(prefix)<64:prefix.extend(data[:64-len(prefix)])
                if received>16*1024*1024:raise ValueError('16 MiB transcript limit reached')
                output.write(data);output.flush()
            if prefix.startswith(b'ERR spawn\n'):raise ConnectionError('native shell creation failed')
    finally:
        if args.output:output.close()


if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as error:
        print('Console stopped: '+type(error).__name__,file=sys.stderr);sys.exit(2)
