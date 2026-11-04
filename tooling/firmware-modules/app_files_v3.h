#pragma once
#include "native_vfs_api_0041.h"
#include <atomic>
#include "app_write_gate_v3.h"

// Platform-owned for a whole boot. The App gets only table(), never this class.
// Reuses the existing File/LittleFS C boundary without serialization or chunks.
class Ap01AppFilesV3 {
    struct Slot {int handle=0,fd=-1;bool writable=false;};
    Ap01VfsOps io;
    const char *root;
    // Existing 16-descriptor budget, not a pool of file contents.
    Slot slots[16];
    uint32_t nextHandle=1;
    bool writable=false,failed=false;
    Ap01AppWriteGateV3 *collection=nullptr;
    std::atomic_flag lock=ATOMIC_FLAG_INIT;
    struct Guard {
        Ap01AppFilesV3 &self;bool held;
        explicit Guard(void *p):self(*(Ap01AppFilesV3 *)p),held(!self.lock.test_and_set(std::memory_order_acquire)){}
        ~Guard(){if(held)self.lock.clear(std::memory_order_release);}
        explicit operator bool() const {return held&&!self.failed;}
    };
    struct Permit {
        Ap01AppWriteGateV3 *gate=nullptr;bool allowed=false;
        explicit Permit(Guard &g,bool mutation=true){
            if(!g)return;
            if(!mutation){allowed=true;return;}
            if(g.self.collection){if(g.self.collection->enter()){gate=g.self.collection;allowed=true;}}
            else allowed=g.self.writable;
        }
        ~Permit(){if(gate)gate->leave();}
        explicit operator bool()const{return allowed;}
    };
    bool path(const char *) const;
    Slot *slot(int);
    static int prepare(void *,const char *);
    static int open(void *,const char *,unsigned);
    static int close(void *,int);
    static int read(void *,int,void *,size_t);
    static int write(void *,int,const void *,size_t);
    static int32_t seek(void *,int,int32_t,unsigned);
    static int32_t size(void *,int);
    static int exists(void *,const char *);
    static int mkdir(void *,const char *);
    static int remove(void *,const char *);
    static int rename(void *,const char *,const char *);
    static int capacity(void *,const char *,uint64_t *,uint64_t *);
public:
    Ap01AppFilesV3(const Ap01VfsOps &backend,const char *privateRoot):io(backend),root(privateRoot){}
    Ap01AppFilesV3(const Ap01AppFilesV3 &)=delete;
    Ap01AppFilesV3 &operator=(const Ap01AppFilesV3 &)=delete;
    Ap01VfsOps table(){return {this,prepare,open,close,read,write,seek,size,exists,mkdir,remove,rename,capacity};}
    // Platform only: success means all earlier calls finished; held writers are
    // denied on their next call too. Busy returns false without changing policy.
    bool writes(bool allow);
    // Resident construction only, before exposing table(). No per-App override.
    void bindGate(Ap01AppWriteGateV3 &gate){collection=&gate;}
};
