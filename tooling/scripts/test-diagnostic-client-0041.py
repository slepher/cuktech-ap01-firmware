"""Offline binary/partial/ramlog checks; synthetic credentials only."""
import importlib.util
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import zlib

spec=importlib.util.spec_from_file_location('diagnostic',Path(__file__).with_name('diagnostic-client-0041.py'))
client=importlib.util.module_from_spec(spec);spec.loader.exec_module(client)
mac='0200000000A1'


def response(raw, total=3):
    value={'boot_id':7,'offset':0,'length':len(raw),'data_hex':raw.hex(),'crc32':zlib.crc32(raw)}
    if total is not None:value.update(total_bytes=total,eof=len(raw)==total)
    return value


with tempfile.TemporaryDirectory(prefix='ap01-diag-client-') as directory:
    root=Path(directory);token=root/'token.json';token.write_text(json.dumps({'device_mac':mac,'token':'a'*32}))
    for name,operation,raw,total,length in [('binary','file',b'\x00\xffA',3,None),('empty-log','file',b'',None,1024),('short-flash','flash',b'A',0x1000000,1024)]:
        out=root/name
        args=['diagnostic','--host','127.0.0.1:1','--token-file',str(token),'--mac',mac,
              '--operation',operation,'--output',str(out),'--path','/dev/ramlog' if total is None else '/data/wapi.conf']
        if length is not None:args+=['--length',str(length)]
        def request(host,credential,identity,op,body=None):
            assert credential=='a'*32 and identity==mac
            return {'boot_id':7} if op=='status' else response(raw,total)
        with patch('sys.argv',args),patch.object(client,'request',request),patch('builtins.print'):
            if name=='short-flash':
                try:client.main()
                except ValueError:pass
                else:raise AssertionError('short flash accepted')
                assert not out.exists() and out.with_name(name+'.partial').exists()
            else:
                client.main();assert out.read_bytes()==raw
                assert json.loads(out.with_name(name+'.json').read_text())['bytes']==len(raw)
    invalid=response(b'A');invalid['crc32']^=1
    try:client.chunk(invalid,0,1,7)
    except ValueError:pass
    else:raise AssertionError('corrupt chunk accepted')
print('0041 diagnostic client: passed')
