"""0041 reboot-switch collection client. Full AMF3 plus one or more changed APX2 files."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import struct
import time
import uuid
from app_set_client_v3 import inspect_manifest, inspect_packages, changed_packages, verify_running, check_capabilities

_spec=importlib.util.spec_from_file_location('legacy_app_client',Path(__file__).with_name('app-update-client-0041.py'))
legacy=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(legacy)
Uncertain=legacy.Uncertain
TERMINAL=legacy.TERMINAL


class Transport(legacy.Transport):
    def __call__(self,method,endpoint,params=None,body=None,binary=False):
        return super().__call__(method,'v3/'+endpoint,params,body,binary)


class Installer(legacy.Installer):
    # Reuse durable receipt writes, transport deadlines and bounded backoff.
    def load_receipt(self):
        self.record=json.loads(self.path.read_text())
        r=self.record
        if (r.get('protocol')!=3 or r.get('device_mac')!=self.mac or r.get('host')!=self.host
                or not re.fullmatch(r'[0-9a-f]{32}',r.get('operation_id','')) or r['operation_id']=='0'*32
                or not re.fullmatch(r'[0-9a-f]{64}',r.get('expected_manifest',''))
                or type(r.get('expected_version')) is not int or not 0<=r['expected_version']<2**64
                or type(r.get('original_boot')) is not int or not 0<r['original_boot']<2**64):
            raise ValueError('invalid collection receipt identity')
        self.manifest=inspect_manifest(bytes.fromhex(r['manifest_hex']))

    def checked(self,status,value,operation=True):
        if value.get('device_mac')!=self.mac:
            raise ValueError('wrong device')
        if status not in (200,202):
            return status,value
        if value.get('protocol')!=3:
            raise ValueError('protocol v3 required')
        if not operation:
            return status,value
        r=self.record
        if (value.get('operation_id')!=r['operation_id'] or value.get('candidate_manifest')!=self.manifest['digest']
                or value.get('candidate_version')!=self.manifest['version']
                or value.get('old_manifest')!=r['expected_manifest'] or value.get('old_version')!=r['expected_version']):
            raise ValueError('operation/manifest fence mismatch')
        offsets=value.get('received');mask=value.get('changed_mask');ready=value.get('ready_mask');seq=value.get('sequence')
        if (type(mask) is not int or mask<0 or mask>>len(self.manifest['apps']) or type(ready) is not int
                or ready<0 or ready&~mask or type(seq) is not int or seq<1
                or not isinstance(offsets,list) or len(offsets)!=8):
            raise ValueError('invalid transaction progress')
        old=r.get('result',{})
        if old and (mask!=old['changed_mask'] or seq<old['sequence'] or ready&old['ready_mask']!=old['ready_mask']):
            raise ValueError('transaction progress regressed')
        for i,n in enumerate(offsets):
            maximum=self.manifest['apps'][i]['package_bytes'] if mask&(1<<i) else 0
            if type(n) is not int or not 0<=n<=maximum or (old and n<old['received'][i]):
                raise ValueError('acknowledged offset regressed or exceeds package')
        if old.get('phase') in TERMINAL and value.get('phase')!=old['phase']:
            raise ValueError('terminal decision changed')
        r['result']=value;r['acknowledged']=True
        legacy.persist(self.path,r)
        return status,value

    def query(self):
        while True:
            if self.clock()>=self.deadline:
                raise Uncertain('budget expired; resume the same receipt')
            try:
                status,value=self.checked(*self.request('GET','update/result',{'operation_id':self.record['operation_id']}))
                if status==404 and self.record.get('acknowledged'):
                    raise ValueError('acknowledged receipt expired; never create a replacement transaction')
                if status!=503 and not (status==409 and value.get('error')=='maintenance_busy'):
                    return status,value
            except Uncertain:
                pass
            self.pause()

    def mutate(self,method,endpoint,body=None,extra=None,binary=False):
        if self.clock()>=self.deadline:
            raise Uncertain('budget expired; resume the same receipt')
        params=dict(extra or {},operation_id=self.record['operation_id'])
        try:
            status,value=self.checked(*self.request(method,endpoint,params,body,binary))
            if status!=503:
                return status,value
        except Uncertain:
            pass
        return self.query()

    def install(self,manifest_blob,blobs):
        wanted=inspect_manifest(manifest_blob);packages=inspect_packages(wanted,blobs)
        if self.path.exists():
            self.load_receipt()
            if self.record['manifest_hex']!=manifest_blob.hex():
                raise ValueError('receipt belongs to a different manifest')
            status,value=self.query()
        else:
            status,value=self.checked(*self.request('GET','status'),operation=False)
            if (status!=200 or value.get('phase') not in {'idle','succeeded','failed_rolled_back','cancelled'}
                    or value.get('cleanup_pending') or value.get('runtime_reporting') is not True):
                raise ValueError('device is not ready for a collection transaction')
            old=value.get('candidate_manifest') if value['phase']=='succeeded' else value.get('old_manifest','0'*64)
            version=value.get('candidate_version') if value['phase']=='succeeded' else value.get('old_version',0)
            boot=value.get('boot_id')
            if (not isinstance(old,str) or not re.fullmatch(r'[0-9a-f]{64}',old)
                    or type(version) is not int or not 0<=version<wanted['version']
                    or bool(version)!=(old!='0'*64) or type(boot) is not int or not 0<boot<2**64
                    or len(wanted['apps'])>value.get('app_max',0)):
                raise ValueError('invalid current collection/boot or app limit')
            check_capabilities(wanted,value)
            self.manifest=wanted
            self.record=dict(protocol=3,device_mac=self.mac,host=self.host,operation_id=uuid.uuid4().hex,
                             manifest_hex=manifest_blob.hex(),expected_manifest=old,expected_version=version,original_boot=boot)
            legacy.persist(self.path,self.record,create=True)
            status=404
        while True:
            if self.clock()>=self.deadline:
                raise Uncertain('budget expired; resume the same receipt')
            if status==404 and not self.record.get('acknowledged'):
                header=bytearray(64);header[:4]=b'ASB3';struct.pack_into('<HH',header,4,1,64)
                header[8:40]=bytes.fromhex(self.record['expected_manifest'])
                struct.pack_into('<QI',header,40,self.record['expected_version'],len(manifest_blob))
                status,value=self.mutate('POST','update/begin',bytes(header)+manifest_blob,binary=True)
                if status==404:self.pause()
                continue
            if status==409 and (value.get('error_code')=='write_drain_pending' or value.get('error')=='maintenance_busy'):
                self.pause();status,value=self.query();continue
            if status not in (200,202):
                raise ValueError('update rejected: '+str(value.get('error_code',status)))
            phase=value.get('phase')
            if phase in TERMINAL:
                if phase!='succeeded' or verify_running(value,wanted,self.record['original_boot']):
                    return value
                self.pause();status,value=self.query();continue
            if phase=='receiving':
                changed=changed_packages(wanted,packages,value['changed_mask'])
                pending=[i for i in changed if not value['ready_mask']&(1<<i)]
                if pending:
                    i=pending[0];offset=value['received'][i];blob=changed[i]
                    if offset<len(blob):
                        maximum=value.get('chunk_max')
                        if type(maximum) is not int or not 1<=maximum<=1024:raise ValueError('invalid chunk limit')
                        part=blob[offset:offset+maximum]
                        status,value=self.mutate('PUT',f'package/{i}/chunk',part,
                            dict(offset=offset,sha256=legacy.hashlib.sha256(part).hexdigest()),True)
                        if status in (200,202) and value['received'][i]==offset:self.pause()
                    else:status,value=self.mutate('POST',f'package/{i}/ready')
                    continue
            if phase in ('receiving','ready'):
                status,value=self.mutate('POST','update/commit');continue
            if phase not in ('switch_pending','trial_started','rollback_pending','rollback_started'):
                raise ValueError('unknown transaction phase')
            self.pause();status,value=self.query()

    def cancel(self):
        self.load_receipt();status,value=self.query()
        while status in (200,202):
            if value.get('phase') in TERMINAL:return value
            status,value=self.mutate('POST','update/cancel')
            if status==409 and value.get('error_code')=='write_drain_pending':
                self.pause();status,value=self.query();continue
            if status in (200,202) and value.get('phase') not in TERMINAL:
                self.pause();status,value=self.query()
        raise ValueError('cancel rejected: '+str(value.get('error_code',status)))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',required=True);p.add_argument('--mac',required=True)
    p.add_argument('--code-file',type=Path,required=True)
    p.add_argument('--action',choices=('install','status','result','cancel'),default='install')
    p.add_argument('--receipt',type=Path);p.add_argument('--manifest',type=Path)
    p.add_argument('--package',type=Path,action='append',default=[]);p.add_argument('--budget',type=float,default=180)
    a=p.parse_args()
    if not re.fullmatch(r'[0-9a-fA-F]{12}',a.mac) or not 1<=a.budget<=3600:p.error('MAC and bounded budget required')
    if a.action!='status' and not a.receipt:p.error('--receipt required')
    if a.action=='install' and not a.manifest:p.error('--manifest required')
    try:
        mac=a.mac.upper();transport=Transport(a.host,a.code_file.read_text().strip(),mac)
        if a.action=='status':
            status,value=transport('GET','status');print(json.dumps(value));return 0 if status==200 else 1
        installer=Installer(transport,mac,a.host,a.receipt,a.budget)
        if a.action=='result':installer.load_receipt();status,value=installer.query()
        elif a.action=='cancel':value=installer.cancel();status=200
        else:value=installer.install(a.manifest.read_bytes(),[p.read_bytes() for p in a.package]);status=200
        print(json.dumps(value))
        if a.action=='result':return 0 if status in (200,202) else 1
        return 0 if value.get('phase') in ({'succeeded'} if a.action=='install' else {'cancelled','failed_rolled_back'}) else 1
    except Uncertain as error:
        print(json.dumps({'state':'unknown','error':str(error),'receipt':str(a.receipt)}));return 2
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'state':'rejected','error':str(error)}));return 1


if __name__=='__main__':raise SystemExit(main())
