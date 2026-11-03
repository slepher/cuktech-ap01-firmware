#include "app_update_record_0041.h"
#include <assert.h>
#include <vector>
#include <stdio.h>
struct Disk {
    std::vector<uint8_t> files[2];bool present[2]={};unsigned position[2]={};
    int cut=-1;bool lostAck=false;
    static unsigned index(const char *p){return p[strlen(p)-1]-'0';}
    static int open(void *p,const char *name,unsigned mode){auto &d=*(Disk *)p;unsigned i=index(name);assert(i<2);if(mode){d.present[i]=true;d.files[i].clear();}d.position[i]=0;return d.present[i]?int(i):-1;}
    static int close(void *,int){return 0;}
    static int read(void *p,int fd,void *out,size_t n){auto &d=*(Disk *)p;auto &v=d.files[fd];n=n<v.size()-d.position[fd]?n:v.size()-d.position[fd];memcpy(out,v.data()+d.position[fd],n);d.position[fd]+=n;return n;}
    static int write(void *p,int fd,const void *data,size_t n){auto &d=*(Disk *)p;if(d.cut>=0&&unsigned(d.cut)<n)n=d.cut;auto b=(const uint8_t *)data;d.files[fd].assign(b,b+n);return d.lostAck?-1:int(n);}
    static int32_t size(void *p,int fd){return ((Disk *)p)->files[fd].size();}
    static int exists(void *p,const char *name){return ((Disk *)p)->present[index(name)];}
    Ap01VfsOps ops(){Ap01VfsOps o{};o.context=this;o.open=open;o.close=close;o.read=read;o.write=write;o.size=size;o.exists=exists;return o;}
};
int main(){
    using R=Ap01AppJournalResult;using P=Ap01AppUpdatePhase;
    uint8_t mac[6]={1,2,3,4,5,6};Ap01AppUpdateRecord seed;
    memcpy(seed.mac,mac,6);seed.transaction[0]=1;seed.newDigest[0]=2;seed.total=512;strcpy(seed.principal,"menu-maintenance");
    seed.sequence=1;uint8_t bytes[256];assert(ap01EncodeAppUpdate(seed,bytes));
    Ap01AppUpdateRecord decoded;assert(ap01DecodeAppUpdate(bytes,decoded));
    for(unsigned i=0;i<256;++i){bytes[i]^=1;assert(!ap01DecodeAppUpdate(bytes,decoded));bytes[i]^=1;}
    auto bad=seed;bad.phase=P::TrialStarted;assert(!ap01EncodeAppUpdate(bad,bytes));
    bad.received=512;bad.trialStarts=1;bad.generation=9;assert(ap01EncodeAppUpdate(bad,bytes));
    bad.trialStarts=2;assert(!ap01EncodeAppUpdate(bad,bytes));
    bad=seed;bad.phase=P::RollbackStarted;bad.received=512;bad.rollbackStarts=1;bad.generation=10;
    assert(!ap01EncodeAppUpdate(bad,bytes));bad.oldDigest[0]=3;assert(ap01EncodeAppUpdate(bad,bytes));
    // Every torn write prefix keeps the last committed state. No new write is
    // accepted after an ambiguous error until the journal is explicitly loaded.
    for(int cut=0;cut<256;++cut){
        Disk disk;auto ops=disk.ops();LittleFSClass fs(ops,"/test");Ap01AppUpdateJournal0041 j(fs,mac);
        assert(j.load()==R::Empty&&j.save(seed)==R::Ok);auto next=*j.current();next.received=128;
        disk.cut=cut;assert(j.save(next)==R::Unknown&&j.save(next)==R::Unknown);
        assert(j.current()->received==0);disk.cut=-1;
        Ap01AppUpdateJournal0041 boot(fs,mac);assert(boot.load()==R::Ok&&boot.current()->received==0);
        assert(boot.save(next)==R::Ok&&boot.current()->sequence==2);
    }
    Disk disk;auto ops=disk.ops();LittleFSClass fs(ops,"/test");Ap01AppUpdateJournal0041 j(fs,mac);
    assert(j.load()==R::Empty&&j.save(seed)==R::Ok);auto next=*j.current();next.received=512;next.phase=P::Ready;
    disk.lostAck=true;assert(j.save(next)==R::Unknown);disk.lostAck=false;
    assert(j.load()==R::Ok&&j.current()->phase==P::Ready&&j.current()->sequence==2);
    next=*j.current();next.phase=P::SwitchPending;assert(j.save(next)==R::Ok);
    next=*j.current();next.phase=P::TrialStarted;next.generation=17;next.trialStarts=1;
    assert(j.save(next)==R::Ok);Ap01AppUpdateJournal0041 boot(fs,mac);
    assert(boot.load()==R::Ok&&boot.current()->trialStarts==1);
    auto reset=seed;assert(boot.save(reset)==R::Invalid);
    reset.transaction[0]=4;assert(boot.save(reset)==R::Invalid);
    uint8_t foreign[6]={9};Ap01AppUpdateJournal0041 wrong(fs,foreign);assert(wrong.load()==R::Corrupt);
    for(auto &file:disk.files)file[0]^=1;
    assert(boot.load()==R::Corrupt&&boot.save(seed)==R::Unknown);
    puts("update journal: codec corruption, phase bounds, 256 torn writes, lost ACK, reboot counters, wrong device passed");
}
