#!/usr/bin/env python3
"""Offline diagnostic protocol, actual journal and local fake-server client checks."""
import argparse
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import zlib


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cc',default='gcc')
    args=parser.parse_args()
    if args.output.exists():parser.error('new report required')
    root=Path(__file__).resolve().parents[2];source=root/'tooling/firmware-modules'
    cases=[]
    with tempfile.TemporaryDirectory(prefix='diagnostics-',dir=args.output.parent) as temporary:
        work=Path(temporary)
        for name,files in [('auth',['diagnostic_console.c','test_diagnostic_console.c']),
                           ('journal',['test_ota_0031_log.c','ota_channel.c','ota_image.c'])]:
            binary=work/name
            command=[args.cc,'-std=c11','-Wall','-Wextra','-Werror','-O1','-g',
                     '-fsanitize=address,undefined','-fno-pie','-no-pie',
                     *[str(source/f) for f in files],'-o',str(binary)]
            subprocess.run(command,check=True,capture_output=True,text=True,timeout=30)
            run=subprocess.run([str(binary)],check=True,capture_output=True,text=True,timeout=20)
            assert not run.stderr;cases.append(dict(name=name,result=json.loads(run.stdout)))
        key='0123456789abcdef'*4;keyfile=work/'test.key';keyfile.write_text(key)
        script=root/'tooling/scripts/diagnostic-console-0031.py'
        def case(mode,expected,operation='shell'):
            transcript=work/(mode+'.out');observed=[];errors=[]
            listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1)
            port=listener.getsockname()[1]
            def read_line(c):
                out=bytearray()
                while len(out)<256:
                    b=c.recv(1)
                    if not b:break
                    out+=b
                    if b==b'\n':break
                return bytes(out)
            log=b'{"stage":"boot"}\n'
            def serve():
                try:
                    with listener:
                        listener.settimeout(4)
                        c,_=listener.accept()
                        with c:
                            c.settimeout(4)
                            assert read_line(c)==b'GET /diagnostic HTTP/1.1\r\n'
                            headers=[]
                            while True:
                                header=read_line(c)
                                if header==b'\r\n':break
                                headers.append(header)
                            assert b'Authorization: Bearer '+key.encode()+b'\r\n' in headers
                            if mode=='rejected':c.sendall(b'HTTP/1.1 401 Error\r\n\r\n');return
                            c.sendall(b'HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: ap01-diag/1\r\n\r\n');observed.append(read_line(c).decode().strip())
                            if mode=='busy':c.sendall(b'ERR busy\n');return
                            if operation=='status':c.sendall(json.dumps({'protocol':'AP01-DIAG/1','padding':'x'*400}).encode()+b'\n');return
                            if operation=='logs':
                                c.sendall(f'OK LOGS {len(log)+(mode=="truncated_logs")}\n'.encode())
                                for b in log:c.sendall(bytes([b]))
                                return
                            if operation in ('interrupt','close'):c.sendall(b'OK SIGNAL\n');return
                            if operation=='flash':
                                assert read_line(c)==b'00000100 00000020\n'
                                data=bytes(range(32));crc=zlib.crc32(data)^(mode=='flash_crc_failure')
                                c.sendall(f'OK FLASH 32 {crc:08x}\n'.encode())
                                c.sendall(data[:-1] if mode=='flash_truncated' else data);return
                            c.sendall(b'OK SHELL\n')
                            while True:
                                command=read_line(c).decode().strip();observed.append(command)
                                if command=='exit':break
                            c.sendall(b'ERR spawn\n' if mode=='spawn_failure' else b'nsh> fixture ps\n')
                except Exception as error:errors.append(type(error).__name__)
            thread=threading.Thread(target=serve,daemon=True);thread.start()
            command=[sys.executable,str(script),'--host','127.0.0.1','--port',str(port),
                     '--auth-key-file',str(keyfile),'--output',str(transcript),'--operation',operation]
            if operation=='shell':command+=['--command','ps']
            if operation=='flash':command+=['--address','0x100','--length','32']
            result=subprocess.run(command,capture_output=True,timeout=10)
            thread.join(5);assert not thread.is_alive() and not errors,errors
            assert result.returncode==expected,(mode,result.stderr)
            assert key.encode() not in result.stdout+result.stderr+transcript.read_bytes()
            if mode in ('shell','spawn_failure'):assert observed==['SHELL','ps','exit']
            if mode=='logs':assert transcript.read_bytes()==log
            if mode=='flash':assert transcript.read_bytes()==bytes(range(32))
            if mode in ('flash_crc_failure','flash_truncated'):assert not transcript.read_bytes()
            cases.append(dict(name=mode,passed=True))
        for mode,expected,operation in [('shell',0,'shell'),('rejected',2,'shell'),('busy',2,'shell'),
                ('spawn_failure',2,'shell'),('status',0,'status'),('logs',0,'logs'),
                ('truncated_logs',2,'logs'),('interrupt',0,'interrupt'),('close',0,'close'),
                ('flash',0,'flash'),('flash_crc_failure',2,'flash'),('flash_truncated',2,'flash')]:
            case(mode,expected,operation)
        # Cross a 64 KiB boundary: the second authenticated request must use
        # the next physical address; a single-chunk fixture cannot prove it.
        listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(2)
        port=listener.getsockname()[1];errors=[]
        expected=bytes(range(256))*256+b'Z'
        def chunks():
            try:
                with listener:
                    listener.settimeout(5)
                    for address,data in [(0,expected[:65536]),(65536,expected[65536:])]:
                        connection,_=listener.accept()
                        with connection:
                            connection.settimeout(5);stream=connection.makefile('rb')
                            assert stream.readline()==b'GET /diagnostic HTTP/1.1\r\n'
                            headers=[]
                            while True:
                                header=stream.readline()
                                if header==b'\r\n':break
                                headers.append(header)
                            assert b'Authorization: Bearer '+key.encode()+b'\r\n' in headers
                            connection.sendall(b'HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: ap01-diag/1\r\n\r\n')
                            assert stream.readline()==b'FLASH\n'
                            assert stream.readline()==f'{address:08x} {len(data):08x}\n'.encode()
                            connection.sendall(f'OK FLASH {len(data)} {zlib.crc32(data):08x}\n'.encode()+data)
                            stream.close()
            except Exception as error:errors.append(type(error).__name__)
        thread=threading.Thread(target=chunks,daemon=True);thread.start()
        transcript=work/'multichunk.bin'
        run=subprocess.run([sys.executable,str(script),'--host','127.0.0.1','--port',str(port),
            '--auth-key-file',str(keyfile),'--operation','flash','--length','65537',
            '--output',str(transcript)],capture_output=True,timeout=15)
        thread.join(6)
        assert not thread.is_alive() and not errors,errors
        assert run.returncode==0 and transcript.read_bytes()==expected,run.stderr
        cases.append(dict(name='flash_multichunk',passed=True))
    sources=[source/f for f in ('diagnostic_console.c','diagnostic_console.h','diagnostic_console_0031.c','test_diagnostic_console.c','ota_0031.c','test_ota_0031_log.c')]
    sources+=[script,Path(__file__).resolve()]
    result=dict(passed=True,cases=cases,device_accessed=False,
                native_task_isolation_verified=False,physical_boot_verified=False,
                sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
    with args.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(passed=True,cases=len(cases),report=str(args.output))))


if __name__=='__main__':main()
