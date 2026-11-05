#pragma once
#include "native_app_port_0041.h"
#include "screen_port_0041.h"
#include <memory>
// Explicit lowest-platform substitutes for host/RV32 model checks. Never linked
// into a ROM. Real loader/provider/host/App code uses these instead of ROM I/O.
struct Ap01ModelPlatformV3 {
    struct Task {void *(*entry)(void *)=nullptr;void *context=nullptr;uint32_t stack=0;};
    Task tasks[4];unsigned taskCount=0,maintenanceStarts=0,mounts=0,stockEvents=0,packageCloses=0;
    uint64_t now=100;
    bool listening=false,busy=false,packageOpen=false;
    bool clockFailed=false;
    uintptr_t threadIdentity=1; // Explicit logical task identity; no scheduler claim.
    bool allowMkdir=false;unsigned mkdirCalls=0;
    const uint8_t *package=nullptr;uint32_t packageBytes=0,position=0;
    unsigned mountedPages=0,activeChild=0,eventCode=0,eventKey=0;void *eventTarget=nullptr;
    ap01_window_0041 *window=nullptr;
    Ap01MaintenanceBridge0041 bridge{};
    // Explicit six-file fixture: bindings, Bundle payload/cache and metadata.
    // Content buffers are allocated lazily; each descriptor owns its cursor.
    struct File {std::unique_ptr<uint8_t[]> bytes;uint32_t size=0,capacity=0;bool present=false;};
    struct Handle {int file=-1;uint32_t position=0;bool writable=false;};
    File files[6];Handle handles[16];bool bundleDirectory=false;
    unsigned bindingWrites=0,bindingRenames=0,bundleWrites=0,bundleRenames=0;
    void (*drawCallback)(void *)=nullptr;void *drawContext=nullptr;
    // Optional single-request wire fixture. Null by default; never real sockets.
    const uint8_t *httpInput=nullptr;uint32_t httpLength=0,httpRead=0;
    uint8_t *httpOutput=nullptr;uint32_t httpCapacity=0,httpWritten=0,httpCloses=0;
    bool httpQueued=false,httpActive=false;
    void (*pause)(uint32_t)=nullptr;
};
extern Ap01ModelPlatformV3 ap01ModelV3;
void ap01ModelStockV3(void *);
