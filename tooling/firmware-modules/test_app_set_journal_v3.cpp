#include "app_set_journal_v3.h"
#include "app_set_selection_v3.h"
#include "app_reboot_v3.h"
#include "app_set_download_v3.h"
#include "app_set_commit_v3.h"
#include "app_set_begin_v3.h"
#include "app_set_cleanup_v3.h"
#include "app_set_http_v3.h"
#include "app_set_service_v3.h"
#include "native_maintenance_0041.h"
#include "native_json_0041.h"
#include "native_integrity_0041.h"
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <map>
#include <string>
#include <vector>
#include <fstream>
#include <iterator>
#include <iostream>
using P=Ap01SetPhaseV3;using R=Ap01SetJournalResultV3;
static unsigned checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"line %d: %s\n",__LINE__,#x);abort();}}while(0)
static const uint8_t mac[6]={1,2,3,4,5,6};
static const char *paths[]={"/resource/app-store/update.0","/resource/app-store/update.1"};
struct Disk {
    std::map<std::string,std::vector<uint8_t>> files;
    std::string opened;
    int cut=320,journalCut=-1;bool lost=false,failOpen=false,failClose=false,failRead=false,failSize=false,failExists=false;
    bool removeLost=false,removeFails=false,checkCleanupBarrier=false;unsigned removes=0;
    uint64_t freeBytes=1u<<26;bool mkdirFails=false;
    bool renameLost=false,renameFails=false;unsigned renames=0;
    unsigned lostWriteAt=0;
    unsigned writes=0,handles=0,opens=0;size_t position=0;bool append=false;
    Ap01VfsOps ops(){Ap01VfsOps v{};v.context=this;
        v.exists=[](void *p,const char *s){auto &d=*(Disk*)p;return d.failExists?-1:int(d.files.count(s));};
        v.open=[](void *p,const char *s,unsigned flags){auto &d=*(Disk*)p;if(d.failOpen)return -1;
            CHECK(!d.handles);if(!flags&&!d.files.count(s))return -1;d.opened=s;++d.handles;++d.opens;
            if(flags==1)d.files[s].clear();d.append=flags==2;d.position=0;return 1;};
        v.close=[](void *p,int){auto &d=*(Disk*)p;CHECK(d.handles==1);--d.handles;return d.failClose?-1:0;};
        v.size=[](void *p,int)->int32_t{auto &d=*(Disk*)p;return d.failSize?-1:int32_t(d.files[d.opened].size());};
        v.read=[](void *p,int,void *b,size_t n){auto &d=*(Disk*)p;if(d.failRead)return -1;
            n=std::min(n,d.files[d.opened].size()-d.position);memcpy(b,d.files[d.opened].data()+d.position,n);d.position+=n;return int(n);};
        v.write=[](void *p,int,const void *b,size_t n){auto &d=*(Disk*)p;++d.writes;
            int cap=d.journalCut>=0&&d.opened.find("/update.")!=std::string::npos?d.journalCut:d.cut;
            size_t keep=std::min(n,size_t(cap));auto src=(const uint8_t*)b;
            if(d.append)d.files[d.opened].insert(d.files[d.opened].end(),src,src+keep);
            else d.files[d.opened].assign(src,src+keep);return d.lost||(d.lostWriteAt&&d.writes==d.lostWriteAt)?-1:int(keep);};
        v.remove=[](void *p,const char *path){auto &d=*(Disk*)p;++d.removes;
            if(d.checkCleanupBarrier)for(auto journal:paths){Ap01SetRecordV3 r;CHECK(d.files[journal].size()==320);
                CHECK(ap01DecodeSetRecordV3(d.files[journal].data(),r));
                CHECK(r.phase==P::Succeeded||r.phase==P::FailedRolledBack||r.phase==P::Cancelled);}
            if(d.removeFails)return -1;d.files.erase(path);return d.removeLost?-1:0;};
        v.mkdir=[](void *p,const char *path){auto &d=*(Disk*)p;if(d.mkdirFails)return -1;d.files[path]={};return 0;};
        v.statfs=[](void *p,const char *,uint64_t *total,uint64_t *free){*total=1u<<26;*free=((Disk*)p)->freeBytes;return 0;};
        v.rename=[](void *p,const char *from,const char *to){auto &d=*(Disk*)p;++d.renames;
            if(d.renameFails||!d.files.count(from)||d.files.count(to))return -1;
            d.files[to]=d.files[from];d.files.erase(from);return d.renameLost?-1:0;};
        v.seek=[](void *p,int,int32_t offset,unsigned whence)->int32_t{auto &d=*(Disk*)p;
            if(whence||offset<0||size_t(offset)>d.files[d.opened].size())return -1;d.position=unsigned(offset);return offset;};return v;}
};
static Ap01SetRecordV3 initial(){Ap01SetRecordV3 r{};r.sequence=1;r.newVersion=1;r.newDigest[0]=7;
    r.transaction[0]=1;r.requestDigest[0]=2;r.changedMask=3;r.changedBytes=512;
    memcpy(r.mac,mac,6);strcpy(r.principal,"owner");return r;}
static void install(Disk &d,unsigned slot,const Ap01SetRecordV3 &r){uint8_t bytes[320];CHECK(ap01EncodeSetRecordV3(r,bytes));d.files[paths[slot]]={bytes,bytes+320};}
static void crc(std::vector<uint8_t> &b){auto n=ap01_native_crc32(b.data(),316);for(unsigned i=0;i<4;++i)b[316+i]=uint8_t(n>>(8*i));}
static void codec(){auto r=initial();uint8_t b[320];Ap01SetRecordV3 decoded;
    CHECK(ap01EncodeSetRecordV3(r,b));CHECK(ap01DecodeSetRecordV3(b,decoded));CHECK(decoded.changedMask==3&&decoded.newVersion==1);
    for(unsigned i=0;i<320;++i){auto c=std::vector<uint8_t>(b,b+320);c[i]^=1;CHECK(!ap01DecodeSetRecordV3(c.data(),decoded));}
    for(unsigned i: {61u,62u,63u,76u,79u,102u,103u,265u,315u}){
        auto c=std::vector<uint8_t>(b,b+320);c[i]=1;crc(c);CHECK(!ap01DecodeSetRecordV3(c.data(),decoded));}
    auto bad=r;bad.readyMask=4;CHECK(!ap01EncodeSetRecordV3(bad,b));
    bad=r;bad.principal[6]='x';CHECK(!ap01EncodeSetRecordV3(bad,b));
    bad=r;bad.trialBoot=1;CHECK(!ap01EncodeSetRecordV3(bad,b));
    bad=r;bad.changedBytes=511;CHECK(!ap01EncodeSetRecordV3(bad,b));
    bad=r;bad.changedMask=0;bad.changedBytes=0;CHECK(ap01EncodeSetRecordV3(bad,b));
}
static void torn(){
    for(unsigned target=0;target<2;++target)for(int cut=0;cut<320;++cut){Disk d;auto a=initial();a.sequence=2-target;
        install(d,target^1,a);Ap01SetJournalV3 j(d.ops(),mac);CHECK(j.load()==R::Ok);
        auto b=a;b.readyMask=1;d.cut=cut;CHECK(j.save(b)==R::Unknown);CHECK(!j.writable());
        unsigned writes=d.writes;CHECK(j.save(b)==R::Unknown&&d.writes==writes);
        CHECK(j.load()==R::Ok);CHECK(j.current()->sequence==a.sequence&&j.current()->readyMask==0);CHECK(!d.handles);
    }
    for(int fault=0;fault<6;++fault){Disk d;auto a=initial();install(d,0,a);Ap01SetJournalV3 j(d.ops(),mac);CHECK(j.load()==R::Ok);
        auto b=a;b.readyMask=1;
        if(fault==0)d.lost=true;if(fault==1)d.failClose=true;if(fault==2)d.failOpen=true;
        if(fault==3)d.failRead=true;if(fault==4)d.failSize=true;if(fault==5)d.failExists=true;
        CHECK(j.save(b)==R::Unknown);CHECK(!j.writable());CHECK(!j.current());CHECK(!d.handles);
        d.lost=d.failClose=d.failOpen=d.failRead=d.failSize=d.failExists=false;
        CHECK(j.load()==R::Ok);CHECK(j.current()->sequence==uint64_t(fault==2?1:2));
    }
}
static void recovery(){
    Disk d;Ap01SetJournalV3 j(d.ops(),mac);CHECK(j.save(initial())==R::Unknown);CHECK(j.load()==R::Empty);
    auto r=initial();CHECK(j.save(r)==R::Ok);r.readyMask=3;r.phase=P::Ready;CHECK(j.save(r)==R::Ok);
    r.phase=P::SwitchPending;CHECK(j.save(r)==R::Ok);r.phase=P::TrialStarted;r.trialStarts=1;r.trialBoot=11;CHECK(j.save(r)==R::Ok);
    auto bad=r;bad.trialBoot=12;CHECK(j.save(bad)==R::Invalid);
    r.phase=P::Succeeded;r.cleanupPending=1;CHECK(j.save(r)==R::Ok);
    auto next=initial();next.transaction[0]=2;next.oldVersion=1;next.newVersion=2;next.oldDigest[0]=7;next.newDigest[0]=8;
    CHECK(j.save(next)==R::Invalid);r.cleanupPending=0;CHECK(j.save(r)==R::Ok);
    bad=next;bad.oldDigest[0]=6;CHECK(j.save(bad)==R::Invalid);CHECK(j.save(next)==R::Ok);CHECK(j.load()==R::Ok);
    next.readyMask=3;next.phase=P::Ready;CHECK(j.save(next)==R::Ok);next.phase=P::SwitchPending;CHECK(j.save(next)==R::Ok);
    next.phase=P::TrialStarted;next.trialStarts=1;next.trialBoot=21;CHECK(j.save(next)==R::Ok);
    next.phase=P::RollbackPending;next.error=7;CHECK(j.save(next)==R::Ok);
    next.phase=P::RollbackStarted;next.rollbackStarts=1;next.rollbackBoot=21;CHECK(j.save(next)==R::Invalid);
    next.rollbackBoot=22;CHECK(j.save(next)==R::Ok);CHECK(j.load()==R::Ok);
    next.phase=P::FailedRolledBack;CHECK(j.save(next)==R::Ok);
    auto retry=initial();retry.transaction[0]=3;retry.oldVersion=1;retry.newVersion=3;retry.oldDigest[0]=7;retry.newDigest[0]=9;
    CHECK(j.save(retry)==R::Ok);CHECK(j.load()==R::Ok);
    // Empty initial set can be rolled back without ever invoking an App.
    Disk empty;Ap01SetJournalV3 e(empty.ops(),mac);CHECK(e.load()==R::Empty);r=initial();CHECK(e.save(r)==R::Ok);
    r.phase=P::Ready;r.readyMask=3;CHECK(e.save(r)==R::Ok);r.phase=P::SwitchPending;CHECK(e.save(r)==R::Ok);
    r.phase=P::RollbackPending;r.error=1;CHECK(e.save(r)==R::Ok);r.phase=P::RollbackStarted;r.rollbackStarts=1;r.rollbackBoot=2;CHECK(e.save(r)==R::Ok);
    r.phase=P::FailedRolledBack;CHECK(e.save(r)==R::Ok);retry=initial();retry.transaction[0]=2;CHECK(e.save(retry)==R::Ok);
}
static void corrupt(){
    auto a=initial();
    for(int kind=0;kind<9;++kind){Disk d;install(d,0,a);auto b=a;
        if(kind==0)b.requestDigest[0]++;if(kind==1)b.sequence=3;
        if(kind==2){b.sequence=2;b.phase=P::TrialStarted;b.readyMask=3;b.trialStarts=1;b.trialBoot=1;}
        if(kind==3)b.mac[0]++;
        install(d,1,b);
        if(kind==4)d.files["/resource/codex-status/app-update.0"]={1};
        if(kind==5)memcpy(d.files[paths[1]].data(),"AUT2",4);
        if(kind==6)d.files[paths[1]][4]=3;
        if(kind==7){d.files[paths[0]].resize(2);d.files[paths[1]].resize(3);}
        Ap01SetJournalV3 j(d.ops(),mac);auto result=j.load();
        CHECK(result==(kind==4||kind==5?R::Legacy:kind==6?R::Unsupported:kind==8?R::Ok:R::Corrupt));
        CHECK(j.writable()==(kind==8));
    }
    for(int fault=0;fault<5;++fault){Disk d;install(d,0,a);
        d.failExists=fault==0;d.failOpen=fault==1;d.failClose=fault==2;d.failRead=fault==3;d.failSize=fault==4;
        Ap01SetJournalV3 j(d.ops(),mac);CHECK(j.load()==R::Io);CHECK(!j.writable());CHECK(!d.handles);
    }
}
struct Preflight {
    bool candidate=true,old=true;unsigned calls=0;
    static bool check(void *p,const uint8_t *digest,uint64_t version){auto &s=*(Preflight*)p;++s.calls;
        CHECK(version!=0);return digest[0]==7?s.candidate:s.old;}
};
static void selection(){
    using M=Ap01SetBootModeV3;
    for(int scenario=0;scenario<7;++scenario){Disk d;auto r=initial();r.oldVersion=1;r.oldDigest[0]=6;r.newVersion=2;
        r.phase=P::SwitchPending;r.readyMask=3;install(d,0,r);Ap01SetJournalV3 j(d.ops(),mac);CHECK(j.load()==R::Ok);
        Preflight check;check.candidate=scenario!=3;check.old=scenario!=4;
        Ap01SetSelectorV3 boot(j,10);
        if(scenario==5)d.lost=true;
        auto chosen=boot.select(&check,Preflight::check);
        if(scenario==5){CHECK(chosen.mode==M::Maintenance);CHECK(!j.current());d.lost=false;CHECK(j.load()==R::Ok);
            CHECK(j.current()->phase==P::TrialStarted);}
        else {CHECK(chosen.mode==(scenario==3?M::Rollback:M::Trial));CHECK(chosen.version==uint64_t(scenario==3?1:2));}
        CHECK(boot.select(&check,Preflight::check).mode==M::Maintenance);
        if(scenario==0){CHECK(boot.accept());CHECK(j.current()->phase==P::Succeeded);CHECK(boot.accept());
            Ap01SetSelectorV3 next(j,11);CHECK(next.select(&check,Preflight::check).mode==M::Stable);continue;}
        if(scenario==3){CHECK(boot.accept());CHECK(j.current()->phase==P::FailedRolledBack);continue;}
        if(scenario==1||scenario==6){CHECK(boot.failed(99));CHECK(j.current()->phase==P::RollbackPending);
            CHECK(!boot.failed(99));Ap01SetSelectorV3 same(j,10);CHECK(same.select(&check,Preflight::check).mode==M::Maintenance);}
        CHECK(j.load()==R::Ok);Ap01SetSelectorV3 next(j,11);chosen=next.select(&check,Preflight::check);
        if(scenario==4){CHECK(chosen.mode==M::Maintenance);CHECK(j.current()->phase==P::RecoveryRequired);continue;}
        CHECK(chosen.mode==M::Rollback&&chosen.digest[0]==6&&chosen.version==1);
        CHECK(j.current()->rollbackStarts==1&&j.current()->rollbackBoot==11);
        if(scenario==6){CHECK(!next.failed(88));CHECK(j.current()->phase==P::RecoveryRequired);}
        else if(scenario==1){CHECK(next.accept());CHECK(j.current()->phase==P::FailedRolledBack);}
        else {Ap01SetSelectorV3 third(j,12);CHECK(third.select(&check,Preflight::check).mode==M::Maintenance);
            CHECK(j.current()->phase==P::RecoveryRequired);}
    }
    Disk d;Ap01SetJournalV3 j(d.ops(),mac);CHECK(j.load()==R::Empty);Preflight check;
    Ap01SetSelectorV3 empty(j,1);CHECK(empty.select(&check,Preflight::check).mode==M::Maintenance);CHECK(!check.calls);
}
static void observation(){
    using D=Ap01SetHealthDecisionV3;
    for(unsigned scenario=0;scenario<7;++scenario){Disk disk;auto r=initial();r.phase=P::SwitchPending;r.readyMask=3;
        install(disk,0,r);Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
        Ap01SetSelectorV3 select(journal,1);Preflight check;CHECK(select.select(&check,Preflight::check).mode==Ap01SetBootModeV3::Trial);
        uint32_t base=scenario==1?UINT32_MAX-1000:0;select.beginObservation(base);select.beginObservation(base+50000);
        D last=D::Waiting;
        for(uint32_t t=0;t<=41000&&last==D::Waiting;t+=1000){
            bool healthy=scenario!=2;
            if(scenario==3&&t>=15000&&t<=16000)healthy=false;
            if(scenario==4&&t==30000)disk.lost=true;
            if(scenario==5&&t>1000&&t<15000)continue;
            last=select.observe(base+t,healthy,scenario==6&&t==2000);
            if(last==D::Approved)CHECK(t==30000);
        }
        CHECK(last==(scenario<=1?D::Approved:scenario==4?D::Maintenance:D::Reboot));
        if(scenario<=1)CHECK(journal.current()->phase==P::Succeeded);
        if(scenario==4)CHECK(!journal.current());
        CHECK(select.observe(base+90000,true,false)==last);
    }
}
static void rebootScheduling(){
    using S=Ap01RebootStateV3;
    for(uint32_t base: {0u,UINT32_MAX-100u}){Ap01AppRebootV3 reboot;unsigned calls=0;
        auto callback=[](void *p){++*(unsigned*)p;};
        CHECK(reboot.state(base)==S::Idle);reboot.request(base);reboot.request(base+1000);
        CHECK(reboot.state(base-1)==S::Pending);
        reboot.tick(base-1,&calls,callback);CHECK(!calls);
        reboot.tick(base+249,&calls,callback);CHECK(!calls);
        reboot.tick(base+250,&calls,callback);CHECK(calls==1&&reboot.state(base+250)==S::Invoked);
        reboot.tick(base+1000,&calls,callback);CHECK(calls==1);
        CHECK(reboot.state(base+5001)==S::Failed);reboot.request(base+6000);CHECK(reboot.state(base+6000)==S::Failed);
        CHECK(reboot.state(base)==S::Failed);
    }
    Ap01AppRebootV3 noCallback;noCallback.request(0);noCallback.tick(250,nullptr,nullptr);
    CHECK(noCallback.state(250)==S::Failed);
    Ap01AppRebootV3 stalled;stalled.request(0);CHECK(stalled.state(5001)==S::Failed);
}
static void downloads(){
    using D=Ap01SetDownloadResultV3;
    for(int cut=0;cut<832;++cut){Disk disk;auto r=initial();r.changedBytes=1024;
        install(disk,0,r);Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
        Ap01ManifestV3 manifest{};manifest.sequence=1;manifest.count=2;memcpy(manifest.digest,r.newDigest,32);
        manifest.entries[0].package_bytes=manifest.entries[1].package_bytes=512;
        Ap01SetDownloadV3 download(disk.ops(),journal,manifest);uint8_t bytes[512];memset(bytes,0x57,sizeof(bytes));
        disk.cut=cut<512?cut:512;disk.journalCut=cut<512?-1:cut-512;CHECK(download.chunk(r.transaction,0,0,bytes,512)==D::Unknown);
        CHECK(download.chunk(r.transaction,1,0,bytes,512)==D::Unknown);
        disk.cut=1024;disk.journalCut=-1;CHECK(journal.load()==R::Ok);CHECK(journal.current()->received[0]==0);
        Ap01SetDownloadV3 resumed(disk.ops(),journal,manifest);
        CHECK(resumed.chunk(r.transaction,0,0,bytes,512)==D::Ok);
        CHECK(journal.current()->received[0]==512&&journal.current()->received[1]==0);
        CHECK(resumed.chunk(r.transaction,0,0,bytes,512)==D::Ok);
        bytes[0]^=1;CHECK(resumed.chunk(r.transaction,0,0,bytes,512)==D::Conflict);
        CHECK(resumed.chunk(r.transaction,1,0,bytes,512)==D::Ok);
        CHECK(journal.current()->received[1]==512);CHECK(journal.load()==R::Ok);
        CHECK(journal.current()->received[0]==512&&journal.current()->received[1]==512);
        CHECK(resumed.chunk(r.transaction,1,512,bytes,1)==D::Bounds);
        auto wrong=r;wrong.transaction[0]++;CHECK(resumed.chunk(wrong.transaction,1,0,bytes,1)==D::Conflict);
    }
}
static void publication(const char *package){
    using D=Ap01SetDownloadResultV3;
    std::ifstream input(package,std::ios::binary);CHECK(bool(input));
    std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(input)),{});
    Apx2Reader reader{&bytes,uint32_t(bytes.size()),[](void *p,uint32_t at,uint8_t *out,uint32_t n){auto &b=*(std::vector<uint8_t>*)p;
        if(at>b.size()||n>b.size()-at)return false;memcpy(out,b.data()+at,n);return true;}};
    Apx2View view{};Apx2Limits limits{1u<<24,1u<<25,1u<<24,1u<<24,1,127,nullptr,3};CHECK(apx2Validate(reader,limits,view)==Apx2Error::Ok);
    Ap01ManifestV3 manifest{};manifest.sequence=1;manifest.count=1;manifest.digest[0]=7;
    auto &e=manifest.entries[0];strcpy(e.id,view.app_id);strcpy(e.version,view.version);memcpy(e.digest,view.digest,32);
    e.package_bytes=bytes.size();e.image_bytes=view.image_bytes+view.bss_bytes;e.heap_bytes=view.heap_bytes;e.stack_bytes=view.stack_bytes;
    e.capabilities=view.required_services;e.data_min=view.data_read_min;e.data_max=view.data_read_max;e.data_write=view.data_write_version;
    const char *hex="0123456789abcdef";std::string final="/resource/app-store/packages/";
    for(auto b:e.digest){final+=hex[b>>4];final+=hex[b&15];}final+=".apx2";
    for(unsigned scenario=0;scenario<8;++scenario){
        using C=Ap01SetCommitResultV3;
        Disk disk;auto r=initial();r.changedMask=r.readyMask=1;r.changedBytes=bytes.size();r.received[0]=bytes.size();
        if(scenario==6)r.readyMask=0;
        install(disk,0,r);Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
        Ap01AppWriteGateV3 gate;CHECK(gate.writes(true));Ap01AppRebootV3 reboot;Ap01SetCommitV3 commit(journal,gate,reboot);
        struct Packages {Apx2Reader reader;bool fail;unsigned opens=0,closes=0;} state{reader,scenario==5};
        Ap01ManifestPackagesV3 packages{&state,[](void *p,const Ap01ManifestEntryV3 &,Apx2Reader &out,uint32_t &version){
            auto &s=*(Packages*)p;if(s.fail)return false;++s.opens;out=s.reader;version=1;return true;
        },[](void *p,Apx2Reader &out){++((Packages*)p)->closes;out={};}};
        if(scenario==1||scenario==2)CHECK(gate.enter());
        if(scenario==3)disk.journalCut=20;
        if(scenario==4)disk.lostWriteAt=2;
        uint8_t expected[32]{};if(scenario==7)expected[0]=1;
        auto call=[&](uint32_t now){return commit.commit(r.transaction,expected,0,manifest,packages,now);};
        auto result=call(0);CHECK(state.opens==state.closes);
        if(scenario>=5){CHECK(result==(scenario==5?C::Package:scenario==6?C::NotReady:C::Conflict));
            CHECK(gate.writable()&&reboot.state(0)==Ap01RebootStateV3::Idle);continue;}
        CHECK(!gate.writable()&&gate.held()&&!gate.writes(true));
        if(scenario==1||scenario==2){CHECK(result==C::Busy&&journal.current()->phase==P::Receiving);
            CHECK(reboot.state(0)==Ap01RebootStateV3::Idle);gate.leave();
            result=call(scenario==2?5000:100);
            if(scenario==2){CHECK(result==C::DrainTimeout&&reboot.state(5000)==Ap01RebootStateV3::Idle);continue;}}
        if(scenario==3||scenario==4){CHECK(result==C::Unknown);CHECK(reboot.state(0)==Ap01RebootStateV3::Idle);
            disk.journalCut=-1;disk.lostWriteAt=0;CHECK(journal.load()==R::Ok);
            Ap01SetCommitV3 restored(journal,gate,reboot);
            CHECK(restored.commit(r.transaction,expected,0,manifest,packages,100)==C::Pending);
        }else CHECK(result==C::Pending);
        CHECK(journal.current()->phase==P::SwitchPending);auto sequence=journal.current()->sequence;
        CHECK(call(200)==C::Pending&&journal.current()->sequence==sequence);
        unsigned reboots=0;reboot.tick(500,&reboots,[](void *p){++*(unsigned*)p;});CHECK(reboots==1);
        CHECK(call(5500)==C::RebootFailed&&journal.current()->sequence==sequence);
    }
    for(unsigned fault=0;fault<6;++fault){Disk disk;disk.cut=1024;auto r=initial();r.changedMask=1;r.changedBytes=bytes.size();
        install(disk,0,r);Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
        Ap01SetDownloadV3 download(disk.ops(),journal,manifest);
        for(uint32_t at=0;at<bytes.size();at+=1024){uint32_t n=std::min(uint32_t(bytes.size())-at,1024u);
            CHECK(download.chunk(r.transaction,0,at,bytes.data()+at,n)==D::Ok);}
        if(fault==1)disk.renameLost=true;
        if(fault==2)disk.renameFails=true;
        if(fault==3)disk.journalCut=31;
        if(fault==4)for(auto &f:disk.files)if(f.first.find(".part")!=std::string::npos)f.second.back()^=1;
        if(fault==5){disk.files[final]=bytes;disk.files[final].back()^=1;}
        auto result=download.ready(r.transaction,0,1);
        CHECK(result==(fault==0?D::Ok:fault>=4?D::Package:D::Unknown));
        if(fault>=4){CHECK(!journal.current()->readyMask&&!disk.renames);continue;}
        disk.renameLost=disk.renameFails=false;disk.journalCut=-1;CHECK(journal.load()==R::Ok);
        Ap01SetDownloadV3 resumed(disk.ops(),journal,manifest);CHECK(resumed.ready(r.transaction,0,1)==D::Ok);
        CHECK(journal.current()->readyMask==1&&disk.files[final]==bytes);
        unsigned calls=disk.renames;CHECK(resumed.ready(r.transaction,0,1)==D::Ok&&calls==disk.renames);
        CHECK(resumed.chunk(r.transaction,0,0,bytes.data(),1)==D::State);
        CHECK(journal.load()==R::Ok&&journal.current()->readyMask==1);
    }
}
static void beginPlanning(){
    using B=Ap01SetBeginResultV3;
    Disk disk;Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Empty);
    Ap01ManifestV3 manifest{};manifest.sequence=1;manifest.digest[0]=7;manifest.count=2;
    strcpy(manifest.entries[0].id,"a");strcpy(manifest.entries[1].id,"z");
    for(unsigned i=0;i<2;++i){manifest.entries[i].package_bytes=256;manifest.entries[i].digest[0]=uint8_t(i+1);}
    uint8_t transaction[16]={1};Ap01SetRecordV3 plan{};
    constexpr uint64_t required=512+4*(64+8*160+56*40)+640;
    CHECK(ap01PlanSetBeginV3(journal,nullptr,manifest,transaction,mac,"owner",required+99,100,plan)==B::Space);
    CHECK(ap01PlanSetBeginV3(journal,nullptr,manifest,transaction,mac,"owner",required+100,100,plan)==B::New);
    CHECK(plan.changedMask==3&&plan.changedBytes==512);auto original=plan;
    CHECK(journal.save(plan)==R::Ok);plan.received[0]=128;CHECK(journal.save(plan)==R::Ok);
    auto sequence=journal.current()->sequence;
    CHECK(ap01PlanSetBeginV3(journal,nullptr,manifest,transaction,mac,"owner",0,100,plan)==B::Replay);
    CHECK(plan.received[0]==128&&plan.sequence==sequence&&journal.current()->sequence==sequence);
    CHECK(ap01PlanSetBeginV3(journal,nullptr,manifest,transaction,mac,"other",required,0,plan)==B::Conflict);
    transaction[0]=2;CHECK(ap01PlanSetBeginV3(journal,nullptr,manifest,transaction,mac,"owner",required,0,plan)==B::Busy);
    original.phase=P::Succeeded;original.trialStarts=1;original.trialBoot=1;original.readyMask=3;
    original.received[0]=original.received[1]=256;
    for(unsigned change=0;change<6;++change){Disk stored;auto current=original;if(change==4)current.cleanupPending=1;
        install(stored,0,current);Ap01SetJournalV3 j(stored.ops(),mac);CHECK(j.load()==R::Ok);
        auto candidate=manifest;candidate.sequence=2;candidate.digest[0]=8;
        if(change==0)candidate.entries[0].digest[0]=9; // Only A updated, Z unchanged.
        if(change==1){candidate.count=3;candidate.entries[2]=candidate.entries[1];candidate.entries[1]=candidate.entries[0];
            strcpy(candidate.entries[1].id,"b");candidate.entries[1].digest[0]=9;} // Insertion shifts Z's index.
        if(change==2)candidate.count=1; // Removal only; no download.
        if(change==3){candidate.entries[0].digest[0]=9;candidate.entries[1].digest[0]=10;}
        auto old=manifest;if(change==5)old.digest[0]=99;
        auto result=ap01PlanSetBeginV3(j,&old,candidate,transaction,mac,"owner",UINT64_MAX,100,plan);
        CHECK(result==(change==4?B::Busy:change==5?B::Conflict:B::New));
        if(change<4)CHECK(plan.changedMask==(change==0?1:change==1?2:change==2?0:3));
    }
}
static void manifestPublication(const char *path){
    using M=Ap01ManifestPublishResultV3;
    std::ifstream input(path,std::ios::binary);CHECK(bool(input));std::vector<uint8_t> bytes((std::istreambuf_iterator<char>(input)),{});
    Apx2Reader reader{&bytes,uint32_t(bytes.size()),[](void *p,uint32_t at,uint8_t *out,uint32_t n){auto &b=*(std::vector<uint8_t>*)p;
        if(at>b.size()||n>b.size()-at)return false;memcpy(out,b.data()+at,n);return true;}};
    Ap01ManifestLimitsV3 limits{8,1u<<24,1u<<24,1u<<24,1u<<24,32,256,127,1u<<28,0};
    Ap01ManifestV3 parsed{};CHECK(ap01ReadManifestV3(reader,limits,parsed)==Ap01ManifestErrorV3::Ok);
    std::string stem="/resource/app-store/manifests/";const char *hex="0123456789abcdef";
    for(auto b:parsed.digest){stem+=hex[b>>4];stem+=hex[b&15];}
    for(size_t prefix=0;prefix<=bytes.size();++prefix){Disk disk;disk.files[stem+".part"]={bytes.begin(),bytes.begin()+prefix};
        CHECK(ap01PublishManifestV3(disk.ops(),reader,limits,parsed)==M::Ok);
        CHECK(disk.files[stem+".amf3"]==bytes&&disk.renames==1);
        CHECK(ap01PublishManifestV3(disk.ops(),reader,limits,parsed)==M::Ok&&disk.renames==1);
    }
    for(unsigned fault=0;fault<5;++fault){Disk disk;
        if(fault==0)disk.cut=17;
        if(fault==1)disk.renameLost=true;
        if(fault==2)disk.renameFails=true;
        if(fault==3){disk.files[stem+".part"]=bytes;disk.files[stem+".part"][0]^=1;}
        if(fault==4){disk.files[stem+".amf3"]=bytes;disk.files[stem+".amf3"][0]^=1;}
        CHECK(ap01PublishManifestV3(disk.ops(),reader,limits,parsed)==(fault>=3?M::Conflict:M::Unknown));
        if(fault>=3){CHECK(!disk.writes&&!disk.renames);continue;}
        disk.cut=320;disk.renameLost=disk.renameFails=false;
        CHECK(ap01PublishManifestV3(disk.ops(),reader,limits,parsed)==M::Ok);
        CHECK(disk.files[stem+".amf3"]==bytes);
    }
    for(unsigned fault=0;fault<6;++fault){Disk disk;Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Empty);
        uint8_t transaction[16]={9};Ap01SetRecordV3 plan{};
        if(fault==1)disk.freeBytes=1;
        if(fault==2)disk.renameLost=true;
        if(fault==3)disk.journalCut=31;
        if(fault==4)disk.mkdirFails=true;
        auto result=ap01BeginSetV3(journal,disk.ops(),nullptr,reader,limits,transaction,mac,"owner",4096,parsed,plan);
        using B=Ap01SetBeginResultV3;
        CHECK(result==(fault==1?B::Space:fault>=2&&fault<=4?B::Unknown:B::New));
        if(fault==1){CHECK(!disk.writes&&!disk.renames);continue;}
        if(fault==3){CHECK(journal.load()==R::Corrupt);CHECK(disk.files[stem+".amf3"]==bytes);continue;}
        if(fault==2||fault==4){CHECK(!journal.current());CHECK(journal.load()==R::Empty);
            disk.renameLost=disk.mkdirFails=false;
            CHECK(ap01BeginSetV3(journal,disk.ops(),nullptr,reader,limits,transaction,mac,"owner",4096,parsed,plan)==B::New);}
        CHECK(journal.current()->phase==P::Receiving&&disk.files[stem+".amf3"]==bytes);
        unsigned writes=disk.writes;disk.freeBytes=0;
        CHECK(ap01BeginSetV3(journal,disk.ops(),nullptr,reader,limits,transaction,mac,"owner",4096,parsed,plan)==B::Replay);
        CHECK(disk.writes==writes);
    }
    auto corrupted=bytes;corrupted.back()^=1;reader.context=&corrupted;Disk disk;
    CHECK(ap01PublishManifestV3(disk.ops(),reader,limits,parsed)==M::Invalid&&!disk.opens&&!disk.writes);
}
static void cancellation(){
    using C=Ap01SetCommitResultV3;using S=Ap01RebootStateV3;
    for(unsigned scenario=0;scenario<8;++scenario){Disk disk;auto r=initial();
        r.phase=scenario==0?P::Receiving:scenario==1?P::Ready:scenario==3?P::TrialStarted:scenario==4?P::Succeeded:P::SwitchPending;
        if(scenario)r.readyMask=3;
        if(scenario==3||scenario==4){r.trialStarts=1;r.trialBoot=11;}
        install(disk,0,r);Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
        Ap01AppWriteGateV3 gate;CHECK(gate.writes(true));Ap01AppRebootV3 reboot;
        Ap01SetCommitV3 action(journal,gate,reboot);
        if(r.phase==P::SwitchPending)reboot.request(0);
        unsigned calls=0;if(scenario==5)reboot.tick(250,&calls,[](void *p){++*(unsigned*)p;});
        if(scenario==6)disk.lost=true;if(scenario==7)disk.cut=17;
        if(scenario==3){CHECK(gate.enter());CHECK(action.cancel(r.transaction,0)==C::Busy);gate.leave();}
        auto result=action.cancel(r.transaction,100);
        CHECK(result==(scenario==3?C::Pending:scenario==4?C::State:scenario==5?C::RebootInFlight:scenario>=6?C::Unknown:C::Cancelled));
        if(scenario==5){CHECK(calls==1&&journal.current()->phase==P::SwitchPending);continue;}
        if(scenario==4){CHECK(journal.current()->phase==P::Succeeded);continue;}
        if(scenario==3){CHECK(journal.current()->phase==P::RollbackPending&&gate.drained());
            auto seq=journal.current()->sequence;CHECK(action.cancel(r.transaction,200)==C::Pending&&journal.current()->sequence==seq);
            reboot.tick(400,&calls,[](void *p){++*(unsigned*)p;});CHECK(calls==1);
            CHECK(action.cancel(r.transaction,6000)==C::RebootFailed);continue;}
        CHECK(reboot.state(100)==S::Idle);reboot.tick(1000,&calls,[](void *p){++*(unsigned*)p;});CHECK(!calls);
        if(scenario>=6){disk.lost=false;disk.cut=320;CHECK(journal.load()==R::Ok);
            CHECK(journal.current()->phase==(scenario==6?P::Cancelled:P::SwitchPending));}
        else {CHECK(journal.current()->phase==P::Cancelled&&journal.current()->cleanupPending);
            auto seq=journal.current()->sequence;CHECK(action.cancel(r.transaction,200)==C::Cancelled&&journal.current()->sequence==seq);}
    }
}
static void cleanup(){
    using C=Ap01SetCleanupResultV3;
    Ap01ManifestV3 old{},candidate{};old.sequence=1;old.digest[0]=1;old.count=2;
    candidate=old;candidate.sequence=2;candidate.digest[0]=2;
    old.entries[0].digest[0]=3;candidate.entries[0].digest[0]=4;
    old.entries[1].digest[0]=candidate.entries[1].digest[0]=5;
    auto packagePath=[](unsigned byte){std::string path="/resource/app-store/packages/";const char *hex="0123456789abcdef";
        path+=hex[byte>>4];path+=hex[byte&15];path+=std::string(62,'0');return path+".apx2";};
    for(unsigned phase=0;phase<3;++phase)for(unsigned fault=0;fault<5;++fault){Disk disk;auto record=initial();
        record.sequence=2;record.oldVersion=1;record.oldDigest[0]=1;record.newVersion=2;record.newDigest[0]=2;
        record.readyMask=3;record.phase=phase==0?P::Succeeded:phase==1?P::FailedRolledBack:P::Cancelled;
        record.cleanupPending=1;
        if(phase<2){record.trialStarts=1;record.trialBoot=1;}
        if(phase==1){record.rollbackStarts=1;record.rollbackBoot=2;record.error=1;}
        auto prior=record;prior.sequence=1;prior.cleanupPending=0;
        prior.phase=phase==0?P::TrialStarted:phase==1?P::RollbackStarted:P::SwitchPending;
        install(disk,0,record);install(disk,1,prior);
        for(unsigned digest=3;digest<=5;++digest)disk.files[packagePath(digest)]={uint8_t(digest)};
        std::string incoming="/resource/app-store/incoming/01"+std::string(30,'0')+"-0.part";
        disk.files[incoming]={1};
        disk.checkCleanupBarrier=true;
        Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
        if(fault==1)disk.cut=10;if(fault==2)disk.removeFails=true;if(fault==3)disk.removeLost=true;if(fault==4)disk.lostWriteAt=2;
        CHECK(ap01CleanupSetV3(journal,disk.ops(),&old,candidate)==(fault?C::Unknown:C::Ok));
        if(fault==1)CHECK(!disk.removes);
        CHECK(disk.files.count(packagePath(5))&&disk.files.count(packagePath(phase==0?4:3)));
        disk.cut=320;disk.removeFails=disk.removeLost=false;disk.lostWriteAt=0;
        CHECK(journal.load()==R::Ok);CHECK(ap01CleanupSetV3(journal,disk.ops(),&old,candidate)==C::Ok);
        CHECK(!journal.current()->cleanupPending&&!disk.files.count(packagePath(phase==0?3:4))&&!disk.files.count(incoming));
        unsigned removes=disk.removes;CHECK(ap01CleanupSetV3(journal,disk.ops(),&old,candidate)==C::Ok&&disk.removes==removes);
    }
}
static std::vector<uint8_t> loadBytes(const char *path){std::ifstream f(path,std::ios::binary);CHECK(bool(f));return {(std::istreambuf_iterator<char>(f)),{}};}
static Apx2Reader bytesReader(std::vector<uint8_t> &bytes){return {&bytes,uint32_t(bytes.size()),[](void *p,uint32_t at,uint8_t *out,uint32_t n){
    auto &b=*(std::vector<uint8_t>*)p;if(at>b.size()||n>b.size()-at)return false;memcpy(out,b.data()+at,n);return true;}};}
static std::string digestPath(const char *prefix,const uint8_t *digest,const char *suffix){std::string path=prefix;const char *hex="0123456789abcdef";
    for(unsigned i=0;i<32;++i){path+=hex[digest[i]>>4];path+=hex[digest[i]&15];}return path+suffix;}
static void fullTransactions(const char *appPath,const char *manifestPath,const char *peerPath){
    using B=Ap01SetBeginResultV3;using D=Ap01SetDownloadResultV3;using C=Ap01SetCommitResultV3;using M=Ap01SetBootModeV3;
    auto original=loadBytes(manifestPath);std::vector<uint8_t> originals[2]={loadBytes(appPath),loadBytes(peerPath)};
    Ap01ManifestLimitsV3 limits{8,1u<<24,1u<<24,1u<<24,1u<<24,32,256,127,1u<<28,0};
    // Fresh install, then single or batch update, with success or whole-set rollback.
    for(unsigned scenario=0;scenario<4;++scenario){Disk disk;disk.cut=1024;
        Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Empty);
        auto currentBytes=original;Ap01ManifestV3 current{};
        struct Store {Disk &disk;Ap01ManifestLimitsV3 limits;
            static bool open(void *p,const Ap01ManifestEntryV3 &e,Apx2Reader &out,uint32_t &version){auto &s=*(Store*)p;
                auto it=s.disk.files.find(digestPath("/resource/app-store/packages/",e.digest,".apx2"));if(it==s.disk.files.end())return false;
                out=bytesReader(it->second);version=1;return true;}
            static void close(void *,Apx2Reader &r){r={};}
            static bool check(void *p,const uint8_t *digest,uint64_t version){auto &s=*(Store*)p;
                auto it=s.disk.files.find(digestPath("/resource/app-store/manifests/",digest,".amf3"));if(it==s.disk.files.end())return false;
                Ap01ManifestV3 parsed{};return ap01ReadManifestV3(bytesReader(it->second),s.limits,parsed)==Ap01ManifestErrorV3::Ok&&
                    parsed.sequence==version&&!memcmp(parsed.digest,digest,32)&&
                    ap01CheckManifestPackagesV3(parsed,{p,open,close})==Ap01ManifestErrorV3::Ok;}
        } store{disk,limits};Ap01ManifestPackagesV3 packages{&store,Store::open,Store::close};
        for(unsigned generation=0;generation<2;++generation){
            auto nextBytes=original;std::vector<uint8_t> payloads[2]={originals[0],originals[1]};
            if(generation){
                for(unsigned i=0;i<2;++i)if(i==0||(scenario&1)){
                    auto &b=payloads[i];memset(b.data()+160,0,32);memcpy(b.data()+160,"d3-test",7);
                    memset(b.data()+192,0,32);uint8_t digest[32];syncSha256(b.data(),b.size(),digest);memcpy(b.data()+192,digest,32);
                    memcpy(nextBytes.data()+64+i*160+32,b.data()+160,32);memcpy(nextBytes.data()+64+i*160+64,digest,32);
                }
                uint64_t version=current.sequence+1;for(unsigned i=0;i<8;++i)nextBytes[16+i]=uint8_t(version>>(8*i));
                unsigned deps=nextBytes[24]|unsigned(nextBytes[25])<<8;
                for(unsigned i=0;i<deps;++i){unsigned at=64+2*160+i*40,target=nextBytes[at+2]|unsigned(nextBytes[at+3])<<8;
                    memcpy(nextBytes.data()+at+8,nextBytes.data()+64+target*160+64,32);}
                memset(nextBytes.data()+32,0,32);uint8_t digest[32];syncSha256(nextBytes.data(),nextBytes.size(),digest);memcpy(nextBytes.data()+32,digest,32);
            }
            auto nextReader=bytesReader(nextBytes),oldReader=bytesReader(currentBytes);uint8_t txn[16]={uint8_t(generation+1)};
            Ap01ManifestV3 next{};Ap01SetRecordV3 plan{};
            CHECK(ap01BeginSetV3(journal,disk.ops(),generation?&oldReader:nullptr,nextReader,limits,txn,mac,"owner",4096,next,plan)==B::New);
            CHECK(plan.changedMask==(generation&&!(scenario&1)?1:3));
            if(generation&&!(scenario&1))CHECK(!memcmp(next.entries[1].digest,current.entries[1].digest,32)&&!plan.received[1]);
            Ap01SetDownloadV3 download(disk.ops(),journal,next);Ap01AppWriteGateV3 gate;CHECK(gate.writes(true));
            Ap01AppRebootV3 reboot;Ap01SetCommitV3 commit(journal,gate,reboot);
            uint8_t expected[32]{};if(generation)memcpy(expected,current.digest,32);
            for(unsigned i=0;i<2;++i)if(plan.changedMask&(1u<<i)){
                auto &b=payloads[i];for(uint32_t at=0;at<b.size();at+=1024){uint32_t n=std::min(uint32_t(b.size())-at,1024u);
                    CHECK(download.chunk(txn,i,at,b.data()+at,n)==D::Ok);}
                CHECK(download.ready(txn,i,1)==D::Ok);
                if(i==0&&(plan.changedMask&2))CHECK(commit.commit(txn,expected,generation?current.sequence:0,next,packages,0)==C::NotReady);
            }
            CHECK(commit.commit(txn,expected,generation?current.sequence:0,next,packages,0)==C::Pending);
            auto seq=journal.current()->sequence;CHECK(commit.commit(txn,expected,generation?current.sequence:0,next,packages,100)==C::Pending&&journal.current()->sequence==seq);
            unsigned reboots=0;reboot.tick(250,&reboots,[](void *p){++*(unsigned*)p;});CHECK(reboots==1&&gate.drained());
            CHECK(journal.load()==R::Ok);Ap01SetSelectorV3 trial(journal,10+generation*10);
            CHECK(trial.select(&store,Store::check).mode==M::Trial);
            if(generation&&scenario>=2){
                // Crash before confirmation: new boot must select the entire old set.
                CHECK(journal.load()==R::Ok);Ap01SetSelectorV3 rollback(journal,21);
                auto selected=rollback.select(&store,Store::check);CHECK(selected.mode==M::Rollback&&!memcmp(selected.digest,current.digest,32));
                rollback.beginObservation(0);for(unsigned t=0;t<=30000;t+=1000)
                    CHECK(rollback.observe(t,true,false)==(t==30000?Ap01SetHealthDecisionV3::Approved:Ap01SetHealthDecisionV3::Waiting));
                CHECK(journal.current()->phase==P::FailedRolledBack);
            }else {trial.beginObservation(0);for(unsigned t=0;t<=30000;t+=1000)
                    CHECK(trial.observe(t,true,false)==(t==30000?Ap01SetHealthDecisionV3::Approved:Ap01SetHealthDecisionV3::Waiting));
                CHECK(journal.current()->phase==P::Succeeded);}
            Ap01SetServiceV3 cleaner(disk.ops(),journal,gate,reboot,limits,mac,30,4096);
            disk.checkCleanupBarrier=true;cleaner.tick(30000);
            CHECK(!journal.current()->cleanupPending&&!gate.held()&&!gate.writable());
            auto cleanupSequence=journal.current()->sequence;unsigned cleanupWrites=disk.writes;
            cleaner.tick(31000);CHECK(journal.current()->sequence==cleanupSequence&&disk.writes==cleanupWrites);
            const auto &kept=generation&&scenario>=2?current:next;
            CHECK(Store::check(&store,kept.digest,kept.sequence));
            if(generation&&!(scenario&1))CHECK(disk.files[digestPath("/resource/app-store/packages/",kept.entries[1].digest,".apx2")]==originals[1]);
            if(generation){const auto &removed=scenario>=2?next:current;
                CHECK(!disk.files.count(digestPath("/resource/app-store/packages/",removed.entries[0].digest,".apx2")));}
            if(!generation){current=next;currentBytes=nextBytes;}
        }
    }
}
static void httpService(const char *appPath,const char *manifestPath,const char *peerPath){
    auto manifest=loadBytes(manifestPath);std::vector<uint8_t> payloads[2]={loadBytes(appPath),loadBytes(peerPath)};
    Ap01ManifestLimitsV3 limits{8,1u<<24,1u<<24,1u<<24,1u<<24,32,256,127,1u<<28,0};
    for(unsigned scenario=0;scenario<4;++scenario){
        Disk disk;disk.cut=1024;Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Empty);
        Ap01AppWriteGateV3 gate;CHECK(gate.writes(true));Ap01AppRebootV3 reboot;
        Ap01SetServiceV3 service(disk.ops(),journal,gate,reboot,limits,mac,11,4096);
        struct Route {Ap01SetServiceV3 &service;bool held=false;unsigned calls=0;} route{service};
        Ap01MaintenancePort0041 port{};port.context=&route;
        port.deviceCode=[](void *,char code[9]){memcpy(code,"01234567",9);return 0;};
        port.enterOperation=[](void *p){auto &r=*(Route *)p;if(r.held)return false;r.held=true;return true;};
        port.leaveOperation=[](void *p){auto &r=*(Route *)p;CHECK(r.held);r.held=false;};
        port.appUpdate=[](void *p,const Ap01HttpRequest &r,const char *principal,uint64_t now){
            auto &route=*(Route *)p;CHECK(route.held);++route.calls;return route.service.handle(r,principal,uint32_t(now));};
        LittleFSClass fs(disk.ops(),"/resource/maintenance-test");
        Ap01Maintenance0041 maintenance(fs,port,{},"010203040506",11);CHECK(maintenance.begin());
        Ap01HttpWorkspace0041 workspace;
        bool dropResponse=false;
        Ap01HttpRequest request{};request.token="01234567";request.deviceMac="010203040506";request.requestId="01000000000000000000000000000000";
        request.contentType="application/octet-stream";
        auto send=[&](const char *method,const char *path,uint32_t now=0,const char *owner="ap01-menu-maintenance"){
            request.method=method;request.path=path;
            if(scenario<2||strcmp(owner,"ap01-menu-maintenance"))return service.handle(request,owner,now);
            struct Wire {std::string input,output;size_t at=0;bool drop;} wire{{},{},0,dropResponse};
            wire.input=std::string(method)+" "+path+"?operation_id="+request.requestId+"&device_mac="+request.deviceMac;
            if(strstr(path,"/chunk"))wire.input+="&offset="+std::string(request.offset)+"&sha256="+request.chunkSha256;
            wire.input+=" HTTP/1.1\r\nAuthorization: Bearer "+std::string(request.token)+
                "\r\nContent-Type: application/octet-stream\r\nContent-Length: "+std::to_string(request.length)+"\r\n\r\n";
            if(request.length)wire.input.append((const char *)request.body,request.length);
            Ap01Stream stream{&wire,[](void *p,uint8_t *out,size_t n,uint64_t){auto &w=*(Wire *)p;
                n=std::min(n,std::min(size_t(17),w.input.size()-w.at));memcpy(out,w.input.data()+w.at,n);w.at+=n;return int(n);},
                [](void *p,const uint8_t *bytes,size_t n,uint64_t){auto &w=*(Wire *)p;if(w.drop)return -1;
                    n=std::min(n,size_t(19));w.output.append((const char *)bytes,n);return int(n);}};
            bool sent=ap01ServeMaintenanceHttp0041(maintenance,stream,now,now+5000,&workspace);
            maintenance.afterResponse(sent);CHECK(!route.held&&sent!=dropResponse);
            Ap01HttpReply reply;
            if(dropResponse){dropResponse=false;reply.status=503;return reply;}
            CHECK(sscanf(wire.output.c_str(),"HTTP/1.1 %d",&reply.status)==1);
            auto body=wire.output.find("\r\n\r\n");CHECK(body!=std::string::npos);reply.bytes=wire.output.substr(body+4).c_str();return reply;};
        std::vector<uint8_t> begin(64+manifest.size());memcpy(begin.data(),"ASB3",4);begin[4]=1;begin[6]=64;
        for(unsigned i=0;i<4;++i)begin[48+i]=uint8_t(manifest.size()>>(8*i));
        memcpy(begin.data()+64,manifest.data(),manifest.size());
        auto beginRequest=[&](uint32_t now){request.body=begin.data();request.length=begin.size();return send("POST","/api/app/v3/update/begin",now);};
        if(scenario>=2){
            request.token="bad";CHECK(beginRequest(0).status==401&&!journal.current()&&!route.calls);request.token="01234567";
            dropResponse=true;CHECK(beginRequest(0).status==503&&journal.current()->phase==P::Receiving);
        }
        CHECK(beginRequest(0).status==200);auto seq=journal.current()->sequence;
        CHECK(beginRequest(1).status==200&&journal.current()->sequence==seq);
        CHECK(send("POST","/api/app/v3/update/begin",2,"stranger").status==404);
        for(unsigned i=0;i<2;++i){
            std::string path="/api/app/v3/package/"+std::to_string(i)+"/chunk";
            auto &b=payloads[i];
            for(uint32_t at=0;at<b.size();at+=1024){
                uint32_t n=std::min(uint32_t(b.size())-at,1024u);request.body=b.data()+at;request.length=n;
                std::string offset=std::to_string(at);request.offset=offset.c_str();uint8_t digest[32];syncSha256(request.body,n,digest);
                auto hash=digestPath("",digest,"");request.chunkSha256=hash.c_str();
                if(!i&&!at){
                    disk.lost=true;CHECK(send("PUT",path.c_str()).status==503);disk.lost=false;
                    CHECK(send("PUT",path.c_str()).status==503);
                    request.length=0;CHECK(send("GET","/api/app/v3/update/result").status==202);request.length=n;
                }
                CHECK(send("PUT",path.c_str()).status==200);
            }
            request.length=0;path="/api/app/v3/package/"+std::to_string(i)+"/ready";
            CHECK(send("POST",path.c_str()).status==200);
        }
        request.length=0;
        if(!(scenario&1)){
            if(scenario>=2){
                dropResponse=true;CHECK(send("POST","/api/app/v3/update/commit",100).status==503);
                CHECK(journal.current()->phase==P::SwitchPending&&reboot.state(100)==Ap01RebootStateV3::Pending);
                seq=journal.current()->sequence;
                CHECK(send("POST","/api/app/v3/update/commit",101).status==202&&journal.current()->sequence==seq);
            }
            CHECK(send("POST","/api/app/v3/update/commit",102).status==202);
            seq=journal.current()->sequence;CHECK(beginRequest(200).status==200);
            request.length=0;CHECK(send("POST","/api/app/v3/update/commit",200).status==202&&journal.current()->sequence==seq);
            disk.files.erase(digestPath("/resource/app-store/manifests/",journal.current()->newDigest,".amf3"));
            Ap01SetServiceV3 recovered(disk.ops(),journal,gate,reboot,limits,mac,11,4096);
            request.method="POST";request.path="/api/app/v3/update/cancel";
            CHECK(recovered.handle(request,"ap01-menu-maintenance",210).status==200);
            recovered.tick(210);CHECK(journal.current()->cleanupPending&&gate.held());
            disk.files[digestPath("/resource/app-store/manifests/",journal.current()->newDigest,".amf3")]=manifest;
            disk.removeLost=true;recovered.tick(1210);CHECK(journal.current()->cleanupPending&&gate.held());
            disk.removeLost=false;unsigned writes=disk.writes;recovered.tick(2210);CHECK(disk.writes==writes);
            request.method="GET";request.path="/api/app/v3/update/result";
            CHECK(recovered.handle(request,"ap01-menu-maintenance",2210).status==200);
            recovered.tick(2210);CHECK(!journal.current()->cleanupPending&&!gate.held()&&!gate.writable());
            CHECK(reboot.state(400)==Ap01RebootStateV3::Idle);
            CHECK(send("GET","/api/app/v3/update/result",400).status==200);
        }else{
            CHECK(gate.enter());CHECK(send("POST","/api/app/v3/update/commit",100).status==409);
            CHECK(beginRequest(4000).status==200);
            begin.back()^=1;CHECK(beginRequest(4500).status==409);begin.back()^=1;
            gate.leave();request.length=0;
            auto reply=send("POST","/api/app/v3/update/commit",5100);
            CHECK(reply.status==409&&strstr(reply.bytes.c_str(),"write_drain_timeout"));
            CHECK(journal.current()->phase==P::Receiving&&reboot.state(6000)==Ap01RebootStateV3::Idle);
        }
        CHECK(!disk.handles);
    }
}
static void runtimeReporting(){
    Disk disk;auto record=initial();install(disk,0,record);Ap01SetJournalV3 journal(disk.ops(),mac);CHECK(journal.load()==R::Ok);
    Ap01AppWriteGateV3 gate;Ap01AppRebootV3 reboot;Ap01ManifestLimitsV3 limits{};limits.apps=8;
    Ap01SetServiceV3 service(disk.ops(),journal,gate,reboot,limits,mac,11,4096);
    Ap01RuntimeSnapshotV3 snapshot;service.runtime(&snapshot,[](void *p){return *(Ap01RuntimeSnapshotV3 *)p;});
    Ap01HttpRequest request{};request.method="GET";request.path="/api/app/v3/status";
    NativeJsonAllocator0041 allocator;JsonDocument doc(&allocator);
    auto read=[&](){auto reply=service.handle(request,"owner",100);CHECK(reply.status==200);
        CHECK(!deserializeJson(doc,reply.bytes.c_str()));CHECK(doc["runtime_reporting"].as<bool>());};
    read();CHECK(doc["limits"]["ram_bytes"].as<uint64_t>()==limits.ram_bytes&&doc["storage_reserve"].as<uint64_t>()==4096);CHECK(!strcmp(doc["runtime"]["boot_state"],"pending")&&doc["runtime"]["running"].size()==0);
    Ap01ManifestV3 running{};running.count=2;running.sequence=42;running.digest[0]=9;
    running.order[0]=1;running.order[1]=0;
    strcpy(running.entries[0].id,"unstarted");strcpy(running.entries[1].id,"actual");strcpy(running.entries[1].version,"running-v1");
    running.entries[1].digest[0]=10;snapshot.manifest=&running;snapshot.attempted=true;snapshot.started=1;snapshot.failed=0;
    read();CHECK(!strcmp(doc["runtime"]["boot_state"],"partial_failed")&&!doc["runtime"]["complete"].as<bool>());
    CHECK(doc["runtime"]["version"].as<unsigned>()==42&&doc["candidate_version"].as<unsigned>()==1);
    CHECK(doc["runtime"]["running"].size()==1&&!strcmp(doc["runtime"]["running"][0]["app_id"],"actual"));
    CHECK(doc["runtime"]["running"][0]["health"].isNull());
    snapshot.started=2;snapshot.complete=true;snapshot.failed=UINT32_MAX;snapshot.health.count=2;
    snapshot.health.state=Ap01SupervisorStateV3::Healthy;snapshot.health.sampled_at=99;
    read();CHECK(doc["runtime"]["running"].size()==2&&doc["runtime"]["complete"].as<bool>());
    CHECK(doc["runtime"]["running"][0]["health"].as<int>()==0&&doc["runtime"]["failed_index"].isNull());
    snapshot={};snapshot.attempted=true;read();CHECK(!strcmp(doc["runtime"]["boot_state"],"failed"));
}
static void httpParsing(){
    Ap01HttpRequest request{};request.method="GET";request.path="/api/app/v3/status";request.length=0;
    const char *device="010203040506";Ap01SetHttpCommandV3 command;
    CHECK(ap01ParseSetHttpV3(request,device,command)==200&&command.action==Ap01SetHttpActionV3::Status);
    request.path="/api/app/update/begin";CHECK(ap01ParseSetHttpV3(request,device,command)==404);
    request.path="/api/app/v3/update/begin";CHECK(ap01ParseSetHttpV3(request,device,command)==405);
    request.method="POST";request.deviceMac=device;request.requestId="01000000000000000000000000000000";
    uint8_t body[128]{};memcpy(body,"ASB3",4);body[4]=1;body[6]=64;body[48]=64;
    request.body=body;request.length=sizeof(body);request.contentType="application/octet-stream";
    CHECK(ap01ParseSetHttpV3(request,device,command)==200&&command.length==64&&command.bytes==body+64);
    for(unsigned i=52;i<64;++i){body[i]=1;CHECK(ap01ParseSetHttpV3(request,device,command)==400&&!command.bytes);body[i]=0;}
    body[8]=1;CHECK(ap01ParseSetHttpV3(request,device,command)==400);body[40]=1;
    CHECK(ap01ParseSetHttpV3(request,device,command)==200&&command.expectedVersion==1);
    request.length=3649;CHECK(ap01ParseSetHttpV3(request,device,command)==413);request.length=128;
    body[48]=63;CHECK(ap01ParseSetHttpV3(request,device,command)==400);body[48]=64;
    request.deviceMac="AABBCCDDEEFF";CHECK(ap01ParseSetHttpV3(request,device,command)==400);request.deviceMac=device;
    request.method="PUT";request.path="/api/app/v3/package/7/chunk";request.offset="0";
    uint8_t digest[32];syncSha256(body,sizeof(body),digest);char text[65];const char *hex="0123456789abcdef";
    for(unsigned i=0;i<32;++i){text[2*i]=hex[digest[i]>>4];text[2*i+1]=hex[digest[i]&15];}text[64]=0;request.chunkSha256=text;
    CHECK(ap01ParseSetHttpV3(request,device,command)==200&&command.index==7&&command.offset==0);
    for(const char *offset: {"-1","+1","01","4294967296","4294967295","1x",""}){request.offset=offset;CHECK(ap01ParseSetHttpV3(request,device,command)==400);}
    request.offset="4294967167";CHECK(ap01ParseSetHttpV3(request,device,command)==200);request.offset="0";
    body[100]^=1;CHECK(ap01ParseSetHttpV3(request,device,command)==400);body[100]^=1;
    request.path="/api/app/v3/package/8/chunk";CHECK(ap01ParseSetHttpV3(request,device,command)==404);
    request.path="/api/app/v3/package/07/chunk";CHECK(ap01ParseSetHttpV3(request,device,command)==404);
    request.path="/api/app/v3/package/7/ready";request.method="POST";request.length=0;
    CHECK(ap01ParseSetHttpV3(request,device,command)==200&&command.action==Ap01SetHttpActionV3::Ready);
    request.requestId="00000000000000000000000000000000";CHECK(ap01ParseSetHttpV3(request,device,command)==400);
}
// Pipe-driven protocol peer for the Python CLI. Executes production transaction
// and HTTP code, but injects health and models reboot; it does not execute Apps.
static uint32_t modelU32(const uint8_t *p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
static uint64_t modelU64(const uint8_t *p){return uint64_t(modelU32(p))|uint64_t(modelU32(p+4))<<32;}
static std::vector<uint8_t> modelHex(const std::string &s){
    CHECK(!(s.size()&1));std::vector<uint8_t> out(s.size()/2);
    auto nibble=[](char c){CHECK((c>='0'&&c<='9')||(c>='a'&&c<='f'));return c<='9'?c-'0':c-'a'+10;};
    for(size_t i=0;i<out.size();++i)out[i]=uint8_t(nibble(s[2*i])*16+nibble(s[2*i+1]));return out;
}
static int httpPeer(){
    struct Boot {
        Disk &disk;Ap01ManifestLimitsV3 limits{8,1u<<24,1u<<24,1u<<24,1u<<24,32,256,127,1u<<28,0};
        Ap01AppWriteGateV3 gate;Ap01AppRebootV3 reboot;Ap01SetJournalV3 journal;
        Ap01SetServiceV3 service;Ap01ManifestV3 running;Ap01RuntimeSnapshotV3 runtime;
        LittleFSClass fs;std::unique_ptr<Ap01Maintenance0041> maintenance;bool held=false;
        Boot(Disk &d,uint64_t id,uint32_t &now,bool fail,const std::vector<uint8_t> *observed=nullptr):disk(d),journal(d.ops(),mac),
            service(d.ops(),journal,gate,reboot,limits,mac,id,4096),fs(d.ops(),"/resource/maintenance-test"){
            auto result=journal.load();CHECK(result==R::Ok||result==R::Empty);
            if(observed){
                const auto &bytes=*observed;CHECK(bytes.size()==912&&!memcmp(bytes.data(),"ARV3\x01\0\0\0",8));
                const auto *raw=bytes.data();const auto *record=journal.current();CHECK(record);
                CHECK(record->phase==P::Succeeded||record->phase==P::FailedRolledBack);
                bool approved=record->phase==P::Succeeded;
                const auto *digest=approved?record->newDigest:record->oldDigest;
                uint64_t version=approved?record->newVersion:record->oldVersion;
                CHECK(modelU64(raw+8)==id&&id==(approved?record->trialBoot:record->rollbackBoot));
                CHECK(modelU64(raw+16)==version&&!memcmp(raw+48,digest,32));
                CHECK(modelU32(raw+32)==1&&modelU32(raw+36)==unsigned(Ap01SupervisorStateV3::Healthy)&&!modelU32(raw+40));
                if(version){Ap01AppSetFilesV3 files(disk.ops());auto path=digestPath("/resource/app-store/manifests/",digest,".amf3");
                    CHECK(files.stage(path.c_str(),digest,limits,1u<<24)==Ap01SetFilesResultV3::Ready);
                    CHECK(ap01ReadManifestV3(files.reader(),limits,running)==Ap01ManifestErrorV3::Ok);}
                CHECK(modelU32(raw+24)==running.count&&modelU32(raw+28)==running.count);
                runtime.manifest=&running;runtime.complete=true;runtime.attempted=true;runtime.started=modelU32(raw+28);
                runtime.health.state=Ap01SupervisorStateV3(modelU32(raw+36));runtime.health.count=modelU32(raw+24);
                runtime.health.sampled_at=modelU32(raw+44);now=runtime.health.sampled_at;
                for(unsigned i=0;i<running.count;++i){unsigned at=80+104*i;
                    CHECK(!memcmp(raw+at,running.entries[i].id,32)&&!memcmp(raw+at+32,running.entries[i].version,32));
                    CHECK(!memcmp(raw+at+64,running.entries[i].digest,32)&&modelU32(raw+at+100)==running.order[i]);
                    CHECK(modelU32(raw+at+96)==0);runtime.health.health[i]=int32_t(modelU32(raw+at+96));}
            }else{
            Ap01SetSelectorV3 selector(journal,id);
            auto selected=selector.select(this,[](void *p,const uint8_t *digest,uint64_t version){auto &b=*(Boot *)p;
                Ap01AppSetFilesV3 files(b.disk.ops());auto path=digestPath("/resource/app-store/manifests/",digest,".amf3");
                return files.stage(path.c_str(),digest,b.limits,1u<<24)==Ap01SetFilesResultV3::Ready&&files.version()==version&&
                    ap01ReadManifestV3(files.reader(),b.limits,b.running)==Ap01ManifestErrorV3::Ok;});
            if(selected.mode!=Ap01SetBootModeV3::Maintenance){
                runtime.manifest=&running;runtime.attempted=true;
                if(fail&&selected.mode==Ap01SetBootModeV3::Trial){CHECK(selector.failed(5));reboot.request(now);}
                else {
                    selector.beginObservation(now);
                    for(unsigned t=0;t<=30000;t+=1000)CHECK(selector.observe(now+t,true,false)==
                        (t==30000?Ap01SetHealthDecisionV3::Approved:Ap01SetHealthDecisionV3::Waiting));
                    now+=30000;runtime.complete=true;runtime.started=running.count;
                    runtime.health.state=Ap01SupervisorStateV3::Healthy;runtime.health.count=running.count;runtime.health.sampled_at=now;
                }
            }
            }
            service.runtime(&runtime,[](void *p){return *(Ap01RuntimeSnapshotV3 *)p;});service.tick(now);
            Ap01MaintenancePort0041 port{};port.context=this;
            port.deviceCode=[](void *,char code[9]){memcpy(code,"01234567",9);return 0;};
            port.enterOperation=[](void *p){auto &b=*(Boot *)p;if(b.held)return false;b.held=true;return true;};
            port.leaveOperation=[](void *p){auto &b=*(Boot *)p;CHECK(b.held);b.held=false;};
            port.appUpdate=[](void *p,const Ap01HttpRequest &request,const char *principal,uint64_t time){auto &b=*(Boot *)p;
                CHECK(b.held);return b.service.handle(request,principal,uint32_t(time));};
            maintenance.reset(new Ap01Maintenance0041(fs,port,{},"010203040506",id));CHECK(maintenance->begin());
        }
    };
    Disk disk;disk.cut=1024;uint64_t identity=11;uint32_t now=0;bool failNext=false;
    auto boot=std::unique_ptr<Boot>(new Boot(disk,identity,now,false));std::string line;
    while(std::getline(std::cin,line)){
        if(line=="FAIL_TRIAL"){failNext=true;std::cout<<"OK"<<std::endl;continue;}
        if(line.rfind("APPLY ",0)==0){
            auto split=line.find(' ',6);CHECK(split!=std::string::npos);
            auto saved=modelHex(line.substr(6,split-6)),observed=modelHex(line.substr(split+1));
            CHECK(saved.size()==648&&observed.size()==912&&modelU64(observed.data()+8)>identity);
            const auto *before=boot->journal.current();CHECK(before&&before->phase==P::SwitchPending);
            Disk candidate;candidate.cut=1024;
            for(unsigned i=0;i<2;++i){auto n=modelU32(saved.data()+4*i);CHECK(n==320);candidate.files[paths[i]]={saved.begin()+8+320*i,saved.begin()+8+320*i+n};}
            Ap01SetJournalV3 imported(candidate.ops(),mac);CHECK(imported.load()==R::Ok);const auto *after=imported.current();
            CHECK(after&&after->sequence>before->sequence&&(after->phase==P::Succeeded||after->phase==P::FailedRolledBack));
            CHECK(!memcmp(before->transaction,after->transaction,16)&&!memcmp(before->requestDigest,after->requestDigest,32));
            CHECK(!memcmp(before->newDigest,after->newDigest,32)&&!memcmp(before->oldDigest,after->oldDigest,32));
            CHECK(before->oldVersion==after->oldVersion&&before->newVersion==after->newVersion&&before->changedBytes==after->changedBytes);
            CHECK(before->changedMask==after->changedMask&&before->readyMask==after->readyMask&&!memcmp(before->received,after->received,sizeof(before->received)));
            CHECK(!strcmp(before->principal,after->principal)&&after->trialStarts==1&&after->cleanupPending);
            boot.reset();for(unsigned i=0;i<2;++i)disk.files[paths[i]]=candidate.files[paths[i]];
            identity=modelU64(observed.data()+8);failNext=false;
            boot.reset(new Boot(disk,identity,now,false,&observed));
            std::cout<<"OK"<<std::endl;continue;
        }
        // Export exact durable model bytes before advancing the reboot clock.
        // A fresh RV32 guest can consume these without fabricating a journal.
        if(line=="SNAPSHOT"){
            CHECK(!disk.handles);std::cout<<"{";bool first=true;const char *hex="0123456789abcdef";
            for(const auto &file:disk.files){
                if(file.second.empty())continue;
                CHECK(file.first.find_first_of("\\\"\n\r")==std::string::npos);
                if(!first)std::cout<<",";first=false;std::cout<<"\""<<file.first<<"\":\"";
                for(unsigned char c:file.second)std::cout<<hex[c>>4]<<hex[c&15];std::cout<<"\"";
            }
            std::cout<<"}"<<std::endl;continue;
        }
        now+=1000;bool restart=false;boot->reboot.tick(now,&restart,[](void *p){*(bool *)p=true;});
        if(restart){boot.reset();boot.reset(new Boot(disk,++identity,now,failNext));failNext=false;}
        struct Wire {std::string input,output;size_t at=0;} wire;
        CHECK(!(line.size()&1));for(size_t i=0;i<line.size();i+=2){unsigned n=0;CHECK(sscanf(line.substr(i,2).c_str(),"%2x",&n)==1);wire.input+=char(n);}
        Ap01Stream stream{&wire,[](void *p,uint8_t *out,size_t n,uint64_t){auto &w=*(Wire *)p;
            n=std::min(n,std::min(size_t(31),w.input.size()-w.at));memcpy(out,w.input.data()+w.at,n);w.at+=n;return int(n);},
            [](void *p,const uint8_t *bytes,size_t n,uint64_t){auto &w=*(Wire *)p;n=std::min(n,size_t(29));w.output.append((const char *)bytes,n);return int(n);}};
        bool sent=ap01ServeMaintenanceHttp0041(*boot->maintenance,stream,now,now+5000);
        boot->maintenance->afterResponse(sent);CHECK(sent&&!boot->held);boot->service.tick(now);
        const char *hex="0123456789abcdef";for(unsigned char c:wire.output)std::cout<<hex[c>>4]<<hex[c&15];std::cout<<std::endl;
    }
    return 0;
}
int main(int argc,char **argv){if(argc==2&&!strcmp(argv[1],"--http-peer"))return httpPeer();CHECK(argc==4);httpParsing();runtimeReporting();httpService(argv[1],argv[2],argv[3]);fullTransactions(argv[1],argv[2],argv[3]);cleanup();cancellation();publication(argv[1]);manifestPublication(argv[2]);beginPlanning();codec();torn();recovery();corrupt();selection();observation();rebootScheduling();downloads();printf("AUT3: %u checks; journal faults, publication, begin/commit/cancel/cleanup, single/batch success and whole-set rollback passed\n",checks);}
