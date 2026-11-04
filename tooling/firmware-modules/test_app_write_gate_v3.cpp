#include "app_files_v3.h"
#include <cassert>
#include <chrono>
#include <condition_variable>
#include <cstdio>
#include <mutex>
#include <thread>
struct Disk {
    std::mutex mutex;std::condition_variable condition;
    bool entered=false,release=false;unsigned writes=0,mutations=0;
    static int open(void *p,const char *,unsigned mode){if(mode)++((Disk *)p)->mutations;return mode?10:11;}
    static int close(void *,int){return 0;}
    static int read(void *,int,void *,size_t){return 0;}
    static int write(void *p,int,const void *,size_t n){auto &s=*(Disk *)p;
        std::unique_lock<std::mutex> lock(s.mutex);++s.writes;s.entered=true;s.condition.notify_all();
        assert(s.condition.wait_for(lock,std::chrono::seconds(5),[&]{return s.release;}));return int(n);}
    static int mutate(void *p,const char *){++((Disk *)p)->mutations;return 0;}
    static int rename(void *p,const char *,const char *){++((Disk *)p)->mutations;return 0;}
    Ap01VfsOps io(){Ap01VfsOps v{};v.context=this;v.open=open;v.close=close;v.read=read;v.write=write;
        v.mkdir=mutate;v.remove=mutate;v.rename=rename;return v;}
};
int main(){
    Disk disk;Ap01AppWriteGateV3 gate;
    Ap01AppFilesV3 a(disk.io(),"/a"),b(disk.io(),"/b");a.bindGate(gate);b.bindGate(gate);
    auto x=a.table(),y=b.table();assert(gate.drained()&&!gate.writable());
    assert(!a.writes(true)&&!b.writes(true));
    assert(x.open(x.context,"/a/value",1)<0&&y.open(y.context,"/b/value",1)<0);
    assert(gate.writes(true)&&gate.writable());
    int first=x.open(x.context,"/a/value",1),second=y.open(y.context,"/b/value",1);assert(first>0&&second>0);
    std::thread writer([&]{assert(x.write(x.context,first,"x",1)==1);});
    {std::unique_lock<std::mutex> lock(disk.mutex);assert(disk.condition.wait_for(lock,std::chrono::seconds(5),[&]{return disk.entered;}));}
    assert(!gate.writes(false)&&!gate.writable()&&!gate.drained());
    assert(!gate.writes(true)); // Cannot reopen until the previous write returned.
    assert(y.write(y.context,second,"y",1)<0&&y.write(y.context,second,nullptr,0)<0);
    assert(y.open(y.context,"/b/new",1)<0&&y.mkdir(y.context,"/b/dir")<0&&y.remove(y.context,"/b/value")<0);
    assert(y.rename(y.context,"/b/value","/b/renamed")<0);
    int reader=y.open(y.context,"/b/value",0);assert(reader>0&&y.read(y.context,reader,nullptr,0)==0);
    {std::lock_guard<std::mutex> lock(disk.mutex);disk.release=true;disk.condition.notify_all();}writer.join();
    assert(gate.writes(false)&&gate.drained()&&disk.writes==1&&disk.mutations==2);
    assert(x.write(x.context,first,"z",1)<0); // Existing writable handles cannot bypass revoke.
    assert(gate.writes(true)&&y.write(y.context,second,"z",1)==1);
    assert(x.close(x.context,first)==0&&y.close(y.context,second)==0&&y.close(y.context,reader)==0);
    assert(gate.writes(false)&&gate.drained());
    assert(gate.hold(true)&&gate.held()&&gate.drained());
    std::thread health([&]{for(unsigned i=0;i<20000;++i){assert(!gate.writes(true));assert(!gate.enter());}});
    for(unsigned i=0;i<20000;++i){assert(gate.writes(false));assert(gate.held());}
    health.join();
    assert(gate.hold(false)&&!gate.held()&&!gate.writable());
    assert(gate.writes(true)&&gate.enter());
    assert(!gate.hold(true)&&gate.held()&&!gate.drained()&&!gate.writes(true));
    gate.leave();assert(gate.drained()&&!gate.writes(true));
    assert(gate.hold(false)&&!gate.writable()&&gate.writes(true));
    puts("collection write gate: common admission, in-flight drain, old-handle revoke, metadata/sync denial, readonly access and explicit reopen passed");
}
