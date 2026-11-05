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
    struct Coordinator {Ap01AppWriteGateV3 *gate=nullptr;bool busy=false,revoke=false;unsigned enters=0,leaves=0;} coordinator;
    Ap01AppWriteGateV3 coordinated(&coordinator,[](void *p){auto &c=*(Coordinator *)p;
        if(c.busy)return false;++c.enters;if(c.revoke)c.gate->hold(true);return true;},
        [](void *p){++((Coordinator *)p)->leaves;});
    coordinator.gate=&coordinated;
    assert(!coordinated.enter()&&!coordinator.enters); // Closed admission never takes the coordinator.
    assert(coordinated.writes(true));coordinator.busy=true;
    assert(!coordinated.enter()&&!coordinator.enters&&!coordinator.leaves);
    coordinator.busy=false;coordinator.revoke=true;
    assert(!coordinated.enter()&&coordinated.held()&&coordinated.drained());
    assert(coordinator.enters==1&&coordinator.leaves==1); // Revocation after lock acquisition releases it.
    assert(coordinated.hold(false)&&coordinated.writes(true));coordinator.revoke=false;
    assert(coordinated.enter()&&coordinator.enters==2&&coordinator.leaves==1);
    coordinated.leave();assert(coordinator.leaves==2&&coordinated.writable());
    struct Scope {
        Ap01AppFilesV3 &files;Ap01AppWriteGateV3 &gate;unsigned calls=0;
        static int32_t run(void *p){auto &s=*(Scope *)p;++s.calls;auto io=s.files.table();
            int fd=io.open(io.context,"/scope/value",1);assert(fd>0);
            int32_t nested=99;assert(!s.files.writeScope(run,p,nested)&&nested==99);
            assert(io.write(io.context,fd,"a",1)==1);
            // An already admitted operation finishes while commit drains it.
            assert(!s.gate.hold(true)&&!s.gate.drained());
            std::thread other([&]{
                assert(io.write(io.context,fd,"b",1)<0&&io.mkdir(io.context,"/scope/dir")<0);
                int32_t untouched=77;assert(!s.files.writeScope(run,p,untouched)&&untouched==77);
                int read=io.open(io.context,"/scope/value",0);assert(read>0&&io.close(io.context,read)==0);
            });other.join();
            assert(io.write(io.context,fd,"c",1)==1&&io.close(io.context,fd)==0);
            return -7; // Real callback failure is distinct from no admission.
        }
    };
    Ap01AppFilesV3 scoped(disk.io(),"/scope");scoped.bindGate(coordinated);
    Scope scope{scoped,coordinated};int32_t outcome=123;
    assert(!scoped.writeScope(Scope::run,&scope,outcome)&&!scope.calls&&outcome==123);
    scoped.threadIdentity(nullptr,[](void *)->uintptr_t{return 0;});
    assert(!scoped.writeScope(Scope::run,&scope,outcome)&&!scope.calls&&outcome==123);
    scoped.threadIdentity(nullptr,[](void *)->uintptr_t{static thread_local int identity;return (uintptr_t)&identity;});
    coordinator.busy=true;
    assert(!scoped.writeScope(Scope::run,&scope,outcome)&&!scope.calls&&outcome==123);
    coordinator.busy=false;
    assert(scoped.writeScope(Scope::run,&scope,outcome)&&scope.calls==1&&outcome==-7);
    assert(coordinator.enters==3&&coordinator.leaves==3&&coordinated.drained());
    assert(!scoped.writeScope(Scope::run,&scope,outcome)&&scope.calls==1);
    assert(coordinated.hold(false)&&coordinated.writes(true));
    assert(scoped.writeScope(Scope::run,&scope,outcome)&&scope.calls==2);
    puts("collection write gate: common admission, in-flight drain, old-handle revoke, metadata/sync denial, readonly access and explicit reopen passed");
}
